
import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_explanation(company, df, analysis):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    client = OpenAI(api_key=api_key)

    # Convert the selected financial periods into safe JSON.
    records = df.tail(2).copy()
    records = records.where(pd.notna(records), None)

    financial_data = records.to_dict(orient="records")

    prompt = f"""
Company: {company}

Financial data (USD):
{json.dumps(financial_data, default=str)}

Calculated financial indicators and alerts:
{json.dumps(analysis, default=str)}

Explain this company's financial results to a retail investor.

Use these sections:
1. Financial Overview
2. Potential Concerns
3. What Investors Should Investigate

Rules:
- Use only the supplied financial data and indicators.
- Do not invent financial figures or company-specific events.
- Do not claim to have reviewed SEC filing narratives.
- Clearly distinguish facts from possible explanations.
- Explain negative cash flow and negative net income carefully.
- Do not label an alert as fraud or misconduct.
- Do not give buy, sell, or hold recommendations.
- Keep the response under 250 words.
- Use clear, beginner-friendly language.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are FairInfo, a financial education assistant. "
            "Explain supplied financial data accurately and neutrally. "
            "If information is missing, acknowledge the limitation."
        ),
        input=prompt,
        max_output_tokens=500
    )

    return response.output_text
