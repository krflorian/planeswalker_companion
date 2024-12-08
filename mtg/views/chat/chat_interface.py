from typing import Protocol
import streamlit as st
from mtg.utils.logging import get_logger
from uuid import uuid4
from mtg.agents import nissa, judge, user
from mtg.utils import (
    parse_card_names,
    to_sync_generator,
    MTGBotConfig,
)

from datetime import datetime, timedelta
from langfuse import Langfuse
from streamlit_cookies_controller import CookieController


cookie_controller = CookieController()

langfuse = Langfuse()

logger = get_logger("mtg-bot")


RATE_LIMIT_TEXT = """Oops, you've reached the limit! 🚦

It seems we’ve hit the API rate limit for now. Since this isn’t a commercial project and the API calls are privately funded, we’ve set a limit to help manage costs.

But don’t worry—it’s just a short wait! ⏳ You’ll be able to use the bot again in 60 minutes.

We’re also working on an exciting option for power users in the future—where you can enjoy unlimited access by simply buying us a coffee ☕. Stay tuned for updates!

Thanks so much for your patience and understanding. If you’re enjoying the bot, feel free to share your feedback or spread the word. See you in an hour! 🚀

"""


class Agent(Protocol):
    def astream_response():
        pass


def handle_chat(config: MTGBotConfig, callback_handler=None):
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
                dataservice_host=config.dataservice_settings.host,
                decks=st.session_state.deck_tool.decks,
                callback_handler=callback_handler,
                trace_id=trace_id,
                session_id=st.session_state.state.session_id,
                config=config,
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

        trace_id = str(uuid4())
        with st.chat_message("judge", avatar=judge.PROFILE_PICTURE):
            parsed_response = call_agent(
                agent=judge,
                agent_executor=st.session_state.judge,
                dataservice_host=config.dataservice_settings.host,
                callback_handler=callback_handler,
                trace_id=trace_id,
                session_id=st.session_state.state.session_id,
                config=config,
            )
            langfuse.trace(
                id=trace_id, input=st.session_state.state.messages[-2]["content"]
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
    session_id: str,
    config: MTGBotConfig,
    query: str = None,
    callback_handler: callable = None,
    **kwargs,
) -> str:
    """handles agent response"""

    request_count = increase_request_count(
        waiting_time_duration=config.rate_limit_settings.waiting_time
    )
    if request_count > config.rate_limit_settings.max_requests:
        expiration_date = cookie_controller.get("planeswalker/expiration_date")
        logger.info(f"hit rate limit - will end at {expiration_date}")
        return RATE_LIMIT_TEXT

    try:
        stream = agent.astream_response(
            agent_executor=agent_executor,
            container=st.status,
            query=query,
            callback_handler=callback_handler,
            trace_id=trace_id,
            session_id=session_id,
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


def increase_request_count(waiting_time_duration: int) -> int:
    """check cookies for request count and increase by one, also set expiration date."""

    request_count = cookie_controller.get("planeswalker/request_count") or 0
    expiration_date = cookie_controller.get("planeswalker/expiration_date")

    if expiration_date is None:
        expiration_date = datetime.now() + timedelta(minutes=waiting_time_duration)
        cookie_controller.set(
            "planeswalker/expiration_date",
            expiration_date.isoformat(),
            expires=expiration_date,
        )
    else:
        expiration_date = datetime.fromisoformat(expiration_date)
        if datetime.now() > expiration_date:
            expiration_date = datetime.now() + timedelta(minutes=waiting_time_duration)
            request_count = 0

    request_count += 1
    cookie_controller.set(
        "planeswalker/request_count", request_count, expires=expiration_date
    )
    logger.info(f"request count {request_count} - expiration date {expiration_date}")
    return request_count
