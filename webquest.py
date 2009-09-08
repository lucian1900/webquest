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
import pango

class WebquestView(gtk.ScrolledWindow):
    __gtype_name__ = 'SugarWebquestView'
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.feed = None
        
        self._vbox = gtk.VBox(spacing=5)
        self.add(self._vbox)
        self._vbox.show()
        
        self._summary = gtk.Label()
        self._vbox.pack_start(self._summary, expand=False)
        self._summary.set_line_wrap(True)
        self._summary.show()
        
        self._description = gtk.Label()
        self._vbox.pack_start(self._description, expand=False)
        self._description.set_alignment(0.12,0)
        self._description.set_line_wrap(True)
        self._description.show()
                
        self._tasks = gtk.Label()
        self._vbox.pack_start(self._tasks, expand=False)
        self._tasks.set_alignment(0.12,0)
        self._tasks.set_line_wrap(True)
        self._tasks.show()
        
        # buddy list
        self._tree_view = gtk.TreeView()
        self.add(self._tree_view)
        self._tree_view.show()
        
        self._tree_view.set_model(gtk.ListStore(str, str))  
        selection = self._tree_view.get_selection()
        selection.connect('changed', self.__selection_changed_cb)
        
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = 400
        column = gtk.TreeViewColumn()
        column.pack_start(cell, expand=False)
        column.add_attribute(cell, 'markup', 1)
        
        self._tree_view.append_column(column)
        self._tree_view.set_search_column(0)
        self._tree_view.props.headers_visible = False
        
    def set(self, uri, summary):
        self._summary.set_markup(summary)
        
        self._description.set_markup('''\n<b>Detailed description (placeholder)</b>\nasdassdfasdgdhsrgasdfaefegfsgdfasdkjnasdkjas;ldkfsadlkfjsadkfaslkdcmnaleiiflsjf\ng\nfdgs\nfdgsdfgdfgsdfg\n\n<b>Tasks</b>\n  1. asda\n  2. asd\n  3. 4545''')
        
    def add_buddy(self, nick):
        model = self._tree_view.get_model()
        model.append([nick, _('none')])        
        
    def remove_buddy(self, nick):
        model = self._tree_view.get_model()
        model.foreach(self._remove_buddy_cb, nick)
        
    def _remove_buddy_cb(self, model, path, tree_iter, user_data):
        nick = model.get_value(tree_iter, 0)
        if nick == user_data:
            model.remove(tree_iter)
        
