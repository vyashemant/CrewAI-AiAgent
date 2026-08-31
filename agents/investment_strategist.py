from typing import List, Literal, Optional

from crewai import LLM, Agent, Task
from pydantic import BaseModel, Field


# ============================================================
# PYDANTIC STRUCTURED OUTPUT MODEL
# ============================================================

class InvestmentStrategy(BaseModel):
    """
    Structured output model for the Investment Strategist.

    The strategist synthesizes the four specialist analyst reports
    into a single, evidence-based investment strategy.
    """

    # Core thesis
    investment_thesis: str = Field(
        description=(
            "One concise paragraph stating the core investment thesis. "
            "This must be grounded in the analyst reports and must not "
            "invent financial data, forecasts, or events."
        )
    )

    # Specialist summaries
    fundamental_assessment: str = Field(
        description=(
            "Summary of the financial fundamentals drawn from the "
            "Financial Analyst report. Identify key strengths and "
            "weaknesses without inventing new metrics."
        )
    )

    market_and_news_assessment: str = Field(
        description=(
            "Summary of market activity and news developments drawn "
            "from the Market and News Analyst report. Distinguish "
            "verified events from interpretation."
        )
    )

    valuation_assessment: str = Field(
        description=(
            "Summary of the valuation picture drawn from the "
            "Valuation Analyst report. State whether the stock "
            "appears expensive, fair, or attractive relative to "
            "reported fundamentals, using only provided multiples."
        )
    )

    risk_assessment: str = Field(
        description=(
            "Summary of the most important risks drawn from the "
            "Risk Analyst report. Prioritise the highest-severity "
            "risks that could materially affect the investment case."
        )
    )

    # Scenario analysis
    bull_case: str = Field(
        description=(
            "Optimistic scenario describing the conditions under which "
            "the investment performs well. Must be grounded in evidence "
            "from the analyst reports, not invented assumptions."
        )
    )

    base_case: str = Field(
        description=(
            "Most-likely scenario based on the current evidence "
            "provided by all four analyst reports."
        )
    )

    bear_case: str = Field(
        description=(
            "Pessimistic scenario describing the conditions under which "
            "the investment underperforms or loses value. Must be grounded "
            "in identified risks and data limitations."
        )
    )

    # Catalysts and risks
    key_catalysts: List[str] = Field(
        description=(
            "List of the most important positive catalysts that could "
            "improve the investment outcome. Each item must be grounded "
            "in the analyst reports."
        )
    )

    key_risks: List[str] = Field(
        description=(
            "List of the most important risks that could negatively "
            "affect the investment outcome. Each item must be grounded "
            "in the analyst reports."
        )
    )

    thesis_change_triggers: List[str] = Field(
        description=(
            "List of specific developments or data points that, if they "
            "occurred, would require reassessment of this thesis. "
            "Examples: guidance cut, margin deterioration, regulatory action."
        )
    )

    # Quality vs valuation distinction
    company_quality: str = Field(
        description=(
            "Assessment of the underlying BUSINESS quality: competitive "
            "position, profitability, balance-sheet strength, and cash "
            "generation. This must be evaluated separately from the stock "
            "price or valuation multiples."
        )
    )

    valuation_view: str = Field(
        description=(
            "Assessment of the STOCK VALUATION relative to the business "
            "quality and available metrics. A high-quality company can "
            "still have an expensive stock. Explicitly state whether the "
            "current valuation multiples appear to justify ownership at "
            "the current price."
        )
    )

    # Final decision fields
    recommendation: Literal["BUY", "HOLD", "SELL"] = Field(
        description=(
            "Final investment recommendation. Must be exactly one of: "
            "BUY, HOLD, SELL. This decision must weigh both company "
            "quality AND current valuation. A high-quality company at "
            "an excessive valuation may still warrant HOLD or SELL."
        )
    )

    confidence: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description=(
            "Confidence level in the recommendation. LOW if data is "
            "materially incomplete or contradictory. MEDIUM if data is "
            "adequate but key uncertainties remain. HIGH if the evidence "
            "is strong and consistent across all four analyst reports."
        )
    )

    # Evidence and limitations
    evidence_summary: str = Field(
        description=(
            "Summary of the key verified facts and calculated metrics "
            "from the analyst reports that most influenced this strategy. "
            "Distinguish verified facts from analyst interpretation."
        )
    )

    information_limitations: str = Field(
        description=(
            "List of important information that was unavailable, "
            "incomplete, or could not be verified. Explain how these "
            "limitations affect the confidence in the recommendation."
        )
    )

    # Contradiction / consistency flag
    contradictions_detected: Optional[str] = Field(
        default=None,
        description=(
            "If any specialist reports contain conflicting or inconsistent "
            "data (e.g., different revenue figures, contradictory risk "
            "assessments), describe the discrepancy here and state which "
            "source should be preferred and why. Set to null if no "
            "material contradictions were detected."
        )
    )


# ============================================================
# AGENT FACTORY
# ============================================================

def create_investment_strategist(llm: LLM) -> Agent:
    """
    Create the Investment Strategist agent.

    The Investment Strategist synthesises the four specialist
    analyst reports (Financial, Market and News, Valuation, Risk)
    into a final, structured investment strategy.

    It does NOT retrieve external data, recalculate metrics,
    or invent financial information.
    """

    return Agent(
        role="Investment Strategist",

        goal=(
            "Synthesise the validated outputs of the Financial Research "
            "Analyst, Market and News Research Analyst, Valuation Research "
            "Analyst, and Risk Research Analyst into a single, coherent, "
            "evidence-based investment strategy. "
            "Produce a final BUY, HOLD, or SELL recommendation with a "
            "stated confidence level, supported by a structured investment "
            "thesis that clearly separates company quality from stock "
            "valuation attractiveness."
        ),

        backstory=(
            "You are a senior investment strategist with 12 years of "
            "experience synthesising specialist research into actionable "
            "investment decisions for institutional clients.\n\n"

            "Your role is to integrate, weigh, and adjudicate between "
            "the findings of four specialist analysts - financial, "
            "market/news, valuation, and risk - and produce a single "
            "coherent investment strategy.\n\n"

            "SYNTHESIS RULES:\n"

            "1. You do not retrieve external data, calculate new metrics, "
            "or verify financial figures independently. Your analysis is "
            "based entirely on the four specialist reports provided.\n"

            "2. You must not invent financial data, forecasts, news events, "
            "peer comparisons, or historical valuation ranges that are not "
            "explicitly present in the analyst reports.\n"

            "3. You must distinguish clearly between:\n"
            "   - Verified facts (directly from retrieved data)\n"
            "   - Analyst interpretation (derived from the reports)\n"
            "   - Your own strategic conclusions\n\n"

            "4. You must explicitly separate:\n"
            "   - COMPANY QUALITY: business fundamentals, profitability, "
            "competitive position, financial strength\n"
            "   - STOCK ATTRACTIVENESS: current valuation relative to "
            "quality and evidence\n\n"

            "5. A high-quality business does NOT automatically justify a "
            "BUY recommendation. If the valuation analyst reports elevated "
            "multiples and no margin of safety is visible, you must "
            "acknowledge this and weigh it in your recommendation.\n\n"

            "6. If the specialist reports contain conflicting data values, "
            "you must identify the contradiction, state which source is "
            "more reliable, and explain how this affects your confidence.\n\n"

            "7. Your recommendation must be one of: BUY, HOLD, SELL.\n"

            "8. Your confidence must be one of: LOW, MEDIUM, HIGH.\n\n"
            "9. If the Consistency Report flags contradictions, you MUST address them and prioritise the Canonical Evidence Snapshot.\n\n"

            "10. Never provide personalised portfolio allocation advice."
        ),

        llm=llm,
        verbose=True,
        allow_delegation=False
    )


# ============================================================
# TASK FACTORY
# ============================================================

def create_investment_strategy_task(agent: Agent) -> Task:
    """
    Create the Investment Strategist task.

    The task receives the four specialist analyst reports
    as input context and produces a structured InvestmentStrategy
    Pydantic model as output.
    """

    separator = "=" * 60

    return Task(
        description=(
            "You are the Investment Strategist responsible for synthesising "
            "the four specialist analyst reports for {company} into a single "
            "final investment strategy.\n\n"

            "The four specialist reports are provided below:\n\n"

            f"{separator}\n"
            "FINANCIAL ANALYST REPORT\n"
            f"{separator}\n"
            "{financial_analyst_report}\n\n"

            f"{separator}\n"
            "MARKET AND NEWS ANALYST REPORT\n"
            f"{separator}\n"
            "{market_news_analyst_report}\n\n"

            f"{separator}\n"
            "VALUATION ANALYST REPORT\n"
            f"{separator}\n"
            "{valuation_analyst_report}\n\n"

            f"{separator}\n"
            "RISK ANALYST REPORT\n"
            f"{separator}\n"
            "{risk_analyst_report}\n\n"


            f"{separator}\n"
            "CANONICAL RESEARCH EVIDENCE AND CONSISTENCY REPORT\n"
            f"{separator}\n"
            "Canonical Evidence Snapshot:\n"
            "{canonical_evidence}\n\n"
            "Consistency Report (Validator Results):\n"
            "{consistency_report}\n\n"
            f"{separator}\n"
            "SYNTHESIS INSTRUCTIONS\n"
            f"{separator}\n\n"

            "Step 1 - DATA INTEGRITY CHECK\n"
            "Before synthesising, scan the four reports for:\n"
            "- Conflicting numerical values across reports\n"
            "- Contradictory assessments of the same factor\n"
            "- Missing or unavailable data that materially affects "
            "the conclusion\n"
            "Record any contradictions in the contradictions_detected field. "
            "If no material contradictions exist, set it to null.\n\n"

            "Step 2 - SEPARATE QUALITY FROM VALUATION\n"
            "Explicitly assess:\n"
            "a) Company Quality - the underlying business quality based "
            "on financial fundamentals, competitive position, profitability, "
            "and financial health reported by the Financial Analyst.\n"
            "b) Valuation View - whether the current stock price and "
            "valuation multiples offer an attractive entry point given "
            "the business quality, using only the Valuation Analyst data.\n"
            "These are distinct questions. A great company can be a poor "
            "investment at the wrong price.\n\n"

            "Step 3 - SCENARIO ANALYSIS\n"
            "Develop a Bull Case, Base Case, and Bear Case using only "
            "evidence from the specialist reports. Do not invent scenarios "
            "that have no basis in the provided data.\n\n"

            "Step 4 - RECOMMENDATION\n"
            "Produce a final recommendation (BUY / HOLD / SELL) and "
            "a confidence level (LOW / MEDIUM / HIGH).\n"
            "- BUY: The investment offers an attractive risk/reward "
            "balance at the current valuation, supported by evidence.\n"
            "- HOLD: The company has merit but the valuation or risk "
            "profile does not offer a sufficiently compelling entry.\n"
            "- SELL: The risk/reward is unfavourable at the current "
            "valuation, or fundamental deterioration is evident.\n\n"

            "CRITICAL RULES:\n"
            "- Do not invent financial data, peer comparisons, "
            "forecasts, or news events.\n"
            "- Do not automatically recommend BUY for a high-quality "
            "company. Valuation must justify the recommendation.\n"
            "- Distinguish verified facts from interpretation in "
            "the evidence_summary field.\n"
            "- Set confidence to LOW if data is incomplete or "
            "contradictions cannot be resolved."
        ),

        expected_output=(
            "A structured investment strategy containing all fields "
            "of the InvestmentStrategy model:\n\n"
            "- investment_thesis\n"
            "- fundamental_assessment\n"
            "- market_and_news_assessment\n"
            "- valuation_assessment\n"
            "- risk_assessment\n"
            "- bull_case\n"
            "- base_case\n"
            "- bear_case\n"
            "- key_catalysts (list)\n"
            "- key_risks (list)\n"
            "- thesis_change_triggers (list)\n"
            "- company_quality\n"
            "- valuation_view\n"
            "- recommendation (BUY / HOLD / SELL)\n"
            "- confidence (LOW / MEDIUM / HIGH)\n"
            "- evidence_summary\n"
            "- information_limitations\n"
            "- contradictions_detected (null if none)\n\n"
            "The recommendation must be BUY, HOLD, or SELL - nothing else. "
            "The confidence must be LOW, MEDIUM, or HIGH - nothing else."
        ),

        output_pydantic=InvestmentStrategy,

        agent=agent
    )
