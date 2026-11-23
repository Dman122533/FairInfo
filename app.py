
import streamlit as st
from data_loader import get_company_list, get_financial_data
from analysis import analyze_financials
from ai_explainer import generate_explanation

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


companies = get_company_list()

company = st.selectbox(
    "Search for a company by ticker or name",
    options=list(companies.keys()),
    index=None,
    placeholder="Search AAPL, NVIDIA, Tesla..."
)

if company is None:
    st.info("Search for a company to view its financial data.")
    st.stop()

cik = companies[company]



@st.cache_data(ttl=3600)
def load_data(cik):
    return get_financial_data(cik)


try:
    with st.spinner("Retrieving SEC financial data..."):
        df = load_data(cik)

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

    
    st.subheader("FairInfo Financial Analysis")

    # Allow users to select a historical fiscal year
    available_years = sorted(
        df["Year End"].dropna().unique(),
        reverse=True
    )

    selected_year = st.selectbox(
        "Select Fiscal Year to Analyze",
        available_years
    )

    # Include the selected year and all earlier years
    historical_df = df[
        df["Year End"] <= selected_year
    ].copy()

    analysis = analyze_financials(historical_df)
    
    st.caption(
    f"Analyzing fiscal year ending {selected_year} "
    "against the preceding fiscal year."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        growth = analysis["revenue_growth"]
        st.metric(
            "Revenue Growth",
            f"{growth:+.2f}%" if growth is not None else "N/A"
        )

    with col2:
        growth = analysis["cash_flow_growth"]
        st.metric(
            "Operating Cash Flow Change",
            f"{growth:+.2f}%" if growth is not None else "N/A"
        )

    with col3:
        ratio = analysis["cash_flow_to_income"]

        if ratio is not None:
            st.metric("Cash Flow / Net Income", f"{ratio:.2f}x")
        else:
            st.metric("Cash Flow / Net Income", "N/A")
            st.caption(
                "Ratio unavailable when net income is "
                "negative, zero, or missing."
            )

    st.divider()

    st.subheader("FairInfo Risk Alerts")

    if analysis["alerts"]:
        for alert in analysis["alerts"]:
            st.warning(
                f"**{alert['title']}**\n\n"
                f"{alert['message']}"
            )
    else:
        st.success(
            "No financial inconsistencies were detected "
            "by the current screening rules."
        )

    st.caption(
        "FairInfo alerts are preliminary screening indicators, "
        "not evidence of misconduct or investment advice."
    )

    st.divider()

    st.subheader("FairInfo AI Financial Explanation")

    st.write(
        "Generate a plain-English explanation of the "
        "selected company's financial performance."
    )

    if st.button("Generate AI Explanation", type="primary"):
        try:
            with st.spinner("Analyzing financial information..."):
                explanation = generate_explanation(
                    company,
                    historical_df,
                    analysis
                )

            st.session_state["ai_explanation"] = explanation
            st.session_state["ai_selection"] = (company, selected_year)

        except Exception as error:
            st.error(f"AI explanation unavailable: {error}")

    if st.session_state.get("ai_selection") == (company, selected_year):
        st.markdown(st.session_state["ai_explanation"])

    st.caption(
        "AI explanations use the financial figures and "
        "screening results supplied by FairInfo. "
        "They are not independently verified financial advice."
    )



except Exception as error:
    st.error(f"Unable to load SEC data: {error}")

st.caption(
    "Source: SEC EDGAR | "
    "Educational research prototype, not investment advice."
)
