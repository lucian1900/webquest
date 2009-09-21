# Copyright (C) 2009, Lucian Branescu Mihaila
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import logging
from gettext import gettext as _

import gtk
import telepathy
import rsvg
from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

from sugar.activity import activity
from sugar.graphics.alert import NotifyAlert
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection

from toolbars import WebquestToolbar
import feed
import webquest
import send

SERVICE = 'org.sugarlabs.Webquest'
IFACE = SERVICE
PATH = '/org/sugarlabs/Webquest'

class WebquestActivity(activity.Activity):
    DEFAULT_FEED_URI = 'http://www.rodrigopadula.com/webquest/webquest/feed'
    DEFAULT_SEND_URI = 'http://www.rodrigopadula.com/webquest/upload'
    
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        self._logger = logging.getLogger('webquest-activity')
        
        # render and cache Browse icon
        #svg_path = os.path.join(activity.get_bundle_path(), 'icons/browse.svg')
        #svg = rsvg.Handle(file=svg_path)
        
        # toolbars
        toolbox = activity.ActivityToolbox(self)
        
        self._webq_toolbar = WebquestToolbar(self)
        toolbox.add_toolbar(_('Webquests'), self._webq_toolbar)
        self._webq_toolbar.connect('toggle-send', self._toggle_send_cb)
        
        self.set_toolbox(toolbox)
        self.toolbox.set_current_toolbar(1)
        toolbox.show_all()
        
        # canvas
        self._hbox = gtk.HBox()
        self.set_canvas(self._hbox)
        self._hbox.show()
        
        self._feed_list = feed.FeedList(self)
        self._hbox.pack_start(self._feed_list)
        self._feed_list.show_all()
        self._feed_list.connect('item-selected', self.__show_webquest_cb)
        self.load_feed(self.DEFAULT_FEED_URI)     
        
        self._webquest_view = webquest.WebquestView(self)
        self._hbox.pack_start(self._webquest_view)
        
        # send bundle window
        self._bundle_win = send.BundleView()
                                   
        #self.connect('shared', self._shared_cb)
        #self.connect('joined', self._joined_cb)
        
    def _alert(self, title, text=None):
        alert = NotifyAlert(timeout=5)
        alert.props.title = title
        alert.props.msg = text
        self.add_alert(alert)
        alert.connect('response', self._alert_cancel_cb)
        alert.show()

    def _alert_cancel_cb(self, alert, response_id):
        self.remove_alert(alert)
        
    def _toggle_send_cb(self, toolbar):
        #if not self._bundle_win.props.has_focus:
        #    self._bundle_win.hide()
        
        if self._bundle_win.props.visible:
            self._bundle_win.hide()
        else:
            self._bundle_win.show()
            
    def _shared_cb(self, activity):
        self._logger.debug('My activity was shared')
        #self._alert('Shared', 'The activity is shared')
        self.initiating = True
        self._sharing_setup()

        self._logger.debug('This is my activity: making a tube...')
        id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})
        
    def _joined_cb(self, activity):
        if not self.shared_activity:
            return

        self._logger.debug('Joined an existing shared activity')
        #self._alert('Joined', 'Joined a shared activity')
        self.initiating = False
        self._sharing_setup()

        self._logger.debug('This is not my activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)
            
    def _sharing_setup(self):
        if self.shared_activity is None:
            self._logger.error('Failed to share or join activity')
            return

        self.conn = self.shared_activity.telepathy_conn
        self.tubes_chan = self.shared_activity.telepathy_tubes_chan
        self.text_chan = self.shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(
            'NewTube', self._new_tube_cb)

        self.shared_activity.connect('buddy-joined', self._buddy_joined_cb)
        self.shared_activity.connect('buddy-left', self._buddy_left_cb)

        self.entry.set_sensitive(True)
        self.entry.grab_focus()

        # Optional - included for example:
        # Find out who's already in the shared activity:
        for buddy in self.shared_activity.get_joined_buddies():
            self._logger.debug('Buddy %s is already in the activity',
                               buddy.props.nick)
                               

    def _buddy_joined_cb (self, activity, buddy):
        """Called when a buddy joins the shared activity.

        This doesn't do much here as HelloMesh doesn't have much 
        functionality. It's up to you do do interesting things
        with the Buddy...
        """
        self._logger.debug('Buddy %s joined', buddy.props.nick)
        self._webquest_view.add_buddy(buddy.props.nick)

    def _buddy_left_cb (self, activity, buddy):
        """Called when a buddy leaves the shared activity.

        This doesn't do much here as HelloMesh doesn't have much 
        functionality. It's up to you do do interesting things
        with the Buddy...
        """
        self._logger.debug('Buddy %s left', buddy.props.nick)
        self._webquest_view.remove_buddy(buddy.props.nick)
        
    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        self._logger.error('ListTubes() failed: %s', e)
        
    def _new_tube_cb(self, id, initiator, type, service, params, state):
        self._logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
                     'params=%r state=%d', id, initiator, type, service,
                     params, state)
        if (type == telepathy.TUBE_TYPE_DBUS and
            service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)
            tube_conn = TubeConnection(self.conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
                id, group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
            self.hellotube = RolesSync(tube_conn, self.initiating,
                                      self.entry_text_update_cb,
                                      self._alert,
                                      self._get_buddy)
          
    def __show_webquest_cb(self, feed_list, uri, summary):
        self._webquest_view.set(uri, summary)
        self._feed_list.hide()
        self._webquest_view.show()
        self._webq_toolbar.enable_back()
        
    def show_feed_list(self):
        self._webquest_view.hide()
        self._feed_list.show()
        self._webq_toolbar.disable_back()
        
    def load_feed(self, uri):
        logging.debug('Loading feed from %s' % uri)
        self._feed_list.update(uri)
        
    def read_file(self, file_path):
        pass
        
    def write_file(self, file_path):
        pass
        
    def can_close(self):
        return True
        
class RolesSync(ExportedGObject):
    """The bit that talks over the TUBES!!!"""

    def __init__(self, tube, is_initiator, text_received_cb,
                 alert, get_buddy):
        super(RolesSync, self).__init__(tube, PATH)
        self._logger = logging.getLogger('hellomesh-activity.RolesSync')
        self.tube = tube
        self.is_initiator = is_initiator
        self.text_received_cb = text_received_cb
        self._alert = alert
        self.entered = False  # Have we set up the tube?
        self.text = '' # State that gets sent or received
        self._get_buddy = get_buddy  # Converts handle to Buddy object
        self.tube.watch_participants(self.participant_change_cb)

    def participant_change_cb(self, added, removed):
        self._logger.debug('Tube: Added participants: %r', added)
        self._logger.debug('Tube: Removed participants: %r', removed)
        for handle, bus_name in added:
            buddy = self._get_buddy(handle)
            if buddy is not None:
                self._logger.debug('Tube: Handle %u (Buddy %s) was added',
                                   handle, buddy.props.nick)
        for handle in removed:
            buddy = self._get_buddy(handle)
            if buddy is not None:
                self._logger.debug('Buddy %s was removed' % buddy.props.nick)
        if not self.entered:
            if self.is_initiator:
                self._logger.debug("I'm initiating the tube, will "
                    "watch for hellos.")
                self.add_hello_handler()
            else:
                self._logger.debug('Hello, everyone! What did I miss?')
                self.Hello()
        self.entered = True

    @signal(dbus_interface=IFACE, signature='')
    def Hello(self):
        """Say Hello to whoever else is in the tube."""
        self._logger.debug('I said Hello.')

    @method(dbus_interface=IFACE, in_signature='s', out_signature='')
    def World(self, text):
        """To be called on the incoming XO after they Hello."""
        if not self.text:
            self._logger.debug('Somebody called World and sent me %s',
                               text)
            self._alert('World', 'Received %s' % text)
            self.text = text
            self.text_received_cb(text)
            # now I can World others
            self.add_hello_handler()
        else:
            self._logger.debug("I've already been welcomed, doing nothing")

    def add_hello_handler(self):
        self._logger.debug('Adding hello handler.')
        self.tube.add_signal_receiver(self.hello_cb, 'Hello', IFACE,
            path=PATH, sender_keyword='sender')
        self.tube.add_signal_receiver(self.sendtext_cb, 'SendText', IFACE,
            path=PATH, sender_keyword='sender')

    def hello_cb(self, sender=None):
        """Somebody Helloed me. World them."""
        if sender == self.tube.get_unique_name():
            # sender is my bus name, so ignore my own signal
            return
        self._logger.debug('Newcomer %s has joined', sender)
        self._logger.debug('Welcoming newcomer and sending them the game state')
        self.tube.get_object(sender, PATH).World(self.text,
                                                 dbus_interface=IFACE)

    def sendtext_cb(self, text, sender=None):
        """Handler for somebody sending SendText"""
        if sender == self.tube.get_unique_name():
            # sender is my bus name, so ignore my own signal
            return
        self._logger.debug('%s sent text %s', sender, text)
        self._alert('sendtext_cb', 'Received %s' % text)
        self.text = text
        self.text_received_cb(text)

    @signal(dbus_interface=IFACE, signature='s')
    def SendText(self, text):
        """Send some text to all participants."""
        self.text = text
        self._logger.debug('Sent text: %s', text)
        self._alert('SendText', 'Sent %s' % text)
