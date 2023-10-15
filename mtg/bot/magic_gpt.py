from dataclasses import dataclass, field
from langchain.chains import LLMChain

from mtg.data_handler import CardDB
from .chat_history import ChatHistory
from .chat import create_chat_model


class MagicGPT:
    def __init__(self, llm_chain: LLMChain, card_db: CardDB, chat_history: ChatHistory):
        self.llm_chain = llm_chain
        self.card_db = card_db
        self.chat_history = chat_history

    def ask(self, query):
        # process query
        message = self.card_db.create_message(query, role="user")
        self.chat_history.add_message(message=message)
        card_data = self.chat_history.get_card_data(number_of_messages=4)

        response = self.llm_chain.predict(human_input=message.text, card_data=card_data)

        # process response
        message = self.card_db.create_message(response, role="assistant")
        self.chat_history.add_message(message=message)

        return self.chat_history.get_human_readable_chat(number_of_messages=4)
