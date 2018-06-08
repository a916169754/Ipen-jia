from decouple import config


def parse_args():
    """解析配置文件， 返回字典"""
    options = {
        'control_port': config('CONTROL_CONNECTION_PORT', cast=int),
        'tls_conf': {
            'private': config('SSL_PRIVATE'),
            'cert': config('SSL_CERT')
        }
    }

    return options
