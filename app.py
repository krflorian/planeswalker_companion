import gradio
from pathlib import Path

from mtg.bot import MagicGPT
from mtg.data_handler import CardDB
from mtg.bot.chat import create_chat_model
from mtg.bot.chat_history import ChatHistory


all_cards_file = Path("data/raw/scryfall_all_cards_with_rulings.json")

card_db = CardDB(all_cards_file)
chat_history = ChatHistory()
llm_chain = create_chat_model(
    model="gpt-3.5-turbo", temperature=1, max_token_limit=2000
)
magic_bot = MagicGPT(llm_chain=llm_chain, card_db=card_db, chat_history=chat_history)

# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chatbot = gradio.Chatbot()

    # creates a new Row component, which is a container for other components.
    with gradio.Row():
        txt = gradio.Textbox(show_label=False, placeholder="Enter text and press enter")
    txt.submit(magic_bot.ask, txt, chatbot)
    txt.submit(None, None, txt, _js="() => {''}")
    with gradio.Row():
        clear_btn = gradio.ClearButton([chatbot, txt])
    clear_btn.click(magic_bot.clear_memory)
ui.launch()
