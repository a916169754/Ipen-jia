import json
import platform

from twisted.internet import ssl, protocol
from twisted.python import log
from twisted.protocols.basic import NetstringReceiver


class Controller(object):
    """连接服务器"""
    def __init__(self, domain: str, host: str, port: int, tls_conf: dict):
        """
        Args:
            host: 服务器ip
            port: 端口
            tls_conf: tls配置信息
        """
        self.domain = domain
        self.host = host
        self.port = port
        self.tls_conf = tls_conf

    def connection(self):
        """连接服务器"""
        # 信任服务器证书
        with open(self.tls_conf['cert'], 'r') as f:
            cert_data = f.read()
        authority = ssl.Certificate.loadPEM(cert_data)
        options = ssl.optionsForClientTLS(self.domain, authority)

        factory = protocol.ClientFactory()
        factory.protocol = ControllerProtocol
        # 开始连接
        from twisted.internet import reactor
        reactor.connectSSL(self.host, self.port, factory, options, timeout=30)
        log.msg('connect {}:{}'.format(self.host, self.port))


class ControllerProtocol(NetstringReceiver):
    def connectionMade(self):
        log.msg('connect {}: success'.format(self.transport.getPeer()))
        req_new_tunnel = {
            'client_id': '',
            'os': platform.platform(),
            'cmd': 'new_tunnel'
        }
        # 请求服务端创建隧道
        self.sendString(json.dumps(req_new_tunnel).encode('utf8'))

    def stringReceived(self, string):
        print(string)

    def connectionLost(self, reason):
        print('closa Control Connection')
