import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name="mtg-bot"):
    # logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # formatter
    #formatter = CustomFormatter()

    # file handler
    file_handler = logging.FileHandler("chat_logs.log", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(CustomFormatter())


    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CustomFormatter())
    
    # add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
