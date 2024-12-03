import streamlit as st
from datetime import datetime, timedelta

from streamlit_cookies_controller import CookieController

st.set_page_config("Cookie QuickStart", "🍪", layout="wide")

controller = CookieController()


rate_limit = 10
window_duration = 1


def increase_count(window_duration: int = window_duration):
    """check cookies for request count and increase by one, also set expiration date."""

    request_count = controller.get("planeswalker/request_count") or 0
    expiration_date = controller.get("planeswalker/expiration_date")

    if expiration_date is None:
        expiration_date = datetime.now() + timedelta(minutes=window_duration)
        controller.set(
            "planeswalker/expiration_date",
            expiration_date.isoformat(),
            expires=expiration_date,
        )
    else:
        expiration_date = datetime.fromisoformat(expiration_date)
        if datetime.now() > expiration_date:
            expiration_date = datetime.now() + timedelta(minutes=window_duration)
            request_count = 0

    request_count += 1
    controller.set("planeswalker/request_count", request_count, expires=expiration_date)


st.button(label="click", on_click=increase_count)

request_count = controller.get("planeswalker/request_count") or 0
if request_count >= rate_limit:
    st.error("Rate Limit!")
    st.stop()
else:
    st.write(f"you can still go - requests {request_count}")
