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



## 📄 `<resources>` 标签 —— 资源准入与变量替换

`<build><resources>` 描述主代码资源的处理规则。它主要回答三个问题：

1. 哪些文件属于本次构建的资源；
2. 这些文件复制到 classpath 的什么位置；
3. 复制时是否替换文件中的变量。

资源处理发生在 `process-resources` 阶段，由 `maven-resources-plugin:resources` 执行。其直接结果不是“生成 JAR”，而是先把资源复制到项目输出目录；默认输出目录是 `target/classes/`。执行到 `package` 阶段时，JAR/WAR 插件才会把这里的内容组装进最终制品。

```text
src/main/resources/**
        │
        │ process-resources
        ▼
target/classes/**              ← 运行时 classpath
        │
        │ package
        ▼
JAR / WAR
```

因此，理解 `<resources>` 时要先分清三个层次：

| 层次 | 负责的问题 | 典型检查位置 |
|------|------------|--------------|
| Maven 资源处理 | 文件有没有被复制、复制到哪里、内容有没有被改写 | `target/classes/` |
| Java classpath | 程序用什么路径访问资源 | `classpath:...` |
| Spring 配置加载 | 配置文件中的属性有没有进入 `Environment` | `PropertySources` / 启动日志 |

文件出现在 JAR 中，只说明 Maven 完成了资源复制；它不代表 Spring 一定会把该文件当作配置源读取。

### 🔖 默认行为

对于常见的 JAR 项目，即使不写 `<resources>`，Maven 也有如下约定：

- `src/main/resources/**` 在 `process-resources` 阶段复制到 `target/classes/**`；
- `filtering` 默认关闭，文件内容原样复制；
- 随后执行 `package` 时，`target/classes/**` 通常会进入 JAR；
- `src/test/resources/**` 由 `<testResources>` 描述，在 `process-test-resources` 阶段复制到 `target/test-classes/**`，只服务于测试 classpath。

这就是“约定优于配置”：目录符合约定时，不需要主动声明 `<resources>`。

### 🔖 三个控制面

#### 1. 选择文件：`directory`、`includes`、`excludes`

```xml
<build>
  <resources>
    <resource>
      <directory>src/main/resources</directory>
      <includes>
        <include>**/*.yml</include>
        <include>META-INF/**</include>
      </includes>
      <excludes>
        <exclude>**/*-local.yml</exclude>
      </excludes>
    </resource>
  </resources>
</build>
```

`directory` 指定资源源目录，`includes` 和 `excludes` 决定目录中的哪些文件可以进入输出目录。没有配置 `includes` 时，通常表示包含目录下的全部资源；若同一文件同时匹配 include 和 exclude，则 exclude 会将其排除。

需要特别注意：显式配置 `<resources>` 相当于重新声明资源集合，不是在 Maven 默认资源规则上“追加几行配置”。如果只声明了一个其他目录，却没有把 `src/main/resources` 写回来，那么其中的 `application.yml`、SPI 注册文件和 `META-INF/spring` 等内容都不会按原默认规则复制。

#### 2. 决定 classpath 路径：`targetPath`

```xml
<resource>
  <directory>src/main/config</directory>
  <targetPath>config</targetPath>
</resource>
```

假设源文件是 `src/main/config/app.yml`，处理后得到：

```text
target/classes/config/app.yml
```

应用访问它时，对应的 classpath 路径是 `classpath:config/app.yml`。因此，`targetPath` 改变的不只是 JAR 内部排版，也会改变程序查找资源时使用的路径。

#### 3. 改写文件内容：`filtering`

```xml
<properties>
  <build.name>order-service</build.name>
</properties>

<build>
  <resources>
    <resource>
      <directory>src/main/resources</directory>
      <filtering>true</filtering>
    </resource>
  </resources>
</build>
```

资源文件：

```properties
app.name=${build.name}
app.version=${project.version}
```

经过 `process-resources` 后，`target/classes` 中的文件已经被改写为具体值。这是**构建期插值**，不是应用启动后的动态取值。

### 🔖 filtering 原理

开启 `filtering` 后，`maven-resources-plugin` 会解析资源中的占位符。常见属性来源包括：

- Maven 项目模型，例如 `${project.version}`；
- POM 中的 `<properties>`；
- `-Dkey=value` 传入的用户属性；
- `<build><filters>` 引入的属性文件；
- 环境变量，例如 `${env.HOME}`。

使用外部 filter 文件时：

```xml
<build>
  <filters>
    <filter>src/main/filters/dev.properties</filter>
  </filters>
</build>
```

#### Maven filtering 与 Spring 占位符不是一回事

| 对比项 | Maven filtering | Spring 属性解析 |
|--------|-----------------|-----------------|
| 发生时间 | 构建期 | 应用启动期或运行期 |
| 执行者 | `maven-resources-plugin` | Spring `Environment` |
| 常见写法 | `${project.version}`、`@project.version@` | `${server.port}` |
| 属性来源 | POM、filter 文件、`-D` 参数等 | 配置文件、环境变量、命令行参数等 |
| 最终效果 | 输出文件内容被实际改写 | 从 Environment 中解析属性值 |

Maven 处理 `${...}` 时，可能提前消费原本想留给 Spring 的占位符。更清晰的做法是让 Maven 只处理 `@...@`，例如 `@project.version@`；Spring 继续使用 `${...}`：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-resources-plugin</artifactId>
  <configuration>
    <delimiters>
      <delimiter>@</delimiter>
    </delimiters>
    <useDefaultDelimiters>false</useDefaultDelimiters>
  </configuration>
</plugin>
```

这里的关键不是单纯增加 `@`，而是用 `useDefaultDelimiters=false` 停止 Maven 继续解析默认的 `${...}`。

如果一个资源不需要构建期插值，就保持 `filtering=false`。图片、证书、压缩包等二进制文件尤其不应参与文本过滤；确有混合需求时，可以拆成两条 `<resource>` 规则，分别处理需要过滤和原样复制的文件。

### 🔖 常见坑

- **只看最终 JAR，不看 `target/classes`**：资源问题发生在 `process-resources` 阶段，优先检查中间产物更容易判断是资源复制失败，还是后续打包失败。
- **自定义 `<resources>` 后丢失默认目录**：显式声明资源集合时，记得保留需要的 `src/main/resources` 规则。
- **误伤 Spring 占位符**：对 `application*.yml` 开启 filtering 后，Maven 和 Spring 可能争用 `${...}`。不需要构建期替换就关闭 filtering；需要时优先区分 delimiter。
- **过滤二进制文件**：filtering 本质上是文本处理，可能破坏图片、证书等文件。将二进制资源放在 `filtering=false` 的规则中。
- **资源进包但代码找不到**：检查 `targetPath`、大小写以及代码使用的 classpath 路径是否一致。
- **META-INF 文件意外丢失**：SPI 注册文件、`spring.factories`、`META-INF/spring/` 等同样受资源规则控制。详见 [META-INF.md](../../后端工程/Spring-persional/META-INF.md)。

### 🔖 资源问题的排查顺序

```text
1. 源文件是否位于 resource.directory 下？
   ↓
2. 是否被 includes / excludes 选中？
   ↓
3. process-resources 后是否出现在 target/classes？
   ↓
4. targetPath 是否改变了 classpath 路径？
   ↓
5. filtering 是否意外改写了文件内容？
   ↓
6. package 后文件是否进入 JAR/WAR？
   ↓
7. 框架或业务代码是否主动加载了该资源？
```

可直接检查中间产物和最终制品：

```bash
mvn process-resources
find target/classes -type f
jar tf target/your-artifact.jar
```

**一句话**：`<resources>` 是 Maven 在 `process-resources` 阶段使用的“文件选择 + 路径映射 + 构建期插值”规则；它决定资源如何进入 classpath，但不决定 Spring 是否加载这些资源。

### 🔖 场景：`resources/zk/` 子目录怎么进 Spring Environment

在 `src/main/resources/` 下新建子目录 `zk/`，放置 `zk.yml`、`zk.properties` 等配置。此时要分别回答两个问题：

1. Maven 有没有把文件复制进 classpath？
2. Spring Boot 有没有把文件加载进 `Environment`？

**先确认 Maven 资源处理**：默认规则会把 `src/main/resources/**` 连同子目录一起复制，所以该文件会出现在 `target/classes/zk/zk.yml`，对应 `classpath:zk/zk.yml`。只有自定义 `<resources>`、`includes` 或 `excludes` 后没有覆盖 `zk/**`，它才可能被排除。

**再确认 Spring 配置加载**：资源位于 classpath，不等于其属性已经进入 Spring `Environment`。Spring Boot 默认查找约定位置和约定名称的配置文件，不会因为任意 YAML 文件位于 classpath 就自动加载它。因此，`@Value("${zk.address}")` 能否取值，取决于是否显式导入了 `zk/zk.yml`。

**再让 Spring 加载它**，三种方式按场景选：

| 方式 | 配置 | 适用 |
|------|------|------|
| `spring.config.import`（推荐，2.4+） | `application.yml` 写 `spring.config.import: optional:classpath:zk/zk.yml` | 加载 yml/properties 进 Environment，支持多文件、可选 |
| `@PropertySource` | `@PropertySource("classpath:zk/zk.properties")` | 只认 `.properties`；yml 需自定义 `PropertySourceFactory` |
| 编程式 `EnvironmentPostProcessor` | 实现接口，`PropertySourceLoader` 读 `classpath:zk/` | 需条件化加载、多环境动态拼接时 |

**示例（推荐方式）**：

```yaml
# src/main/resources/application.yml
spring:
  config:
    import:
      - optional:classpath:zk/zk.yml        # zk 子目录的配置
      - optional:classpath:zk/zk-${spring.profiles.active}.yml
```

```yaml
# src/main/resources/zk/zk.yml
zk:
  address: 127.0.0.1:2181
  session-timeout: 30000
```

加载后 `@Value("${zk.address}")` / `@ConfigurationProperties(prefix = "zk")` 直接可用，等价于写在根 `application.yml` 里。

**坑**：

- `classpath:zk/application.yml` 默认也不会仅因文件名是 `application.yml` 就被自动扫描；是否加载仍取决于 Spring Boot 的配置搜索位置或显式 import。
- `@PropertySource` 原生不支持 YAML；要加载 YAML，优先使用 `spring.config.import`，或者提供自定义 `PropertySourceFactory`。
- 若配置含敏感信息，不应依靠 Maven filtering 将秘密固化进制品；敏感值更适合在部署或运行时通过环境变量、配置中心等方式注入。
- `optional:` 表示资源不存在时允许继续启动。若该配置是应用运行的硬性前提，就不要添加 `optional:`，让缺失尽早暴露。

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
