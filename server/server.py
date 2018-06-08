import sys

from twisted.python import log

from parse import parse_args
from control import Control


def main():
    log.startLogging(sys.stdout)

    opt = parse_args()

    control = Control(opt['control_port'], opt['tls_conf'])
    control.start_listen()

    from twisted.internet import reactor

    reactor.run()

if __name__ == "__main__":
    main()
