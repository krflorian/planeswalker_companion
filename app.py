import streamlit as st
from pydantic import BaseModel, Field
from uuid import uuid4
from mtg.utils import load_config


config = load_config("configs/config.yaml")


class State(BaseModel):
    session_id: str
    judge_called: bool
    deck_upload_triggered: bool
    messages: list[dict] = Field(default_factory=list)


if "state" not in st.session_state:
    st.session_state.state = State(
        session_id=str(uuid4()),
        judge_called=False,
        deck_upload_triggered=False,
    )

chat_page = st.Page(
    page="mtg/views/chat/chat_page.py",
    title="Chat",
)

info_page = st.Page(
    page="mtg/views/info/info_page.py",
    title="Info",
)

pg = st.navigation(pages=[chat_page, info_page])
pg.run()
