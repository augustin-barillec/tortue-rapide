import logging
import socket
import time

logger = logging.getLogger(__name__)


def is_internet(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logger.error(ex)
        return False


class InternetChecker:
    def __init__(self):
        self._internet = True

    def run_threaded(self):
        return self._internet

    def update(self):
        while True:
            self._internet = is_internet()
            time.sleep(1)


class InternetLaxChecker:
    def __init__(self):
        self._lax_internet = True

    def run_threaded(self):
        return self._lax_internet

    def update(self):
        cnt = 0
        while True:
            logger.info('cnt={}'.format(cnt))
            aux = is_internet()
            if not aux:
                cnt += 1
            else:
                cnt = 0
            if cnt == 5:
                logger.info('Setting lax_internet to False...')
                self._lax_internet = False
                logger.info('Set lax_internet to False')
            time.sleep(1)
