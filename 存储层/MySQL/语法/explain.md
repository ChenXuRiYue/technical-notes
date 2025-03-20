# 1. `EXPLAIN` 的基本语法
在 MySQL 中，`EXPLAIN` 的基本用法是在 SQL 语句前加上 `EXPLAIN` 关键字。完整语法如下：

```sql
EXPLAIN [FORMAT = {TRADITIONAL | JSON | TREE}] <SQL语句>;
```

#### 组成部分
- **`EXPLAIN`**：核心关键字，用于触发执行计划分析。
- **`FORMAT`**（可选）：指定输出格式，MySQL 8.0+ 支持以下选项：
  - `TRADITIONAL`：默认格式，以表格形式输出（早期版本的唯一格式）。
  - `JSON`：以 JSON 格式输出，包含更详细的信息。
  - `TREE`：以树形结构输出，更加直观地展示查询执行的层次关系。
- **`<SQL语句>`**：要分析的 SQL 查询，支持 `SELECT`、`INSERT`、`UPDATE`、`DELETE` 等（但最常用的是 `SELECT`）。

#### 示例
```sql
EXPLAIN SELECT * FROM users WHERE age > 30;
```
```sql
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE age > 30;
```
```sql
EXPLAIN FORMAT=TREE SELECT * FROM users WHERE age > 30;
```

---

# 2. 支持的 SQL 语句
`EXPLAIN` 可以分析以下类型的 SQL 语句：
- **SELECT**：最常用的场景，用于分析查询的执行计划。
- **INSERT/UPDATE/DELETE**：可以分析这些语句的执行计划，但通常只显示涉及的表扫描部分（例如 `WHERE` 条件的执行方式）。
- **TABLE**（MySQL 8.0.19+）：直接指定表名，用于检查表的访问方式。
  ```sql
  EXPLAIN TABLE users;
  ```

**注意**：`EXPLAIN` 不会实际执行查询，而是模拟优化器如何规划执行。

---

# 3. 输出格式详解
`EXPLAIN` 的输出取决于 `FORMAT` 参数，下面分别介绍三种格式：

#### (1) `FORMAT = TRADITIONAL`（默认表格格式）
这是 MySQL 的传统输出方式，以表格形式展示执行计划。每一行代表查询中涉及的一个表或操作。常见字段包括：
- **`id`**：查询的标识符，标识子查询的执行顺序。
- **`select_type`**：查询类型（前面已详细介绍，如 `SIMPLE`、`PRIMARY` 等）。
- **`table`**：涉及的表名或别名。
- **`partitions`**：涉及的分区（如果使用了分区表）。
- **`type`**：访问类型（如 `ALL`、`index`、`range` 等）。
- **`possible_keys`**：可能使用的索引。
- **`key`**：实际使用的索引。
- **`key_len`**：使用的索引长度。
- **`ref`**：引用列或常量。
- **`rows`**：预计扫描的行数。
- **`filtered`**：过滤后的行数百分比。
- **`Extra`**：附加信息（如 `Using index`、`Using temporary` 等）。

**示例输出**：
```sql
EXPLAIN SELECT * FROM users WHERE age > 30;
```
```
id | select_type | table | type | possible_keys | key  | rows | Extra
1  | SIMPLE      | users | ALL  | NULL          | NULL | 1000 | Using where
```

#### (2) `FORMAT = JSON`
JSON 格式提供了更详细的信息，适合复杂查询的分析。它将执行计划组织为嵌套结构，包含成本估算和更多优化器细节。

**示例输出**（简化版）：
```sql
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE age > 30;
```
```json
{
  "query_block": {
    "select_id": 1,
    "cost_info": {
      "query_cost": "123.45"
    },
    "table": {
      "table_name": "users",
      "access_type": "ALL",
      "rows_examined_per_scan": 1000,
      "rows_produced_per_join": 333,
      "filtered": "33.33",
      "cost_info": {
        "read_cost": "100.00",
        "eval_cost": "23.45"
      },
      "used_columns": ["id", "name", "age"],
      "attached_condition": "(`users`.`age` > 30)"
    }
  }
}
```
- **优点**：包含成本信息（`cost_info`）和更细粒度的执行细节。
- **适用场景**：调试复杂查询或需要精确性能分析时。

#### (3) `FORMAT = TREE`（MySQL 8.0.21+）
树形格式以文本形式展示执行计划的层次结构，更加直观，适合理解查询的执行顺序。

**示例输出**：
```sql
EXPLAIN FORMAT=TREE SELECT * FROM users WHERE age > 30;
```
```
-> Filter: (users.age > 30)  (cost=123.45 rows=333)
    -> Table scan on users  (cost=100.00 rows=1000)
```
- **优点**：清晰展示执行步骤的嵌套关系。
- **适用场景**：快速理解查询的逻辑流程。

---

# 4. 扩展用法
MySQL 还提供了一些变体或增强功能：

#### (1) `EXPLAIN ANALYZE`（MySQL 8.0.18+）
- **语法**：
  ```sql
  EXPLAIN ANALYZE <SQL语句>;
  ```
- **功能**：不仅显示执行计划，还会实际执行查询并返回运行时的统计信息（如实际行数、循环次数等）。
- **输出示例**：
  ```sql
  EXPLAIN ANALYZE SELECT * FROM users WHERE age > 30;
  ```
  ```
  -> Filter: (users.age > 30)  (cost=123.45 rows=333) (actual time=0.123..0.456 rows=350 loops=1)
      -> Table scan on users  (cost=100.00 rows=1000) (actual time=0.100..0.300 rows=1000 loops=1)
  ```
- **适用场景**：需要对比优化器的估计和实际执行情况时。

#### (2) `EXPLAIN FOR CONNECTION`
- **语法**：
  ```sql
  EXPLAIN FOR CONNECTION <connection_id>;
  ```
- **功能**：分析某个正在运行的连接的执行计划。
- **使用场景**：调试长时间运行的查询。

---

# 5. 注意事项
- **权限**：需要对涉及的表有 `SELECT` 权限。
- **限制**：`EXPLAIN` 是基于优化器的估计，可能与实际执行略有差异（尤其在数据量大或统计信息不准确时）。
- **版本差异**：不同 MySQL 版本支持的字段和格式可能不同（如 `filtered` 在 5.7+ 引入，`TREE` 在 8.0.21+ 引入）。

---

# 6. 实践建议
如果你想深入学习 `EXPLAIN` 的语法和应用，可以尝试以下步骤：
1. 准备一个简单的表和查询，运行 `EXPLAIN` 并观察默认输出。
2. 修改 `FORMAT` 参数，比较 `TRADITIONAL`、`JSON` 和 `TREE` 的差异。
3. 添加索引或调整查询，再次运行 `EXPLAIN`，观察执行计划的变化。



# 7. 困惑总结

## 7.1 字段设计

主要困惑在于 这个 执行计划 explain 的理解。 为什么这样设计？ 通过 展示的字段可以看出什么信息？

### **type 中有一个 ref 和 表头中的ref 是一回事吗？**

这两者**不是一回事**，它们在功能和含义上完全不同。

(1) **type 列中的 ref**

- **位置**：出现在 EXPLAIN 的 type 列中，是访问类型的一种选项。
- **含义**：表示 MySQL 使用**非唯一索引**通过与某个值（常量或前表列）匹配来查找表中的行。
- **上下文**：描述访问方式，属于优化器选择的数据检索策略。
- **常见值**：ALL, index, ref, eq_ref, const 等，ref 是其中之一。

(2) **表头中的 ref 列**

- **位置**：出现在 EXPLAIN 输出的一列，通常在 key_len 之后。
- **含义**：表示当前表在执行索引查找时，**具体引用的值或列**，也就是匹配索引的“输入”。
- **上下文**：与 key 字段配合，说明索引如何被使用。
- **常见值**：const, 表名.列名（如 mysql_learn.o.order_id）, NULL 等。

### type 中 ALL、index、rang、ref 之间的差别

 [explain_type.md](explain_type.md) 
