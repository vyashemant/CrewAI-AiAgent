# AI Investment Research Team

An AI investment research project built with **CrewAI**, **Google Gemini**, **yfinance**, **SEC EDGAR XBRL Company Facts API**, **Marketaux**, and **FastAPI**.

The current system implements a complete multi-agent investment research pipeline with five specialized roles:

- Financial Analyst
- Market & News Analyst
- Valuation Analyst
- Risk Analyst
- Investment Strategist

> **Current status: Phase 4.6 complete.**

---

## Project Goal

The long-term goal is to build an AI Investment Research Team that can analyze public companies through specialized research roles and produce a comprehensive investment research report.

The project is now a multi-agent system. The current implementation spans the complete research pipeline from data retrieval to the final structured investment report.

## Multi-Agent Workflow

```text
User
  |
  v
Research Pipeline
  |
  +--> Market Data Retrieval (Yahoo Finance)
  |
  +--> SEC Financial Data Retrieval (EDGAR)
  |
  +--> Python Financial Metrics Engine
  |
  +--> Canonical / Validated Research Context
  |
  +--> Financial Analyst
  |
  +--> Market & News Analyst
  |
  +--> Valuation Analyst
  |
  +--> Risk Analyst
  |
  +--> Investment Strategist
  |
  v
Structured Investment Research Report
```

Specialist agents are strictly instructed **not** to independently invent numerical financial facts when validated Python/SEC context is available.

---

## Architectural Principle: Deterministic Financial Computation

**LLMs are NOT responsible for deterministic financial calculations.**

Python retrieves, validates, normalizes, and calculates financial metrics before the relevant context is provided to the LLM agents. 

This includes:
- revenue, gross profit, operating income, net income
- assets, liabilities, stockholders' equity, cash, debt
- operating cash flow, capital expenditure, free cash flow
- margins and growth metrics
- CAGR (Compound Annual Growth Rate)
- debt/equity-related metrics
- other deterministic financial calculations already present in the code

**Why this architecture is important:**
- **Reproducibility & Numerical Consistency:** Ensures the math is always correct.
- **Reduced Hallucination Risk:** LLMs don't invent facts or calculate incorrect ratios.
- **Separation of Concerns:** Separates computation from interpretation.
- **Easier Testing & Debugging:** Deterministic data pipelines can be reliably tested.
- **Stronger Evidence Traceability:** All facts can be traced to their SEC or market source.

---

## SEC Data Pipeline

The SEC Financial Data Tool retrieves official SEC EDGAR XBRL Company Facts data. It currently provides:
- Current financial data
- Raw financial evidence
- Normalized financial data
- Reporting metadata
- Historical financial data

### Historical Financial Extraction
Historical observations include metadata such as fiscal year, value, unit, form, filing date, period start, and period end. The historical series extracted are:
- revenue, gross profit, operating income, net income
- assets, liabilities, stockholders' equity, cash
- total debt, operating cash flow, capital expenditure

Extraction behavior:
- Focuses on annual 10-K data.
- Grouped by fiscal year.
- Duplicate fiscal years are resolved by taking the latest filing.
- Sorted chronologically.
- Limited to the latest five fiscal years.

---

## Financial Metrics Engine

Financial metrics are calculated by Python rather than by the LLM. 

The **CAGR** calculation uses actual elapsed fiscal years (`last_fy - first_fy`). It does NOT assume that the number of observations minus one represents the elapsed time. This makes the calculation robust when there are gaps in fiscal years. Invalid CAGR cases (such as non-positive starting values) safely return `None` rather than `NaN` or Infinity. 

Trend labels and margin trends are also produced deterministically where implemented.

---

## Structured Report

The final report is generated as a structured Pydantic model (`InvestmentResearchReport`), which natively supports JSON serialization. It contains:
- Identity: company, ticker, research date
- Market snapshot
- Financial summary and metrics
- Historical analysis (includes `historical_financials` containing the financial series, and `trend_summary`)
- Specialist reports (plain text)
- Investment strategy
- Data sources and Evidence registry

---

## API & Backend

The project includes a FastAPI backend (`api/main.py`).
- **Endpoints:** `/health` for health checks and `/api/v1/research` for executing the research pipeline.
- **Request Validation:** Uses Pydantic to validate parameters like `company` and `ticker`.
- **Response:** Returns the structured `InvestmentResearchReport` as a JSON response.

---

## Engineering Highlights

- **Multi-agent architecture:** 5 specialized agents working together seamlessly using CrewAI.
- **Deterministic financial computation:** Hard math is done in Python, preventing LLM hallucinations.
- **SEC EDGAR integration:** Real-world parsing of complex XBRL company facts.
- **Structured Pydantic outputs:** Ensures reliable JSON schema for API consumption.
- **Historical financial extraction:** Robust parsing of past 5 years of fiscal data with fiscal-year deduplication.
- **CAGR edge-case handling:** Calculates exact years and safely handles negative inputs.
- **FastAPI backend:** Serves the AI workflow via a modern REST API.
- **Separation of Concerns:** Retrieval, computation, and reasoning are entirely distinct phases.

---

## Project Structure

```text
CrewAI/
|-- agents/                     # CrewAI agent definitions and prompts
|   |-- investment_research_report.py
|   |-- investment_strategist.py
|   |-- market_news_analyst.py
|   |-- risk_analyst.py
|   `-- valuation_analyst.py
|-- api/                        # FastAPI backend
|   |-- __init__.py
|   `-- main.py
|-- tools/                      # External data retrieval and metric calculation
|   |-- financial_data_tool.py
|   |-- financial_metrics.py
|   |-- market_data_tool.py
|   |-- news_data_tool.py
|   `-- sec_financial_tool.py
|-- utils/                      # Helper utilities
|-- db/                         # Persistence layer
|-- data/                       # Local data storage
|-- .env.example                # Example environment variables
|-- app.py                      # End-to-end CLI runner
|-- requirements.txt            # Python dependencies
`-- test_*.py                   # Unit and integration tests
```

---

## Running The Project

### Command Line
Run the existing end-to-end pipeline:
```bash
python app.py
```

### API
Start the FastAPI application:
```bash
uvicorn api.main:app --reload
```

---

## Testing

The project uses a comprehensive test suite covering different layers of the application.

**1. Deterministic / Local Tests (No external API calls):**
- `test_serialization.py`: Validates Pydantic serialization of the final report.
- `test_consistency.py`: Validates consistency logic.
- `test_investment_research_report.py`: Tests structured report assembly with mock data, including recent regressions for `stockholders_equity` historical tracking.
- `test_api.py`: FastAPI endpoint testing.
- `test_evidence_registry.py`: Validates evidence storage and traceability.

*(Note: `test_historical_metrics.py` currently encounters a `ModuleNotFoundError: No module named 'pytest'` when executed directly via python, so it should be run via the `pytest` command instead.)*

**2. External Services / API Tests:**
- `test_sec_tool.py`: Tests the live SEC EDGAR data extraction.
- Agent tests (`test_valuation_agent.py`, `test_risk_analyst.py`, etc.).

**3. End-to-End Application:**
- `python app.py`: Executes the complete multi-agent pipeline and prints the report.

---

## Roadmap

### COMPLETED
- CrewAI setup and Google Gemini integration
- Financial, Market & News, Valuation, and Risk Analysts
- Investment Strategist and structured report generation
- SEC EDGAR data retrieval (normalized + raw evidence)
- Historical financial extraction (latest 5 fiscal years, deduplicated)
- Python-calculated financial metrics and robust CAGR edge-case handling
- FastAPI foundation and structured JSON responses
- Evidence registry and data validation

### NEXT
- API response and service-layer refinement
- Frontend architecture and Investment research dashboard
- Report visualization and Loading/progress UX

### FUTURE / OPTIONAL
- Evaluation framework
- CI/CD pipeline
- Performance benchmarking

---

## Example Output

*(This is a shortened conceptual example, not a complete live report.)*

```json
{
  "company": "Apple Inc.",
  "ticker": "AAPL",
  "financial_summary": {
    "revenue": 416161000000.0,
    "gross_profit": 195201000000.0
  },
  "financial_metrics": {
    "gross_margin": 46.91,
    "operating_margin": 31.97
  },
  "historical_analysis": {
      "historical_financials": {
          "stockholders_equity": [
              {"fy": 2023, "value": 62146000000.0, "unit": "USD"},
              {"fy": 2024, "value": 56950000000.0, "unit": "USD"}
          ]
      },
      "trend_summary": {
          "revenue_trend": "Moderate Growth"
      }
  },
  "investment_strategy": {
      "recommendation": "HOLD",
      "confidence": "HIGH"
  }
}
```

---

## Important Disclaimer

This project is an AI research and educational system, not a financial advisor.

AI-generated analysis can contain errors, incomplete information, outdated information, or incorrect interpretations. Investment decisions should not be based solely on the output of this system. The system retrieves current market data and official SEC financial data, but users should independently verify important financial information before making decisions.
