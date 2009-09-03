from gettext import gettext as _

import gtk
import feedparser

class WebquestView(gtk.ScrolledWindow):
    __gtype_name__ = 'SugarWebquestView'
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self._feed = None
        
        self._view = gtk.VBox(spacing=5)
        self.add(self._view)
        
        self._summary = gtk.Label('placeholder summary')
        self._view.pack_start(self._summary, expand=False)
        
        self._description = gtk.Label('placeholder description')
        self._view.pack_start(self._description, expand=False)
        
    def set(self, uri, summary):
        self._summary.set_markup(summary)
        
        self._feed = feedparser.parse(uri)
