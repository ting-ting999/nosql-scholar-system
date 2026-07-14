# 部署与运行说明

## 1. 本地运行

进入项目目录并安装依赖：

```powershell
cd nosql-scholar-system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如需重新处理原始数据，执行：

```powershell
python scripts\prepare_data.py --input "path\to\scholar-data-full.txt"
```

构建向量索引：

```powershell
python scripts\build_vector_index.py
```

启动 Web 系统：

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

本地访问地址：

```text
http://127.0.0.1:8000
```

说明：`127.0.0.1` 是本机地址，只能在本机浏览器访问，不是公网地址。

## 2. Render 公网部署

本项目已增加 Render 部署配置文件：

```text
render.yaml
runtime.txt
.gitignore
```

Render 使用的构建命令为：

```bash
pip install -r requirements.txt && python scripts/build_vector_index.py
```

Render 使用的启动命令为：

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1
```

部署步骤：

1. 将 `nosql_scholar_system` 上传到 GitHub 仓库。
2. 登录 Render，选择 `New` -> `Blueprint`。
3. 连接 GitHub 仓库，Render 会自动读取 `render.yaml`。
4. 点击部署，等待依赖安装、向量索引构建和 Web 服务启动。
5. 部署成功后，访问 `https://nosql-scholar-system.onrender.com`。

注意事项：

- `data/processed/papers.json` 和 `data/neo4j/*.csv` 需要随仓库提交。
- `data/faiss/*.npy`、`data/faiss/*.npz`、`data/faiss/*.index`、`data/faiss/*.pkl` 不需要提交，Render 会在部署时重新生成。
- 公网环境通过 `DISABLE_FAISS=1` 使用稀疏 TF-IDF 矩阵，避免免费实例超过 512MB 内存限制；本地安装 FAISS 后仍可使用 `IndexFlatIP`。
- Render 免费服务长时间无人访问可能会休眠，首次访问会有几十秒冷启动时间。
- 如果课程验收需要稳定访问，建议答辩前提前打开一次公网地址，等待服务唤醒。

## 3. MongoDB 与 Neo4j 说明

公网展示层读取预处理后的 JSON、CSV 和向量索引文件，使演示服务与外部数据库解耦。MongoDB 与 Neo4j 的数据导入和查询流程由以下脚本独立完成：

- MongoDB 导入脚本：`scripts/import_mongodb.py`
- Neo4j 导入 CSV：`data/neo4j/*.csv`
- Neo4j 导入脚本：`docs/neo4j_import.cypher`

如果需要在云端同时连接真实 MongoDB，可在 Render 环境变量中配置：

```text
MONGODB_URI
MONGODB_DB
```
