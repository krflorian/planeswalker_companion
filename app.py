from pathlib import Path
import streamlit as st

from mtg.agents import create_llm, create_memory, create_chat_agent
from mtg.agents import nissa, judge, user
from mtg.tools import CardSearchTool, RulesSearchTool, UserDeckLookupTool, CallJudgeTool
from mtg.utils.logging import get_logger
from mtg.utils.ui import to_sync_generator


logger = get_logger(__name__)


# TODO upvote, downvote

VERSION = "1.0.0"
MODEL_VERSION = "gpt-4o"

FOOTER_TEXT = f"""
Support Nissa on [Patreon](https://www.patreon.com/NissaPlaneswalkerCompanion)  
version: {VERSION}  
chat model: {MODEL_VERSION}
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
    llm = create_llm(MODEL_VERSION)
    memory = create_memory(llm=llm)
    judge_tool = CallJudgeTool()
    card_search_tool = CardSearchTool()
    rules_search_tool = RulesSearchTool()
    deck_lookup_tool = UserDeckLookupTool()

    st.session_state.call_judge = judge_tool
    st.session_state.agent = create_chat_agent(
        tools=[judge_tool, card_search_tool, rules_search_tool, deck_lookup_tool],
        memory=memory,
        model_name="gpt-4o",
        system_message=nissa.SYSTEM_MESSAGE,
        prompt=nissa.PROMPT,
    )
    # st.session_state.judge = create

if "uploaded_files" not in st.session_state:
    decks_path = Path("data/decks")
    st.session_state.uploaded_files = set()
    for file in decks_path.iterdir():
        if file.suffix == ".txt":
            st.session_state.uploaded_files.add(file.stem)

# HANDLE SIDEBAR
# upload deck feature
with st.sidebar:

    data_path = Path("data/decks")
    uploaded_file = st.file_uploader("## Upload your deck here:", type="txt")
    if (uploaded_file is not None) and (
        uploaded_file.name not in st.session_state.uploaded_files
    ):
        with (data_path / uploaded_file.name).open("wb") as outfile:
            outfile.write(uploaded_file.getbuffer())
        st.session_state.uploaded_files.add(uploaded_file.stem)

    sidebar_text = "Available Decks: \n\n"
    for file in data_path.iterdir():
        if file.suffix == ".txt":
            sidebar_text += f"**- {file.stem}**  \n"
    st.markdown(sidebar_text)

    # HANDLE BUTTONS and JUDGE
    # check if judge is called
    col1, col2 = st.columns(2)

    if (
        col1.button("Call Judge", type="primary", use_container_width=True)
        or st.session_state.call_judge.is_called
    ):
        st.session_state.messages.append(
            {
                "role": "judge",
                "content": "i am the judge and i will check all rules questions",
                "image": judge.PROFILE_PICTURE,
            }
        )
        st.session_state.call_judge.is_called = False

    if col2.button("Reset Conversation", use_container_width=True):
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
        stream = nissa.astream_response(
            agent_executor=st.session_state.agent,
            query=query,
            decks=list(st.session_state.uploaded_files),
            container=st.status,
        )
        generator = to_sync_generator(stream)
        response = st.write_stream(generator)

    # TODO parse message
    st.session_state.messages.append(
        {"role": "nissa", "content": response, "image": nissa.PROFILE_PICTURE}
    )
