
import pandas as pd


def calculate_growth(current, previous):
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return None

    return ((current - previous) / abs(previous)) * 100


def analyze_financials(df):
    """Analyze financial performance and identify warning signals."""

    results = {
        "revenue_growth": None,
        "cash_flow_growth": None,
        "cash_flow_to_income": None,
        "alerts": []
    }

    if len(df) < 2:
        return results

    df = df.sort_values("Year End").reset_index(drop=True)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    revenue_growth = calculate_growth(
        latest["Revenue"],
        previous["Revenue"]
    )

    cash_flow_growth = calculate_growth(
        latest["Operating Cash Flow"],
        previous["Operating Cash Flow"]
    )

    results["revenue_growth"] = revenue_growth
    results["cash_flow_growth"] = cash_flow_growth

    # Cash flow compared to reported net income
    net_income = latest["Net Income"]
    cash_flow = latest["Operating Cash Flow"]

    if pd.notna(net_income) and net_income > 0 and pd.notna(cash_flow):
        results["cash_flow_to_income"] = cash_flow / net_income

    # Alert 1: Revenue increasing while cash flow decreases
    if (
        revenue_growth is not None
        and cash_flow_growth is not None
        and revenue_growth > 0
        and cash_flow_growth < 0
    ):
        results["alerts"].append({
            "title": "Revenue and Cash Flow Divergence",
            "message": (
                f"Revenue increased by {revenue_growth:.2f}% "
                f"while operating cash flow declined by "
                f"{abs(cash_flow_growth):.2f}%. "
                "This divergence may warrant further investigation."
            )
        })

    # Alert 2: Negative operating cash flow
    if pd.notna(cash_flow) and cash_flow < 0:
        results["alerts"].append({
            "title": "Negative Operating Cash Flow",
            "message": (
                "The company reported negative operating cash flow "
                "for its latest fiscal year. This may indicate "
                "cash generation challenges."
            )
        })

    # Alert 3: Low cash flow relative to net income
    ratio = results["cash_flow_to_income"]

    if ratio is not None and ratio < 0.75:
        results["alerts"].append({
            "title": "Low Cash Flow Relative to Net Income",
            "message": (
                f"Operating cash flow represents only "
                f"{ratio * 100:.1f}% of reported net income. "
                "This difference may warrant further analysis."
            )
        })

    return results
