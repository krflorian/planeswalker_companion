import gradio
import yaml

from mtg.bot import MagicGPT
from mtg.history.chat_history import ChatHistory

VERSION = "0.0.1"
MODEL_NAME = "gpt-4-1106-preview"

with open("configs/config.yaml", "r") as infile:
    config = yaml.load(infile, Loader=yaml.FullLoader)

HEADER_TEXT = """
# Hi, I'm Nissa! 
I can help you with all kinds of questions regarding Magic the Gathering rules or help you with brewing a new deck.
"""

FOOTER_TEXT = f"""
Support Nissa on [Patreon](https://www.patreon.com/NissaPlaneswalkerCompanion)  
version: {VERSION}
"""

magic_bot = MagicGPT(
    chat_history=ChatHistory(
        data_service_host=config.get("data_service_host", "127.0.0.1")
    ),
    model=MODEL_NAME,
    temperature_deck_building=0.7,
    max_token_limit=2000,
)


def update_user_message(user_message, magic_bot: MagicGPT = magic_bot):
    """"""
    chat = magic_bot.process_user_query(user_message)
    return chat


def update_textbox(textboxtext, user_message):
    user_message = textboxtext
    return "", user_message


def process_user_message(magic_bot: MagicGPT = magic_bot):
    responses = magic_bot.ask()
    for chat in responses:
        yield chat


def clear_memory(magic_bot: MagicGPT = magic_bot):
    magic_bot.clear_memory()


# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    gradio.Markdown(HEADER_TEXT)
    # chat
    chat = gradio.Chatbot()

    user_message = gradio.State("")

    # textbox
    with gradio.Row():
        txt = gradio.Textbox(
            show_label=False, placeholder="Enter text and press enter", scale=7
        )
        submit_btn = gradio.Button(value="Submit", variant="primary", scale=1)

    # clear button
    clear_btn = gradio.ClearButton([chat, txt], value="Start new Conversation")

    gradio.Markdown(FOOTER_TEXT)
    # submit text
    txt.submit(
        update_textbox, inputs=[txt, user_message], outputs=[txt, user_message]
    ).then(
        update_user_message,
        inputs=[user_message],
        outputs=[chat],
        queue=False,
    ).then(
        process_user_message, outputs=[chat]
    )

    # submit button
    submit_btn.click(
        update_textbox, inputs=[txt, user_message], outputs=[txt, user_message]
    ).then(
        update_user_message,
        inputs=[user_message],
        outputs=[chat],
        queue=False,
    ).then(
        process_user_message, outputs=[chat]
    )

    # clear button
    clear_btn.click(clear_memory)
ui.launch()
