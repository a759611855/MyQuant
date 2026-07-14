# MyQuant

个人量化分析平台：看板、数据同步、评分、最近新闻。

## 功能

- **看板**：观察列表规模、K 线样本、评分前列与最近新闻一览
- **数据同步**：通过 yfinance 拉取行情写入本地 SQLite（失败时使用可复现回退数据）
- **评分**：动量 / 波动 / 趋势 / 流动性四因子加权，输出综合分与等级
- **新闻**：聚合公开财经 RSS，并缓存到本地

## 本地目录

推荐路径：`/Users/xgh/MyQuant`

```bash
git clone https://github.com/a759611855/MyQuant.git /Users/xgh/MyQuant
cd /Users/xgh/MyQuant
```

## 启动

### 1. 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API 文档：http://127.0.0.1:8000/docs

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开：http://127.0.0.1:5173

## 推荐使用顺序

1. 打开「数据同步」→ 同步全部观察列表  
2. 打开「评分」→ 重新计算评分  
3. 打开「新闻」→ 获取最近新闻  
4. 回到「看板」查看总览  

## 提交规则

- **不提交**：`*.csv`、`backend/data/`、`node_modules/`、虚拟环境
- **可提交**：代码、配置、文档
