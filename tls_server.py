import sys

from twisted.internet import ssl, protocol, task, defer
from twisted.python import log
from twisted.python.modules import getModule
from twisted.protocols.basic import LineOnlyReceiver


sslContext = ssl.DefaultOpenSSLContextFactory(
    'ssl/private.pem',  # 私钥
    'cert.crt',  # 公钥
)



class ThroughProxyProtocol(LineOnlyReceiver):
    def connectionMade(self):
        print("listen 2333")
        self.transport.write(b'312312312')
        #

    def dataReceived(self, data):
        print(data)
        #if hasattr(self, 'proxy'):

    def connectionLost(self, reason):
        print('cloas3')



def main():
    factory = protocol.Factory()
    factory.protocol = ThroughProxyProtocol

    from twisted.internet import reactor
    reactor.listenSSL(8888, factory, sslContext)

    reactor.run()


if __name__ == "__main__":
    main()
