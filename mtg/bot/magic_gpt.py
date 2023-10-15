import time
from datetime import datetime, timedelta

from langchain.chains import LLMChain

from mtg.data_handler import CardDB
from mtg.utils.logging import get_logger
from .chat_history import ChatHistory

logger = get_logger(__name__)


class MagicGPT:
    def __init__(self, llm_chain: LLMChain, card_db: CardDB, chat_history: ChatHistory):
        self.llm_chain = llm_chain
        self.card_db = card_db
        self.chat_history = chat_history
        self._last_updated = datetime.now()

    def clear_memory(self):
        self.llm_chain.memory.clear()
        self.chat_history.clear()

    def ask(self, query):
        try:
            chat = self._ask(query)
            return chat
        except Exception as e:
            logger.error(e)
            self.clear_memory()
            return [
                [
                    query,
                    f"Something went wrong, I am restarting. Please ask the question again.",
                ]
            ]

    def _ask(self, query):
        # no user system yet so clear memory after every hour
        if datetime.now() - self._last_updated > timedelta(hours=1):
            self.clear_memory()
        self._last_updated = datetime.now()

        # process query
        message = self.card_db.create_message(query, role="user")
        self.chat_history.add_message(message=message)
        card_data = self.chat_history.get_card_data(
            number_of_messages=2, max_number_of_cards=4
        )

        start = time.time()
        response = self.llm_chain.predict(human_input=message.text, card_data=card_data)
        logger.debug(f"runtime llm chain: {time.time()-start:.2f}sec")

        # process response
        message = self.card_db.create_message(response, role="assistant")
        self.chat_history.add_message(message=message)

        return self.chat_history.get_human_readable_chat(number_of_messages=6)
