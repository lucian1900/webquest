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

from sugar.activity import activity

from toolbars import WebquestToolbar, BundleToolbar
import feed
import webquest

class WebquestActivity(activity.Activity):
    DEFAULT_FEED_URI = 'http://webquest.rafaelsilva.net/webquest/feed'
    
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        # toolbars
        toolbox = activity.ActivityToolbox(self)
        
        self._webq_toolbar = WebquestToolbar(self)
        toolbox.add_toolbar(_('Webquests'), self._webq_toolbar)
        
        self._bundle_toolbar = BundleToolbar(self)
        toolbox.add_toolbar(_('Bundle'), self._bundle_toolbar)
        
        self.set_toolbox(toolbox)
        self.toolbox.set_current_toolbar(1)
        toolbox.show_all()
        
        # canvas
        self._hbox = gtk.HBox()
        self.set_canvas(self._hbox)
        self._hbox.show()
        
        self._feed_list = feed.FeedList()
        self._hbox.pack_start(self._feed_list)
        self._feed_list.show_all()
        self._feed_list.connect('item-selected', self.__show_webquest_cb)
        self.load_feed(self.DEFAULT_FEED_URI)     
        
        self._webquest_view = webquest.WebquestView()
        self._hbox.pack_start(self._webquest_view)
                                   
        self.connect('shared', self._shared_cb)
        self.connect('joined', self._joined_cb)
        
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