from tools.market_data_tool import MarketDataTool


tool = MarketDataTool()

result = tool.run(
    ticker="AAPL"
)

print(result)