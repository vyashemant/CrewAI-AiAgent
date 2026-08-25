from tools.financial_metrics import FinancialMetricsEngine


engine = FinancialMetricsEngine()


# ============================================================
# TEST 1 — COMPLETE DATA
# ============================================================

metrics = engine.calculate_all(
    revenue=416_161_000_000,
    previous_revenue=391_035_000_000,
    gross_profit=195_201_000_000,
    operating_income=133_050_000_000,
    net_income=112_010_000_000,
    previous_net_income=93_739_000_000,
    operating_cash_flow=111_482_000_000,
    capital_expenditure=-12_715_000_000,
    cash=35_934_000_000,
    total_debt=106_600_000_000,
    assets=359_241_000_000,
    equity=73_733_000_000
)


print("=" * 70)
print("COMPLETE DATA TEST")
print("=" * 70)

for name, value in metrics.items():
    print(f"{name}: {value}")


# ============================================================
# TEST 2 — INCOMPLETE DEBT DATA
# ============================================================

metrics_incomplete = engine.calculate_all(
    revenue=416_161_000_000,
    gross_profit=195_201_000_000,
    operating_income=133_050_000_000,
    net_income=112_010_000_000,
    operating_cash_flow=111_482_000_000,
    capital_expenditure=-12_715_000_000,
    cash=35_934_000_000,
    total_debt=None,
    assets=359_241_000_000,
    equity=73_733_000_000
)


print("\n")
print("=" * 70)
print("INCOMPLETE DATA TEST")
print("=" * 70)

print(
    "Debt-to-Equity:",
    metrics_incomplete["debt_to_equity"]
)

print(
    "Net Cash:",
    metrics_incomplete["net_cash"]
)