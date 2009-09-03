import os
import logging
from gettext import gettext as _

import gtk

from sugar.activity import activity

from toolbars import WebquestToolbar, BundleToolbar
import feed
import webquest

class WebquestActivity(activity.Activity):
    DEFAULT_FEED_URI = '/media/desktop/webquest_rss.xml'
    
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
        
        
        # tabs
        self._hbox = gtk.HBox()
        self.set_canvas(self._hbox)
        self._hbox.show()
        
        self._feed_list = feed.FeedList()
        self._hbox.pack_start(self._feed_list)
        self._feed_list.show_all()
        self._feed_list.connect('item-selected', self.__show_webquest_cb)        
        
        self._webquest_view = webquest.WebquestView()
        self._hbox.pack_start(self._webquest_view)
                                   
        self.load_feed(self.DEFAULT_FEED_URI)
        
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
        self._feed_list.uri = uri
        self._feed_list.update()
        
    def read_file(self, file_path):
        pass
        
    def write_file(self, file_path):
        pass
        
    def can_close(self):
        return True