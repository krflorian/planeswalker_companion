import streamlit as st


def handle_deck_upload_screen():
    # deck upload
    if st.session_state.state.deck_upload_triggered:
        deck_upload_screen()


@st.dialog("Deck Upload")
def deck_upload_screen():
    deck_name = st.text_input("Deck Name")
    st.write("Cards:")
    deck = st.text_area("Format: 1x Card Name", height=275)

    if st.button("Upload Deck", type="primary", use_container_width=True):
        # TODO if not deck_name
        # TODO add info to cards
        # TODO add deck type
        st.session_state.deck_tool.decks[deck_name] = deck
        st.write(f"Successfully uploaded deck: '{deck_name}'")
        st.session_state.state.deck_upload_triggered = False
        st.rerun()
