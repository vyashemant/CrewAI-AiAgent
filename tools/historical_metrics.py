from typing import Optional

class HistoricalTrendEngine:
    """
    Computes deterministic growth rates (CAGR), trends, and labels from
    multi-year historical financial data.
    """
    
    def __init__(self, historical_data: dict):
        self.historical = historical_data

    def _get_values(self, key: str) -> list[dict]:
        return self.historical.get(key, [])

    def _cagr(self, values: list[dict]) -> Optional[float]:
        """
        Calculate Compound Annual Growth Rate (CAGR).
        Requires at least 2 data points (with non-zero starting value).
        Uses actual fiscal year differences.
        """
        if not values or len(values) < 2:
            return None
        
        first = values[0]
        last = values[-1]
        
        first_fy = first.get("fy")
        last_fy = last.get("fy")
        first_val = first.get("value")
        last_val = last.get("value")
        
        if first_fy is None or last_fy is None or first_val is None or last_val is None:
            return None
            
        years = last_fy - first_fy
        if years <= 0:
            return None
            
        if first_val <= 0:
            return None
            
        try:
            return ((last_val / first_val) ** (1 / years)) - 1
        except (ValueError, ZeroDivisionError, TypeError):
            return None

    def _growth_label(self, cagr: Optional[float]) -> str:
        if cagr is None:
            return "Unavailable"
        cagr_pct = round(cagr * 100, 2)
        if cagr_pct >= 10:
            return "Strong Growth"
        elif cagr_pct > 2:
            return "Moderate Growth"
        elif cagr_pct >= -2:
            return "Flat"
        else:
            return "Declining"

    def _margin_trend_label(self, values: list[dict]) -> str:
        """
        Determine if margins are improving, stable, or deteriorating based on start vs end.
        """
        if not values or len(values) < 2:
            return "Unavailable"
            
        first = values[0].get("value")
        last = values[-1].get("value")
        
        if first is None or last is None:
            return "Unavailable"
            
        diff = last - first
        # Arbitrary thresholds for margins (values are percentages like 0.25 for 25%)
        # Let's assume values here are absolute dollars (e.g. gross profit). We should compute margin first.
        return "Unavailable"  # Internal helper for margins only

    def _trend_label_for_metric(self, values: list[dict], metric_type: str = "growth") -> str:
        if not values or len(values) < 2:
            return "Unavailable"
            
        first = values[0].get("value")
        last = values[-1].get("value")
        
        if first is None or last is None:
            return "Unavailable"
            
        if metric_type == "growth":
            if first > 0:
                cagr = self._cagr(values)
                return self._growth_label(cagr)
            else:
                # If negative starting value, just look at absolute change
                if last > first:
                    return "Improving"
                else:
                    return "Deteriorating"
        elif metric_type == "debt":
            if last < first * 0.95:
                return "Improving"
            elif last > first * 1.05:
                return "Increasing"
            else:
                return "Stable"
        
        return "Unavailable"

    def _calculate_margin(self, num_key: str, den_key: str) -> list[dict]:
        nums = {item["fy"]: item["value"] for item in self._get_values(num_key)}
        dens = {item["fy"]: item["value"] for item in self._get_values(den_key)}
        
        margins = []
        for fy in sorted(set(list(nums.keys()) + list(dens.keys()))):
            n = nums.get(fy)
            d = dens.get(fy)
            if n is not None and d is not None and d != 0:
                margins.append({"fy": fy, "value": n / d})
        return margins

    def get_trends(self) -> dict:
        revenue = self._get_values("revenue")
        net_income = self._get_values("net_income")
        total_debt = self._get_values("total_debt")
        
        rev_cagr = self._cagr(revenue)
        ni_cagr = self._cagr(net_income)
        
        gross_margins = self._calculate_margin("gross_profit", "revenue")
        operating_margins = self._calculate_margin("operating_income", "revenue")
        net_margins = self._calculate_margin("net_income", "revenue")
        
        def _margin_label(margins: list[dict]) -> str:
            if len(margins) < 2: return "Unavailable"
            f, l = margins[0]["value"], margins[-1]["value"]
            if l - f > 0.01: return "Improving"
            if l - f < -0.01: return "Deteriorating"
            return "Stable"

        return {
            "metrics": {
                "revenue_cagr": rev_cagr,
                "net_income_cagr": ni_cagr,
            },
            "labels": {
                "Revenue Trend": self._trend_label_for_metric(revenue, "growth"),
                "Net Income Trend": self._trend_label_for_metric(net_income, "growth"),
                "Debt Trend": self._trend_label_for_metric(total_debt, "debt"),
                "Gross Margin Trend": _margin_label(gross_margins),
                "Operating Margin Trend": _margin_label(operating_margins),
                "Net Margin Trend": _margin_label(net_margins),
            }
        }
