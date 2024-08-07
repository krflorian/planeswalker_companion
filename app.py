import streamlit as st

from mtg.agents import create_llm, create_memory, create_chat_agent, create_judge_agent
from mtg.agents import nissa, judge, user
from mtg.tools import (
    CardSearchTool,
    CardNameSearchTool,
    RulesSearchTool,
    UserDeckLookupTool,
    JudgeReportTool,
)
from mtg.utils.logging import get_logger
from mtg.utils import parse_card_names, load_config, to_sync_generator


# TODO urls and card search for deck upload
# TODO user and persistance for decks

logger = get_logger("mtg-bot")
config = load_config("configs/config.yaml")

model_version = config.llm_settings.llm_model_version

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

if "judge_called" not in st.session_state:
    st.session_state.judge_called = False

if "agent" not in st.session_state:
    # setup tools and llm
    llm = create_llm(model_version)
    memory = create_memory(llm=llm)

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
        model_name="gpt-4o",
    )
    st.session_state.judge = create_judge_agent(
        system_message=judge.SYSTEM_MESSAGE,
        prompt=judge.PROMPT,
        tools=[card_name_search_tool, rules_search_tool, judge_report_tool],
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
            # TODO if not deck_name
            # TODO add info to cards
            # TODO add deck type
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
        st.session_state.judge_called = True

    # reset conversation
    if col2.button("Reset Conversation", use_container_width=True):
        st.session_state.agent.memory.clear()
        st.session_state.messages = st.session_state.messages[:2]
        st.write("resetting conversation")

# HANDLE CHAT
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["image"]):
        st.markdown(message["content"])

# Triggers when user adds input
if query := st.chat_input("What is up?"):
    # Add user message to chat history
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

    parsed_response = parse_card_names(
        response,
        url=config.dataservice_settings.host,
        endpoint="parse_card_urls",
    )

    if "@judge" in parsed_response:
        st.session_state.judge_called = True

    st.session_state.messages.append(
        {"role": "nissa", "content": parsed_response, "image": nissa.PROFILE_PICTURE}
    )
    st.rerun()


if st.session_state.judge_called:
    # TODO does not work when nissa calls the judge
    # Display assistant response in chat message container
    with st.chat_message("judge", avatar=judge.PROFILE_PICTURE):
        stream = judge.astream_response(
            agent_executor=st.session_state.judge,
            container=st.status,
        )
        generator = to_sync_generator(stream)
        response = st.write_stream(generator)

    parsed_response = parse_card_names(
        response,
        url=config.dataservice_settings.host,
        endpoint="parse_card_urls/",
    )
    st.session_state.messages.append(
        {"role": "judge", "content": parsed_response, "image": judge.PROFILE_PICTURE}
    )
    st.session_state.judge_called = False
    st.rerun()
