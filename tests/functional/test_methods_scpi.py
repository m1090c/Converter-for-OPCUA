# -*- coding: UTF-8 -*-
# Copyright (c) 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
sys.path.append("../../pyutilities")
import logging
import time

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()

from opcua import Client
from opcua import ua
from security.config_security import UaSecurity


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    #logger = logging.getLogger("KeepAlive")
    # logger.setLevel(logging.DEBUG)

    client = Client("opc.tcp://localhost:4840")
    uasecurity = UaSecurity()
    if uasecurity.get_securitytype() == 'tls':
        server_cert, client_cert, private_key = uasecurity.get_certificates()
        if server_cert is None:
            print('tls is enabled, but server cert is missing with current configuration')
            sys.exit(-1)
        if private_key is None:
            print('tls is enabled, but private key is missing with current configuration')
            sys.exit(-1)
        client.load_client_certificate(server_cert)
        client.load_private_key(private_key)

    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always
        # be in address space such as Root or Objects
        root = client.get_root_node()
        print("Root node is: ", root)
        objects = client.get_objects_node()
        print("Objects node is: ", objects)

        # Node objects have methods to read and write node attributes as well
        # as browse or populate address space
        print("Children of root are: ", root.get_children())

        obj = root.get_child(["0:Objects"])
        scpi = obj.get_child(["2:ScpiPlugin"])

        # calling a method on server
        # tcp
        print('\r\ntest scpi open @tcp:127.0.0.1')
        res = scpi.call_method("2:open", "tcp:127.0.0.1:80")
        print("method result is: ", res)

        print('\r\ntest scpi state @tcp:127.0.0.1')
        res = scpi.call_method("2:state", "tcp:127.0.0.1:80")
        print("method result is: ", res)

        print('\r\ntest scpi send @tcp:127.0.0.1')
        res = scpi.call_method("2:send", "tcp:127.0.0.1:80", "TST123")
        print("method result is: ", res)

        print('\r\ntest scpi close @tcp:127.0.0.1')
        res = scpi.call_method("2:close", "tcp:127.0.0.1:80")
        print("method result is: ", res)

        # calling a method on server
        # ser
        print('\r\ntest scpi open @ser:/dev/ttyS100')
        res = scpi.call_method(
            "2:open",
            "ser:/dev/ttyS100",
            "9600-8-N-2-5-1-0-0")
        print("method result is: ", res)

        print('\r\ntest scpi state @ser:/dev/ttyS100')
        res = scpi.call_method("2:state", "")
        print("method result is: ", res)

        print('\r\ntest scpi send @ser:/dev/ttyS100')
        res = scpi.call_method("2:send", "ser:/dev/ttyS100", "*IDN?\r\n")
        print("method result is: ", res)

        print('\r\ntest scpi close @ser:/dev/ttyS100')
        res = scpi.call_method("2:close", "ser:/dev/ttyS100")
        print("method result is: ", res)

        print('\r\ndone')

    finally:
        client.disconnect()
