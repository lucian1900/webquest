from gettext import gettext as _
import logging

import gtk

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.alert import Alert
from sugar.graphics.icon import Icon

class WebquestToolbar(gtk.Toolbar):
    def __init__(self, act):
        gtk.Toolbar.__init__(self)
        
        self._activity = act
        
        self._hello = ToolButton('emblem-favorite')
        self._hello.set_tooltip('Hello')
        self._hello.connect('clicked', self.__hello_cb)
        self.insert(self._hello, -1)
        self._hello.show()
        
    def __hello_cb(self, button):
        logging.debug('hello')
        
class BundleToolbar(gtk.Toolbar):
    def __init__(self, act):
        gtk.Toolbar.__init__(self)
    
        self._activity = act