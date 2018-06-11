import json
import re

from twisted.python import log
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import Protocol


class Tunnel(object):
    tunnels = {}

    def __init__(self):
        self.clients = {}

    def new_tunnel(self, port, client_id):
        tunnel = Tunnel.tunnels.get(str(port), None)
        if tunnel:
            tunnel.clients[str(client_id)] = None
        else:
            factory = TunnelFactory(self)

            from twisted.internet import reactor

            p = reactor.listenTCP(port, factory, interface='0.0.0.0')
            #  记录
            self.clients[str(client_id)] = None

            if not port:
                port = p.getHost().port
            Tunnel.tunnels[str(port)] = self
        return port


class TunnelProtocol(Protocol):

    def dataReceived(self, data):
        p = re.compile('(?<=Host: ).+?(?=\r\n)')
        host = re.search(p, data.decode('utf8'))
        if not host:
            log.msg(b'unmatched host')
            self.transport.write('unmatched host')
            self.transport.loseConnection()
            return
        hostname = host[0].split('.')[0]
        msg_id = str(id(self))
        if len(msg_id) > 8:
            msg_id = msg_id[:8]
        elif len(msg_id) < 8:
            msg_id = msg_id.zfill(8)

        protocol = self.factory.tunnel.clients.get(hostname)
        if protocol:
            protocol.tunnel_msg[msg_id] = self

            msg = {
                'id': msg_id,
                'body': data.decode('utf8')
            }
            protocol.transport.write(json.dumps(msg).encode('utf8'))
        else:
            log.msg('unknown server')
            self.transport.write(b'unknown server')
            self.transport.loseConnection()


class TunnelFactory(ServerFactory):
    protocol = TunnelProtocol

    def __init__(self, tunnel):
        self.tunnel = tunnel
