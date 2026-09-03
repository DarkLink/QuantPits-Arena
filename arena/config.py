"""
arena/config.py
===============
全局路径常量与默认运行参数配置
"""

from pathlib import Path

# 项目根目录
REPO_ROOT = Path(__file__).resolve().parent.parent

# Qlib 数据只读路径
QLIB_DATA_URI = Path.home() / ".qlib" / "qlib_data" / "cn_data"
CALENDAR_PATH = QLIB_DATA_URI / "calendars" / "day.txt"

# 本地资产目录
MODELS_DIR = REPO_ROOT / "artifacts" / "models"
CONFIGS_DIR = REPO_ROOT / "artifacts" / "configs"
MANIFESTS_PRIVATE_DIR = REPO_ROOT / "manifests" / "private"
MANIFESTS_PUBLIC_DIR = REPO_ROOT / "manifests" / "public"
ALIAS_MAP_FILE = MANIFESTS_PRIVATE_DIR / "alias_map.yaml"

# 运行输出目录
RUNS_DIR = REPO_ROOT / "runs"

# 默认时间锚定与交易日范围
DEFAULT_ANCHOR_DATE = "2026-07-03"        # 周五收盘截断日
DEFAULT_FIRST_TRADE_DATE = "2026-07-06"   # 周一首周开盘建仓日
DEFAULT_END_DATE = "2026-08-28"           # 截止周五收盘结算日

# 默认市场与基准
DEFAULT_MARKET = "csirun300"
DEFAULT_BENCHMARK = "SH000300"

# 默认资金与费率
DEFAULT_INITIAL_NAV = 1.0
DEFAULT_INITIAL_CASH = 100_000_000.0
DEFAULT_OPEN_COST = 0.0005    # 万分之五
DEFAULT_CLOSE_COST = 0.0015   # 千分之一点五
DEFAULT_MIN_COST = 5.0        # 最低 5 元
DEFAULT_LIMIT_THRESHOLD = 0.095

# 默认策略配置
DEFAULT_TOPK = 22
DEFAULT_CANONICAL_DROP_N = 3
DEFAULT_DEAL_PRICE = "open"   # 默认周一开盘价成交
DEFAULT_VALUATION_FREQ = "daily"
