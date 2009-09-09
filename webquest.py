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
        #selection.connect('changed', self.__selection_changed_cb)
        
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
        logging.debug('##### %s' % uri)
        xml = urllib2.urlopen(uri).read()
        feed = ElementTree.fromstring(xml).find('webquest')
        
        self._summary.set_markup(summary)
        
        
        self._description.set_markup('<b>%s</b>\n' % _('Process Description') + 
                                     feed.find('process-description').text)
        tasks_text = u'<b>%s</b>\n' % _('Tasks')
        for i, e in enumerate(feed.find('tasks').getchildren()):
            tasks_text += i + '. ' + e.find('task-description').text + '\n'
        self._tasks.set_markup(tasks_text)
        
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
            
def parse(uri):
    data = urllib2.urlopen(uri).read()
    tree = ElementTree.fromstring(data)
    d = dict()
    
    return XmlDictConfig(tree)      

class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    
    From http://code.activestate.com/recipes/410469/
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})
