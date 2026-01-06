import logging
from logstash_async.handler import AsynchronousLogstashHandler
from config import config


class CustomLoggerFilter(logging.Filter):
    def filter(self, log):
        return True


def create_logger(name, level=config["logs.base_level"]):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addFilter(CustomLoggerFilter())
        add_console_logger(logger)

        if config["logs.logstash"]["enabled"]:
            add_logstash_logger(logger)

    logger.propagate = False
    return logger


def add_console_logger(logger, level=config["logs.base_level"]):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(config["logs.console.format"]))
    logger.addHandler(console_handler)


def add_logstash_logger(logger, level=config["logs.base_level"]):
    logstash_handler = AsynchronousLogstashHandler(
        host=config["logs.logstash"]["host"],
        port=config["logs.logstash"]["port"],
        version=config["logs.logstash"]["version"],
        level=level,
    )
    logger.addHandler(logstash_handler)
