import time
from gettext import gettext as _
import logging

import gtk
import feedparser

class FeedList(gtk.ScrolledWindow):
    __gtype_name__ = "SugarFeedList"
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self._uri = None
        self._feed = None
        
        self._tree_view = gtk.TreeView()
        self.add(self._tree_view)
        self._tree_view.set_model(gtk.TreeStore(str))        
        
        selection = self._tree_view.get_selection()
        selection.connect('changed', self.__selection_changed_cb)
        
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', 0)
        
        self._tree_view.append_column(column)
        self._tree_view.set_search_column(0)
        
        self.update()
        
    def __selection_changed_cb(self, selection):
        model, tree_iter = selection.get_selected()
    
    def update(self):
        model = self._tree_view.get_model()
        
        self._feed = feedparser.parse(self._uri)
        
        for e in self._feed.entries:
            column = '%s\n%s\n%s' % (e.title, e.description, e.updated)
            model.append(None, [column])
        
    def set_uri(self, uri):
        self._uri = uri
        self.update()
    
    def get_uri(self):
        return self._uri
    
    uri = property(get_uri, set_uri, None)
    
class FeedItem(gtk.VBox):
    __gtype_name__ = "SugarFeedItem"
    
    def __init__(self):
        gtk.VBox.__init__(self)
        
        