from crewai import LLM,Agent,Task,Crew,Process
from crewai.tools import BaseTool
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI API KEY not found.")

llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.6
)

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
    verbose=False
)

financial_analysis_task = Task(
    description=(
        "Perform a fundamental financial analysis of {company}. "
        "Analyze its revenue growth, profitability, earnings performance, "
        "cash flow, debt levels, business growth, and overall financial health. "
        "Identify the most important positive and negative financial factors. "
        "Do not make unsupported claims. Clearly state when information "
        "is unavailable."
    ),

    expected_output=(
        "A structured financial analysis containing:\n"
        "1. Company overview\n"
        "2. Revenue and growth analysis\n"
        "3. Profitability analysis\n"
        "4. Cash flow analysis\n"
        "5. Debt and financial stability\n"
        "6. Key financial strengths\n"
        "7. Key financial weaknesses\n"
        "8. Overall financial health assessment\n"
        "9. Important financial metrics used in the analysis"
    ),

    agent=financial_analyst
)

team = Crew(
    agents=[financial_analyst],
    tasks=[financial_analysis_task],
    process=Process.sequential,
    verbose=True
)

result = team.kickoff(
    inputs={
        "company": "Apple Inc."
    }
)