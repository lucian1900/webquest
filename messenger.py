#    Copyright (C) 2007, One Laptop Per Child
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import logging
import dbus
from dbus.gobject_service import ExportedGObject
import base64

SERVICE = "org.sugarlabs.WebquestActivity"
IFACE = SERVICE
PATH = "/org/sugarlabs/WebquestActivity"

_logger = logging.getLogger('messenger')

class Messenger(ExportedGObject):
    def __init__(self, tube, is_initiator, model):
        ExportedGObject.__init__(self, tube, PATH)
        self.tube = tube
        self.is_initiator = is_initiator
        self.members = []
        self.entered = False
        self.model = model
        self.bus_name = None
        self.tube.watch_participants(self.participant_change_cb)

    def participant_change_cb(self, added, removed):
        _logger.debug('Participants change add=%s    rem=%s'
                      %(added, removed))
        for handle, bus_name in added:
            _logger.debug('Add member handle=%s  bus_name=%s'
                          %(str(handle), str(bus_name)))
            self.members.append(bus_name)
            
        for handle in removed:
            _logger.debug('Remove member %r', handle)
            try:
                self.members.remove(self.tube.participants[handle])
            except ValueError:
                _logger.debug('Remove member %r - already absent', handle)
                        
        if not self.entered:
            self.tube.add_signal_receiver(self._add_role_receiver, '_add_role',
                                          IFACE, path=PATH,
                                          sender_keyword='sender',
                                          byte_arrays=True)
            self.bus_name = self.tube.get_unique_name()
            if self.is_initiator:
                _logger.debug('Initialising a new shared browser, I am %s .'
                              %self.tube.get_unique_name())                
            else:               
                # sync with other members
                _logger.debug('Joined I am %s .'%self.bus_name)                
                for member in self.members:
                    if member != self.bus_name:
                        _logger.debug('Get info from %s' %member)
                        self.tube.get_object(member, PATH).sync_with_members(
                            dbus_interface=IFACE,
                            reply_handler=self.reply_sync, error_handler=lambda
                            e:self.error_sync(e, 'transfering file'))
                                                                         
        self.entered = True
        
    def reply_sync(self, a_ids, sender):
        a_ids.pop()
        self.tube.get_object(sender, PATH).send_role(sender, 
                                                     self.model.my_role)

    def error_sync(self, e, when):    
        _logger.error('Error %s: %s'%(when, e))

    @dbus.service.method(dbus_interface=IFACE, in_signature='as',
                         out_signature='ass', sender_keyword='sender')
    def sync_with_members(self, b_ids, sender=None):
        '''Sync with members '''
        b_ids.pop()
        # roles the caller wants from me
        self.tube.get_object(sender, PATH).send_role('owner', 'role')
        a_ids = self.model.get_roles_ids()
        a_ids.append('')
        # roles I want from the caller
        return (a_ids, self.bus_name)               
        
    @dbus.service.method(dbus_interface=IFACE, in_signature='ss', 
                         out_signature='')
    def send_role(self, owner, role):
        a_ids = self.model.get_roles_ids()
        if identifier not in a_ids:
            self.model.add_role(owner, role)
                    
    @dbus.service.signal(IFACE, signature='sss')
    def _add_role(self, identifier, owner, role):        
        '''Signal to send the role information (add)'''
        _logger.debug('Add Link: %s '%url)
        
    def _add_role_receiver(self, identifier, owner, role):
        '''Member sent a role'''
        handle = self.tube.bus_name_to_handle[sender]            
        if self.tube.self_handle != handle:
        #    thumb = base64.b64decode(buf)
        #    self.model.add_link(url, title, thumb, owner, color, timestamp) 
        #    _logger.debug('Added link: %s to linkbar.'%(url))
            pass