from tools.financial_data_tool import FinancialDataTool


tool = FinancialDataTool()

result = tool.run(
    ticker="AAPL"
)

print(result)