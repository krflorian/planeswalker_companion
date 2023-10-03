from dataclasses import dataclass, field
import yaml
import openai
import logging
import os

from mtg.data_handler import CardDB
from .chat_history import ChatHistory


try:
    with open("config/config.yaml", "r") as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    openai.api_key = config.get("open_ai_token")
    logging.info("loaded open ai token from config file ")
except:
    logging.warn("did not find config file")
    openai.api_key = os.environ["open_ai_token"]
    logging.info("loaded open ai token from environment")


@dataclass
class MagicGPT:
    card_db: CardDB
    chat_history: ChatHistory = ChatHistory()

    def ask(self, query):
        # process query
        message = self.card_db.create_message(query, role="user")
        self.chat_history.add_message(message=message)

        prompt = self.chat_history.create_prompt()
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            n=1,
            temperature=0,
        )
        response = chat_completion.choices[0].message.content

        # process response
        message = self.card_db.create_message(response, role="assistant")
        self.chat_history.add_message(message=message)

        return self.chat_history.create_human_readable_chat()
