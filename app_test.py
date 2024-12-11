import streamlit as st
from streamlit_cookies_controller import CookieController


controller = CookieController()
cookies = controller.get("planeswalker/performance_cookies")

st.write(cookies)
