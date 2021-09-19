import logging
import sys
import os
import traceback

LOG_PATH = "/app/"


class FileLogger:
    def __init__(self, filename, level='DEBUG'):
        if not os.path.exists(LOG_PATH):    # Log dosyasını oluştur
            os.makedirs(LOG_PATH)

        if not os.path.exists(LOG_PATH + filename):  # set permissions
            os.mknod(LOG_PATH + filename)
            os.chmod(LOG_PATH + filename, 0o777)    # web server can write (www-data)

        self.log_path = LOG_PATH + filename

        log_formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')
        root_logger = logging.getLogger()

        file_handler = logging.FileHandler(self.log_path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

        root_logger.setLevel(level)
        self.logger = root_logger

    def critical(self, *msg):
        str_msg = self._concat(*msg)
        self.logger.critical(str_msg)

    def exception(self, *msg):
        str_msg = self._concat(*msg)
        self.logger.exception(str_msg)

    def unhandled_exceptions(self, exctype, value, tb):
        e = traceback.format_exception(exctype, value, tb)
        self.logger.error(str(e))   # log to file
        traceback.print_exception(exctype, value, tb)  # and log to std_err

    def error(self, *msg):
        str_msg = self._concat(*msg)
        self.logger.error(str_msg)

    def info(self, *msg):
        self.logger.info(self._concat(*msg))

    def debug(self, *msg):
        self.logger.debug(self._concat(*msg))

    def warning(self, *msg):
        self.logger.warning(self._concat(*msg))

    def _concat(self, *args):
        result = ''
        for r in args:
            result = result + str(r) + ' '
        return result


logger = FileLogger("distscanner.log", level='WARNING')
sys.excepthook = logger.unhandled_exceptions

