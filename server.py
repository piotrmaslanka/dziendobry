"""
DZIENDOBRY is a simple, yet powerful, robuse and extensible service discovery protocol.
The server is only a single script in size, and configuration is inline.

See README for protocol specification, COPYING for license.
"""

services = {
    '50985b5c-b8ac-4e12-af6f-127a4e53193f': ''      # Sample Service
}

import uuid, struct, socket, select

if __name__ == '__main__':

    # Reparse data
    ns = {}
    for k, v in services.iteritems():
        ns[uuid.UUID(k)] = v
    services = ns

    # Construct a response packet
    rp = 'WITAMUPRZEJMIE\x00'
    for k, v in services.iteritems():
        rp = rp + chr(16 + len(v)) + k.bytes + v

    # Bind ports
    ports_to_listen = []
    try:
        port5000 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port5000.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port5000.bind(('', 5000))
        ports_to_listen.append(port5000)
    except socket.error:
        pass

    try:
        port6000 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port6000.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port6000.bind(('', 6000))
        ports_to_listen.append(port6000)
    except socket.error:
        pass

    try:
        port7000 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port7000.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port7000.bind(('', 7000))
        ports_to_listen.append(port7000)
    except socket.error:
        pass

    # Select on them

    while True:
        rx, ws, xs = select.select(ports_to_listen, [], [], 10)

        for r in rx:
            data, addr = r.recvfrom(1024)
            resp_ip, resp_port = addr
            if not data.startswith('DZIENDOBRY'): continue  # Malformed

            data = data[10:]        # skip DZIENDOBRY

            while len(data) > 1:    # Process options
                option, optsize = ord(data[0]), ord(data[1])

                if option == 0:       # Respond only to a UUID
                    if optsize != 16 or len(data) < 18:
                        resp_ip = None
                        break               # MALFORMED PACKET
                    uid = uuid.UUID(bytes=data[2:18])
                    if uid not in services:
                        resp_ip = None      # don't respond, don't process anymore
                        break
                    data = data[18:]    # cut out UUID

                elif option == 1:      # Respond to a different port
                    if optsize != 2:
                        resp_ip = None
                        break           # MALFORMED PACKET
                    resp_port, = struct.unpack('!H', data[2:4])
                    data = data[4:]     # cut out port

            if resp_ip == None: # We shouldn't respond
                continue

            # We can respond
            r.sendto(rp, (resp_ip, resp_port))
