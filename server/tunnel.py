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

            reactor.listenTCP(port, factory, interface='0.0.0.0')
            #  记录
            self.clients[str(client_id)] = None
            #  self.clients.append({'client_id': client_id, 'protocol': None})
            Tunnel.tunnels[str(port)] = self


class TunnelProtocol(NetstringReceiver):
    def connectionMade(self):
        pass

    def stringReceived(self, info):
        hostname = ''
        protocol = self.factory.tunnel.clients.get(hostname)
        if protocol:
            protocol.sendString(info)

    def connectionLost(self, reason):
        pass


class TunnelFactory(ServerFactory):
    protocol = TunnelProtocol

    def __init__(self, tunnel):
        self.tunnel = tunnel
