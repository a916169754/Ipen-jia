from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver

from tunnel import Tunnel


class ProxyConnServer(object):
    """此连接作为隧道流量的承载者"""
    def __init__(self, tls_conf, client_id):
        """
        Args:
            tls_conf: tls 配置信息
            client_id: 客户端id
        """
        self.tls_conf = tls_conf
        self.client_id = client_id

    def start(self):
        ssl_context = ssl.DefaultOpenSSLContextFactory(
            self.tls_conf['private'],
            self.tls_conf['cert'],
        )

        factory = protocol.ServerFactory()
        factory.protocol = ProxyProtocol
        factory.client_id = self.client_id

        from twisted.internet import reactor
        reactor.listenSSL(self.port, factory, ssl_context)


class ProxyProtocol(NetstringReceiver):
    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())
        tunnel = Tunnel.tunnels.get(self.factory.client_id)
        tunnel.clients
        self.sendString(json.dumps(res))

    def stringReceived(self, info):
        req_data = json.loads(info)
        handel = HandelRequest(req_data, self)
        handel.start()

    def connectionLost(self, reason):
        log.msg('close connection ')