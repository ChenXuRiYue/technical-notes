# 📌 maven-basic

整理些 maven 常识

## 📄 maven 背景

**AI 生成：**

在 2000 年代初，Java 生态正处于爆发期，但项目构建却极其混乱。开发者普遍使用 Ant（Apache Ant）——一个基于 XML 的任务驱动构建工具。Ant 灵活，但缺乏约定，每个项目都要从头写构建脚本，依赖管理更是手动下载 JAR 包、放到 lib 目录，极易出现“依赖地狱”（dependency hell）：版本冲突、传递依赖缺失、重复打包等问题。

Maven 最初由 Jason van Zyl 于 2002 年左右在 Apache Jakarta 项目中提出，其核心理念是 **“约定优于配置”（Convention over Configuration）**。它试图将构建过程标准化：源码放 src/main/java，测试放 src/test/java，输出到 target/…… 这些约定让项目结构统一，新人加入即可上手。

更重要的是，Maven 引入了 **项目对象模型（Project Object Model, POM）** —— 用一个 pom.xml 描述整个项目的元数据、依赖、构建生命周期。这不仅是配置文件，更是一种**声明式构建语言**。



### 🔖 **发展阶段：从工具到平台**

Maven 的演进大致可分为几个阶段：

1. **Maven 1（2004年前后）**
    基于 Jelly 脚本（一种 XML 脚本语言），插件机制原始，性能差，社区反馈不佳。
2. **Maven 2（2004年发布）**
    彻底重写，引入清晰的生命周期（clean, default, site）、标准目录结构、依赖传递机制（transitive dependencies）和中央仓库（Central Repository）。这是 Maven 成为主流的关键转折点。它首次实现了“声明依赖，自动下载+解析”的能力。
3. **Maven 3（2010年发布）**
    兼容 Maven 2 的 POM，但底层重构成更模块化、线程安全的架构。支持并行构建（-T 参数）、更好的错误报告、严格的 POM 验证。Maven 3 至今仍是主流（当前最新为 3.9.x），稳定性极高。
4. **Maven 4（尚未正式发布，但已在规划）**
    社区长期讨论，目标包括：更现代的 DSL（可能支持 Kotlin 或 YAML）、改进的依赖解析算法、原生支持模块化（JPMS）、更快的构建性能、更好的 IDE 集成等。但进展缓慢，部分原因是 Gradle 和 Bazel 等新工具分流了创新动力。

### 🔖 当前生态

如今，Maven 已远超“构建工具”的范畴，成为 Java 生态的**基础设施层**：

- **中央仓库（Maven Central）** 是全球最大的 Java 组件分发平台，托管数百万个 artifact。几乎所有开源 Java 库都通过它发布。
- **依赖管理事实标准**：即使你用 Gradle，它的依赖语法也沿用了 Maven 的 groupId/artifactId/version（GAV）坐标体系。
- **CI/CD 集成**：Jenkins、GitLab CI、GitHub Actions 等默认支持 mvn 命令，构建流程高度标准化。
- **插件生态**：从编译（maven-compiler-plugin）、打包（maven-jar-plugin）、测试（surefire）、静态分析（spotbugs）、到生成文档（javadoc）、发布（deploy）——几乎每个开发环节都有官方或社区插件。
- **BOM（Bill of Materials）机制**：通过 import scope 管理依赖版本一致性，被 Spring Boot、Quarkus 等框架广泛采用。

但也要看到挑战：

- **XML 的冗长性** vs. Gradle 的 Groovy/Kotlin DSL 更简洁；
- **构建速度慢**（尤其大型多模块项目）；
- **依赖冲突调试困难**（mvn dependency:tree 是常用但不够直观的工具）；
- **对非 Java 语言支持弱**（虽然可通过插件扩展，但不如 Bazel 或 Gradle 灵活）。

## 📄 maven 环境搭建

略

## 📄 maven 结构示例

```xml
<project>
  <!-- 必填 -->
  <modelVersion>4.0.0</modelVersion>
  <groupId>...</groupId>
  <artifactId>...</artifactId>
  <version>...</version>

  <!-- 可选：基础元数据 -->
  <packaging>...</packaging>
  <name>...</name>
  <description>...</description>
  <url>...</url>
  <inceptionYear>...</inceptionYear>
  <organization>...</organization>
  <licenses>...</licenses>
  <developers>...</developers>
  <contributors>...</contributors>
  <mailingLists>...</mailingLists>

  <!-- 继承与聚合 -->
  <parent>...</parent>
  <modules>...</modules>

  <!-- 属性 -->
  <properties>...</properties>

  <!-- 依赖 -->
  <dependencyManagement>...</dependencyManagement>
  <dependencies>...</dependencies>

  <!-- 构建 -->
  <build>
    <sourceDirectory>...</sourceDirectory>
    <resources>...</resources>
    <testResources>...</testResources>
    <plugins>...</plugins>
    <pluginManagement>...</pluginManagement>
    <!-- ...其他 build 子元素 -->
  </build>

  <!-- 仓库 -->
  <repositories>...</repositories>
  <pluginRepositories>...</pluginRepositories>

  <!-- 分发管理 -->
  <distributionManagement>...</distributionManagement>

  <!-- 报告（较少用） -->
  <reporting>...</reporting>

  <!-- Profiles -->
  <profiles>...</profiles>
</project>
```

## 📄 maven 三大核心生命周期

### 1. **clean 生命周期**

**目的**：清理项目构建产物（主要是 `target/` 目录）。

#### 阶段（phases）：

- `pre-clean`
- `clean` ← **最常用**，默认绑定 `maven-clean-plugin:clean`
- `post-clean`

```
mvn clean
```

→ 删除 `target/` 目录，确保下一次构建从“干净状态”开始。

> 💡 注意：`clean` 是一个独立生命周期。执行 `mvn clean compile` 会先运行 clean lifecycle，再运行 default lifecycle 到 `compile`。

------

### 2. **default 生命周期**

**目的**：完成项目的主要构建流程——从源码到可部署构件（artifact）。

这是你日常打交道最多的生命周期，包含如 `compile`、`test`、`package`、`install`、`deploy` 等关键阶段（前面已详述）。

核心阶段节选：

- `validate` → `compile` → `test` → `package` → `verify` → `install` → `deploy`

典型用法：

```
mvn package      # 构建 JAR/WAR
mvn install      # 构建并安装到本地仓库
mvn deploy       # 构建并发布到远程仓库
```

> ✅ 这是 Maven “构建”的主干道。

------

### 3. **site 生命周期**

**目的**：生成项目站点文档（project site），包括报告、依赖分析、测试覆盖率等。

在现代开发中使用较少（尤其在微服务+CI/CD普及后），但在需要生成正式项目文档或合规报告时仍有价值。

阶段（phases）：

- `pre-site`
- `site` ← 绑定 `maven-site-plugin:site`，生成 HTML 站点
- `post-site`
- `site-deploy` ← 将站点部署到服务器（如 Web 服务器）

典型用法：

```
mvn site
```

→ 在 `target/site/` 下生成静态网站，包含：

- 项目信息（POM 元数据）
- 依赖树
- Javadoc
- Surefire 测试报告
- Checkstyle / PMD / Jacoco 覆盖率（如果配置了相关插件）

> 📌 注意：site 生命周期的实用性高度依赖插件配置。默认生成的内容较基础，需显式引入报告插件才能丰富内容。

### 三大生命周期的关系：

**完全独立**

- 执行 `mvn clean` **不会**触发 default 或 site。
- 执行 `mvn deploy` **不会**自动 clean。
- 执行 `mvn site` **不会**编译代码（除非你手动绑定插件到 site 阶段）。

但你可以**组合调用**：

```
mvn clean site deploy
```

→ 依次执行：

1. clean lifecycle（清空 target）
2. site lifecycle（生成文档）
3. default lifecycle（直到 deploy）



## 🌳 生长思考

对发散的自由捕捉、精确化



## 💭 反复绊脚

1. 装了 IDEA 还需要装 maven 吗？

- IDEA 内置了 maven，如果使用 IDEA内的 maven，使用全局统一的 .m2/setting.xml 需要在 IDEA 中显示指定。如果本地安装了 maven，则需要在 IDEA 中将 maven 工具指向自己安装的 maven 目录。

----

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
关于 maven 

# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题
我希望了解 关于maven 的历史，当前的生态，以及后续的发展方向。

# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```