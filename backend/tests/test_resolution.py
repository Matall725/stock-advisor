"""股票代码/名称/拼音缩写解析模块单元测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from unittest.mock import patch
import data.stock_data

@patch('data.stock_data._call_with_retry')
def test_stock_code_resolution(mock_call):
    # 模拟股票基础数据
    mock_df = pd.DataFrame([
        {"code": 600519, "name": "贵州茅台"},
        {"code": 1, "name": "平安银行"},
        {"code": "300750", "name": "宁德时代"},
    ])
    mock_call.return_value = mock_df
    
    # 重置加载状态，强制使用 mock 数据重新加载
    data.stock_data._stock_name_loaded = False
    data.stock_data._stock_name_map = {}
    data.stock_data._stock_name_to_code = {}
    data.stock_data._stock_initials_to_codes = {}
    
    # 1. 验证标准6位代码
    assert data.stock_data.resolve_stock_code("600519") == "600519"
    assert data.stock_data.resolve_stock_code("000001") == "000001"
    
    # 2. 验证中文全称匹配
    assert data.stock_data.resolve_stock_code("贵州茅台") == "600519"
    assert data.stock_data.resolve_stock_code("平安银行") == "000001"
    
    # 3. 验证拼音缩写精确匹配 (大小写无关)
    assert data.stock_data.resolve_stock_code("GZMT") == "600519"
    assert data.stock_data.resolve_stock_code("gzmt") == "600519"
    assert data.stock_data.resolve_stock_code("payh") == "000001"
    assert data.stock_data.resolve_stock_code("NDSD") == "300750"
    
    # 4. 验证中文名称子串模糊匹配
    assert data.stock_data.resolve_stock_code("茅台") == "600519"
    assert data.stock_data.resolve_stock_code("宁德") == "300750"
    
    # 5. 验证拼音前缀模糊匹配
    assert data.stock_data.resolve_stock_code("GZM") == "600519"
    assert data.stock_data.resolve_stock_code("ND") == "300750"
    
    # 6. 验证后缀清洗匹配
    assert data.stock_data.resolve_stock_code("600519.SH") == "600519"
    assert data.stock_data.resolve_stock_code("000001.SZ") == "000001"
    
    # 7. 验证未知内容兜底返回原内容
    assert data.stock_data.resolve_stock_code("UNKNOWN") == "UNKNOWN"


@patch('data.stock_data._call_with_retry')
def test_stock_search(mock_call):
    # 模拟股票基础数据
    mock_df = pd.DataFrame([
        {"code": 600519, "name": "贵州茅台"},
        {"code": 1, "name": "平安银行"},
        {"code": "300750", "name": "宁德时代"},
    ])
    mock_call.return_value = mock_df
    
    # 重置并重新加载
    data.stock_data._stock_name_loaded = False
    data.stock_data._stock_name_map = {}
    data.stock_data._stock_name_to_code = {}
    data.stock_data._stock_initials_to_codes = {}
    data.stock_data._stock_code_to_initials = {}
    
    # 1. 搜索代码前缀
    res1 = data.stock_data.search_stocks("600")
    assert len(res1) == 1
    assert res1[0]["code"] == "600519"
    assert res1[0]["name"] == "贵州茅台"
    assert res1[0]["pinyin"] == "GZMT"
    
    # 2. 搜索拼音首字母前缀
    res2 = data.stock_data.search_stocks("PA")
    assert len(res2) == 1
    assert res2[0]["code"] == "000001"
    assert res2[0]["pinyin"] == "PAYH"
    
    # 3. 搜索中文子串
    res3 = data.stock_data.search_stocks("时代")
    assert len(res3) == 1
    assert res3[0]["code"] == "300750"
    
    # 4. 搜索空值
    assert data.stock_data.search_stocks("") == []

