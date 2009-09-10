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
import urllib2
from xml.etree import ElementTree

import gtk
import pango

class WebquestView(gtk.ScrolledWindow):
    __gtype_name__ = 'SugarWebquestView'
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
                
        self._vbox = gtk.VBox(spacing=2)
        self.add_with_viewport(self._vbox)
        self._vbox.show()
        
        self._summary = gtk.Label()
        self._vbox.pack_start(self._summary, expand=True, fill=True)
        self._summary.set_line_wrap(True)
        self._summary.show()
        
        self._description = gtk.Label()
        self._vbox.pack_start(self._description, expand=True, fill=True)
        #self._description.set_alignment(0.12,0)
        self._description.props.width_chars = 70
        self._description.set_line_wrap(True)
        self._description.show()
                
        self._tasks = gtk.Label()
        self._vbox.pack_start(self._tasks, expand=True, fill=True)
        #self._tasks.set_alignment(0.12,0)
        self._tasks.set_line_wrap(True)
        self._tasks.show()
        
        # Resources list
        self._resources = gtk.TreeView()
        self._vbox.pack_start(self._resources)
        self._resources.show()
        
        self._resources.set_model(gtk.ListStore(str, str))  
        selection = self._resources.get_selection()
        selection.connect('changed', self.__resource_selection_changed_cb)
        
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = 800
        column = gtk.TreeViewColumn()
        column.pack_start(cell, expand=False)
        column.add_attribute(cell, 'markup', 1)
        
        self._resources.append_column(column)
        self._resources.set_search_column(0)
        self._resources.props.headers_visible = False
        
        # buddy list
        self._buddies = gtk.TreeView()
        self._vbox.pack_start(self._buddies)
        self._buddies.show()
        
        self._buddies.set_model(gtk.ListStore(str, str))  
        selection = self._buddies.get_selection()
        selection.connect('changed', self.__buddy_selection_changed_cb)
        
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = 800
        column = gtk.TreeViewColumn()
        column.pack_start(cell, expand=False)
        column.add_attribute(cell, 'markup', 1)
        
        self._buddies.append_column(column)
        self._buddies.set_search_column(0)
        self._buddies.props.headers_visible = False
        
    def set(self, uri, summary):
        xml = urllib2.urlopen(uri).read()
        feed = ElementTree.fromstring(xml).find('webquest')
        
        self._summary.set_markup(summary)
    
        self._description.set_markup('<b>%s</b>\n' % _('Process Description') + 
                                     feed.find('process-description').text)
    
        tasks_text = u'<b>%s</b>\n' % _('Tasks')
        for i, e in enumerate(feed.find('tasks').getchildren()):
            tasks_text += '%s. %s\n' % (i+1, e.find('task-description').text)
        self._tasks.set_markup(tasks_text)
        
        model = self._resources.get_model()
        for i in feed.find('references').getchildren():
            model.append(['<u>%s</u>' % i.find('reference-description').text,
                          i.find('url').text])
        
    def add_buddy(self, nick):
        model = self._buddies.get_model()
        model.append([nick, _('none')])        
        
    def remove_buddy(self, nick):
        model = self._buddies.get_model()
        model.foreach(self._remove_buddy_cb, nick)
        
    def _remove_buddy_cb(self, model, path, tree_iter, user_data):
        nick = model.get_value(tree_iter, 0)
        if nick == user_data:
            model.remove(tree_iter)
            
    def __resource_selection_changed_cb(self, selection):
        pass
    
    def __buddy_selection_changed_cb(self, selection):
        pass