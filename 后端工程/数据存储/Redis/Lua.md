# Redis 中的 Lua 使用

##  Redis 中的Lua 脚本

1. 为什么选择了Lua 脚本
2. redis 中是怎么嵌入Lua 脚本的？
3. Lua 脚本的机制是什么？
4. Lua 脚本不可替代的意义
5. Lua 相关的基础语法是什么？



## 简介

Redis中的Lua脚本是一种强大的功能，允许用户在Redis服务器上执行复杂的操作，而无需多次往返客户端和服务器。这不仅可以提高性能，还可以保证操作的原子性。以下是关于Redis中Lua脚本的详细使用方法和一些示例。



## 语法

### Redis 语法

- EVAL 命令： ```EVAL script numkeys key[key ...] arg[arg...]```
  - script: Lua 脚本代码
  - numkeys 使用的键数量
  - key ： 脚本中使用的键。
  - arg [arg ... ] 传递给 EVAL 脚本的其它参数



​	**demo:**

1. 购物车中同时更新库存

```lua
EVAL "redis.call('DECRBY', KEYS[1], ARGV[1]); redis.call('INCRBY', 		KEYS[2], ARGV[1])" 2 inventory product_id 5
```

2. 条件执行

```lua
EVAL "if redis.call('GET', KEYS[1]) > ARGV[1] then return redis.call('INCRBY', KEYS[2], ARGV[2]) end" 2 user_points discount 100 10
```

3. 红包雨: 实现一个抢红包的场景，确保每个用户只能抢三个红包

```lua
local REDBAG_LIMIT_KEY = KEYS[1]
local REDBAG_INFO_KEY = KEYS[2]
local REDBAG_USER_KEY = KEYS[3]
local userId = ARGV[1]

local grabCount = redis.call('hincrby', REDBAG_LIMIT_KEY, userId, 1)
if(grabCount > 3) then
    return "-1"
end

local amount = redis.call('lpop', REDBAG_INFO_KEY)
if(amount == nil) then
    return "-2"
end

redis.call('zadd', REDBAG_USER_KEY, amount, userId.."-"..grabCount)
return amount
```

**生长思考**

redis 中使用 lua 脚本其实就是走普通的 执行redis 命令获得相关内容。 基于获取的信息完成基础的逻辑过程。 最终调用 redis 客户端命令。类似于在终端使用redis



## 意义以及特性

1. Lua 脚本可以保证整个操作序列的原子性。同时发生或者同时删除。
2. 可以压缩 多个命令，组合成一个lua 脚本。减少网络通信次数，降低网络开销
3. 方便代码复用，减少大代码文件传输

## 其它问题

1. 为什么使用 lua? 

   与 C 兼容的轻量级别的 脚本语言
