#!/usr/bin/env python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet import ssl, task, protocol, endpoints, defer
from twisted.python.modules import getModule
from twisted.protocols.policies import Protocol
from twisted.protocols.policies import ClientFactory


class ServerProtocol(Protocol):

    def connectionMade(self):
        print(5)
        print(self.transport.getPeer())
        self.transport.write(b'312312312')

    def dataReceived(self, data):
        print(2)
        print(data)

    def connectionLost(self, reason):
        print('cloas1')


class ServerFactory(ClientFactory):

    protocol = ServerProtocol

    def __init__(self):
        self.client = ''


def main():
    from twisted.internet import reactor
    server_factory = ServerFactory()
    certData = getModule(__name__).filePath.sibling('cert.crt').getContent()
    authority = ssl.Certificate.loadPEM(certData)
    options = ssl.optionsForClientTLS(u'localhost', authority)
    reactor.connectSSL('localhost', 8888, server_factory, options, timeout=30)
    reactor.run()


if __name__ == "__main__":
    main()
