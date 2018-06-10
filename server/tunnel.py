import json

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
            #  self.clients.append({'client_id': client_id, 'protocol': None})
            if not port:
                port = p.getHost().port
            Tunnel.tunnels[str(port)] = self
        return port


class TunnelProtocol(Protocol):

    def connectionMade(self):
        log.msg(1246)

    def dataReceived(self, data):
        hostname = 'www'
        msg_id = str(id(self))
        if len(msg_id) > 8:
            msg_id = msg_id[:8]
        elif len(msg_id) < 8:
            msg_id = msg_id.zfill(8)

        protocol = self.factory.tunnel.clients.get(hostname)
        protocol.tunnel_msg[msg_id] = self

        if protocol:
            msg = {
                'id': msg_id,
                'body': data.decode('utf8')
            }
            protocol.transport.write(json.dumps(msg).encode('utf8'))

    def connectionLost(self, reason):
        pass


class TunnelFactory(ServerFactory):
    protocol = TunnelProtocol

    def __init__(self, tunnel):
        self.tunnel = tunnel
