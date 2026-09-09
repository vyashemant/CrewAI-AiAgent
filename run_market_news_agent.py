import os

from dotenv import load_dotenv
from crewai import LLM, Crew, Process

from agents.market_news_analyst import (
    create_market_news_analyst,
    create_market_news_task,
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
# AGENT + TASK
# ============================================================

market_news_analyst = create_market_news_analyst(
    llm
)

market_news_task = create_market_news_task(
    market_news_analyst
)


# ============================================================
# SAMPLE NEWS DATA
# ============================================================

research_context = """
COMPANY:
Apple Inc.

TICKER:
AAPL

CURRENT MARKET DATA:
Current Price: $310.34
Previous Close: $309.35
52-Week High: $344.57
52-Week Low: $224.69
Market Cap: $4.529T
Beta: 1.086

RECENT NEWS:

1.
Title:
Apple set to launch its new Mac mini, first upgrade in nearly two years

Description:
Apple is reportedly preparing to launch a new Mac mini after
nearly two years. The product has reportedly seen strong demand
and may include newer Apple silicon.

Published:
2026-08-25

Source:
Business Standard

URL:
https://www.business-standard.com/

2.
Title:
Apple Mac Mini: Apple gears up to launch its first New Mac Mini
in two years

Description:
Apple is reportedly preparing a new Mac mini launch, potentially
ahead of a September event. Reports indicate testing involving
newer processor generations.

Published:
2026-08-25

Source:
Economic Times

URL:
https://economictimes.indiatimes.com/

IMPORTANT:

The news descriptions above are the available factual information.

Do not invent additional details.

Do not claim that an event has officially occurred unless the
provided information explicitly states that it occurred.

Do not calculate financial ratios.
"""


# ============================================================
# CREW
# ============================================================

crew = Crew(
    agents=[
        market_news_analyst
    ],

    tasks=[
        market_news_task
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


print("\n")
print("=" * 80)
print("MARKET & NEWS ANALYST RESULT")
print("=" * 80)

print(result)