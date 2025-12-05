# 📌 maven-plugin

## 📄 maven plugin 概念框架

Maven Plugin 是 Maven 构建系统中的**可扩展执行单元**。它封装了特定任务的逻辑（如编译 Java 源码、运行测试、生成 Javadoc、打包 JAR/WAR 等），并通过标准接口与 Maven 的核心构建引擎集成。Maven 本身几乎不包含具体构建逻辑——所有实际工作都由插件完成。

换句话说：**Maven 是一个插件执行框架**，其“能力”完全由插件赋予。

核心概念框架：

1. **Mojo（Maven Goal 的实现单元）**
   - 每个插件包含一个或多个 Mojo。
   - 每个 Mojo 对应一个 **goal**（如 `compiler:compile` 中的 `compile`）。
   - Mojo 通过注解（旧版用 Javadoc 注释，新版用 `@Mojo`）声明其行为、参数、生命周期绑定等。
2. **Goal vs Phase**
   - **Phase** 是生命周期中的一个**阶段**（如 `compile`, `test`, `package`）。
   - **Goal** 是插件提供的一个**可执行任务**。
   - Maven 通过将 Goal **绑定到 Phase** 来实现自动化执行。
   - 用户也可直接调用 Goal（如 `mvn compiler:compile`），绕过生命周期。
3. **生命周期（Lifecycle）与默认绑定（Default Binding）**
   - Maven 有三套标准生命周期：`default`（构建）、`clean`（清理）、`site`（文档）。
   - 每个生命周期由一系列有序 Phase 组成。
   - 插件的 Goal 可以（也通常）被绑定到某个 Phase，形成“当执行此 Phase 时，自动触发该 Goal”。
4. **插件坐标（Plugin Coordinates）**
   - 插件本身也是一个 Maven artifact，具有 `groupId:artifactId:version`。
   - 例如：`org.apache.maven.plugins:maven-compiler-plugin:3.11.0`
   - 在 `<plugins>` 中声明时，若省略 `groupId`，默认为 `org.apache.maven.plugins`
5. **插件配置（Configuration）**
   - 通过 `<configuration>` 块向 Mojo 传递参数。
   - 支持属性注入、POM 表达式（如 `${project.build.sourceDirectory}`）、甚至复杂对象结构。
6. **插件解析与加载机制**
   - Maven 在执行前会解析插件依赖（包括插件自身的依赖），并从本地/远程仓库下载。
   - 插件运行在独立的 ClassLoader 中，避免污染项目类路径（这点常被忽视，但对理解插件隔离性很重要）。

## 📄 插件分类

一、按 **与 Maven 生命周期的绑定关系** 分类（最核心的维度）

1. **默认绑定插件（Default-Bound Plugins）**

- 由 Apache Maven 官方提供，预绑定到 `default`、`clean`、`site` 三大生命周期的特定 phase。
- 定义在 **Super POM**（所有项目的隐式父 POM）中。
- 用户通常无需显式声明即可使用（但建议显式指定版本以避免隐式升级风险）。

> 示例：
>
> - `maven-compiler-plugin` → 绑定到 `compile` 和 `test-compile`
> - `maven-surefire-plugin` → 绑定到 `test`
> - `maven-jar-plugin` → 绑定到 `package`
> - `maven-install-plugin` → 绑定到 `install`
> - `maven-deploy-plugin` → 绑定到 `deploy`

2. **非绑定插件（Unbound / Standalone Plugins）**

- 不自动绑定到任何生命周期 phase。
- 必须通过 **显式调用 goal**（如 `mvn plugin:goal`）或 **手动绑定到 phase** 才能执行。
- 多用于辅助任务、一次性操作或条件性构建步骤。

> 示例：
>
> - `maven-dependency-plugin`：常用 `dependency:tree`、`dependency:copy`
> - `build-helper-maven-plugin`：添加额外 source directory（需手动绑定）
> - `exec-maven-plugin`：运行任意 Java/main 或 shell 命令

二、按 **功能用途** 分类（你最初提到的方向，这里细化）

1. **构建基础设施类**

- 负责项目结构、依赖、元数据管理
- 通常由 Maven Core 间接调用，或作为其他插件的基础

> - `maven-resources-plugin`：复制并过滤资源文件（`src/main/resources` → target）
> - `maven-archetype-plugin`：生成项目骨架
> - `maven-help-plugin`：查询 effective POM、插件信息等

2. **编译与语言处理类**

- 处理源码到字节码的转换

> - `maven-compiler-plugin`（Java）
> - `scala-maven-plugin`
> - `groovy-maven-plugin`
> - `jaxb2-maven-plugin`（XML → Java）
> - `protobuf-maven-plugin`（.proto → Java）

3. **测试支持类**

- 执行、报告、覆盖测试

> - `maven-surefire-plugin`：单元测试（JUnit/TestNG）
> - `maven-failsafe-plugin`：集成测试（支持 pre/post 集成测试阶段）
> - `jacoco-maven-plugin`：代码覆盖率
> - `pitest-maven`：突变测试

4. **打包与分发类**

- 将产物组装成可部署格式

> - `maven-jar-plugin`
> - `maven-war-plugin`
> - `maven-ear-plugin`
> - `maven-shade-plugin`：uber-JAR（含依赖重定位）
> - `spring-boot-maven-plugin`：repackage 成可执行 JAR
> - `maven-assembly-plugin`：自定义打包结构（tar.gz, zip 等）

5. **质量与规范类**

- 静态分析、格式校验、安全扫描

> - `maven-checkstyle-plugin`
> - `maven-pmd-plugin`
> - `spotbugs-maven-plugin`（原 FindBugs）
> - `sonar-maven-plugin`
> - `license-maven-plugin`：检查/更新许可证头

6. **部署与发布类**

- 将构件推送到仓库或服务器

> - `maven-deploy-plugin`：部署到远程仓库（如 Nexus）
> - `wagon-maven-plugin`：通过 HTTP/FTP 上传文件
> - `docker-maven-plugin`（如 Spotify 或 Fabric8 版本）：构建并推送镜像

7. **自定义流程控制类**

- 实现项目特有的构建逻辑

> - `exec-maven-plugin`：调用 main 方法或脚本
> - `gmavenplus-plugin`：嵌入 Groovy 脚本
> - 自研插件：如生成 API 文档、校验 Git 提交信息、加密配置等

三、按 **开发来源** 分类

| 类型                  | 说明                                             | 典型 groupId                                         |
| --------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| **Apache 官方插件**   | 由 Maven 团队维护，命名规范为 `maven-xxx-plugin` | `org.apache.maven.plugins`                           |
| **第三方社区插件**    | 由 Spring、Google、JBoss 等组织维护              | `org.springframework.boot`, `com.google.cloud.tools` |
| **企业/个人自研插件** | 内部工具链扩展                                   | 通常为公司域名倒置，如 `com.mycompany.maven`         |

> ⚠️ 注意：Maven 对官方插件有命名约定——**只有 Apache 项目可用 `maven-xxx-plugin`**，第三方应使用 `xxx-maven-plugin`（如 `spring-boot-maven-plugin`）。这是为了防止命名冲突。

四、按 **执行上下文与副作用** 分类

1. **纯读取型（Read-only）**

- 仅读取项目元数据，不修改文件系统或网络

> - `maven-help-plugin:effective-pom`
> - `versions-maven-plugin:display-dependency-updates`

2. **写入型（Write/Modify）**

- 修改本地文件（生成代码、重写资源、打包）

> - `maven-compiler-plugin`
> - `maven-resources-plugin`（启用 filtering 时）

3. **网络交互型（Network I/O）**

- 与远程仓库、API、服务器通信

> - `maven-deploy-plugin`
> - `docker-maven-plugin:push`

4. **跨模块感知型（Multi-module Aware）**

- 能访问 reactor 中其他模块的信息（需特殊设计）

> - 自定义插件若注入 `@Parameter(defaultValue = "${reactorProjects}")` 可获取所有模块
> - 大多数标准插件**不具备跨模块上下文**，仅作用于当前 module

五、按 **技术实现复杂度** 分类（对开发者而言）

| 类型                | 特点                                                         |
| ------------------- | ------------------------------------------------------------ |
| **配置驱动型**      | 仅通过 `<configuration>` 控制行为，无自定义 Java 逻辑（如 `maven-resources-plugin`） |
| **标准 Mojo 型**    | 实现 `execute()`，使用 Maven 提供的上下文对象（如 `MavenProject`） |
| **字节码操作型**    | 在 `execute()` 中使用 ASM/Javassist 修改 `.class` 文件       |
| **脚本嵌入型**      | 内嵌 Groovy/JavaScript 引擎执行动态逻辑（如 `gmavenplus-plugin`） |
| **守护进程/服务型** | 启动长期运行进程（罕见，通常不推荐，因 Maven 是批处理模型）  |

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
maven-plugin 机制。从常识到进阶

# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链

# 当前问题
maven-plugin 中的一些基础概念有什么？
就个人目前的理解来看：
它在maven生命周期中起作用，集成了基于maven 规约下的各种操作，主要分类有：
1. maven 工具本身，比如清理缓存，pom解析，下载依赖，推送依赖等。
2. 代码分析测试部署构建相关插件

请你检查我的理解是否有遗误，并给出一个相对严谨的概念框架

# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```



