import time

from twisted.internet.protocol import ClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver

none_respone = b'HTTP/1.0 200 OK\r\nDate: Mon, 28 May 2018 07:28:47 GMT\r\nServer: WSGIServer/0.2 CPython/3.6.2\r\nContent-Type: text/html; charset=utf-8\r\nX-Frame-Options: SAMEORIGIN\r\nContent-Length: 8\r\n\r\nlocal server inactave'


class LocalProtocol(Protocol):

    def connectionMade(self):
        print('new connection local 8888')
        self.factory.proxy.local = self

    def dataReceived(self, data):
        print(3)
        print(data)
        self.factory.proxy.transport.write(data)

    def connectionLost(self, reason):
        print('cloas')
        from twisted.internet import reactor
        local_factory = LocalFactory(self.factory.proxy)
        reactor.connectTCP('localhost', 8888, local_factory)


class LocalFactory(ClientFactory):

    protocol = LocalProtocol

    def __init__(self, proxy):
        self.proxy = proxy

    def clientConnectionFailed(self, connector, reason):
        #  本地服务未启动，1秒后尝试重新链接
        from twisted.internet import reactor

        reactor.callLater(1, connector.connect)
        #connector.connect()

    def clientConnectionLost(self, connector, reason):
        # 本地链接断开
        print('duanle')
        delattr(self.proxy, 'local')


class ServerProtocol(Protocol):

    def connectionMade(self):
        print(5)
        from twisted.internet import reactor
        local_factory = LocalFactory(self)
        reactor.connectTCP('localhost', 8888, local_factory)

    def dataReceived(self, data):
        print(2)
        print(data)
        if hasattr(self, 'local'):
            self.local.transport.write(data)
        else:
            self.transport.write(none_respone)

    def connectionLost(self, reason):
        print('cloas1')


class ServerFactory(ClientFactory):

    protocol = ServerProtocol

    def __init__(self):
        self.client = ''


def main():
    from twisted.internet import reactor
    server_factory = ServerFactory()
    print(1)
    reactor.connectTCP('0.0.0.0', 2333, server_factory, timeout=30)
    reactor.run()


if __name__ == "__main__":
    main()
