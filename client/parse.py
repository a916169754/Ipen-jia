from decouple import config


def parse_args():
    """解析配置文件， 返回字典"""
    options = {
        'control_port': config('CONTROL_CONNECTION_PORT', cast=int),
        'tls_conf': {
            'cert': config('SSL_CERT')
        },
        'domain': config('DOMAIN'),
        'host': config('HOST'),
        'local_port': config('LOCAL_PORT', cast=int),
        'tunnel_port': config('TUNNEL_PORT', cast=int)
    }

    return options
