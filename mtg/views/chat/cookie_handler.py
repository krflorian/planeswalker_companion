import streamlit as st
from datetime import datetime, timedelta
from streamlit_cookies_controller import CookieController
from mtg.utils.logging import get_logger

logger = get_logger("mtg-bot")

cookie_controller = CookieController()


def set_performance_cookies():
    cookie_controller.set("planeswalker/performance_cookies", True)
    st.success("Your preferences have been saved! 🎉")


# Function to handle cookie preferences
@st.dialog("Cookie Preferences")
def cookie_preferences_dialog():
    st.write(
        """
We Value Your Privacy  
Our website uses cookies to enhance your experience and provide essential functionality.  
We use cookies to track user requests for rate limiting and collect anonymized chat message data to continuously improve Nissas Answers.

You can learn more about how we handle your data in our [Privacy Policy](https://nissa.planeswalkercompanion.com/info_page).
"""
    )
    # accept_ads = st.checkbox("Accept cookies for ads")
    _ = st.checkbox("Accept cookies for performance", value=True, disabled=True)

    pressed = st.button("Save Preferences", on_click=set_performance_cookies)
    if pressed:
        st.rerun()


def handle_cookie_preference_dialog():
    """check if user accepted performance cookies"""
    if not cookie_controller.get("planeswalker/performance_cookies"):
        cookie_preferences_dialog()


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
