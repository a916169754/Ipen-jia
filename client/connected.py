import json

from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver

from tunnel import Tunnel


class ProxyConnClient(object):
    def __init__(self, host: str, port: int, tls_conf: dict, domain: str):
        """
        Args:
            port: 端口号
            tls_conf: tls 配置信息
            client_id: 客户端id
            tunnel: 隧道
        """
        self.host = host
        self.port = port
        self.tls_conf = tls_conf
        self.domain = domain

    def start(self):
        with open(self.tls_conf['cert'], 'r') as f:
            cert_data = f.read()
        authority = ssl.Certificate.loadPEM(cert_data)
        options = ssl.optionsForClientTLS(self.domain, authority)

        factory = ProxyFactory()
        factory.protocol = ProxyProtocol
        # 开始连接
        from twisted.internet import reactor
        reactor.connectSSL(self.host, self.port, factory, options, timeout=30)
        log.msg('connect {}:{}'.format(self.host, self.port))


class ProxyProtocol(NetstringReceiver):

    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())

    def stringReceived(self, info):
        req_data = json.loads(info)

        factory = LocalFactory(self, req_data['id'], req_data['body'])
        from twisted.internet import reactor
        reactor.connectTCP('localhost', 8888, factory)

    def connectionLost(self, reason):
        self.factory.tunnel.clients[self.factory.client_id] = None
        log.msg('close connection ')


class ProxyFactory(protocol.ClientFactory):
    protocol = ProxyProtocol

    def clientConnectionFailed(self, connector, reason):
        #  本地服务未启动，1秒后尝试重新链接
        from twisted.internet import reactor

        reactor.callLater(1, connector.connect)

    def clientConnectionLost(self, connector, reason):
        # 本地链接断开
        print('lost coon')


class LocalProtocol(NetstringReceiver):
    def connectionMade(self):
        self.factory.proxy.factory.local = self
        self.sendString(self.factory.msg_body)

    def stringReceived(self, info):
        res = {
            'id': self.factory.msg_id,
            'body': info
        }
        self.factory.proxy.sendString(json.dumps(res))
        self.transport.loseConnection()

    def connectionLost(self, reason):
        log.msg('close connection ')


class LocalFactory(protocol.ClientFactory):
    protocol = LocalProtocol

    def __init__(self, proxy, msg_id, msg_body):
        self.proxy = proxy
        self.msg_id = msg_id
        self.msg_body = msg_body
