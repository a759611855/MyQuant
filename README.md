# MyQuant

量化相关项目仓库。

## 本地目录

推荐本地路径：`/Users/xgh/MyQuant`

### 首次关联 GitHub（本地已有代码时）

在本地执行：

```bash
cd /Users/xgh/MyQuant
git init
git remote add origin https://github.com/a759611855/MyQuant.git
git fetch origin
git checkout -b main
# 或已有 main 时：git pull origin main --allow-unrelated-histories
```

### 或直接克隆到该目录

```bash
git clone https://github.com/a759611855/MyQuant.git /Users/xgh/MyQuant
cd /Users/xgh/MyQuant
```

## 提交规则

- **不提交**：所有 `.csv` / `.CSV` 文件（已在 `.gitignore` 中忽略）
- **可提交**：代码、配置、文档等其余文件

```bash
cd /Users/xgh/MyQuant
git status          # 确认 *.csv 显示为 ignored
git add .
git commit -m "描述本次改动"
git push -u origin main
```
