"""情绪面分析：涨跌停比、换手率偏离度、量比"""
import pandas as pd
import numpy as np


def analyze(kline: pd.DataFrame, quote: dict, limit_stats: dict):
    """
    分析市场情绪，给出 -100 ~ +100 评分
    参数:
        kline: 日K线 DataFrame
        quote: 实时行情 dict (含 turnover, volume_ratio)
        limit_stats: 涨跌停统计 dict (含 zt_count, dt_count, zt_ratio)
    返回:
        score, detail
    """
    detail = {
        "limit": {"score": 0, "weight": 40},
        "turnover": {"score": 0, "weight": 30},
        "volume": {"score": 0, "weight": 30},
    }

    limit_score = _limit_score(limit_stats)
    turnover_score = _turnover_score(kline, quote)
    volume_score = _volume_score(quote)

    detail["limit"]["score"] = limit_score
    detail["turnover"]["score"] = turnover_score
    detail["volume"]["score"] = volume_score

    total = limit_score * 0.40 + turnover_score * 0.30 + volume_score * 0.30
    return round(total, 2), detail


def _limit_score(limit_stats: dict) -> float:
    if not limit_stats:
        return 0.0
    zt = limit_stats.get("zt_count", 0)
    dt = limit_stats.get("dt_count", 0)
    if zt == 0 and dt == 0:
        return 0.0
    if zt > dt * 2:
        return 40.0
    elif zt > dt:
        return 20.0
    elif dt > zt * 2:
        return -40.0
    elif dt > zt:
        return -20.0
    return 0.0


def _turnover_score(kline: pd.DataFrame, quote: dict) -> float:
    if "turnover" not in quote or kline is None or kline.empty:
        return 0.0
    current = quote["turnover"]
    recent = kline["turnover"].values.astype(float) if "turnover" in kline.columns else []
    if len(recent) < 5:
        return 0.0
    avg5 = np.mean(recent[-5:])
    if avg5 == 0:
        return 0.0
    ratio = current / avg5
    if ratio > 2.0:
        return 30.0
    elif ratio > 1.5:
        return 15.0
    elif ratio < 0.5:
        return -30.0
    elif ratio < 0.7:
        return -15.0
    return 0.0


def _volume_score(quote: dict) -> float:
    vr = quote.get("volume_ratio", 0)
    if vr > 2.0:
        return 30.0
    elif vr > 1.5:
        return 15.0
    elif vr < 0.5:
        return -30.0
    elif vr < 0.7:
        return -15.0
    return 0.0