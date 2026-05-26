"""分析模块基础单元测试（不依赖 AKShare 网络请求）"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from analysis.technical import analyze as tech_analyze
from analysis.capital import analyze as cap_analyze
from analysis.sentiment import analyze as sent_analyze
from analysis.information import analyze as info_analyze
from analysis.scorer import _score_to_signal


def _make_kline(days=120, trend='up'):
    """生成模拟K线数据"""
    np.random.seed(42)
    base = 10.0
    if trend == 'up':
        prices = [base + i * 0.05 + np.random.normal(0, 0.1) for i in range(days)]
    elif trend == 'down':
        prices = [base - i * 0.05 + np.random.normal(0, 0.1) for i in range(days)]
    else:
        prices = [base + np.random.normal(0, 0.2) for i in range(days)]

    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=days, freq="B"),
        "open": [p + np.random.normal(0, 0.05) for p in prices],
        "close": prices,
        "high": [p + abs(np.random.normal(0, 0.1)) for p in prices],
        "low": [p - abs(np.random.normal(0, 0.1)) for p in prices],
        "volume": np.random.randint(100000, 1000000, days),
        "turnover": np.random.uniform(1.0, 5.0, days),
    })


class TestTechnicalAnalysis:
    def test_upward_trend_positive_score(self):
        kline = _make_kline(days=120, trend='up')
        score, detail = tech_analyze(kline)
        assert isinstance(score, float)
        assert -100 <= score <= 100
        assert detail != {}

    def test_downward_trend_negative_score(self):
        kline = _make_kline(days=120, trend='down')
        score, detail = tech_analyze(kline)
        assert isinstance(score, float)
        assert -100 <= score <= 100

    def test_short_data_returns_zero(self):
        kline = _make_kline(days=5)
        score, detail = tech_analyze(kline)
        assert score == 0.0
        assert detail == {}

    def test_minimal_data_works(self):
        kline = _make_kline(days=10)
        score, detail = tech_analyze(kline)
        assert isinstance(score, float)


class TestCapitalAnalysis:
    def test_positive_fund_flow(self):
        df = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=5),
            "main_net": [1000000, 2000000, 1500000, 3000000, 2500000],
            "main_ratio": [5.0, 8.0, 6.0, 10.0, 9.0],
            "super_large_net": [500000, 1000000, 800000, 1500000, 1200000],
            "super_large_ratio": [3.0, 5.0, 4.0, 7.0, 6.0],
            "large_net": [500000, 1000000, 700000, 1500000, 1300000],
            "large_ratio": [2.0, 3.0, 2.0, 3.0, 3.0],
        })
        score, detail = cap_analyze(df)
        assert isinstance(score, float)
        assert -100 <= score <= 100

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        score, detail = cap_analyze(df)
        assert score == 0.0

    def test_none_dataframe(self):
        score, detail = cap_analyze(None)
        assert score == 0.0


class TestSentimentAnalysis:
    def test_bullish_market(self):
        kline = _make_kline(days=60)
        quote = {"turnover": 8.0, "volume_ratio": 2.5}
        limit_stats = {"zt_count": 100, "dt_count": 20, "zt_ratio": 5.0}
        score, detail = sent_analyze(kline, quote, limit_stats)
        assert isinstance(score, float)
        assert -100 <= score <= 100

    def test_empty_inputs(self):
        kline = pd.DataFrame()
        quote = {}
        limit_stats = {}
        score, detail = sent_analyze(kline, quote, limit_stats)
        assert isinstance(score, float)


class TestInformationAnalysis:
    def test_bullish_news(self):
        news = [
            {"title": "业绩预增，机构看好", "content": "公司业绩大幅增长", "time": "2026-01-01"},
            {"title": "突破新高，合作签约", "content": "股价创新高", "time": "2026-01-02"},
        ]
        score, detail = info_analyze(news)
        assert score > 0
        assert detail["bullish"] > 0

    def test_bearish_news(self):
        news = [
            {"title": "业绩预减，被调查", "content": "公司亏损严重", "time": "2026-01-01"},
            {"title": "违规减持，退市风险", "content": "股价创新低", "time": "2026-01-02"},
        ]
        score, detail = info_analyze(news)
        assert score < 0
        assert detail["bearish"] > 0

    def test_empty_news(self):
        score, detail = info_analyze([])
        assert score == 0.0

    def test_mixed_news(self):
        news = [
            {"title": "业绩预增", "content": "增长", "time": "2026-01-01"},
            {"title": "业绩预减", "content": "亏损", "time": "2026-01-02"},
        ]
        score, detail = info_analyze(news)
        assert detail["bullish"] > 0
        assert detail["bearish"] > 0


class TestScoreToSignal:
    def test_strong_buy(self):
        signal, color = _score_to_signal(80)
        assert signal == "强烈买入"

    def test_buy(self):
        signal, color = _score_to_signal(30)
        assert signal == "买入"

    def test_hold(self):
        signal, color = _score_to_signal(0)
        assert signal == "持有"

    def test_sell(self):
        signal, color = _score_to_signal(-40)
        assert signal == "卖出"

    def test_strong_sell(self):
        signal, color = _score_to_signal(-80)
        assert signal == "强烈卖出"

    def test_boundary_60(self):
        signal, color = _score_to_signal(60)
        assert signal == "强烈买入"

    def test_boundary_20(self):
        signal, color = _score_to_signal(20)
        assert signal == "买入"

    def test_boundary_minus20(self):
        signal, color = _score_to_signal(-20)
        assert signal == "持有"

    def test_boundary_minus60(self):
        signal, color = _score_to_signal(-60)
        assert signal == "卖出"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
