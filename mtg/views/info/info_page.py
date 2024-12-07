import streamlit as st


st.set_page_config(
    page_title="Contact",
    page_icon="assets/info.webp",
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


# Privacy Policy

Effective Date: 5.12.2024

We value your privacy and are committed to transparency in how we handle your data. This policy explains what we collect, why, and how we protect it.

1. What We Collect  
Chat Data: Anonymized messages sent to the chatbot to improve responses about Magic: The Gathering.  
Cookies: Used to track user activity for rate-limiting and improving functionality.  

2. How We Use Your Data  
Provide accurate and relevant answers.
Monitor and improve system performance.
Enhance the Service by analyzing anonymized data.  

3. Sharing of Data  
We do not sell or share your information with third parties.

4. Data Retention and Deletion  
All data collected is anonymized and cannot be traced back to you. As a result, data cannot be deleted but is used solely to improve the Service.

5. Cookies  
Cookies help us manage requests and analyze usage.  

6. Contact Us  
For questions, contact us at https://github.com/krflorian.

By using the Service, you agree to this Privacy Policy.

"""
)
