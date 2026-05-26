"""估值与操作区间评估模块"""
import pandas as pd
import numpy as np

def analyze_valuation(kline: pd.DataFrame, current_price: float, total_score: float) -> dict:
    """
    根据历史K线、最新价格和综合评分，计算操作分类与价格区间评估
    """
    default_result = {
        "support": 0.0,
        "resistance": 0.0,
        "current_price": current_price,
        "operation_class": "暂无评级",
        "price_zone_desc": "未知区间",
        "buy_zone": [0.0, 0.0],
        "hold_zone": [0.0, 0.0],
        "sell_zone": [0.0, 0.0],
        "suggestion": "缺乏足够的历史交易数据，无法进行价格区间和操作建议评估。"
    }

    if kline is None or kline.empty:
        return default_result

    closes = kline["close"].dropna().tolist()
    if len(closes) < 10:
        return default_result

    # 1. 如果没有获取到实时价格，则使用最近一个交易日的收盘价作为最新价
    if not current_price or current_price <= 0:
        current_price = float(closes[-1])

    # 2. 计算支撑与阻力位
    # 采用 15% 和 85% 分位数以过滤极端噪音，使区间更平滑且具备统计意义
    support = round(float(np.percentile(closes, 15)), 2)
    resistance = round(float(np.percentile(closes, 85)), 2)
    
    # 极端防呆逻辑：如果计算出来的区间重叠，采用绝对最低/最高价
    if support >= resistance:
        support = round(float(min(closes)), 2)
        resistance = round(float(max(closes)), 2)
        
    if support >= resistance:
        # 如果依然重合（如一字板等极端无波动股票），人为制造点波幅
        support = round(support * 0.95, 2)
        resistance = round(resistance * 1.05, 2)

    # 3. 划分三个价格区间
    # 买入吸筹区：支撑位 ± 5%
    # 分批止盈区：压力位 ± 5%
    # 震荡持有区：两者之间
    buy_lower = round(support * 0.95, 2)
    buy_upper = round(support * 1.05, 2)
    
    sell_lower = round(resistance * 0.95, 2)
    sell_upper = round(resistance * 1.05, 2)
    
    # 确保区间不发生交错
    if buy_upper >= sell_lower:
        midpoint = (support + resistance) / 2
        buy_upper = round(midpoint * 0.95, 2)
        sell_lower = round(midpoint * 1.05, 2)

    # 4. 判断当前价格所处的状态
    if current_price <= buy_upper:
        price_zone_desc = "低位支撑区"
    elif current_price >= sell_lower:
        price_zone_desc = "高位压力区"
    else:
        price_zone_desc = "中枢震荡区"

    # 5. 结合综合系数与价格区间判定操作分类与文字建议
    # total_score 范围为 -100 ~ 100
    if total_score >= 60:  # 强烈买入信号
        if current_price <= buy_upper:
            operation_class = "强烈推荐买入（最佳建仓契机）"
            suggestion = f"当前股票综合得分为 {total_score} 分（表现极佳），且最新股价 ({current_price} 元) 已进入低位支撑区 ({buy_lower} - {buy_upper} 元)。多项指标显示安全边际极高，属于非常难得的左侧或右侧建仓点，建议分批积极布局。"
        elif current_price >= sell_lower:
            operation_class = "逢高分批止盈（切勿盲目追高）"
            suggestion = f"当前股票综合得分虽高达 {total_score} 分，但股价 ({current_price} 元) 已触及高位压力区 ({sell_lower} - {sell_upper} 元)。短期上行空间受限，追高风险极大。建议持有者逐步分批逢高止盈，空仓者耐心等待股价回调至支撑区。"
        else:
            operation_class = "偏多持有/逢回调分批吸纳"
            suggestion = f"股票综合得分 {total_score} 分表现强劲，目前价格 ({current_price} 元) 处于中枢震荡区。已有仓位建议继续持股待涨；若无仓位，不建议在此位置一次性满仓，可等后续回调至支撑线附近 ({buy_upper} 元以下) 逢低分批吸纳。"
            
    elif total_score >= 20:  # 买入信号
        if current_price <= buy_upper:
            operation_class = "逢低谨慎吸纳"
            suggestion = f"股票综合评分为 {total_score} 分，整体走势偏多，且最新股价 ({current_price} 元) 已回落至支撑区附近 ({buy_lower} - {buy_upper} 元)。此区间下行空间有限，具备较好防守性，可考虑建立轻仓或中仓，注意止损点设在 {buy_lower} 元下方。"
        elif current_price >= sell_lower:
            operation_class = "持股观望/谨防遇阻回调"
            suggestion = f"综合评分为偏多的 {total_score} 分，但最新股价 ({current_price} 元) 已接近压力区 ({sell_lower} - {sell_upper} 元)。考虑到阻力线抛压，当前性价比不高。建议已有仓位持股观望，切忌高位追加仓位。"
        else:
            operation_class = "持股待涨/静待方向选择"
            suggestion = f"综合评分为 {total_score} 分，多头仍占优势，股价处于中枢震荡区 ({current_price} 元)。建议继续持股，若计划加仓可等价格向下探底支撑区 {buy_upper} 元附近再行布局。"
            
    elif total_score <= -60:  # 强烈卖出信号
        operation_class = "强烈建议减仓/避险"
        if current_price <= buy_upper:
            suggestion = f"当前综合评分为 {total_score} 分，空头信号极强。尽管价格已来到支撑区 ({buy_lower} - {buy_upper} 元)，但由于趋势向下且动能严重衰竭，支撑位随时有被跌破的风险，绝非抄底时机。强烈建议持仓者止损离场或大幅减仓避险。"
        else:
            suggestion = f"当前综合评分为 {total_score} 分，下行趋势极其确立。股价 ({current_price} 元) 距离下方支撑仍有空间，破位概率极大。建议立即逢高或市价卖出减仓，保护本金安全。"
            
    elif total_score <= -20:  # 卖出信号
        if current_price >= sell_lower:
            operation_class = "逢高果断减仓/止损"
            suggestion = f"当前股票综合评分为 {total_score} 分，处于空头弱势。最新股价 ({current_price} 元) 运行到高位压力区 ({sell_lower} - {sell_upper} 元)，遭遇上方密集套牢盘和技术阻力。这是极佳的逢高减仓或出局良机，避免后续调整套牢。"
        elif current_price <= buy_upper:
            operation_class = "偏空观望/防范破位风险"
            suggestion = f"综合评分为偏空的 {total_score} 分，股价虽然在支撑位附近 ({buy_lower} - {buy_upper} 元)，但由于多头力量羸弱，盘整后破位向下的风险较大。建议空仓者绝对不要进场，持仓者密切关注支撑位得失，破位即止损。"
        else:
            operation_class = "逢反弹分批减持"
            suggestion = f"综合评分为偏空的 {total_score} 分，股价在中枢区间震荡。建议利用盘中冲高或反弹行情，分批分步骤降低持仓比例，耐心等待系统性企稳评分走高。"
            
    else:  # -20 < total_score < 20，中性信号
        if current_price <= buy_upper:
            operation_class = "低位震荡盘整/轻仓试探"
            suggestion = f"当前综合评分为中性 ({total_score} 分)，多空力量均衡，价格处于支撑区 ({buy_lower} - {buy_upper} 元)。此处可能存在小幅技术性反弹，可配合网格交易或在支撑位附近极轻仓尝试低吸，若日K线收盘价跌破 {buy_lower} 元则严格止损。"
        elif current_price >= sell_lower:
            operation_class = "压力位遇阻/分批锁利"
            suggestion = f"当前综合评分为中性 ({total_score} 分)，且最新价 ({current_price} 元) 位于压力区 ({sell_lower} - {sell_upper} 元) 附近，向上突破需要更大的成交量配合。建议冲高受阻时适当逢高减磅，锁定已有利润，静待方向明朗。"
        else:
            operation_class = "区间无趋势震荡/多看少动"
            suggestion = f"综合评分为中性的 {total_score} 分，代表当前无明显趋势，价格 ({current_price} 元) 运行在支撑与压力的中段。操作性价比极低，建议多看少动，持股观望或空仓等待多空分出胜负。"

    return {
        "support": support,
        "resistance": resistance,
        "current_price": current_price,
        "operation_class": operation_class,
        "price_zone_desc": price_zone_desc,
        "buy_zone": [buy_lower, buy_upper],
        "hold_zone": [buy_upper, sell_lower],
        "sell_zone": [sell_lower, sell_upper],
        "suggestion": suggestion
    }
