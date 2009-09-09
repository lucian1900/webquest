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

import time
from gettext import gettext as _
import logging
from xml.etree import ElementTree
import urllib2

import gobject
import gtk
import pango

from sugar.graphics.alert import NotifyAlert

class FeedList(gtk.ScrolledWindow):
    __gtype_name__ = "SugarFeedList"
    
    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_FIRST,
                          gobject.TYPE_NONE, ([str, str])),
    }
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.uri = None
        self._feed = None
        
        self._tree_view = gtk.TreeView()
        self.add(self._tree_view)
        self._tree_view.show()
        
        self._tree_view.set_model(gtk.ListStore(int, str))  
        selection = self._tree_view.get_selection()
        selection.connect('changed', self.__selection_changed_cb)
        
        cell = gtk.CellRendererText()
        cell.props.wrap_mode = pango.WRAP_WORD
        cell.props.wrap_width = 800
        column = gtk.TreeViewColumn()
        column.pack_start(cell, expand=False)
        column.add_attribute(cell, 'markup', 1)
        
        self._tree_view.append_column(column)
        self._tree_view.set_search_column(0)
        self._tree_view.props.headers_visible = False
                
    def __selection_changed_cb(self, selection):
        model, tree_iter = selection.get_selected()
        index = model.get_value(tree_iter, 0)
        uri = self._feed.findall('item')[index].find('source').attrib['url']
        summary = model.get_value(tree_iter, 1)
        
        self.emit('item-selected', uri, summary)
    
    def update(self, uri):
        self.uri = uri
        xml = urllib2.urlopen(uri).read()
        self._feed = ElementTree.fromstring(xml).find('channel')
        model = self._tree_view.get_model()
        
        for i, e in enumerate(self._feed.findall('item')):
            
            logging.debug('@@@@@ %s' % e)
            title = u'<b>%s</b>' % e.find('title').text
            descr = unicode(e.find('description').text)
            date = u'<b>%s</b>: ' % _('Date')
            try:
                t = time.strptime(e.find('pubDate').text, 
                                  "%a, %m/%d/%Y - %H:%M")
            except ValueError:
                date += 'Unknown'
            else:
                date += time.strftime('%d %b %Y', t)
                
            rating_no = int(e.find('comments').text)
            rating_head = u'<span foreground="#000">%s</span>' \
                          % u'\u2605' * rating_no
            rating_tail = u'<span foreground="#eee">%s</span>' \
                          % u'\u2605' * (5 - rating_no)
            rating = '\t<b>Rating</b>: ' + rating_head + rating_tail
            
            row = '\n'.join([title, descr, date + rating])
            model.append([i, row])
        
        