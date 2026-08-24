import os

from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process

from tools.financial_data_tool import FinancialDataTool
from tools.market_data_tool import MarketDataTool

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


# ============================================================
# 4. FINANCIAL RESEARCH ANALYST
# ============================================================

financial_analyst = Agent(
    role="Financial Research Analyst",

    goal=(
        "Analyze a company's financial performance, business fundamentals, "
        "growth trends, profitability, valuation, and overall financial "
        "health using verified data retrieved through available tools."
    ),

    backstory=(
        "You are an experienced financial research analyst with 7 years "
        "of experience analyzing publicly traded companies.\n\n"

        "You specialize in financial statements, market data, "
        "profitability, valuation, growth metrics, and financial risk.\n\n"

        "IMPORTANT RULES:\n"
        "1. Use tools before making claims about financial numbers.\n"
        "2. Never invent missing financial data.\n"
        "3. Never infer cash, debt, or net cash from incomplete data.\n"
        "4. Never create dates that were not retrieved from a tool.\n"
        "5. Clearly distinguish retrieved facts from interpretation.\n"
        "6. If data is unavailable, explicitly report it as unavailable.\n"
        "7. Do not provide personalized investment advice."
    ),

    tools=[
        financial_data_tool,
        market_data_tool
    ],

    llm=llm,

    verbose=True,

    allow_delegation=False
)


# ============================================================
# 5. FINANCIAL ANALYSIS TASK
# ============================================================

financial_analysis_task = Task(
    description=(
        "Perform a fundamental financial analysis of {company}.\n\n"

        "First identify the correct stock ticker.\n\n"

        "Then retrieve the required information using the available "
        "financial and market data tools.\n\n"

        "Use the tools to analyze:\n"
        "- Current market price\n"
        "- Market capitalization\n"
        "- Historical price performance\n"
        "- Revenue\n"
        "- Revenue growth\n"
        "- Profitability\n"
        "- Earnings\n"
        "- Cash flow\n"
        "- Debt\n"
        "- Valuation\n"
        "- Overall financial health\n\n"

        "DATA INTEGRITY RULES:\n\n"

        "1. Never invent financial numbers.\n"

        "2. Never use your pretrained knowledge as a substitute "
        "for retrieved financial data when the tool can provide it.\n"

        "3. If a financial statement is empty or unavailable, "
        "report the metric as unavailable.\n"

        "4. Never calculate net cash, debt, profitability, margins, "
        "or other balance-sheet metrics from incomplete data.\n"

        "5. Do not infer balance-sheet values from Enterprise Value "
        "and Market Capitalization alone.\n"

        "6. Do not invent the report date. Use the actual retrieved "
        "data period/date when available.\n"

        "7. Every important numerical claim must be identifiable "
        "as retrieved data or a calculation based on retrieved data.\n"

        "8. Clearly separate:\n"
        "   - Retrieved Facts\n"
        "   - Calculated Metrics\n"
        "   - Analyst Interpretation\n"
        "   - Missing Information\n\n"

        "9. Do not provide personalized investment advice."
    ),

    expected_output=(
        "A professional financial research report containing:\n\n"

        "1. Company Overview\n"
        "2. Data Sources\n"
        "3. Data Retrieval Date\n"
        "4. Current Market Snapshot\n"
        "5. Historical Market Performance\n"
        "6. Revenue and Growth Analysis\n"
        "7. Profitability Analysis\n"
        "8. Earnings Analysis\n"
        "9. Cash Flow Analysis\n"
        "10. Debt and Financial Stability\n"
        "11. Valuation Analysis\n"
        "12. Key Financial Strengths\n"
        "13. Key Financial Weaknesses\n"
        "14. Important Financial Metrics\n"
        "15. Retrieved Facts\n"
        "16. Calculated Metrics\n"
        "17. Analyst Interpretation\n"
        "18. Missing or Unavailable Information\n"
        "19. Overall Financial Health Assessment\n\n"

        "The report must clearly distinguish retrieved data from "
        "analysis and calculations."
    ),

    agent=financial_analyst
)


# ============================================================
# 6. CREW CONFIGURATION
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


# ============================================================
# 7. RUN THE CREW
# ============================================================

if __name__ == "__main__":

    company = "Apple Inc."

    print("\n" + "=" * 70)
    print("AI INVESTMENT RESEARCH TEAM")
    print("=" * 70)

    print(f"\nAnalyzing: {company}")
    print("Research type: Fundamental Financial Analysis")
    print("Data source: Yahoo Finance via yfinance")
    print("\nStarting analysis...\n")

    result = team.kickoff(
        inputs={
            "company": company
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