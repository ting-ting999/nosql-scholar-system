# Neo4j 关联分析查询

## 1. 某学者的合作作者及合作次数

```cypher
MATCH (a:Author {name: "Liu, Bo"})-[:WROTE]->(p:Paper)<-[:WROTE]-(co:Author)
WHERE co <> a
RETURN co.name AS 合作作者, count(p) AS 合作次数
ORDER BY 合作次数 DESC
LIMIT 20;
```

## 2. 某学院与其他学院的合作关系

```cypher
MATCH (s1:School)<-[:BELONGS_TO]-(a1:Author)-[:WROTE]->(p:Paper)<-[:WROTE]-(a2:Author)-[:BELONGS_TO]->(s2:School)
WHERE s1.name < s2.name
RETURN s1.name AS 学院A, s2.name AS 学院B, count(DISTINCT p) AS 合作论文数
ORDER BY 合作论文数 DESC
LIMIT 20;
```

## 3. 某关键词相关的核心学者与代表论文

```cypher
MATCH (k:Keyword {name: "deep learning"})<-[:HAS_KEYWORD]-(p:Paper)<-[:WROTE]-(a:Author)
RETURN a.name AS 学者, count(p) AS 论文数, sum(p.times_cited) AS 总被引
ORDER BY 论文数 DESC, 总被引 DESC
LIMIT 20;
```

## 4. 两位学者之间的最短合作路径

```cypher
MATCH path = shortestPath(
  (a:Author {name: "Liu, Bo"})-[:COAUTHORED*..6]-(b:Author {name: "Wang, Bo"})
)
RETURN path;
```

## 5. 某机构在合作网络中的连接地位

```cypher
MATCH (i:Institution)<-[:AFFILIATED_WITH]-(a:Author)-[:WROTE]->(p:Paper)
RETURN i.name AS 机构, count(DISTINCT a) AS 学者数, count(DISTINCT p) AS 论文数
ORDER BY 学者数 DESC, 论文数 DESC
LIMIT 20;
```

## 6. 高被引论文与关键词关系

```cypher
MATCH (p:Paper)-[:HAS_KEYWORD]->(k:Keyword)
WHERE p.times_cited >= 20
RETURN k.name AS 关键词, count(p) AS 高被引论文数, sum(p.times_cited) AS 总被引
ORDER BY 高被引论文数 DESC, 总被引 DESC
LIMIT 20;
```

## 7. 期刊中的核心发文学院

```cypher
MATCH (s:School)<-[:BELONGS_TO]-(a:Author)-[:WROTE]->(p:Paper)-[:PUBLISHED_IN]->(j:Journal)
WITH j, s, count(DISTINCT p) AS paper_count
ORDER BY paper_count DESC
RETURN j.name AS 期刊, collect({school: s.name, count: paper_count})[0..5] AS 主要学院
LIMIT 10;
```

