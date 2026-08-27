# AI Investment Research Team

An AI investment research project built with **CrewAI**, **Google Gemini**, **yfinance**, **SEC EDGAR XBRL Company Facts API**, and **Marketaux**.

The current system implements a complete multi-agent investment research pipeline with five specialized roles:

- Financial Research Analyst
- Market & News Research Analyst
- Valuation Research Analyst
- Risk Research Analyst
- Investment Strategist

Python retrieves, validates, normalizes, and calculates financial data before the CrewAI tasks begin. The specialized Gemini agents then interpret the validated research context from their respective perspectives. The Investment Strategist synthesises all four specialist reports into a final structured investment recommendation.

> **Current status: Phase 3 complete.**

---

## Project Goal

The long-term goal is to build an AI Investment Research Team that can analyze public companies through specialized research roles and produce a comprehensive investment research report.

The planned long-term architecture is:

```text
User
 |
 v
Research Manager / Orchestrator
 |
 v
+----------------------+----------------------+
|                      |                      |
v                      v                      v
Financial Analyst   Market / News Analyst   Valuation Analyst
                                               |
                                               v
                                           Risk Analyst
                                               |
                                               v
                                      Investment Strategist
                                               |
                                               v
                                  Final Investment Research Report
```

The project is now a multi-agent system. The current implementation spans the complete research pipeline from data retrieval to final structured investment report.

---

## Current Architecture

```text
Yahoo Finance
    |
    v
Market Data Tool

SEC EDGAR
    |
    v
SEC Financial Data Tool
    |
    v
Normalized Financial Data
    |
    v
Financial Metrics Engine
    |
    v
Validated Research Context
    |
    +--------------------------+---------------------------+
    |                          |                           |
    v                          v                           v
Financial Analyst    Market & News Analyst    Valuation Analyst
    |                          |                           |
    +------------------+-------+---------------------------+
                       |
                       v
                  Risk Analyst
                       |
                       v
             Investment Strategist
                       |
                       v
      InvestmentResearchReport (structured final output)
```

The design principle is:

```text
RETRIEVAL -> VALIDATION -> CALCULATION -> REASONING
```

- Yahoo Finance is used for current market data.
- SEC EDGAR is the primary source for fundamental financial statements.
- Python validates and normalizes financial data.
- Python calculates deterministic financial metrics.
- CrewAI/Gemini interprets the validated data.
- Missing data is reported as unavailable rather than invented.

---

## Current Implementation

### Financial Research Analyst

The Financial Research Analyst produces a structured financial research report covering:

- Company overview
- Data sources
- Market data
- Financial reporting period
- Revenue analysis
- Profitability analysis
- Earnings analysis
- Cash-flow analysis
- Balance-sheet analysis
- Debt and financial stability
- Valuation analysis
- Calculated financial metrics
- Key financial strengths
- Key financial weaknesses
- Missing or unavailable information
- Overall financial health assessment

All external financial data is retrieved by the Python orchestration layer before CrewAI kickoff. The analyst receives the pre-retrieved verified research context and is responsible for interpretation, explanation, and financial reasoning.

### Market & News Research Analyst

The Market & News Research Analyst covers:

- Recent company developments
- Key news events
- Market activity (price, 52-week range, beta)
- Positive and negative catalysts
- Industry and external factors
- Potential stock impact
- Key events to monitor
- Information limitations

### Valuation Research Analyst

The Valuation Research Analyst covers:

- Market capitalization and enterprise value
- Valuation multiples (P/E, forward P/E, P/S, P/B, EV/EBITDA)
- Profitability and efficiency metrics from SEC data
- Valuation strengths and risks
- Overall valuation assessment
- Data limitations

### Risk Research Analyst

The Risk Research Analyst covers:

- Financial risks (leverage, debt, cash flow)
- Business risks (concentration, ecosystem, growth)
- Market risks (valuation, volatility, scale)
- Valuation risks (multiple compression)
- News and event risks
- Data-quality risks and limitations
- Key risk factors summary
- Overall risk assessment

### Investment Strategist

The Investment Strategist synthesises all four specialist reports and produces a structured `InvestmentStrategy` Pydantic object covering:

- Investment thesis
- Fundamental, market/news, valuation, and risk assessments
- Bull, base, and bear cases
- Key catalysts and key risks
- Thesis change triggers
- Company quality and valuation view
- Final recommendation (BUY / HOLD / SELL)
- Confidence level (LOW / MEDIUM / HIGH)
- Evidence summary and information limitations

### Final Investment Research Report

The `InvestmentResearchReport` Pydantic model assembles all pipeline outputs into one canonical, JSON-serialisable object. It is constructed deterministically in Python — no additional LLM or API calls are made.

Sections:

- Identity (company, ticker, research date)
- Market snapshot (from Yahoo Finance)
- Financial summary (from SEC EDGAR)
- Financial metrics (from the Python Metrics Engine)
- News (from Marketaux)
- Specialist reports (all four plain-text outputs)
- Investment strategy (composed `InvestmentStrategy` object)
- Data sources (provenance record)

---

## Data Sources

### Yahoo Finance

Yahoo Finance data is retrieved through `yfinance` and is used for current market information such as:

- Current stock price
- Previous close
- Day high and low
- 52-week high and low
- Volume and average volume
- Market capitalization
- Beta
- Dividend yield
- Recent historical prices

### SEC EDGAR

SEC EDGAR data is retrieved through the SEC XBRL Company Facts API and is used for official financial statement information such as:

- Revenue
- Gross profit
- Operating income
- Net income
- Assets
- Liabilities
- Stockholders' equity
- Cash and cash equivalents
- Current debt
- Non-current debt
- Total debt
- Operating cash flow
- Capital expenditure
- Reporting metadata including CIK, form, fiscal year, filing date, and reporting period

The SEC tool preserves raw SEC evidence and also creates normalized financial data for deterministic metric calculation.

---

## Tools

### `tools/market_data_tool.py`

Retrieves current and recent historical market data from Yahoo Finance through `yfinance`.

### `tools/sec_financial_tool.py`

Retrieves official SEC EDGAR company facts, extracts the latest annual financial statement values, preserves raw evidence, creates normalized financial data, validates debt components, and preserves reporting metadata.

### `tools/financial_metrics.py`

Contains the deterministic Financial Metrics Engine. It calculates financial metrics only when all required inputs are available. If required data is missing, the metric returns `None` and is reported as unavailable.

Calculated metrics include:

- Revenue growth
- Net income growth
- Gross margin
- Operating margin
- Net profit margin
- Free cash flow
- FCF margin
- Debt-to-equity
- Net cash
- Return on equity
- Return on assets
- Asset turnover
- Equity multiplier

### `tools/financial_data_tool.py`

Retrieves additional Yahoo Finance fundamental data, including financial statements and valuation metrics. Valuation multiples (P/E, forward P/E, P/S, P/B, EV/EBITDA) sourced here are passed to the Valuation and Risk analysts.

### `tools/news_data_tool.py`

Retrieves recent news articles for the ticker from the Marketaux API. Articles include title, description, snippet, URL, publication date, source, and per-entity sentiment scores.

---

## Project Structure

```text
CrewAI/
|-- .vscode/
|-- agents/
|   |-- __init__.py
|   |-- investment_research_report.py
|   |-- investment_strategist.py
|   |-- market_news_analyst.py
|   |-- risk_analyst.py
|   `-- valuation_analyst.py
|-- tools/
|   |-- __init__.py
|   |-- financial_data_tool.py
|   |-- financial_metrics.py
|   |-- market_data_tool.py
|   |-- news_data_tool.py
|   `-- sec_financial_tool.py
|-- .env
|-- .env.example
|-- .gitignore
|-- app.py
|-- README.md
|-- requirements.txt
|-- test_financial_metrics.py
|-- test_financial_tool.py
|-- test_investment_research_report.py
|-- test_investment_strategist.py
|-- test_market_news_agent.py
|-- test_market_tool.py
|-- test_news_tool.py
|-- test_risk_analyst.py
|-- test_sec_tool.py
`-- test_valuation_agent.py
```

---

## Technology Stack

- Python
- CrewAI
- Google Gemini (`gemini-2.0-flash`)
- python-dotenv
- yfinance
- pandas
- requests
- pydantic
- SEC EDGAR XBRL Company Facts API
- Marketaux News API

---

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SEC_USER_AGENT=YourAppName your-email@example.com
```

`GEMINI_API_KEY` is required. `SEC_USER_AGENT` is recommended for SEC API requests.

Never commit your `.env` file.

---

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running The Project

Run:

```bash
python app.py
```

The current application analyzes Apple Inc. using ticker `AAPL`. You can change the `company` and `ticker` values in `app.py`.

---

## Tests

Run:

```bash
python test_financial_metrics.py
python test_sec_tool.py
python test_market_tool.py
python test_financial_tool.py
python test_news_tool.py
python test_market_news_agent.py
python test_valuation_agent.py
python test_risk_analyst.py
python test_investment_strategist.py
python test_investment_research_report.py
```

The metrics test includes both complete-data and incomplete-data cases. Missing inputs must remain unavailable. For example, if total debt is unavailable, debt-to-equity and net cash must return `None`.

The agent tests (`test_market_news_agent.py`, `test_valuation_agent.py`, `test_risk_analyst.py`, `test_investment_strategist.py`) make live Gemini API calls and take 1–5 minutes each.

The `test_investment_research_report.py` test uses only mock data — no live API or Gemini calls.

---

## Roadmap

### Phase 1 - Foundation

- [x] CrewAI setup
- [x] Gemini LLM
- [x] Financial Research Analyst
- [x] Financial analysis task
- [x] Sequential Crew

### Phase 2 - Real Financial Data

- [x] Yahoo Finance market data
- [x] SEC EDGAR financial data
- [x] SEC reporting metadata
- [x] SEC raw financial evidence
- [x] SEC normalized financial data
- [x] Current/non-current debt validation
- [x] Total debt calculation
- [x] Signed CapEx normalization
- [x] Financial Metrics Engine
- [x] Missing-data validation
- [x] Pre-retrieved research context
- [x] Python-calculated financial metrics
- [x] Financial Analyst integration
- [x] End-to-end application

### Phase 3 - Multi-Agent Investment Research

- [x] Financial Analyst
- [x] Market & News Analyst
- [x] Valuation Analyst
- [x] Risk Analyst
- [x] Investment Strategist
- [x] Multi-agent workflow
- [x] Specialist report synthesis
- [x] Final structured investment research report

### Phase 4 - API & Frontend

- [ ] FastAPI backend
- [ ] REST endpoints for research pipeline
- [ ] Structured API responses (JSON)
- [ ] Frontend or report export
- [ ] Authentication
- [ ] Deployment

### Phase 5 - Production

- [ ] Evaluation framework
- [ ] CI/CD pipeline
- [ ] Performance benchmarking

---

## Important Disclaimer

This project is an AI research and educational system, not a financial advisor.

AI-generated analysis can contain errors, incomplete information, outdated information, or incorrect interpretations. Investment decisions should not be based solely on the output of this system.

The system retrieves current market data and official SEC financial data, but users should independently verify important financial information before making decisions.
