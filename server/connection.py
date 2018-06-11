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

    def listen(self):
        ssl_context = ssl.DefaultOpenSSLContextFactory(
            self.tls_conf['private'],
            self.tls_conf['cert'],
        )

        factory = protocol.ServerFactory()
        factory.protocol = ProxyProtocol
        factory.tunnel = self.tunnel
        factory.client_id = self.client_id

        from twisted.internet import reactor
        p = reactor.listenSSL(self.port, factory, ssl_context)
        return p.getHost().port


class ProxyProtocol(NetstringReceiver):
    tunnel_msg = {}

    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())
        self.factory.tunnel.clients[self.factory.client_id] = self

    def stringReceived(self, data):
        log.msg(str(data[:8]))

        tunnel_conn = ProxyProtocol.tunnel_msg.get(data[:8].decode('utf8'))
        if data[8:] == b'local server close':
            tunnel_conn.transport.loseConnection()
            return
        tunnel_conn.transport.write(data[8:])

    def connectionLost(self, reason):
        self.factory.tunnel.clients.pop(self.factory.client_id)
        log.msg('close connection ')
