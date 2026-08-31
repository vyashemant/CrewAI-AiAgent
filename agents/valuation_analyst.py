from crewai import LLM, Agent, Task


def create_valuation_analyst(llm: LLM) -> Agent:
    """
    Create the Valuation Research Analyst.

    This agent interprets pre-retrieved market valuation metrics
    and Python-calculated financial metrics.

    It does not retrieve external data and does not make a
    final BUY/SELL/HOLD recommendation.
    """

    return Agent(
        role="Valuation Research Analyst",

        goal=(
            "Evaluate whether a company's current market valuation "
            "appears reasonable, expensive, attractive, or difficult "
            "to assess relative to its financial performance, "
            "profitability, cash generation, and available valuation "
            "metrics."
        ),

        backstory=(
            "You are an experienced equity valuation analyst with "
            "strong expertise in interpreting market multiples and "
            "company fundamentals. You specialize in P/E, Forward "
            "P/E, Price-to-Sales, Price-to-Book, EV/EBITDA, and "
            "price-to-free-cash-flow relationships. You compare "
            "valuation with the company's actual financial performance "
            "and clearly distinguish verified data from interpretation. "
            "You never invent missing financial information and you "
            "do not make final investment recommendations."
        ),

        llm=llm,

        verbose=True
    )


def create_valuation_task(agent: Agent) -> Task:
    """
    Create the Valuation Analyst task.
    """

    return Task(
        description=(
            "Perform a valuation analysis of {company} using only "
            "the pre-retrieved and validated research context provided "
            "to you.\n\n"

            "RESEARCH CONTEXT:\n"
            "{research_context}\n\n"

            "The Python orchestration layer has already retrieved "
            "the relevant market and financial data and calculated "
            "deterministic financial metrics. Treat those values as "
            "authoritative.\n\n"

            "Analyze the following areas when the required data is "
            "available:\n\n"

            "1. Earnings valuation\n"
            "   - Trailing P/E\n"
            "   - Forward P/E\n\n"

            "2. Revenue valuation\n"
            "   - Price-to-Sales\n\n"

            "3. Book-value valuation\n"
            "   - Price-to-Book\n\n"

            "4. Enterprise valuation\n"
            "   - Enterprise Value\n"
            "   - EV/EBITDA\n\n"

            "5. Cash-flow valuation\n"
            "   - Market capitalization relative to Free Cash Flow "
            "when the required values are available\n\n"

            "6. Valuation versus fundamentals\n"
            "   - Revenue growth when available\n"
            "   - Profitability\n"
            "   - Free cash flow\n"
            "   - Margins\n"
            "   - Return metrics\n\n"

            "7. Valuation strengths\n\n"

            "8. Valuation risks\n\n"

            "9. Overall valuation assessment\n\n"

            "Clearly distinguish between:\n"
            "- Retrieved valuation metrics\n"
            "- Python-calculated metrics\n"
            "- Analyst interpretation\n"
            "- Potential implications\n\n"

            "Do not invent peer-company multiples, historical "
            "valuation ranges, growth rates, earnings forecasts, "
            "or other information that is not present in the "
            "research context.\n\n"

            "Do not independently recalculate metrics that are "
            "already supplied by the Financial Metrics Engine.\n\n"

            "If a required metric is unavailable, explicitly state "
            "that it is unavailable and explain why if the context "
            "provides a reason.\n\n"

            "Do not provide a BUY, SELL, or HOLD recommendation. "
            "The final investment decision will be handled later "
            "by the Investment Strategist."
        

            "CRITICAL EVIDENCE RULES:\n"
            "1. You must use the provided JSON CanonicalResearchSnapshot as your sole source of numerical truth.\n"
            "2. If a metric is missing, null, or marked 'Unavailable' in the snapshot, you MUST state it is unavailable. Do NOT calculate it yourself.\n"
            "3. Do NOT invent or estimate any missing data.\n"
            "4. Distinguish between 'retrieved' facts (from external sources) and 'calculated' facts (from the Python Metrics Engine) as indicated in the JSON.\n"
        ),

        expected_output=(
            "A structured Valuation Research Report containing:\n\n"

            "1. Valuation Overview\n"
            "2. Earnings Valuation\n"
            "3. Revenue Valuation\n"
            "4. Book-Value Valuation\n"
            "5. Enterprise Valuation\n"
            "6. Cash-Flow Valuation\n"
            "7. Valuation vs Financial Fundamentals\n"
            "8. Valuation Strengths\n"
            "9. Valuation Risks\n"
            "10. Overall Valuation Assessment\n"
            "11. Data Limitations\n\n"

            "The report must distinguish verified numerical "
            "information from analyst interpretation and must not "
            "contain a final BUY/SELL/HOLD recommendation."
        ),

        agent=agent
    )