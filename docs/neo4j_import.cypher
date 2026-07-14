CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.paper_id IS UNIQUE;
CREATE CONSTRAINT author_id IF NOT EXISTS FOR (a:Author) REQUIRE a.author_id IS UNIQUE;
CREATE CONSTRAINT institution_id IF NOT EXISTS FOR (i:Institution) REQUIRE i.institution_id IS UNIQUE;
CREATE CONSTRAINT school_id IF NOT EXISTS FOR (s:School) REQUIRE s.school_id IS UNIQUE;
CREATE CONSTRAINT keyword_id IF NOT EXISTS FOR (k:Keyword) REQUIRE k.keyword_id IS UNIQUE;
CREATE CONSTRAINT journal_id IF NOT EXISTS FOR (j:Journal) REQUIRE j.journal_id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///papers.csv' AS row
MERGE (p:Paper {paper_id: row.paper_id})
SET p.title = row.title,
    p.year = CASE row.year WHEN '' THEN null ELSE toInteger(row.year) END,
    p.times_cited = CASE row.times_cited WHEN '' THEN 0 ELSE toInteger(row.times_cited) END,
    p.doi = row.doi;

LOAD CSV WITH HEADERS FROM 'file:///authors.csv' AS row
MERGE (a:Author {author_id: row.author_id})
SET a.name = row.name;

LOAD CSV WITH HEADERS FROM 'file:///institutions.csv' AS row
MERGE (i:Institution {institution_id: row.institution_id})
SET i.name = row.name;

LOAD CSV WITH HEADERS FROM 'file:///schools.csv' AS row
MERGE (s:School {school_id: row.school_id})
SET s.name = row.name;

LOAD CSV WITH HEADERS FROM 'file:///keywords.csv' AS row
MERGE (k:Keyword {keyword_id: row.keyword_id})
SET k.name = row.name;

LOAD CSV WITH HEADERS FROM 'file:///journals.csv' AS row
MERGE (j:Journal {journal_id: row.journal_id})
SET j.name = row.name;

LOAD CSV WITH HEADERS FROM 'file:///rel_wrote.csv' AS row
MATCH (a:Author {author_id: row.author_id})
MATCH (p:Paper {paper_id: row.paper_id})
MERGE (a)-[:WROTE]->(p);

LOAD CSV WITH HEADERS FROM 'file:///rel_affiliated_with.csv' AS row
MATCH (a:Author {author_id: row.author_id})
MATCH (i:Institution {institution_id: row.institution_id})
MERGE (a)-[:AFFILIATED_WITH]->(i);

LOAD CSV WITH HEADERS FROM 'file:///rel_belongs_to.csv' AS row
MATCH (a:Author {author_id: row.author_id})
MATCH (s:School {school_id: row.school_id})
MERGE (a)-[:BELONGS_TO]->(s);

LOAD CSV WITH HEADERS FROM 'file:///rel_has_keyword.csv' AS row
MATCH (p:Paper {paper_id: row.paper_id})
MATCH (k:Keyword {keyword_id: row.keyword_id})
MERGE (p)-[:HAS_KEYWORD]->(k);

LOAD CSV WITH HEADERS FROM 'file:///rel_published_in.csv' AS row
MATCH (p:Paper {paper_id: row.paper_id})
MATCH (j:Journal {journal_id: row.journal_id})
MERGE (p)-[:PUBLISHED_IN]->(j);

LOAD CSV WITH HEADERS FROM 'file:///rel_coauthored.csv' AS row
MATCH (a1:Author {author_id: row.author_a})
MATCH (a2:Author {author_id: row.author_b})
MERGE (a1)-[r:COAUTHORED]-(a2)
ON CREATE SET r.paper_ids = [row.paper_id], r.weight = 1
ON MATCH SET r.paper_ids = CASE WHEN row.paper_id IN r.paper_ids THEN r.paper_ids ELSE r.paper_ids + row.paper_id END,
             r.weight = size(r.paper_ids);

