#!/usr/bin/python

import logging

log = logging.getLogger('rhsm-app.' + __name__)

import dbus
import dbus.service
import dbus.mainloop.glib

import slip.dbus
import slip.dbus.service

from rhsm.dbus.services import decorators
from rhsm.dbus.services import base_service
from rhsm.dbus.services import base_properties

# TODO: move these to a config/constants module
FACTS_DBUS_BUS_NAME = "com.redhat.Subscriptions1.Facts.User"
FACTS_DBUS_INTERFACE = "com.redhat.Subscriptions1.Facts"
FACTS_DBUS_PATH = "/com/redhat/Subscriptions1/Facts/User"
PK_FACTS_COLLECT = "com.redhat.Subscriptions1.Facts.collect"


class Facts(base_service.BaseService):

    default_polkit_auth_required = PK_FACTS_COLLECT
    persistent = True
    default_props_data = {'version': '-infinity+37',
                          'answer': '42',
                          'last_update': 'before now, probably'}

    def __init__(self, *args, **kwargs):
        super(Facts, self).__init__(*args, **kwargs)
        self._interface_name = FACTS_DBUS_INTERFACE
        self._props = base_properties.BaseProperties(self._interface_name,
                                                     data=self.default_props_data,
                                                     prop_changed_callback=self.PropertiesChanged)

    @slip.dbus.polkit.require_auth(PK_FACTS_COLLECT)
    @decorators.dbus_service_method(dbus_interface=FACTS_DBUS_INTERFACE,
                                    in_signature='ii',
                                    out_signature='i')
    @decorators.dbus_handle_exceptions
    def AddInts(self, int_a, int_b, sender=None):
        log.debug("AddInts %s %s, int_a, int_b")
        total = int_a + int_b
        return total

    @slip.dbus.polkit.require_auth(PK_FACTS_COLLECT)
    @decorators.dbus_service_method(dbus_interface=FACTS_DBUS_INTERFACE,
                                   out_signature='s')
    @decorators.dbus_handle_exceptions
    def Return42(self, sender=None):
        log.debug("Return42")
        return '42'

    @dbus.service.signal(dbus_interface=FACTS_DBUS_INTERFACE,
                         signature='')
    @decorators.dbus_handle_exceptions
    def ServiceStarted(self):
        log.debug("Facts serviceStarted emit")


def run():
    base_service.run_service(dbus.SystemBus,
                             FACTS_DBUS_BUS_NAME,
                             FACTS_DBUS_INTERFACE,
                             FACTS_DBUS_PATH,
                             Facts)
