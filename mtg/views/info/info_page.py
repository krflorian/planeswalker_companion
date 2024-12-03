import streamlit as st


st.set_page_config(
    page_title="Contact",
    page_icon="assets/builder.webp",
    layout="wide",
)

st.markdown(
    """

    <style>

    /* Hide the Streamlit header and menu */

    header {visibility: hidden;}

    /* Optionally, hide the footer */

    .streamlit-footer {display: none;}

    </style>

    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
# Contact 
### Florian Krempl  
https://github.com/krflorian  
Kleine Pfarrgasse 5/15  
1020 Wien  
AUSTRIA 
"""
)
