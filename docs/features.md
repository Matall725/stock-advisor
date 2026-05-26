# 股票顾问系统 - 功能文档

本文档介绍项目中每个文件的功能和用途。

---

## 目录

- [后端文件](#后端文件)
  - [main.py](#mainpy)
  - [config.py](#configpy)
  - [requirements.txt](#requirementstxt)
  - [cache/manager.py](#cachemanagerpy)
  - [data/stock_data.py](#datastock_datapy)
  - [analysis/technical.py](#analysistechnicalpy)
  - [analysis/capital.py](#analysiscapitalpy)
  - [analysis/sentiment.py](#analysissentimentpy)
  - [analysis/information.py](#analysisinformationpy)
  - [analysis/scorer.py](#analysiscorerpy)
  - [api/routes.py](#apiroutespy)
- [前端文件](#前端文件)
  - [package.json](#packagejson)
  - [vite.config.js](#viteconfigjs)
  - [index.html](#indexhtml)
  - [src/main.js](#srcmainjs)
  - [src/App.vue](#srcappvue)
  - [src/api/index.js](#srcapiindexjs)
  - [src/components/StockSearch.vue](#srccomponentsstocksearchvue)
  - [src/components/SignalCard.vue](#srccomponentssignalcardvue)
  - [src/components/ScoreRadar.vue](#srccomponentsscoreradarvue)
  - [src/components/KlineChart.vue](#srccomponentsklinechartvue)
  - [src/views/Home.vue](#srcviewshomevue)
- [文档文件](#文档文件)
  - [docs/plan.md](#docsplanmd)
  - [docs/memory.md](#docsmemorymd)
  - [docs/features.md](#docsfeaturesmd)

---

## 后端文件

### main.py
**路径**：`backend/main.py`
**状态**：✅ 已实现
**功能**：FastAPI 应用入口，启动 HTTP 服务器

**主要逻辑**：
- 创建 FastAPI 实例，标题为"股票操作提示系统"
- 配置 CORS 中间件，允许所有来源访问
- 挂载 API 路由到 `/api` 前缀
- 使用 Uvicorn 启动服务器，监听 `127.0.0.1:8000`

**依赖**：
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `api.routes` - API 路由模块（需创建）

---

### config.py
**路径**：`backend/config.py`
**状态**：✅ 已实现
**功能**：系统全局配置，集中管理权重、阈值、缓存参数

**配置项**：
| 配置项 | 类型 | 说明 |
|--------|------|------|
| `DEFAULT_WEIGHTS` | dict | 四维度默认权重（技术0.40、资金0.25、资讯0.20、情绪0.15） |
| `SIGNAL_THRESHOLDS` | list | 五级信号阈值（强烈买入>=60、买入>=20、持有>=-20、卖出>=-60、强烈卖出<-60） |
| `CACHE_DIR` | str | 缓存目录路径 |
| `CACHE_TTL` | int | 缓存过期时间（4小时=14400秒） |
| `KLINE_DAYS` | int | K线默认天数（120天） |

---

### requirements.txt
**路径**：`backend/requirements.txt`
**状态**：✅ 已实现
**功能**：定义 Python 依赖包清单

**依赖列表**：
| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.115.0 | Web API 框架 |
| uvicorn | 0.30.0 | ASGI 服务器 |
| akshare | >=1.14.0 | A股金融数据获取 |
| pandas | >=2.0.0 | 数据分析处理 |
| numpy | >=1.24.0 | 数值计算 |
| diskcache | >=5.6.0 | 磁盘缓存 |

---

### cache/manager.py
**路径**：`backend/cache/manager.py`
**状态**：✅ 已实现
**功能**：缓存管理器，避免重复请求 AKShare 数据

**函数说明**：
| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `get(key)` | key: str | any | 根据 key 获取缓存值，不存在返回 None |
| `put(key, value, ttl)` | key: str, value: any, ttl: int | None | 存入缓存，默认 TTL 4小时 |
| `clear()` | 无 | None | 清空全部缓存 |

**依赖**：
- `diskcache` - 磁盘缓存库
- `config.CACHE_DIR` - 缓存目录路径
- `config.CACHE_TTL` - 默认缓存时间

---

### data/stock_data.py
**路径**：`backend/data/stock_data.py`
**状态**：✅ 已实现
**功能**：数据获取模块，封装 AKShare 接口

**计划函数**：
| 函数 | 功能 | AKShare 接口 | 返回格式 |
|------|------|--------------|----------|
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

---

### analysis/technical.py
**路径**：`backend/analysis/technical.py`
**状态**：✅ 已实现
**功能**：技术面分析，基于K线数据计算技术指标并评分

**指标体系**（满分100）：
| 指标 | 权重 | 评分逻辑 |
|------|------|----------|
| MA多空排列 | 30分 | MA5>MA10>MA20>MA60 = 多头（+30），反之空头（-30） |
| MACD | 25分 | 金叉+25，死叉-25，柱状线趋势±10 |
| KDJ | 20分 | 超卖区（<20）+20，超买区（>80）-20 |
| RSI | 25分 | RSI<30 超卖+25，RSI>70 超买-25 |

**输出**：-100 ~ +100 分值

---

### analysis/capital.py
**路径**：`backend/analysis/capital.py`
**状态**：✅ 已实现
**功能**：资金面分析，分析主力资金动向

**指标体系**（满分100）：
| 指标 | 权重 | 评分逻辑 |
|------|------|----------|
| 近5日主力净流入趋势 | 50分 | 连续净流入+50，连续净流出-50 |
| 大单/超大单净额占比 | 50分 | 占比>20% +50，占比<-20% -50 |

**输出**：-100 ~ +100 分值

---

### analysis/sentiment.py
**路径**：`backend/analysis/sentiment.py`
**状态**：✅ 已实现
**功能**：情绪面分析，衡量市场情绪热度

**指标体系**（满分100）：
| 指标 | 权重 | 评分逻辑 |
|------|------|----------|
| 涨跌停比 | 40分 | 涨停>跌停 +40，涨停<跌停 -40 |
| 换手率偏离度 | 30分 | 换手率>5日均值2倍 +30，<0.5倍 -30 |
| 量比 | 30分 | 量比>2 +30，量比<0.5 -30 |

**输出**：-100 ~ +100 分值

---

### analysis/information.py
**路径**：`backend/analysis/information.py`
**状态**：✅ 已实现
**功能**：资讯面分析，基于新闻关键词判断利多/利空

**关键词词典**：
- 利多关键词：利好、增长、突破、涨停、收购、合作、业绩预增、创新高
- 利空关键词：利空、下跌、减持、跌停、亏损、违规、业绩预减、创新低

**评分逻辑**：
| 条件 | 分数 |
|------|------|
| 利多 > 利空 × 2 | +100 |
| 利多 > 利空 | +50 |
| 利多 = 利空 | 0 |
| 利多 < 利空 | -50 |
| 利多 < 利空 × 2 | -100 |

**输出**：-100 ~ +100 分值

---

### analysis/scorer.py
**路径**：`backend/analysis/scorer.py`
**状态**：✅ 已实现
**功能**：综合评分引擎，加权合成四维度分数

**计算公式**：
```
total_score = technical × 0.40 + capital × 0.25 + information × 0.20 + sentiment × 0.15
```

**信号映射**：
| 分数区间 | 信号 | 颜色代码 |
|----------|------|----------|
| >= 60 | 强烈买入 | #c62828 |
| >= 20 | 买入 | #4caf50 |
| >= -20 | 持有 | #9e9e9e |
| >= -60 | 卖出 | #ef5350 |
| < -60 | 强烈卖出 | #b71c1c |

---

### api/routes.py
**路径**：`backend/api/routes.py`
**状态**：✅ 已实现
**功能**：RESTful API 路由定义

**接口列表**：
| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/signal` | code | 获取综合信号 |
| GET | `/api/stock/info` | code | 获取股票基本信息 |
| GET | `/api/stock/kline` | code, days | 获取K线数据 |
| GET | `/api/stock/detail` | code | 获取完整分析详情 |

---

## 前端文件

### package.json
**路径**：`frontend/package.json`
**状态**：✅ 已实现
**功能**：Node.js 项目配置和依赖管理

**主要依赖**：
- `vue` - Vue 3 框架
- `axios` - HTTP 客户端
- `echarts` - 图表库
- `vue-echarts` - Vue ECharts 封装

---

### vite.config.js
**路径**：`frontend/vite.config.js`
**状态**：✅ 已实现
**功能**：Vite 构建工具配置

**配置内容**：
- 开发服务器代理（将 `/api` 代理到后端 `http://127.0.0.1:8000`）
- 路径别名设置

---

### index.html
**路径**：`frontend/index.html`
**状态**：✅ 已实现
**功能**：HTML 入口文件

---

### src/main.js
**路径**：`frontend/src/main.js`
**状态**：✅ 已实现
**功能**：Vue 应用入口

---

### src/App.vue
**路径**：`frontend/src/App.vue`
**状态**：✅ 已实现
**功能**：Vue 根组件

---

### src/api/index.js
**路径**：`frontend/src/api/index.js`
**状态**：✅ 已实现
**功能**：Axios 封装，定义 API 请求函数

**函数列表**：
- `getSignal(code)` - 获取综合信号
- `getStockInfo(code)` - 获取股票信息
- `getKline(code, days)` - 获取K线数据
- `getDetail(code)` - 获取完整详情

---

### src/components/StockSearch.vue
**路径**：`frontend/src/components/StockSearch.vue`
**状态**：✅ 已实现
**功能**：股票搜索组件

**功能特性**：
- 输入框支持股票代码或名称
- 防抖搜索（300ms延迟）
- 回车/点击触发查询

---

### src/components/SignalCard.vue
**路径**：`frontend/src/components/SignalCard.vue`
**状态**：✅ 已实现
**功能**：信号展示卡片

**展示内容**：
- 股票名称、代码
- 五级信号文字（带背景颜色）
- 总分和四维度小分数

---

### src/components/ScoreRadar.vue
**路径**：`frontend/src/components/ScoreRadar.vue`
**状态**：✅ 已实现
**功能**：四维度雷达图

**图表配置**：
- ECharts 雷达图
- 四个维度：技术面、资金面、资讯面、情绪面
- 分值范围 0-100

---

### src/components/KlineChart.vue
**路径**：`frontend/src/components/KlineChart.vue`
**状态**：✅ 已实现
**功能**：K线图组件

**图表配置**：
- ECharts K线图
- 叠加 MA5/MA10/MA20 均线
- 底部成交量柱状图
- 支持缩放和拖拽

---

### src/views/Home.vue
**路径**：`frontend/src/views/Home.vue`
**状态**：✅ 已实现
**功能**：主页面

**布局结构**：
- 顶部：股票搜索框
- 中部：信号卡片 + 雷达图（左右布局）
- 底部：K线图

---

## 文档文件

### docs/plan.md
**路径**：`docs/plan.md`
**状态**：✅ 已实现
**功能**：项目计划文档

**内容**：
- 项目概述和目标
- 技术栈说明
- 项目结构规划
- 分阶段实施计划
- API 接口设计
- 风险与应对

---

### docs/memory.md
**路径**：`docs/memory.md`
**状态**：✅ 已实现
**功能**：构建记忆文档

**内容**：
- 每日构建进展记录
- 已完成工作清单
- 待完成工作清单
- 决策记录

---

### docs/features.md
**路径**：`docs/features.md`
**状态**：✅ 已实现（本文件）
**功能**：功能文档

**内容**：
- 每个文件的功能说明
- 函数/组件接口定义
- 配置项说明
- 依赖关系

---

*文档创建时间：2026-05-13*
*最后更新：2026-05-13*
