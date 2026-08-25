import os

from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process

from tools.financial_data_tool import FinancialDataTool
from tools.market_data_tool import MarketDataTool
from tools.sec_financial_tool import SECFinancialDataTool
from tools.financial_metrics import FinancialMetricsEngine

# ============================================================
# 1. ENVIRONMENT CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please add GEMINI_API_KEY to your .env file."
    )


# ============================================================
# 2. LLM CONFIGURATION
# ============================================================

llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.3
)


# ============================================================
# 3. INITIALIZE TOOLS
# ============================================================

financial_data_tool = FinancialDataTool()
market_data_tool = MarketDataTool()
sec_financial_tool = SECFinancialDataTool()
metrics_engine = FinancialMetricsEngine()


# ============================================================
# 4. RESEARCH CONTEXT PREPARATION
# ============================================================

def format_currency(value):
    """Format large dollar values for the LLM research context."""

    if value is None:
        return "Unavailable"

    try:
        absolute_value = abs(value)

        if absolute_value >= 1_000_000_000:
            formatted = f"${absolute_value / 1_000_000_000:.3f}B"
        elif absolute_value >= 1_000_000:
            formatted = f"${absolute_value / 1_000_000:.3f}M"
        else:
            formatted = f"${absolute_value:,.0f}"

        if value < 0:
            return f"-{formatted}"

        return formatted

    except TypeError:
        return "Unavailable"


def format_metric(value, suffix=""):
    """Format calculated metrics while preserving unavailable values."""

    if value is None:
        return "Unavailable"

    return f"{value:.2f}{suffix}"


def build_financial_research_context(
    ticker,
    market_result,
    sec_result,
    calculated_metrics
):
    """
    Build the validated context that the analyst should interpret.
    Metrics in this context are calculated by Python, not by the LLM.
    """

    if not isinstance(sec_result, dict):
        return (
            "Validated financial research context is unavailable.\n"
            f"SEC retrieval result: {sec_result}\n"
            f"Market retrieval result: {market_result}"
        )

    financial_data = sec_result.get(
        "financial_data",
        {}
    )

    normalized = financial_data.get(
        "normalized",
        {}
    )

    metadata = sec_result.get(
        "reporting_metadata",
        {}
    )

    calculated_lines = []
    unavailable_lines = []

    metric_labels = {
        "revenue_growth": ("Revenue Growth", "%"),
        "net_income_growth": ("Net Income Growth", "%"),
        "gross_margin": ("Gross Margin", "%"),
        "operating_margin": ("Operating Margin", "%"),
        "net_profit_margin": ("Net Profit Margin", "%"),
        "free_cash_flow": ("Free Cash Flow", "$"),
        "fcf_margin": ("FCF Margin", "%"),
        "debt_to_equity": ("Debt-to-Equity", "%"),
        "net_cash": ("Net Cash", "$"),
        "return_on_equity": ("ROE", "%"),
        "return_on_assets": ("ROA", "%"),
        "asset_turnover": ("Asset Turnover", "x"),
        "equity_multiplier": ("Equity Multiplier", "x")
    }

    for key, value in calculated_metrics.items():
        label, metric_type = metric_labels.get(
            key,
            (key, "")
        )

        if value is None:
            unavailable_lines.append(
                f"- {label}: Unavailable"
            )
            continue

        if metric_type == "$":
            formatted = format_currency(value)
        elif metric_type == "%":
            formatted = format_metric(value, "%")
        elif metric_type == "x":
            formatted = format_metric(value, "x")
        else:
            formatted = format_metric(value)

        calculated_lines.append(
            f"- {label}: {formatted}"
        )

    return (
        "PRE-RETRIEVED VERIFIED FINANCIAL RESEARCH CONTEXT\n\n"
        "Use this context as the authoritative retrieved and calculated "
        "financial data for the report. Do not recalculate these metrics "
        "and do not invent unavailable values.\n\n"

        "Data Sources\n"
        "- Market data: Yahoo Finance via yfinance\n"
        "- Financial statements: SEC EDGAR XBRL Company Facts API\n\n"

        "Market Data Period\n"
        "- Current market information from the Market Data Tool at runtime.\n"
        f"- Market tool output: {market_result}\n\n"

        "Latest Financial Reporting Period\n"
        f"- Ticker: {ticker}\n"
        f"- Company: {sec_result.get('company')}\n"
        f"- CIK: {metadata.get('cik')}\n"
        f"- Form: {metadata.get('form')}\n"
        f"- Fiscal Year: {metadata.get('fiscal_year')}\n"
        f"- Fiscal Period: {metadata.get('fiscal_period')}\n"
        f"- Filed: {metadata.get('filed')}\n"
        f"- Period Start: {metadata.get('period_start')}\n"
        f"- Period End: {metadata.get('period_end')}\n\n"

        "Retrieved Financial Facts\n"
        f"- Revenue: {format_currency(normalized.get('revenue'))}\n"
        f"- Gross Profit: {format_currency(normalized.get('gross_profit'))}\n"
        f"- Operating Income: {format_currency(normalized.get('operating_income'))}\n"
        f"- Net Income: {format_currency(normalized.get('net_income'))}\n"
        f"- Assets: {format_currency(normalized.get('assets'))}\n"
        f"- Liabilities: {format_currency(normalized.get('liabilities'))}\n"
        f"- Stockholders' Equity: {format_currency(normalized.get('stockholders_equity'))}\n"
        f"- Cash and Equivalents: {format_currency(normalized.get('cash'))}\n"
        f"- Total Debt: {format_currency(normalized.get('total_debt'))}\n"
        f"- Operating Cash Flow: {format_currency(normalized.get('operating_cash_flow'))}\n"
        f"- Capital Expenditure: {format_currency(normalized.get('capital_expenditure'))}\n\n"

        "Calculated Metrics\n"
        + "\n".join(calculated_lines)
        + "\n\n"

        "Unavailable Metrics\n"
        + "\n".join(unavailable_lines)
        + "\n\n"

        "Raw SEC Evidence\n"
        f"{financial_data.get('raw')}"
    )


# ============================================================
# 5. FINANCIAL RESEARCH ANALYST
# ============================================================

financial_analyst = Agent(
    role="Financial Research Analyst",

    goal=(
        "Analyze a company's financial performance, business fundamentals, "
        "growth trends, profitability, valuation, and financial health "
        "using verified market data and official SEC financial information."
    ),

    backstory=(
        "You are an experienced financial research analyst with 7 years "
        "of experience analyzing publicly traded companies.\n\n"

        "You specialize in financial statements, market data, "
        "profitability, valuation, growth metrics, and financial risk.\n\n"

        "Your analysis must be evidence-driven. All external financial "
        "data has already been retrieved by the Python orchestration "
        "layer before the task begins.\n\n"

        "The PRE-RETRIEVED VERIFIED FINANCIAL RESEARCH CONTEXT is "
        "authoritative. Do not call external tools to retrieve duplicate "
        "financial data. Do not replace the provided values with "
        "pretrained knowledge.\n\n"

        "DATA INTEGRITY RULES:\n"

        "1. Use the pre-retrieved verified research context for current "
        "market information.\n"

        "2. Use the pre-retrieved verified research context for SEC "
        "financial statement information.\n"

        "3. Never invent financial numbers.\n"

        "4. Never use pretrained knowledge as a substitute for retrieved "
        "data provided in the context.\n"

        "5. Clearly identify the source and reporting period of financial "
        "data.\n"

        "6. Do not mix current market data with historical financial "
        "statement data without clearly identifying their different dates.\n"

        "7. Never infer unavailable balance-sheet values.\n"

        "8. If information is unavailable, explicitly state that it "
        "is unavailable.\n"

        "9. The PRE-RETRIEVED VERIFIED FINANCIAL RESEARCH CONTEXT is "
        "the authoritative source for numerical analysis.\n"

        "10. Never independently calculate a metric that the Python "
        "Financial Metrics Engine already calculated.\n"

        "11. Clearly distinguish retrieved facts, calculated metrics, "
        "and analyst interpretation.\n"

        "12. Do not provide personalized investment advice."
    ),

    llm=llm,

    verbose=True,

    allow_delegation=False
)


# ============================================================
# 6. FINANCIAL ANALYSIS TASK
# ============================================================

financial_analysis_task = Task(

    description=(

        "Perform a fundamental financial analysis of {company}.\n\n"

        "{research_context}\n\n"

        "STEP 1 - USE AUTHORITATIVE CONTEXT\n"
        "Use the pre-retrieved verified research context as the "
        "authoritative source for numerical analysis.\n\n"

        "STEP 2 - INTERPRET CURRENT MARKET DATA\n"
        "Interpret the current market data contained in the context, "
        "including stock price, market capitalization, 52-week range, "
        "volume, beta, and valuation metrics when available.\n\n"

        "STEP 3 - INTERPRET OFFICIAL FINANCIAL DATA\n"
        "Interpret the SEC financial facts contained in the context. "
        "Do not retrieve duplicate data.\n\n"

        "Interpret and analyze:\n"
        "- Revenue\n"
        "- Gross profit\n"
        "- Operating income\n"
        "- Net income\n"
        "- Assets\n"
        "- Liabilities\n"
        "- Stockholders' equity\n"
        "- Cash and cash equivalents\n"
        "- Debt\n"
        "- Operating cash flow\n"
        "- Capital expenditure\n\n"

        "STEP 4 - USE VALIDATED CALCULATED METRICS\n"
        "Use the calculated metrics provided in the validated research "
        "context. Do not independently recalculate metrics that Python "
        "has already calculated, including:\n"
        "- Revenue growth\n"
        "- Gross margin\n"
        "- Operating margin\n"
        "- Net profit margin\n"
        "- Free cash flow\n"
        "- Debt-to-equity ratio\n"
        "- Net cash/debt where the required data is available\n\n"

        "STEP 5 - ANALYZE\n"
        "Evaluate the company's financial strength, growth, profitability, "
        "cash generation, balance-sheet position, and valuation.\n\n"

        "DATA INTEGRITY RULES:\n"

        "1. Never invent numerical values.\n"

        "2. Fundamental financial data must come from the pre-retrieved "
        "SEC EDGAR context when available.\n"

        "3. Current market data must come from the pre-retrieved Yahoo "
        "Finance context.\n"

        "4. Always identify the reporting period for financial statements.\n"

        "5. Do not describe FY2025 financial data as current 2026 financial data.\n"

        "6. Do not infer missing debt, cash, equity, or other balance-sheet "
        "values from Enterprise Value or Market Capitalization.\n"

        "7. Only report a metric as calculated when the validated research "
        "context provides a calculated value.\n"

        "8. If required inputs are unavailable, report the metric as "
        "'Unavailable'.\n"

        "9. Clearly separate retrieved facts from calculations and "
        "interpretations.\n"

        "10. Do not provide personalized investment advice."
    ),

    expected_output=(

        "A professional financial research report containing:\n\n"

        "1. Company Overview\n"
        "2. Data Sources\n"
        "3. Market Data Retrieval Date\n"
        "4. Latest Financial Reporting Period\n"
        "5. Current Market Snapshot\n"
        "6. Revenue and Growth Analysis\n"
        "7. Profitability Analysis\n"
        "8. Earnings Analysis\n"
        "9. Cash Flow Analysis\n"
        "10. Balance Sheet Analysis\n"
        "11. Debt and Financial Stability\n"
        "12. Valuation Analysis\n"
        "13. Calculated Financial Metrics\n"
        "14. Key Financial Strengths\n"
        "15. Key Financial Weaknesses\n"
        "16. Retrieved Facts\n"
        "17. Calculated Metrics\n"
        "18. Analyst Interpretation\n"
        "19. Missing or Unavailable Information\n"
        "20. Overall Financial Health Assessment\n\n"

        "Every major numerical claim must identify whether it is "
        "retrieved or calculated. Calculated metrics must come from "
        "the Python Financial Metrics Engine context when provided."
    ),

    agent=financial_analyst
)


# ============================================================
# 7. CREW CONFIGURATION
# ============================================================

team = Crew(
    agents=[
        financial_analyst
    ],

    tasks=[
        financial_analysis_task
    ],

    process=Process.sequential,

    verbose=True
)

def prepare_financial_research(ticker):
    """
    Retrieve financial data and calculate validated metrics
    before sending the information to the LLM.
    """

    market_result = market_data_tool.run(
        ticker=ticker
    )

    sec_result = sec_financial_tool.get_financial_data(
        ticker=ticker
    )

    normalized = {}

    if isinstance(sec_result, dict):
        normalized = sec_result.get(
            "financial_data",
            {}
        ).get(
            "normalized",
            {}
        )

    calculated_metrics = metrics_engine.calculate_from_sec_data(
        normalized
    )

    return build_financial_research_context(
        ticker=ticker,
        market_result=market_result,
        sec_result=sec_result,
        calculated_metrics=calculated_metrics
    )


# ============================================================
# 8. RUN THE CREW
# ============================================================

if __name__ == "__main__":

    company = "Apple Inc."
    ticker = "AAPL"

    print("\n" + "=" * 70)
    print("AI INVESTMENT RESEARCH TEAM")
    print("=" * 70)

    print(f"\nAnalyzing: {company}")
    print(f"Ticker: {ticker}")
    print("Research type: Fundamental Financial Analysis")
    print("Data sources: Yahoo Finance via yfinance and SEC EDGAR")
    print("\nStarting analysis...\n")

    research_context = prepare_financial_research(
        ticker=ticker
    )

    result = team.kickoff(
        inputs={
            "company": company,
            "research_context": research_context
        }
    )

    # ========================================================
    # 8. DISPLAY RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL FINANCIAL ANALYSIS")
    print("=" * 70)

    print(result)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
