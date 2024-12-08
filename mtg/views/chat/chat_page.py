import streamlit as st
from uuid import uuid4
from langfuse.callback import CallbackHandler
from datetime import datetime, timedelta

from mtg.agents import create_memory, create_chat_agent, create_judge_agent
from mtg.agents import nissa, judge
from mtg.tools import (
    CardSearchTool,
    CardNameSearchTool,
    RulesSearchTool,
    UserDeckLookupTool,
    JudgeReportTool,
)
from mtg.utils.logging import get_logger
from mtg.utils import load_config
from streamlit_cookies_controller import CookieController


# setup
st.set_page_config(
    page_title="Nissa",
    page_icon=nissa.PROFILE_PICTURE,
    layout="wide",
)

from mtg.views.chat.sidebar import handle_sidebar
from mtg.views.chat.chat_interface import handle_chat
from mtg.views.chat.deck_upload import handle_deck_upload_screen

logger = get_logger("mtg-bot")

config = load_config("configs/config.yaml")

langfuse_handler = CallbackHandler()


# page
st.markdown(
    """

    <style>

    /* Hide the Streamlit header and menu */

    header {visibility: hidden;}

    /* Optionally, hide the footer */

    .streamlit-footer {display: none;}

    </style>

    """,
    unsafe_allow_html=True,
)


# Function to handle cookie preferences
@st.dialog("Cookie Preferences")
def handle_cookie_preferences():
    st.write(
        """
We Value Your Privacy  
Our website uses cookies to enhance your experience and provide essential functionality.  
We use cookies to track user requests for rate limiting and collect anonymized chat message data to continuously improve Nissas Answers.

You can learn more about how we handle your data in our [Privacy Policy](https://nissa.planeswalkercompanion.com/info_page).
"""
    )
    # accept_ads = st.checkbox("Accept cookies for ads")
    _ = st.checkbox("Accept cookies for performance", value=True, disabled=True)

    if st.button("Save Preferences"):
        st.session_state.cookie_controller.set("planeswalker/performance_cookies", True)
        st.success("Your preferences have been saved! 🎉")
        st.rerun()


# HANDLE STATE
# Initialize chat history
if not st.session_state.state.messages:
    trace_id = str(uuid4())
    st.session_state.state.messages = [
        {
            "role": "nissa",
            "content": nissa.WELCOME_TEXT,
            "image": nissa.PROFILE_PICTURE,
            "trace_id": trace_id,
        },
        {
            "role": "judge",
            "content": judge.WELCOME_TEXT,
            "image": judge.PROFILE_PICTURE,
            "trace_id": trace_id,
        },
    ]

if "agent" not in st.session_state:
    # add agent, judge + deck tool to session state
    # setup tools and llm
    memory = create_memory()

    # tools
    card_search_tool = CardSearchTool(
        url=config.dataservice_settings.host,
        threshold=config.dataservice_settings.card_search_threshold,
        number_of_cards=config.dataservice_settings.card_search_number_of_cards,
    )

    card_name_search_tool = CardNameSearchTool(
        url=config.dataservice_settings.host,
    )

    rules_search_tool = RulesSearchTool(
        url=config.dataservice_settings.host,
        threshold=config.dataservice_settings.rules_search_threshold,
    )
    judge_report_tool = JudgeReportTool()
    st.session_state.deck_tool = UserDeckLookupTool()

    # agents
    st.session_state.agent = create_chat_agent(
        system_message=nissa.SYSTEM_MESSAGE,
        prompt=nissa.PROMPT,
        tools=[
            st.session_state.deck_tool,
            card_search_tool,
            card_name_search_tool,
            rules_search_tool,
        ],
        memory=memory,
        model_name=config.llm_settings.nissa_llm_model_version,
    )

    st.session_state.judge = create_judge_agent(
        system_message=judge.SYSTEM_MESSAGE,
        prompt=judge.PROMPT,
        tools=[card_name_search_tool, rules_search_tool, judge_report_tool],
        memory=memory,
        model_name=config.llm_settings.judge_llm_model_version,
    )

cookie_controller = CookieController()
accepted_cookies = cookie_controller.get("planeswalker/performance_cookies")
if not accepted_cookies:
    cookies = cookie_controller.getAll()
    logger.info(f"did not find performance_cookies: {cookies}")
    handle_cookie_preferences()

handle_sidebar()
handle_deck_upload_screen()
handle_chat(config=config, callback_handler=langfuse_handler)
