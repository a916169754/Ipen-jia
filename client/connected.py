import json

from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver
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
        """
        接受到数据时，转发给本地端口
        """
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


class LocalProtocol(Protocol):

    def connectionMade(self):
        log.msg('data: ', self.factory.msg_body)

        self.factory.proxy.factory.local = self
        self.transport.write(self.factory.msg_body.encode('utf8'))

    def dataReceived(self, data):
        """
        将本地服务的回复回传给服务端
        数据头部增加消息id，用以区分不同客户端的消息
        """
        log.msg(data[:20])

        res = str(self.factory.msg_id).encode('utf8') + data
        self.factory.proxy.sendString(res)

    def connectionLost(self, reason):
        res = str(self.factory.msg_id).encode('utf8') + b'local server close'
        self.factory.proxy.sendString(res)


class LocalFactory(protocol.ClientFactory):
    protocol = LocalProtocol

    def __init__(self, proxy, msg_id, msg_body):
        self.proxy = proxy
        self.msg_id = msg_id
        self.msg_body = msg_body
