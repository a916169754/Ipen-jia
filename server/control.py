import json

from twisted.python import log

from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver


class Control(object):
    """Control Connection 用以与客户端传递指令"""
    def __init__(self, port: int, tls_conf: dict):
        """
        Args:
            port: 端口
            tls_conf: tls配置信息
        """
        self.port = port
        self.tls_conf = tls_conf

    def start_listen(self):
        """建立一个链接，开始监听端口"""
        ssl_context = ssl.DefaultOpenSSLContextFactory(
            self.tls_conf['private'],
            self.tls_conf['cert'],
        )

        factory = protocol.ServerFactory()
        factory.protocol = ControlProtocol

        from twisted.internet import reactor
        reactor.listenSSL(self.port, factory, ssl_context)


class ControlProtocol(NetstringReceiver):
    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())

    def stringReceived(self, info):
        req_data = json.loads(info)
        handel = HandelRequest(req_data, self.transport)
        handel.start()

    def connectionLost(self, reason):
        log.msg('close connection ')


class HandelRequest(object):
    """处理客户端请求"""
    def __init__(self, req_data: dict, transport):
        """
        Args:
            req_data: 客户端传递过来的命令数据
            transport: 与客户端的连接
        """
        self.req_data = req_data
        self.transport = transport

    def start(self):
        fun = self.get_handel_fun()
        if fun != "error":
            fun()
        else:
            log.msg('undefined cmd: ', self.req_data.get('cmd', 'null'))
            self.transport.loseConnection()

    def get_handel_fun(self):
        return {
            'new_tunnel': self.__new_tunnel,
        }.get(self.req_data.get('cmd'), 'error')

    def __new_tunnel(self):
        from twisted.internet import reactor

        reactor.listenTCP(2333, factory, interface='0.0.0.0')