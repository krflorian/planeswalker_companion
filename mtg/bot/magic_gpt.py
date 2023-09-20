from dataclasses import dataclass, field
import yaml
import openai
import logging
import os

from mtg.data_handler import CardDB
from .chat_history import ChatHistory

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

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
        query_doc = self.card_db.process_text(query)
        processed_query = self.card_db.replace_card_names_with_urls(query_doc)
        cards = self.card_db.extract_card_data_from_doc(query_doc)

        self.chat_history.add_message(
            text=query, role="user", cards=cards, processed_text=processed_query
        )

        prompt = self.chat_history.create_prompt()
        logging.debug("sending question: %s", prompt)
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            n=1,
            temperature=0,
        )
        response = chat_completion.choices[0].message.content

        # process response
        response_doc = self.card_db.process_text(response)
        processed_response = self.card_db.replace_card_names_with_urls(response_doc)
        self.chat_history.add_message(
            text=response, role="assistant", cards=[], processed_text=processed_response
        )

        return self.chat_history.create_human_readable_chat()
