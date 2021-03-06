import json
import platform

from twisted.internet import ssl, protocol
from twisted.python import log
from twisted.protocols.basic import NetstringReceiver

from connected import ProxyConnClient


class Controller(object):
    """连接服务器"""
    def __init__(self, domain: str, host: str, port: int, tls_conf: dict, local_port: int, tunnel_port: int):
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
        self.local_port = local_port
        self.tunnel_port = tunnel_port

    def connection(self):
        """连接服务器"""
        # 信任服务器证书
        with open(self.tls_conf['cert'], 'r') as f:
            cert_data = f.read()
        authority = ssl.Certificate.loadPEM(cert_data)
        options = ssl.optionsForClientTLS(self.domain, authority)

        factory = protocol.ClientFactory()
        factory.protocol = ControllerProtocol
        factory.domain = self.domain
        factory.host = self.host
        factory.tls_conf = self.tls_conf
        factory.local_port = self.local_port
        factory.tunnel_port = self.tunnel_port

        # 开始连接
        from twisted.internet import reactor
        reactor.connectSSL(self.host, self.port, factory, options, timeout=30)
        log.msg('connect {}:{}'.format(self.host, self.port))


class ControllerProtocol(NetstringReceiver):
    def connectionMade(self):
        log.msg('connect {}: success'.format(self.transport.getPeer()))

    def stringReceived(self, info):
        log.msg(info)
        res_data = json.loads(info.decode('utf8'))
        handel = HandelResponse(res_data, self, self.factory.domain, self.factory.host, self.factory.tls_conf,
                                self.factory.local_port, self.factory.tunnel_port)
        handel.start()
        print(info)

    def connectionLost(self, reason):
        print('closa Control Connection')


class ControllerFactory(protocol.ClientFactory):
    protocol = ControllerProtocol

    def clientConnectionFailed(self, connector, reason):
        #  服务端未启动，1秒后尝试重新链接
        from twisted.internet import reactor

        reactor.callLater(1, connector.connect)

    def clientConnectionLost(self, connector, reason):
        # 服务端连接断开
        log.msg('lost server coon')


class HandelResponse(object):
    """处理服务器响应"""
    def __init__(self, res_data: dict, protocol, domain, host, tls_conf, local_port, tunnel_port):
        """
        Args:
            res_data: 服务端响应数据
            protocol: twisted Protocol
        """
        self.res_data = res_data
        self.protocol = protocol
        self.domain = domain
        self.host = host
        self.tls_conf = tls_conf
        self.local_port = local_port
        self.tunnel_port = tunnel_port

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
            'start_tunnel': self.__req_proxy_connection,
            'start_proxy': self.__conn_proxy,
        }.get(self.res_data.get('res'), 'error')

    def __req_new_tunnel(self):
        log.msg('tunnel url: {}.{}:{}'.format(self.res_data.get('client_id'), self.domain, self.tunnel_port))

        req_new_tunnel = {
            'client_id': self.res_data.get('client_id'),
            'port': self.tunnel_port,
            'os': platform.platform(),
            'cmd': 'new_tunnel'
        }
        # 请求服务端创建隧道
        self.protocol.sendString(json.dumps(req_new_tunnel).encode('utf8'))

    def __req_proxy_connection(self):
        req_new_tunnel = {
            'tunnel_port': self.res_data.get('tunnel_port'),
            'client_id': self.res_data.get('client_id'),
            'cmd': 'new_proxy'
        }
        self.protocol.sendString(json.dumps(req_new_tunnel).encode('utf8'))

    def __conn_proxy(self):
        proxy = ProxyConnClient(self.host, self.res_data.get('port'), self.tls_conf, self.domain, self.local_port)
        proxy.conn()
