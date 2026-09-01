import os
import sys

from services.research_pipeline import run_investment_research

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
