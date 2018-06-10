import json
import random
import string

from twisted.python import log
from twisted.internet import ssl, protocol
from twisted.protocols.basic import NetstringReceiver

from tunnel import Tunnel
from connection import ProxyConnServer


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
        """
        建立一个链接，开始监听端口
        """
        ssl_context = ssl.DefaultOpenSSLContextFactory(
            self.tls_conf['private'],
            self.tls_conf['cert'],
        )

        factory = protocol.ServerFactory()
        factory.protocol = ControlProtocol
        factory.tls_conf = self.tls_conf

        from twisted.internet import reactor
        reactor.listenSSL(self.port, factory, ssl_context)


class ControlProtocol(NetstringReceiver):
    def connectionMade(self):
        log.msg("receive request .... ", self.transport.getPeer())
        #  随机给客户端生成id， 不考虑排重
        # client_id = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        client_id = 'www'
        res = {
            'client_id': client_id,
            'res': 'success'
        }
        self.sendString(json.dumps(res).encode('utf8'))

    def stringReceived(self, info):
        req_data = json.loads(info.decode('utf8'))
        handel = HandelRequest(req_data, self, self.factory.tls_conf)
        handel.start()

    def connectionLost(self, reason):
        log.msg('close connection ')


class HandelRequest(object):
    """处理客户端请求"""
    def __init__(self, req_data: dict, protocol, tls_conf):
        """
        Args:
            req_data: 客户端传递过来的命令数据
            protocol: twisted Protocol
        """
        self.req_data = req_data
        self.protocol = protocol
        self.tls_conf = tls_conf

    def start(self):
        fun = self.get_handel_fun()
        if fun != "error":
            fun()
        else:
            log.msg('undefined cmd: ', self.req_data.get('cmd', 'null'))
            self.protocol.transport.loseConnection()

    def get_handel_fun(self):
        return {
            'new_tunnel': self.__new_tunnel,
            'new_proxy': self.__new_proxy,
        }.get(self.req_data.get('cmd'), 'error')

    def __new_tunnel(self):
        tunnel = Tunnel()
        port = tunnel.new_tunnel(self.req_data.get('port', 0), self.req_data.get('client_id'))

        res = {
            'tunnel_port': port,
            'client_id': self.req_data.get('client_id'),
            'res': 'start_tunnel'
        }
        self.protocol.sendString(json.dumps(res).encode('utf8'))

    def __new_proxy(self):
        log.msg(self.req_data)
        log.msg(Tunnel.tunnels)
        tunnel = Tunnel.tunnels.get(str(self.req_data['tunnel_port']))
        proxy = ProxyConnServer(0, self.tls_conf, self.req_data['client_id'], tunnel)
        port = proxy.listen()

        res = {
            'port': port,
            'res': 'start_proxy'
        }
        self.protocol.sendString(json.dumps(res).encode('utf8'))
