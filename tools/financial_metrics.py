from typing import Optional


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_valid_number(value) -> bool:
    """
    Check whether a value is a valid numeric value.
    """

    return (
        value is not None
        and isinstance(value, (int, float))
        and value == value
    )


def calculate_percentage(numerator, denominator) -> Optional[float]:
    """
    Calculate a percentage safely.

    Returns None when the required data is unavailable
    or the denominator is zero.
    """

    if not is_valid_number(numerator):
        return None

    if not is_valid_number(denominator):
        return None

    if denominator == 0:
        return None

    return (numerator / denominator) * 100


def calculate_ratio(numerator, denominator) -> Optional[float]:
    """
    Calculate a ratio safely.
    """

    if not is_valid_number(numerator):
        return None

    if not is_valid_number(denominator):
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# ============================================================
# FINANCIAL METRICS ENGINE
# ============================================================

class FinancialMetricsEngine:
    """
    Calculate financial metrics only when all required
    underlying data is available.
    """

    # ========================================================
    # PROFITABILITY METRICS
    # ========================================================

    @staticmethod
    def gross_margin(
        gross_profit,
        revenue
    ):

        return calculate_percentage(
            gross_profit,
            revenue
        )

    @staticmethod
    def operating_margin(
        operating_income,
        revenue
    ):

        return calculate_percentage(
            operating_income,
            revenue
        )

    @staticmethod
    def net_profit_margin(
        net_income,
        revenue
    ):

        return calculate_percentage(
            net_income,
            revenue
        )

    # ========================================================
    # GROWTH METRICS
    # ========================================================

    @staticmethod
    def revenue_growth(
        current_revenue,
        previous_revenue
    ):

        if not is_valid_number(current_revenue):
            return None

        if not is_valid_number(previous_revenue):
            return None

        if previous_revenue == 0:
            return None

        return (
            (current_revenue - previous_revenue)
            / previous_revenue
        ) * 100

    @staticmethod
    def net_income_growth(
        current_income,
        previous_income
    ):

        if not is_valid_number(current_income):
            return None

        if not is_valid_number(previous_income):
            return None

        if previous_income == 0:
            return None

        return (
            (current_income - previous_income)
            / previous_income
        ) * 100

    # ========================================================
    # CASH FLOW METRICS
    # ========================================================

    @staticmethod
    def free_cash_flow(
        operating_cash_flow,
        capital_expenditure
    ):

        if not is_valid_number(operating_cash_flow):
            return None

        if not is_valid_number(capital_expenditure):
            return None

        # SEC reports capital expenditure as a cash outflow
        # in this context, so add the negative outflow.
        return (
            operating_cash_flow
            + capital_expenditure
        )

    @staticmethod
    def fcf_margin(
        free_cash_flow,
        revenue
    ):

        return calculate_percentage(
            free_cash_flow,
            revenue
        )

    # ========================================================
    # BALANCE SHEET METRICS
    # ========================================================

    @staticmethod
    def debt_to_equity(
        total_debt,
        equity
    ):

        return calculate_percentage(
            total_debt,
            equity
        )

    @staticmethod
    def net_cash(
        cash,
        total_debt
    ):

        if not is_valid_number(cash):
            return None

        if not is_valid_number(total_debt):
            return None

        return cash - total_debt

    # ========================================================
    # RETURN METRICS
    # ========================================================

    @staticmethod
    def return_on_equity(
        net_income,
        equity
    ):

        return calculate_percentage(
            net_income,
            equity
        )

    @staticmethod
    def return_on_assets(
        net_income,
        assets
    ):

        return calculate_percentage(
            net_income,
            assets
        )

    # ========================================================
    # EFFICIENCY METRICS
    # ========================================================

    @staticmethod
    def asset_turnover(
        revenue,
        assets
    ):

        return calculate_ratio(
            revenue,
            assets
        )

    @staticmethod
    def equity_multiplier(
        assets,
        equity
    ):

        return calculate_ratio(
            assets,
            equity
        )

    # ========================================================
    # COMPLETE METRICS
    # ========================================================

    def calculate_all(
        self,
        revenue=None,
        previous_revenue=None,
        gross_profit=None,
        operating_income=None,
        net_income=None,
        previous_net_income=None,
        operating_cash_flow=None,
        capital_expenditure=None,
        cash=None,
        total_debt=None,
        assets=None,
        equity=None
    ):

        fcf = self.free_cash_flow(
            operating_cash_flow,
            capital_expenditure
        )

        return {

            "revenue_growth": self.revenue_growth(
                revenue,
                previous_revenue
            ),

            "net_income_growth": self.net_income_growth(
                net_income,
                previous_net_income
            ),

            "gross_margin": self.gross_margin(
                gross_profit,
                revenue
            ),

            "operating_margin": self.operating_margin(
                operating_income,
                revenue
            ),

            "net_profit_margin": self.net_profit_margin(
                net_income,
                revenue
            ),

            "free_cash_flow": fcf,

            "fcf_margin": self.fcf_margin(
                fcf,
                revenue
            ),

            "debt_to_equity": self.debt_to_equity(
                total_debt,
                equity
            ),

            "net_cash": self.net_cash(
                cash,
                total_debt
            ),

            "return_on_equity": self.return_on_equity(
                net_income,
                equity
            ),

            "return_on_assets": self.return_on_assets(
                net_income,
                assets
            ),

            "asset_turnover": self.asset_turnover(
                revenue,
                assets
            ),

            "equity_multiplier": self.equity_multiplier(
                assets,
                equity
            )
        }

    def calculate_from_sec_data(
        self,
        financial_data
    ):
        """
        Calculate metrics from normalized SEC financial data.
        """

        return self.calculate_all(

            revenue=financial_data.get(
                "revenue"
            ),

            previous_revenue=financial_data.get(
                "previous_revenue"
            ),

            gross_profit=financial_data.get(
                "gross_profit"
            ),

            operating_income=financial_data.get(
                "operating_income"
            ),

            net_income=financial_data.get(
                "net_income"
            ),

            previous_net_income=financial_data.get(
                "previous_net_income"
            ),

            operating_cash_flow=financial_data.get(
                "operating_cash_flow"
            ),

            capital_expenditure=financial_data.get(
                "capital_expenditure"
            ),

            cash=financial_data.get(
                "cash"
            ),

            total_debt=financial_data.get(
                "total_debt"
            ),

            assets=financial_data.get(
                "assets"
            ),

            equity=financial_data.get(
                "stockholders_equity"
            )
        )