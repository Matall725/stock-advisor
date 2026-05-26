"""系统配置：权重、阈值、缓存参数"""
import os

# 四维度默认权重（总和 = 1.0）
DEFAULT_WEIGHTS = {
    "information": 0.20,
    "capital": 0.25,
    "sentiment": 0.15,
    "technical": 0.40,
}

# 五级信号阈值（总分 -100 ~ +100，符合 A 股红涨绿跌习惯）
SIGNAL_THRESHOLDS = [
    (60, "强烈买入", "#c62828"),   # 深红
    (20, "买入", "#ef5350"),       # 浅红
    (-20, "持有", "#9e9e9e"),      # 灰色
    (-60, "卖出", "#4caf50"),      # 浅绿
    (-101, "强烈卖出", "#2e7d32"), # 深绿
]

# 缓存目录
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
# 缓存过期时间（秒）
CACHE_TTL = 4 * 60 * 60  # 4小时

# K线默认天数
KLINE_DAYS = 120
