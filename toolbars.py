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
        
        entry_item = gtk.ToolItem()
        entry_item.set_expand(True)
        entry_item.add(self._entry)
        self.insert(entry_item, -1)
        self._entry.show()
        
        self._refresh = ToolButton('view-refresh')
        self._refresh.set_tooltip(_('Refresh'))
        self._refresh.connect('clicked', self.__refresh_cb)
        self.insert(self._refresh, -1)
        self._refresh.show()
        
    def __entry_activate_cb(self, entry):
        self._activity.load_feed(entry.get_text())
        
    def __go_back_cb(self, button):
        self._activity.show_feed_list()
        
    def __refresh_cb(self, button):
        self._activity.load_feed(entry.get_text())
                
    def enable_back(self):
        self._back.props.sensitive = True
    
    def disable_back(self):
        self._back.props.sensitive = False
        
class BundleToolbar(gtk.Toolbar):
    def __init__(self, act):
        gtk.Toolbar.__init__(self)
    
        self._activity = act