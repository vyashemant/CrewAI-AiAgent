from dotenv import load_dotenv

from tools.news_data_tool import NewsDataTool


# Load environment variables
load_dotenv()


# ============================================================
# TEST NEWS DATA TOOL
# ============================================================

tool = NewsDataTool()

result = tool.run(
    ticker="AAPL",
    limit=3
)

print("=" * 80)
print("NEWS DATA TOOL TEST")
print("=" * 80)

print(result)