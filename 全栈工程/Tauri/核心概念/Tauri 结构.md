# 📌 Tauri 结构

- 多语言和通用工具包
- 应用程序工具包，允许制作 Webview OS 应用程序
- 在 Webview 和基于 Rust 的后端之间建立桥接



## ⚙️ 核心生态系统

### 📄 tauri

这是一个主要的 crate，将所有内容结合在一起。它将运行时、宏、工具和 API 整合成一个最终产品



### 📄 tauri-runtime
Tauri 本身与底层 Webview 库之间的粘合层

### 📄 tauri-macros
通过利用 [`tauri-codegen`](https://github.com/tauri-apps/tauri/tree/dev/crates/tauri-codegen) crate 为上下文、处理程序和命令创建宏。


### 📄 tauri-utils
在许多地方重复使用的通用代码，提供有用的工具，如解析配置文件、检测平台三元组、注入 CSP 和管理资产。


### 📄 tauri-build
在构建时应用宏，以设置 `cargo` 所需的一些特殊功能

### 📄 tauri-codegen

嵌入、哈希和压缩资产，包括应用程序的图标以及系统托盘。在编译时解析[`tauri.conf.json`](https://v2.tauri.app/zh-cn/reference/config/)并生成 Config 结构

### 📄 tauri-runtime-wry

这个 crate 为 WRY 打开了直接的系统级交互，例如打印、监视器检测和其他与窗口相关的任务

## ⚙️ Tauri 工具

### 📄 API 

创建 cos 、 esm javaScript 断电，方便导入到前端框架中，以便 web view 可以调用和监听后端活动

### 📄 Bundler (Rust / shell)

一个库，为其检测或被告知的平台构建 Tauri 应用程序。目前支持 macOS、Windows 和 Linux—但在不久的将来也将支持移动平台。可以在 Tauri 项目之外使用。



### 📄 Cli.rs (Rust)

这个 Rust 可执行文件提供了 CLI 所需的所有活动的完整接口。它在 macOS、Windows 和 Linux 上运行。

### 📄 create-tauri-app(JavaScript)

一个工具包，使工程团队能够快速搭建新的 `tauri-apps` 项目，使用他们选择的前端框架（只要它已被配置）。



## ⚙️ 上游 Crates

### 📄 TAO

一个跨平台的应用程序窗口创建库，支持所有主要平台。，如 Windows、macOS、Linux、iOS 和 Android。用 Rust 编写，它是 [winit](https://github.com/rust-windowing/winit) 的一个分支，我们根据自己的需要进行了扩展—例如菜单栏和系统托盘。

### 📄 WRY

WRY 是一个跨平台的 WebView 渲染库，用 Rust 编写，支持所有主要桌面平台，如 Windows、macOS 和 Linux。Tauri 使用 WRY 作为抽象层，负责确定使用哪个 Webview（以及如何进行交互）。



## ⚙️ 其它工具

### 📄 tauri-action

Github 工作流，为所有平台构建 Tauri 二进制文件。

### 📄 tauri-vscode

增强 Visual Studio Code 界面，提供了一些非常实用的功能。

### 📄 vue-cli-plugin-tauri

允许在 vue-cli项目中非常快速的安装 Tauri

## ⚙️ 插件

插件由第三方编写（尽管可能有官方支持的插件）。一个插件通常完成三件事：

1. 使 Rust 代码能够“做某事”。
2. 提供接口粘合，使其易于集成到应用程序中。
3. 提供 JavaScript API，以便与 Rust 代码进行接口。


## 🌳 生长思考
- 后续需要在使用中感受这套工具集
- 插件设计思想的启发


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



