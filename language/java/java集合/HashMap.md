# HashMap

HashMap 是用来基于 哈希表 实现 key value 的快速存取的类。当前的内容中

## 类结构

1. 哈希桶
2. 节点
3. 链表
4. 红黑树



## 原理性问题



## 使用细节

1. 空值的使用：

   hashmap 允许空值。put 一个null 导致了哈希冲突。

   并发安全下的 ConcurrentHashMap 不允许。

