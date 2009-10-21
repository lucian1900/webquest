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
    
    def __init__(self, act):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self._activity = act
                
        self._vbox = gtk.VBox(spacing=2)
        self.add_with_viewport(self._vbox)
        self._vbox.show()
        
        self._hbox = gtk.HBox(spacing=4)
        self._vbox.pack_start(self._hbox)
        self._hbox.show()

        # title
        self._summary = gtk.Label()
        self._hbox.pack_start(self._summary, expand=True, fill=True)
        self._summary.set_line_wrap(True)
        self._summary.show()
        
        self._vbox_work = gtk.VBox()
        self._vbox.pack_start(self._vbox_work)
        self._vbox_work.show()
        
        self._link = gtk.Label()
        self._link.set_markup('<b>Link</b>')
        self._link.set_size_request(gtk.gdk.screen_width() - 100, -1)
        self._hbox_link.pack_start(self._link, expand=True, fill=True)
        self._link.show()
        
        self._web_link = gtk.Label()
        self._web_link.set_size_request(gtk.gdk.screen_width() - 100, -1)
        self._hbox_link.pack_start(self._web_link, expand=True, fill=True)
        self._web_link.set_selectable(True)
        self._web_link.show()
        
        self._description = gtk.Label()
        self._description.set_size_request(gtk.gdk.screen_width() - 100, -1)
        self._vbox_work.pack_start(self._description, expand=True, fill=True)
        self._description.set_line_wrap(True)
        self._description.show()
                
        self._tasks = gtk.Label()
        self._tasks.set_size_request(gtk.gdk.screen_width() - 100, -1)
        self._vbox_work.pack_start(self._tasks, expand=True, fill=True)
        self._tasks.set_line_wrap(True)
        self._tasks.show()
        
        # me
        self._hbox_me = gtk.HBox()
        self._vbox_work.pack_start(self._hbox_me)
        
        self._me = gtk.Label(_('My role'))
        self._hbox_me.pack_start(self._me)
        self._me.show()
        
        self._my_role = gtk.ComboBox()
        self._my_role.set_model(gtk.ListStore(str))
        self._my_role.connect('changed', self.__role_changed_cb)
        self._hbox_me.pack_start(self._my_role)
        self._my_role.show()
        
        # buddy list
        self._buddies = gtk.TreeView()
        self._vbox_work.pack_start(self._buddies)
        
        self._buddies.set_model(gtk.ListStore(str, str))  
        selection = self._buddies.get_selection()
        selection.connect('changed', self.__buddy_selection_changed_cb)
        
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = gtk.gdk.screen_width() - 200
        
        column_nick = gtk.TreeViewColumn()
        column_nick.pack_start(cell, expand=False)
        column_nick.add_attribute(cell, 'markup', 0)
        
        column_role = gtk.TreeViewColumn()
        column_role.pack_start(cell, expand=False)
        column_role.add_attribute(cell, 'markup', 1)
        
        self._buddies.append_column(column_nick)
        self._buddies.append_column(column_role)
        self._buddies.set_search_column(0)
        self._buddies.props.headers_visible = False
        
    def set(self, uri, summary):
        try:
            xml = urllib2.urlopen(uri).read()
        except (urllib2.URLError, urllib2.HTTPError, IOError), e:
            logging.debug('Error %s' % e)
            self._activity._alert(_('Network error'), 
                                  _('Couldn\'t download webquest data'))
            return
            
        feed = ElementTree.fromstring(xml).find('webquest')
        
        self._summary.set_markup(summary)    
        self._description.set_markup('<b>%s</b>\n' % _('Process Description') + 
                                     feed.find('process-description').text)
    
        self._web_link.set_text(uri)
    
        tasks_text = u'<b>%s</b>\n' % _('Tasks')
        for i, e in enumerate(feed.find('tasks').getchildren()):
            tasks_text += '%s. %s\n' % (i+1, e.find('task-description').text)
        self._tasks.set_markup(tasks_text)
        
        # my role, filling the combobox
        roles = feed.find('roles')
        if roles is not None:
            self._my_role.show()
            self._buddies.show()
            
            model = self._my_role.get_model()
            for i in roles.getchildren():
                model.append([i.find('description').text])
            
        # add buddies
        for nick, role in self._activity.model.roles.items():
            self.add_buddy(nick, role)
        
    def add_buddy(self, nick, role):
        model = self._buddies.get_model()
        model.append([nick, role])        
        
    def remove_buddy(self, nick):
        model = self._buddies.get_model()
        model.foreach(self._remove_buddy_cb, nick)
        
    def _remove_buddy_cb(self, model, path, tree_iter, user_data):
        nick = model.get_value(tree_iter, 0)
        if nick == user_data:
            model.remove(tree_iter)
            
    def __role_changed_cb(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        
        self._activity.model.my_role = index
            
    def __my_role_activate_cb(self, entry):
        self._activity._my_role = entry.get_text()
    
    def __resource_selection_changed_cb(self, selection):
        pass
    
    def __buddy_selection_changed_cb(self, selection):
        pass