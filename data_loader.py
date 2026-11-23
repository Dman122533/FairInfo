
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

COMPANIES = {
    "Apple (AAPL)": "0000320193",
    "Microsoft (MSFT)": "0000789019",
    "NVIDIA (NVDA)": "0001045810"
}

@st.cache_data(ttl=86400)
def get_company_list():
    url = "https://www.sec.gov/files/company_tickers.json"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    companies = response.json()

    company_list = {}

    for company in companies.values():
        ticker = company["ticker"]
        name = company["title"]
        cik = str(company["cik_str"]).zfill(10)

        label = f"{ticker} - {name}"
        company_list[label] = cik

    return dict(sorted(company_list.items()))


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
                        "Accession": item.get("accn"),
                        "Tag Priority": tags.index(tag)
                    })

    if not all_entries:
        return pd.DataFrame(columns=["Year End", "Value", "Accession"])

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

    return df[["Year End", "Value", "Accession"]]


def get_financial_data(cik):
    facts = get_company_facts(cik)

    combined = None

    for metric, tags in METRICS.items():
        df = get_annual_metric(facts, tags)

        df = df.rename(
            columns={
                "Value": metric,
                "Accession": f"{metric} Accession"
            }
        )

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
