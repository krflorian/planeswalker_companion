from typing import Protocol
import streamlit as st
from mtg.utils.logging import get_logger
from uuid import uuid4
from mtg.agents import nissa, judge, user
from mtg.utils import parse_card_names, to_sync_generator

from langfuse import Langfuse

langfuse = Langfuse()

logger = get_logger("mtg-bot")


class Agent(Protocol):
    def astream_response():
        pass


def handle_chat(dataservice_host: str, callback_handler=None):
    # Display chat messages from history on app rerun
    display_chat_history()

    # Triggers when user adds input
    if query := st.chat_input("What is up?"):
        # Add user message to chat history
        trace_id = str(uuid4())
        st.session_state.state.messages.append(
            {
                "role": "user",
                "content": query,
                "image": user.PROFILE_PICTURE,
                "trace_id": trace_id,
            }
        )
        # Display user message in chat message container
        with st.chat_message("user", avatar=user.PROFILE_PICTURE):
            st.markdown(query)

        # Display assistant response in chat message container
        with st.chat_message("nissa", avatar=nissa.PROFILE_PICTURE):
            parsed_response = call_agent(
                agent=nissa,
                agent_executor=st.session_state.agent,
                query=query,
                dataservice_host=dataservice_host,
                decks=st.session_state.deck_tool.decks,
                callback_handler=callback_handler,
                trace_id=trace_id,
            )

        if "@judge" in parsed_response:
            parsed_response = parsed_response.replace("@judge", "")
            st.session_state.state.judge_called = True

        st.session_state.state.messages.append(
            {
                "role": "nissa",
                "content": parsed_response,
                "image": nissa.PROFILE_PICTURE,
                "trace_id": trace_id,
            }
        )
        st.rerun()

    if st.session_state.state.judge_called:
        with st.chat_message("judge", avatar=judge.PROFILE_PICTURE):
            trace_id = st.session_state.state.messages[-1]["trace_id"]
            parsed_response = call_agent(
                agent=judge,
                agent_executor=st.session_state.judge,
                dataservice_host=dataservice_host,
                callback_handler=callback_handler,
                trace_id=trace_id,
            )

        st.session_state.state.messages.append(
            {
                "role": "judge",
                "content": parsed_response,
                "image": judge.PROFILE_PICTURE,
                "trace_id": trace_id,
            }
        )
        st.session_state.state.judge_called = False
        st.rerun()


def record_feedback(feedback: int):
    feedback_mapping = {0: "BAD", 1: "GOOD"}
    trace_id = st.session_state.state.messages[-1]["trace_id"]

    langfuse.score(
        trace_id=trace_id,
        name="feedback",
        value=feedback_mapping.get(feedback),
        data_type="CATEGORICAL",
    )
    st.toast("thank you for your feedback!")


def display_chat_history():
    for idx, message in enumerate(st.session_state.state.messages):
        with st.chat_message(message["role"], avatar=message["image"]):
            st.markdown(message["content"])
            if idx == len(st.session_state.state.messages) - 1:
                feedback = st.feedback(options="thumbs")
    if feedback is not None:
        record_feedback(feedback)


def call_agent(
    agent: Agent,
    agent_executor,
    dataservice_host: str,
    trace_id: str,
    query: str = None,
    callback_handler: callable = None,
    **kwargs,
) -> str:
    """handles agent response"""
    try:
        stream = agent.astream_response(
            agent_executor=agent_executor,
            container=st.status,
            query=query,
            callback_handler=callback_handler,
            trace_id=trace_id,
            **kwargs,
        )
        generator = to_sync_generator(stream)
        response = st.write_stream(generator)
        parsed_response = parse_card_names(
            response,
            url=dataservice_host,
            endpoint="parse_card_urls",
        )

    except Exception as e:
        logger.error(e)
        parsed_response = """Sorry, something went wrong, please try reloading the page...  
        If this Problem continues, please contact the admin."""

    return parsed_response
