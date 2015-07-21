from __future__ import print_function
import socket, uuid, time, struct


class Scanner(object):

    class ServiceInfo(object):
        def __init__(self, ip_address, service_uuid, extra_info):
            """
            :param ip_address: IP address of discovered service
            :param service_uuid: UUID of discovered service
            :type service_uuid: uuid.UUID
            :param extra_info: str, extra advertised info
            """
            self.ip_address = ip_address
            self.service_uuid = service_uuid
            self.extra_info = extra_info

        def __eq__(self, other):
            return self.ip_address == other.ip_address and self.service_uuid == other.service_uuid

        def __hash__(self):
            return self.ip_address.__hash__() ^ self.service_uuid.__hash__()

    def __init__(self, **options):
        """options will be sent as part of the request"""
        opts = ''
        for opt_i, opt_v in options.iteritems():
            opts += chr(opt_i) + chr(len(opt_v)) + opt_v

        self.request = 'DZIENDOBRY' + opts

    def discover(self, wait_time=5):
        """
        This will take wait_time seconds and return a set of Scanner.ServiceInfo elements
        :param wait_time: seconds to wait on respones
        :return: set of Scanner.ServiceInfo elements
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0)
        _, port = sock.getsockname()

        sock.sendto(self.request+struct.pack('!BBH', 1, 2, port), ('255.255.255.255', 5000))
        sock.sendto(self.request+struct.pack('!BBH', 1, 2, port), ('255.255.255.255', 6000))
        sock.sendto(self.request+struct.pack('!BBH', 1, 2, port), ('255.255.255.255', 7000))

        time.sleep(wait_time)

        responses = set()

        while True:
            try:
                resp, address = sock.recvfrom(1024)
            except socket.error:
                break

            if not resp.startswith('WITAMUPRZEJMIE'):
                continue

            resp = resp[14:]

            if ord(resp[0]) < 8:
                continue        # can't be less than 8
            uid = uuid.UUID(bytes=resp[1:17])
            asi = resp[17:ord(resp[0])]

            responses.add(Scanner.ServiceInfo(address[0], uid, asi))

        return responses


# dict of (uuid => tuple(service name, vendor)
KNOWN_SERVICES = {
    uuid.UUID('0ababec8-0851-4818-9c62-5bbd82cd3687'): ('SMOK Z', 'DMS')
}

if __name__ == '__main__':
    for serv in Scanner().discover(wait_time=10):
        if serv.service_uuid in KNOWN_SERVICES:
            print('[%s] %s by %s. Extras=%s' % (serv.ip_address,
                                     KNOWN_SERVICES[serv.service_uuid][0],
                                     KNOWN_SERVICES[serv.service_uuid][1],
                                     repr(serv.extra_info))
                  )
        else:
            print('[%s] %s. Extras=%s' % (serv.ip_address,
                                          serv.service_uuid,
                                          repr(serv.extra_info)))
    print('Discovery complete, press [ENTER]')
    raw_input()