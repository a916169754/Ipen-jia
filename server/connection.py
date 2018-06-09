import json

from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver

from tunnel import Tunnel


class ProxyConnServer(object):
    """此连接作为隧道流量的承载者"""
    def __init__(self, port: int, tls_conf: dict, client_id: str, tunnel: Tunnel):
        """
        Args:
            port: 端口号
            tls_conf: tls 配置信息
            client_id: 客户端id
            tunnel: 隧道
        """
        self.port = port
        self.tls_conf = tls_conf
        self.client_id = client_id
        self.tunnel = tunnel

    def start(self):
        ssl_context = ssl.DefaultOpenSSLContextFactory(
            self.tls_conf['private'],
            self.tls_conf['cert'],
        )

        factory = protocol.ServerFactory()
        factory.protocol = ProxyProtocol
        factory.tunnel = self.tunnel
        factory.client_id = self.client_id

        from twisted.internet import reactor
        reactor.listenSSL(self.port, factory, ssl_context)


class ProxyProtocol(NetstringReceiver):
    tunnel_msg = {}

    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())
        self.factory.tunnel.clients[self.factory.client_id] = self

    def stringReceived(self, info):
        req_data = json.loads(info)
        tunnel_conn = ProxyProtocol.tunnel_msg.get(req_data['id'])
        tunnel_conn.sendString(req_data['body'])

    def connectionLost(self, reason):
        self.factory.tunnel.clients[self.factory.client_id] = None
        log.msg('close connection ')
