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
    return chat, magic_bot


def update_textbox(textboxtext, user_message):
    user_message = textboxtext
    return "", user_message


def process_user_message(magic_bot):
    responses = magic_bot.ask()
    for chat in responses:
        yield chat


def clear_memory(magic_bot):
    magic_bot.clear_memory()


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
    user_message = gradio.State("")
    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    # submit text
    txt.submit(
        update_textbox, inputs=[txt, user_message], outputs=[txt, user_message]
    ).then(
        update_user_message,
        inputs=[user_message, magic_bot],
        outputs=[chat, magic_bot],
        queue=False,
    ).then(
        process_user_message, inputs=[magic_bot], outputs=[chat]
    )

    # submit button
    submit_btn.click(
        update_textbox, inputs=[txt, user_message], outputs=[txt, user_message]
    ).then(
        update_user_message,
        inputs=[user_message, magic_bot],
        outputs=[chat, magic_bot],
        queue=False,
    ).then(
        process_user_message, inputs=[magic_bot], outputs=[chat]
    )

    # clear button
    clear_btn = gradio.ClearButton([chat, txt], value="Start new Conversation")
    clear_btn.click(clear_memory, inputs=[magic_bot])
ui.launch()
