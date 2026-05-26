"""资讯面分析：新闻关键词利多/利空判断"""
import re

BULLISH_KEYWORDS = ["利好", "增长", "突破", "涨停", "收购", "合作", "业绩预增", "创新高", "机构看好", "回购", "增持", "扭亏"]
BEARISH_KEYWORDS = ["利空", "下跌", "减持", "跌停", "亏损", "违规", "业绩预减", "创新低", "退市", "被调查", "商誉减值", "质押"]


def analyze(news: list):
    """
    分析新闻利多/利空，给出 -100 ~ +100 评分
    参数:
        news: [{"title": str, "content": str, "time": str}, ...]
    返回:
        score, detail
    """
    if not news:
        return 0.0, {"bullish": 0, "bearish": 0, "ratio": 0}

    bull_count = 0
    bear_count = 0

    for item in news:
        text = (item.get("title", "") + item.get("content", ""))
        bull_hits = sum(1 for kw in BULLISH_KEYWORDS if kw in text)
        bear_hits = sum(1 for kw in BEARISH_KEYWORDS if kw in text)
        bull_count += bull_hits
        bear_count += bear_hits

    ratio = 0.0
    if bear_count > 0:
        ratio = bull_count / bear_count
    elif bull_count > 0:
        ratio = 999.0

    if ratio > 2:
        score = 100.0
    elif ratio > 1:
        score = 50.0
    elif ratio == 1:
        score = 0.0
    elif 0 < ratio < 1:
        score = -50.0
    else:
        score = -100.0 if bear_count > 0 else 0.0

    detail = {
        "bullish": bull_count,
        "bearish": bear_count,
        "ratio": round(ratio, 2),
    }
    return round(score, 2), detail