# 📌 maven-build

maven 并没有 build 命令。这里的maven-build 代表了 maven 的一个构建系统。该文档描述了 maven 是怎么构建项目，输出 JAR 字节码文件。

## 📄 maven 构建系统概述

Maven 的 build 是一个**声明式、约定优于配置**的构建系统。它不直接“编译代码”或“打包 JAR”，而是通过一套标准化的生命周期模型，协调一系列插件来完成这些任务。

## 📄 maven 执行机制

以 `mvn clean install` 为例：

1. **解析命令，确认执行的顺序**

   - `clean` 是另一个生命周期（clean lifecycle）的阶段。


   - `install` 属于 default lifecycle。


   - Maven 会先执行 `clean` 生命周期的 `pre-clean → clean → post-clean`（但通常只绑定 `clean:clean` 到 `clean` 阶段），然后执行 default 生命周期从 `validate` 到 `install` 的所有阶段。


2. **加载项目 POM**

   - 读取当前目录下的 `pom.xml`，解析依赖、插件、属性、继承关系


   - 构建有效的 POM（effective POM），合并父 POM、默认值、profile 等


3. **执行生命周期：**

   -  **执行生命周期阶段（按序）**：

   -  **validate**：验证项目是否正确且所有必要信息可用。

   -  **compile**：编译主源码（默认 `src/main/java`）→ 触发 `maven-compiler-plugin:compile`。

   -  **test**：使用测试框架（如 JUnit）运行测试 → `maven-surefire-plugin:test`。

   -  **package**：将编译后的代码打包成 JAR/WAR 等 → `maven-jar-plugin:jar`。

   -  **verify**：运行集成测试或校验包完整性（可选）。

   -  **install**：将生成的 artifact（如 JAR）安装到本地 Maven 仓库（`~/.m2/repository`），供其他本地项目依赖。


4. **依赖管理**：

   - 在需要时（如 compile 阶段），Maven 会根据 `<dependencies>` 声明，从远程仓库（如 Maven Central）下载缺失的依赖到本地仓库。
   - 依赖范围（scope）决定依赖在哪些阶段可用（如 `test` 依赖不会进入最终 JAR）。

5. **插件机制**

   - 每个阶段的行为由绑定的插件目标实现。例如，`compile` 阶段默认绑定 `maven-compiler-plugin:compile`。

   - 插件本身也是 Maven artifact，可被版本控制和复用。



## 📄 build Fail 场景积累





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
我需要学习 maven 的 build 流程。让我的 build 失败排查能力得到成长。

# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题
maven build 是什么？在终端输入该命令，maven 完成了什么样的过程？它最后达到什么样的结果？

# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```