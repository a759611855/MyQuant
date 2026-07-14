# MyQuant

个人量化分析平台：看板、数据同步、评分、最近新闻。

## 功能

- **看板**：观察列表规模、K 线样本、评分前列与最近新闻一览
- **数据同步**：通过 yfinance 拉取行情写入本地 SQLite（失败时使用可复现回退数据）
- **评分**：动量 / 波动 / 趋势 / 流动性四因子加权，输出综合分与等级
- **新闻**：聚合公开财经 RSS，并缓存到本地

## 本地启动（推荐）

路径：`/Users/xgh/MyQuant`

```bash
# 1) 拉代码（首次或更新）
mkdir -p /Users/xgh
cd /Users/xgh
if [ ! -d MyQuant/.git ]; then
  git clone https://github.com/a759611855/MyQuant.git MyQuant
fi
cd MyQuant
git fetch origin
git checkout cursor/quant-platform-2cc6
git pull origin cursor/quant-platform-2cc6

# 2) 一键启动前后端
chmod +x scripts/dev.sh
./scripts/dev.sh
```

浏览器打开：**http://127.0.0.1:5173**  
API 文档：**http://127.0.0.1:8000/docs**

按 `Ctrl+C` 可同时停止前后端。

### 分终端启动（可选）

```bash
# 终端 1 — 后端
cd /Users/xgh/MyQuant/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 终端 2 — 前端
cd /Users/xgh/MyQuant/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## 推荐使用顺序

1. 「数据同步」→ 同步全部观察列表  
2. 「评分」→ 重新计算评分  
3. 「新闻」→ 获取最近新闻  
4. 「看板」查看总览  

## 提交规则

- **不提交**：`*.csv`、`backend/data/*`、`node_modules/`、虚拟环境
- **可提交**：代码、配置、文档
