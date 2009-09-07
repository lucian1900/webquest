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
import feedparser

class WebquestView(gtk.ScrolledWindow):
    __gtype_name__ = 'SugarWebquestView'
    
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        self.feed = None
        
        self._vbox = gtk.VBox(spacing=5)
        self.add(self._vbox)
        self._vbox.show()
        
        self._summary = gtk.Label()
        self._vbox.pack_start(self._summary, expand=False)
        self._summary.show()
        
        self._description = gtk.Label()
        self._vbox.pack_start(self._description, expand=False)
        self._description.set_alignment(0.12,0)
        self._description.set_line_wrap(True)
        self._description.show()
                
    def set(self, uri, summary):
        self._summary.set_markup(summary)
        
        self._description.set_markup('''\n<b>Detailed description (placeholder)</b>\nasdassdfasdgdhsrgasdfaefegfsgdfasdkjnasdkjas;ldkfsadlkfjsadkfaslkdcmnaleiiflsjf\ng\nfdgs\nfdgsdfgdfgsdfg\n\n<b>Tasks</b>\n  1. asda\n  2. asd\n  3. 4545''')
        
        self.feed = feedparser.parse(uri)
        logging.debug('@@@@@ %s' % self.feed)
        open('/media/desktop/webq.json', 'w').write(str(self.feed))
