import argparse
import logging
import time
import urllib.parse

from prometheus_client import start_http_server, REGISTRY

from prometheus_eaton_ups_exporter import DEFAULT_PORT
from prometheus_eaton_ups_exporter.exporter import UPSExporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Eaton UPS device metric exporter for Prometheus'))

    parser.add_argument(
        '-w', '--web.listen-address',
        dest='listen_address',
        required=False,
        type=str,
        default=f':{DEFAULT_PORT}',
        help=f'Address and port to listen on (default = :{DEFAULT_PORT})')

    parser.add_argument(
        '-c', '--config',
        dest='config',
        required=True,
        help='configuration json file containing UPS addresses and login info')

    parser.add_argument(
        '-l', '--log',
        dest='log_level',
        required=False,
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        help='Specify logging level')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=args.log_level,
        format='[%(asctime)s] %(levelname)s: %(message)s')
    logger = logging.getLogger('prometheus_ntp_exporter')
    logger.setLevel(args.log_level)
    logger.info(f'Log level: {logging.getLevelName(logger.level)}')

    try:
        listen_addr = urllib.parse.urlsplit(f'//{args.listen_address}')
        addr = listen_addr.hostname if listen_addr.hostname else '0.0.0.0'
        port = listen_addr.port if listen_addr.port else DEFAULT_PORT

        REGISTRY.register(UPSExporter(config=args.config))

        start_http_server(port, addr=addr)
        logger.info(f'Listening on {listen_addr.netloc}')
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
        exit(0)
    except Exception as exc:
        logger.error(exc)
        logger.critical(
            'Exporter shut down unexpectedly during server startup. '
            'Please contact your administrator.')
        exit(1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
        exit(0)
    except Exception as exc:
        logger.error(exc)
        logger.critical(
            'Exporter shut down unexpectedly. Please contact your '
            'administrator.')
        exit(1)


if __name__ == "__main__":
    main()
