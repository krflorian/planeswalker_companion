import os
import yaml
import logging


def get_openai_api_key():
    try:
        with open("configs/config.yaml", "r") as infile:
            config = yaml.load(infile, Loader=yaml.FullLoader)
        openai_api_key = config.get("open_ai_token")
        logging.info("loaded open ai token from config file ")
    except:
        logging.warn("did not find config file")
        openai_api_key = os.environ["open_ai_token"]
        logging.info("loaded open ai token from environment")
    return openai_api_key
