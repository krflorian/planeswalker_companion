import gradio
import yaml
from pathlib import Path

from mtg.bot import MagicGPT
from mtg.history.chat_history import ChatHistory
from mtg.utils.logging import get_logger

logger = get_logger(__name__)

with open("configs/config.yaml", "r") as infile:
    config = yaml.load(infile, Loader=yaml.FullLoader)


VERSION = "0.0.4"

DECKBUILDING_MODEL_NAME = config.get("llm_model_name_deckbuilding", "gpt-3.5-turbo")
RUKES_MODEL_NAME = config.get("llm_model_name_rules", "gpt-4-0125-preview")

HEADER_TEXT = """
# Hi, I'm Nissa! 
I can help you with all kinds of questions regarding Magic: the Gathering rules or help you with brewing a new deck.  
I will never save any user data. To help enhance my training and development, feel free to use the like/dislike button to save messages.  
[Patreon](https://www.patreon.com/NissaPlaneswalkerCompanion)  
"""

FOOTER_TEXT = f"""
Support Nissa on [Patreon](https://www.patreon.com/NissaPlaneswalkerCompanion)  
version: {VERSION}  
deckbuilding model: {DECKBUILDING_MODEL_NAME}  
rules model: {RUKES_MODEL_NAME}  
"""


def get_magic_bot() -> MagicGPT:
    """Initialize Magicbot with Memory for user session."""
    logger.info("Creating new user session.")
    magic_bot = MagicGPT(
        chat_history=ChatHistory(
            data_service_host=config.get("data_service_host", "127.0.0.1")
        ),
        model_deckbuilding=DECKBUILDING_MODEL_NAME,
        model_rules=RUKES_MODEL_NAME,
        temperature_deck_building=0.7,
        max_token_limit=1000,
        data_filepath=Path(config.get("message_filepath", "data/raw/messages")),
    )
    return magic_bot


def update_user_message(user_message: str, magic_bot: MagicGPT):
    """Process the User question - Classifies intent and adds information."""
    chat = magic_bot.process_user_query(user_message)
    return chat, magic_bot


def update_textbox(textboxtext: str, user_message: str):
    """Clear the user message from Textbox."""
    user_message = textboxtext
    return "", user_message


def process_user_message(magic_bot: MagicGPT):
    """Streams the response of the Chatbot."""
    responses = magic_bot.ask()
    for chat in responses:
        yield chat


def clear_memory(magic_bot: MagicGPT):
    """Delete conversation history."""
    magic_bot.clear_memory()


def up_vote(magic_bot: MagicGPT, like_state: gradio.LikeData):
    magic_bot.save_chat(liked=like_state.liked, message_index=like_state.index)
    return


# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as ui:
    gradio.Markdown(HEADER_TEXT)
    # chat
    chat = gradio.Chatbot(likeable=True)

    magic_bot = gradio.State(get_magic_bot)
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
    clear_btn.click(clear_memory, inputs=[magic_bot])

    # upvote button
    chat.like(up_vote, [magic_bot], outputs=[txt])

ui.launch(favicon_path='./assets/favicon1.jpg')

