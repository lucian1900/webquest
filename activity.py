import os
import logging

from sugar.activity import activity

import toolbars

class WebquestActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        self._primary_toolbar = toolbars.PrimaryToolbar(self)
        self._primary_toolbar.show_all()
        
        self.set_toolbar_box(self._primary_toolbar)
        
    def read_file(self, file_path):
        pass
        
    def write_file(self, file_path):
        pass
        
    def can_close(self):
        return True