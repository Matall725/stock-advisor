# 股票顾问系统 - 项目计划文档

## 一、项目概述

### 1.1 项目名称
股票操作提示系统（Stock Advisor）

### 1.2 项目目标
构建一个基于四维度分析模型的A股股票操作提示系统，为用户提供买卖信号建议。

### 1.3 核心功能
- **四维度分析**：技术面（40%）、资金面（25%）、资讯面（20%）、情绪面（15%）
- **五级信号输出**：强烈买入 / 买入 / 持有 / 卖出 / 强烈卖出
- **综合评分**：-100 ~ +100 分值映射到五级信号

### 1.4 技术栈
| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 后端框架 | FastAPI | 0.115.0 | Web API 服务 |
| ASGI服务器 | Uvicorn | 0.30.0 | 异步HTTP服务器 |
| 数据源 | AKShare | >=1.14.0 | A股金融数据获取 |
| 数据处理 | Pandas + NumPy | >=2.0.0 / >=1.24.0 | 数据分析计算 |
| 缓存 | DiskCache | >=5.6.0 | 磁盘缓存 |
| 前端框架 | Vue 3 + Vite | - | 用户界面 |
| 图表库 | ECharts | - | K线图、雷达图 |

---

## 二、项目结构规划

```
stock-advisor/
├── docs/                          # 项目文档
│   ├── plan.md                    # 本文档（项目计划）
│   ├── memory.md                  # 构建记忆（记录每步进展）
│   └── features.md                # 功能文档（文件说明）
├── backend/                       # 后端服务
│   ├── main.py                    # ✅ FastAPI 入口
│   ├── config.py                  # ✅ 系统配置
│   ├── requirements.txt           # ✅ 依赖清单
│   ├── cache/                     # 缓存模块
│   │   ├── __init__.py
│   │   └── manager.py             # ✅ 缓存管理器
│   ├── data/                      # 数据获取模块
│   │   ├── __init__.py
│   │   └── stock_data.py          # 🆕 AKShare 数据获取
│   ├── analysis/                  # 分析模块
│   │   ├── __init__.py
│   │   ├── technical.py           # 🆕 技术面分析
│   │   ├── capital.py             # 🆕 资金面分析
│   │   ├── sentiment.py           # 🆕 情绪面分析
│   │   ├── information.py         # 🆕 资讯面分析
│   │   └── scorer.py              # 🆕 综合评分引擎
│   └── api/                       # API路由模块
│       ├── __init__.py
│       └── routes.py              # 🆕 RESTful 路由
└── frontend/                      # 前端项目
    ├── package.json               # 🆕 Vue 3 依赖
    ├── vite.config.js             # 🆕 Vite 配置
    ├── index.html                 # 🆕 HTML 入口
    └── src/
        ├── main.js                # 🆕 Vue 入口
        ├── App.vue                # 🆕 根组件
        ├── api/
        │   └── index.js           # 🆕 Axios 封装
        ├── components/
        │   ├── StockSearch.vue    # 🆕 股票搜索
        │   ├── SignalCard.vue     # 🆕 信号卡片
        │   ├── ScoreRadar.vue     # 🆕 雷达图
        │   └── KlineChart.vue     # 🆕 K线图
        └── views/
            └── Home.vue           # 🆕 主页面
```

---

## 三、分阶段实施计划

### 阶段 1：后端核心模块

#### 1.1 数据获取模块 (`data/stock_data.py`)
**目标**：封装 AKShare 数据接口，提供统一的数据获取函数

**功能清单**：
| 函数名 | 功能 | 数据源 | 返回格式 |
|--------|------|--------|----------|
| `get_kline(code, days)` | 获取日K线数据 | `stock_zh_a_hist` | DataFrame |
| `get_fund_flow(code)` | 获取资金流向 | `stock_individual_fund_flow` | DataFrame |
| `get_realtime_quote(code)` | 获取实时行情 | `stock_zh_a_spot_em` | dict |
| `get_limit_stats()` | 获取涨跌停统计 | `stock_zt_pool_em` / `stock_dt_pool_em` | dict |
| `get_stock_news(code)` | 获取个股新闻 | `stock_news_em` | list |

**缓存策略**：
- K线数据：4小时TTL
- 实时行情：5分钟TTL
- 资金流向：4小时TTL
- 新闻数据：2小时TTL

#### 1.2 技术面分析 (`analysis/technical.py`)
**目标**：基于K线数据计算技术指标并评分

**指标体系**（满分100）：
| 指标 | 权重 | 评分逻辑 |
|------|------|----------|
| MA多空排列 | 30分 | MA5>MA10>MA20>MA60 = 多头（+30），反之空头（-30） |
| MACD | 25分 | 金叉+25，死叉-25，柱状线趋势±10 |
| KDJ | 20分 | 超卖区（<20）+20，超买区（>80）-20 |
| RSI | 25分 | RSI<30 超卖+25，RSI>70 超买-25 |

**输出**：-100 ~ +100 分值

#### 1.3 资金面分析 (`analysis/capital.py`)
**目标**：分析主力资金动向

**指标体系**（满分100）：
| 指标 | 权重 | 评分逻辑 |
|------|------|----------|
| 近5日主力净流入趋势 | 50分 | 连续净流入+50，连续净流出-50 |
| 大单/超大单净额占比 | 50分 | 占比>20% +50，占比<-20% -50 |

**输出**：-100 ~ +100 分值

#### 1.4 情绪面分析 (`analysis/sentiment.py`)
**目标**：衡量市场情绪热度

**指标体系**（满分100）：
| 指标 | 权重 | 评分逻辑 |
|------|------|----------|
| 涨跌停比 | 40分 | 涨停>跌停 +40，涨停<跌停 -40 |
| 换手率偏离度 | 30分 | 换手率>5日均值2倍 +30，<0.5倍 -30 |
| 量比 | 30分 | 量比>2 +30，量比<0.5 -30 |

**输出**：-100 ~ +100 分值

#### 1.5 资讯面分析 (`analysis/information.py`)
**目标**：基于新闻关键词判断利多/利空

**利多关键词**：利好、增长、突破、涨停、收购、合作、业绩预增、创新高
**利空关键词**：利空、下跌、减持、跌停、亏损、违规、业绩预减、创新低

**评分逻辑**：
- 利多新闻数 > 利空新闻数 × 2：+100
- 利多新闻数 > 利空新闻数：+50
- 利多新闻数 = 利空新闻数：0
- 利多新闻数 < 利空新闻数：-50
- 利多新闻数 < 利空新闻数 × 2：-100

**输出**：-100 ~ +100 分值

#### 1.6 综合评分引擎 (`analysis/scorer.py`)
**目标**：加权合成四维度分数，输出最终信号

**公式**：
```
total_score = technical × 0.40 + capital × 0.25 + information × 0.20 + sentiment × 0.15
```

**信号映射**：
| 分数区间 | 信号 | 颜色 |
|----------|------|------|
| >= 60 | 强烈买入 | #c62828（深红） |
| >= 20 | 买入 | #4caf50（绿） |
| >= -20 | 持有 | #9e9e9e（灰） |
| >= -60 | 卖出 | #ef5350（浅红） |
| < -60 | 强烈卖出 | #b71c1c（深红） |

---

### 阶段 2：API 接口

#### 2.1 接口设计 (`api/routes.py`)

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/signal` | `code` | 获取综合信号 |
| GET | `/api/stock/info` | `code` | 获取股票基本信息 |
| GET | `/api/stock/kline` | `code`, `days` | 获取K线数据 |
| GET | `/api/stock/detail` | `code` | 获取完整分析详情 |

#### 2.2 响应格式

**综合信号接口** (`/api/signal`)：
```json
{
  "code": "000001",
  "name": "平安银行",
  "signal": "买入",
  "color": "#4caf50",
  "total_score": 32.5,
  "breakdown": {
    "technical": 45.0,
    "capital": 30.0,
    "information": 20.0,
    "sentiment": 15.0
  },
  "updated_at": "2026-05-13T20:00:00"
}
```

**K线数据接口** (`/api/stock/kline`)：
```json
{
  "code": "000001",
  "name": "平安银行",
  "days": 120,
  "kline": [
    {
      "date": "2026-05-13",
      "open": 12.50,
      "close": 12.80,
      "high": 12.90,
      "low": 12.40,
      "volume": 1500000
    }
  ]
}
```

---

### 阶段 3：前端 Vue 3 项目

#### 3.1 项目初始化
```bash
npm create vite@latest frontend -- --template vue
cd frontend
npm install axios echarts vue-echarts
```

#### 3.2 组件设计

**StockSearch.vue**（股票搜索）：
- 输入框支持股票代码（000001）或名称（平安银行）
- 防抖搜索，输入300ms后触发
- 回车或点击搜索按钮触发查询

**SignalCard.vue**（信号卡片）：
- 显示股票名称、代码
- 显示五级信号文字（带背景颜色）
- 显示总分和四维度小分数
- 响应式设计

**ScoreRadar.vue**（雷达图）：
- ECharts 雷达图展示四维度得分
- 技术面、资金面、资讯面、情绪面四个维度
- 分值范围 0-100

**KlineChart.vue**（K线图）：
- ECharts K线图展示日K线
- 叠加 MA5/MA10/MA20 均线
- 底部显示成交量柱状图
- 支持缩放和拖拽

**Home.vue**（主页面）：
- 顶部：股票搜索框
- 中部：信号卡片 + 雷达图（左右布局）
- 底部：K线图
- 响应式布局

---

### 阶段 4：集成与优化

#### 4.1 前后端联调
- 确保 CORS 配置正确
- 测试所有API接口
- 处理跨域问题

#### 4.2 错误处理
- 股票代码无效：返回404 + 错误提示
- 网络超时：前端显示重试按钮
- 数据为空：显示"暂无数据"提示
- AKShare 限流：缓存兜底

#### 4.3 性能优化
- 后端：合理设置缓存TTL
- 前端：组件懒加载
- 前端：ECharts 按需引入

#### 4.4 文档完善
- 编写 README.md
- 补充 API 文档（FastAPI 自动生成）

---

## 四、开发顺序

```
Step 1: data/stock_data.py          # 数据获取（所有分析的基础）
Step 2: analysis/technical.py       # 技术面分析
Step 3: analysis/capital.py         # 资金面分析
Step 4: analysis/sentiment.py       # 情绪面分析
Step 5: analysis/information.py     # 资讯面分析
Step 6: analysis/scorer.py          # 综合评分引擎
Step 7: api/routes.py               # API 路由
Step 8: 修复 main.py                # 确保后端可运行
Step 9: 前端项目初始化              # Vue 3 + Vite
Step 10: 前端组件开发               # 搜索、信号、图表
Step 11: 前后端联调                 # 集成测试
Step 12: 优化与文档                 # 收尾
```

---

## 五、风险与应对

| 风险 | 影响 | 应对方案 |
|------|------|----------|
| AKShare 接口限流 | 数据获取失败 | 缓存兜底 + 重试机制 |
| AKShare 接口变更 | 代码报错 | 版本锁定 + 异常捕获 |
| 新闻数据质量差 | 资讯面评分不准 | 关键词词典可配置化 |
| 前端图表性能 | 大数据量卡顿 | 数据采样 + 虚拟滚动 |

---

## 六、验收标准

1. 后端可启动，`/api/signal?code=000001` 返回正确信号
2. 四维度评分逻辑正确，总分在 -100 ~ +100 范围内
3. 前端可展示信号卡片、雷达图、K线图
4. 错误场景有友好提示
5. 代码有基本注释

---

*文档创建时间：2026-05-13*
*最后更新：2026-05-13*
