# Zset

## 跳表原理

[ChenXuRiYue/emqx-test: 跳表实现+MQTT生产者消费者模型实践](https://github.com/ChenXuRiYue/emqx-test)

跳表（Skip List）是一种基于随机化的数据结构，用于快速查找、插入和删除有序元素。它的核心思想是通过引入多层索引，减少查找的时间复杂度，平均达到 O(log n)。下面我详细解释一下跳表的原理：

### 1. **基本概念**
跳表可以看作是对普通有序链表的优化。在普通链表中，查找一个元素需要从头遍历到目标位置，时间复杂度为 O(n)。跳表通过增加“跳跃”的层次结构，让查找过程更高效。

- **底层链表**：跳表的基础是一个有序的单链表，包含所有元素。
- **多层索引**：在底层链表之上，随机选择一些节点，构建更高层次的索引链表。每层索引指向下层链表中的部分节点，层级越高，节点越稀疏。

### 2. **结构特点**
- **节点结构**：每个节点不仅存储数据和指向下一个节点的指针，还可能有多个指向更高层索引的指针。每个节点的层数是随机决定的（通常基于抛硬币的概率，比如 50% 的概率升一层）。
- **层级分布**：假设有 n 个元素，底层包含所有元素（第 0 层），第 1 层大约有 n/2 个节点，第 2 层有 n/4 个节点，以此类推，最高层通常只有少数几个节点。
- **顶部层级**：最高层通常只包含少数几个节点（甚至只有一个），作为查找的起点。

### 3. **工作原理**
以查找为例，跳表的搜索过程从最高层开始，逐步向下层逼近目标：

- **查找过程**：
  1. 从最高层的第一个节点开始。
  2. 在当前层，沿着指针向右移动，直到遇到一个节点，其值大于或等于目标值。
  3. 如果当前节点的值等于目标值，则查找成功；如果大于目标值或到达链表末尾，则下降到下一层，从上一个访问的节点继续查找。
  4. 重复上述步骤，直到在第 0 层找到目标值或确认目标不存在。

- **时间复杂度**：由于每层的节点数量呈指数递减，平均情况下，查找路径的步数是对数的，因此时间复杂度为 O(log n)。

### 4. **插入和删除**
- **插入**：
  1. 首先按照查找过程找到插入位置。
  2. 创建新节点，随机决定其层数（例如通过抛硬币，概率 p = 0.5）。
  3. 将新节点插入到每一层对应的位置，更新指针。
- **删除**：
  1. 找到目标节点的位置。
  2. 从每一层中移除该节点，并调整前后节点的指针。

插入和删除的平均时间复杂度也是 O(log n)，因为操作依赖于查找过程。

### 5. **随机化的作用**
跳表的层数是随机生成的，这种随机性保证了结构的平衡性，避免了像二叉搜索树那样的退化情况（例如变成线性结构）。理论上，跳表的性能依赖于概率分布，但实践证明它非常高效且实现简单。

### 6. **优点与缺点**
- **优点**：
  - 查找、插入、删除的平均时间复杂度为 O(log n)。
  - 实现简单，不需要复杂的平衡操作（如红黑树）。
  - 动态性好，适合并发环境（可以加锁优化）。
- **缺点**：
  - 空间复杂度较高（每个节点需要额外的指针）。
  - 性能依赖随机化，可能有极小概率出现不平衡。

### 7. **直观比喻**
想象你在找一本书，书架上有几层索引：
- 最底层是所有书的完整列表。
- 中间层是每 10 本书的标记。
- 顶层是每 100 本书的标记。
你会先从顶层开始，快速定位大致范围，再逐步向下细化查找。跳表就是类似的“分层跳跃”思想。

总结来说，跳表通过多层索引和随机化的层级分配，实现了一种简单而高效的动态数据结构，非常适合需要快速查找的场景，比如数据库索引或内存缓存系统。





## 实现demo

**node**

```java
package Axel.Chen.datastruct;

public class Node<K extends Comparable<K>, V> {
    private K key;
    private V value;

    private Node<K, V> next;
    private Node<K, V> down;

    // 计算跨度：虽然当前语境不需要，但是，如果复用到排行榜中，这里可以产生重要的作用。
    Integer Length;

    public Node(K key, V value) {
        this.key = key;
        this.value = value;
        this.Length = 1;
    }

    // 若干 get set 接口
    public K getKey() {
        return key;
    }

    public V getValue() {
        return value;
    }

    public Node<K, V> getNext() {
        return next;
    }

    public Node<K, V> getDown() {
        return down;
    }

    public void setNext(Node<K, V> next) {
        this.next = next;
    }

    public void setDown(Node<K, V> down) {
        this.down = down;
    }

    public void setLength(Integer length) {
        Length = length;
    }
}
```

**skipList**

```java
package Axel.Chen.datastruct;

import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.locks.ReentrantReadWriteLock;
public class SkipList<K extends Comparable<K>, V> {
    // 跳表相关的一些配置：
    // 1. 新建层次随机概率
    private final double PROBABILITY = 0.5;
    // 2. 跳表最大层数
    private final int MAX_LEVEL = 32;
    // 3. 跳表层数
    private int level;
    // 4. 头结点
    private final List<Node<K, V>> head;
    // 5. 链表元素个数
    private int size;
    // 读写场景共存。使用读写锁来处理并发场景
    private final ReentrantReadWriteLock lock;

    public SkipList() {
        level = 0;
        head = new LinkedList<>();
        head.add(new Node<>(null, null));
        // 7，并发锁优化
        lock = new ReentrantReadWriteLock();
    }

    public Integer getRandomLevel() {
        int res = 0;
        while (res < MAX_LEVEL && Math.random() < PROBABILITY) res++;
        return res;
    }

    public void insert(K key, V value) {
        // 加锁
        lock.writeLock().lock();
        // 1.特判插入第一个节点，直接构造
        // 2. 已经初始化跳表
        List<Node<K, V>> skipList = getSplitNodeList(key);
        updateSkipStructureWhenInsert(skipList, key, value);
        // 更新元素个数
        size++;
        // 解锁
        lock.writeLock().unlock();
    }
    // TODO delete方法

    List<Node<K, V>> getSplitNodeList(K key){
        List<Node<K, V>> split = new LinkedList<>();
        // 从顶层头节点开始向下递归查找
        Node<K, V> current = head.get(level);
        while (current != null) {
            // 分为几种情况：
            Node<K, V> next = current.getNext();
            // 1. 下一个为 null， 需要向下走
            if (next == null) {
                split.add(current);
                current = current.getDown();
            }
            // 2. 比较next.key 和 大小
            else {
                // 2.1 比较，如果 left > next.key ，则向右走
                if (key.compareTo(next.getKey()) > 0) {
                    current = current.getNext();
                }
                // 2.2 比较，如果 left < next.key ，则向下走
                else {
                    // 转折点，无论如何都记录到 update中
                    split.add(current);
                    // 2.2.3 判断是否在最底层
                    if (current.getDown() == null) {
                        break;
                    } else {
                        // 记录转折点。
                        current = current.getDown();
                    }
                }
            }
        }
        // 对 update 数组取反， 方便处理
        Collections.reverse(split);
        return split;
    }

    public void updateSkipStructureWhenInsert(List<Node<K, V>> split, K key, V value){
        // 1. 随机化当前新插入节点的层数
        int randomLevel = getRandomLevel();

        if (randomLevel > level) {
            // 2.1 新建一层
            ++level;
            Node<K, V> newNode = new Node<>(key, value);
            newNode.setNext(null);
            newNode.setDown(head.get(level - 1));
            split.add(newNode);
            head.add(newNode);
        } else{
            // 2.2 取子数组
            split = split.subList(0, randomLevel + 1);
        }
        // 3. skipList 内容链表以及索引
        Node<K, V> downNode = null;
        for (Node<K, V> kvNode : split) {
            Node<K, V> newNode = new Node<>(key, value);
            newNode.setDown(downNode);
            downNode = newNode;
            newNode.setNext(kvNode.getNext());
            kvNode.setNext(newNode);
        }
    }


    /**
     * 查出列表中，在 left 和 right 之间的数据
     */
    public List<Node<K, V>> search(K left, K right) {
        lock.readLock().lock();
        Node<K, V> last = getLastNodeSmallerThanKey(left);
        // 底层链表搜索出对应的范围。
        List<Node<K, V>> res = getListByIntervalInBottom(left, right,last);
        lock.readLock().unlock();
        return res;
    }

    private Node<K, V> getLastNodeSmallerThanKey(K key){
        Node<K, V> current = head.get(level);
        // 定位到最底层的分界点。
        while (current != null) {
            // 分类讨论
            Node<K, V> next = current.getNext();
            // 1. next.key 为 null， 需要向下走
            if (next == null) {
                current = current.getDown();
            }
            // 2. 比较next.key和 大小
            else {
                // 2.1 如果 left > next.key ，则向右走
                if (key.compareTo(next.getKey()) > 0) {
                    current = current.getNext();
                }
                // 2.2 如果 left 大于，则向下走
                else {
                    // 2.2.3 判断是否在最底层
                    if (current.getDown() == null) {
                        break;
                    } else {
                        current = current.getDown();
                    }
                }
            }
        }
        return current;
    }

    private List<Node<K, V>> getListByIntervalInBottom(K left, K right, Node<K, V> Last){
        List<Node<K, V>> res = new LinkedList<>();
        Node<K, V> current = Last;
        // 跳出循环时候 current 指向最后一个比它小的元素。 对其进行重新定位 -> 指向下一个即第一个大于等于 left 的元素
        if (current != null) current = current.getNext();
        while (current != null && current.getKey().compareTo(right) <= 0) {
            res.add(current);
            current = current.getNext();
        }
        return res;
    }

    public Integer getSize(){
        return size;
    }
}
```

