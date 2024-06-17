import streamlit as st
from dotenv import load_dotenv

from mtg.agents import create_llm, create_memory, create_chat_agent, create_judge_agent

from mtg.agents import nissa, judge, user
from mtg.tools import (
    CardSearchTool,
    RulesSearchTool,
    UserDeckLookupTool,
    CallJudgeTool,
    JudgeReportTool,
)
from mtg.utils.logging import get_logger
from mtg.utils.ui import to_sync_generator

import os
import yaml

logger = get_logger("mtg-bot")
with open("configs/config.yaml", "r") as infile:
    config = yaml.safe_load(infile)

os.environ["OPENAI_API_KEY"] = config["open_ai_token"]
model_version = config.get("llm_model_version", "gpt-4o")

VERSION = "1.1.0"

FOOTER_TEXT = f"""
Support Nissa on [Patreon](https://www.patreon.com/NissaPlaneswalkerCompanion)  
version: {VERSION}  
chat model: {model_version}
"""

st.set_page_config(
    page_title="Nissa",
    page_icon=nissa.PROFILE_PICTURE,
    layout="wide",
)

# HANDLE STATE
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "nissa",
            "content": nissa.WELCOME_TEXT,
            "image": nissa.PROFILE_PICTURE,
        },
        {
            "role": "judge",
            "content": judge.WELCOME_TEXT,
            "image": judge.PROFILE_PICTURE,
        },
    ]

if "agent" not in st.session_state:

    # setup tools and llm
    llm = create_llm(model_version)
    memory = create_memory(llm=llm)

    # tools
    card_search_tool = CardSearchTool(
        url=config.get("data_service_host", "http://localhost:8000/")
    )
    rules_search_tool = RulesSearchTool(
        url=config.get("data_service_host", "http://localhost:8000/")
    )
    judge_report_tool = JudgeReportTool()
    st.session_state.judge_tool = CallJudgeTool()
    st.session_state.deck_tool = UserDeckLookupTool()

    # agents
    st.session_state.agent = create_chat_agent(
        system_message=nissa.SYSTEM_MESSAGE,
        prompt=nissa.PROMPT,
        tools=[
            st.session_state.judge_tool,
            st.session_state.deck_tool,
            card_search_tool,
            rules_search_tool,
        ],
        memory=memory,
        model_name="gpt-4o",
    )
    st.session_state.judge = create_judge_agent(
        system_message=judge.SYSTEM_MESSAGE,
        tools=[card_search_tool, rules_search_tool, judge_report_tool],
        memory=memory,
        model_name="gpt-4o",
    )

# HANDLE SIDEBAR
# upload deck feature
with st.sidebar:

    with st.popover("Upload Deck"):
        deck_name = st.text_input("Deck Name")
        st.write("Cards:")
        deck = st.text_area("Format: 1x Card Name", height=275)

        if st.button("Upload Deck", type="primary", use_container_width=True):
            st.session_state.deck_tool.decks[deck_name] = deck
            st.write(f"Successfully uploaded deck: '{deck_name}'")

    sidebar_text = "Available Decks: \n\n"
    for deck_name in st.session_state.deck_tool.decks.keys():
        sidebar_text += f"**- {deck_name}**  \n"
    st.markdown(sidebar_text)

    # HANDLE BUTTONS
    col1, col2 = st.columns(2)

    # call judge
    if col1.button("Call Judge", type="primary", use_container_width=True):
        st.session_state.judge_tool.is_called = True

    # reset conversation
    if col2.button("Reset Conversation", use_container_width=True):
        # TODO reset memory and chat history
        st.write("resetting conversation")

# HANDLE CHAT
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["image"]):
        st.markdown(message["content"])

# Triggers when user adds input
if query := st.chat_input("What is up?"):
    # Add user message to chat history
    # TODO parse message
    st.session_state.messages.append(
        {"role": "user", "content": query, "image": user.PROFILE_PICTURE}
    )
    # Display user message in chat message container
    with st.chat_message("user", avatar=user.PROFILE_PICTURE):
        st.markdown(query)

    # Display assistant response in chat message container
    with st.chat_message("nissa", avatar=nissa.PROFILE_PICTURE):
        try:
            stream = nissa.astream_response(
                agent_executor=st.session_state.agent,
                query=query,
                decks=list(st.session_state.deck_tool.decks),
                container=st.status,
            )
            generator = to_sync_generator(stream)
            response = st.write_stream(generator)

        except Exception as e:
            logger.error(e)
            response = "Sorry, something went wrong..."

    # TODO parse message
    st.session_state.messages.append(
        {"role": "nissa", "content": response, "image": nissa.PROFILE_PICTURE}
    )

if st.session_state.judge_tool.is_called:
    # TODO does not work when nissa calls the judge
    # Display assistant response in chat message container
    with st.chat_message("judge", avatar=judge.PROFILE_PICTURE):
        stream = judge.astream_response(
            agent_executor=st.session_state.judge,
            container=st.status,
        )
        generator = to_sync_generator(stream)
        response = st.write_stream(generator)
    st.session_state.messages.append(
        {"role": "judge", "content": response, "image": judge.PROFILE_PICTURE}
    )
    st.session_state.judge_tool.is_called = False
