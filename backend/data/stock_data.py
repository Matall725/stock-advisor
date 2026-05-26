"""数据获取模块：通过 AKShare 获取 A 股行情数据"""
import logging
import time
import akshare as ak
import pandas as pd
import numpy as np
from cache.manager import get as cache_get, put as cache_put

logger = logging.getLogger(__name__)

KLINE_CACHE_TTL = 4 * 60 * 60
QUOTE_CACHE_TTL = 5 * 60
FUND_CACHE_TTL = 4 * 60 * 60
NEWS_CACHE_TTL = 2 * 60 * 60


def _call_with_retry(func, *args, retries=3, delay=1.0, backoff=2.0, **kwargs):
    """
    带重试和指数退避地调用 AKShare 接口，避免因为瞬间网络抖动/被限流导致请求直接失败。
    """
    curr_delay = delay
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"调用 {func.__name__} 失败，已达最大重试次数 {retries}。错误: {e}")
                raise
            logger.warning(f"调用 {func.__name__} 失败 (尝试 {attempt + 1}/{retries}): {e}，将在 {curr_delay} 秒后重试...")
            time.sleep(curr_delay)
            curr_delay *= backoff


def _clean_code(code: str) -> str:
    cleaned = code.strip().replace(".SZ", "").replace(".SH", "")
    return resolve_stock_code(cleaned)


def _market_prefix(code: str) -> str:
    if code.startswith(("0", "3")):
        return "sz"
    return "sh"


def get_kline(code: str, days: int = 120) -> pd.DataFrame:
    code = _clean_code(code)
    cache_key = f"kline_{code}_{days}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    start = _offset_date(days)
    end = _today()

    try:
        df = _call_with_retry(ak.stock_zh_a_hist, symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "收盘": "close",
            "最高": "high", "最低": "low", "成交量": "volume",
            "成交额": "amount", "振幅": "amplitude", "涨跌幅": "pct_change",
            "涨跌额": "change", "换手率": "turnover",
        })
    except Exception as e:
        logger.warning(f"stock_zh_a_hist 失败，尝试 stock_zh_a_daily: {e}")
        symbol = f"{_market_prefix(code)}{code}"
        df = _call_with_retry(ak.stock_zh_a_daily, symbol=symbol, start_date=start, end_date=end, adjust="qfq")
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] >= cutoff]

    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "close", "high", "low", "volume", "amount", "turnover"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values("date").tail(days).reset_index(drop=True)
    cache_put(cache_key, df, KLINE_CACHE_TTL)
    return df



def get_realtime_quote(code: str) -> dict:
    code = _clean_code(code)
    cache_key = f"quote_{code}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    # 尝试 1: stock_bid_ask_em
    try:
        df = _call_with_retry(ak.stock_bid_ask_em, symbol=code)
        data = dict(zip(df["item"], df["value"]))
        result = _parse_quote_dict(code, data)
        cache_put(cache_key, result, QUOTE_CACHE_TTL)
        return result
    except Exception as e:
        logger.warning(f"stock_bid_ask_em 失败: {e}")

    # 尝试 2: stock_zh_a_spot_em (全量快照中筛选)
    try:
        df = _call_with_retry(ak.stock_zh_a_spot_em)
        row = df[df["代码"] == code]
        if not row.empty:
            r = row.iloc[0]
            result = {
                "code": code,
                "name": str(r.get("名称", "")),
                "price": _safe_float(r.get("最新价")),
                "pct_change": _safe_float(r.get("涨跌幅")),
                "change": _safe_float(r.get("涨跌额")),
                "volume": int(_safe_float(r.get("成交量"))),
                "amount": _safe_float(r.get("成交额")),
                "high": _safe_float(r.get("最高")),
                "low": _safe_float(r.get("最低")),
                "open": _safe_float(r.get("今开")),
                "pre_close": _safe_float(r.get("昨收")),
                "turnover": _safe_float(r.get("换手率")),
                "volume_ratio": _safe_float(r.get("量比")),
            }
            cache_put(cache_key, result, QUOTE_CACHE_TTL)
            return result
    except Exception as e:
        logger.warning(f"stock_zh_a_spot_em 失败: {e}")

    # 尝试 3: K线降级
    logger.info(f"实时行情全部失败，从K线降级 code={code}")
    return _quote_from_kline(code)


def _parse_quote_dict(code: str, data: dict) -> dict:
    name = _get_stock_name(code)
    return {
        "code": code,
        "name": name,
        "price": _safe_float(data.get("最新价")),
        "pct_change": _safe_float(data.get("涨跌幅")),
        "change": _safe_float(data.get("涨跌额")),
        "volume": int(_safe_float(data.get("成交量"))),
        "amount": _safe_float(data.get("成交额")),
        "high": _safe_float(data.get("最高")),
        "low": _safe_float(data.get("最低")),
        "open": _safe_float(data.get("今开")),
        "pre_close": _safe_float(data.get("昨收")),
        "turnover": _safe_float(data.get("换手率")),
        "volume_ratio": _safe_float(data.get("量比")),
    }


def _quote_from_kline(code: str) -> dict:
    try:
        df = get_kline(code, 10)
        if df.empty:
            raise ValueError("K线数据为空")
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        name = _get_stock_name(code)
        price = float(last["close"])
        pre_close = float(prev["close"])
        result = {
            "code": code,
            "name": name,
            "price": price,
            "pct_change": round((price - pre_close) / pre_close * 100, 2) if pre_close else 0,
            "change": round(price - pre_close, 2),
            "volume": int(float(last.get("volume", 0))),
            "amount": float(last.get("amount", 0)),
            "high": float(last["high"]),
            "low": float(last["low"]),
            "open": float(last["open"]),
            "pre_close": pre_close,
            "turnover": float(last.get("turnover", 0)) * 100,
            "volume_ratio": 0.0,
        }
        cache_put(f"quote_{code}", result, QUOTE_CACHE_TTL)
        return result
    except Exception as e:
        logger.error(f"K线降级也失败 code={code}: {e}")
        raise


_stock_name_cache = {}
_stock_name_loaded = False
_stock_name_map = {}
_stock_name_to_code = {}
_stock_initials_to_codes = {}
_stock_code_to_initials = {}


def _load_stock_name_map():
    """懒加载全量股票名称映射，生成中文名称、代码与拼音首字母反查索引，避免重复请求"""
    global _stock_name_loaded, _stock_name_map, _stock_name_to_code, _stock_initials_to_codes, _stock_code_to_initials
    if _stock_name_loaded:
        return
    try:
        from pypinyin import pinyin, Style
        df = _call_with_retry(ak.stock_info_a_code_name)
        new_name_map = {}
        new_name_to_code = {}
        new_initials_to_codes = {}
        new_code_to_initials = {}
        for _, row in df.iterrows():
            code_str = str(row["code"]).strip().zfill(6)
            name_str = str(row["name"]).strip()
            new_name_map[code_str] = name_str
            new_name_to_code[name_str] = code_str
            
            # 计算拼音首字母
            try:
                initials = "".join([item[0] for item in pinyin(name_str, style=Style.FIRST_LETTER) if item]).upper()
                if initials:
                    if initials not in new_initials_to_codes:
                        new_initials_to_codes[initials] = []
                    new_initials_to_codes[initials].append(code_str)
                    new_code_to_initials[code_str] = initials
            except Exception as e:
                logger.warning(f"计算股票 {name_str} 拼音缩写失败: {e}")
                
        _stock_name_map = new_name_map
        _stock_name_to_code = new_name_to_code
        _stock_initials_to_codes = new_initials_to_codes
        _stock_code_to_initials = new_code_to_initials
        _stock_name_loaded = True
        logger.info(f"已加载 {len(_stock_name_map)} 只股票名称与拼音首字母索引")
    except Exception as e:
        logger.warning(f"加载股票名称映射失败: {e}")


def resolve_stock_code(query: str) -> str:
    """
    解析股票代码、名称或拼音缩写为标准 6 位股票代码。
    支持：
    1. 标准6位代码 (如 600519)
    2. 完整股票名称 (如 贵州茅台)
    3. 拼音缩写 (如 GZMT, gzmt)
    4. 部分股票名称模糊匹配 (如 茅台 -> 600519)
    5. 部分拼音缩写模糊匹配 (如 GZM -> 600519)
    """
    if not query:
        return ""
    
    query = query.strip()
    
    # 如果是6位数字，直接返回
    if query.isdigit() and len(query) == 6:
        return query
        
    # 确保加载了映射表
    if not _stock_name_loaded:
        _load_stock_name_map()
        
    # 1. 尝试精确匹配股票代码
    if query in _stock_name_map:
        return query
        
    # 2. 尝试精确匹配股票名称
    if query in _stock_name_to_code:
        return _stock_name_to_code[query]
        
    # 3. 尝试精确匹配拼音缩写
    query_upper = query.upper()
    if query_upper in _stock_initials_to_codes:
        return _stock_initials_to_codes[query_upper][0]
        
    # 4. 尝试模糊匹配股票名称 (子串匹配)
    name_matches = []
    for name, code in _stock_name_to_code.items():
        if query in name:
            name_matches.append((name, code))
    if name_matches:
        # 优先匹配以查询词开头的股票，其次按名字长度升序排序
        name_matches.sort(key=lambda x: (not x[0].startswith(query), len(x[0])))
        return name_matches[0][1]
        
    # 5. 尝试模糊匹配拼音缩写 (前缀匹配)
    initials_matches = []
    for initials, codes in _stock_initials_to_codes.items():
        if query_upper in initials:
            initials_matches.append((initials, codes[0]))
    if initials_matches:
        initials_matches.sort(key=lambda x: (not x[0].startswith(query_upper), len(x[0])))
        return initials_matches[0][1]
        
    # 如果全都不匹配，清洗后缀后再判断
    cleaned = query.replace(".SZ", "").replace(".SH", "")
    if cleaned.isdigit() and len(cleaned) == 6:
        return cleaned
        
    return query


def search_stocks(query: str, limit: int = 10) -> list:
    """
    根据代码、中文名称或拼音缩写模糊搜索股票，返回候选匹配列表。
    返回格式: [{"code": "600519", "name": "贵州茅台", "pinyin": "GZMT"}]
    """
    if not query:
        return []
        
    query = query.strip()
    query_upper = query.upper()
    
    # 确保已加载映射
    if not _stock_name_loaded:
        _load_stock_name_map()
        
    results = []
    seen_codes = set()
    
    # 1. 优先匹配以查询词开头的股票代码
    for code, name in _stock_name_map.items():
        if code.startswith(query):
            results.append({"code": code, "name": name, "pinyin": _stock_code_to_initials.get(code, "")})
            seen_codes.add(code)
            if len(results) >= limit:
                break
                
    # 2. 匹配拼音首字母缩写前缀
    if len(results) < limit:
        for initials, codes in _stock_initials_to_codes.items():
            if initials.startswith(query_upper):
                for code in codes:
                    if code not in seen_codes:
                        results.append({"code": code, "name": _stock_name_map[code], "pinyin": initials})
                        seen_codes.add(code)
                        if len(results) >= limit:
                            break
            if len(results) >= limit:
                break
                
    # 3. 匹配中文名称中包含的
    if len(results) < limit:
        for name, code in _stock_name_to_code.items():
            if code not in seen_codes and query in name:
                results.append({"code": code, "name": name, "pinyin": _stock_code_to_initials.get(code, "")})
                seen_codes.add(code)
                if len(results) >= limit:
                    break
                    
    # 4. 匹配拼音缩写包含的 (非前缀)
    if len(results) < limit:
        for initials, codes in _stock_initials_to_codes.items():
            if query_upper in initials:
                for code in codes:
                    if code not in seen_codes:
                        results.append({"code": code, "name": _stock_name_map[code], "pinyin": initials})
                        seen_codes.add(code)
                        if len(results) >= limit:
                            break
            if len(results) >= limit:
                break
                
    return results



def _get_stock_name(code: str) -> str:
    if code in _stock_name_cache:
        return _stock_name_cache[code]
    if not _stock_name_loaded:
        _load_stock_name_map()
    name = _stock_name_map.get(code, "")
    if name:
        _stock_name_cache[code] = name
    return name


def get_fund_flow(code: str) -> pd.DataFrame:
    code = _clean_code(code)
    cache_key = f"fund_flow_{code}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        df = _call_with_retry(ak.stock_individual_fund_flow, stock=code, market=_market_prefix(code))
        df = _rename_fund_flow_columns(df)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        cache_put(cache_key, df, FUND_CACHE_TTL)
        return df
    except Exception as e:
        logger.warning(f"获取资金流向失败 code={code}: {e}")
        return pd.DataFrame()


def _rename_fund_flow_columns(df: pd.DataFrame) -> pd.DataFrame:
    """兼容不同版本 AKShare 的资金流向列名"""
    rename_map = {
        "日期": "date",
        "主力净流入-净额": "main_net",
        "主力净流入-净占比": "main_ratio",
        "超大单净流入-净额": "super_large_net",
        "超大单净流入-净占比": "super_large_ratio",
        "大单净流入-净额": "large_net",
        "大单净流入-净占比": "large_ratio",
        "中单净流入-净额": "medium_net",
        "中单净流入-净占比": "medium_ratio",
        "小单净流入-净额": "small_net",
        "小单净流入-净占比": "small_ratio",
    }
    existing = {k: v for k, v in rename_map.items() if k in df.columns}
    if existing:
        df = df.rename(columns=existing)
    return df


def get_limit_stats() -> dict:
    cache_key = "limit_stats"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    today = _today()
    try:
        zt = _call_with_retry(ak.stock_zt_pool_em, date=today)
    except Exception as e:
        logger.warning(f"stock_zt_pool_em 失败: {e}")
        zt = None
    try:
        dt = _call_with_retry(ak.stock_zt_pool_dtgc_em, date=today)
    except Exception as e:
        logger.warning(f"stock_zt_pool_dtgc_em 失败: {e}")
        dt = None

    if zt is not None and dt is not None:
        result = {
            "zt_count": len(zt),
            "dt_count": len(dt),
            "zt_ratio": len(zt) / max(len(dt), 1),
        }
        cache_put(cache_key, result, QUOTE_CACHE_TTL)
        return result

    logger.warning("涨跌停统计部分数据缺失，使用默认值")
    return {"zt_count": 0, "dt_count": 0, "zt_ratio": 1.0}


def get_stock_news(code: str) -> list:
    code = _clean_code(code)
    cache_key = f"news_{code}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        df = _call_with_retry(ak.stock_news_em, symbol=code)
        news_list = []
        title_col = next((c for c in ["新闻标题", "标题", "title"] if c in df.columns), "title")
        content_col = next((c for c in ["新闻内容", "内容", "content"] if c in df.columns), "content")
        time_col = next((c for c in ["发布时间", "时间", "time"] if c in df.columns), "time")
        for _, row in df.head(20).iterrows():
            news_list.append({
                "title": str(row.get(title_col, "")),
                "content": str(row.get(content_col, "")),
                "time": str(row.get(time_col, "")),
            })
        cache_put(cache_key, news_list, NEWS_CACHE_TTL)
        return news_list
    except Exception as e:
        logger.warning(f"获取新闻失败 code={code}: {e}")
        return []


def _offset_date(days: int) -> str:
    return (pd.Timestamp.now() - pd.Timedelta(days=days)).strftime("%Y%m%d")


def _today() -> str:
    return pd.Timestamp.now().strftime("%Y%m%d")


def _safe_float(val) -> float:
    try:
        if isinstance(val, (int, float)):
            return float(val)
        if val is None or val == "-" or val == "":
            return 0.0
        return float(val)
    except (ValueError, TypeError):
        return 0.0