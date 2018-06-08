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

    def stringReceived(self, info):
        res_data = json.loads(info)
        handel = HandelResponse(res_data, self)
        handel.start()
        print(info)

    def connectionLost(self, reason):
        print('closa Control Connection')


class HandelResponse(object):
    """处理服务器响应"""
    def __init__(self, res_data: dict, protocol):
        """
        Args:
            res_data: 服务端响应数据
            protocol: twisted Protocol
        """
        self.res_data = res_data
        self.protocol = protocol

    def start(self):
        fun = self.get_handel_fun()
        if fun != "error":
            fun()
        else:
            log.msg('undefined cmd: ', self.res_data.get('res', 'null'))
            self.protocol.transport.loseConnection()

    def get_handel_fun(self):
        return {
            'success': self.__req_new_tunnel,
            'start_tunnel': self.__req_private_connection,
        }.get(self.res_data.get('res'), 'error')

    def __req_new_tunnel(self):
        req_new_tunnel = {
            'client_id': self.res_data.get('client_id'),
            'port': 80,
            'os': platform.platform(),
            'cmd': 'new_tunnel'
        }
        # 请求服务端创建隧道
        self.protocol.sendString(json.dumps(req_new_tunnel).encode('utf8'))

    def __req_private_connection(self):
        req_new_tunnel = {
            'cmd': 'new_proxy'
        }
        self.protocol.sendString(json.dumps(req_new_tunnel).encode('utf8'))
