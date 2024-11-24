import streamlit as st


rules_page = st.Page(
    page="mtg/views/rules_page.py",
    title="Rules",
    # icon=":data/assets/favicon1.jpg:",
)

contact_page = st.Page(
    page="mtg/views/contact_page.py",
    title="Contact",
    # icon="data/assets/favicon1.jpgs"
)

pg = st.navigation(pages=[rules_page, contact_page])
pg.run()
