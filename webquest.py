from gettext import gettext as _

import gtk
import feedparser

class WebquestView(gtk.ScrolledWindow):
    __gtype_name__ = 'SugarWebquestView'
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self._feed = None
        
        self._vbox = gtk.VBox(spacing=5)
        self.add(self._vbox)
        self._vbox.show()
        
        self._summary = gtk.Label('placeholder summary')
        self._vbox.pack_start(self._summary, expand=False)
        self._summary.show()
        
        self._description = gtk.Label('placeholder description')
        self._vbox.pack_start(self._description, expand=False)
        self._description.justify = gtk.JUSTIFY_FILL
        self._description.show()
                
    def set(self, uri, summary):
        self._summary.set_markup(summary)
        
        self._description.set_markup('''\n<b>Detailed description (placeholder)</b>\nasdassdfasdgadsssssssssssssasdasdfasgfgdhsrgasdfaefegfsgdfasdkjnasdkjas;ldkfsadlkfjsadkfaslkdcmnaleiiflsjf\ng\nfdgs\nfdgsdfgdfgsdfg\n\n<b>Tasks</b>\n  1. asda\n  2. asd\n  3. 4545''')
        
        self._feed = feedparser.parse(uri)
