from crewai import Agent, Task


def create_risk_analyst(llm):
    """
    Create the Risk Research Analyst.

    The Risk Analyst evaluates financial, business, market,
    valuation, and news-related risks using the validated
    research context prepared by the Python orchestration layer.
    """

    risk_analyst = Agent(
        role="Risk Research Analyst",

        goal=(
            "Identify, evaluate, and clearly explain the major risks "
            "associated with a publicly traded company using only the "
            "validated research context provided by the research pipeline. "
            "Assess financial, business, market, valuation, news/event, "
            "and data-quality risks without inventing unavailable facts."
        ),

        backstory=(
            "You are an experienced equity risk research analyst with "
            "7 years of experience evaluating risks in publicly traded "
            "companies. You specialize in identifying financial risks, "
            "business risks, market risks, valuation risks, and risks "
            "arising from recent company developments. "
            "You are conservative and evidence-driven. "
            "You distinguish verified facts from analyst interpretation "
            "and potential scenarios. "
            "You never invent missing financial information, "
            "and you explicitly identify data limitations when the "
            "available research context is incomplete."
        ),

        llm=llm,
        verbose=False
    )

    return risk_analyst


def create_risk_analysis_task(agent):
    """
    Create the Risk Analyst task.

    The task receives the same validated research context used by
    the other specialist analysts.
    """

    risk_analysis_task = Task(
        description=(
            "Perform a comprehensive risk analysis of {company} "
            "using the validated research context provided below.\n\n"

            "RESEARCH CONTEXT:\n"
            "{research_context}\n\n"

            "Analyze the company across the following risk categories:\n\n"

            "1. FINANCIAL RISK\n"
            "Evaluate relevant financial risks using the provided "
            "financial statements and calculated metrics. Consider "
            "debt levels, debt-to-equity, net cash or net debt, "
            "profitability, cash flow, balance-sheet strength, and "
            "financial leverage when the required data is available.\n\n"

            "2. BUSINESS RISK\n"
            "Identify important business risks visible from the "
            "available research context. Consider business model "
            "dependencies, growth pressures, profitability pressures, "
            "competitive pressures, product or service dependencies, "
            "and other company-specific risks supported by the data.\n\n"

            "3. MARKET RISK\n"
            "Evaluate market-related risks using available market data. "
            "Consider beta, recent price behavior, trading range, "
            "market conditions, and other relevant market information "
            "when available.\n\n"

            "4. VALUATION RISK\n"
            "Evaluate whether the current valuation creates downside "
            "risk. Consider Trailing P/E, Forward P/E, Price-to-Sales, "
            "Price-to-Book, EV/EBITDA, FCF valuation, and other "
            "valuation information available in the research context.\n\n"

            "5. NEWS AND EVENT RISK\n"
            "Analyze recent company news and identify developments "
            "that could create positive or negative risk. Consider "
            "product announcements, regulatory developments, "
            "competitive developments, operational issues, "
            "macroeconomic factors, and other relevant events when "
            "supported by the available news data.\n\n"

            "6. DATA-QUALITY RISK\n"
            "Identify important information that is unavailable, "
            "incomplete, stale, or insufficient for a reliable "
            "conclusion. Do not fill missing information with "
            "assumptions.\n\n"

            "For every important risk:\n"
            "- Clearly identify the risk.\n"
            "- Explain the evidence supporting it.\n"
            "- Explain why it matters.\n"
            "- Distinguish verified facts from interpretation.\n"
            "- Do not invent facts, financial values, forecasts, "
            "peer comparisons, or historical data.\n\n"

            "Do not provide a BUY, SELL, or HOLD recommendation. "
            "Do not provide portfolio allocation advice. "
            "Your responsibility is risk analysis only."
        ),

        expected_output=(
            "A structured risk research report containing:\n"
            "1. Risk analysis overview\n"
            "2. Financial risks\n"
            "3. Business risks\n"
            "4. Market risks\n"
            "5. Valuation risks\n"
            "6. News and event risks\n"
            "7. Data-quality risks and limitations\n"
            "8. Key risk factors\n"
            "9. Overall risk assessment\n"
            "10. Important evidence and metrics used"
        ),

        agent=agent
    )

    return risk_analysis_task