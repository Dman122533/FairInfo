
import streamlit as st
from data_loader import COMPANIES, get_financial_data
def format_money(value):
    if value != value:  # Handles missing values
        return "N/A"
    elif abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    else:
        return f"${value:,.2f}"

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
    list(COMPANIES.keys())
)


@st.cache_data(ttl=3600)
def load_data(selected_company):
    return get_financial_data(selected_company)


try:
    with st.spinner("Retrieving SEC financial data..."):
        df = load_data(company)

    if df.empty:
        st.warning("No financial data was found.")
        st.stop()

    latest = df.iloc[-1]

    st.subheader("Financial Overview")
    st.caption(f"Latest available fiscal year: {latest['Year End']}")

    col1, col2, col3 = st.columns(3)

    metrics = [
        ("Revenue", col1),
        ("Net Income", col2),
        ("Operating Cash Flow", col3)
    ]

    for metric, column in metrics:
        value = latest[metric]

        if st.session_state.get("unused", False):
            pass

        with column:
            if value != value:  # Missing value
                st.metric(metric, "N/A")
            else:
                st.metric(metric, f"${value / 1e9:,.2f}B")

    st.divider()

    st.subheader("Historical Financial Data")

    formatted_df = df.copy()

    for column in ["Revenue", "Net Income", "Operating Cash Flow"]:
        formatted_df[column] = formatted_df[column].apply(format_money)

    st.dataframe(
        formatted_df,
        use_container_width=True,
        hide_index=True
    )
    st.subheader("Financial Trends")

    chart_data = df.set_index("Year End")[
        ["Revenue", "Net Income", "Operating Cash Flow"]
    ] / 1e9

    st.line_chart(chart_data)

    st.caption("Values shown in billions of USD.")

    st.subheader("FairInfo Risk Alerts")
    st.info(
        "Financial inconsistency detection "
        "will be added in the next development stage."
    )

except Exception as error:
    st.error(f"Unable to load SEC data: {error}")

st.caption(
    "Source: SEC EDGAR | "
    "Educational research prototype, not investment advice."
)
