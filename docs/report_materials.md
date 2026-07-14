# 课程报告可直接使用的素材

## 项目题目

基于 NoSQL 的科研数据分析系统

## 总体设计

本项目以教师提供的 Web of Science 学者科研数据为对象，围绕论文元数据管理、统计分析、学术关系挖掘和语义相似检索开展系统设计。系统采用 MongoDB 作为主存储数据库，用文档模型保存论文标题、作者、摘要、关键词、机构、学院、期刊、年份、被引次数等半结构化字段；采用 Neo4j 构建 Author、Paper、Institution、School、Keyword、Journal 等实体及其关系；采用 FAISS 思路对论文标题、摘要和关键词进行向量化，实现相似论文检索、相似学者发现和潜在合作推荐；前端使用 ECharts 对统计结果和关系图谱进行展示。

## 数据预处理

原始数据为 Web of Science 纯文本格式，每篇论文以 `ER` 结束，字段包括 `AU`、`AF`、`TI`、`SO`、`DE`、`AB`、`C1`、`C3`、`CR`、`PY`、`TC`、`DI`、`WC`、`SC`、`UT` 等。预处理过程包括：

- 识别两位大写字段码，将连续缩进行合并到所属字段。
- 对作者、机构、参考文献等多值字段保留列表结构。
- 对关键词、学科类别等分号分隔字段进行切分。
- 根据 `UT` 或 DOI 构造论文唯一编号。
- 从地址字段中抽取学院简称，并映射为中文学院名称。
- 对缺失年份、被引次数、关键词等字段进行默认值处理。

## MongoDB 存储设计

MongoDB 适合存储 Web of Science 这类字段数量多、结构不完全一致的半结构化数据。项目以 `papers` 集合为核心，每篇论文保存为一个文档，主要字段包括：

```json
{
  "paper_id": "WOS:001588882900135",
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "keywords": ["关键词1", "关键词2"],
  "abstract": "摘要",
  "journal": "期刊或会议来源",
  "year": 2025,
  "times_cited": 0,
  "school": "自动化学院",
  "institutions": ["Guangdong University of Technology"]
}
```

创建索引包括 `paper_id` 唯一索引、`year`、`school`、`authors`、`keywords` 普通索引，以及标题、摘要、关键词的全文索引。

## 可视化分析角度

项目实现了六类图表：

- 年度发文趋势与年度被引趋势。
- 不同学院发文量对比。
- 高频关键词热点分析。
- 主要期刊来源分布。
- Web of Science 学科类别分布。
- 合作机构关系统计。

## Neo4j 图谱建模

实体类型：

- `Author`：学者。
- `Paper`：论文。
- `Institution`：机构。
- `School`：学院。
- `Keyword`：关键词。
- `Journal`：期刊或会议来源。

关系类型：

- `(Author)-[:WROTE]->(Paper)`
- `(Author)-[:AFFILIATED_WITH]->(Institution)`
- `(Author)-[:BELONGS_TO]->(School)`
- `(Paper)-[:HAS_KEYWORD]->(Keyword)`
- `(Paper)-[:PUBLISHED_IN]->(Journal)`
- `(Author)-[:COAUTHORED]-(Author)`

## 向量化与 FAISS 设计

项目将论文标题、摘要、关键词和 Keywords Plus 拼接为论文语义文本，使用文本向量化方法生成高维向量，并进行 L2 归一化。向量索引用于支持：

- 输入研究主题，返回相似论文。
- 将学者近年论文标题、摘要、关键词拼接为作者画像，计算相似学者。
- 根据语义相似但图谱中尚未合作的学者，提出潜在合作推荐。

系统代码中优先检测 FAISS。如果环境安装 `faiss-cpu`，则使用 `IndexFlatIP` 构建内积相似度索引；若未安装，则使用 scikit-learn 的余弦相似度作为可运行兜底，保证展示系统稳定运行。

## 创新点

- 结构化字段优先的实体提取方式，减少从自由文本抽取导致的误差。
- 学院简称规则映射，将 WOS 地址中的英文缩写转换为中文学院名称。
- 将 Neo4j 合作关系与向量语义相似度结合，用于发现潜在合作学者。
- 构建统一 Web 系统，将文档数据库、图数据库和向量检索结果集中展示。

