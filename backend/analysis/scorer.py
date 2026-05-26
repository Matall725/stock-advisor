"""综合评分引擎：四维度加权合成"""
import numpy as np
from config import DEFAULT_WEIGHTS, SIGNAL_THRESHOLDS, KLINE_DAYS
from analysis.technical import analyze as tech_analyze
from analysis.capital import analyze as cap_analyze
from analysis.sentiment import analyze as sent_analyze
from analysis.information import analyze as info_analyze
from analysis.valuation import analyze_valuation
from data.stock_data import (
    get_kline, get_fund_flow, get_realtime_quote,
    get_limit_stats, get_stock_news,
)


def _to_python(obj):
    """递归把 numpy 标量/数组转为原生 Python 类型，确保 JSON 可序列化"""
    if isinstance(obj, dict):
        return {k: _to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_python(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def get_signal(code: str) -> dict:
    """
    获取股票综合信号
    返回: {code, name, signal, color, total_score, breakdown, updated_at}
    """
    from datetime import datetime

    try:
        kline = get_kline(code, KLINE_DAYS)
    except Exception:
        kline = None

    try:
        fund_flow = get_fund_flow(code)
    except Exception:
        fund_flow = None

    try:
        quote = get_realtime_quote(code)
    except Exception:
        quote = {}

    try:
        limit_stats = get_limit_stats()
    except Exception:
        limit_stats = {}

    try:
        news = get_stock_news(code)
    except Exception:
        news = []

    tech_score, tech_detail = tech_analyze(kline) if kline is not None and not kline.empty else (0.0, {})
    cap_score, cap_detail   = cap_analyze(fund_flow) if fund_flow is not None and not fund_flow.empty else (0.0, {})
    sent_score, sent_detail = sent_analyze(kline, quote, limit_stats) if kline is not None else (0.0, {})
    info_score, info_detail = info_analyze(news)

    total_score = (
        tech_score * DEFAULT_WEIGHTS["technical"]
        + cap_score * DEFAULT_WEIGHTS["capital"]
        + info_score * DEFAULT_WEIGHTS["information"]
        + sent_score * DEFAULT_WEIGHTS["sentiment"]
    )
    total_score = round(float(total_score), 2)

    signal, color = _score_to_signal(total_score)

    current_price = float(quote.get("price", 0.0))
    val_res = analyze_valuation(kline, current_price, total_score)

    result = {
        "code": code,
        "name": quote.get("name", ""),
        "signal": signal,
        "color": color,
        "total_score": total_score,
        "breakdown": {
            "technical":   {"score": float(tech_score), "detail": _to_python(tech_detail)},
            "capital":     {"score": float(cap_score),  "detail": _to_python(cap_detail)},
            "sentiment":   {"score": float(sent_score), "detail": _to_python(sent_detail)},
            "information": {"score": float(info_score), "detail": _to_python(info_detail)},
        },
        "valuation": _to_python(val_res),
        "updated_at": datetime.now().isoformat(),
    }
    return result


def _score_to_signal(score: float) -> tuple:
    for threshold, signal, color in SIGNAL_THRESHOLDS:
        if score >= threshold:
            return signal, color
    return "强烈卖出", "#2e7d32"