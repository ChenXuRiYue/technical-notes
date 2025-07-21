# LRU 缓存

[146. LRU 缓存 - 力扣（LeetCode）](https://leetcode.cn/problems/lru-cache/description/)





## 更优解法

map: 维护指针
双向链表维护 key, value 对，简化删除维护方案



## 思路1

维护一个 映射关系，以及一个链表， 各个键的数量。逐步判断处理即可。



## code 1

```go
import (
    "fmt"
)

type LRUCache struct {
    kv map[int]int    // key - value 键值对存储空间
    cunt map[int]int  // 记录当前某个元素在链表中的个数。
    cap int           // 结构的容量大小
    len int
    head *node   
    tail *node
}

type node struct {
    value int
    next  *node
}


func Constructor(capacity int) LRUCache {    
    return LRUCache{make(map[int]int), make(map[int]int), capacity, 0, nil, nil};
}


func (this *LRUCache) Get(key int) int {
    if _, ok := this.kv[key]; ok == false {
         return -1
    } else {
        this.cunt[key] = this.cunt[key] + 1
        this.tail.next = &node{key, nil}
        this.tail = this.tail.next
        return this.kv[key]
    }
}


func (this *LRUCache) Put(key int, value int)  {
    if _, ok := this.kv[key]; ok == true {
        this.kv[key] = value
        this.cunt[key] = this.cunt[key] + 1
        this.tail.next = &node{key, nil}
        this.tail = this.tail.next
    } else {
        // 添加
        this.kv[key] = value
        if this.head == nil {
            this.head = &node{key, nil}
            this.tail = this.head
            this.cunt[key] = 1;
        } else {
            this.tail.next = &node{key, nil}
            this.tail = this.tail.next
            c, ok := this.cunt[key]
            if(ok) {
                this.cunt[key] = c + 1
            } else {
                this.cunt[key] = 1
            }
        }
        // fmt.Println()
        // fmt.Println("####")
        // 开启更新淘汰
        if this.len == this.cap  {
            fmt.Println("ddd")
            for {
                // fmt.Println("ddd")
                val := this.head.value
                t := this.cunt[val]
                // fmt.Println(val, " ", this.cunt[val])


                this.cunt[val] = t - 1
                this.head = this.head.next
                if t == 1{
                    // fmt.Println("xxx - val")
                    // fmt.Println(val)
                    // fmt.Println("xxx - siz")
                    // fmt.Println(t)
                    delete(this.cunt, val)
                    delete(this.kv, val)
                    break
                }

            }
        } else {
            this.len = this.len + 1
        }
        // fmt.Println(this.len)
    }
}


/**
 * Your LRUCache object will be instantiated and called as such:
 * obj := Constructor(capacity);
 * param_1 := obj.Get(key);
 * obj.Put(key,value);
 */
```

评价反思：

1. 重复代码过多。封装程度不够。
2. 命名不规范



## code2

遵行代码整洁之道：封装组合出 list。

```go


type LRUCache struct {
    kv map[int]int    // key - value 键值对存储空间
    cap int           // 结构的容量大小
    list linkedList
}

type node struct {
    value int
    next  *node
}

type linkedList struct {
    head *node   
    tail *node
    valueTypeCount  int
    cunt map[int]int
}

func (list *linkedList) addProcessor(value int) {
    list.insertNode(value)
    list.matinMessage(value)
}

// 插入节点
func (list *linkedList)insertNode(value int) {
    if list.tail == nil {
        list.tail = &node{value, nil}
        list.head = list.tail
    } else {
        list.tail.next = &node{value, nil}
		list.tail = list.tail.next
    }
}

func (list *linkedList)clearListUselessNode(cap int)([]int) {
	deleteValue := make([]int, 0)
    for list.valueTypeCount > cap  {
        for {
            val := list.head.value
            t := list.cunt[val]
            list.cunt[val] = t - 1
            list.head = list.head.next
            if t == 1{
				deleteValue = append(deleteValue, val)
                delete(list.cunt, val)
                break
            }
        }
        list.valueTypeCount = list.valueTypeCount-1
    } 
	return deleteValue
}


func (list *linkedList)matinMessage(key int) {
    c, ok := list.cunt[key]
    if(ok) {
        list.cunt[key] = c + 1
    } else {
        list.cunt[key] = 1
		list.valueTypeCount = list.valueTypeCount + 1;
    }
}

func Constructor(capacity int) LRUCache {    
    return LRUCache{make(map[int]int), capacity, linkedList{nil, nil, 0, make(map[int]int)}};
}


func (lru *LRUCache) Get(key int) int {
    if _, ok := lru.kv[key]; !ok {
         return -1
    } else {
        lru.list.addProcessor(key)
        return lru.kv[key]
    }
}

func (lru *LRUCache) clearKey(arr []int) {
	for _,  val := range arr {
		delete(lru.kv, val)
	}
}



func (lru *LRUCache) Put(key int, value int)  {
    lru.list.addProcessor(key)
	arr := lru.list.clearListUselessNode(lru.cap)
	lru.clearKey(arr)
    lru.kv[key] = value
}


/**
 * Your LRUCache object will be instantiated and called as such:
 * obj := Constructor(capacity);
 * param_1 := obj.Get(key);
 * obj.Put(key,value);
 */
```

