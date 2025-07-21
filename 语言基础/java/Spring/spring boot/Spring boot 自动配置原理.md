# Spring boot 自动配置原理

## 自动配置 感受

（就像我生在了21世纪，看着犁田机觉得，这不是生来如此吗？它就应该是这样的困惑。）

## **配置了什么？**

你的疑惑本质是“配置了什么？”，这让我觉得你可能在思考：自动配置到底在背后干了什么具体的事情？它配置的对象是什么？结果是什么？我会尽量用直白的方式解答，把这个“幕后操作”讲清楚，同时结合你之前的“犁田机”比喻，让你有个更具体的感受。

---

### 自动配置配置了什么？
本质上，Spring Boot 的自动配置是在配置 **你的应用程序运行所需的核心组件和服务**，这些组件在 Spring 里叫 **Bean**。说得更具体点，它配置的是：
- **功能模块**：比如 Web 服务、数据库连接、消息队列等。
- **运行环境**：比如端口号、线程池、日志级别等。
- **连接外部资源**：比如数据库、缓存服务器。

这些东西合起来，就是让你的程序能跑起来的“基础设施”。下面我拆开讲讲它到底配置了什么。

---

#### 1. **功能模块（工具箱里的工具）**
自动配置会根据你加的依赖，给你配置好相应的功能模块。比如：
- **加了 `spring-boot-starter-web`（想做网站）**：
  - 配置了啥？
    - 一个 Web 服务器（默认是 Tomcat），让你能接收 HTTP 请求。
    - 一个 `DispatcherServlet`，负责把请求分发给你的代码。
    - Spring MVC 的控制器支持，让你能写 `@Controller` 处理网页逻辑。
  - 结果：你写个 `@GetMapping("/hello")`，访问 `localhost:8080/hello` 就能看到页面。
- **加了 `spring-boot-starter-data-jpa`（想用数据库）**：
  - 配置了啥？
    - 一个 `DataSource`（数据源），连接你的数据库。
    - 一个 `EntityManager`，帮你操作数据库里的表。
    - 一个事务管理器，处理数据库事务（比如提交或回滚）。
  - 结果：你写个 `@Entity` 类和 `@Repository`，就能直接存取数据。

就像犁田机自带了犁头、播种器，你说要种田，它就自动把这些工具装好。

---

#### 2. **运行环境（田地的基本条件）**
自动配置还会设置一些运行时的“基础条件”，让程序能正常工作。比如：
- **端口号**：默认配置 Web 服务器跑在 8080 端口。
- **线程池**：配置 Tomcat 的线程池，让它能处理多个请求。
- **日志**：默认用 Logback，配置好日志级别和输出格式。
- **静态资源路径**：配置 `/static` 文件夹，让你放网页的 CSS、JS 文件。

这些就像犁田机自动调好了马力、油门，你不用自己去拧螺丝。

---

#### 3. **外部资源连接（水源和仓库）**
如果你的程序需要跟外部系统打交道，自动配置会帮你连上。比如：
- **数据库**：
  - 配置了啥？一个 `DataSource`，可能用 HikariCP 连接池，连接到 MySQL、H2 或其他数据库。
  - 怎么知道连哪？从 `application.properties` 里读 `spring.datasource.url`。
- **消息队列**：
  - 加了 `spring-boot-starter-amqp`，会配置 RabbitMQ 客户端。
- **缓存**：
  - 加了 `spring-boot-starter-cache`，会配置 Redis 或 Ehcache。

就像犁田机自动接上了水渠、种子仓，你不用自己去挖沟引水。

---

### 配置的本质是什么？
用一句话概括：**自动配置配置的是 Spring 容器里的 Bean，以及这些 Bean 运行所需的设置**。
- **Bean 是啥？** 就是程序里的“零件”，比如数据库连接对象、Web 服务器对象。
- **设置是啥？** 就是这些零件的参数，比如数据库地址、服务器端口。

这些 Bean 和设置被装进 Spring 的“工具箱”（ApplicationContext），你需要时直接拿来用。

---

### 用“犁田机”比喻讲清楚
假设你是个农民（开发者），想种田（写程序）：
- **没有自动配置（传统 Spring）**：
  - 你得自己造犁田机：找个发动机（Web 服务器）、装个犁头（MVC）、挖条水渠（DataSource），还得调好油门（端口号）。
  - 每一步都要你亲手做，写一堆 XML 或 Java 代码。
- **有了自动配置（Spring Boot）**：
  - 你只要说：“我要种小麦（加个 Web 依赖）。”
  - Spring Boot 就像个智能犁田机，自动装好犁头、接上水渠、调好马力（配置 Web 服务器、MVC、端口），直接开动。
  - 如果你想换个播种方式（改配置），加句指令（改 `application.properties`）就行。

配置的内容就是：**犁田机本身（功能模块）+田地的准备（运行环境）+水源种子（外部资源）**。

## **自动配置到底简洁了哪一步？**

场景： 我在配置 web应用，数据库访问、日志配置。

#### Spring:

**控制器配置**

```java
package com.example;

import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.mvc.Controller;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class HelloController implements Controller {
    @Override
    public ModelAndView handleRequest(HttpServletRequest request, HttpServletResponse response) {
        ModelAndView mav = new ModelAndView("hello"); // 视图名
        mav.addObject("message", "Hello, World!");
        return mav;
    }
}
```

**XML配置**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:context="http://www.springframework.org/schema/context"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
       http://www.springframework.org/schema/beans/spring-beans.xsd
       http://www.springframework.org/schema/context
       http://www.springframework.org/schema/context/spring-context.xsd">

    <!-- 定义控制器 -->
    <bean id="helloController" class="com.example.HelloController" />

    <!-- URL 映射 -->
    <bean id="urlMapping" class="org.springframework.web.servlet.handler.SimpleUrlHandlerMapping">
        <property name="mappings">
            <props>
                <prop key="/hello">helloController</prop>
            </props>
        </property>
    </bean>

    <!-- 视图解析器 -->
    <bean id="viewResolver" class="org.springframework.web.servlet.view.InternalResourceViewResolver">
        <property name="prefix" value="/WEB-INF/views/" />
        <property name="suffix" value=".jsp" />
    </bean>
</beans>
```

**Web配置**

```xml
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">
    <servlet>
        <servlet-name>dispatcher</servlet-name>
        <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
        <init-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>/WEB-INF/applicationContext.xml</param-value>
        </init-param>
        <load-on-startup>1</load-on-startup>
    </servlet>
    <servlet-mapping>
        <servlet-name>dispatcher</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>
</web-app>
```

JSP 视图：
```jsp
<html>
<body>
<h1>${message}</h1>
</body>
</html>
```

启动方式： 部署到 Tomcat 等Servlet 容器。



#### Spring Boot 配置

**控制器：**

```java
package com.example;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    @GetMapping("/hello")
    public String sayHello() {
        return "Hello, World!";
    }
}
```

**主类**

```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**依赖**

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.2.4</version>
    </dependency>
</dependencies>
```

自动配置了什么？

TomCat，Spring MVC, DispatcherServlet， 默认端口号。

---

### 总结：Spring Boot 的便捷性
| 方面         | 传统 Spring（手动配置）                | Spring Boot（自动配置）   |
| ------------ | -------------------------------------- | ------------------------- |
| **Web 应用** | XML 配置 Servlet、视图解析器，部署麻烦 | 加依赖，写控制器，直接跑  |
| **数据库**   | 手动配 DataSource、JdbcTemplate        | 加依赖 + 属性，DAO 直接用 |
| **日志**     | 写 XML 配置 Log4j                      | 默认可用，属性调整即可    |
| **代码量**   | 多文件、多配置                         | 少文件、少配置            |

**经典位置的感受**：
- **传统 Spring**：配置分散在 XML、`web.xml`、代码里，改个东西要找半天。
- **Spring Boot**：配置集中在 `pom.xml`（依赖）和 `application.properties`，核心逻辑在代码里，一目了然。



## 自动配置原理以及流程

Spring Boot 的自动配置原理可以用一句话概括：**基于条件判断和约定优于配置的机制，Spring Boot 在应用程序启动时动态加载并配置所需的 Bean 和环境设置。** 下面我会详细拆解它的原理，结合代码和流程，让你彻底理解它是怎么工作的。

---

### 自动配置的核心原理
自动配置的核心在于以下几个关键点：
1. **条件注解（Conditional Annotations）**：根据运行时环境（如类路径、属性值）决定是否应用某个配置。
2. **`spring.factories` 文件**：定义了所有可能的自动配置类，Spring Boot 在启动时加载它们。
3. **`@EnableAutoConfiguration` 注解**：自动配置的入口，触发整个机制。
4. **Spring 容器**：最终执行配置，把 Bean 装进容器。

这些机制协作起来，让 Spring Boot 做到“智能配置”。下面我一步步展开。

---

### 1. **自动配置的入口：@EnableAutoConfiguration**
Spring Boot 的主类通常标注 `@SpringBootApplication`，而它包含了 `@EnableAutoConfiguration`，这是自动配置的起点。

#### 代码位置
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

- `@SpringBootApplication` 是 `@Configuration`、`@EnableAutoConfiguration` 和 `@ComponentScan` 的组合。
- `@EnableAutoConfiguration` 告诉 Spring Boot：“我要自动配置，请开始工作！”

#### 背后原理
- `@EnableAutoConfiguration` 通过导入 `AutoConfigurationImportSelector` 类启动自动配置流程。
- `AutoConfigurationImportSelector` 会去读取 `META-INF/spring.factories` 文件，加载所有可能的自动配置类。

---

### 2. **`spring.factories` 文件：配置清单**
`spring.factories` 文件是自动配置的“蓝图”，位于每个 Spring Boot Starter 的 JAR 包中（路径：`META-INF/spring.factories`）。

#### 经典示例
```properties
# 来自 spring-boot-autoconfigure.jar
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration,\
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,\
org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration
```

- **作用**：列出了所有可能的自动配置类。
- **原理**：Spring Boot 在启动时扫描所有依赖中的 `spring.factories`，把这些配置类加载到候选列表中，等待条件判断。

---

### 3. **条件注解：动态决策**
自动配置类并不是一股脑儿全加载，而是通过条件注解（`@Conditional`）来决定是否生效。Spring Boot 使用了 Spring Framework 的条件机制。

#### 经典条件注解
- **`@ConditionalOnClass`**：检查类路径中是否存在某个类。
- **`@ConditionalOnMissingBean`**：如果容器中没有某个 Bean，则创建。
- **`@ConditionalOnProperty`**：根据配置文件中的属性值决定。

#### 示例代码：`DataSourceAutoConfiguration`
```java
@Configuration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class }) // 需有 DataSource 类
@EnableConfigurationProperties(DataSourceProperties.class) // 读取 spring.datasource.* 属性
@Import({ HikariDataSourceConfiguration.class })
public class DataSourceAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean // 如果用户没定义 DataSource，则提供默认的
    public DataSource dataSource(DataSourceProperties properties) {
        // 创建并配置 DataSource
    }
}
```

- **原理**：
  - 如果类路径中有 `DataSource`（比如加了 JDBC 依赖），这个配置类生效。
  - 如果用户没手动定义 `DataSource` Bean，Spring Boot 就用默认的（比如 HikariCP）。
  - 属性（如 `spring.datasource.url`）会从 `application.properties` 读取。

---

### 4. **工作流程：从启动到配置**
自动配置的原理可以用一个流程来描述：

#### 步骤分解
1. **启动 SpringApplication**：
   - `SpringApplication.run()` 创建 `ApplicationContext`（Spring 容器）。
   - `@EnableAutoConfiguration` 触发 `AutoConfigurationImportSelector`。

2. **加载 spring.factories**：
   - `AutoConfigurationImportSelector` 读取所有 JAR 包中的 `spring.factories`，获取自动配置类的列表。
   - 比如加载 `WebMvcAutoConfiguration`、`DataSourceAutoConfiguration`。

3. **条件评估**：
   - 对每个自动配置类，Spring Boot 检查条件注解。
   - 比如：
     - `WebMvcAutoConfiguration` 需要类路径中有 `Servlet` 和 `DispatcherServlet`。
     - `DataSourceAutoConfiguration` 需要有 `DataSource` 类和数据库驱动。

4. **创建 Bean**：
   - 条件满足的配置类会被加载，它们的 `@Bean` 方法执行，生成 Bean。
   - 这些 Bean 被注入到 Spring 容器。

5. **用户覆盖**：
   - 如果用户手动定义了某个 Bean（比如自定义 `DataSource`），自动配置会跳过（`@ConditionalOnMissingBean` 的作用）。
   - 用户还可以通过 `application.properties` 修改默认设置。

#### 流程图（文字版）
```
启动 SpringApplication
    ↓
加载 spring.factories（候选配置类）
    ↓
条件评估（@Conditional）
    ↓
满足条件的配置类生效
    ↓
创建 Bean 并注入容器
    ↓
用户自定义覆盖（可选）
```

---

### 5. **代码中的经典体现**
让我们结合一个具体例子，看看自动配置的原理如何体现在代码中。

#### 示例：Web 自动配置
- **依赖**（`pom.xml`）：
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

- **自动配置类**（`WebMvcAutoConfiguration`）：
```java
@Configuration
@ConditionalOnWebApplication(type = ConditionalOnWebApplication.Type.SERVLET) // 需要是 Web 应用
@ConditionalOnClass({ Servlet.class, DispatcherServlet.class }) // 需要 Servlet 环境
@AutoConfigureAfter({ DispatcherServletAutoConfiguration.class })
public class WebMvcAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public DispatcherServlet dispatcherServlet() {
        return new DispatcherServlet();
    }
}
```

- **结果**：
  - 加了 `spring-boot-starter-web`，类路径中有 `Servlet` 和 `DispatcherServlet`。
  - `WebMvcAutoConfiguration` 生效，配置了 `DispatcherServlet` 和嵌入式 Tomcat。
  - 你写个 `@RestController`，就能直接跑 Web 服务。

---

### 6. **原理的本质**
自动配置的本质是：
- **约定优于配置**：通过默认规则（比如默认端口 8080、默认 HikariCP）减少手动配置。
- **条件驱动**：根据环境（依赖、属性）动态选择配置。
- **模块化**：每个功能（Web、数据库等）有独立的自动配置类，互不干扰。

就像一台“智能机器”，它会：
1. 看你带了什么零件（依赖）。
2. 根据零件决定装什么功能（条件注解）。
3. 用默认设置装好（`spring.factories` 和 `@Bean`）。
4. 让你随时调整（配置文件或自定义 Bean）。

---

### 总结
Spring Boot 自动配置的原理是通过 `@EnableAutoConfiguration` 启动，从 `spring.factories` 加载配置类，用条件注解动态筛选，最终在 Spring 容器中生成 Bean。相比传统 Spring 的手动配置（XML 或 Java Config），它把繁琐的“手工组装”变成了“智能流水线”，极大地提高了开发效率。

## 使用自动配置的基本方法

明白了，你的意思是想了解如何“自定义 SDK”（Software Development Kit），而不是直接使用 Spring Boot 的自动配置。我猜你可能是想知道如何在 Spring Boot 的基础上，创建一个自定义的 SDK（比如一个封装好的工具包或库），让它也能利用自动配置的原理，或者你想深入探讨如何在 Spring Boot 中自定义自动配置的实现。以下我会从 Spring Boot 的自动配置原理出发，总结一个**自定义 SDK 并使用自动配置的基本方法**，并结合代码示例，让你清楚地看到如何操作。

---

### 自定义 SDK 并使用自动配置的基本方法

自定义 SDK 的目标通常是封装一些功能（比如工具类、服务），并让它在 Spring Boot 项目中“即插即用”。通过利用 Spring Boot 的自动配置机制，你可以让你的 SDK 自动加载并配置好，减少使用者的手动配置工作。以下是具体步骤：

#### 1. **创建 SDK 项目并定义功能**
- **做什么**：创建一个独立的 Maven 或 Gradle 项目，作为你的自定义 SDK，包含核心功能代码。
- **怎么做**：
  - 定义一个功能类（比如一个服务或工具）。
  - 打包成 JAR，供其他项目依赖。
- **示例**：
  - 创建一个简单的 SDK 项目 `my-sdk`。
  - 定义一个服务类：
```java
package com.example.mysdk;

public class MySdkService {
    private String message;

    public MySdkService(String message) {
        this.message = message;
    }

    public String sayHello() {
        return "Hello from MySdk: " + message;
    }
}
```

---

#### 2. **添加 Spring Boot 依赖**
- **做什么**：让你的 SDK 支持 Spring Boot 的自动配置，引入必要的 Spring Boot 依赖。
- **怎么做**：
  - 在 `pom.xml` 中添加 `spring-boot-starter` 和 `spring-boot-autoconfigure`。
- **示例**（`pom.xml`）：
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
        <version>3.2.4</version>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-autoconfigure</artifactId>
        <version>3.2.4</version>
    </dependency>
</dependencies>
```

---

#### 3. **创建自动配置类**
- **做什么**：编写一个 `@Configuration` 类，利用条件注解实现自动配置逻辑。
- **怎么做**：
  - 定义一个配置类，创建 `MySdkService` 的 Bean。
  - 使用条件注解（如 `@ConditionalOnProperty`）让配置更灵活。
- **示例**：
```java
package com.example.mysdk;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConditionalOnProperty(prefix = "mysdk", name = "enabled", havingValue = "true", matchIfMissing = true)
public class MySdkAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public MySdkService mySdkService(MySdkProperties properties) {
        return new MySdkService(properties.getMessage());
    }
}
```
- **说明**：
  - `@ConditionalOnProperty`：只有当 `mysdk.enabled=true`（或未设置时默认 true）时生效。
  - `@ConditionalOnMissingBean`：如果用户没手动定义 `MySdkService`，就用这个默认的。

---

#### 4. **定义配置属性（可选）**
- **做什么**：允许用户通过配置文件（如 `application.properties`）自定义 SDK 的行为。
- **怎么做**：
  - 创建一个属性类，用 `@ConfigurationProperties` 绑定配置。
- **示例**：
```java
package com.example.mysdk;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "mysdk")
public class MySdkProperties {
    private String message = "Default Message";

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
```
- 在自动配置类中启用：
```java
@Configuration
@EnableConfigurationProperties(MySdkProperties.class) // 启用属性绑定
@ConditionalOnProperty(prefix = "mysdk", name = "enabled", havingValue = "true", matchIfMissing = true)
public class MySdkAutoConfiguration {
    // 同上
}
```

---

#### 5. **注册自动配置到 `spring.factories`**
- **做什么**：告诉 Spring Boot 在启动时加载你的自动配置类。
- **怎么做**：
  - 在 `src/main/resources/META-INF` 下创建 `spring.factories` 文件。
- **示例**（`META-INF/spring.factories`）：
```
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.mysdk.MySdkAutoConfiguration
```
- **效果**：Spring Boot 启动时会扫描这个文件，加载 `MySdkAutoConfiguration`。

---

#### 6. **打包并发布 SDK**
- **做什么**：将 SDK 打包成 JAR，发布到 Maven 仓库或本地使用。
- **怎么做**：
  - 用 `mvn clean install` 打包。
  - 其他项目通过依赖引入：
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>my-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

---

#### 7. **在应用中使用自定义 SDK**
- **做什么**：在 Spring Boot 应用中引入 SDK，验证自动配置效果。
- **怎么做**：
  - 添加依赖，写一个控制器测试。
- **示例**：
  - 主类（保持不变）：
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```
  - 控制器：
```java
package com.example.demo;

import com.example.mysdk.MySdkService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
    @Autowired
    private MySdkService mySdkService;

    @GetMapping("/test")
    public String test() {
        return mySdkService.sayHello();
    }
}
```
  - 可选配置文件（`application.properties`）：
```properties
mysdk.message=Custom Message
mysdk.enabled=true
```
- **运行结果**：访问 `localhost:8080/test`，返回 "Hello from MySdk: Custom Message"。

---

### 方法总结
| 步骤          | 操作                          | 关键代码/文件                 |
| ------------- | ----------------------------- | ----------------------------- |
| 创建 SDK 项目 | 定义功能类                    | `MySdkService.java`           |
| 添加依赖      | 引入 Spring Boot 依赖         | `pom.xml`                     |
| 自动配置类    | 用 `@Configuration` 定义 Bean | `MySdkAutoConfiguration.java` |
| 配置属性      | 用 `@ConfigurationProperties` | `MySdkProperties.java`        |
| 注册自动配置  | 创建 `spring.factories`       | `META-INF/spring.factories`   |
| 打包发布      | 用 Maven 打包并发布           | `mvn clean install`           |
| 使用 SDK      | 在应用中引入并测试            | `TestController.java`         |

---

### 便捷性感受
- **传统方式**：如果没有自动配置，你需要在每个项目中手动创建 `MySdkService` 的 Bean，配置它的属性，还要处理依赖注入。
- **自定义 SDK + 自动配置**：只需加个依赖，写几行配置（甚至不写也行），SDK 就自动工作，像 Spring Boot 自带的功能一样无缝。



