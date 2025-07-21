

### **完整的 `type` 类型列表**
1. **ALL（全表扫描）**
   - 扫描整个表，效率最低。

2. **index（索引全扫描）**
   
   - 扫描整个索引，效率中等。 （找到了叶子节点然后一路向后遍历直到叶子终点。）
   
3. **range（范围扫描）**
   
   - 通过索引扫描范围内的数据，效率较高。
   
4. **ref（非唯一索引等值匹配）**
   - 已解释：通过非唯一索引进行等值匹配，效率很高。

5. **eq_ref（唯一索引等值匹配）**
   - **含义**: 使用唯一索引（或主键）进行等值匹配，每次查找只返回一行数据。
   - **特点**: 
     - 常用于联表查询（JOIN），通过主键或唯一索引匹配。
     - 效率非常高，因为每次匹配的结果是唯一的。
   - **示例**: 
     ```sql
     EXPLAIN SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
     ```
     如果 `user_id` 是唯一索引，`type` 会是 `eq_ref`。
   - **性能**: 比 `ref` 更高，因为返回的行数固定为 1。

6. **const（常量级别查询）**
   - **含义**: 查询条件是常量，且通过主键或唯一索引直接定位到一行数据。
   - **特点**: 
     - 查询结果在优化阶段就确定，只访问一行。
     - 通常用于 `WHERE` 条件直接指定主键或唯一索引的情况。
   - **示例**: 
     ```sql
     EXPLAIN SELECT * FROM users WHERE id = 1;
     ```
     如果 `id` 是主键，`type` 会是 `const`。
   - **性能**: 最高，几乎没有额外开销。

7. **system（系统表查询）**
   - **含义**: 表只有一行数据（通常是系统表），直接返回结果。
   - **特点**: 
     - 比 `const` 更特殊，仅适用于特殊表（如 MyISAM 的系统表）。
     - 实际中很少见，因为普通表很少只有一行。
   - **性能**: 最高，与 `const` 类似。

8. **NULL（无需访问表或索引）**
   - **含义**: 查询无需访问表或索引，优化阶段就能得出结果。
   - **特点**: 
     - 通常出现在非常简单的查询中，比如直接计算或使用元数据。
   - **示例**: 
     ```sql
     EXPLAIN SELECT MAX(id) FROM users WHERE 1 = 0;
     ```
     如果条件永远不成立，可能是 `NULL`。
   - **性能**: 理论上最优，因为不涉及任何数据访问。

9. **index_merge（索引合并）**
   - **含义**: 查询使用了多个索引，通过合并（交集或并集）获取结果。
   - **特点**: 
     - 数据库分别扫描多个索引，然后合并结果。
     - 通常出现在查询条件涉及多个索引字段时。
   - **示例**: 
     ```sql
     EXPLAIN SELECT * FROM users WHERE age > 20 AND status = 'active';
     ```
     如果 `age` 和 `status` 各有索引，可能是 `index_merge`。
   - **性能**: 取决于合并的复杂度和数据量，通常比 `range` 低。

10. **unique_subquery（唯一子查询）**
    - **含义**: 在子查询中使用了唯一索引进行等值匹配。
    - **特点**: 
      - 常出现在 `IN` 子查询中，且子查询结果通过唯一索引优化。
    - **示例**: 
      ```sql
      EXPLAIN SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE order_date = '2023-01-01');
      ```
      如果 `user_id` 是唯一索引，可能是 `unique_subquery`。
    - **性能**: 较高，与 `eq_ref` 类似。

11. **index_subquery（非唯一索引子查询）**
    - **含义**: 类似 `unique_subquery`，但使用的是非唯一索引。
    - **特点**: 返回多行数据，效率略低于 `unique_subquery`。
    - **示例**: 同上，但 `user_id` 是非唯一索引。
    - **性能**: 与 `ref` 类似。

12. **fulltext（全文索引扫描）**
    - **含义**: 使用全文索引进行搜索。
    - **特点**: 
      - 适用于 `MATCH ... AGAINST` 语法，常用于文本搜索。
    - **示例**: 
      ```sql
      EXPLAIN SELECT * FROM articles WHERE MATCH(title) AGAINST('database');
      ```
    - **性能**: 取决于全文索引的实现，效率因场景而异。

---

### **效率排序（从高到低）**
```
NULL > system > const > eq_ref > ref > unique_subquery > index_subquery > range > index_merge > index > ALL
```
- **注意**: `fulltext` 的效率不好直接比较，取决于具体场景。

---

### **总结**
除了你提到的 `ALL`、`index`、`range` 和 `ref`，还有 `eq_ref`、`const`、`system` 等更高效的类型，以及 `index_merge`、`unique_subquery` 等特殊情况。选择哪种类型取决于查询条件、索引设计和表结构。优化时，目标通常是将 `type` 从低效的 `ALL` 或 `index` 提升到 `ref`、`eq_ref` 或 `const`。

如果你指的是 `EXPLAIN` 中的其他字段（比如 `rows`、`filtered` 等），请告诉我，我会进一步说明！