from twisted.internet import protocol
from twisted.protocols.basic import NetstringReceiver


class Tunnel(object):
    tunnels = []

    def __init__(self):
        self.tunnels = []

    def new_tunnel(self, port):
        factory = protocol.ServerFactory()
        factory.protocol = TunnelProtocol

        from twisted.internet import reactor

        reactor.listenTCP(port, factory, interface='0.0.0.0')


class TunnelProtocol(NetstringReceiver):
    def connectionMade(self):
        pass

    def stringReceived(self, info):
        pass

    def connectionLost(self, reason):
        pass