# Spring

## Container Overview

1. The `org.springframework.context.ApplicationContext` interface represents the Spring IoC container and is responsible for instantiating, configuring, and **assembling** the beans. 

   **assembling：** 组装

## Introduction to the Spring IoC Container and Beans

1. Dependency injection (DI) is a specialized form of IoC, **whereby** objects define their dependencies (that is, the other objects they work with) only through constructor arguments, arguments to a factory method, or properties that are set on the object instance after it is constructed or returned from a factory method. 

   **where by**：通过某种方法、手段或工具（by which / through which 通过这种方式）

2. The [`BeanFactory`](https://docs.spring.io/spring-framework/docs/6.2.9/javadoc-api/org/springframework/beans/factory/BeanFactory.html) interface provides an **advanced** configuration **mechanism** capable of managing any type of object. [`ApplicationContext`](https://docs.spring.io/spring-framework/docs/6.2.9/javadoc-api/org/springframework/context/ApplicationContext.html) is a sub-interface of `BeanFactory` 
   **advanced**：先进的、高级的 
   **mechanism**：机制 

## Core Technologies

1. This part of the reference documentation covers all the technologies that are absolutely **integral** to the Spring Framework. 

   **integral**：绝对不可缺的 

2. **Foremost** amongst these is the Spring Framework’s Inversion of Control (IoC) container. **A thorough treatment of** the Spring Framework’s IoC container is closely followed by comprehensive coverage of Spring’s Aspect-Oriented Programming (AOP) technologies. 
   **Foremost**：最重要的 
   **Inversion of Control：** 控制反转 
   **A thorough treatment of：** 对 ...... 进行彻底治疗之后、全面探讨 

3. The Spring Framework has its own AOP framework, which is **conceptually** easy to understand and which successfully **addresses the 80% sweet spot of AOP requirements** in Java enterprise programming. 

   **conceptually：** 概念上 
   **addresses the 80% sweet spot of AOP requirements**：满足了 80% 最常见、最典型的AOP 使用场景 

## Spring FrameWork Overview

1. Spring makes it easy to create Java **enterprise applications**.
   **enterprise application：企业级应用

2. It provides everything you need to **embrace the Java language** in an enterprise environment, with support for Groovy and Kotlin as **alternative languages** on the JVM, and with the flexibility to create many kinds of **architectures** depending on an application’s needs. **As of** Spring Framework 6.0, Spring requires Java 17+.

   **embrace the Java language** ： 拥抱 Java 语言
   **alternative languages** ：替代语言
   **the flexibility to create many kinds of architectures **：创建多种架构的灵活性
   **As of** 从....开始

3. Spring supports a wide range of **application scenarios.**
   **application scenarios** ： 应用场景

4. Others may run as a single jar with **the server embedded**, possibly in a cloud environment. 
   其它的应用可能作为一个单一的 JAR 文件来运行，这个 JAR 文件内部已经包含了（嵌入式服务器），它们可能运行在云环境中。（例如Spring boot 应用中内嵌了 Tomcat）

5. Spring is open source. It has a large and active community that provides continuous feedback based on **a diverse range of real-world use cases.**
   **a diverse range of real-world use cases ** ：各种各样的真实示例

6. The term "Spring" means different things in different contexts. It can be used to refer to the Spring Framework project itself, which is **where it all started**.
   **where it all started** ：一切的开始

7. Most often, when people say "Spring", they mean the entire family of projects. This **reference documentation** focuses on the foundation: the Spring Framework itself.

   **reference documentation：** 参考文档

8. At the heart are the modules of the core container, including a configuration model and a **dependency injection mechanism**. 
   **dependency injection mechanism** ：依赖注入机制

9. It also includes the Servlet-based Spring MVC web framework and, in parallel, the Spring WebFlux reactive web framework.

   它还包括 基于 Servlet 的 Spring MVC Web 框架以及 Spring webFlux 反应式Web 框架。

10. A note about modules: Spring Framework’s jars allow for deployment to the module path (Java Module System). For use in module-enabled applications, the Spring Framework jars come with `Automatic-Module-Name` manifest entries which define stable language-level module names (`spring.core`, `spring.context`, etc.) independent from jar artifact names. The jars follow the same naming pattern with `-` instead of `.` – for example, `spring-core` and `spring-context`. Of course, Spring Framework’s jars also work fine on the classpath.

   关于模块的一个说明：Spring Framework 的 JAR 包支持部署到模块路径（Java 模块系统）上。为了在启用了模块的应用中使用，Spring Framework 的 JAR 包包含了 `Automatic-Module-Name` 清单条目，这些条目定义了稳定的、语言级别的模块名称（如 `spring.core`、`spring.context` 等），这些名称独立于 JAR 包的工件名称。这些 JAR 包遵循相同的命名模式，只是用 `-` 代替了 `.`，例如 `spring-core` 和 `spring-context`。当然，Spring Framework 的 JAR 包在类路径上也能正常运行。

11. Spring came into being in 2003 **as a response to the complexity of the early [J2EE](https://en.wikipedia.org/wiki/Java_Platform,_Enterprise_Edition) specifications.**

    **as a response to the complexity of the early [J2EE](https://en.wikipedia.org/wiki/Java_Platform,_Enterprise_Edition) specifications.： ** 为了应对早起 J2EE 规范的复杂性

12. While some consider Java EE and its modern-day successor Jakarta EE to be in competition with Spring, they are in fact **complementary**. The Spring programming model does not embrace the Jakarta EE platform **specification**;rather, it integrates with carefully selected **individual** specifications from the traditional EE umbrella:

    **while: **  上述语言中表示 尽管\虽然
    **a. 时间连词：表示同时发生**

    - 这种用法通常涉及两个动作或状态在同一时间段内发生。
    - 常见搭配有进行时态（如 `was working`），强调持续性动作。

    **b. 对比连词：表示对比**

    - 用于连接两个相对立或不同的观点、事实或情况。
    - 通常出现在并列句中，用来突出两者之间的差异。

    **c. 让步连词：表示尽管/虽然**

    - 用于连接两个相对立或不同的观点、事实或情况。
    - 通常出现在并列句中，用来突出两者之间的差异。

    **complementary** ：补充、附加、另外

    **specification： 规格**
    **individual: ** 个人、个别、个体
    **the traditional EE umbrella:**  传统的 EE 框架 （umbrella 伞的意思）

13. The Spring Framework also supports the Dependency Injection ([JSR 330](https://www.jcp.org/en/jsr/detail?id=330)) and **Common Annotations ([JSR 250](https://www.jcp.org/en/jsr/detail?id=250)) specifications**, which application developers may choose to use instead of the Spring-specific mechanisms provided by the Spring Framework. Originally, those were based on common `javax` packages.

    **Common Annotations ([JSR 250](https://www.jcp.org/en/jsr/detail?id=250)) specifications** ：常见注解

14. Spring continues to innovate and to **evolve**.
    **evolve：** 发展

15. Provide choice at every level. **Spring lets you defer design decisions as late as possible**. For example, you can switch **persistence** providers through configuration without changing your code. The same is true for many other **infrastructure concerns** and integration with third-party APIs.

    **Spring lets you defer design decisions as late as possible**：Spring 让你可以尽可能推迟设计决策
    **persistence**：持久化
    **infrastructure concerns**：基础设施

16. **Accommodate diverse perspectives.**. Spring **embraces flexibility** and is not **opinionated** about how things should be done. It supports a wide range of application needs with different perspectives.

    **Accommodate diverse perspectives.**： 容纳多元化观点
    **embraces flexibility：** 拥抱灵活性
    **opinionated**： 固执己见

17. Maintain strong **backward compatibility**. Spring’s evolution has been carefully managed to force few breaking changes between versions. Spring supports a carefully chosen range of JDK versions and third-party libraries to **facilitate maintenance** of applications and libraries that depend on Spring.

    **backward compatibility**：向后兼容
    **evolution：** 进化
    **facilitate maintenance**：方便维护

18. Care about API design. The Spring team puts a lot of thought and time into making APIs that are **intuitive** and that hold up across many versions and many years.

    **intuitive：** 直观的

19. Set high standards for code quality. The Spring Framework puts a strong **emphasis** on meaningful, current, and accurate javadoc. It is one of very few projects that can claim clean code structure with no circular dependencies between packages.
    **emphasis**：强调

20. For how-to questions or **diagnosing** or debugging issues, we suggest using Stack Overflow. 

    **diagnosing**：诊断

****

## **Why Spring** - 7.31

1. Spring makes programming Java quicker, easier, and safer for everybody. Spring’s focus on speed, simplicity, and **productivity** has made **it** the [world's most popular](https://www.jetbrains.com/lp/devecosystem-2023/java/) Java framework.

   **it** 代指 Spring。关于 it 的代词语法

   a. 只能指代单数、中性事物（物体、动物、概念、想法、情况等）

   b. 分析逻辑结构和语义

2. We use a lot of the tools that come with the Spring framework and **reap** the benefits of having a lot of **the out of the box solutions**, and not having to worry about writing a ton of additional code—so that really saves us some time and energy.

   **reap:  收获**
   **the out of the box solutions： 开箱即用的解决方案**

3. **Spring’s flexible libraries** are trusted by developers all over the world. Spring **delivers** **delightful** experiences to millions of end-users every day—whether that’s [streaming TV](https://medium.com/netflix-techblog/netflix-oss-and-spring-boot-coming-full-circle-4855947713a0), [online shopping](https://tech.target.com/2018/12/18/spring-feign.html), or countless **other innovative solutions.** Spring also has contributions from all the big names in tech, including Alibaba, Amazon, Google, Microsoft, and more.

   **Spring’s flexible libraries：灵活的库**

   **delivers：传递**
   **delightful： 愉快的**
   **countless other innovative solutions.： 无数的其它创新解决方案**

   

4. Spring’s flexible and **comprehensive set of extensions** and third-party libraries let developers build almost any application imaginable. At its core, Spring Framework’s [Inversion of Control (IoC)](https://en.wikipedia.org/wiki/Inversion_of_control) and [Dependency Injection (DI)](https://en.wikipedia.org/wiki/Dependency_injection) **features provide the foundation for a wide-ranging set of features and functionality.** Whether you’re building secure, **reactive**, cloud-based microservices for the web, or **complex streaming data flows for the enterprise**, Spring has the tools to help.

   **comprehensive set of extensions： 全面综合的扩展**
   **features provide the foundation for a wide-ranging set of features and functionality.：IOC 和 DI 特性为广泛的功能和特性提供基础**：
   **reactive: 响应式** 

   **complex streaming data flows for the enterprise： 为企业提供复杂的数据流**

5. [Spring Boot](https://spring.io/guides/gs/spring-boot/) transforms how you approach Java programming tasks, **radically streamlining** your experience. Spring Boot combines necessities such as an application context and an auto-configured, embedded web server to make [microservice](https://spring.io/microservices) development a cinch. To go even faster, you can combine Spring Boot with Spring Cloud’s rich set of supporting libraries, servers, patterns, and templates, to safely deploy entire microservices-based architectures into the [cloud](https://spring.io/cloud), in record time.

   **Transforms： 改变、转换**
   **radically streamlining：彻底精简**
   **embedded web server： 嵌入式服务器**
   **make [microservice](https://spring.io/microservices) development a cinch. 使微服务开发轻而易举**

6. Our engineers care deeply about performance. With Spring, you’ll notice fast startup, fast shutdown, and **optimized execution**, by default. Increasingly, Spring projects also support the [reactive](https://spring.io/reactive) (nonblocking) programming model for even greater efficiency. Developer productivity is Spring’s superpower. Spring Boot helps developers build applications with ease and with far less toil than other competing paradigms. Embedded web servers, auto-configuration, and “fat jars” help you get started quickly, and innovations like [LiveReload in Spring DevTools](https://docs.spring.io/spring-boot/docs/current/reference/html/using-spring-boot.html#using-boot-devtools-livereload) mean developers can iterate faster than ever before. You can even start a new Spring project in seconds, with the Spring Initializr at [start.spring.io](https://start.spring.io/).

   **optimized execution** 优化执行
   **By default**: 默认情况下

   **far less toil than other competing paradigms.  比其他竞争的模式更加轻松、且省力很多。**

7. Spring has a **proven track record of dealing with security issues quickly and responsibly.** The Spring committers work with security professionals to **patch** and test any reported vulnerabilities. Third-party dependencies are also **monitored closely**, and **regular updates** are issued to help keep your data and applications as safe as possible. In addition, [Spring Security](https://spring.io/projects/spring-security) makes it easier for you to integrate with **industry-standard** security schemes and deliver trustworthy solutions that are secure by default.

   **Spring has a proven track record of dealing with security issues quickly and responsibly. ： Spring 团队在迅速、负责周全地处理安全问题方面具有长期可验证的良好记录**
   **patch： 补丁、修补**
   **vulnerabilities： 漏洞**
   **monitored closely：密切关注**
   **regular updates：定期更新**
   **Are issued to: 旨在、为了**
   **industry-standard：行业标准安全方案**

8. The [Spring community](https://spring.io/community) is **enormous**, global, diverse, and spans folks of all ages and capabilities, from complete beginners to **seasoned pros**. No matter where you are on your journey, you can find the support and resources you need to get you to the next level: [quickstarts](https://spring.io/quickstart), [videos](https://spring.io/guides>guides & tutorials, , [meetups](https://spring.io/events), [support](https://spring.io/support), or **even formal [training and certification](https://spring.io/training)**

   **enormous：巨大的**
   **seasoned pros：经验丰富的专业人士**

   **even formal training and certification.： 甚至是正式的培训和认证**

   

**Generative AI** 生成式AI
**Microsevices** 微服务
**Reactive** 响应式
**Cloud**
**Yep apps**
**Serverless** 无服务器
**Event Driven** 事件驱动
**Batch** 批处理