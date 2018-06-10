import sys

from twisted.python import log

from parse import parse_args
from controller import Controller


def main():
    log.startLogging(sys.stdout)

    opt = parse_args()

    control = Controller(
        opt['domain'], opt['host'], opt['control_port'], opt['tls_conf'], opt['local_port'], opt['tunnel_port']
    )
    control.connection()

    from twisted.internet import reactor

    reactor.run()


if __name__ == "__main__":
    main()
