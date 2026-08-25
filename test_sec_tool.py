from tools.sec_financial_tool import SECFinancialDataTool


tool = SECFinancialDataTool()

result = tool.run(
    ticker="AAPL"
)

print(result)