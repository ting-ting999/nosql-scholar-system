# 基于 NoSQL 的科研数据分析系统

本项目面向 NoSQL 数据库课程设计，使用教师提供的 Web of Science 学者科研数据，完成 MongoDB 文档存储、Neo4j 学术知识图谱、FAISS/向量语义检索、统计可视化和统一 Web 展示。

## 功能模块

- WOS 文本解析与清洗：作者、标题、摘要、关键词、机构、学院、期刊、年份、被引次数等字段结构化。
- MongoDB 主存储：以论文为核心文档保存科研元数据，并提供聚合分析脚本。
- Neo4j 知识图谱：构建 Author、Paper、Institution、School、Keyword、Journal 节点及关系。
- 向量语义分析：支持相似论文检索、相似学者发现、主题聚类和潜在合作推荐。
- Web 展示系统：统计仪表盘、图表分析、学者画像、图谱查询说明、向量检索页面。

## 快速开始

```powershell
cd D:\learn\NoSQL\nosql_scholar_system
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\prepare_data.py --input "C:\Users\zyt18\Downloads\scholar-data-full.txt"
python scripts\build_vector_index.py
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

打开浏览器访问：

```text
http://127.0.0.1:8000
```

## 数据库脚本

- MongoDB 导入：`python scripts/import_mongodb.py`
- Neo4j CSV 生成：由 `scripts/prepare_data.py` 自动生成到 `data/neo4j`
- Neo4j Cypher 导入脚本：`docs/neo4j_import.cypher`
- 分析查询脚本：`docs/cypher_queries.md`

## 目录结构

```text
backend/              FastAPI 后端接口
frontend/             静态前端页面
scripts/              数据处理、入库、向量索引脚本
data/processed/       清洗后的 JSON/CSV 数据
data/neo4j/           Neo4j 导入 CSV
data/faiss/           向量索引与元数据
docs/                 报告素材、部署说明、Cypher 语句
```
