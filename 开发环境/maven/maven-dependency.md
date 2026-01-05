# 📌 maven-dependency

该文档总结 maven 依赖模块机制的细节

## 📄 Artifact (构件)

每个依赖在 maven 中是一个 artifact，由三元组唯一标识：
`groupId:artifactId:version`

classifier (jdk8，sources，javadoc)

> classifier 是可选的字符串，附加在文件名中，用于区分同一 artifact 的不同“附属产物”或“构建变体”。
> **命名规则**：最终文件名格式为：
>  `${artifactId}-${version}-${classifier}.${packaging}`

packaging  (jar，war，pom)

> packaging 声明该 artifact 的**构建产物类型**，决定了 Maven 如何处理它。它出现在 POM 的 `<packaging>` 元素中，默认是 `jar`。
>
> - 常见值：
>   - `jar`：标准 Java 库
>   - `war`：Web 应用归档（部署到 Tomcat 等）
>   - `pom`：**不是代码库，而是元数据容器**（如 BOM、父 POM）
>   - `ear`：企业应用（Java EE）
>   - `maven-plugin`：Maven 插件本身

## 📄 声明方式

在 POM 的 `<dependencies>` 中通过 `<dependency>` 声明直接依赖。

## 📄 依赖的作用域

`控制依赖在不同 classpath（编译、测试、运行等）中的可见性`

- `compile`（默认）：全程可用
- `provided`：JDK 或容器提供（如 servlet-api）
- `runtime`：编译不需要，运行需要（如 JDBC 驱动）
- `test`：仅测试阶段（如 JUnit）



## 📄 依赖管理

- `<dependencyManagement>` 不引入依赖，仅**统一版本与配置**。
- 子模块继承后，只需声明 GAV，无需 version/scope 等。
- 是多模块项目控制依赖一致性的核心机制。
- 通常与 BOM（Bill of Materials，packaging=pom）配合使用，如 Spring Boot 的 `spring-boot-dependencies`。

## 📄 依赖调解和冲突解决

Maven 自动解析以来的依赖，构建依赖树。可通过 `mvn dependency:tree` 查看实际解析结果

- 当同一 artifact 出现多个版本时，Maven 不使用“最新版本优先”，而是：
  - **路径最短优先**：A → B → C(v1) vs A → D → E → C(v2)，选 v1
  - 若路径长度相同，则**先声明者胜出**（POM 中顺序）
- 这是非确定性的潜在来源，需通过 `<dependencyManagement>` 显式锁定

### 📄 可选依赖 （Optional Dependencies）

- `<optional>true</optional>` 表示该依赖**不会传递**给使用者。
- 语义上表示“该功能是可插拔的”，如日志实现（slf4j + logback）
- 使用者若需要此功能，必须显式声明

## 📄 依赖排除（Exclusions）

- 在 `<dependency>` 内使用 `<exclusions>` 主动切断传递依赖链。
- 常用于解决冲突、移除冗余或替换实现（如用 logback 替代 log4j）
- 排除基于 GAV，不验证是否存在

### 📄 **仓库体系（Repository System）**

- 本地仓库（~/.m2/repository）：缓存所有下载的 artifacts。
- 远程仓库（如 Maven Central、公司 Nexus）：按需拉取。
- 仓库优先级、镜像（mirror）、代理等影响依赖解析路径。
- SNAPSHOT 版本支持开发中的频繁更新，通过时间戳元数据实现。



## 🌳 生长思考

1. 多个包引入了同一个依赖，maven 选择哪些版本？

2. 依赖冲突是什么？为什么会产生依赖冲突？怎么解决依赖冲突？

   > Maven 的“冲突解决”只解决“选哪个版本”，但不保证“选出来的版本在语义上兼容
   >
   > 有时候为了避免版本漂移，项目使用了禁止插件：如 enforcer。要求所有路径解析到同一个版本，否则构建失败 -- 把隐式风险显示化
   >
   > ```
   > <groupId>org.apache.maven.plugins</groupId>
   >   <artifactId>maven-enforcer-plugin</artifactId>
   >   <executions>
   >     <execution>
   >       <id>enforce</id>
   >       <configuration>
   >         <rules>
   >           <dependencyConvergence/> <!-- 禁止同一 GAV 多版本 -->
   >         </rules>
   >       </configuration>
   >     </execution>
   >   </executions>
   > </plugin>
   > ```

💭 反复绊脚

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
maven - 依赖
# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题
请你为我提供一份关于 maven 依赖体系的概念体系清单，类似于大纲

# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```



