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

import gobject
import gtk
import pango

from sugar.graphics import style

class BundleView(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        
        self.set_decorated(False)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_border_width(style.LINE_WIDTH)
        
        width = gtk.gdk.screen_width() - style.GRID_CELL_SIZE * 2
        height = gtk.gdk.screen_height() - style.GRID_CELL_SIZE * 2
        self.set_size_request(width, height)
        
        vbox = gtk.VBox()
        self.add(vbox)
        vbox.show()
        
        # address entry
        hbox = gtk.HBox()
        vbox.pack_start(hbox, expand=False)
        hbox.show()
        
        self._add_button = gtk.Button(label='Add')
        hbox.pack_start(self._add_button, expand=False)
        self._add_button.connect('button-press-event', self.__add_cb)
        self._add_button.show()
        
        self._entry = gtk.Entry()
        hbox.pack_start(self._entry, expand=True)
        self._entry.show()
        
        self._send_button = gtk.Button(label='Send')
        hbox.pack_start(self._send_button, expand=False)
        self._send_button.connect('button-press-event', self.__send_cb)
        self._send_button.show()
        
        # object list
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)
        sw.show()
        
        self._tree_view = gtk.TreeView()
        sw.add(self._tree_view)
        
        self._tree_view.set_model(gtk.ListStore(int, str))  
        selection = self._tree_view.get_selection()
                
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = gtk.gdk.screen_width()
        column = gtk.TreeViewColumn()
        column.pack_start(cell, expand=False)
        column.add_attribute(cell, 'markup', 1)
        
        self._tree_view.append_column(column)
        self._tree_view.set_search_column(0)
        self._tree_view.props.headers_visible = False
        
        self._tree_view.show()
    
    def __add_cb(self, button):
        pass
        
    def __send_cb(self, button):
        pass
        
class Toolbar(gtk.Toolbar):
    pass