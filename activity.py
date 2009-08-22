import os
import logging
from gettext import gettext as _

import gtk

from sugar.activity import activity

import toolbars
import feed

class WebquestActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        # toolbars
        self._primary_toolbar = toolbars.PrimaryToolbar(self)
        self._primary_toolbar.show_all()
        self.set_toolbar_box(self._primary_toolbar)
        
        # tabs
        self._notebook = gtk.Notebook()
        self._notebook.show()
        self.set_canvas(self._notebook)
        
        self._feed_list = feed.FeedList()
        self._feed_list.show_all()
        self._notebook.append_page(self._feed_list, gtk.Label(_('Feeds')))
        

        
    def read_file(self, file_path):
        pass
        
    def write_file(self, file_path):
        pass
        
    def can_close(self):
        return True