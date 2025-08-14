# 📖 Spring Framework Overview

**From: ** [Spring Framework overview](https://docs.spring.io/spring-framework/reference/overview.html#overview-feedback)

## Overview

使命：更简单的开发 Java 企业级应用

语言：Java（逐渐要求更新更实用的 Java 版本）以及 kotlin 、groovy 等运行在虚拟机中的语言

生态：广泛的生态，大量的用户提供了真实的业务场景来指导 Spring 的发展


## what we Mean by "Spring"

官方文档中没有谈到 Spring 名称的历史。通过资料查询，Spring 大概源于 Java 早期配置的复杂性，有冬去春来之意。

不同的上下文下，**Spring** 代表了不同的语义。
1. > It can be used to refer to the Spring Framework project itself, which is where it all started.

​	指代这个 Spring Framework 本身，它是所有生态的基础。包括了 依赖注入、面向切面变成、事务管理、数据访问、Web MVC 等

2. > Most often, when people say "Spring", they mean the entire family of projects. This reference documentation focuses on the foundation: the Spring Framework itself.

 	大多数时候指的是整个生态的产品 - 包括了 Spring boot、Spring Security、Spring Security 等。

Spring Framework 分为若干模块。其核心模块包括了配置模型、依赖注入等。在这个基础上，Spring 支持了不同的应用框架。

> Beyond that, the Spring Framework provides foundational support for different application architectures, including **messaging**, **transactional data** and **persistence**, and **web**. It also includes the **Servlet-based Spring MVC web framework** and, in parallel, **the Spring WebFlux reactive web framework**.

## History of Spring and Spring Framework

> Spring came into being in 2003 as a response to the complexity of the early [J2EE](https://en.wikipedia.org/wiki/Java_Platform,_Enterprise_Edition) specifications.


> While some consider **Java EE** and its modern-day successor **Jakarta EE** to be in competition with Spring, they are in fact complementary. 

Spring 是和 Java EE、Jakarta EE 是相互补充的，它仔细选择集成了一些关键、有用的规范。
（集成这些规范意味着：建立兼容性和可移植性：Spring 应用可以部署到任何支持这些规范的容器中 如 Tomcat、Jetty、WildFly. 与 非 Spring 的组建无缝衔接、不需要重复定义 HTTP请求，持久化对象等方式。

这一小段的主要内容：

1. Spring 和 Jakarta EE 的关系
2. Spring 的发展与未来

## Design Philosophy

**Spring 设计理念：**

> When you learn about a framework, it’s important to know not only what it does but what principles it follows. 
>
> 在你了解一个框架的时候，不仅要看他实现完成了什么，了解它的设计原则也是非常重要的。

- Spring 允许你再开发过程中，把一些关键的技术选择或者架构决策、退出到更晚的阶段做，而不是在项目初期就一锤定音。

  比如：数据库、事务管理、部署内置Tomcat 到容器

  这是通过依赖注入 + 控制反转实现的。Spring 注重面向接口编程+ 抽象模版。这样才使得不同的实例可以通过替换（因为它们拥有同一套模版方法）
  其它相关的技术比如：自动配置、Profile(环境配置等)。它们都使得Spring 项目的运行架构可以灵活切换开发。

- 容纳多元化的观点、不固执己见，对广泛的应用需求支持不同的观点以及处理方式

- 向后兼容：控制版本差异，JDK 版本选择 以及第三方库的严格要求

- 关注 API 设计，追求精确、简洁、直观

- 严格把控代码质量

## Feedback and Contributions

Spring 的社区集中在 Stack Overflow，该社区方便开发者的诊断、调试问题。如果明确在 Spring 框架中找到了问题，那么在 Github 中提出 issue。



## Getting Started

开始创建一个 Spring 项目，推荐使用 Spring Boot-based-application。它提供了快速、默认的应用创建方式。

