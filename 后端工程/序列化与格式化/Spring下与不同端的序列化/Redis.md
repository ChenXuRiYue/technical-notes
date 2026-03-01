# 📌 Redis 为端点的序列化

数据实体通过一系列的序列化过程，存储进 Redis 中

## 📄 redis 数据格式

Redis 在协议层将数据抽象为不透明的二进制字节流 （Opaque Byte Sequences）

- 不透明：Redis 服务器本身不解析、不理解、不关心字节内部的具体结构或语义，仅将其视为二进制流进行存储和传输
- 抽象：强调这是 Redis 对上层数据的一种逻辑映射

Redis 接收的数据格式并非随意的字节流，而是 RESP （Redis Serialization Protocol 格式）

## 📄 Spring 的对象 存入 Redis 

- 业务层调用

  **redisTemplate**

  ```java
  redisTemplate.opsForValue().set(key, user, 30, TimeUnit.MINUTES);
  ```

  **redisson**

  ```java
  // 1. 获取锁对象 (本地动作，无网络交互)
  // 名字 "order_lock_1001" 就是 Redis 中的 Key
  RLock lock = redisson.getLock("order_lock_1001");
  
  try {
      // 2. 尝试加锁 (真正的分布式动作开始)
      // 参数含义：等待最多 10 秒获取锁，获取成功后自动过期时间为 30 秒
      // 【底层发生了什么？】
      // A. 发送 Lua 脚本：检查 Key 是否存在。
      // B. 若不存在 -> SETNX (原子设置)。
      // C. 若存在且属于当前线程 -> 重入计数 +1 (可重入)。
      // D. 若存在且属于其他线程 -> 返回失败或进入等待队列。
      boolean isLocked = lock.tryLock(10, 30, TimeUnit.SECONDS);
  
      if (isLocked) {
          // 3. 执行业务逻辑
          processOrder();
          
          // 【隐含的关键动作：Watchdog (看门狗)】
          // 如果你没有指定 leaseTime (或者像这里只指定了初始时间)，
          // Redisson 会启动一个后台定时任务 (默认每 10 秒)，
          // 自动执行 Lua 脚本给锁“续期”，防止业务没跑完锁就断了。
          // 只有当你显式指定了过期时间且不调用 unlock，看门狗才不工作。
      } else {
          // 获取锁失败的处理逻辑
          log.warn("获取锁失败，业务降级处理");
      }
  
  } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
  } finally {
      // 4. 释放锁
      // 【底层发生了什么？】
      // A. 检查是否持有锁。
      // B. 递减重入计数。
      // C. 若计数为 0 -> DEL Key。
      // D. 发布解锁消息 (Pub/Sub)，唤醒正在 wait 的其他客户端。
      if (lock.isHeldByCurrentThread()) {
          lock.unlock();
      }
  }
  ```

- 序列化

  根据配置，类对象发生序列化。格式根据配置决定。

  - 二进制字节流
  - JSON 文本字符串

  ⬇️ 转为 byte[] 数组

- Redis 客户端执行 RESP 协议封装

- 网络传输

- 服务端接收和存储

## 📄 web 业务场景

### 🔖 缓存模式演进

> 为一个对象建立了一套缓存机制。随着业务变更，需要对这个对象结构变更
>
> - 增加字段
> - 删除字段
> - 更新名称
>   - 类名
>   - 字段名
>
> 灰度过程中，redis 的两类数据怎么处理？

假设系统中存在 **旧版本代码 V1** 和 **新版本代码 V2**

📝 **增加字段：（Add Field）**

- v2 读旧数据

  - Json（Jackson/Gson）默认行为是忽略未知字段缺失。

  - 二进制，如果配置了默认值机制，通常能兼容；如果严格依赖字段顺序或注册表，可能会报错

- v1 读新数据

  - Json v1 反序列化时，会看到多出来的 vipLevel ziduan 只要配置了 FAIL_ON_UNKNOWN_PROPERTIES = false (JackSon 默认通常为  ignore 或者可配置)。v1 会直接忽略该字段，正常读取 id 和 name。

- 写操作

  - V1 写变为旧格式
  - V2 写 保留 vipLevel

📝 **删除字段：（Remove Field）**

**现象**：V2 对象删掉了 `obsoleteField`。

- **Redis 中的数据状态**：
  - 旧数据：`{"id":1, "name":"Alice", "obsoleteField":"xxx"}`
  - 新数据：`{"id":1, "name":"Alice"}`
- **处理策略**：
  1. **V2 读旧数据**：
     - **JSON**：V2 类中没有 `obsoleteField`，反序列化时直接忽略该字段。**天然兼容。**
  2. **V1 读新数据**：
     - **JSON**：V1 期望有 `obsoleteField`，但新数据里没有。V1 反序列化后，该字段为 `null`。
     - **风险点**：V1 的业务逻辑是否依赖该字段非空？如果 V1 代码里有 `if (obj.obsoleteField != null)` 的逻辑，可能会走分支错误。
     - **对策**：确保 V1 代码对 `null` 值有健壮的处理（防御性编程）。通常在删除字段前，该字段在业务上应该已经不再强依赖了。
  3. **写操作**：
     - V1 写入：会把 `obsoleteField` 写回去（即使它是空的或旧的）。
     - V2 写入：彻底移除该字段。
     - **结果**：只要 V1 不崩溃，随着 V1 实例下线，旧数据会被 V2 覆盖清洗。

📝 **更新名称 (Rename)**

**难度**：⭐⭐⭐⭐ (高危，需人工干预)
**现象**：类名 `User` -> `Member`，或字段名 `userName` -> `username`。
**痛点**：JSON 是键值对匹配，Key 变了就匹配不到了；二进制更是直接错位。

**字段名变更 (**`userName` **->** `username`**)**

- **如果不处理**：
  - V2 读旧数据：找不到 `username`，值为 null
  - V1 读新数据：找不到 `userName`，值为 null
  - **后果**：数据丢失，业务逻辑错误

处理方法：

- 评估不变
- 双写过渡

📝 **类名变更 (**`User` **->** `Member`**)**

**风险**：如果 JSON 中存了 `@class":"com.example.User"`，V2 试图反序列化为 `Member` 时会失败（类型不匹配）。

**处理策略**：

1. **移除 `@class` 依赖**：如果在 `RedisTemplate` 或 `Redisson` 中指定了目标 Class (`readValue(..., Member.class)`)，则 JSON 中的 `@class` 可以被忽略或不写入。

2. **类型映射 (Type Mapping)**：

   - Jackson 允许配置 `ObjectMapper` 进行类型替换：

     ```java
     mapper.addMixIn(Member.class, UserMixin.class); 
     // 或者配置反序列化时的类型映射
     mapper.registerSubtypes(new NamedType(Member.class, "com.example.User"));
     ```

   - 告诉解析器：“当你看到 `@class` 是 `User` 时，请实例化为 `Member` 类”。

3. **双类共存**：在 V2 代码中保留旧的 `User` 类（标记 Deprecated），让它继承或委托给新的 `Member` 类，直到灰度结束

## 🌳 生长思考

- Jackson 在缓存演进中的默认表现如何？

  - 新增字段

    - V2 读 V1 为 null
    - V1 读 v2 丢弃多余字段

  - 删除字段

    类似上

  ❗️**值得注意的是 默认行为 读为 null 时，是业务逻辑上的风险，非序列化风险**

## 💭 反复绊脚

记录回顾、使用文档时，遇到的困惑

## 🗺️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思



## ⚙️ prompt

探究该文档模块过程中的 prompt 记录
模版如下：

```markdown
# 背景
我是一名追求效率的学习者。我从事于Java后端开发工程师的工作。
我认为学习本质上就是 大量正确信息的消化 + 关键结论的感受 + 自由的发散。
依托这样的思想，我希望和你来进行一场talk。

我们的 talk 基于以下原则
1. 你是 该talk 主题下的专家
2. 我是一名在其他领域具有通用性技能的工程师，如 Java、传统算法、后端工程、C++ 语法、Go 语法等。拥有一定计算机基础的知识。
3. 我们是不同领域的擅长者，这是一场圆桌会议式的talk。就和索尔维会议一样，阿尔伯特·爱因斯坦与尼尔斯·玻尔之间的交流。
4. 以你的权重为主前提下，我希望我们相互的问询感兴趣的内容。这样可以推动 talk 的进度。
# talk 主题
Redis 与序列化

# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题
一个对象要存储到 redis 调用接口之前，提供了什么过程？ redis 接收什么样的数据？

# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```



