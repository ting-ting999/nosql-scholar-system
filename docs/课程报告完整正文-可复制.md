# NoSQL 数据库课程报告

题目：基于 NoSQL 的科研数据分析系统

## 一、项目背景

随着高校科研活动规模不断扩大，论文、作者、机构、关键词、期刊、引用文献等科研数据呈现出数据量大、字段类型多、结构不完全统一、实体关系复杂等特点。传统关系型数据库虽然适合结构稳定的数据管理，但在处理 Web of Science 这类半结构化学术元数据时，需要设计较多固定表结构，并且在作者合作、机构关联、关键词主题关系等复杂网络分析方面不够直观。因此，使用 NoSQL 数据库对科研数据进行存储、分析和展示具有较强的现实意义。

本项目以教师提供的 Web of Science 学者科研数据为对象，围绕广东工业大学相关科研论文元数据，设计并实现了一个“基于 NoSQL 的科研数据分析系统”。系统综合使用 MongoDB、Neo4j、向量检索和 Web 可视化技术：MongoDB 用于存储论文元数据，Neo4j 用于构建学术知识图谱，向量检索模块用于实现相似论文和相似学者发现，前端网站用于统一展示统计图表、学者画像、图谱分析和语义检索结果。

本项目共处理 5000 篇论文记录，识别出 8519 名学者、14084 个关键词和 2038 个期刊或会议来源。通过本项目，可以较完整地展示 NoSQL 数据库在科研数据管理、统计分析、关联关系挖掘和语义检索中的综合应用。

【插入图 1：系统首页截图。建议截图位置：打开网站 `http://127.0.0.1:8000`，截取包含广东工业大学校园主题头图、论文总数、学者数量、关键词数量和期刊来源的首页。】

## 二、任务目标

本项目的总体目标是完成一个可运行、可展示、可说明原理的科研数据分析系统。结合课程设计任务书要求，本项目主要完成以下目标。

第一，完成 Web of Science 科研论文数据的解析、清洗和结构化转换。原始数据为纯文本格式，包含论文标题、作者、摘要、关键词、机构、期刊、年份、被引次数等字段。系统需要将这些字段转换为便于数据库存储和分析的 JSON、CSV 数据。

第二，完成 NoSQL 主存储设计。本项目在 Hadoop、Redis、MongoDB 三类技术中选择 MongoDB 作为主存储数据库，将每篇论文以文档形式保存，保留作者、关键词、机构、参考文献等数组字段，并支持按年份、学院、关键词、期刊等维度进行聚合统计。

第三，完成科研数据统计分析与可视化。系统基于处理后的论文数据，使用 ECharts 绘制年度发文趋势、年度被引趋势、学院发文量、高频关键词、主要期刊来源、WOS 学科类别和合作机构关系等图表。

第四，完成 Neo4j 学术知识图谱构建。系统从论文元数据中抽取 Author、Paper、Institution、School、Keyword、Journal 等实体，构建作者撰写论文、论文包含关键词、作者隶属学院、论文发表在期刊等关系，并提供多条 Cypher 查询用于关联关系分析。

第五，完成向量语义检索设计与实现。系统将论文标题、摘要、关键词等内容拼接为论文语义文本，构建文本向量索引，实现相似论文检索和相似学者发现。代码中支持 FAISS 索引；若运行环境暂未安装 FAISS，则使用余弦相似度作为兜底方案，保证系统可运行。

第六，完成统一 Web 展示系统。系统前端包含总览、统计图表、学者画像、知识图谱、向量检索五个页面，能够将课程项目的主要成果集中展示，便于课程答辩和报告说明。

【插入图 2：网站顶部导航栏截图。要求能看到“总览、统计图表、学者画像、知识图谱、向量检索”等模块。】

## 三、总体设计思路

本项目采用“数据解析清洗—NoSQL 存储—图谱建模—向量检索—Web 展示”的总体设计思路。系统首先读取教师提供的 `scholar-data-full.txt` 文件，对 Web of Science 文本记录进行字段解析和数据清洗；然后将清洗后的数据导出为 `papers.json`、`papers_flat.csv`、Neo4j 导入 CSV 和向量检索元数据；接着分别用于 MongoDB 文档存储、Neo4j 图谱导入、向量索引构建和 Web 前端展示。

系统整体流程如下：

```text
scholar-data-full.txt
        ↓
Web of Science 文本解析与字段清洗
        ↓
papers.json / summary.json / papers_flat.csv / Neo4j CSV
        ↓
MongoDB 文档数据库存储
        ↓
Neo4j 学术知识图谱构建
        ↓
论文文本向量化与相似检索
        ↓
FastAPI 后端接口
        ↓
Web 前端可视化展示
```

系统各模块分工如下。`scripts/prepare_data.py` 负责原始数据解析、字段清洗、学院识别、统计摘要生成和 Neo4j CSV 生成；`scripts/import_mongodb.py` 负责将论文元数据导入 MongoDB；`scripts/build_vector_index.py` 负责构建论文文本向量索引；`backend/main.py` 使用 FastAPI 提供数据接口；`frontend/index.html`、`frontend/styles.css`、`frontend/app.js` 负责前端页面和交互展示。

从数据库分工来看，MongoDB 负责论文元数据的主存储和聚合统计，Neo4j 负责实体关系和路径分析，向量检索模块负责语义层面的相似论文和相似学者发现，ECharts 负责统计图表和图谱预览。通过多种 NoSQL 相关技术的组合，系统能够同时展示文档存储、图数据库和向量检索在科研数据场景中的作用。

【插入图 3：项目总体架构图。可以使用上面的流程图重新绘制成图片，也可以直接截图报告中的流程图。】

【插入图 4：项目目录截图。建议截取 `backend`、`frontend`、`scripts`、`data`、`docs` 等目录。】

## 四、数据来源与预处理

本项目数据来源为教师提供的 Web of Science 学者科研数据文件 `scholar-data-full.txt`。该文件主要围绕广东工业大学相关学者论文元数据展开，共包含 5000 条论文记录。原始数据采用 Web of Science 纯文本格式，每篇论文由多个字段组成，并以 `ER` 作为单篇记录结束标记。

原始数据中常见字段包括：`AU` 表示作者缩写，`AF` 表示作者全名，`TI` 表示论文标题，`SO` 表示期刊或会议来源，`DE` 表示作者关键词，`ID` 表示 Keywords Plus，`AB` 表示摘要，`C1` 表示作者地址，`C3` 表示机构，`CR` 表示参考文献，`PY` 表示发表年份，`TC` 表示被引次数，`DI` 表示 DOI，`WC` 表示 Web of Science 学科类别，`SC` 表示研究方向，`UT` 表示 WOS 唯一编号。

由于 Web of Science 文本字段存在多行延续情况，直接按行读取会导致标题、摘要、关键词、地址、参考文献等字段被截断。因此，本项目在数据预处理阶段采用字段码识别和缩进行合并的方法：当某一行以两位大写字段码开头时，将其识别为新字段；当某一行以缩进开头时，将其视为上一字段的延续内容。对于作者、机构、参考文献等多值字段，系统保留列表结构；对于关键词、学科类别等分号分隔字段，系统进一步切分为数组。

数据预处理主要包括以下步骤。第一，读取原始文本并按 `ER` 拆分为单篇论文记录。第二，识别并合并多行字段，避免摘要和标题内容丢失。第三，对 `AF`、`AU`、`DE`、`ID`、`C1`、`C3` 等字段进行标准化处理。第四，使用 `UT` 字段作为论文唯一编号；若 `UT` 缺失，则使用 DOI 或序号生成 `paper_id`。第五，从地址字段中提取学院信息，并将英文简称映射为中文学院名称。第六，生成清洗后的 `papers.json`、统计摘要 `summary.json`、扁平化 CSV 和 Neo4j 导入 CSV。

清洗后系统共得到 5000 条有效论文记录。数据统计结果显示，论文数量较多的年份集中在近几年，其中 2022 年 502 篇、2023 年 497 篇、2024 年 630 篇、2025 年 588 篇、2026 年 329 篇。学院维度中，自动化学院 823 篇、计算机学院 513 篇、机电工程学院 484 篇、材料与能源学院 421 篇、信息工程学院 349 篇、物理与光电工程学院 344 篇。关键词维度中，高频关键词包括 deep learning、optimization、feature extraction、mechanical properties、evolutionary algorithm 等。

【插入图 5：原始 `scholar-data-full.txt` 数据截图。建议展示 `AU`、`TI`、`AB`、`DE`、`C1` 等字段。】

【插入图 6：清洗后 `papers.json` 数据截图。建议展示一条论文记录中的 `paper_id`、`title`、`authors`、`keywords`、`year`、`school` 等字段。】

## 五、NoSQL 数据库存储设计

本项目在 Hadoop、Redis、MongoDB 三类技术中选择 MongoDB 作为主存储数据库。选择 MongoDB 的原因主要有三点。第一，Web of Science 科研论文数据属于典型半结构化数据，不同论文可能存在字段缺失或字段数量不同的情况，MongoDB 的文档模型比固定表结构更灵活。第二，论文元数据中包含作者、关键词、机构、参考文献等数组字段，MongoDB 可以直接保存数组和嵌套结构，避免拆分成大量关系表。第三，MongoDB 支持聚合管道和全文索引，适合完成年度趋势、学院发文量、关键词热点等统计分析。

MongoDB 数据库命名为 `nosql_scholar`，核心集合为 `papers`。每篇论文对应一个 MongoDB 文档，主要字段设计如下：

```json
{
  "paper_id": "WOS:001588882900135",
  "title": "论文标题",
  "abstract": "论文摘要",
  "authors": ["作者1", "作者2"],
  "keywords": ["关键词1", "关键词2"],
  "journal": "期刊或会议来源",
  "year": 2025,
  "times_cited": 0,
  "school": "自动化学院",
  "institutions": ["Guangdong University of Technology"],
  "wos_categories": ["Automation & Control Systems"],
  "references": ["参考文献1", "参考文献2"]
}
```

系统通过 `scripts/import_mongodb.py` 完成 MongoDB 导入。导入时采用 `paper_id` 作为唯一键，使用 upsert 方式写入数据，避免重复导入造成重复记录。同时系统创建多个索引，包括 `paper_id` 唯一索引、`year` 年份索引、`school` 学院索引、`authors` 作者索引、`keywords` 关键词索引，以及基于 `title`、`abstract`、`keywords` 的全文索引。

MongoDB 可支持多类典型查询。例如，按年份分组统计年度发文量和被引次数；按学院分组统计学院发文量；展开关键词数组统计高频关键词；按期刊来源分组统计主要发文期刊。这些聚合查询的结果既可用于课程报告分析，也可以作为 Web 前端图表的数据来源。

典型 MongoDB 聚合查询示例如下：

```javascript
db.papers.aggregate([
  { $match: { year: { $ne: null } } },
  {
    $group: {
      _id: "$year",
      count: { $sum: 1 },
      citations: { $sum: "$times_cited" }
    }
  },
  { $sort: { _id: 1 } }
])
```

通过 MongoDB 文档存储，本项目较好地保存了原始论文元数据的字段结构，并为后续统计分析、学者查询和 Web 展示提供了数据基础。

【插入图 7：`scripts/import_mongodb.py` 代码截图。】

【插入图 8：MongoDB Compass 中 `papers` 集合截图。如果没有安装 MongoDB Compass，可改为插入 MongoDB 导入脚本运行截图。】

## 六、数据分析与可视化

本项目使用 Web 前端和 ECharts 对科研数据进行可视化展示。系统实现了总览页面和统计图表页面，图表风格参考 SCI 论文图版进行调整，使用较克制但层次丰富的配色、虚线网格、圆角柱状图和图版编号，使统计结果更适合课程报告和答辩展示。

第一类图表是年度发文趋势与年度被引趋势。该图以年份为横轴，同时展示每年的发文量和被引次数。统计结果显示，广东工业大学相关论文数量在近几年明显增加，2022 年发文 502 篇，2023 年发文 497 篇，2024 年达到 630 篇，2025 年为 588 篇，说明数据集中近年来的科研产出较为集中。从被引趋势看，2021 年被引 6349 次，2022 年被引 7574 次，说明部分较早发表的论文已经形成较高引用积累，而 2025 年和 2026 年论文由于发表时间较近，被引次数相对较低。

【插入图 9：网站首页“年度发文与被引趋势”图。】

第二类图表是学院发文量分析。统计结果显示，自动化学院发文量最高，共 823 篇；计算机学院 513 篇；机电工程学院 484 篇；材料与能源学院 421 篇；信息工程学院 349 篇；物理与光电工程学院 344 篇。这说明自动化、计算机、机电、材料等工科方向是该数据集中科研产出的主要来源，与广东工业大学的工科优势较为一致。

【插入图 10：网站首页“学院发文量”图。】

第三类图表是高频关键词热点分析。关键词统计结果显示，deep learning 出现 85 次，optimization 出现 56 次，feature extraction 出现 48 次，mechanical properties 出现 46 次，evolutionary algorithm 出现 42 次，attention mechanism 出现 34 次，microstructure 出现 32 次，training 出现 30 次，transfer learning 出现 27 次，machine learning 出现 26 次。由此可以看出，人工智能、优化算法、特征提取、材料性能和微观结构等方向是数据集中的主要研究热点。

【插入图 11：统计图表页面“关键词热点 Top 30”图。】

第四类图表是主要期刊来源分布。统计结果显示，论文来源最多的是 IEEE ACCESS，共 50 篇；其次是 CERAMICS INTERNATIONAL，共 44 篇；APPLIED SCIENCES-BASEL 共 39 篇；INFORMATION SCIENCES 共 38 篇；JOURNAL OF ALLOYS AND COMPOUNDS 共 36 篇；APPLIED THERMAL ENGINEERING、JOURNAL OF MATERIALS SCIENCE-MATERIALS IN ELECTRONICS 和 ENERGY 均为 31 篇。期刊分布说明该数据集覆盖电子信息、材料、能源、人工智能等多个学科方向。

【插入图 12：统计图表页面“主要期刊分布”图。】

第五类图表是 Web of Science 学科类别分布。统计结果显示，Engineering, Electrical & Electronic 类别最多，共 1286 篇；Materials Science, Multidisciplinary 为 763 篇；Computer Science, Artificial Intelligence 为 730 篇；Automation & Control Systems 为 505 篇；Computer Science, Information Systems 为 446 篇。该结果进一步说明电子工程、材料科学、人工智能、自动化控制等方向是数据集中的核心学科领域。

【插入图 13：统计图表页面“WOS 学科类别”图。】

第六类图表是合作机构关系分析。该图根据论文机构字段统计不同机构之间的合作关系，用于观察科研合作网络中的主要合作对象。合作机构关系可以帮助发现广东工业大学与其他高校、研究机构或企业之间的科研联系，为后续合作网络分析和潜在合作推荐提供基础。

【插入图 14：统计图表页面“合作机构关系”图。】

## 七、Neo4j 图谱构建与关联分析

本项目使用 Neo4j 构建学术知识图谱。图谱建模的核心思想是将科研论文数据中的对象抽象为节点，将对象之间的联系抽象为关系，从而支持合作网络、关键词关联、学院合作、机构连接度和最短路径等分析。

系统设计了六类节点。`Author` 节点表示学者，主要属性为作者姓名；`Paper` 节点表示论文，主要属性包括论文编号、标题、年份、被引次数、DOI；`Institution` 节点表示机构；`School` 节点表示学院；`Keyword` 节点表示关键词；`Journal` 节点表示期刊或会议来源。

系统设计了六类主要关系。`Author -[:WROTE]-> Paper` 表示作者撰写论文；`Author -[:AFFILIATED_WITH]-> Institution` 表示作者所属机构；`Author -[:BELONGS_TO]-> School` 表示作者隶属学院；`Paper -[:HAS_KEYWORD]-> Keyword` 表示论文包含关键词；`Paper -[:PUBLISHED_IN]-> Journal` 表示论文发表在某一期刊或会议来源中；`Author -[:COAUTHORED]- Author` 表示作者之间存在合作关系。

图谱数据由 `scripts/prepare_data.py` 自动生成，保存到 `data/neo4j` 目录中，包括 `papers.csv`、`authors.csv`、`institutions.csv`、`schools.csv`、`keywords.csv`、`journals.csv` 以及多类关系 CSV。Neo4j 导入脚本位于 `docs/neo4j_import.cypher`。导入时先为各类节点创建唯一约束，再通过 `LOAD CSV WITH HEADERS` 批量导入节点和关系。

典型 Cypher 查询一：查询某学者的合作作者及合作次数。

```cypher
MATCH (a:Author {name: "Liu, Bo"})-[:WROTE]->(p:Paper)<-[:WROTE]-(co:Author)
WHERE co <> a
RETURN co.name AS 合作作者, count(p) AS 合作次数
ORDER BY 合作次数 DESC
LIMIT 20;
```

该查询可以找出指定学者的主要合作对象，并按合作论文数量排序，适合分析核心学者的合作网络。

典型 Cypher 查询二：查询学院之间的合作关系。

```cypher
MATCH (s1:School)<-[:BELONGS_TO]-(a1:Author)-[:WROTE]->(p:Paper)<-[:WROTE]-(a2:Author)-[:BELONGS_TO]->(s2:School)
WHERE s1.name < s2.name
RETURN s1.name AS 学院A, s2.name AS 学院B, count(DISTINCT p) AS 合作论文数
ORDER BY 合作论文数 DESC
LIMIT 20;
```

该查询可以发现不同学院之间的合作强度，适合分析校内跨学院科研合作情况。

典型 Cypher 查询三：查询某关键词相关的核心学者。

```cypher
MATCH (k:Keyword {name: "deep learning"})<-[:HAS_KEYWORD]-(p:Paper)<-[:WROTE]-(a:Author)
RETURN a.name AS 学者, count(p) AS 论文数, sum(p.times_cited) AS 总被引
ORDER BY 论文数 DESC, 总被引 DESC
LIMIT 20;
```

该查询可以找出某一研究主题下的核心学者和代表性产出，适合用于研究热点分析。

典型 Cypher 查询四：查询两位学者之间的最短合作路径。

```cypher
MATCH path = shortestPath(
  (a:Author {name: "Liu, Bo"})-[:COAUTHORED*..6]-(b:Author {name: "Wang, Bo"})
)
RETURN path;
```

该查询可以判断两位学者之间是否存在直接或间接合作联系，体现图数据库在路径分析方面的优势。

典型 Cypher 查询五：查询机构在合作网络中的连接地位。

```cypher
MATCH (i:Institution)<-[:AFFILIATED_WITH]-(a:Author)-[:WROTE]->(p:Paper)
RETURN i.name AS 机构, count(DISTINCT a) AS 学者数, count(DISTINCT p) AS 论文数
ORDER BY 学者数 DESC, 论文数 DESC
LIMIT 20;
```

该查询可以发现合作网络中连接度较高的机构，有助于分析科研合作中的重要机构节点。

【插入图 15：网站“知识图谱”页面截图。】

【插入图 16：Neo4j Browser 图谱可视化截图。如果未导入 Neo4j，可插入 `docs/neo4j_import.cypher` 和 `docs/cypher_queries.md` 的截图。】

## 八、实体提取方法说明

为了保证实体提取的准确性，本项目采用“结构化字段优先 + 规则清洗 + 标准化映射”的方法，而不是直接从摘要自由文本中进行不稳定抽取。Web of Science 数据本身已经提供了较完整的结构化字段，因此优先使用这些字段可以减少实体识别误差。

作者实体主要来自 `AF` 字段，该字段通常保存作者全名，比 `AU` 作者缩写更适合作为 Author 节点名称。论文实体由 `UT` 字段构造唯一编号，如果 `UT` 缺失，则使用 DOI 或序号生成 `paper_id`。关键词实体主要来自 `DE` 字段，并辅助使用 `ID` 字段。期刊实体来自 `SO` 字段。机构实体来自 `C3` 字段，并结合 `C1` 地址字段进行补充。

学院实体的提取相对复杂，因为 Web of Science 地址字段中常使用英文缩写。本项目从 `C1` 地址中提取 `Guangdong Univ Technol` 后面的学院短语，并建立英文简称到中文学院名称的映射表。例如，`Sch Automat`、`Fac Automat`、`Coll Automat` 统一映射为“自动化学院”；`Sch Mat & Energy` 映射为“材料与能源学院”；`Sch Electromech Engn` 映射为“机电工程学院”；`Sch Comp Sci & Technol` 和 `Sch Comp` 映射为“计算机学院”；`Sch Informat Engn` 映射为“信息工程学院”。

对于无法准确识别的学院，系统不会随意推断，而是保留原始短语或标记为“未知学院”。这样既避免了错误归类，也便于后续人工核验和补充规则。从统计结果看，系统已经能够识别自动化学院、计算机学院、机电工程学院、材料与能源学院、信息工程学院、物理与光电工程学院等主要学院，为学院维度分析提供了数据基础。

在实体清洗过程中，系统还对空格、标点、大小写进行了统一处理。例如，关键词统计时统一转为小写，减少 `Deep Learning` 和 `deep learning` 被统计为两个不同关键词的情况；机构字段中对明显被错误切分的短语进行过滤；作者字段保留原始姓名格式，避免因过度处理导致同名学者混淆。

【插入图 17：`scripts/prepare_data.py` 中学院映射表和实体提取函数截图。】

## 九、向量化与 FAISS 分析设计

本项目在向量化与语义分析模块中，将论文标题、摘要、关键词和 Keywords Plus 拼接为论文语义文本，并基于这些文本构建向量索引。相比只使用论文标题，标题加摘要和关键词能够更完整地表达论文研究主题，从而提高相似论文检索的效果。

向量化对象主要包括两类。第一类是论文文本向量，即将每篇论文的标题、摘要、关键词拼接后进行向量化，用于相似论文检索。第二类是作者画像向量，即将某位作者多篇论文的标题、摘要、关键词拼接为作者研究画像，用于相似学者发现。

系统代码位于 `backend/vector_search.py` 和 `scripts/build_vector_index.py`。系统优先检测运行环境中是否安装 FAISS。如果安装了 `faiss-cpu`，则使用 FAISS 的 `IndexFlatIP` 构建内积相似度索引，并将索引保存到 `data/faiss/paper_faiss.index`。如果当前环境暂未安装 FAISS，系统会使用 scikit-learn 的文本向量化和余弦相似度作为兜底方案，保证向量检索页面可以正常运行。该设计既满足课程中向量数据库与 FAISS 的设计要求，也保证了项目展示的稳定性。

相似论文检索的基本流程如下。用户在网站“向量检索”页面输入研究主题，例如 `deep learning optimization artificial intelligence`；系统将输入文本转换为查询向量；然后与论文向量索引进行相似度计算；最后返回相似度最高的论文列表，包括论文标题、年份、期刊、关键词和相似度分数。

相似学者发现的基本流程如下。系统将每位作者参与发表的多篇论文标题、摘要和关键词拼接为作者画像文本，然后计算不同作者画像之间的相似度。用户输入某位学者姓名后，系统返回研究方向相近的学者。这一结果可以进一步与 Neo4j 合作关系结合，用于发现“研究方向相似但尚未合作”的潜在合作对象。

本项目的向量检索模块实现了图谱关系分析之外的语义分析能力。图数据库更关注显式关系，例如是否共同发表论文；向量检索更关注隐含语义，例如研究主题是否相似。二者结合后，可以从“已有合作关系”和“潜在语义相似关系”两个角度分析科研合作。

【插入图 18：网站“向量检索”页面截图，展示相似论文检索结果。】

【插入图 19：网站“相似学者”检索结果截图。】

【插入图 20：`scripts/build_vector_index.py` 或 `backend/vector_search.py` 中向量索引构建代码截图。】

## 十、系统实现过程与结果展示

本项目最终实现了一个完整的 Web 展示系统，目录结构如下：

```text
nosql_scholar_system
├── backend              FastAPI 后端接口
├── frontend             前端页面、样式和交互脚本
├── scripts              数据处理、MongoDB 导入、向量索引构建脚本
├── data
│   ├── processed         清洗后的 JSON/CSV 数据
│   ├── neo4j             Neo4j 导入 CSV
│   └── faiss             向量索引和元数据
├── docs                 报告素材、Cypher 查询、部署说明
├── README.md
├── requirements.txt
└── run_server.ps1
```

系统后端采用 FastAPI 实现，主要接口包括 `/api/summary`、`/api/papers`、`/api/authors/{author_name}`、`/api/graph-preview`、`/api/vector/papers`、`/api/vector/authors` 等。其中 `/api/summary` 返回论文总数、作者数量、关键词数量、期刊数量和各类统计图表数据；`/api/authors/{author_name}` 返回学者画像；`/api/vector/papers` 返回相似论文检索结果；`/api/vector/authors` 返回相似学者结果。

前端网站包含五个页面。总览页面展示广东工业大学科研数据系统的校园主题头图、核心指标卡、研究流程和主要图表；统计图表页面展示关键词热点、主要期刊、WOS 学科类别和合作机构关系；学者画像页面支持输入作者姓名，查看论文数量、被引次数、学术年龄、合作作者、关键词和代表论文；知识图谱页面展示高被引论文子图预览和代表性 Cypher 查询；向量检索页面支持相似论文检索和相似学者发现。

系统本地运行方式如下：

```powershell
cd D:\learn\NoSQL\nosql_scholar_system
python scripts\prepare_data.py --input "C:\Users\zyt18\Downloads\scholar-data-full.txt"
python scripts\build_vector_index.py
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

运行后在浏览器访问：

```text
http://127.0.0.1:8000
```

需要说明的是，`127.0.0.1` 是本机地址，只能在本机访问，并不是公网地址。如果需要让教师通过外网访问，可以进一步使用云服务器部署或内网穿透工具。本项目当前提交版本主要提供本地可运行系统、项目源代码、数据处理结果、Neo4j 脚本、报告素材和部署说明。

【插入图 21：系统首页完整截图。】

【插入图 22：统计图表页面截图。】

【插入图 23：学者画像页面截图。建议查询 `Liu, Bo`。】

【插入图 24：知识图谱页面截图。】

【插入图 25：向量检索页面截图。】

【插入图 26：系统运行终端截图。建议展示 `uvicorn backend.main:app --host 127.0.0.1 --port 8000` 运行成功。】

## 十一、总结与心得体会

通过本次课程项目，我对 NoSQL 数据库在科研数据场景中的应用有了更加具体的理解。科研论文数据不仅包含标题、摘要、关键词等文本字段，还包含作者、机构、学院、期刊、引用文献等复杂关系。单一数据库很难完整表达这些不同类型的数据需求，因此需要根据不同任务选择合适的 NoSQL 技术。

MongoDB 适合保存 Web of Science 这类半结构化论文元数据。由于每篇论文的字段不完全相同，文档数据库可以灵活保存不同字段，同时保留作者、关键词、机构等数组结构，便于后续统计分析。Neo4j 适合表达作者、论文、机构、学院、关键词和期刊之间的复杂关系，能够直观支持合作网络、最短路径、核心学者等图分析任务。向量检索则可以从语义层面发现相似论文和相似学者，弥补传统关键词检索只关注字面匹配的不足。

本项目中遇到的主要困难包括 Web of Science 多行字段解析、学院名称标准化、Neo4j 三元组构建、向量索引环境兼容和前端综合展示。针对多行字段解析问题，系统通过字段码识别和缩进行合并解决；针对学院名称标准化问题，系统建立英文简称到中文学院的映射表；针对向量检索环境问题，系统设计了 FAISS 优先、余弦相似度兜底的方式，保证系统在不同环境下都能运行。

从系统实现效果看，本项目已经完成课程设计任务书中的主要要求，包括 NoSQL 主存储、统计图表、Neo4j 图谱、向量检索和 Web 展示。后续如果继续改进，可以从以下几个方面进行：第一，将系统部署到公网服务器，方便教师远程访问；第二，引入更强的文本嵌入模型，例如 Sentence-BERT，提高相似论文检索效果；第三，进一步完善作者消歧算法，减少同名作者造成的误差；第四，将 Neo4j 合作关系和向量相似度结合，形成更完整的潜在合作推荐模块。

## 十二、参考文献

[1] MongoDB Documentation. Aggregation Operations and Indexes. MongoDB Inc.

[2] Neo4j Documentation. Cypher Query Language Manual. Neo4j Graph Data Platform.

[3] Johnson J, Douze M, Jegou H. Billion-scale similarity search with GPUs. IEEE Transactions on Big Data, 2019.

[4] Facebook AI Similarity Search Documentation. FAISS: A library for efficient similarity search and clustering of dense vectors.

[5] Apache ECharts Documentation. ECharts: An Open Source JavaScript Visualization Library.

[6] Clarivate. Web of Science Core Collection Field Tags.

[7] 《NoSQL 数据库》课程资料，广东工业大学。

## 十三、附录

本项目提交材料包括课程报告文档、项目源代码、数据处理脚本、前端展示系统、Neo4j 导入脚本、Cypher 查询语句和部署说明。

项目主要文件说明如下：

```text
backend/main.py                    FastAPI 后端入口
backend/data_store.py              本地数据读取和学者画像接口
backend/vector_search.py           向量检索模块
frontend/index.html                前端页面结构
frontend/styles.css                前端样式文件
frontend/app.js                    前端交互和图表渲染
scripts/prepare_data.py            WOS 数据解析与清洗脚本
scripts/import_mongodb.py          MongoDB 导入脚本
scripts/build_vector_index.py      向量索引构建脚本
data/processed/papers.json         清洗后的论文数据
data/processed/summary.json        统计摘要数据
data/neo4j/*.csv                   Neo4j 导入 CSV 文件
docs/neo4j_import.cypher           Neo4j 导入脚本
docs/cypher_queries.md             图数据库分析查询语句
docs/deployment.md                 部署与运行说明
docs/video_script.md               视频讲解稿
```

系统运行环境主要包括 Python、FastAPI、ECharts、MongoDB、Neo4j 和向量检索相关依赖。若需要启动本地系统，可进入项目目录后执行 `run_server.ps1`，或按照 `docs/deployment.md` 中的步骤手动运行。

【插入图 27：项目压缩包或项目目录截图。】

【插入图 28：`docs/deployment.md` 部署说明截图。】
