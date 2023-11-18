import gradio
from pathlib import Path

from mtg.bot import MagicGPT
from mtg.data_handler import CardDB
from mtg.bot.chat_history import ChatHistory

all_cards_file = Path("data/cards/scryfall_all_cards_with_rulings.json")
vector_db_file = Path("data/artifacts/card_vector_db.p")

card_db = CardDB(all_cards_file=all_cards_file, vector_db_file=vector_db_file)
chat_history = ChatHistory()
magic_bot = MagicGPT(
    card_db=card_db,
    chat_history=chat_history,
    model="gpt-4-1106-preview",
    temperature_deck_building=0.7,
    max_token_limit=2000,
)

gradio.ChatInterface

# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chatbot = gradio.Chatbot()
    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    clear_btn = gradio.ClearButton([chatbot, txt], value="Start new Conversation")
    txt.submit(magic_bot.ask, txt, chatbot)
    txt.submit(lambda x: "", txt, txt)

    clear_btn.click(magic_bot.clear_memory)
    submit_btn.click(magic_bot.ask, inputs=[txt], outputs=[chatbot])
    submit_btn.click(lambda x: "", [txt], [txt])

ui.launch()
