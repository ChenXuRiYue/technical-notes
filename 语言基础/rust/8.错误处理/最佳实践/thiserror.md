# 📌 thiserror

该文档介绍 Rust 生态中，应用最广泛的错误处理框架：thiserror

## 📄 哲学

用最少的样板代码定义结构化的自定义错误类型

## 📄 场景

对一种场景感受就是：

如果存写一个 error 起码要做这几步：

- 枚举定义

  ```rust
  pub enum MyError {
    NotFound(String),
    Parse(String)
  }
  ```

- 支持格式化输出

  ```rust
  impl fmt::Display for MyError {
    
    fn fmt(&self, f &mut fmt::Formatter<'_>) -> fmt::Result {
      match self {
        MyError::NotFound(name) => write!(f, "'{}' Not Found", name),
        MyError::Parse(msg) => write!(f, "parse error: {}", msg), 
      }
    }
  }
  ```

- 第三方 create 的 错误自动转换为项目自定义错误体系

  ```rust
  impl std::error::Error for MyError {}
  
  impl From<serde_json::Error> for MyError {
    fn from(e: serde_json::Error) -> Self {
        MyError::Parse(e.to_string())
    }
  }
  ```

但仔细考虑发现：格式化输出、构造，是类似的、可归一的工作

## 📄 语法细节

- 派生宏定义

  > **\#[derive(Debug, thiserror::Error)]  // 派生宏**
  >
  > **#[error("格式化字符串")]        // 必填，定义 Display 输出**
  > enum MyError {
  >    Variant1(Type),
  >    Variant2 { field: Type },
  > }

- 格式化字符串.

  提供了三种插值：

  - 元组变体 — 用 {0} {1} 按位置引用
  - 结构体变体 — 用字段名引用
  - 可以混合 Display trait 实现

  ```rust
  use serde::Serialize;
  
  #[derive(Debug, thiserror::Error, Serialize)]
  #[serde(tag = "error", content = "message")]
  pub enum PluginError {
      #[error("Manifest parse failed: {0}")]
      ManifestParse(String),
  
      #[error("Plugin '{0}' is not installed")]
      PluginNotFound(String),
  
      #[error("Command '{command}' not found in plugin '{plugin}'")]
      CommandNotFound { plugin: String, command: String },
  
      #[error("Permission denied: {capability}")]
      PermissionDenied { capability: String },
  
      #[error("Internal error: {0}")]
      Internal(String),
  }
  ```

- 自动错误转换

  ```rust
  #[error("parse error: {0}")]
  Parse(#[from] serde_json::Error),
  ```

  等价于：

  ```rust
  impl From<serde_json::Error> for MyError {
    fn from(e: serde_json::Error) -> Self {
      AppError::Parse(e)
    }
  }
  ```



## 🌳 生长思考

对发散的自由捕捉、精确化

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


# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题


# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```



