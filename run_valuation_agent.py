import os

from dotenv import load_dotenv
from crewai import LLM, Crew, Process

from agents.valuation_analyst import (
    create_valuation_analyst,
    create_valuation_task,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found."
    )


# ============================================================
# LLM
# ============================================================

llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.3
)


# ============================================================
# AGENT
# ============================================================

valuation_analyst = create_valuation_analyst(
    llm
)


# ============================================================
# TASK
# ============================================================

valuation_task = create_valuation_task(
    valuation_analyst
)


# ============================================================
# SAMPLE VALIDATED RESEARCH CONTEXT
# ============================================================

research_context = """
COMPANY:
Apple Inc.

TICKER:
AAPL


============================================================
MARKET DATA
============================================================

Current Price:
$310.845

Previous Close:
$310.34

Market Capitalization:
$4,532,514,848,768

Beta:
1.086

Dividend Yield:
0.35%


============================================================
VALUATION METRICS
============================================================

Trailing P/E:
35.61x

Forward P/E:
32.56x

Price-to-Sales:
9.71x

Price-to-Book:
42.19x

Enterprise Value:
$4,551,102,955,520

Enterprise Value / EBITDA:
27.10x


============================================================
SEC FINANCIAL DATA
============================================================

Fiscal Year:
2025

Revenue:
$416,161,000,000

Gross Profit:
$195,201,000,000

Operating Income:
$133,050,000,000

Net Income:
$112,010,000,000

Operating Cash Flow:
$111,482,000,000

Capital Expenditure:
-$12,715,000,000


============================================================
PYTHON-CALCULATED FINANCIAL METRICS
============================================================

Gross Margin:
46.91%

Operating Margin:
31.97%

Net Profit Margin:
26.92%

Free Cash Flow:
$98,767,000,000

FCF Margin:
23.73%

ROE:
151.91%

ROA:
31.18%

Asset Turnover:
1.16

Equity Multiplier:
4.87


============================================================
IMPORTANT DATA LIMITATIONS
============================================================

Previous-year revenue is unavailable in the verified SEC context.

Previous-year net income is unavailable.

No peer-company valuation multiples are provided.

No historical valuation range is provided.

Do not invent peer comparisons or historical valuation data.

Do not provide a BUY, SELL, or HOLD recommendation.
"""


# ============================================================
# CREW
# ============================================================

crew = Crew(
    agents=[
        valuation_analyst
    ],

    tasks=[
        valuation_task
    ],

    process=Process.sequential,

    verbose=True
)


# ============================================================
# RUN
# ============================================================

result = crew.kickoff(
    inputs={
        "company": "Apple Inc.",
        "research_context": research_context
    }
)


# ============================================================
# OUTPUT
# ============================================================

print("\n")
print("=" * 80)
print("VALUATION ANALYST RESULT")
print("=" * 80)

print(result)