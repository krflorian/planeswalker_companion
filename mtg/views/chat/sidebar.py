import streamlit as st
from streamlit.delta_generator import DeltaGenerator


def handle_sidebar():
    with st.sidebar:
        deck_upload()

        col1, col2 = st.columns(2)
        call_judge_button(col2)
        reset_conversation_button(col1)
        ad_window()


def toggle_deck_upload_popover():
    st.session_state.state.deck_upload_popover = True


def deck_upload():
    st.button("Upload Deck", on_click=toggle_deck_upload_popover)

    if st.session_state.deck_tool.decks:
        sidebar_text = "Available Decks: \n\n"
        for deck_name in st.session_state.deck_tool.decks.keys():
            sidebar_text += f"**- {deck_name}**  \n"
        st.markdown(sidebar_text)


def call_judge_button(column: DeltaGenerator):
    if column.button("Call Judge", type="primary", use_container_width=True):
        st.session_state.state.judge_called = True


def reset_conversation_button(column: DeltaGenerator):
    """Clears agent memory and resets the history to the welcome messages."""
    if column.button("Reset Conversation", use_container_width=True):
        st.session_state.agent.memory.clear()
        st.session_state.state.messages = st.session_state.state.messages[:2]
        st.write("resetting conversation")


def ad_window():
    iframe_code = """
    <div style="position:relative; padding-bottom:56.25%; height:0; overflow:hidden;">
        <iframe src="https://www.example.com" 
                style="position:absolute; top:0; left:0; width:100%; height:100%; border:none;" 
                frameborder="0" 
                allowfullscreen>
        </iframe>
    </div>
    """

    st.components.v1.html(iframe_code, height=600)
