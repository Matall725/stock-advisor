"""技术面分析：MA / MACD / KDJ / RSI 综合评分"""
import pandas as pd
import numpy as np


def analyze(kline: pd.DataFrame):
    """
    对K线数据做技术面综合评分
    参数:
        kline: DataFrame, 包含 close, high, low, volume 列，按 date 升序
    返回:
        (score, detail): tuple[float, dict]
    """
    if len(kline) < 10:
        return 0.0, {}

    close = kline["close"].values.astype(float)
    high = kline["high"].values.astype(float)
    low = kline["low"].values.astype(float)

    data_len = len(close)
    ma_period = min(60, data_len - 1)
    ma20_period = min(20, data_len - 1)
    ma10_period = min(10, data_len - 1)
    ma5_period = min(5, data_len - 1)

    ma_score_val = _ma_score(close, ma5_period, ma10_period, ma20_period, ma_period)
    macd_score_val = _macd_score(close)
    kdj_score_val = _kdj_score(close, high, low)
    rsi_score_val = _rsi_score(close)

    detail = {
        "ma": {"score": ma_score_val, "weight": 30},
        "macd": {"score": macd_score_val, "weight": 25},
        "kdj": {"score": kdj_score_val, "weight": 20},
        "rsi": {"score": rsi_score_val, "weight": 25},
    }

    total = sum(d["score"] * d["weight"] / 100.0 for d in detail.values())
    return round(total, 2), detail


def _ma_score(close: np.ndarray, ma5_p=5, ma10_p=10, ma20_p=20, ma60_p=60) -> float:
    ma5 = np.mean(close[-ma5_p:])
    ma10 = np.mean(close[-ma10_p:])
    ma20 = np.mean(close[-ma20_p:])
    ma60 = np.mean(close[-ma60_p:])

    bullish = 0
    if ma5 > ma10:
        bullish += 1
    if ma10 > ma20:
        bullish += 1
    if ma20 > ma60:
        bullish += 1

    if bullish == 3:
        return 30.0
    elif bullish == 2:
        return 15.0
    elif bullish == 1:
        return 0.0
    else:
        return -30.0


def _macd_score(close: np.ndarray) -> float:
    ema12 = _ema(close, 12)
    ema26 = _ema(close, 26)
    dif = ema12 - ema26
    dea = _ema(dif, 9)
    macd_bar = 2 * (dif - dea)

    bars = macd_bar[-3:]
    prev = bars[-2]
    curr = bars[-1]

    score = 0.0
    if prev <= 0 and curr > 0:
        score += 10.0
    elif prev >= 0 and curr < 0:
        score -= 10.0
    if curr > prev:
        score += min(7.5, (curr - prev) * 5)
    else:
        score -= min(7.5, (prev - curr) * 5)

    return max(-25.0, min(25.0, score))


def _kdj_score(close: np.ndarray, high: np.ndarray, low: np.ndarray) -> float:
    n = min(9, len(close))
    if n < 3:
        return 0.0
    k_val, _d, j_val = _kdj(close, high, low, n)
    if j_val < 20:
        return 20.0
    elif j_val > 80:
        return -20.0
    else:
        if j_val > _d and k_val < 50:
            return 10.0
        elif j_val < _d and k_val > 50:
            return -10.0
        return 0.0


def _rsi_score(close: np.ndarray) -> float:
    period = min(14, len(close) - 1)
    if period < 2:
        return 0.0
    rsi = _rsi(close, period)
    if rsi < 30:
        return 25.0
    elif rsi > 70:
        return -25.0
    elif rsi < 40:
        return 12.0
    elif rsi > 60:
        return -12.0
    return 0.0


def _ema(data: np.ndarray, period: int) -> np.ndarray:
    alpha = 2 / (period + 1)
    result = np.zeros_like(data)
    result[0] = data[0]
    for i in range(1, len(data)):
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
    return result


def _kdj(close: np.ndarray, high: np.ndarray, low: np.ndarray, n: int = 9):
    k_arr = np.zeros(len(close))
    d_arr = np.zeros(len(close))
    j_arr = np.zeros(len(close))

    for i in range(n - 1, len(close)):
        hh = np.max(high[i - n + 1:i + 1])
        ll = np.min(low[i - n + 1:i + 1])
        rsv = (close[i] - ll) / (hh - ll) * 100 if hh != ll else 50.0

        if i == n - 1:
            k_arr[i] = 50
            d_arr[i] = 50
        else:
            k_arr[i] = 2 / 3 * k_arr[i - 1] + 1 / 3 * rsv
            d_arr[i] = 2 / 3 * d_arr[i - 1] + 1 / 3 * k_arr[i]
        j_arr[i] = 3 * k_arr[i] - 2 * d_arr[i]

    return k_arr[-1], d_arr[-1], j_arr[-1]


def _rsi(close: np.ndarray, period: int = 14) -> float:
    deltas = np.diff(close)
    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))