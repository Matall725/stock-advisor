"""RESTful API 路由"""
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from data.stock_data import get_kline, get_realtime_quote
from analysis.scorer import get_signal, _to_python
from config import KLINE_DAYS

router = APIRouter()


def _serialize_record(r: dict) -> dict:
    """将 DataFrame 记录中的 numpy / pandas / Timestamp 类型全部转为原生 Python"""
    out = {}
    for k, v in r.items():
        if isinstance(v, (pd.Timestamp,)):
            out[k] = v.isoformat()
        elif hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif isinstance(v, (np.integer,)):
            out[k] = int(v)
        elif isinstance(v, (np.floating, np.float64, np.float32)):
            out[k] = float(v)
        elif isinstance(v, np.ndarray):
            out[k] = v.tolist()
        elif pd.isna(v) if not isinstance(v, (list, dict, str, bool)) else False:
            out[k] = None
        else:
            out[k] = v
    return out


@router.get("/stock/search")
def stock_search(q: str = Query("", description="搜索关键字，可以是代码、名称或拼音")):
    try:
        from data.stock_data import search_stocks
        return search_stocks(q)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/signal")
def signal(code: str = Query(..., description="股票代码，如 000001")):
    try:
        return get_signal(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stock/info")
def stock_info(code: str = Query(..., description="股票代码")):
    try:
        return _to_python(get_realtime_quote(code))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stock/kline")
def stock_kline(
    code: str = Query(..., description="股票代码"),
    days: int = Query(default=KLINE_DAYS, ge=1, le=365),
):
    try:
        df      = get_kline(code, days)
        records = [_serialize_record(r) for r in df.to_dict(orient="records")]
        name    = ""
        try:
            q    = get_realtime_quote(code)
            name = q.get("name", "")
        except Exception:
            pass
        return {"code": code, "name": name, "days": days, "kline": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stock/detail")
def stock_detail(code: str = Query(..., description="股票代码")):
    try:
        return get_signal(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))