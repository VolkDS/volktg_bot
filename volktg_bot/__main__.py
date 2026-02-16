import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv
from importlib import metadata

from . import logger
from .manager import Manager


def get_args():
    parser = argparse.ArgumentParser(prog='volktg_bot')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    return parser.parse_args()


def print_version():
    meta = metadata.metadata('volktg_bot')
    print('Name: %s' % meta['Name'])
    print('Version: %s' % meta['Version'])
    print('Author: %s' % meta['Author-email'])
    print('License: %s' % meta['License'])


def init_logger():
    log_level = os.getenv("LOGGER_LOG_LEVEL")
    # log_filepath = ""
    log = logger.logger_init(log_level, logger.FMT_STRING_DEBUG)
    # if len(log_filepath) > 0:
    #     log = logger.logger_configure(log_filepath, log_level, conf.get('log.to_console_too'), logger.FMT_STRING_DEBUG)
    return log

def main():
    load_dotenv()

    try:
        log = init_logger()
    except Exception as e:
        sys.stderr(f"FATAL: Init logger failed: {e}")
        sys.exit(1)

    log.info("Start program")

    try:
        manager = Manager()
        asyncio.run(manager.run())
    except Exception as e:
        log.critical(f"FATAL: Init manager failed: {e}")
        sys.exit(1)

    log.info("Exit")

if __name__ == "__main__":
    main()
