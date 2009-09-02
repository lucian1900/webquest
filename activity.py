import os
import logging
from gettext import gettext as _

import gtk

from sugar.activity import activity

from toolbars import WebquestToolbar, BundleToolbar
import feed

class WebquestActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        # toolbars
        toolbox = activity.ActivityToolbox(self)
        
        self._webq_toolbar = WebquestToolbar(self)
        toolbox.add_toolbar(_('Webquests'), self._webq_toolbar)
        
        self._bundle_toolbar = BundleToolbar(self)
        toolbox.add_toolbar(_('Bundle'), self._bundle_toolbar)
        
        self.set_toolbox(toolbox)
        toolbox.show()
        
        # tabs
        self._notebook = gtk.Notebook()
        self._notebook.show()
        self.set_canvas(self._notebook)
        
        self._feed_list = feed.FeedList()
        self._feed_list.show_all()
        self._notebook.append_page(self._feed_list, gtk.Label(_('WebQuests')))
        self._feed_list.uri = '/media/desktop/webquest_rss.xml' # hard-coded
        
        
    def read_file(self, file_path):
        pass
        
    def write_file(self, file_path):
        pass
        
    def can_close(self):
        return True