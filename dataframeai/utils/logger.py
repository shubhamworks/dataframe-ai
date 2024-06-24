import logging

class Logger:
    LOG_LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    @staticmethod
    def get_logger(level='debug'):
        logger = logging.getLogger(__name__)
        logger.setLevel(Logger.LOG_LEVELS[level])
        if not logger.hasHandlers():
            logger.addHandler(logging.StreamHandler())
        return logger