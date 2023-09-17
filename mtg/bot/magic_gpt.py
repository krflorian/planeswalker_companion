from dataclasses import dataclass, field
import yaml
import openai
import logging
import os

from mtg.data_handler import CardDB

logging.basicConfig(encoding="utf-8", level=logging.INFO)

try:
    with open("config/config.yaml", "r") as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    openai.api_key = config.get("open_ai_token")
    logging.info("loaded open ai token from config file ")
except:
    logging.warn("did not find config file")
    openai.api_key = os.environ["open_ai_token"]
    logging.info("loaded open ai token from environment")


# list models
# models = openai.Model.list()

SYSTEM_MESSAGE = """
You are a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
Do not answer questions unrelated to Magic the Gathering. 

Here are mtg related patterns that you use to describe Mana: 
Colored Mana: 
    White = {W}
    Blue = {U}
    Black = {B}
    Red = {R}
    Green = {G}

2 white Mana would be described as {W}{W} whereas two colorless mana would be described with just the number inside brackets: {2}
If there is a T inside the brackets {T} this means tap the card. 
"""

REMEMBER_MESSAGE = """
Remember:  You are a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
Do not answer questions unrelated to Magic the Gathering. Give Short and truthfull answers.
"""


@dataclass
class MagicGPT:
    card_db: CardDB
    chat_history: list[str] = field(default_factory=list)
    _history: list[dict] = field(default_factory=list)

    def __post__init__(self) -> None:
        self._history.append({"role": "system", "content": SYSTEM_MESSAGE})

    def ask(self, query):
        query_doc = self.card_db.process_text(query)

        processed_query = self.card_db.replace_card_names_with_urls(query_doc)
        cards_data = self.card_db.extract_card_data_from_doc(query_doc)
        cards_text = "\n\n".join([card.to_text() for card in cards_data])

        # create prompt
        prompt = ""
        if cards_text:
            prompt += f"\n\nCONTEXT: \n{cards_text}"
        prompt += f"\n\nUSER QUESTION: \n{query}"

        # chatgpt api
        self._history.append({"role": "user", "content": REMEMBER_MESSAGE})
        self._history.append({"role": "user", "content": prompt})

        logging.debug("sending question: %s", self._history)
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self._history,
            n=1,
            temperature=0,
        )
        response = chat_completion.choices[0].message.content

        # process response
        response_doc = self.card_db.process_text(response)
        processed_response = self.card_db.replace_card_names_with_urls(response_doc)

        # delete remember message from history
        del self._history[-2]
        self._history.append({"role": "assistant", "content": response})
        self._history = self._history[-4:]

        # build chat
        self.chat_history.append([processed_query, processed_response])
        self.chat_history = self.chat_history[-2:]
        return self.chat_history
