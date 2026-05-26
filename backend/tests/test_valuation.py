"""股价估值与操作区间评估模块单元测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from analysis.valuation import analyze_valuation

def _make_mock_kline(days=120):
    """生成简单的模拟收盘价数据"""
    np.random.seed(42)
    # 平均价格 100 元，标准差 10
    prices = [100.0 + float(np.random.normal(0, 10)) for _ in range(days)]
    return pd.DataFrame({
        "close": prices
    })

def test_valuation_empty_kline():
    res = analyze_valuation(pd.DataFrame(), 100.0, 50)
    assert res["support"] == 0.0
    assert res["resistance"] == 0.0
    assert res["operation_class"] == "暂无评级"

def test_valuation_insufficient_data():
    kline = pd.DataFrame({"close": [10.0, 11.0]})
    res = analyze_valuation(kline, 10.5, 30)
    assert res["operation_class"] == "暂无评级"

def test_valuation_fallback_current_price():
    kline = _make_mock_kline(100)
    last_close = float(kline["close"].iloc[-1])
    res = analyze_valuation(kline, 0.0, 40)
    assert res["current_price"] == last_close

def test_valuation_strong_buy():
    kline = _make_mock_kline(120)
    closes = kline["close"].dropna().tolist()
    support = float(np.percentile(closes, 15))
    
    # 股价低于或等于支撑位 1.05 倍，且总分 >= 60 (强烈买入)
    price_near_support = support * 1.01
    res = analyze_valuation(kline, price_near_support, 75)
    assert "强烈推荐买入" in res["operation_class"]
    assert res["support"] > 0
    assert res["resistance"] > res["support"]

def test_valuation_high_price_strong_buy_score():
    kline = _make_mock_kline(120)
    closes = kline["close"].dropna().tolist()
    resistance = float(np.percentile(closes, 85))
    
    # 股价高于阻力位，即便总分 >= 60，操作建议也应当警示不宜追涨
    price_near_resistance = resistance * 1.02
    res = analyze_valuation(kline, price_near_resistance, 80)
    assert "逢高分批止盈" in res["operation_class"]

def test_valuation_bearish_reduce():
    kline = _make_mock_kline(120)
    closes = kline["close"].dropna().tolist()
    resistance = float(np.percentile(closes, 85))
    
    # 股价高位，且总分偏空
    price_near_resistance = resistance * 0.99
    res = analyze_valuation(kline, price_near_resistance, -45)
    assert "逢高果断减仓" in res["operation_class"]

def test_valuation_neutral_震荡():
    kline = _make_mock_kline(120)
    closes = kline["close"].dropna().tolist()
    support = float(np.percentile(closes, 15))
    resistance = float(np.percentile(closes, 85))
    
    # 价格位于两者中间，且得分为中性 (比如 0 分)
    mid_price = (support + resistance) / 2
    res = analyze_valuation(kline, mid_price, 0.0)
    assert "无趋势震荡" in res["operation_class"]
