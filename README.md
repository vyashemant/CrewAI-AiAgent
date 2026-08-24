# AI Investment Research Team

A multi-agent investment research system built with **CrewAI** and **Google Gemini**.

The project is designed to analyze publicly traded companies by dividing investment research into specialized roles such as financial analysis, market research, valuation, risk analysis, and final investment synthesis.

> **Current status:** Foundation / Phase 1. The project currently implements the Financial Research Analyst agent. Additional agents and real-time data tools are planned.

---

## 🎯 Project Goal

The goal is to build a portfolio-quality GenAI application that demonstrates how multiple specialized AI agents can collaborate to produce a structured investment research report.

Instead of asking one LLM to perform every task, the system will eventually divide the research workflow across specialized agents:

```text
                         User
                           │
                           ▼
                  Investment Research
                         Manager
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Financial         Market &          Valuation
      Analyst           News Analyst       Analyst
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                      Risk Analyst
                           │
                           ▼
                 Investment Strategist
                           │
                           ▼
                 Final Research Report
```

---

## 🚧 Current Implementation

The current version contains one working agent:

### Financial Research Analyst

The agent is responsible for:

- Company overview
- Revenue and growth analysis
- Profitability analysis
- Earnings performance
- Cash-flow analysis
- Debt and financial stability
- Financial strengths
- Financial weaknesses
- Important financial metrics
- Overall financial health assessment

The current implementation uses CrewAI's sequential process and accepts a company name as an input.

Example:

```python
result = team.kickoff(
    inputs={
        "company": "Apple Inc."
    }
)
```

---

## 🧠 Planned Multi-Agent Architecture

The complete system is planned around five specialized agents.

### 1. Financial Research Analyst

Analyzes:

- Revenue
- Earnings
- Profitability
- Cash flow
- Debt
- Financial health
- Financial trends

### 2. Market & News Research Analyst

Analyzes:

- Recent company news
- Industry trends
- Competitors
- Regulatory developments
- Market sentiment
- Positive and negative catalysts

### 3. Equity Valuation Analyst

Analyzes:

- P/E
- P/S
- EV/EBITDA
- Price-to-Free-Cash-Flow
- Historical valuation
- Peer valuation
- Growth versus valuation

### 4. Investment Risk Analyst

Analyzes:

- Financial risks
- Operational risks
- Competitive risks
- Regulatory risks
- Technology risks
- Macroeconomic risks
- Downside scenarios

### 5. Senior Investment Research Strategist

Synthesizes the outputs from the other agents and produces:

- Executive summary
- Bull case
- Bear case
- Financial assessment
- Valuation assessment
- Risk assessment
- Key uncertainties
- Important metrics to monitor
- Overall research conclusion

---

## 🛠️ Technology Stack

### AI / Agent Framework

- Python
- CrewAI
- Google Gemini

### Configuration

- python-dotenv
- Environment variables

### Planned Tools

The next development phase will introduce external tools for:

- Financial data
- Stock prices
- Company financial statements
- News
- Market information
- SEC/company filings

This is important because an investment research application should use retrieved data rather than relying only on the LLM's pretrained knowledge.

---

## 📁 Current Project Structure

```text
ai-investment-research/
│
├── .env
├── .gitignore
├── requirements.txt
└── app.py
```

As the project grows, the structure can evolve into:

```text
ai-investment-research/
│
├── agents/
│   ├── financial_analyst.py
│   ├── market_researcher.py
│   ├── valuation_analyst.py
│   ├── risk_analyst.py
│   └── investment_strategist.py
│
├── tasks/
│   ├── financial_analysis.py
│   ├── market_research.py
│   ├── valuation_analysis.py
│   ├── risk_analysis.py
│   └── investment_strategy.py
│
├── tools/
│   ├── financial_data.py
│   ├── market_data.py
│   └── news_search.py
│
├── config/
│   └── settings.py
│
├── main.py
├── requirements.txt
├── .env
└── .gitignore
```

---

## ⚙️ Installation

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd ai-investment-research
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit your `.env` file to GitHub.

Your `.gitignore` should contain:

```gitignore
.env
__pycache__/
*.pyc
.venv/
venv/
```

---

## ▶️ Running the Project

Run:

```bash
python main.py
```

The current implementation analyzes:

```text
Apple Inc.
```

You can change the company in `main.py`:

```python
company = "Apple Inc."
```

For example:

```python
company = "NVIDIA"
```

or:

```python
company = "Microsoft"
```

---

## 📊 Example Output

The Financial Research Analyst is expected to produce a structured report similar to:

```text
Financial Analysis

1. Company Overview
2. Revenue and Growth Analysis
3. Profitability Analysis
4. Earnings Performance
5. Cash Flow Analysis
6. Debt and Financial Stability
7. Key Financial Strengths
8. Key Financial Weaknesses
9. Important Financial Metrics
10. Overall Financial Health Assessment
```

---

## 🔄 Development Roadmap

### Phase 1 — Foundation
- [x] CrewAI setup
- [x] Gemini LLM integration
- [x] Financial Research Analyst
- [x] Financial analysis task
- [x] Sequential Crew execution

### Phase 2 — Real Financial Data
- [ ] Financial-data tool
- [ ] Stock-price tool
- [ ] Financial statement retrieval
- [ ] Source references
- [ ] Data validation

### Phase 3 — Multi-Agent System
- [ ] Market & News Analyst
- [ ] Valuation Analyst
- [ ] Risk Analyst
- [ ] Investment Strategist
- [ ] Agent-to-agent workflow

### Phase 4 — Advanced Research
- [ ] News search
- [ ] SEC/company filing retrieval
- [ ] RAG pipeline
- [ ] Historical financial analysis
- [ ] Peer comparison
- [ ] Evidence-based citations

### Phase 5 — Production Application
- [ ] FastAPI backend
- [ ] Web interface
- [ ] Structured JSON responses
- [ ] Research report export
- [ ] Logging
- [ ] Error handling
- [ ] Evaluation framework
- [ ] Deployment

---

## ⚠️ Important Disclaimer

This project is an **AI research and educational system**, not a financial advisor.

AI-generated analysis can contain errors, incomplete information, outdated information, or incorrect interpretations. Investment decisions should not be based solely on the output of this system.

The production version should retrieve current financial data and provide sources for material claims before being used for research.

---

## 💡 Why This Project?

This project is designed to demonstrate practical GenAI engineering skills including:

- Multi-agent architecture
- Agent specialization
- LLM orchestration
- Task decomposition
- Tool calling
- Retrieval-augmented generation
- Structured outputs
- Financial data processing
- Backend API integration
- AI system evaluation

The long-term objective is to build an investment research pipeline where specialized agents independently investigate different aspects of a company and a senior agent synthesizes the evidence into a single research report.

---

## 📌 Project Status

**Current:** 🟡 In Development

**Completed:** Financial Research Analyst

**Next milestone:** Connect the Financial Research Analyst to reliable financial-data tools and validate generated metrics against source data.
