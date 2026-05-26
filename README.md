# 股票顾问 - 操作提示系统 (Stock Advisor)

基于四维度量化分析模型与估值评估体系的 A 股股票操作提示系统。本项目采用前后端分离架构，后端基于 FastAPI 提供高效的 API 服务与数据计算，前端基于 Vue 3 + Vite + ECharts 提供直观的可视化交互界面。

---

## 🌟 核心特性

### 1. 四维度量化评分模型 (权重占比)
系统通过对个股多维度数据的实时抓取与计算，生成 -100 至 +100 的综合评分：
- 📈 **技术面 (40%)**：基于历史 K 线计算 MA 均线多空排列、MACD 金叉/死叉及柱状线趋势、KDJ 超买超卖区间、RSI 强弱指标。
- 💰 **资金面 (25%)**：分析近 5 日主力资金净流入/流出趋势，以及大单/超大单资金净额占比。
- 📰 **资讯面 (20%)**：实时抓取个股近期新闻，基于利多/利空关键词词典进行情感倾向评分。
- 🔥 **情绪面 (15%)**：结合全市场涨跌停比、个股换手率偏离度（对比 5 日均值）、实时量比进行热度评估。

### 2. 估值与支撑阻力评估
- **支撑位与阻力位**：基于历史 K 线收盘价的 15% 和 85% 分位数计算，过滤极端噪音，具备统计学意义。
- **三段式价格区间**：自动划分 **买入吸筹区**（支撑位±5%）、**分批止盈区**（压力位±5%）和**中枢震荡区**（两者之间）。
- **智能操作建议**：结合综合评分与当前股价所处区间，输出 12 种细分操作分类（如“强烈推荐买入（最佳建仓契机）”、“逢高分批止盈（切勿盲目追高）”等）及详细的文字指导。

### 3. 五级操作信号输出
根据综合评分自动映射操作信号及主题色：
- 🔴 **强烈买入** (评分 $\ge 60$)：深红色 (`#c62828`)
- 🟢 **买入** (评分 $\ge 20$)：绿色 (`#4caf50`)
- ⚪ **持有** (评分 $\ge -20$)：灰色 (`#9e9e9e`)
- 🟡 **卖出** (评分 $\ge -60$)：浅红色 (`#ef5350`)
- ⚫ **强烈卖出** (评分 $< -60$)：深红色/黑色 (`#b71c1c`)

### 4. 现代化前端交互
- **智能搜索**：支持股票代码（如 `000001`）、中文名称（如 `平安银行`）或拼音首字母缩写（如 `payh`）的模糊匹配与防抖搜索。
- **可视化图表**：
  - **雷达图**：直观展示技术面、资金面、资讯面、情绪面四维得分。
  - **K线图**：展示日 K 线，叠加 MA5/MA10/MA20 均线，底部配以成交量柱状图，支持无级缩放与拖拽。
  - **估值仪表盘**：直观呈现支撑位、阻力位及当前股价所处位置。

### 5. 高效的数据缓存与防限流
- 整合 **DiskCache** 缓存库，基于 SQLite 磁盘缓存，无需部署额外的 Redis 服务。
- 针对不同数据源设置差异化缓存 TTL（K线 4h、实时行情 5min、资金流向 4h、新闻 2h），并支持指数退避重试与降级机制，确保系统在高频访问下的稳定性。

---

## 🛠️ 技术栈

| 层级 | 关键技术 | 版本 | 用途 |
|------|------|------|------|
| **后端** | FastAPI | 0.115.0 | 高性能异步 Web API 框架 |
| | Uvicorn | 0.30.0 | ASGI 服务器 |
| | AKShare | $\ge$ 1.14.0 | A股金融数据接口源 |
| | Pandas + NumPy | $\ge$ 2.0.0 | 数据清洗、技术指标计算与分位数统计 |
| | DiskCache | $\ge$ 5.6.0 | 磁盘缓存管理 |
| **前端** | Vue 3 | - | 渐进式 JavaScript 框架 |
| | Vite | - | 极速前端构建工具 |
| | ECharts | - | 数据可视化图表库 |
| | Axios | - | 异步 HTTP 请求客户端 |

---

## 📂 项目结构

```
stock-advisor/
├── backend/                       # 后端服务
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 全局配置（权重、阈值、缓存路径）
│   ├── requirements.txt           # Python 依赖包清单
│   ├── cache/                     # 缓存模块
│   │   └── manager.py             # 缓存读写与管理
│   ├── data/                      # 数据获取模块
│   │   └── stock_data.py          # 封装 AKShare 接口（带重试与降级）
│   ├── analysis/                  # 四维度分析与估值引擎
│   │   ├── technical.py           # 技术面分析 (MA, MACD, KDJ, RSI)
│   │   ├── capital.py             # 资金面分析 (主力流向趋势、大单占比)
│   │   ├── sentiment.py           # 情绪面分析 (涨跌停比、换手率偏离度)
│   │   ├── information.py         # 资讯面分析 (新闻情感关键词匹配)
│   │   ├── valuation.py           # 估值与支撑阻力评估
│   │   └── scorer.py              # 综合评分与信号映射
│   ├── api/                       # API 路由模块
│   │   └── routes.py              # RESTful API 路由定义
│   └── tests/                     # 单元测试
│       ├── test_analysis.py       # 分析模块测试
│       ├── test_valuation.py      # 估值模块测试
│       └── test_resolution.py     # 股票代码解析测试
├── frontend/                      # 前端项目
│   ├── package.json               # Node.js 依赖配置
│   ├── vite.config.js             # Vite 配置（包含 API 代理）
│   ├── index.html                 # 页面入口
│   └── src/
│       ├── main.js                # Vue 应用入口
│       ├── App.vue                # 根组件
│       ├── api/
│       │   └── index.js           # Axios 接口封装
│       ├── components/
│       │   ├── StockSearch.vue    # 股票搜索组件（防抖、模糊匹配）
│       │   ├── SignalCard.vue     # 信号与得分展示卡片
│       │   ├── ScoreRadar.vue     # 四维度雷达图组件
│       │   ├── KlineChart.vue     # K线与成交量图表组件
│       │   └── ValuationCard.vue  # 估值与操作建议展示卡片
│       └── views/
│           └── Home.vue           # 主页面布局
├── docs/                          # 项目文档
│   ├── plan.md                    # 项目计划
│   ├── features.md                # 功能设计文档
│   └── memory.md                  # 开发构建记忆
├── start.bat                      # Windows 批处理一键启动脚本
└── start.ps1                      # Windows PowerShell 一键启动脚本
```

---

## 🚀 快速开始

### 准备工作
- 安装 Python 3.8 或更高版本
- 安装 Node.js 16 或更高版本（包含 npm）

### 方式一：一键启动 (Windows)
双击运行项目根目录下的 `start.bat`，或者在 PowerShell 中执行：
```powershell
.\start.ps1
```
该脚本会自动：
1. 创建 Python 虚拟环境并安装后端依赖。
2. 安装前端 Node 依赖。
3. 启动 FastAPI 后端服务 (`http://127.0.0.1:8000`)。
4. 启动 Vite 前端开发服务器 (`http://localhost:5173`)。
5. 自动在浏览器中打开前端页面。

---

### 方式二：手动分步启动

#### 1. 启动后端服务
```bash
cd backend
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
# 安装依赖
pip install -r requirements.txt
# 启动服务
python main.py
```
*后端服务将运行在 `http://127.0.0.1:8000`，您可以通过 `http://127.0.0.1:8000/docs` 查看 Swagger 交互式 API 文档。*

#### 2. 启动前端服务
```bash
cd frontend
# 安装依赖
npm install
# 启动开发服务器
npm run dev
```
*前端服务将运行在 `http://localhost:5173`。*

---

## 📡 API 接口说明

### 1. 股票搜索
* **路径**：`/api/stock/search`
* **方法**：`GET`
* **参数**：`q` (string, 必须) - 搜索关键字（代码、名称或拼音首字母，如 `600519`、`贵州茅台`、`gzmt`）
* **返回示例**：
```json
[
  {
    "code": "600519",
    "name": "贵州茅台",
    "pinyin": "GZMT"
  }
]
```

### 2. 获取综合信号与估值分析
* **路径**：`/api/signal` 或 `/api/stock/detail`
* **方法**：`GET`
* **参数**：`code` (string, 必须) - 6位股票代码
* **返回示例**：
```json
{
  "code": "000001",
  "name": "平安银行",
  "signal": "买入",
  "color": "#4caf50",
  "total_score": 32.5,
  "breakdown": {
    "technical": {
      "score": 45.0,
      "detail": {
        "ma_trend": "多头排列",
        "macd_signal": "金叉",
        "kdj_status": "正常",
        "rsi_value": 42.5
      }
    },
    "capital": {
      "score": 30.0,
      "detail": {
        "net_flow_5d": 12500.0,
        "large_order_ratio": 0.15
      }
    },
    "sentiment": {
      "score": 15.0,
      "detail": {
        "zt_dt_ratio": 1.2,
        "turnover_deviation": 0.3,
        "volume_ratio": 1.1
      }
    },
    "information": {
      "score": 20.0,
      "detail": {
        "news_count": 12,
        "positive_count": 8,
        "negative_count": 2
      }
    }
  },
  "valuation": {
    "support": 10.50,
    "resistance": 12.80,
    "current_price": 11.20,
    "operation_class": "偏多持有/逢回调分批吸纳",
    "price_zone_desc": "中枢震荡区",
    "buy_zone": [9.98, 11.03],
    "hold_zone": [11.03, 12.16],
    "sell_zone": [12.16, 13.44],
    "suggestion": "股票综合得分 32.5 分表现强劲，目前价格 (11.2 元) 处于中枢震荡区。已有仓位建议继续持股待涨；若无仓位，不建议在此位置一次性满仓，可等后续回调至支撑线附近 (11.03 元以下) 逢低分批吸纳。"
  },
  "updated_at": "2026-05-26T20:00:00.000000"
}
```

### 3. 获取实时行情
* **路径**：`/api/stock/info`
* **方法**：`GET`
* **参数**：`code` (string, 必须) - 6位股票代码
* **返回示例**：
```json
{
  "code": "000001",
  "name": "平安银行",
  "price": 11.20,
  "pct_change": 1.54,
  "change": 0.17,
  "volume": 450000,
  "amount": 5040000.0,
  "high": 11.30,
  "low": 11.05,
  "open": 11.10,
  "pre_close": 11.03,
  "turnover": 0.23,
  "volume_ratio": 1.15
}
```

### 4. 获取K线数据
* **路径**：`/api/stock/kline`
* **方法**：`GET`
* **参数**：
  - `code` (string, 必须) - 6位股票代码
  - `days` (int, 可选) - 获取K线的天数，默认 120 天，范围 1-365
* **返回示例**：
```json
{
  "code": "000001",
  "name": "平安银行",
  "days": 120,
  "kline": [
    {
      "date": "2026-05-25T00:00:00",
      "open": 11.00,
      "close": 11.03,
      "high": 11.15,
      "low": 10.95,
      "volume": 380000,
      "amount": 4180000.0,
      "turnover": 0.19
    }
  ]
}
```

---

## 🧪 单元测试

后端提供了完善的单元测试，覆盖了指标计算、估值逻辑和股票代码解析等核心功能。
在后端目录下运行以下命令执行测试：
```bash
# 激活虚拟环境后运行
pytest tests/
```

---

## ⚖️ 免责声明

1. 本系统提供的所有股票分析评分、操作信号及价格区间建议均基于历史公开数据和特定数学模型计算得出，**不构成任何实质性的投资建议或操作指引**。
2. 股市有风险，投资需谨慎。用户因参考本系统数据或建议进行投资决策所导致的任何直接或间接损失，**本系统及开发者不承担任何法律责任**。
