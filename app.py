import os
import sys
import time
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process

from tools.financial_data_tool import FinancialDataTool
from tools.market_data_tool import MarketDataTool
from tools.sec_financial_tool import SECFinancialDataTool
from tools.news_data_tool import NewsDataTool
from tools.financial_metrics import FinancialMetricsEngine
from tools.historical_metrics import HistoricalTrendEngine

from utils.consistency import build_canonical_snapshot, validate_consistency
from utils.evidence import build_evidence_registry
import json

from agents.market_news_analyst import (
    create_market_news_analyst,
    create_market_news_task
)

from agents.valuation_analyst import (
    create_valuation_analyst,
    create_valuation_task
)

from agents.risk_analyst import (
    create_risk_analyst,
    create_risk_analysis_task
)

from agents.investment_strategist import (
    create_investment_strategist,
    create_investment_strategy_task,
)

from agents.investment_research_report import (
    build_investment_research_report,
    HistoricalAnalysis,
    HistoricalFinancials,
    TrendSummary
)

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

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
news_data_tool = NewsDataTool()
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
    calculated_metrics,
    trends_result=None
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
        f"{financial_data.get('raw')}\n\n"

        "Historical Trends & Labels\n"
        f"{json.dumps(trends_result.get('labels', {}), indent=2) if trends_result else 'Unavailable'}\n\n"
        
        "Historical CAGR Metrics\n"
        f"{json.dumps(trends_result.get('metrics', {}), indent=2) if trends_result else 'Unavailable'}"
    )


def build_valuation_metrics_section(financial_data_result):
    """
    Format the FinancialDataTool valuation_metrics dict into a
    labelled context block for the research context.

    financial_data_result is the raw dict returned by
    financial_data_tool._run(ticker).
    """

    if not isinstance(financial_data_result, dict):
        return (
            "\n\nMarket Valuation Metrics — Yahoo Finance via yfinance\n"
            "- Valuation metrics unavailable."
        )

    vm = financial_data_result.get("valuation_metrics", {})

    def fmt_multiple(value, decimals=2):
        if value is None:
            return "Unavailable"
        return f"{value:.{decimals}f}x"

    market_cap = vm.get("Market Cap")
    trailing_pe = vm.get("Trailing P/E")
    forward_pe = vm.get("Forward P/E")
    price_to_sales = vm.get("Price To Sales")
    price_to_book = vm.get("Price To Book")
    enterprise_value = vm.get("Enterprise Value")
    ev_to_ebitda = vm.get("Enterprise To EBITDA")

    return (
        "\n\nMarket Valuation Metrics — Yahoo Finance via yfinance\n"
        "These are retrieved market valuation metrics. "
        "The Valuation Analyst must prefer these over any "
        "independently derived calculations from SEC data.\n"
        f"- Market Capitalization: {format_currency(market_cap)}\n"
        f"- Trailing P/E: {fmt_multiple(trailing_pe)}\n"
        f"- Forward P/E: {fmt_multiple(forward_pe)}\n"
        f"- Price-to-Sales: {fmt_multiple(price_to_sales)}\n"
        f"- Price-to-Book: {fmt_multiple(price_to_book)}\n"
        f"- Enterprise Value: {format_currency(enterprise_value)}\n"
        f"- Enterprise Value / EBITDA: {fmt_multiple(ev_to_ebitda)}"
    )


def build_combined_research_context(
    ticker,
    market_result,
    sec_result,
    calculated_metrics,
    financial_data_result,
    news_result,
    trends_result=None
):
    """
    Build the combined research context that all three specialist
    agents receive. Extends the financial context with the
    FinancialDataTool valuation metrics and news data.
    """

    financial_context = build_financial_research_context(
        ticker,
        market_result,
        sec_result,
        calculated_metrics,
        trends_result=trends_result
    )

    valuation_section = build_valuation_metrics_section(
        financial_data_result
    )

    news_section = (
        "\n\nRecent Company News\n"
        f"{news_result}"
    )

    return financial_context + valuation_section + news_section


def build_compact_financial_snapshot(ticker, sec_result, calculated_metrics):
    """
    Build a compact SEC and metrics snapshot for specialists that
    need verified figures but not the full raw SEC evidence payload.
    """

    if not isinstance(sec_result, dict):
        return (
            "Verified financial snapshot is unavailable.\n"
            f"SEC retrieval result: {sec_result}"
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
            formatted = "Unavailable"
        elif metric_type == "$":
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
        "VERIFIED FINANCIAL SNAPSHOT\n\n"
        "Use these retrieved SEC facts and Python-calculated metrics as "
        "authoritative. Do not invent unavailable values.\n\n"

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
    )


def build_specialist_research_contexts(ticker, prepared):
    """
    Build scoped specialist contexts from one prepared research snapshot.
    No external data is retrieved here.
    """

    financial_context = build_financial_research_context(
        ticker=ticker,
        market_result=prepared["market_data"],
        sec_result=prepared["sec_data"],
        calculated_metrics=prepared["metrics"],
        trends_result=prepared.get("trends", {})
    ) + build_valuation_metrics_section(
        prepared["financial_data"]
    )

    compact_financial_snapshot = build_compact_financial_snapshot(
        ticker=ticker,
        sec_result=prepared["sec_data"],
        calculated_metrics=prepared["metrics"]
    )

    market_context = (
        "PRE-RETRIEVED VERIFIED MARKET AND NEWS CONTEXT\n\n"
        "Use only this single runtime snapshot. Do not retrieve "
        "or invent additional news, market data, or financial values.\n\n"
        "Market Data - Yahoo Finance via yfinance\n"
        f"{prepared['market_data']}\n\n"
        "Relevant Financial Context\n"
        f"{compact_financial_snapshot}\n\n"
        "Recent Company News - Marketaux\n"
        f"{prepared['news_data']}"
    )

    valuation_context = (
        "PRE-RETRIEVED VERIFIED VALUATION CONTEXT\n\n"
        "Use only this single runtime snapshot. Do not retrieve "
        "or invent peer multiples, historical ranges, or forecasts.\n\n"
        f"{compact_financial_snapshot}"
        f"{build_valuation_metrics_section(prepared['financial_data'])}"
    )

    risk_context = (
        "PRE-RETRIEVED VERIFIED RISK CONTEXT\n\n"
        "Use only this single runtime snapshot. Do not invent missing "
        "risk factors, financial values, forecasts, or news events.\n\n"
        f"{compact_financial_snapshot}\n\n"
        "Market Data - Yahoo Finance via yfinance\n"
        f"{prepared['market_data']}"
        f"{build_valuation_metrics_section(prepared['financial_data'])}\n\n"
        "Recent Company News - Marketaux\n"
        f"{prepared['news_data']}"
    )

    return {
        "Financial Analyst": financial_context,
        "Market & News Analyst": market_context,
        "Valuation Analyst": valuation_context,
        "Risk Analyst": risk_context
    }


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
# 7. MARKET & NEWS ANALYST
# ============================================================

market_news_analyst = create_market_news_analyst(llm)

market_news_task = create_market_news_task(market_news_analyst)


# ============================================================
# 8. VALUATION ANALYST
# ============================================================

valuation_analyst = create_valuation_analyst(llm)

valuation_task = create_valuation_task(valuation_analyst)


# ============================================================
# 9. RISK ANALYST
# ============================================================

risk_analyst = create_risk_analyst(llm)

risk_analysis_task = create_risk_analysis_task(risk_analyst)


# ============================================================
# 10. INVESTMENT STRATEGIST
# ============================================================

investment_strategist = create_investment_strategist(llm)

investment_strategy_task = create_investment_strategy_task(investment_strategist)

# ============================================================
# 11. SPECIALIST CREW CONFIGURATION
# ============================================================

specialist_team = Crew(
    agents=[
        financial_analyst,
        market_news_analyst,
        valuation_analyst,
        risk_analyst
    ],

    tasks=[
        financial_analysis_task,
        market_news_task,
        valuation_task,
        risk_analysis_task
    ],

    process=Process.sequential,

    verbose=True
)


# ============================================================
# 12. INVESTMENT STRATEGY CREW CONFIGURATION
# ============================================================

strategy_team = Crew(
    agents=[
        investment_strategist
    ],

    tasks=[
        investment_strategy_task
    ],

    process=Process.sequential,

    verbose=True
)

def prepare_financial_research(ticker):
    """
    Retrieve financial data and calculate validated metrics
    before sending the information to the LLM.
    """

    market_data = market_data_tool.run(
        ticker=ticker
    )

    sec_data = sec_financial_tool.get_financial_data(
        ticker=ticker
    )

    # Retrieve valuation metrics from Yahoo Finance via FinancialDataTool.
    # Call _run() directly to obtain the raw dict before stringification.
    financial_data = financial_data_tool._run(
        ticker=ticker
    )

    news_data = news_data_tool.run(
        ticker=ticker,
        limit=3
    )

    normalized = sec_data.get(
        "financial_data",
        {}
    ).get(
        "normalized",
        {}
    )

    metrics = metrics_engine.calculate_from_sec_data(
        normalized
    )

    historical_data = sec_data.get(
        "financial_data",
        {}
    ).get(
        "historical",
        {}
    )
    
    trend_engine = HistoricalTrendEngine(historical_data)
    trends = trend_engine.get_trends()

    return {
        "market_data": market_data,
        "sec_data": sec_data,
        "financial_data": financial_data,
        "news_data": news_data,
        "metrics": metrics,
        "trends": trends
    }


def build_research_context_from_prepared(ticker, prepared):
    """
    Convert the prepared research dict into the combined context
    string that all three specialist agents receive.
    """

    return build_combined_research_context(
        ticker=ticker,
        market_result=prepared["market_data"],
        sec_result=prepared["sec_data"],
        calculated_metrics=prepared["metrics"],
        financial_data_result=prepared["financial_data"],
        news_result=prepared["news_data"]
    )


def run_single_specialist(name, agent, task, base_inputs, research_context):
    """
    Run one specialist analyst in an isolated one-task crew.
    Each specialist receives the same prepared research snapshot.
    """

    start_time = time.perf_counter()

    crew = Crew(
        agents=[
            agent
        ],

        tasks=[
            task
        ],

        process=Process.sequential,

        verbose=True
    )

    result = crew.kickoff(
        inputs={
            **base_inputs,
            "research_context": research_context
        }
    )

    elapsed = time.perf_counter() - start_time

    if getattr(result, "tasks_output", None):
        report = result.tasks_output[0]
    else:
        report = result

    return {
        "name": name,
        "report": str(report),
        "elapsed": elapsed
    }


def run_specialists_in_parallel(base_inputs, research_contexts):
    """
    Run independent specialist agents concurrently after data retrieval.
    The Investment Strategist still runs only after all reports complete.
    """

    specialists = [
        (
            "Financial Analyst",
            financial_analyst,
            financial_analysis_task
        ),
        (
            "Market & News Analyst",
            market_news_analyst,
            market_news_task
        ),
        (
            "Valuation Analyst",
            valuation_analyst,
            valuation_task
        ),
        (
            "Risk Analyst",
            risk_analyst,
            risk_analysis_task
        )
    ]

    results = {}

    with ThreadPoolExecutor(max_workers=len(specialists)) as executor:
        future_to_name = {
            executor.submit(
                run_single_specialist,
                name,
                agent,
                task,
                base_inputs,
                research_contexts[name]
            ): name
            for name, agent, task in specialists
        }

        for future in as_completed(future_to_name):
            result = future.result()
            results[result["name"]] = result

    return results


def print_pipeline_timing(timings):
    """Print compact timing information for the major pipeline stages."""

    print("\n")
    print("RESEARCH PIPELINE TIMING")
    print("-" * 80)
    print(f"Data retrieval:              {timings['data_retrieval']:.2f} sec")
    print(f"Context preparation:         {timings['context_preparation']:.2f} sec")
    print(
        f"Parallel specialist stage:   "
        f"{timings['parallel_specialist_stage']:.2f} sec"
    )

    for name in [
        "Financial Analyst",
        "Market & News Analyst",
        "Valuation Analyst",
        "Risk Analyst"
    ]:
        print(f"{name + ':':28} {timings[name]:.2f} sec")

    print(f"Investment Strategist:       {timings['investment_strategist']:.2f} sec")
    print(f"Total:                       {timings['total']:.2f} sec")
    print("-" * 80)


# ============================================================
# 13. RUN RESEARCH PIPELINE
# ============================================================

def run_investment_research(company: str, ticker: str):
    """
    Execute the full investment research pipeline for a given company and ticker.
    Returns the canonical InvestmentResearchReport and a timings dictionary.
    """
    total_start = time.perf_counter()
    timings = {}

    print("\n")
    print("=" * 80)
    print("STEP 1 - PREPARING RESEARCH DATA")
    print("=" * 80)

    stage_start = time.perf_counter()
    prepared = prepare_financial_research(ticker)
    timings["data_retrieval"] = time.perf_counter() - stage_start

    stage_start = time.perf_counter()
    research_contexts = build_specialist_research_contexts(
        ticker=ticker,
        prepared=prepared
    )
    timings["context_preparation"] = time.perf_counter() - stage_start

    print("\n")
    print("=" * 80)
    print("STEP 2 - RUNNING SPECIALIST ANALYSTS")
    print("=" * 80)

    specialist_inputs = {
        "company": company,
        "ticker": ticker
    }

    stage_start = time.perf_counter()
    specialist_results = run_specialists_in_parallel(
        specialist_inputs,
        research_contexts
    )
    timings["parallel_specialist_stage"] = time.perf_counter() - stage_start

    print("\n")
    print("=" * 80)
    print("STEP 3 - COLLECTING SPECIALIST REPORTS")
    print("=" * 80)

    financial_report = specialist_results["Financial Analyst"]["report"]
    market_news_report = specialist_results["Market & News Analyst"]["report"]
    valuation_report = specialist_results["Valuation Analyst"]["report"]
    risk_report = specialist_results["Risk Analyst"]["report"]

    for name, result in specialist_results.items():
        timings[name] = result["elapsed"]

    print("\n")
    print("=" * 80)
    print("STEP 4 - VALIDATING RESEARCH CONSISTENCY")
    print("=" * 80)

    canonical_evidence = build_canonical_snapshot(ticker, prepared)
    consistency_report = validate_consistency(
        specialist_results=specialist_results,
        canonical_evidence=canonical_evidence
    )

    print("\nConsistency Validation:")
    print(json.dumps(consistency_report, indent=2))

    print("\n")
    print("=" * 80)
    print("STEP 5 - RUNNING INVESTMENT STRATEGIST")
    print("=" * 80)

    stage_start = time.perf_counter()
    strategy_result = strategy_team.kickoff(
        inputs={
            "company": company,
            "ticker": ticker,
            "financial_analyst_report": financial_report,
            "market_news_analyst_report": market_news_report,
            "valuation_analyst_report": valuation_report,
            "risk_analyst_report": risk_report,
            "canonical_evidence": canonical_evidence,
            "consistency_report": json.dumps(
                consistency_report,
                indent=2
            )
        }
    )
    timings["investment_strategist"] = time.perf_counter() - stage_start

    # --------------------------------------------------------
    # STEP 6: EXTRACT STRUCTURED STRATEGY
    # --------------------------------------------------------

    strategy = strategy_result.pydantic

    # --------------------------------------------------------
    # STEP 6: BUILD FINAL INVESTMENT RESEARCH REPORT
    # --------------------------------------------------------

    research_date = datetime.date.today().isoformat()

    final_report = None

    if strategy is not None:
        try:
            evidence_registry = build_evidence_registry(canonical_evidence)
            
            trends = prepared.get("trends", {})
            labels = trends.get("labels", {})
            metrics_cagr = trends.get("metrics", {})
            
            trend_summary = TrendSummary(
                revenue_trend=labels.get("Revenue Trend", "Unavailable"),
                net_income_trend=labels.get("Net Income Trend", "Unavailable"),
                debt_trend=labels.get("Debt Trend", "Unavailable"),
                gross_margin_trend=labels.get("Gross Margin Trend", "Unavailable"),
                operating_margin_trend=labels.get("Operating Margin Trend", "Unavailable"),
                net_margin_trend=labels.get("Net Margin Trend", "Unavailable"),
                revenue_cagr=metrics_cagr.get("revenue_cagr"),
                net_income_cagr=metrics_cagr.get("net_income_cagr")
            )
            
            historical_data = prepared.get("sec_data", {}).get("financial_data", {}).get("historical", {})
            hf_kwargs = {}
            for k, v in historical_data.items():
                if isinstance(v, list) and v:
                    hf_kwargs[k] = v
            historical_financials = HistoricalFinancials(**hf_kwargs) if hf_kwargs else None
            
            historical_analysis = HistoricalAnalysis(
                historical_financials=historical_financials,
                trend_summary=trend_summary
            )
            
            final_report = build_investment_research_report(
                company=company,
                ticker=ticker,
                research_date=research_date,
                prepared=prepared,
                specialist_results=specialist_results,
                strategy=strategy,
                evidence_registry=evidence_registry,
                historical_analysis=historical_analysis,
                trend_summary=trend_summary,
            )
        except Exception as report_build_error:
            print(f"\n[WARNING] Could not build InvestmentResearchReport: {report_build_error}")
            final_report = None

    timings["total"] = time.perf_counter() - total_start
    return final_report, strategy_result, timings


if __name__ == "__main__":

    company = "Apple Inc."
    ticker = "AAPL"

    print("\n")
    print("=" * 80)
    print("AI INVESTMENT RESEARCH TEAM")
    print("=" * 80)

    final_report, strategy_result, timings = run_investment_research(company, ticker)
    
    if final_report is not None:
        strategy = final_report.investment_strategy
    else:
        strategy = strategy_result.pydantic if strategy_result else None

    # --------------------------------------------------------
    # STEP 7: DISPLAY FINAL INVESTMENT STRATEGY (existing output)
    # --------------------------------------------------------\n    # STEP 7: DISPLAY FINAL INVESTMENT STRATEGY (existing output)
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("FINAL INVESTMENT STRATEGY")
    print("=" * 80)

    if strategy is None:

        print("\nStructured strategy was not returned.")
        print("\nRaw strategist output:")
        print(strategy_result.raw)

    else:

        print(f"\nCompany: {company}")
        print(f"Ticker: {ticker}")
        print(f"Recommendation: {strategy.recommendation}")
        print(f"Confidence: {strategy.confidence}")

        print("\n" + "-" * 80)
        print("INVESTMENT THESIS")
        print("-" * 80)
        print(strategy.investment_thesis)

        print("\n" + "-" * 80)
        print("COMPANY QUALITY")
        print("-" * 80)
        print(strategy.company_quality)

        print("\n" + "-" * 80)
        print("VALUATION VIEW")
        print("-" * 80)
        print(strategy.valuation_view)

        print("\n" + "-" * 80)
        print("FUNDAMENTAL ASSESSMENT")
        print("-" * 80)
        print(strategy.fundamental_assessment)

        print("\n" + "-" * 80)
        print("MARKET & NEWS ASSESSMENT")
        print("-" * 80)
        print(strategy.market_and_news_assessment)

        print("\n" + "-" * 80)
        print("VALUATION ASSESSMENT")
        print("-" * 80)
        print(strategy.valuation_assessment)

        print("\n" + "-" * 80)
        print("RISK ASSESSMENT")
        print("-" * 80)
        print(strategy.risk_assessment)

        print("\n" + "-" * 80)
        print("BULL CASE")
        print("-" * 80)
        print(strategy.bull_case)

        print("\n" + "-" * 80)
        print("BASE CASE")
        print("-" * 80)
        print(strategy.base_case)

        print("\n" + "-" * 80)
        print("BEAR CASE")
        print("-" * 80)
        print(strategy.bear_case)

        print("\n" + "-" * 80)
        print("KEY CATALYSTS")
        print("-" * 80)

        for index, catalyst in enumerate(
            strategy.key_catalysts,
            1
        ):
            print(f"{index}. {catalyst}")

        print("\n" + "-" * 80)
        print("KEY RISKS")
        print("-" * 80)

        for index, risk in enumerate(
            strategy.key_risks,
            1
        ):
            print(f"{index}. {risk}")

        print("\n" + "-" * 80)
        print("THESIS CHANGE TRIGGERS")
        print("-" * 80)

        for index, trigger in enumerate(
            strategy.thesis_change_triggers,
            1
        ):
            print(f"{index}. {trigger}")

        print("\n" + "-" * 80)
        print("EVIDENCE SUMMARY")
        print("-" * 80)
        print(strategy.evidence_summary)

        print("\n" + "-" * 80)
        print("INFORMATION LIMITATIONS")
        print("-" * 80)
        print(strategy.information_limitations)

        print("\n" + "-" * 80)
        print("CONTRADICTIONS / DATA CONSISTENCY ISSUES")
        print("-" * 80)

        if strategy.contradictions_detected:
            print(strategy.contradictions_detected)
        else:
            print("None detected.")

        print("\n")
        print("=" * 80)
        print(
            f"FINAL RECOMMENDATION: "
            f"{strategy.recommendation} | "
            f"CONFIDENCE: {strategy.confidence}"
        )
        print("=" * 80)

    print_pipeline_timing(timings)

    # --------------------------------------------------------
    # STEP 8: PRINT FINAL INVESTMENT RESEARCH REPORT SUMMARY
    # --------------------------------------------------------

    if final_report is not None:

        print("\n")
        print("=" * 60)
        print("FINAL INVESTMENT RESEARCH REPORT")
        print("=" * 60)

        print(f"\nCompany:          {final_report.company}")
        print(f"Ticker:           {final_report.ticker}")
        print(f"Research Date:    {final_report.research_date}")

        strat = final_report.investment_strategy

        print("\n" + "-" * 60)
        print("FINAL RECOMMENDATION")
        print("-" * 60)
        print(f"Recommendation:   {strat.recommendation}")
        print(f"Confidence:       {strat.confidence}")

        print("\n" + "-" * 60)
        print("INVESTMENT THESIS")
        print("-" * 60)
        print(strat.investment_thesis)

        print("\n" + "-" * 60)
        print("FINANCIAL SUMMARY")
        print("-" * 60)
        fs = final_report.financial_summary
        def _fmt(v):
            if v is None:
                return "Unavailable"
            if abs(v) >= 1_000_000_000:
                return f"${v / 1_000_000_000:.3f}B"
            if abs(v) >= 1_000_000:
                return f"${v / 1_000_000:.3f}M"
            return f"${v:,.0f}"
        print(f"  Revenue:              {_fmt(fs.revenue)}")
        print(f"  Gross Profit:         {_fmt(fs.gross_profit)}")
        print(f"  Operating Income:     {_fmt(fs.operating_income)}")
        print(f"  Net Income:           {_fmt(fs.net_income)}")
        print(f"  Operating Cash Flow:  {_fmt(fs.operating_cash_flow)}")
        print(f"  Free Cash Flow:       {_fmt(final_report.financial_metrics.free_cash_flow)}")

        print("\n" + "-" * 60)
        print("VALUATION")
        print("-" * 60)
        print(strat.valuation_assessment)

        print("\n" + "-" * 60)
        print("RISK")
        print("-" * 60)
        print(strat.risk_assessment)

        print("\n" + "-" * 60)
        print("BULL CASE")
        print("-" * 60)
        print(strat.bull_case)

        print("\n" + "-" * 60)
        print("BASE CASE")
        print("-" * 60)
        print(strat.base_case)

        print("\n" + "-" * 60)
        print("BEAR CASE")
        print("-" * 60)
        print(strat.bear_case)

        print("\n" + "-" * 60)
        print("DATA LIMITATIONS")
        print("-" * 60)
        print(strat.information_limitations)

        print("\n" + "-" * 60)
        print("DATA SOURCES")
        print("-" * 60)
        ds = final_report.data_sources
        print(f"  Market Data:          {ds.market_data}")
        print(f"  Financial Statements: {ds.financial_statements}")
        print(f"  News:                 {ds.news}")
        print(f"  Metrics:              {ds.metrics}")
        print(f"  Specialist Analysis:  {ds.specialist_analysis}")
        print(f"  Investment Strategy:  {ds.investment_strategy}")

        print("\n" + "=" * 60)
        print(
            f"FINAL: {strat.recommendation} | "
            f"CONFIDENCE: {strat.confidence} | "
            f"DATE: {final_report.research_date}"
        )
        print("=" * 60)

        # Verify serialisation
        try:
            import json
            _ = json.dumps(final_report.model_dump(), default=str)
            print("\n[OK] final_report.model_dump() and JSON serialisation successful.")
        except Exception as serial_err:
            print(f"\n[WARNING] JSON serialisation failed: {serial_err}")

    else:
        print("\n[WARNING] Final investment research report could not be assembled.")
