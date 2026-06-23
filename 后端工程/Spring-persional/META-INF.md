# 📌 META-INF

META-INF 是 Java 规范中 JAR/WAR 包内的**元数据目录**，由 JAR 规范（JSR-200）定义。所有 Java 归档文件（`.jar`、`.war`、`.ear`）都必须包含它，用于存放包级别的描述信息和服务发现机制。

Java 的 `java.util.jar`、`java.util.ServiceLoader`、`ClassLoader` 等核心 API 会**自动读取** META-INF 下的文件，无需开发者手动解析。

## 📄 MANIFEST.MF

MANIFEST = 清单（清单文件），JAR 包的"身份证 + 使用说明书"。由 `jar` 命令打包时自动生成，JVM 和构建工具自动读取。内容是纯文本的 `Key: Value` 键值对，存放在 JAR 根路径 `META-INF/MANIFEST.MF`。

```properties
Manifest-Version: 1.0
Main-Class: com.example.App
Class-Path: lib/spring-core-6.jar lib/spring-beans-6.jar
```

| 字段 | 作用 | 示例 |
|------|------|------|
| `Main-Class` | 可执行 JAR 的入口类 | `com.example.App` |
| `Class-Path` | 依赖 JAR 的相对路径 | `lib/spring-core-6.jar` |
| `Implementation-Title/Version` | 包的描述信息 | `My Library / 1.0.0` |
| `Multi-Release` | 多版本 JAR（JDK 9+）标记 | `true` |
| `Automatic-Module-Name` | 模块化系统的模块名（无 module-info.java 时） | `com.example.mylib` |
| `Sealed` | 密封包，禁止其他 JAR 扩展该包 | `true` |

### 🔖 Maven 构建时的生成时机

Maven 打包 JAR 经历两个关键阶段，MANIFEST.MF 会被**写两次**：

```
mvn package
  │
  ├─ 1. maven-jar-plugin（package 阶段）
  │     生成初版 MANIFEST.MF，打入 JAR
  │     默认只有 Manifest-Version: 1.0
  │     可通过 pom.xml 自定义追加字段 ↓
  │
  └─ 2. spring-boot-maven-plugin（repackage 阶段）
        读取初版 MANIFEST.MF → 追加 Spring Boot 特有字段 → 覆写
        追加：Main-Class / Start-Class / Spring-Boot-Version / Spring-Boot-Classes / Spring-Boot-Lib
        最终得到可执行的 fat JAR
```

**自定义字段的方法**（在 pom.xml 中）：

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-jar-plugin</artifactId>
      <configuration>
        <archive>
          <manifestEntries>
            <Implementation-Title>${project.name}</Implementation-Title>
            <Implementation-Version>${project.version}</Implementation-Version>
            <Automatic-Module-Name>com.example.mylib</Automatic-Module-Name>
          </manifestEntries>
        </archive>
      </configuration>
    </plugin>
  </plugins>
</build>
```

**注意**：`maven-jar-plugin` 生成的字段和 `spring-boot-maven-plugin` 追加的字段最终合并到同一个 MANIFEST.MF，两者不冲突——Spring Boot 插件是在初版基础上追加，不会覆盖你自定义的字段。

<img src="https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260623113505740.png" alt="image-20260623113505740" style="zoom:50%;" />

## 📄 SPI 服务发现（services/）

### 🔖 SPI 解决什么问题

JDK 定义了 `java.sql.Driver` 接口，但**不需要知道未来会有哪些数据库**。它只管两件事：定义接口 + 提供扫描工具。实现和注册全由第三方自己做。

```
JDK（完全被动）                 MySQL 团队（第三方）
┌─────────────────────┐       ┌─────────────────────────┐
│ 1. 定义接口          │       │ 1. 写实现类              │
│    java.sql.Driver   │       │    MySQLDriver           │
│    { connect(); }    │       │      implements Driver   │
│                      │       │                          │
│ 2. 提供扫描工具      │       │ 2. 在自己的 JAR 里注册    │
│    ServiceLoader     │       │    META-INF/services/    │
│                      │       │      java.sql.Driver     │
│ 我不知道谁会来，     │       │      内容：com.mysql...   │
│ 来了我就能发现。     │       │                          │
└─────────────────────┘       └─────────────────────────┘
          ↓                              ↓
          └──── 用户加个 JAR 依赖，运行时自动对接 ────┘
```

**三方各自的责任**：

| 角色 | 做什么 | 例子 |
|------|--------|------|
| JDK | 定义接口 + 提供 `ServiceLoader` 扫描工具 | `java.sql.Driver` 接口 |
| 第三方厂商 | 写实现 + 在自己 JAR 里创建 SPI 注册文件 | MySQL 写 `MySQLDriver`，注册到 `META-INF/services/java.sql.Driver` |
| 开发者 | 引入第三方 JAR 依赖 | `pom.xml` 加 `mysql-connector-j` |

**核心价值**：JDK 不需要知道谁会来，来了就能被发现。你加个 MySQL 驱动 JAR 就自动生效，不需要改任何代码。

### 🔖 SPI 与 Spring Bean 的关系

`spring.factories` 和 Java SPI 解决的是**同一个问题**，只是发现方不同：

```
Java SPI                              Spring spring.factories
┌──────────────────────┐              ┌──────────────────────┐
│ ServiceLoader        │              │ AutoConfiguration-   │
│   .load(Driver.class)│              │ ImportSelector       │
│                      │              │                      │
│ 扫描 META-INF/       │              │ 扫描 META-INF/       │
│   services/接口名     │              │   spring.factories   │
│                      │              │                      │
│ → 得到实现类实例      │              │ → 得到 Spring Bean    │
│   (Java 对象)        │              │   (IoC 容器管理)     │
└──────────────────────┘              └──────────────────────┘
```

| 维度 | Java SPI | Spring spring.factories |
|------|----------|------------------------|
| 约定目录 | `META-INF/services/接口名` | `META-INF/spring.factories` |
| 发现方 | `java.util.ServiceLoader`（JVM 原生） | `AutoConfigurationImportSelector`（Spring 实现） |
| 注册什么 | 接口的实现类 | 自动配置类 / 监听器 / 初始化器等 |
| 最终效果 | 得到一个实现类实例（普通 Java 对象） | 得到 Spring Bean（IoC 容器管理，支持注入、AOP 等） |
| 谁在用 | JDK 自身（JDBC、SLF4J） | Spring Boot 生态（所有 Starter） |

**一句话**：SPI 是 Java 原生的"注册 → 自动发现"机制，给的是普通对象；`spring.factories` 是同一套思想在 Spring 生态的变体，给的是 Spring Bean。两者解决的核心问题一样——接口定义方和实现方互不认识，但能自动对接。

### 🔖 典型使用场景

- JDBC 驱动注册（`java.sql.Driver`）—— 加驱动 JAR 就自动生效，不需要 `Class.forName()`
- SLF4J 绑定日志实现（`org.slf4j.spi.SLF4JServiceProvider`）—— 加 Logback 或 Log4j2 的 JAR 自动绑定
- Dubbo 服务提供者自动注册
- Spring Boot 的 `spring.factories` 本质也是 SPI 思想的变体

## 📄 Spring Boot 自动配置注册

`META-INF/spring.factories`（2.x）/ `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（3.x）——自动配置的注册入口。

> 详细机制见：`语言基础/java/Spring/spring boot/Spring boot 自动配置原理.md`

## 📄 安全签名

`META-INF/*.SF` / `*.DSA` / `*.RSA` 用于 JAR 签名验证（`jarsigner` 工具生成），保障包的完整性和来源可信。

## 📄 构建工具行为

| 工具 | 行为 |
|------|------|
| Maven | `src/main/resources/META-INF/` 原样打入 JAR；`<manifestEntries>` 追加 MANIFEST 字段 |
| Maven Shade | 合并多个 JAR 的 META-INF；`ServicesResourceTransformer` 自动追加 SPI 文件 |
| Gradle | `src/main/resources/META-INF/` 原样打入，`jar.manifest.attributes` 配置 MANIFEST |

## 📄 Spring 开发场景 · META-INF 设计范围盘点

### 🔖 场景一：封装自定义 Starter / SDK

> **需求**：团队有通用能力（Redis 工具、统一鉴权、日志切面等），想封装成 SDK，其他项目引入依赖就自动生效。

**执行流程**：

1. **编写自动配置类** — `@Configuration` + `@ConditionalOnClass` / `@ConditionalOnProperty` 等条件注解，决定何时生效
2. **注册到 META-INF** — 在 `src/main/resources/META-INF/` 下创建注册文件：

   | Spring Boot 版本 | 注册文件 |
   |------------------|----------|
   | 2.x | `spring.factories` → `org.springframework.boot.autoconfigure.EnableAutoConfiguration=com.xxx.XxxAutoConfiguration` |
   | 3.x | `spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` → 每行一个全限定类名 |

3. **（可选）添加配置元数据** — 创建 `META-INF/additional-spring-configuration-metadata.json`，给自定义 `application.yml` 属性加描述、默认值、类型约束，IDE 写配置时自动补全 + 悬浮提示
4. **发布 JAR** — `mvn deploy` 或推送到内部 Maven 仓库

**别人怎么用**：

```
pom.xml 加依赖 → Spring Boot 启动时扫描所有 JAR 的 META-INF 注册文件
→ 发现你的自动配置类 → 条件注解满足 → Bean 自动注入容器
→ 业务代码直接 @Autowired 使用，零配置
```

**涉及 META-INF 文件**：`spring.factories` / `AutoConfiguration.imports`（必须）、`additional-spring-configuration-metadata.json`（可选）

---

### 🔖 场景二：使用第三方 Starter（消费者视角）

> **需求**：项目要接 Redis、RabbitMQ、Elasticsearch 等中间件。

**你做的事**：`pom.xml` 加 `spring-boot-starter-data-redis` 依赖，在 `application.yml` 写配置。

**背后 META-INF 的作用**：Spring Boot 启动 → 扫描该 Starter JAR 的 `spring.factories` → 发现 `RedisAutoConfiguration` → 条件满足 → 自动注入 `RedisTemplate` 等 Bean → 你直接 `@Autowired` 用。

**理解 META-INF 的价值**：当自动配置不生效时，你知道去哪排查——检查 Starter JAR 里的 `spring.factories` 是否注册了、条件注解是否满足。

---

### 🔖 场景三：排查自动配置问题

> **需求**：引入了 Starter 但 Bean 没注入，或注入了意料之外的 Bean。

**排查手段**：

| 方法 | 操作 | 看什么 |
|------|------|--------|
| `/actuator/conditions` | 访问 Actuator 端点 | 每个自动配置类的条件匹配结果（matched / did not match） |
| `--debug` 启动参数 | `java -jar app.jar --debug` | 控制台输出条件评估报告 |
| 源码查看 | 解压 Starter JAR，看 `META-INF/spring.factories` | 注册了哪些自动配置类 |
| `@ConditionalOn*` 注解 | 读自动配置类源码 | 触发条件是什么（类存在？属性存在？Bean 不存在？） |

**排查流程**：发现问题 → 看 `actuator/conditions` 确认哪个配置类没生效 → 去对应 JAR 的 META-INF 找注册文件 → 读源码看条件注解 → 调整依赖或配置。

---

### 🔖 场景四：中间件 SPI 自动发现

> **需求**：引入数据库驱动、日志框架等，不想手动注册。

**你做的事**：`pom.xml` 加 `mysql-connector-j` 依赖，写 `spring.datasource.url`。

**背后 META-INF 的作用**：JAR 内部 `META-INF/services/java.sql.Driver` 注册了驱动实现类 → `java.util.ServiceLoader` 启动时自动发现 → JDBC 连接池直接可用。

| 中间件 | SPI 注册文件 | 效果 |
|--------|-------------|------|
| MySQL / PostgreSQL | `services/java.sql.Driver` | 不需要 `Class.forName("com.mysql.cj.jdbc.Driver")` |
| SLF4J + Logback | `services/org.slf4j.spi.SLF4JServiceProvider` | 自动绑定日志实现 |
| Dubbo | `services/...` | 服务提供者自动注册 |

**与 Spring 自动配置的关系**：SPI 是 Java 原生机制，Spring 的 `spring.factories` 是 SPI 思想在 Spring 生态的变体——同样是"注册 → 自动发现"，只是发现方从 `ServiceLoader` 换成了 Spring 的 `AutoConfigurationImportSelector`。

---

### 🔖 场景五：老项目维护（XML 命名空间）

> **需求**：维护使用 XML 配置的老 Spring 项目（Dubbo XML、Spring Integration 等），需要理解自定义标签怎么解析的。

| META-INF 文件 | 作用 | 示例 |
|---------------|------|------|
| `spring.handlers` | 自定义 XML 标签 → 解析器类映射 | `http\://dubbo.apache.org/schema/dubbo=DubboBeanDefinitionParser` |
| `spring.schemas` | XSD URL → 本地 classpath 路径映射 | 离线校验 XML，不依赖网络下载 XSD |

Spring Boot 时代基本不碰，但维护老项目时，理解这两个文件才能搞懂 `<dubbo:service>` 这种自定义标签是怎么变成 Bean 的。

---

### 🔖 场景六：Spring Boot 版本迁移（2.x → 3.x）

> **需求**：升级 Spring Boot 版本，自动配置注册方式变了。

| 变化 | 2.x | 3.x |
|------|-----|-----|
| 注册文件 | `META-INF/spring.factories` | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` |
| Key | `EnableAutoConfiguration` 作为 key | 无 key，直接每行写类名 |
| 兼容性 | — | 3.x 仍读 `spring.factories`，但已废弃，未来版本将移除 |

**迁移操作**：创建新文件 → 把类名从 `spring.factories` 的 value 部分逐行搬到新文件 → 删除旧文件中的自动配置条目。

---

### 🔖 场景七：运维与构建信息

| 文件 | 来源 | 用途 |
|------|------|------|
| `META-INF/maven/{groupId}/{artifactId}/pom.properties` | Maven 自动生成 | 依赖溯源：出问题时知道是哪个版本的 JAR |
| `META-INF/build-info.properties` | Spring Boot Maven Plugin | `/actuator/info` 展示构建时间、版本、Git commit |

---

**场景全景图**：

```
封装 SDK（场景一）          使用 Starter（场景二）        排查问题（场景三）
  编写自动配置类               pom.xml 加依赖              actuator/conditions
  ↓ 注册到 META-INF           ↓                          ↓ 看条件匹配
  发布 JAR                    Spring Boot 扫描 META-INF   解压 JAR 看 spring.factories
                              ↓ 发现自动配置类             ↓
                              Bean 自动注入               找到根因，调整配置
                              ↓
中间件 SPI（场景四）          业务代码直接用
  JAR 内 services/ 注册
  ↓ ServiceLoader 自动发现
  驱动/日志框架可用
```

## 📄 与 JPMS 模块化的关系

### 🔖 背景：JPMS 是什么

Java 9 引入 JPMS（Java Platform Module System），核心目标是解决 JAR hell——类路径扁平、包名冲突、依赖关系不透明。通过 `module-info.java` 显式声明模块的边界：

```java
module com.example.mylib {
    requires spring.core;        // 依赖谁
    exports com.example.api;     // 暴露哪些包给外部用
    opens com.example.impl to spring.beans;  // 允许反射访问（Spring 需要）
}
```

### 🔖 META-INF 与 module-info.java 的功能对比

| 维度 | META-INF（传统） | module-info.java（JPMS） |
|------|-----------------|------------------------|
| 模块名 | `MANIFEST.MF` 的 `Automatic-Module-Name` | `module com.xxx {}` 声明 |
| 依赖声明 | 无（靠 Maven/Gradle 管理） | `requires` 显式声明 |
| 包暴露控制 | 无（所有 public 类都可见） | `exports` 精确控制哪些包对外可见 |
| 反射开放 | 无限制 | `opens` 显式开放（Spring / Jackson 需要） |
| 服务声明 | `META-INF/services/` | `uses` / `provides...with` |
| 强制性 | 可选 | 模块化 JAR 必须声明 |

**一句话**：META-INF 是"松散元数据"，JPMS 是"强约束模块描述符"。META-INF 描述 JAR 自身属性，JPMS 描述 JAR 与外界的边界关系。

### 🔖 为什么需要 Automatic-Module-Name 过渡

现实问题：Spring Boot 项目的绝大多数依赖（Spring 自身、第三方库）仍是**非模块化 JAR**（没有 `module-info.java`）。但项目本身如果想用模块化，就需要给这些 JAR 一个模块名。

**没有 `Automatic-Module-Name` 时**：JVM 根据 JAR 文件名自动生成一个模块名（如 `spring-core-6.0.0.jar` → `spring.core.6.0.0`），这个名称不稳定——换版本就变，下游 `requires` 语句全部编译报错。

**有 `Automatic-Module-Name` 时**：MANIFEST.MF 声明稳定模块名（如 `Automatic-Module-Name: spring.core`），JAR 文件名变化不影响，下游可以安全地 `requires spring.core`。

```
非模块化 JAR                          模块化 JAR
┌─────────────────────┐              ┌─────────────────────┐
│ MANIFEST.MF         │              │ module-info.java    │
│   Automatic-Module-  │  过渡期依赖   │   requires spring.core │
│   Name: spring.core  │ ←─────────── │   exports com.xxx   │
│                     │              │                     │
│ (没有 module-info)  │              │ (完整模块声明)       │
└─────────────────────┘              └─────────────────────┘
```

### 🔖 实际开发中的影响

| 场景 | 影响 |
|------|------|
| Spring Boot 项目（大多数） | 不用管 JPMS，Spring Boot fat JAR 运行在类路径模式，META-INF 照常工作 |
| 封装 SDK 给模块化项目用 | 在 MANIFEST.MF 加 `Automatic-Module-Name`，给下游一个稳定的模块名引用 |
| 项目自身要模块化 | 需要写 `module-info.java`，处理好与非模块化依赖的兼容（`requires` 那些有 `Automatic-Module-Name` 的 JAR） |
| Spring 的 `opens` 问题 | Spring 反射注入 Bean 需要 `opens`，模块化 JAR 里要显式声明，否则运行时报 `InaccessibleObjectException` |

**结论**：目前 Spring Boot 生态主流仍是非模块化 + META-INF。JPMS 是未来方向，但 `Automatic-Module-Name` 在过渡期内是两者之间的桥梁——在 META-INF 里预埋一个稳定模块名，等依赖生态整体模块化后再迁移到 `module-info.java`。

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

对发散的自由捕捉、精确化

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

记录回顾、使用文档时，遇到的困惑。风格要求：Q&A 并列排布，每个问题直击要害，用分隔线区分，语言简洁朴素。适当情况下可增加简单推导或推理过程，但不堆砌。

**Q1：SPI 和 Spring IoC、Dubbo 注册中心是什么关系？都是"接口 + 实现 + 发现"，为什么我平时只碰后面两个？**

三者解决同一类问题，但作用层级不同：

| 维度 | Java SPI | Spring IoC | Dubbo 注册中心 |
|------|----------|------------|----------------|
| 接口定义方 | JDK | 你 | 你 |
| 实现注册方式 | `META-INF/services/` 文件 | `@Service` 注解 | `@DubboService` + 注册中心 |
| 发现方 | `ServiceLoader` | Spring 容器包扫描 | Consumer 查 Zookeeper / Nacos |
| 发现范围 | 本地 classpath | 本地 classpath | 远程网络（跨 JVM） |
| 你是否直接碰 | 几乎不碰 | 每天用 | 用 Dubbo 时用 |

SPI 是 JVM 级的原语，Spring IoC 用 `@Service` + 包扫描替代了它（注解 > 配置文件），Dubbo 用注册中心替代了它（远程发现 > 本地扫描）。你平时不直接碰 SPI，是因为框架帮你做了同样的事，只是方式更优雅。

你直接碰 SPI 的场景：写 SLF4J 日志实现绑定、写 JDBC 驱动、理解 `spring.factories` 为什么长那个样子。

---

**Q2：MySQL 实现了 Driver 接口，为什么还需要 SPI 注册？实现接口不就够了吗？**

实现接口 = "我会做"，SPI 注册 = "我在这"。光会做不够，还得让人找得到你。

没有 SPI 的年代，必须手动写 `Class.forName("com.mysql.cj.jdbc.Driver")` 来告诉 JDK：classpath 里有这个实现。有了 SPI，`DriverManager` 启动时自动调 `ServiceLoader.load(Driver.class)` 扫描所有 JAR 的 `META-INF/services/java.sql.Driver` 文件，自动发现所有实现。

`Class.forName()` 是手动指路，SPI 是自动登记。

## 🗺️ 修订记录

## 🛠️ 实践经历

记录实践经历：demo + 工作经历 + 第三方优秀经验反思

## ⚙️ prompt

探究该文档模块过程中的 prompt 记录

## 调研

AI 创建笔记时，调研结果追加到此处。仅记录相关经验和信息，由用户自行整理。
