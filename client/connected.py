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

        factory = protocol.ClientFactory()
        factory.protocol = ProxyProtocol
        # 开始连接
        from twisted.internet import reactor
        reactor.connectSSL(self.host, self.port, factory, options, timeout=30)
        log.msg('connect {}:{}'.format(self.host, self.port))


class ProxyProtocol(NetstringReceiver):
    tunnel_msg = {}

    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())
        factory = LocalFactory()
        from twisted.internet import reactor
        reactor.connectTCP('localhost', 8888, factory)

    def stringReceived(self, info):
        req_data = json.loads(info)
        tunnel_conn = ProxyProtocol.tunnel_msg.get(req_data['id'])
        tunnel_conn.sendString(req_data['body'])

    def connectionLost(self, reason):
        self.factory.tunnel.clients[self.factory.client_id] = None
        log.msg('close connection ')


class LocalProtocol(NetstringReceiver):
    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())
        factory = LocalProtocol()
        from twisted.internet import reactor
        reactor.connectTCP('localhost', 8888, factory)

    def stringReceived(self, info):
        req_data = json.loads(info)
        tunnel_conn = ProxyProtocol.tunnel_msg.get(req_data['id'])
        tunnel_conn.sendString(req_data['body'])

    def connectionLost(self, reason):
        self.factory.tunnel.clients[self.factory.client_id] = None
        log.msg('close connection ')


class LocalFactory(protocol.ClientFactory):
    protocol = LocalProtocol
