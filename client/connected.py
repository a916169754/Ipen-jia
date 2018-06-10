import json

from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver, LineOnlyReceiver
from twisted.internet.protocol import Protocol


class ProxyConnClient(object):
    def __init__(self, host: str, port: int, tls_conf: dict, domain: str, local_port: int):
        """
        Args:
            port: 端口号
            tls_conf: tls 配置信息
            local_port: 本地端口
        """
        self.host = host
        self.port = port
        self.tls_conf = tls_conf
        self.domain = domain
        self.local_port = local_port

    def conn(self):
        with open(self.tls_conf['cert'], 'r') as f:
            cert_data = f.read()
        authority = ssl.Certificate.loadPEM(cert_data)
        options = ssl.optionsForClientTLS(self.domain, authority)

        factory = ProxyFactory(self.local_port)
        factory.protocol = ProxyProtocol
        # 开始连接
        from twisted.internet import reactor
        reactor.connectSSL(self.host, self.port, factory, options, timeout=30)
        log.msg('proxy connect {}:{}'.format(self.host, self.port))


class ProxyProtocol(NetstringReceiver):

    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())

    def dataReceived(self, data):
        log.msg(data)
        req_data = json.loads(data.decode('utf8'))

        factory = LocalFactory(self, req_data['id'], req_data['body'])
        from twisted.internet import reactor
        reactor.connectTCP('localhost', self.factory.local_port, factory)

    def stringReceived(self, string):
        pass

    def connectionLost(self, reason):
        log.msg('close connection ')


class ProxyFactory(protocol.ClientFactory):
    protocol = ProxyProtocol

    def __init__(self, local_port=80):
        super(ProxyFactory, self).__init__()
        self.local_port = local_port

    def clientConnectionFailed(self, connector, reason):
        #  本地服务未启动，1秒后尝试重新链接
        print(1)
        from twisted.internet import reactor

        reactor.callLater(1, connector.connect)

    def clientConnectionLost(self, connector, reason):
        # 本地链接断开
        print('lost coon')


class LocalProtocol(Protocol):
    def __init__(self):
        self.res = b""

    def connectionMade(self):
        self.factory.proxy.factory.local = self
        self.transport.write(self.factory.msg_body.encode('utf8'))

    def dataReceived(self, data):
        log.msg(data)
        #self.res += data
        #log.msg(data)
        # res = {
        #     'id': self.factory.msg_id,
        #     'body': data.decode('utf8')
        # }
        #log.msg(res)
        res = str(self.factory.msg_id).encode('utf8') + data
        log.msg(res)
        #self.factory.proxy.transport.getHandle().sendall(data)
        self.factory.proxy.sendString(res)
        #self.transport.loseConnection()

    def connectionLost(self, reason):
        #res = (str(self.factory.msg_id) + '=id-ljl').encode('utf8') + self.res
        #self.factory.proxy.transport.write(res)
        log.msg('close connection ')


class LocalFactory(protocol.ClientFactory):
    protocol = LocalProtocol

    def __init__(self, proxy, msg_id, msg_body):
        self.proxy = proxy
        self.msg_id = msg_id
        self.msg_body = msg_body
