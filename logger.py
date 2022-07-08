import logging
import logging.handlers

def set_logger(module_name):
    logger = logging.getLogger(module_name)
    logger.handlers.clear()

    streamHandler = logging.StreamHandler()
    fileHandler = logging.handlers.RotatingFileHandler("../stream/system.log", maxBytes=10000, backupCount=5)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] (%(filename)s | %(funcName)s | %(lineno)s) %(message)s")

    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    streamHandler.setLevel(logging.INFO)
    fileHandler.setLevel(logging.DEBUG)

    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

    return logger

def main():
    logger = set_logger(__name__)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warn")
    logger.error("error")
    logger.critical("critical")

if __name__ == "__main__":
    main()