import gradio
from pathlib import Path
import logging

from mtg.bot import MagicGPT
from mtg.data_handler import CardDB

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("chat_logs.log", mode="w"), stream_handler],
)

all_cards_file = Path("data/raw/scryfall_all_cards_with_rulings.json")

card_db = CardDB(all_cards_file)
magic_bot = MagicGPT(card_db)

# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chatbot = gradio.Chatbot()

    # creates a new Row component, which is a container for other components.
    with gradio.Row():
        txt = gradio.Textbox(show_label=False, placeholder="Enter text and press enter")
    txt.submit(magic_bot.ask, txt, chatbot)
    txt.submit(None, None, txt, _js="() => {''}")
ui.launch()
