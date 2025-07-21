# Elasticsearch 笔记

## 1. 基本理论原理
Elasticsearch 是一个分布式搜索和分析引擎，基于 Lucene 构建。
- **核心机制**: 倒排索引（Inverted Index），类似书的索引页，记录词和文档的映射，搜索时直接查词。
- **分布式**: 数据分片存储在多个节点，查询并行处理。
- **近实时**: 数据写入后默认 1 秒可查。
- **RESTful**: 用 HTTP 接口（GET、PUT、POST 等）操作。

**工作流程**:
1. 数据存入索引。
2. 分词（Analyzer 切词）。
3. 构建倒排索引。
4. 查询时匹配词，返回结果。

---

## 2. 基本结构
Elasticsearch 的数据组织层次：
- **集群（Cluster）**: 多节点组成，共享数据。
- **节点（Node）**: 一台服务器，负责存储和计算。
- **索引（Index）**: 数据集合，类似数据库表。
- **分片（Shard）**: 索引分成小块。
  - **主分片（Primary Shard）**: 原始数据。
  - **副本分片（Replica Shard）**: 备份。
- **文档（Document）**: 最小单位，JSON 格式。

---

## 3. 存储模型
Elasticsearch 的存储基于 Lucene，设计高效搜索和扩展性。

### 3.1 存储原理
- **倒排索引**:
  
  - 例子：
    ```json
    {"id": 1, "name": "小明 在家"}
    {"id": 2, "name": "小红 在学校"}
    ```
  - 分词后：
    ```
    词       文档 ID
    小明     1
    在家     1
    小红     2
    在学校   2
    ```
  - 搜索 "小明" → 文档 1。
- **分片机制**:
  - 索引分成多个分片，文档按 ID 哈希分配。
  - 副本分片备份数据，分散到其他节点。
- **文件存储**:
  
  - 用 Lucene 格式（`.fdt`, `.fdx`）存磁盘。
  - 每个分片是一个 Lucene 索引。

### 3.2 写入流程
1. 客户端发文档到协调节点。
2. 根据 ID 计算分片。
3. 写入主分片内存，同步副本。
4. 刷新（默认 1 秒）后可查。
5. 定期合并成磁盘段（不可变）。

### 3.3 查询流程
1. 客户端发查询到协调节点。
2. 广播到相关分片。
3. 分片并行查询。
4. 合并结果返回。

### 3.4 特点
- **不可变性**: 段只新增，更新靠标记删除。
- **分布式**: 分片分散，副本保证高可用。
- **近实时**: 写入到查询有短暂延迟。

---

## 4. 基本语法
Elasticsearch 用 REST API 操作，数据用 JSON。

### 4.1 创建索引
```bash
PUT /myindex
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "age": { "type": "integer" }
    }
  }
}
```

### 4.2 插入文档
- 指定 ID:
```bash
PUT /myindex/_doc/1
{
  "name": "小明",
  "age": 25
}
```
- 自动 ID:
```bash
POST /myindex/_doc
{
  "name": "小红",
  "age": 30
}
```

### 4.3 查询文档
```bash
GET /myindex/_doc/1
```
**返回**:
```json
{
  "_index": "myindex",
  "_id": "1",
  "_source": { "name": "小明", "age": 25 }
}
```

### 4.4 搜索
- 精确查（`term`）:
```bash
POST /myindex/_search
{
  "query": { "term": { "age": 25 } }
}
```
- 模糊查（`match`）:
```bash
POST /myindex/_search
{
  "query": { "match": { "name": "小明" } }
}
```
- 多条件（`bool`）:
```bash
POST /myindex/_search
{
  "query": {
    "bool": {
      "filter": [
        { "term": { "age": 25 } },
        { "match": { "name": "小明" } }
      ]
    }
  }
}
```

### 4.5 更新
- 全量替换:
```bash
PUT /myindex/_doc/1
{
  "name": "小明",
  "age": 26
}
```
- 部分更新:
```bash
POST /myindex/_update/1
{
  "doc": { "age": 26 }
}
```

### 4.6 删除
- 文档:
```bash
DELETE /myindex/_doc/1
```
- 索引:
```bash
DELETE /myindex
```

### 4.7 批量操作
```bash
POST /_bulk
{"index": {"_index": "myindex", "_id": "1"}}
{"name": "小明", "age": 25}
{"index": {"_index": "myindex", "_id": "2"}}
{"name": "小红", "age": 30}
```

---

## 5. Java 集成
用 `RestHighLevelClient`（7.x）操作。

### 5.1 依赖（Maven）
```xml
<dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>elasticsearch-rest-high-level-client</artifactId>
    <version>7.17.9</version>
</dependency>
```

### 5.2 示例代码
```java
import org.apache.http.HttpHost;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.client.RestClient;
import org.elasticsearch.client.RestHighLevelClient;

public class ElasticsearchExample {
    public static void main(String[] args) throws Exception {
        RestHighLevelClient client = new RestHighLevelClient(
                RestClient.builder(new HttpHost("localhost", 9200, "http")));
        
        IndexRequest request = new IndexRequest("myindex")
                .id("1")
                .source("name", "小明", "age", 25);
        
        client.index(request, RequestOptions.DEFAULT);
        client.close();
    }
}
```

---

## 6. MySQL 集成
同步 MySQL 数据到 Elasticsearch。

### 6.1 用 Logstash
**配置** `logstash.conf`:
```
input {
  jdbc {
    jdbc_driver_library => "mysql-connector-java-8.0.28.jar"
    jdbc_driver_class => "com.mysql.cj.jdbc.Driver"
    jdbc_connection_string => "jdbc:mysql://localhost:3306/mydb"
    jdbc_user => "root"
    jdbc_password => "password"
    statement => "SELECT id, name, age FROM users"
  }
}
output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "myindex"
    document_id => "%{id}"
  }
}
```
**运行**:
```bash
logstash -f logstash.conf
```

### 6.2 用 Java
```java
import java.sql.*;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.action.index.IndexRequest;

public class MySQLToElasticsearch {
    public static void main(String[] args) throws Exception {
        Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/mydb", "root", "password");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT id, name, age FROM users");

        RestHighLevelClient client = new RestHighLevelClient(
                RestClient.builder(new HttpHost("localhost", 9200, "http")));

        while (rs.next()) {
            IndexRequest request = new IndexRequest("myindex")
                    .id(rs.getString("id"))
                    .source("name", rs.getString("name"), "age", rs.getInt("age"));
            client.index(request, RequestOptions.DEFAULT);
        }

        rs.close();
        stmt.close();
        conn.close();
        client.close();
    }
}
```

---

## 总结
- **理论**: 倒排索引 + 分布式。
- **结构**: 集群 > 节点 > 索引 > 分片 > 文档。
- **存储**: 分片 + 不可变段 + 近实时。
- **语法**: REST API + JSON。
- **集成**: Java 用客户端，MySQL 用 Logstash 或代码。

这份笔记已经融合所有内容，如果需要调整或补充某部分，告诉我！