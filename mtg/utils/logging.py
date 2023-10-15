import logging


def get_logger(name="mtg-bot"):
    # logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # handler
    file_handler = logging.FileHandler("chat_logs.log", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
