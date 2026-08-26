from crewai import LLM
import os

from dotenv import load_dotenv

from agents.risk_analyst import (
    create_risk_analyst,
    create_risk_analysis_task
)


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")


llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.3
)


risk_analyst = create_risk_analyst(llm)

risk_analysis_task = create_risk_analysis_task(
    risk_analyst
)


research_context = """
COMPANY:
Apple Inc.

TICKER:
AAPL

============================================================
MARKET DATA
============================================================

Current Price: 310.34
52-Week High: 344.57
52-Week Low: 224.69
Beta: 1.086
Market Capitalization: 4.53 trillion USD

============================================================
VALUATION DATA
============================================================

Trailing P/E: 35.47x
Forward P/E: 32.54x
Price-to-Sales: 9.70x
Price-to-Book: 42.17x
Enterprise Value: 4.55 trillion USD
EV/EBITDA: 27.10x

============================================================
SEC FINANCIAL DATA
============================================================

Revenue: 416.161 billion USD
Gross Profit: 195.201 billion USD
Operating Income: 133.050 billion USD
Net Income: 112.010 billion USD

Assets: 359.241 billion USD
Liabilities: 285.508 billion USD
Stockholders' Equity: 73.733 billion USD

Cash: 35.934 billion USD
Total Debt: 90.678 billion USD

Operating Cash Flow: 111.482 billion USD
Capital Expenditure: -12.715 billion USD

============================================================
CALCULATED FINANCIAL METRICS
============================================================

Revenue Growth: 6.43%
Net Income Growth: 19.49%

Gross Margin: 46.91%
Operating Margin: 31.97%
Net Profit Margin: 26.92%

Free Cash Flow: 98.767 billion USD
FCF Margin: 23.73%

Debt-to-Equity: 144.58%
Net Cash: -70.666 billion USD

Return on Equity: 151.91%
Return on Assets: 31.18%

Asset Turnover: 1.16
Equity Multiplier: 4.87

============================================================
RECENT NEWS
============================================================

Apple is reportedly preparing a new Mac mini generation.

Recent articles indicate continued interest in Apple's hardware
and AI-related ecosystem.

News data is limited and should not be treated as confirmation
of unannounced company plans.

============================================================
DATA LIMITATIONS
============================================================

Historical valuation ranges are unavailable.

Peer valuation data is unavailable.

Long-term business forecasts are unavailable.

Do not invent missing information.
"""


inputs = {
    "company": "Apple Inc.",
    "research_context": research_context
}


risk_analysis_task.description = risk_analysis_task.description.format(
    company=inputs["company"],
    research_context=inputs["research_context"]
)


result = risk_analyst.execute_task(
    task=risk_analysis_task
)


print("=" * 80)
print("RISK ANALYST RESULT")
print("=" * 80)
print(result)