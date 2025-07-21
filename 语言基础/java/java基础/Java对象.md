# Java 对象

## 关于存储

**示例：**

1. ```java
   class A {
       int age;
       boolean flag;
   }
   ```

2. ```java
   class String {
       private final byte[] value;
       private final byte coder;
       // ......
   }
   ```

**对象结构：**
1. 对象头（Object Header）：包括 Mark Word（锁状态、GC 信息等）、Klass Pointer（指向类元数据），数组对象还包括长度字段。
2. 实例数据：类的成员变量数据。
3. 对齐填充：确保对象大小为 8 字节的倍数（64 位 JVM）。

**存储位置：**

- **对于示例 1**：  
  `new A()` 创建的对象存储在堆内存（通常在年轻代的 Eden 区，由垃圾回收器管理）。对象引用（局部变量）存储在当前方法调用栈中。

- **对于示例 2**：  
  由于字符串常量池的优化特性，当执行 `new String("demo")` 时：
  - 如果 "demo" 是第一次出现，JVM 会在字符串常量池（位于堆内存中）创建一个 `String` 对象，其 `value` 字段指向存储 "demo" 内容的 `byte[]`。
  - 同时，`new String("demo")` 会在堆内存的普通区域（非常量池）创建一个新的 `String` 对象。
  - 新对象的 `value` 字段会复用常量池中 "demo" 的 `byte[]`（通过引用共享），而不是创建新的 `byte[]`。