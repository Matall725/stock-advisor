# 股票顾问系统 - 构建记忆文档

本文档记录项目每一步构建的进展，便于回溯和交接。

---

## 2026-05-13：项目初始化

### 已完成工作

#### 1. 项目骨架搭建
- 创建后端目录结构：`backend/`、`backend/analysis/`、`backend/api/`、`backend/data/`、`backend/cache/`
- 创建前端目录：`frontend/`（空目录）
- 初始化 Git 仓库

#### 2. 后端入口 (`backend/main.py`)
- 使用 FastAPI 框架
- 配置 CORS 中间件（允许所有来源）
- 挂载 API 路由到 `/api` 前缀
- 使用 Uvicorn 启动，监听 `127.0.0.1:8000`
- **注意**：当前引用了不存在的 `api.routes`，需要后续创建

#### 3. 系统配置 (`backend/config.py`)
- 定义四维度权重：技术面40%、资金面25%、资讯面20%、情绪面15%
- 定义五级信号阈值：强烈买入(>=60)、买入(>=20)、持有(>=-20)、卖出(>=-60)、强烈卖出(<-60)
- 配置缓存目录和TTL（4小时）
- 配置K线默认天数（120天）

#### 4. 依赖清单 (`backend/requirements.txt`)
- fastapi 0.115.0
- uvicorn 0.30.0
- akshare >= 1.14.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- diskcache >= 5.6.0

#### 5. 缓存管理器 (`backend/cache/manager.py`)
- 封装 diskcache 库
- 提供 `get(key)`、`put(key, value, ttl)`、`clear()` 三个函数
- 自动创建缓存目录

#### 6. 项目文档
- 创建 `docs/` 目录
- 编写计划文档 `docs/plan.md`
- 编写记忆文档 `docs/memory.md`（本文件）
- 编写功能文档 `docs/features.md`

### 待完成工作
- [x] 数据获取模块 `data/stock_data.py`
- [x] 技术面分析 `analysis/technical.py`
- [x] 资金面分析 `analysis/capital.py`
- [x] 情绪面分析 `analysis/sentiment.py`
- [x] 资讯面分析 `analysis/information.py`
- [x] 综合评分引擎 `analysis/scorer.py`
- [x] API 路由 `api/routes.py`
- [x] 修复 `main.py` 导入问题
- [x] 前端项目初始化
- [x] 前端组件开发
- [x] 前后端联调

### 决策记录
| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-05-13 | 选择 FastAPI 作为后端框架 | 异步支持好，自带OpenAPI文档 |
| 2026-05-13 | 选择 AKShare 作为数据源 | 免费、覆盖A股主要数据 |
| 2026-05-13 | 选择 DiskCache 作为缓存 | 基于SQLite，无需额外服务 |
| 2026-05-13 | 选择 Vue 3 + Vite 作为前端 | 轻量级、易上手 |
| 2026-05-13 | 选择 ECharts 作为图表库 | 社区成熟，K线图支持好 |

---

---

## 2026-05-13 (Step 1)：数据获取模块

### 完成工作
- [x] 创建 `data/stock_data.py`
  - `get_kline(code, days)` — 获取前复权日K线数据
  - `get_realtime_quote(code)` — 获取实时行情（价格/涨跌幅/换手率/量比等）
  - `get_fund_flow(code)` — 获取个股资金流向（主力/大单/小单）
  - `get_limit_stats()` — 获取全市场涨跌停统计
  - `get_stock_news(code)` — 获取个股近期新闻
  - 所有函数均使用缓存管理器拦截重复请求
  - 不同接口设置不同 TTL：K线4h、行情5min、资金4h、新闻2h

### 决策记录
| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-05-13 | K线使用前复权(qfq) | 反映真实收益 |
| 2026-05-13 | 涨跌停统计失败时返回默认值 | 避免单个接口异常阻塞整个系统 |

---

## 模板：后续构建记录

### YYYY-MM-DD：阶段名称

#### 完成工作
- [ ] 任务1
- [ ] 任务2

#### 遇到问题
- 问题描述及解决方案

#### 决策记录
| 日期 | 决策 | 原因 |
|------|------|------|
| | | |

---

## 2026-05-13 (Step 12)：优化与收尾

### 完成工作
- [x] 创建 `.gitignore`（Python/Node/Cache/IDE 忽略规则）
- [x] 创建 `README.md`（项目说明、快速开始、API 文档）
- [x] 更新 `docs/memory.md` 和 `docs/features.md` 所有文件状态

### 后续补充
- [x] 创建 `start.ps1` + `start.bat` 一键启动脚本（自动安装依赖、启动后端+前端、打开浏览器）

### Bug 修复 (2026-05-13)
- [x] `technical.py:14-15` — 修复返回 bare `0.0` 导致 scorer.py 解包崩溃，改为 `(0.0, {})`
- [x] `sentiment.py:45` — 修复涨跌停判断逻辑 `zt < dt * 2` → `dt > zt * 2`，等量情况不再误判为强烈利空
- [x] `routes.py:49-50` — `stock_detail` 补充 try/except，避免未捕获异常返回 500
- [x] `capital.py`, `sentiment.py`, `information.py` — 修复 type hint `-> float` 改为实际返回的 tuple
- [x] `scorer.py:2,11` — 合并重复的 `from config import` 语句
- [x] `config.py:21` — CACHE_DIR 改为 `os.path.dirname(__file__)+.cache`，消除硬编码绝对路径
- [x] `stock_data.py` — `get_kline` 主用 `stock_zh_a_daily`，降级 `stock_zh_a_hist`
- [x] `stock_data.py` — `get_realtime_quote` 主用 `stock_bid_ask_em`，3次重试+降级到K线
- [x] `stock_data.py` — 修复 `stock_dt_pool_em` → `stock_zt_pool_dtgc_em`（函数名变更）
- [x] `stock_data.py` — 修复 `stock_news_em(stock=)` → `stock_news_em(symbol=)`（参数名变更）

### 最终文件清单
- 后端：14 个 Python 文件（main.py, config.py, 5个analysis, routes, data, cache）
- 前端：8 个文件（Vue组件、API封装、Vite配置）
- 文档：3 个 md 文件（plan, memory, features）+ README
- 配置：.gitignore

---

*文档创建时间：2026-05-13*
*最后更新：2026-05-13*
