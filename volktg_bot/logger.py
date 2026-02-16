import logging
import logging.handlers

FMT_STRING_DEFAULT = "%(asctime)s %(levelname)-10s %(message)s"
FMT_STRING_DEBUG   = "%(asctime)s %(levelname)-10s [%(filename)s]:%(lineno)s %(message)s"


def _create_formatter(fmt_string=None):
    if fmt_string is None:
        fmt_string = FMT_STRING_DEFAULT
    formatter = logging.Formatter(fmt_string)
    formatter.default_msec_format = '%s.%03d'
    return formatter


def _create_console_handler(level, formatter):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    return console_handler


def _create_file_handler(file_name, level, formatter):
    file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when='MIDNIGHT')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    return file_handler


def logger_get():
    return logging.getLogger("main_application")


def logger_init(level, fmt_string=None):
    logger = logger_get()
    logger.setLevel(level)
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    formatter = _create_formatter(fmt_string)
    logger.addHandler(_create_console_handler(level, formatter))
    return logger


def logger_configure(file_name, level, to_console_too=False, fmt_string=None):
    logger = logger_get()
    logger.setLevel(level)
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    formatter = _create_formatter(fmt_string)
    logger.addHandler(_create_file_handler(file_name, level, formatter))
    if to_console_too:
        logger.addHandler(_create_console_handler(level, formatter))
    return logger
