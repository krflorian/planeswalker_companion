import streamlit as st

# Initialize session state for cookies if not already set
if "accept_ads" not in st.session_state:
    st.session_state.accept_ads = None  # None means undecided
if "accept_performance" not in st.session_state:
    st.session_state.accept_performance = None
if "popup_shown" not in st.session_state:
    st.session_state.popup_shown = False  # Track if the popup has been shown


# Function to handle cookie preferences
@st.dialog("Cookie Preferences")
def handle_cookie_preferences():
    st.write("### Cookie Preferences")
    st.write(
        "We use cookies to improve your experience. ",
        "https://nissa.planeswalkercompanion.com/info_page",
    )
    accept_ads = st.checkbox("Accept cookies for ads")
    accept_performance = st.checkbox(
        "Accept cookies for performance", value=True, disabled=True
    )

    if st.button("Save Preferences"):
        st.session_state.accept_ads = accept_ads
        st.success("Your preferences have been saved! 🎉")


# Main app logic
def main():
    if not st.session_state.popup_shown:
        handle_cookie_preferences()

    # Main app content
    st.title("Welcome to My Streamlit App")
    if (
        st.session_state.accept_ads is None
        or st.session_state.accept_performance is None
    ):
        st.info("Please set your cookie preferences using the dialog.")
    else:
        st.success("Cookie preferences have been set.")
        st.write("Here are your preferences:")
        st.write(
            f"Cookies for ads: {'Accepted' if st.session_state.accept_ads else 'Declined'}"
        )
        st.write(
            f"Cookies for performance: {'Accepted' if st.session_state.accept_performance else 'Declined'}"
        )


if __name__ == "__main__":
    main()
