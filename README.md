# 股票顾问 - 操作提示系统

基于四维度分析模型的 A 股股票操作提示系统。

## 功能

- **四维度分析**：技术面(40%) / 资金面(25%) / 资讯面(20%) / 情绪面(15%)
- **五级信号**：强烈买入 / 买入 / 持有 / 卖出 / 强烈卖出
- **K线图表**：日K线 + MA均线 + 成交量
- **雷达图**：四维度可视化评分

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + AKShare + Pandas |
| 前端 | Vue 3 + Vite + ECharts |
| 缓存 | DiskCache (SQLite) |

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
# 服务启动于 http://127.0.0.1:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
# 服务启动于 http://localhost:5173
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/signal?code=000001` | 获取综合信号 |
| GET | `/api/stock/info?code=000001` | 获取实时行情 |
| GET | `/api/stock/kline?code=000001&days=120` | 获取K线数据 |
| GET | `/api/stock/detail?code=000001` | 获取完整分析详情 |

## 项目结构

```
stock-advisor/
├── backend/          # 后端服务
│   ├── main.py       # FastAPI 入口
│   ├── config.py     # 系统配置
│   ├── data/         # 数据获取 (AKShare)
│   ├── analysis/     # 四维度分析引擎
│   ├── api/          # RESTful API
│   └── cache/        # 磁盘缓存
├── frontend/         # Vue 3 前端
│   └── src/
│       ├── components/  # 信号卡片、雷达图、K线图
│       └── views/       # 主页面
└── docs/             # 项目文档
```

## 文档

- [项目计划](docs/plan.md)
- [构建记忆](docs/memory.md)
- [功能说明](docs/features.md)