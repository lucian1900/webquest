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
import telepathy.client

from sugar.activity import activity
from sugar.graphics.alert import NotifyAlert
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection

from toolbars import WebquestToolbar
from messenger import Messenger
import feed
import webquest
import send
import model

SERVICE = 'org.sugarlabs.Webquest'
IFACE = SERVICE
PATH = '/org/sugarlabs/Webquest'

_logger = logging.getLogger('webquest-activity')

class WebquestActivity(activity.Activity):
    DEFAULT_FEED_URI = 'http://www.rodrigopadula.com/webquest/webquest/feed'
    DEFAULT_SEND_URI = 'http://www.rodrigopadula.com/webquest/upload'
    
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
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
                                   
        self.model = model.Model()
        self.messenger = None
        
        self.connect('shared', self._shared_cb)
        self.connect('joined', self._joined_cb)
        
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
        _logger.debug('My activity was shared')
        #self._alert('Shared', 'The activity is shared')
        self.initiating = True
        self._sharing_setup()

        _logger.debug('This is my activity: making a tube...')
        id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})
        
    def _joined_cb(self, activity):
        if not self.shared_activity:
            return

        _logger.debug('Joined an existing shared activity')
        #self._alert('Joined', 'Joined a shared activity')
        self.initiating = False
        self._sharing_setup()

        _logger.debug('This is not my activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes( \
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)
        
    def _sharing_setup(self):
        if self._shared_activity is None:
            _logger.debug('Failed to share or join activity')
            return

        bus_name, conn_path, channel_paths = \
                self._shared_activity.get_channels()

        # Work out what our room is called and whether we have Tubes already
        room = None
        tubes_chan = None
        text_chan = None
        for channel_path in channel_paths:
            channel = telepathy.client.Channel(bus_name, channel_path)
            htype, handle = channel.GetHandle()
            if htype == telepathy.HANDLE_TYPE_ROOM:
                _logger.debug('Found our room: it has handle#%d "%s"' 
                   %(handle, self.tube_conn.InspectHandles(htype,
                                                           [handle])[0]))
                room = handle
                ctype = channel.GetChannelType()
                if ctype == telepathy.CHANNEL_TYPE_TUBES:
                    _logger.debug('Found our Tubes channel at %s'%channel_path)
                    tubes_chan = channel
                elif ctype == telepathy.CHANNEL_TYPE_TEXT:
                    _logger.debug('Found our Text channel at %s'%channel_path)
                    text_chan = channel

        if room is None:
            _logger.debug("Presence service didn't create a room")
            return
        if text_chan is None:
            _logger.debug("Presence service didn't create a text channel")
            return

        # Make sure we have a Tubes channel - PS doesn't yet provide one
        if tubes_chan is None:
            _logger.debug("Didn't find our Tubes channel, requesting one...")
            tubes_chan = self.tube_conn.request_channel( \
                                                  telepathy.CHANNEL_TYPE_TUBES,
                                                  telepathy.HANDLE_TYPE_ROOM, 
                                                  room, True)
                                                  
        self.tubes_chan = tubes_chan
        self.text_chan = text_chan

        tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal( \
               'NewTube', self._new_tube_cb)

    def _buddy_joined_cb (self, activity, buddy):
        'Called when a buddy joins the shared activity.'
        _logger.debug('Buddy %s joined', buddy.props.nick)
        self._webquest_view.add_buddy(buddy.props.nick)

    def _buddy_left_cb (self, activity, buddy):
        'Called when a buddy leaves the shared activity.'
        _logger.debug('Buddy %s left', buddy.props.nick)
        self._webquest_view.remove_buddy(buddy.props.nick)
        
    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        _logger.error('ListTubes() failed: %s', e)
        
    def _new_tube_cb(self, identifier, initiator, type, service, params, state):
        _logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
                      'params=%r state=%d' %(identifier, initiator, type, 
                                             service, params, state))

        if (type == telepathy.TUBE_TYPE_DBUS and
            service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(
                        identifier)

            self.tube_conn = TubeConnection(self.conn, 
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES], 
                identifier, group_iface = self.text_chan[
                    telepathy.CHANNEL_INTERFACE_GROUP])

            _logger.debug('Tube created')
            self.messenger = Messenger(self.tube_conn, self.initiating, 
                                       self.model)
          
    def __show_webquest_cb(self, feed_list, uri, summary, web_uri):
        self._webquest_view.set(uri, summary, web_uri)
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