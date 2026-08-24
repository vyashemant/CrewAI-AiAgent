import os

from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process


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
# 3. FINANCIAL RESEARCH ANALYST
# ============================================================

financial_analyst = Agent(
    role="Financial Research Analyst",

    goal=(
        "Analyze a company's financial performance, business fundamentals, "
        "growth trends, profitability, and overall financial health using "
        "reliable and relevant financial information."
    ),

    backstory=(
        "You are an experienced financial research analyst with 7 years of "
        "experience analyzing publicly traded companies. You specialize in "
        "understanding financial statements, revenue and profit trends, "
        "business fundamentals, growth metrics, and financial risks. "
        "You provide objective, evidence-based analysis and clearly "
        "distinguish facts from assumptions."
    ),

    llm=llm,
    verbose=True,
    allow_delegation=False
)


# ============================================================
# 4. FINANCIAL ANALYSIS TASK
# ============================================================

financial_analysis_task = Task(
    description=(
        "Perform a fundamental financial analysis of {company}.\n\n"

        "Analyze the company's:\n"
        "- Revenue growth\n"
        "- Profitability\n"
        "- Earnings performance\n"
        "- Cash flow\n"
        "- Debt levels\n"
        "- Business growth\n"
        "- Overall financial health\n\n"

        "Identify the most important positive and negative financial "
        "factors.\n\n"

        "Do not make unsupported claims. Clearly distinguish between "
        "known facts, assumptions, and areas where information is "
        "unavailable."
    ),

    expected_output=(
        "A structured financial analysis containing:\n\n"

        "1. Company Overview\n"
        "2. Revenue and Growth Analysis\n"
        "3. Profitability Analysis\n"
        "4. Earnings Performance\n"
        "5. Cash Flow Analysis\n"
        "6. Debt and Financial Stability\n"
        "7. Key Financial Strengths\n"
        "8. Key Financial Weaknesses\n"
        "9. Important Financial Metrics\n"
        "10. Overall Financial Health Assessment\n\n"

        "The analysis should be factual, balanced, and easy to understand."
    ),

    agent=financial_analyst
)


# ============================================================
# 5. CREW CONFIGURATION
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
# 6. RUN THE CREW
# ============================================================

if __name__ == "__main__":

    company = "Apple Inc."

    print("\n" + "=" * 70)
    print("AI INVESTMENT RESEARCH TEAM")
    print("=" * 70)

    print(f"\nAnalyzing: {company}")
    print("Research type: Fundamental Financial Analysis")
    print("\nStarting analysis...\n")

    result = team.kickoff(
        inputs={
            "company": company
        }
    )

    # ========================================================
    # 7. DISPLAY RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL FINANCIAL ANALYSIS")
    print("=" * 70)

    print(result)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)