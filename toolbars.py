from gettext import gettext as _
import logging

import gtk

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.alert import Alert
from sugar.graphics.icon import Icon
from sugar._sugarext import AddressEntry

class WebquestToolbar(gtk.Toolbar):
    def __init__(self, act):
        gtk.Toolbar.__init__(self)
        
        self._activity = act
        
        self._back = ToolButton('go-previous-paired')
        self._back.set_tooltip(_('Back'))
        self._back.props.sensitive = False
        self._back.connect('clicked', self.__go_back_cb)
        self.insert(self._back, -1)
        self._back.show()
        
        self._entry = gtk.Entry()
        self._entry.set_text(self._activity.DEFAULT_FEED_URI)
        self._entry.connect('activate', self.__entry_activate_cb)
        self._entry.show()
        
        entry_item = gtk.ToolItem()
        entry_item.set_expand(True)
        entry_item.add(self._entry)
        self.insert(entry_item, -1)
        self._entry.show
        
    def __entry_activate_cb(self, entry):
        self._activity.load_feed(entry.get_text())
        
    def __go_back_cb(self, button):
        self._activity.show_feed_list()
        
    def enable_back(self):
        self._back.props.sensitive = True
    
    def disable_back(self):
        self._back.props.sensitive = False
        
class BundleToolbar(gtk.Toolbar):
    def __init__(self, act):
        gtk.Toolbar.__init__(self)
    
        self._activity = act