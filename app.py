
import streamlit as st

st.set_page_config(
    page_title="FairInfo",
    page_icon="📊",
    layout="wide"
)

st.title("FairInfo")
st.subheader("AI-Powered Investment Intelligence")

st.write(
    "Making financial research more accessible "
    "to everyday investors."
)

st.divider()

company = st.selectbox(
    "Select a company",
    ["Apple (AAPL)", "Microsoft (MSFT)", "NVIDIA (NVDA)"]
)

st.subheader("Financial Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Revenue", "Coming Soon")

with col2:
    st.metric("Net Income", "Coming Soon")

with col3:
    st.metric("Operating Cash Flow", "Coming Soon")

st.divider()

st.subheader("Financial Analysis")
st.info("Financial analysis will appear here.")

st.subheader("FairInfo Risk Alerts")
st.info("Potential financial inconsistencies will appear here.")

st.caption(
    "FairInfo is an educational research prototype, "
    "not personalized investment advice."
)
