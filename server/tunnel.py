import json

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver


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
                port = p.port
            Tunnel.tunnels[str(port)] = self
        return port


class TunnelProtocol(NetstringReceiver):

    def connectionMade(self):
        pass

    def stringReceived(self, info):
        hostname = ''
        msg_id = str(id(self))

        protocol = self.factory.tunnel.clients.get(hostname)
        protocol.tunnel_msg[msg_id] = self

        if protocol:
            msg = {
                'id': msg_id,
                'body': info
            }
            protocol.sendString(json.dumps(msg))

    def connectionLost(self, reason):
        pass


class TunnelFactory(ServerFactory):
    protocol = TunnelProtocol

    def __init__(self, tunnel):
        self.tunnel = tunnel
