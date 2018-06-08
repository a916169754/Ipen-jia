from twisted.internet.protocol import ServerFactory, Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.web import http


class ThroughProtocol(Protocol):

    def connectionMade(self):
        self.factory.server.proxy = self
        print(1)

        # print(type(self.factory.body))
        # self.transport.write(self.factory.body)
        # self.transport.loseConnection()

    def dataReceived(self, data):
        print(data)
        self.factory.server.transport.write(data)

    def connectionLost(self, reason):
        print('cloas2')


class ThroughFactory(ServerFactory):
    protocol = ThroughProtocol

    def __init__(self, server):
        self.server = server


class ThroughProxyProtocol(Protocol):
    def connectionMade(self):
        print("listen 2333")
        factory = ThroughFactory(self)

        from twisted.internet import reactor

        self.p =reactor.listenTCP(8000, factory, interface='0.0.0.0')
        #

    def dataReceived(self, data):
        print(data)
        #if hasattr(self, 'proxy'):
        self.proxy.transport.write(data)

    def connectionLost(self, reason):
        self.p.loseConnection()
        print('cloas3')


class ThroughProxyFactory(ServerFactory):
    protocol = ThroughProxyProtocol

    def __init__(self, body):
        self.body = body


def main():
    factory = ThroughProxyFactory('123445'.encode('utf8'))

    from twisted.internet import reactor

    a = reactor.listenTCP(2333, factory, interface='0.0.0.0')
    print(a.port)

    reactor.run()


if __name__ == "__main__":
    main()
