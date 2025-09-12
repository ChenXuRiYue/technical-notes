# 📌 Rust 入门

该文档总结：关于 Rust 最基础的认知

## 📄 Hello world

从最简单的程序开始：

main.rs

```rust
fn main() {
  println!("hello world!");
}
```

**文件命名**：

1. 以 .rs 为结尾
2. 按照规范应该使用下划线分割单词

**入口函数：**

1. main 为函数的入口
2. main 没有参数、也没有返回值

**函数：**

1. fn 为函数标识符
2. {} 定义函数体

**打印：**

1. ； 分隔语句
2. println!("xxxx") 中 ！表示调用了一个 Rust宏

## 📄 编译与运行

编译 和运行时两个独立的步骤：

**编译**：

1. 最简单的编译语句：`rustc main.rs`

**运行**：

1. Mac Or Linux 中：`./main`
2. Window: `.\main.exe`

**语言基本性质上**：

Rust 是一门预编译型语言。可执行文件可以在各个主流系统上运行

## 📄 Cargo

Cargo 是Rust 的构建系统和包管理器。它是管理 Rust 项目的最主流官方工具。它具有几个重要功能：

1. 构建任务
2. 下载依赖
3. 编译库等

### 🔖 使用

${\large {\color[RGB]{250, 157, 30}创建项目}} $
 `cargo new hello_cargo` : 将会创建一个名为 hello_cargo 的目录和项目。

${\large {\color[RGB]{250, 157, 30}基本结构}} $

```txt
[src]
  main.rs
[target]
.gitignore
Cargo.lock
Cargo.toml
```

${\large {\color[RGB]{250, 157, 30}Git}} $

Git 作为最佳实践融合在工程开发中。

${\large {\color[RGB]{250, 157, 30}Cargo.toml}} $

类似于 Java/Maven 的 Pom、Node.js 的 package.json、Go 的 go.mod


```toml 
[package]
name = "hello_cargo"
version = "0.1.0"
edition = "2024"

[dependencies]
```

TOML 全称是 **Tom's Obvious, Minimal Language**，由 Tom Preston-Werner 创建（GitHub 联合创始人，也是 Ruby 的 Jekyll 作者）。他也是 Git、Homebrew、Octopress 等知名项目的贡献者。

${\normalsize{\color[RGB]{253, 175, 14}语法清单}}$

✅ 核心语法元素

| 结构            | 示例                                                 | 说明                                       |
| --------------- | ---------------------------------------------------- | ------------------------------------------ |
| **键值对**      | `name = "my-app"`                                    | 基本单位，支持字符串、数字、布尔、数组等   |
| **表（Table）** | `[package]`                                          | 用 `[表名]` 定义一个命名空间，类似 section |
| **内联表**      | `serde = { version = "1.0", features = ["derive"] }` | 简写复杂依赖                               |
| **数组**        | `features = ["cli", "gui"]`                          | 支持混合类型，但通常用于同类型列表         |
| **数组中的表**  | `[[bin]]`                                            | 特殊语法，用于定义多个可执行文件           |

更深入需要开一个单独专栏。在 rust 想法项目实现中深入。



${\large {\color[RGB]{250, 157, 30}运行项目}} $

`cargo run`
`cargo check`: 预检是否成功编译

${\large {\color[RGB]{250, 157, 30}发布构建}} $

`cargo build --release`

## 📄 数字游戏

编写一个数字游戏

```rust
use std::cmp::Ordering;
use std::io;

use rand::Rng;

fn main() {
    println!("猜数字游戏\n");

    // mut 关键字定义了一个变量。省略则代表定义了一个常量
    let secret_number = rand::thread_rng().gen_range(1..=100);
    loop {
        println!("请输入一个数字\n");
        let mut guess = String::new();

        io::stdin()
            .read_line(&mut guess)
            // 该语句使用处理常用错误
            .expect("读取失败\n");
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };
        match guess.cmp(&secret_number) {
            Ordering::Less => println!("太小了"),
            Ordering::Greater => println!("太大了"),
            Ordering::Equal => {
                println!("正确！");
                break;
            }
        }
    }
}
```

该段代码涉及了：

1. 变量定义、常量定义
2. 输入输出
3. 比较
4. 错误 处理
5. match
6. 循环等

可以感受到 rust 和其他语言鲜明的特点。非常注重错误处理。变量定义也有些抽象，不够直观。

## 🌳 生长思考

1. TOML 配置文件语法格式等扩展问题

## 💭 反复绊脚

记录回顾、使用文档时，遇到的困惑



## 🗺️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思



## ⚙️ prompt

```markdown
# 背景
我是一名追求效率的学习者。我从事于 IT 后端开发工程师。对于学习，我认为本质上就是 大量的正确的信息记忆消化理解 + 关键结论的感受 + 自由发散扩展。
依托这样的思想，我希望和你来进行一场talk
我的第一目标是写一个基于 Rust的桌面端工具（类似于 githubdesktop 的桌面级客户端工具。）

# talk 主题
我们基于rust 官方文档进行讨论。作为新手难免我会遇到一些困惑。我希望你作为一个富有经验的工程师和我交流。你希望向我介绍 rust 之美。而我基于我的经验（Java、C++）和你就一些问题展开讨论。（当然你是正确信息、丰富例子的提供者）

# 输入格式
略

# 输出格式
略

# 思维链
请自由发挥

# 当前问题
1. toml 的基础配置语法，以及和 Rust 语境下的最常见的例子。因

# 问题阶段
## 问题一 
1. 问题描述
我使用 cargo 创建了一个项目。就其产生的内容而言，我存在一些困惑。比如 cargo.toml 是什么文件格式？我见过yaml，go的 .mod。rust 作为一个新语言。cargo 也作为一个著名框架。为什么选择了这个文件格式呢？它的背景是什么？
2. 结论
我已经知道了 cargo.toml 的文件格式以及历史。以及相比于其他几种主流的配置，其优劣性。

```



