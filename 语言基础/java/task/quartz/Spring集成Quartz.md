# Spring 中集成 Quartz

本次做一个Demo 使用Spring boot 集成 Quartz。发现了一些现象。
按照常规步骤，我们需要关注 Job、JobDetail、Trigger。

但是调度器的创建，以及其在 Spring IOC 的容器， Job 在其中以什么方式运行？

## 1. schedulerFactoryBean（）

官方文档

[SchedulerFactoryBean (Spring Framework 6.2.4 API)](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/scheduling/quartz/SchedulerFactoryBean.html)

[`FactoryBean`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/FactoryBean.html) that creates and configures a Quartz [`Scheduler`](https://www.quartz-scheduler.org/api/2.3.0/org/quartz/Scheduler.html), manages its lifecycle as part of the Spring application context, and exposes the Scheduler as bean reference for dependency injection.

Allows registration of JobDetails, Calendars and Triggers, automatically starting the scheduler on initialization and shutting it down on destruction. In scenarios that just require static registration of jobs at startup, there is no need to access the Scheduler instance itself in application code.

For dynamic registration of jobs at runtime, use a bean reference to this SchedulerFactoryBean to get direct access to the Quartz Scheduler (`org.quartz.Scheduler`). This allows you to create new jobs and triggers, and also to control and monitor the entire Scheduler.

Note that Quartz instantiates a new Job for each execution, in contrast to Timer which uses a TimerTask instance that is shared between repeated executions. Just JobDetail descriptors are shared.

When using persistent jobs, it is strongly recommended to perform all operations on the Scheduler within Spring-managed (or plain JTA) transactions. Else, database locking will not properly work and might even break. (See [`setDataSource`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/scheduling/quartz/SchedulerFactoryBean.html#setDataSource(javax.sql.DataSource)) javadoc for details.)

The preferred way to achieve transactional execution is to demarcate declarative transactions at the business facade level, which will automatically apply to Scheduler operations performed within those scopes. Alternatively, you may add transactional advice for the Scheduler itself.

Compatible with Quartz 2.1.4 and higher, as of Spring 4.1.

Spring 框架中 SchedulerFactoryBean 的功能和使用方式，它是一个 FactoryBean，用于创建和管理 Quartz Scheduler（调度器）的生命周期，并将其作为 Spring 应用上下文中的 bean 暴露出来，以便进行依赖注入。

1. **功能与生命周期管理**：
   - `SchedulerFactoryBean` 负责创建和配置 Quartz `Scheduler`，并在 Spring 应用上下文初始化时自动启动调度器，在销毁时关闭调度器。
   - 它允许注册 `JobDetails`（任务详情）、`Calendars`（日历）和 `Triggers`（触发器）。

2. **使用场景**：
   - **静态任务注册**：如果只需在启动时注册固定的任务，无需在应用代码中直接访问 `Scheduler` 实例。
   - **动态任务注册**：如果需要在运行时动态创建任务或触发器，可以通过 bean 引用获取 `Scheduler` 实例，直接操作 Quartz 调度器。

3. **Quartz 的特性**：
   - Quartz 为每次任务执行创建一个新的 `Job` 实例，而不是像 Java 的 `Timer` 那样重复使用同一个任务实例。共享的只有 `JobDetail` 描述符。

4. **持久化任务的注意事项**：
   - 使用持久化任务时，强烈建议在 Spring 管理的事务（或 JTA 事务）中操作 `Scheduler`，否则数据库锁机制可能无法正常工作，甚至出现问题。
   - 可通过 `setDataSource` 方法配置数据源以支持持久化。

5. **事务支持**：
   - 推荐在业务 facade 层使用声明式事务，这样调度器操作会自动包含在事务范围内。
   - 或者，可以为 `Scheduler` 本身添加事务建议。

6. **兼容性**：
   - 从 Spring 4.1 开始，`SchedulerFactoryBean` 兼容 Quartz 2.1.4 及以上版本。

总结来说，`SchedulerFactoryBean` 提供了一种方便的方式，将 Quartz 调度器集成到 Spring 中，支持静态和动态任务注册，并强调在持久化场景下使用事务以确保操作的可靠性和一致性。

这段代码是由 Spring 官方提供的用来在 Spring 中集成quartz



### Schedule 的创建时机

在 Spring 的 IoC 流程中，`SchedulerFactoryBean` 创建 Quartz `Scheduler` 的具体时机与 Spring 的 Bean 生命周期和 `FactoryBean` 的特性密切相关。下面我结合专业概念和通俗语言，详细解释 `Scheduler` 是什么时候创建的。

---

### 专业解答：`Scheduler` 的创建时机
`SchedulerFactoryBean` 是一个 `FactoryBean`，它的核心职责是通过 `getObject()` 方法返回一个 `Scheduler` 实例。Spring IoC 容器会在以下时机触发 `Scheduler` 的创建：

1. **Bean 实例化阶段**：
   - Spring IoC 容器启动时，会扫描所有定义的 Bean（包括 `SchedulerFactoryBean`）。
   - 当容器处理到 `SchedulerFactoryBean` 的定义时，会先实例化 `SchedulerFactoryBean` 本身（调用其构造方法）。

2. **依赖注入和属性设置阶段**：
   - 实例化后，Spring 会通过 setter 方法（如 `setDataSource`、`setJobDetails`、`setTriggers`）注入配置属性。这是 `SchedulerFactoryBean` 准备创建 `Scheduler` 的“原材料”。

3. **初始化阶段（`afterPropertiesSet`）**：
   - 因为 `SchedulerFactoryBean` 实现了 `InitializingBean` 接口，Spring 在属性设置完成后会调用其 `afterPropertiesSet()` 方法。
   - 在这个方法中，`SchedulerFactoryBean` 会真正创建 Quartz `Scheduler` 实例。它会：
     - 使用 `SchedulerFactory`（Quartz 的工厂类）创建 `Scheduler`。
     - 根据配置（如数据源、线程池、任务等）初始化 `Scheduler`。
     - 如果配置了 `autoStartup=true`（默认值），还会调用 `scheduler.start()` 启动调度器。

4. **暴露给容器（`getObject` 调用）**：
   - `SchedulerFactoryBean` 作为 `FactoryBean`，Spring 会调用其 `getObject()` 方法获取最终的 Bean 对象（即 `Scheduler`）。
   - 这个调用通常发生在：
     - 容器初始化时，如果其他 Bean 依赖 `Scheduler`（比如通过 `@Autowired` 注入）。
     - 或第一次显式访问 `Scheduler` Bean 时（延迟加载的情况）。
   - 在 `getObject()` 中，`SchedulerFactoryBean` 返回之前创建好的 `Scheduler` 实例。

**总结**：`Scheduler` 的创建发生在 `SchedulerFactoryBean` 的 `afterPropertiesSet()` 方法中，通常是 Spring IoC 容器初始化阶段（Bean 的 `post-construct` 阶段）。但它被暴露给其他代码使用（通过 `getObject()`）可能稍晚，取决于依赖关系和加载策略。

---

### 代码视角：实际创建点
以下是 `SchedulerFactoryBean` 的简化逻辑，帮你直观理解：
```java
public class SchedulerFactoryBean implements FactoryBean<Scheduler>, InitializingBean, DisposableBean {
    private DataSource dataSource;
    private List<JobDetail> jobDetails;
    private List<Trigger> triggers;

    private Scheduler scheduler;

    @Override
    public void afterPropertiesSet() throws Exception {
        // 创建 Scheduler
        SchedulerFactory factory = new StdSchedulerFactory();
        scheduler = factory.getScheduler();

        // 配置 Scheduler（比如数据源、任务等）
        if (dataSource != null) {
            // 设置数据库支持
        }
        if (jobDetails != null) {
            for (JobDetail job : jobDetails) {
                scheduler.scheduleJob(job, /* trigger */);
            }
        }

        // 默认启动
        if (isAutoStartup()) {
            scheduler.start();
        }
    }

    @Override
    public Scheduler getObject() {
        return scheduler; // 返回创建好的 Scheduler
    }

    @Override
    public void destroy() throws Exception {
        if (scheduler != null) {
            scheduler.shutdown(); // 销毁时关闭
        }
    }
}
```
- **`afterPropertiesSet()`**：`Scheduler` 在这里被创建和配置。
- **`getObject()`**：返回给 IoC 容器或依赖它的代码。

---

### 最终答案
`Scheduler` 是在 Spring IoC 容器初始化 `SchedulerFactoryBean` 时，通过 `afterPropertiesSet()` 方法创建的。具体时间点是容器启动后的 Bean 初始化阶段（通常在应用启动时完成）。如果配置了自动启动，它还会立刻开始调度任务。



## 2. spring-boot-starter-quartz

使用 `spring-boot-starter-quartz` 意味着你将 Spring Boot 与 Quartz 调度器集成到你的项目中，利用 Spring Boot 提供的便捷性和自动化配置来简化 Quartz 的使用。让我用通俗易懂的语言结合专业概念，解释它的含义和作用。

---

### 通俗解释：相当于请了个“智能管家”
假设你开了一家公司，需要安排一些定时任务（比如每天早上发邮件、每周统计数据）。Quartz 是个很强大的“任务调度员”，但自己配置它有点麻烦，就像你得亲自告诉它每一步怎么做。而 `spring-boot-starter-quartz` 就像 Spring Boot 给你派来的一个“智能管家”，它会自动帮你把 Quartz 设置好，让你只需要说“做什么、什么时候做”，剩下的细节它自己搞定。

换句话说，这个 starter 是 Spring Boot 的一个“开箱即用”工具包，帮你快速把 Quartz 调度功能嵌入到 Spring Boot 项目中，省去手动配置的麻烦，还能跟 Spring 的生态（如 IoC 容器、依赖注入）无缝对接。

---

### 专业含义：依赖和自动配置
`spring-boot-starter-quartz` 是 Spring Boot 提供的一个 Maven/Gradle 依赖，具体来说：

1. **依赖引入**：
   - 在 `pom.xml`（Maven）或 `build.gradle`（Gradle）中添加：
     ```xml
     <dependency>
         <groupId>org.springframework.boot</groupId>
         <artifactId>spring-boot-starter-quartz</artifactId>
     </dependency>
     ```
   - 这会自动拉取 Quartz 的核心库（`quartz`）和 Spring 对 Quartz 的集成支持（比如 `SchedulerFactoryBean`）。

2. **自动配置**：
   - Spring Boot 的核心特性之一是“约定优于配置”。当你引入这个 starter 后，Spring Boot 会检测到 Quartz 存在，然后自动创建一个 `Scheduler`（Quartz 的调度器）实例，并通过 `SchedulerFactoryBean` 进行配置。
   - 默认情况下，它会：
     - 使用内存存储（`RAMJobStore`）来保存任务和触发器。
     - 把 `Scheduler` 注册为 Spring 的 Bean，供你的代码通过依赖注入使用（比如 `@Autowired Scheduler scheduler`）。

3. **简化开发**：
   - 你可以直接定义 Quartz 的 `JobDetail`（任务详情）和 `Trigger`（触发器）作为 Spring Bean，Spring Boot 会自动将它们关联到 `Scheduler` 上。
   - 比如：
     ```java
     @Bean
     public JobDetail myJobDetail() {
         return JobBuilder.newJob(MyJob.class).build();
     }
     
     @Bean
     public Trigger myTrigger(JobDetail myJobDetail) {
         return TriggerBuilder.newTrigger()
             .forJob(myJobDetail)
             .withSchedule(SimpleScheduleBuilder.repeatSecondlyForever(10))
             .build();
     }
     ```
   - Spring Boot 会确保这些任务在应用启动时被调度器加载并执行。

---

### 意味着什么？
具体到你的项目，使用 `spring-boot-starter-quartz` 意味着以下几点：

1. **省时省力**：
   - 你不需要手动创建和管理 Quartz 的 `SchedulerFactory` 或 `Scheduler`，Spring Boot 自动完成这些底层工作。
   - 比如，不用写复杂的初始化代码，只需配置几个属性或定义几个 Bean。

2. **默认内存调度**：
   - 默认情况下，任务和触发器信息存储在内存中（`RAMJobStore`）。这意味着应用重启后，之前的调度信息会丢失，适合开发测试或简单场景。
   - 如果需要持久化（比如存到数据库），你得额外配置 `spring.quartz.job-store-type=jdbc` 并提供数据源。

3. **Spring 生态集成**：
   - 你的 Quartz 任务（`Job`）可以像普通 Spring Bean 一样，通过 `@Autowired` 注入其他服务（比如数据库服务、邮件服务）。
   - 比如：
     ```java
     public class MyJob extends QuartzJobBean {
         @Autowired
         private MyService myService;
     
         @Override
         protected void executeInternal(JobExecutionContext context) {
             myService.doSomething();
         }
     }
     ```

4. **灵活配置**：
   - 你可以通过 `application.properties` 或 `application.yml` 调整 Quartz 的行为，比如：
     ```properties
     spring.quartz.job-store-type=jdbc  # 使用数据库存储
     spring.quartz.properties.org.quartz.threadPool.threadCount=10  # 设置线程池大小
     ```
   - 这让你可以轻松定制调度器的线程数、存储方式等。

5. **动态调度支持**：
   - 你可以用代码动态添加任务，比如通过 REST API 调用 `scheduler.scheduleJob(jobDetail, trigger)`，非常适合需要运行时调整任务的应用。

---

### 使用它的场景
- **简单定时任务**：比如每隔 10 秒打印日志、每天清理临时文件。
- **复杂调度需求**：比如基于 Cron 表达式的复杂时间表（“每周一早上 9 点执行”）。
- **持久化任务**：需要任务在应用重启后还能继续执行（需要配置 JDBC 存储）。

---

### 注意事项
1. **对比 Spring 自带调度**：
   - Spring Boot 自带 `@Scheduled` 注解也能做定时任务，但它更简单，适合固定间隔的任务。
   - `spring-boot-starter-quartz` 更强大，支持持久化、集群、动态调整，适合复杂调度场景。

2. **内存 vs 数据库**：
   - 默认内存存储简单但不持久，重启就丢数据。如果需要持久化，得配置数据库并初始化 Quartz 表（SQL 脚本在 Quartz 源码里）。

3. **依赖注入的 Job**：
   - 如果你的 `Job` 需要 Spring Bean，必须用 `QuartzJobBean`（Spring 提供的包装类），否则 Quartz 默认不会识别 Spring 的依赖注入。

---

### 总结
使用 `spring-boot-starter-quartz` 意味着你选择了一个便捷的方式，把 Quartz 的强大调度能力融入 Spring Boot 项目。它通过自动配置和 Spring 的 IoC 机制，让你专注于业务逻辑，而不是底层的调度器管理。简单来说，就是“花最少的力气，干最复杂的事”，特别适合需要定时任务或动态调度的应用！



## 3. 实践过程中带来的细节问题

在写demo 时。自己手动重新配置了一遍 Scheduler Factor bean，后续没做其它调整。

1. 必须手动的将Job、Trigger、JobDetail 手动添加到容器中。
2. Trigger、JobDetail 不能够自动注入 RabbitTemplate.



是因为自己配置之后，Bean 没有交由容器管理，其成员也不能由组件自动注入。此时 Job 是由 Schedule 调度器创建的。



AI：解答如下：

---

### 专业解答：Spring Boot 的自动配置与 Bean 覆盖机制

#### 1. 默认行为（自动配置）
当你引入 `spring-boot-starter-quartz` 时，Spring Boot 的自动配置（`QuartzAutoConfiguration` 类）会：
- 创建一个 `SchedulerFactoryBean` 实例。
- 配置默认属性（比如内存存储 `RAMJobStore`、线程池等）。
- 将生成的 `Scheduler` 注册为一个 Bean，供依赖注入使用。
- 默认 Bean 的名字通常是 `schedulerFactoryBean`（由方法名或类名推导）。

#### 2. 你的手动配置
你的代码：
```java
@Bean
public SchedulerFactoryBean schedulerFactoryBean() {
    SchedulerFactoryBean factory = new SchedulerFactoryBean();
    factory.setStartupDelay(2); // 延迟2秒启动
    factory.setAutoStartup(true); // 自动启动
    factory.setJobDetails(taskToMqJobDetail());
    factory.setTriggers(taskToMqTrigger());
    return factory;
}
```
- 你显式定义了一个 `SchedulerFactoryBean` 的 Bean。
- Bean 的名字默认是方法名 `schedulerFactoryBean`。
- 这个 Bean 会生成一个 `Scheduler`，并按照你的配置（延迟启动、手动指定的任务和触发器）工作。

#### 3. Bean 覆盖规则
Spring IoC 容器遵循以下规则：
- **同名 Bean 覆盖**：如果容器中已经有一个同名的 Bean（比如 `schedulerFactoryBean`），后定义的 Bean 会覆盖前面的。
- **自动配置的优先级较低**：Spring Boot 的自动配置 Bean 通常被设计为“条件性”的（用 `@ConditionalOnMissingBean` 注解），意思是如果用户没有定义同类型的 Bean，它才会生效。一旦你手动定义了一个 `SchedulerFactoryBean`，自动配置的那个就会被跳过。

在你的例子中：
- Spring Boot 的 `QuartzAutoConfiguration` 检查到你已经定义了一个 `SchedulerFactoryBean`（名字相同或类型匹配）。
- 自动配置会退让，你的 `schedulerFactoryBean` 会成为容器中唯一的 `SchedulerFactoryBean`，它生成的 `Scheduler` 也会覆盖默认的。

#### 4. 结果
- **默认 Bean 被覆盖**：Spring Boot 自动配置的 `SchedulerFactoryBean` 和它生成的 `Scheduler` 不会生效。
- **你的配置生效**：容器里只会有你手动配置的 `SchedulerFactoryBean`，调度器会按照你的设置运行（延迟 2 秒启动，只调度 `taskToMqJobDetail` 和 `taskToMqTrigger`）。

---

### 会出现什么问题？
手动配置覆盖默认 Bean 本身不会直接“出错”，但可能会带来一些影响或需要注意的地方：

1. **丢失自动配置的特性**：
   - Spring Boot 默认会根据 `application.properties`（如 `spring.quartz.*`）自动设置一些属性（比如线程池大小、存储类型）。你手动配置后，这些属性不会自动应用，除非你显式设置。
   - 比如，默认是 `RAMJobStore`，如果你想要 JDBC 存储，得自己调用 `factory.setDataSource(dataSource)`。

2. **任务范围受限**：
   - 默认配置会自动加载所有标注 `@Bean` 的 `JobDetail` 和 `Trigger`，而你手动配置只指定了 `taskToMqJobDetail` 和 `taskToMqTrigger`。其他任务（如果有）不会被调度，除非你手动加到 `setJobDetails` 和 `setTriggers` 里。

3. **配置冲突风险**：
   - 如果你在 `application.properties` 里还配置了 `spring.quartz` 属性（比如 `spring.quartz.job-store-type=jdbc`），但代码里没对应设置（比如没设置 `dataSource`），可能会导致行为不一致。

4. **动态调度问题**：
   - 如果你本来想依赖默认 `Scheduler` 的动态调度功能（比如通过注入 `Scheduler` 添加任务），但手动配置覆盖后，只有你指定的静态任务会生效，后续动态添加的任务需要额外处理。

---

### 验证覆盖的简单实验
你可以试试加个日志，看看哪个 `Scheduler` 在运行：
```java
@Bean
public SchedulerFactoryBean schedulerFactoryBean() {
    SchedulerFactoryBean factory = new SchedulerFactoryBean();
    factory.setStartupDelay(2);
    factory.setAutoStartup(true);
    factory.setJobDetails(taskToMqJobDetail());
    factory.setTriggers(taskToMqTrigger());
    System.out.println("Using my custom SchedulerFactoryBean");
    return factory;
}
```
启动应用后，如果只看到你的日志输出，说明默认的被覆盖了。

---

### 如何避免问题？
1. **保留自动配置，扩展它**：
   - 注入默认的 `Scheduler` 而不是覆盖：
     ```java
     @Autowired
     private Scheduler scheduler;
     
     @PostConstruct
     public void init() throws SchedulerException {
         scheduler.scheduleJob(taskToMqJobDetail(), taskToMqTrigger());
     }
     ```
   - 这样保留 Spring Boot 的默认配置，只动态添加任务。

2. **显式命名避免冲突**：
   - 如果你想同时用默认和自定义的 `Scheduler`，给你的 Bean 取个不同的名字：
     ```java
     @Bean(name = "myCustomSchedulerFactoryBean")
     public SchedulerFactoryBean schedulerFactoryBean() {
         // 你的配置
     }
     ```
   - 这样默认的 `schedulerFactoryBean` 不会被覆盖。

3. **完整配置**：
   
   - 如果坚持手动配置，确保把需要的属性都设置好（比如 `setDataSource`、`setQuartzProperties`），避免遗漏。

---

### 最终答案
- **会覆盖吗？** 是的，你的 `SchedulerFactoryBean` 会覆盖 Spring Boot 自动配置的默认 `SchedulerFactoryBean`，因为它们名字相同（`schedulerFactoryBean`），Spring 以你手动定义的为准。
- **会有问题吗？** 不会直接报错，但可能丢失默认配置的便利性（比如属性自动加载），而且只调度你指定的任务，其他任务需要手动添加。

建议根据需求选择：如果只是加几个任务，注入默认 `Scheduler` 动态调度更简单；如果需要完全掌控，手动配置没问题，但要确保配置完整。

