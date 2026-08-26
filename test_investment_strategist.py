import os
import json

from dotenv import load_dotenv
from crewai import LLM, Crew, Process

from agents.investment_strategist import (
    create_investment_strategist,
    create_investment_strategy_task,
    InvestmentStrategy,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")


# ============================================================
# LLM  (same model / temperature as all other agents)
# ============================================================

llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.3
)


# ============================================================
# SAMPLE SPECIALIST REPORTS  (Apple Inc. / AAPL)
#
# These are representative outputs that the four specialist
# agents would have produced in the full pipeline.
# Using static samples so this test runs independently without
# network calls to Yahoo Finance / SEC EDGAR / Marketaux.
# ============================================================

FINANCIAL_ANALYST_REPORT = """
FINANCIAL RESEARCH REPORT - Apple Inc. (AAPL)

DATA SOURCES:
- Market data: Yahoo Finance via yfinance
- Financial statements: SEC EDGAR XBRL (FY2025)

LATEST FINANCIAL REPORTING PERIOD:
- Company: Apple Inc.
- Ticker: AAPL
- Form: 10-K
- Fiscal Year: 2025
- Period End: 2025-09-27

CURRENT MARKET SNAPSHOT (Verified - Yahoo Finance):
- Current Price: $310.34
- 52-Week High: $344.57
- 52-Week Low: $224.69
- Market Capitalization: $4.53 trillion USD
- Beta: 1.086
- Dividend Yield: 0.35%

RETRIEVED FINANCIAL FACTS (Verified - SEC EDGAR FY2025):
- Revenue: $416.161 billion
- Gross Profit: $195.201 billion
- Operating Income: $133.050 billion
- Net Income: $112.010 billion
- Assets: $359.241 billion
- Liabilities: $285.508 billion
- Stockholders' Equity: $73.733 billion
- Cash and Equivalents: $35.934 billion
- Total Debt: $90.678 billion
- Operating Cash Flow: $111.482 billion
- Capital Expenditure: -$12.715 billion

CALCULATED METRICS (Python Financial Metrics Engine):
- Revenue Growth: 6.43%
- Net Income Growth: 19.49%
- Gross Margin: 46.91%
- Operating Margin: 31.97%
- Net Profit Margin: 26.92%
- Free Cash Flow: $98.767 billion
- FCF Margin: 23.73%
- Debt-to-Equity: 144.58%
- Net Cash: -$70.666 billion (net debt position)
- Return on Equity (ROE): 151.91%
- Return on Assets (ROA): 31.18%
- Asset Turnover: 1.16x
- Equity Multiplier: 4.87x

KEY FINANCIAL STRENGTHS:
1. Exceptional profitability: operating margin 31.97%, net margin 26.92%
2. Strong free cash flow of $98.767 billion (FCF margin 23.73%)
3. High capital efficiency: ROE 151.91%, ROA 31.18%
4. Revenue and net income growing: 6.43% and 19.49% respectively

KEY FINANCIAL WEAKNESSES / CONCERNS:
1. Net debt position: $70.666 billion (debt exceeds cash)
2. High debt-to-equity of 144.58% driven by buyback-heavy capital structure
3. High equity multiplier (4.87x) indicates significant financial leverage
4. Revenue growth of 6.43% is moderate for a company trading at premium multiples

OVERALL FINANCIAL HEALTH ASSESSMENT (Analyst Interpretation):
Apple demonstrates exceptional profitability and cash generation. The balance
sheet shows a net debt position, but this is largely by design given Apple's
aggressive share buyback programme funded by its massive free cash flow.
The business fundamentals are strong. Whether the stock price reflects fair
value is a separate valuation question.

DATA LIMITATIONS:
- Historical revenue and net income data (prior year) available only via
  calculated growth rates from the metrics engine.
- No peer-company financial data available.
"""

MARKET_NEWS_ANALYST_REPORT = """
MARKET AND NEWS RESEARCH REPORT - Apple Inc. (AAPL)

RECENT COMPANY DEVELOPMENTS:
Apple is reportedly preparing a new Mac mini generation, which would be the
first upgrade to that product line in nearly two years.

KEY NEWS EVENTS (Verified - Marketaux, 2026-08-25):
1. Source: Business Standard
   Title: Apple set to launch its new Mac mini, first upgrade in nearly two years
   Description: Apple is reportedly preparing to launch a new Mac mini
   after nearly two years. The product has reportedly seen strong demand
   and may include newer Apple silicon.

2. Source: Economic Times
   Title: Apple Mac Mini - Apple gears up to launch its first New Mac Mini in two years
   Description: Apple is reportedly preparing a new Mac mini launch,
   potentially ahead of a September event. Reports include testing of
   newer processor generations.

MARKET ACTIVITY (Verified - Yahoo Finance):
- Current Price: $310.34 (previous close: $309.35)
- 52-Week Range: $224.69 - $344.57
- The stock is trading approximately 9.9% below its 52-week high
- Beta: 1.086 (slightly above-market volatility)

POSITIVE CATALYSTS (Analyst Interpretation):
- Potential Mac mini product refresh could stimulate hardware refresh cycle
- Continued interest in Apple's AI-related ecosystem may drive services growth
- Upcoming September product event historically associated with iPhone launch

NEGATIVE CATALYSTS / CONCERNS (Analyst Interpretation):
- The Mac mini refresh is reported, not officially announced - risk of delay
- Limited news coverage reduces confidence in near-term catalyst timing

INDUSTRY / EXTERNAL FACTORS (Analyst Interpretation):
- The broader AI hardware and services cycle may benefit Apple's ecosystem
- Macro uncertainties could affect consumer hardware spending

POTENTIAL STOCK IMPACT (Analyst Interpretation):
- A confirmed Mac mini launch and broader product event could provide
  a short-term positive catalyst
- Without a confirmed launch, near-term catalysts from hardware are unclear

INFORMATION LIMITATIONS:
- News coverage is limited to two articles from 2026-08-25
- No earnings guidance, analyst estimate changes, or macro data available
- No information on recent institutional or insider activity
- All news-based scenarios are speculative; only reported/confirmed facts
  should be treated as verified
"""

VALUATION_ANALYST_REPORT = """
VALUATION RESEARCH REPORT - Apple Inc. (AAPL)

VALUATION OVERVIEW:
Apple is currently valued at a significant premium across all major valuation
metrics. The following analysis uses only the verified data provided.

RETRIEVED VALUATION METRICS (Yahoo Finance via yfinance):
- Market Capitalization: $4.53 trillion USD
- Trailing P/E: 35.47x
- Forward P/E: 32.54x
- Price-to-Sales: 9.70x
- Price-to-Book: 42.17x
- Enterprise Value: $4.55 trillion USD
- EV/EBITDA: 27.10x

EARNINGS VALUATION:
Trailing P/E of 35.47x and Forward P/E of 32.54x indicate the market is
pricing Apple at a significant premium to average historical market multiples.
The forward P/E implies some expectation of earnings growth.

REVENUE VALUATION:
Price-to-Sales of 9.70x is elevated for a hardware-led technology company.
It implies the market is pricing in continued high margins and growth.

BOOK-VALUE VALUATION:
Price-to-Book of 42.17x is extremely elevated. This is partly explained by
Apple's aggressive buyback programme reducing book equity, and partly by the
premium the market assigns to Apple's brand, ecosystem, and earnings power.
This metric alone is not a reliable valuation anchor given the capital structure.

ENTERPRISE VALUATION:
EV/EBITDA of 27.10x is well above typical industrial and consumer averages.
For a company growing revenue at 6.43%, this implies the market is paying
for a combination of margin quality and perceived durability of earnings.

CASH-FLOW VALUATION:
Free Cash Flow: $98.767 billion (Python-calculated)
Market Cap / FCF (Price-to-FCF, analyst-derived): approximately 45.9x
This is a high multiple relative to the FCF yield it implies (~2.2%).
Note: This ratio was derived by the analyst from provided data, not
retrieved from an external source.

VALUATION VERSUS FUNDAMENTALS:
Apple's financial fundamentals are strong (46.91% gross margin, 23.73% FCF
margin, 31.97% operating margin). The premium multiples are partly justified
by this quality. However:
- Revenue growth of 6.43% is moderate and may not support current multiples
  over the long term unless services or AI-driven growth accelerates
- Without peer data or historical valuation ranges, it is not possible to
  determine whether current multiples are historically unusual or typical
  for Apple

VALUATION STRENGTHS:
- FCF generation supports the market cap at current multiples
- Strong margins provide downside buffer

VALUATION RISKS:
- Multiple compression risk if revenue growth disappoints
- No margin of safety visible at current multiples
- Elevated Price-to-FCF (~45.9x) leaves limited room for fundamental underperformance

OVERALL VALUATION ASSESSMENT (Analyst Interpretation):
Apple is priced at a premium that reflects its quality but leaves limited
margin of safety. The stock is NOT cheap by any standard metric. Whether the
premium is justified depends on future growth - particularly in services and
AI - which is not available in the verified context.

DATA LIMITATIONS:
- No historical valuation range for Apple available
- No peer-company multiples available
- No forward earnings growth estimates available
- Do not invent historical ranges or peer comparisons
"""

RISK_ANALYST_REPORT = """
RISK ANALYSIS REPORT - Apple Inc. (AAPL)

RISK ANALYSIS OVERVIEW:
Apple is a high-quality business with a robust financial profile. However,
its current valuation creates meaningful downside risk if fundamentals
disappoint. Risks are identified below by category.

1. FINANCIAL RISK
Verified data:
- Total Debt: $90.678 billion
- Cash: $35.934 billion
- Net Debt: $70.666 billion (net debt position)
- Debt-to-Equity: 144.58%
- Equity Multiplier: 4.87x

Assessment (Analyst Interpretation):
While the net debt position is notable, Apple's $98.767 billion free cash
flow provides strong debt-servicing capacity. The financial risk from
leverage is moderated by cash generation. Debt-to-equity is elevated
primarily due to buyback-driven equity reduction, not impaired solvency.
Financial risk is MODERATE given the context.

2. BUSINESS RISK
Verified data supports the following concerns:
- Revenue growth of 6.43% is moderate. Sustained premium valuation requires
  either growth acceleration or sustained margin strength.
- Product concentration: hardware remains the primary revenue driver.
  Services and software are growing but composition data is unavailable.
- Upcoming product cycle (Mac mini) may support near-term hardware revenue,
  but this has not been officially confirmed.
Business risk is MODERATE.

3. MARKET RISK
Verified data:
- Beta: 1.086 (slightly above-market)
- Current price: $310.34 (9.9% below 52-week high of $344.57)
- 52-week low: $224.69 (28% below current price - significant historical downside)

Assessment (Analyst Interpretation):
Beta of 1.086 implies slightly above-average market sensitivity. The 52-week
range shows the stock has experienced significant volatility. Market risk
is MODERATE.

4. VALUATION RISK
Verified data:
- Trailing P/E: 35.47x
- Forward P/E: 32.54x
- EV/EBITDA: 27.10x
- Price-to-FCF: ~45.9x (analyst-derived)

Assessment (Analyst Interpretation):
At current multiples, any earnings shortfall, revenue disappointment, or
macro deterioration could trigger material multiple compression. The lack
of a visible margin of safety makes VALUATION RISK HIGH. This is the
primary risk for the investment case.

5. NEWS AND EVENT RISK
Verified events:
- Reported (not confirmed) Mac mini launch ahead of September event
News risk is LOW to MODERATE. The news base is limited.

6. DATA-QUALITY RISK
Important limitations:
- No peer company data available
- No historical valuation range available
- No forward earnings guidance available
- No information on Apple's services/hardware revenue mix breakdown

These gaps reduce confidence in the overall assessment. Data-quality risk
is MODERATE.

KEY RISK FACTORS:
1. HIGH: Valuation risk - premium multiples with limited margin of safety
2. MODERATE: Revenue growth deceleration risk
3. MODERATE: Net debt position (though manageable given FCF)
4. MODERATE: Market volatility (Beta >1, wide 52-week range)
5. LOW-MODERATE: Business model concentration in hardware

OVERALL RISK ASSESSMENT (Analyst Interpretation):
The primary risk is valuation. Apple's business quality mitigates most
fundamental risks, but the stock price leaves limited room for error.
An investor accepting current multiples is essentially paying for continued
execution and growth acceleration - neither of which is guaranteed by the
available evidence.
"""


# ============================================================
# AGENT AND TASK
# ============================================================

investment_strategist = create_investment_strategist(llm)

investment_strategy_task = create_investment_strategy_task(
    investment_strategist
)


# ============================================================
# CREW
# ============================================================

crew = Crew(
    agents=[
        investment_strategist
    ],

    tasks=[
        investment_strategy_task
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
        "financial_analyst_report": FINANCIAL_ANALYST_REPORT,
        "market_news_analyst_report": MARKET_NEWS_ANALYST_REPORT,
        "valuation_analyst_report": VALUATION_ANALYST_REPORT,
        "risk_analyst_report": RISK_ANALYST_REPORT,
    }
)


# ============================================================
# OUTPUT
# ============================================================

print("\n")
print("=" * 48)
print("INVESTMENT STRATEGIST RESULT")
print("=" * 48)

# result.pydantic gives us the structured InvestmentStrategy object
# when output_pydantic is set on the task.
strategy = result.pydantic

if strategy is None:
    # Fallback: print raw output if structured parsing failed
    print("\n[WARNING] Pydantic structured output not available.")
    print("Raw output:")
    print(result.raw)
else:
    print(f"\nCOMPANY:              Apple Inc. (AAPL)")
    print(f"RECOMMENDATION:       {strategy.recommendation}")
    print(f"CONFIDENCE:           {strategy.confidence}")
    print()

    print("-" * 48)
    print("INVESTMENT THESIS")
    print("-" * 48)
    print(strategy.investment_thesis)
    print()

    print("-" * 48)
    print("COMPANY QUALITY")
    print("-" * 48)
    print(strategy.company_quality)
    print()

    print("-" * 48)
    print("VALUATION VIEW")
    print("-" * 48)
    print(strategy.valuation_view)
    print()

    print("-" * 48)
    print("FUNDAMENTAL ASSESSMENT")
    print("-" * 48)
    print(strategy.fundamental_assessment)
    print()

    print("-" * 48)
    print("MARKET & NEWS ASSESSMENT")
    print("-" * 48)
    print(strategy.market_and_news_assessment)
    print()

    print("-" * 48)
    print("VALUATION ASSESSMENT")
    print("-" * 48)
    print(strategy.valuation_assessment)
    print()

    print("-" * 48)
    print("RISK ASSESSMENT")
    print("-" * 48)
    print(strategy.risk_assessment)
    print()

    print("-" * 48)
    print("BULL CASE")
    print("-" * 48)
    print(strategy.bull_case)
    print()

    print("-" * 48)
    print("BASE CASE")
    print("-" * 48)
    print(strategy.base_case)
    print()

    print("-" * 48)
    print("BEAR CASE")
    print("-" * 48)
    print(strategy.bear_case)
    print()

    print("-" * 48)
    print("KEY CATALYSTS")
    print("-" * 48)
    for i, catalyst in enumerate(strategy.key_catalysts, 1):
        print(f"  {i}. {catalyst}")
    print()

    print("-" * 48)
    print("KEY RISKS")
    print("-" * 48)
    for i, risk in enumerate(strategy.key_risks, 1):
        print(f"  {i}. {risk}")
    print()

    print("-" * 48)
    print("THESIS CHANGE TRIGGERS")
    print("-" * 48)
    for i, trigger in enumerate(strategy.thesis_change_triggers, 1):
        print(f"  {i}. {trigger}")
    print()

    print("-" * 48)
    print("EVIDENCE SUMMARY")
    print("-" * 48)
    print(strategy.evidence_summary)
    print()

    print("-" * 48)
    print("INFORMATION LIMITATIONS")
    print("-" * 48)
    print(strategy.information_limitations)
    print()

    if strategy.contradictions_detected:
        print("-" * 48)
        print("CONTRADICTIONS / DATA CONSISTENCY ISSUES")
        print("-" * 48)
        print(strategy.contradictions_detected)
        print()
    else:
        print("-" * 48)
        print("CONTRADICTIONS / DATA CONSISTENCY ISSUES")
        print("-" * 48)
        print("None detected.")
        print()

    print("=" * 48)
    print(f"FINAL: {strategy.recommendation} | Confidence: {strategy.confidence}")
    print("=" * 48)
