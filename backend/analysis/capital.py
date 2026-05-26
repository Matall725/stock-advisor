"""资金面分析：主力资金流向"""
import pandas as pd
import numpy as np


def analyze(fund_flow: pd.DataFrame):
    """
    分析资金流向，给出 -100 ~ +100 评分
    参数:
        fund_flow: DataFrame, 包含 main_net, main_ratio, super_large_net,
                   large_net, super_large_ratio, large_ratio 列
    返回:
        score: float, -100 ~ +100
    """
    if fund_flow is None or fund_flow.empty:
        return 0.0, {"trend": {"score": 0, "weight": 50}, "ratio": {"score": 0, "weight": 50}}

    recent = fund_flow.tail(5)
    if len(recent) < 3:
        return 0.0, {"trend": {"score": 0, "weight": 50}, "ratio": {"score": 0, "weight": 50}}

    trend_score = _trend_score(recent)
    ratio_score = _ratio_score(recent)

    detail = {
        "trend": {"score": trend_score, "weight": 50},
        "ratio": {"score": ratio_score, "weight": 50},
    }
    total = trend_score * 0.50 + ratio_score * 0.50
    return round(total, 2), detail


def _trend_score(recent: pd.DataFrame) -> float:
    main_nets = recent["main_net"].values.astype(float)
    positive_days = int(np.sum(main_nets > 0))
    negative_days = int(np.sum(main_nets < 0))

    if positive_days > negative_days:
        if positive_days >= 4:
            return 50.0
        elif positive_days >= 3:
            return 30.0
        else:
            return 10.0
    elif negative_days > positive_days:
        if negative_days >= 4:
            return -50.0
        elif negative_days >= 3:
            return -30.0
        else:
            return -10.0
    return 0.0


def _ratio_score(recent: pd.DataFrame) -> float:
    try:
        super_large_ratio = recent["super_large_ratio"].values.astype(float)
        large_ratio = recent["large_ratio"].values.astype(float)
        combined = np.nanmean(super_large_ratio[-3:]) + np.nanmean(large_ratio[-3:])
    except (KeyError, IndexError):
        return 0.0

    if combined > 20:
        return 50.0
    elif combined > 10:
        return 30.0
    elif combined > 5:
        return 15.0
    elif combined < -20:
        return -50.0
    elif combined < -10:
        return -30.0
    elif combined < -5:
        return -15.0
    return 0.0