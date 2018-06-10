import json

from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver, LineOnlyReceiver
from twisted.internet.protocol import Protocol

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

    #def dataReceived(self, data):
        # print(data)
        # #req_data = json.loads(data.decode('utf8'))
        # req_data = data.decode('utf8').split('=id-ljl')
        # log.msg(data)
        # tunnel_conn = ProxyProtocol.tunnel_msg.get(str(req_data[0]))
        # if not tunnel_conn:
        #     log.msg(req_data[0])
        # tunnel_conn.transport.write(req_data[1].encode('utf8'))
        #print(11111)

    def stringReceived(self, data):
        # req_data = json.loads(data.decode('utf8'))
        #log.msg(data)
        log.msg(str(data[:8]))
        #req_data = data.decode().split('=id-ljl')
        #log.msg(data)
        tunnel_conn = ProxyProtocol.tunnel_msg.get(data[:8].decode('utf8'))
        tunnel_conn.transport.write(data[8:])

    def connectionLost(self, reason):
        #  self.factory.tunnel.clients[self.factory.client_id] = None
        log.msg('close connection ')
