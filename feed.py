import time
from gettext import gettext as _
import logging

import gobject
import gtk
import feedparser

class FeedList(gtk.ScrolledWindow):
    __gtype_name__ = "SugarFeedList"
    
    __gsignals__ = {
        'item-selected': (gobject.SIGNAL_RUN_FIRST,
                          gobject.TYPE_NONE, ([str, str])),
    }
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.uri = None
        self._feed = None
        
        self._tree_view = gtk.TreeView()
        self.add(self._tree_view)
        self._tree_view.show()      
        
        self._tree_view.set_model(gtk.ListStore(int, str))  
        selection = self._tree_view.get_selection()
        selection.connect('changed', self.__selection_changed_cb)
        
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'markup', 1)
        
        self._tree_view.append_column(column)
        self._tree_view.set_search_column(0)
        self._tree_view.props.headers_visible = False
        
        self.update()
        
    def __selection_changed_cb(self, selection):
        model, tree_iter = selection.get_selected()
        index = model.get_value(tree_iter, 0)
        uri = self._feed.entries[index].links[0].href
        summary = model.get_value(tree_iter, 1)
        
        self.emit('item-selected', uri, summary)
    
    def update(self):
        model = self._tree_view.get_model()
        
        self._feed = feedparser.parse(self.uri)
        logging.debug(self._feed)
        
        for i, e in enumerate(self._feed.entries):
            title = u'<b>%s</b>' % e.title
            descr = e.description
            
            t = e.updated_parsed
            date = u'<b>Date</b>: %s %s %s' % (t.tm_mday, t.tm_mon, t.tm_year)
            
            rating_head = u'<span foreground="#000">%s</span>' \
                          % u'\u2605' * int(e.comments)
            rating_tail = u'<span foreground="#aaa">%s</span>' \
                          % u'\u2605' * (5-int(e.comments))
            rating = '\t<b>Rating</b>: ' + rating_head + rating_tail
            
            row = '\n'.join([title, descr, date + rating])
            model.append([i, row])

    
class FeedItem(gtk.VBox):
    __gtype_name__ = "SugarFeedItem"
    
    def __init__(self):
        gtk.VBox.__init__(self)
        
        