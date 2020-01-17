import logging
import socket
import time

logger = logging.getLogger(__name__)

def check_internet(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logger.error(ex)
        return False


class InternetChecker:
    def __init__(self):
        self._internet = None

    def run_threaded(self):
        return self._internet

    def update(self):
        while True:
            self._internet = check_internet()
            time.sleep(1)
