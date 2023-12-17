import gradio
from pathlib import Path

from mtg.bot import MagicGPT
from mtg.data_handler import CardDB
from mtg.bot.chat_history import ChatHistory

all_cards_file = Path("data/cards/scryfall_all_cards_with_rulings.json")
vector_db_file = Path("data/artifacts/card_vector_db.p")

card_db = CardDB(all_cards_file=all_cards_file, vector_db_file=vector_db_file)


def update_user_message(user_message, magic_bot: MagicGPT):
    """"""
    chat = magic_bot.process_user_query(user_message)
    return "", chat, magic_bot


def process_user_message(magic_bot):
    chat = magic_bot.ask()
    return chat


def clear_memory(magic_bot):
    magic_bot.clear_memory()
    return [[]], magic_bot


# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chat = gradio.Chatbot()
    magic_bot = gradio.State(
        MagicGPT(
            card_db=card_db,
            chat_history=ChatHistory(),
            model="gpt-4-1106-preview",
            temperature_deck_building=0.7,
            max_token_limit=2000,
        )
    )
    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    # submit text
    txt.submit(
        update_user_message,
        inputs=[txt, magic_bot],
        outputs=[txt, chat, magic_bot],
        queue=False,
    ).then(process_user_message, inputs=[magic_bot], outputs=[chat])

    # submit button
    submit_btn.click(
        update_user_message,
        inputs=[txt, magic_bot],
        outputs=[txt, chat, magic_bot],
        queue=False,
    ).then(process_user_message, inputs=[magic_bot], outputs=[chat])

    # clear button
    clear_btn = gradio.ClearButton([txt], value="Start new Conversation")
    clear_btn.click(clear_memory, inputs=[magic_bot], outputs=[chat])
ui.launch()
