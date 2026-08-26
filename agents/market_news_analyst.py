from crewai import LLM, Agent, Task


def create_market_news_analyst(llm: LLM) -> Agent:
    """
    Create the Market & News Research Analyst.

    This agent is responsible for interpreting:
    - recent company news
    - market activity
    - catalysts
    - external developments
    - potential market/company impact

    It does not perform fundamental financial calculations.
    """

    return Agent(
        role="Market & News Research Analyst",

        goal=(
            "Analyze recent company news, market activity, business "
            "developments, catalysts, and external events that may "
            "affect the company or its stock. Provide objective, "
            "evidence-based interpretation using only the research "
            "data provided to you."
        ),

        backstory=(
            "You are an experienced market and news research analyst "
            "specializing in publicly traded companies. You analyze "
            "recent company announcements, product launches, "
            "partnerships, regulatory developments, industry events, "
            "market movements, and other developments that may affect "
            "a company's business or stock. You distinguish verified "
            "facts from interpretation and never invent missing "
            "information."
        ),

        llm=llm,

        verbose=True
    )


def create_market_news_task(
    agent: Agent
) -> Task:
    """
    Create the Market & News analysis task.
    """

    return Task(

        description=(
            "Analyze the recent market and news information provided "
            "for {company}.\n\n"

            "RESEARCH CONTEXT:\n"
            "{research_context}\n\n"

            "Use only the provided research context as the source "
            "of factual claims. Do not invent news, dates, events, "
            "market movements, or company developments.\n\n"

            "Analyze:\n"
            "1. Recent company developments\n"
            "2. Most important recent news\n"
            "3. Recent market activity\n"
            "4. Positive catalysts\n"
            "5. Negative catalysts\n"
            "6. Industry and external factors\n"
            "7. Potential impact on the company\n"
            "8. Potential impact on the stock\n"
            "9. Important events or developments to monitor\n"
            "10. Information limitations\n\n"

            "Distinguish clearly between:\n"
            "- Verified news/events\n"
            "- Market observations\n"
            "- Analyst interpretation\n"
            "- Potential future implications\n\n"

            "Do not perform detailed fundamental financial analysis. "
            "Do not calculate financial ratios. Those responsibilities "
            "belong to the Financial Research Analyst and Financial "
            "Metrics Engine."
        ),

        expected_output=(
            "A structured Market & News Research Report containing:\n\n"

            "1. Recent Company Developments\n"
            "2. Key News Events\n"
            "3. Market Activity\n"
            "4. Positive Catalysts\n"
            "5. Negative Catalysts\n"
            "6. Industry / External Factors\n"
            "7. Potential Company Impact\n"
            "8. Potential Stock Impact\n"
            "9. Key Events to Monitor\n"
            "10. Information Limitations\n\n"

            "Clearly distinguish factual information from analyst "
            "interpretation and potential implications."
        ),

        agent=agent
    )