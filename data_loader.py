
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

COMPANIES = {
    "Apple (AAPL)": "0000320193",
    "Microsoft (MSFT)": "0000789019",
    "NVIDIA (NVDA)": "0001045810"
}

HEADERS = {
    "User-Agent": os.getenv("SEC_USER_AGENT", ""),
    "Accept-Encoding": "gzip, deflate",
}

METRICS = {
    "Revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet"
    ],
    "Net Income": ["NetIncomeLoss"],
    "Operating Cash Flow": [
        "NetCashProvidedByUsedInOperatingActivities"
    ]
}


def get_company_facts(cik):
    if not HEADERS["User-Agent"]:
        raise ValueError("Set SEC_USER_AGENT in your .env file.")

    url = (
        "https://data.sec.gov/api/xbrl/companyfacts/"
        f"CIK{cik}.json"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def get_annual_metric(facts, tags):
    gaap = facts.get("facts", {}).get("us-gaap", {})
    all_entries = []

    for tag in tags:
        if tag not in gaap:
            continue

        entries = gaap[tag].get("units", {}).get("USD", [])

        for item in entries:
            if (
                item.get("form") == "10-K"
                and item.get("fp") == "FY"
                and item.get("start")
                and item.get("end")
                and item.get("fy")
            ):
                duration = (
                    pd.to_datetime(item["end"])
                    - pd.to_datetime(item["start"])
                ).days

                if 330 <= duration <= 380:
                    all_entries.append({
                        "Year End": item["end"],
                        "Value": item["val"],
                        "Filed": item["filed"],
                        "Tag Priority": tags.index(tag)
                    })

    if not all_entries:
        return pd.DataFrame(columns=["Year End", "Value"])

    df = pd.DataFrame(all_entries)

    # Prefer our primary revenue tag when multiple tags
    # describe the same fiscal period.
    df = df.sort_values(
        ["Year End", "Tag Priority", "Filed"],
        ascending=[True, True, False]
    )

    df = df.drop_duplicates(
        subset=["Year End"],
        keep="first"
    )

    df = df.sort_values("Year End").tail(5)

    return df[["Year End", "Value"]]


def get_financial_data(company):
    cik = COMPANIES[company]
    facts = get_company_facts(cik)

    combined = None

    for metric, tags in METRICS.items():
        df = get_annual_metric(facts, tags)
        df = df.rename(columns={"Value": metric})

        if combined is None:
            combined = df
        else:
            combined = pd.merge(
                combined,
                df,
                on="Year End",
                how="outer"
            )

    if combined is None:
        return pd.DataFrame()

    return combined.sort_values("Year End").tail(5)
