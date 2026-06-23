# 📌 Gateway 网关

基础谈资：和新人聊网关时，最该侃侃而谈的内容

## 📄 网关是什么

### 定义

一句话：**网关是系统的统一入口，所有外部请求先经过它，再转发到内部服务。**

类比理解：网关就像一栋大楼的前台。所有访客（请求）先到前台登记，前台负责判断你该去几楼（路由）、验证你的身份（鉴权）、限制同时进入的人数（限流），然后指引你过去。

在技术上，网关是一个**反向代理**，部署在所有后端服务之前，客户端只和网关打交道，不知道后端有多少个服务、各自在哪。

> 网关 = 微服务的「门卫」。它不生产业务逻辑，但它决定了谁能进、进到哪、进多快。

### 技术演进

```
单体时代         SOA 时代           微服务时代          云原生时代
(2000s)         (2005+)            (2014+)            (2018+)
   │               │                  │                  │
  Nginx        ESB（企业             API Gateway       Service Mesh
 反向代理       服务总线）         (Zuul / Gateway)    (Envoy / Sidecar)
   │               │                  │                  │
 纯转发        重量级、集中式       轻量级、面向        流量下沉到
 无业务逻辑    XML 配置地狱         HTTP API 治理       基础设施层
```

**关键节点：**

- **Nginx（2004）**：最早的反向代理方案，能做转发和负载均衡，但没有业务治理能力（鉴权、限流要靠写 Lua 脚本）
- **ESB（~2005）**：SOA 时代的"重量级网关"，能做协议转换、消息路由，但配置复杂、性能差、与业务耦合重
- **Netflix Zuul 1.x（2013）**：第一个流行的微服务网关，基于 Servlet 阻塞模型，Spring Cloud 生态的默认选择
- **Spring Cloud Gateway（2017）**：Spring 官方出品，基于 WebFlux 响应式编程，解决了 Zuul 1.x 的性能瓶颈
- **Kong / APISIX（2015+）**：基于 Nginx + Lua 的高性能网关，更偏向基础设施层
- **Envoy + Service Mesh（2017+）**：流量治理下沉到 sidecar proxy，网关职责进一步模糊化

**云原生时代补充分明：**

- **Envoy**：本质是"更现代的 Nginx"，由 Lyft 开发，后捐给 CNCF。比 Nginx 更擅长微服务间通信（动态服务发现、gRPC 原生支持、丰富可观测性指标）
- **Sidecar（边车模式）**：不是产品，是部署模式 — 给每个服务实例旁部署一个 Envoy，所有进出流量先经过它
- **Service Mesh（服务网格）**：把所有 Sidecar Envoy 统一管理。典型实现 **Istio** = 数据平面（一堆 Envoy 转发流量）+ 控制平面（统一配置路由、安全、限流策略）

**Service Mesh 和传统网关不是替代关系，而是分层：**

| | 传统网关（Spring Cloud Gateway） | Service Mesh（Istio + Envoy） |
|---|---|---|
| **流量方向** | 北向：外部 → 集群入口 | 东西向：服务 ↔ 服务 |
| **复杂度** | 低，一个 Spring Boot 应用搞定 | 高，需要 K8s 基础 + Istio 运维 |
| **适用场景** | 绝大多数业务足够了 | 几百上千个微服务、多集群场景 |

> 现实：大多数公司用 Spring Cloud Gateway 就够了。Service Mesh 更多是大厂在用，解决"几百个服务互相调用时的治理问题"。

## 📄 解决什么问题

没有网关时，微服务架构面临几个痛点：

| 痛点 | 说明 |
|------|------|
| **客户端要感知后端拓扑** | 前端/移动端需要知道每个服务的地址，耦合严重 |
| **横切逻辑重复** | 鉴权、日志、限流等逻辑每个服务都要写一遍 |
| **跨域问题** | 多个服务各跑各的端口，前端请求跨域满天飞 |
| **安全暴露面大** | 每个服务都可能被直接访问，攻击面大 |

网关统一收口后：客户端只认一个地址，横切逻辑在网关层集中处理，后端服务不直接暴露。

## 📄 网关的核心能力

### 路由（Route）

最基础的能力。根据请求的路径、Header、Query 参数等条件，将请求转发到对应的后端服务。

```
/api/user/**  → user-service
/api/order/** → order-service
```

### 鉴权（Authentication & Authorization）

统一的身份验证入口。常见的鉴权方式：

- **JWT 校验**：网关解析 Token，验证签名和过期时间，通过后把用户信息写入 Header 传给下游
- **OAuth2 集成**：网关作为 OAuth2 资源服务器，校验 access_token
- **白名单放行**：登录、注册等接口不需要 Token，通过路由配置直接放行

### 限流（Rate Limiting）

防止某个客户端或接口把后端服务打挂。常见策略：

| 策略 | 说明 |
|------|------|
| **令牌桶** | 按固定速率放令牌，请求拿不到令牌就被拒 |
| **滑动窗口** | 统计最近 N 秒内的请求数，超限拒绝 |
| **按维度限流** | 按 IP、用户 ID、接口路径分别限流 |

Spring Cloud Gateway 内置了 `RequestRateLimiter` 过滤器，底层用 Redis + 令牌桶实现。

### 熔断（Circuit Breaker）

当下游服务出故障时，快速失败而不是让请求一直等着超时。防止一个服务挂掉拖垮整个链路（雪崩效应）。

三种状态：**关闭**（正常放行）→ **打开**（直接拒绝，不调用下游）→ **半开**（放少量请求试探，恢复了就关闭）。

Spring Cloud Gateway 集成 Resilience4j 实现熔断。

### 日志与监控

网关是所有流量的入口，天然适合做统一的日志采集和监控埋点：

- 请求耗时、状态码、来源 IP
- 链路追踪 ID（TraceId）注入，方便跨服务排查
- 对接 Prometheus / Grafana 做可视化

### 其他能力

- **跨域处理（CORS）**：在网关层统一配置，下游服务不用各自处理
- **负载均衡**：同一服务多个实例时，按策略（轮询、权重、最少连接）分发请求
- **请求/响应改写**：修改 Header、Body、路径前缀（Path Rewrite）
- **灰度发布**：按比例或按条件（Header、Cookie）将流量导向不同版本的服务

## 📄 链路追踪

一个请求从进网关到后端服务经历了什么

### 🔖 Gateway Filter 链路

Spring Cloud Gateway 的核心是 **Filter Chain（过滤器链）**。请求进入后按顺序经过一系列 Filter，每个 Filter 可以在"调用前"或"调用后"执行逻辑。

```
客户端请求
    │
    ▼
┌─────────────────────────────┐
│  Gateway Handler Mapping    │  ← 根据 Predicate 匹配路由
│  (Route Predicate 匹配)     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Pre Filter（前置过滤器）    │  ← 鉴权、限流、日志、Header 注入
│  - AuthenticationFilter     │
│  - RateLimiterFilter        │
│  - RequestLoggingFilter     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Netty HttpClient           │  ← 实际转发请求到下游服务
│  (负载均衡 → 服务实例)       │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Post Filter（后置过滤器）   │  ← 响应改写、日志、指标采集
│  - ResponseLoggingFilter    │
│  - SetStatusFilter          │
└─────────────┬───────────────┘
              │
              ▼
         返回客户端
```

**两类 Filter：**

| 类型 | 执行时机 | 典型用途 |
|------|---------|---------|
| **Global Filter** | 对所有路由生效 | 鉴权、日志、链路追踪 ID 注入 |
| **GatewayFilter** | 仅对指定路由生效 | 某个接口的限流、路径改写 |

**执行顺序：** 通过 `getOrder()` 方法决定，数字越小越先执行。

### 🔖 下游服务调用链路

网关转发请求到下游服务时，涉及两个关键机制：

**负载均衡（LoadBalancer）：**

Gateway 通过 `LoadBalancerClient` 选择目标服务实例。默认集成 Spring Cloud LoadBalancer（早期用 Ribbon）：

```
lb://user-service/api/user/1
  │            │
  │            └── 服务名（从注册中心获取实例列表）
  └── lb 协议表示走负载均衡
```

常见策略：轮询（Round Robin）、随机、权重。

**服务发现（Service Discovery）：**

Gateway 从注册中心（Nacos / Eureka / Consul）拉取服务实例列表，实现动态路由。不需要硬编码 IP 地址：

```
Gateway 启动 → 注册中心（Nacos）
                    │
                    ├── user-service: [192.168.1.10:8080, 192.168.1.11:8080]
                    ├── order-service: [192.168.1.20:8081]
                    └── ...
```

服务实例上下线时，注册中心通知 Gateway 更新实例列表，实现无感知扩缩容。

## 📄 Spring Cloud Gateway 语法体系

### 路由配置（YAML）

路由是 Gateway 最核心的配置单元。每条路由由四部分组成：**ID、URI、Predicates、Filters**。

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service-route          # 路由唯一标识
          uri: lb://user-service           # 目标服务（lb:// 走负载均衡）
          predicates:                      # 匹配条件（全部满足才命中）
            - Path=/api/user/**
            - Method=GET,POST
          filters:                         # 过滤器（对匹配的请求做处理）
            - StripPrefix=1                # 去掉路径第一段 /api
```

**路由匹配逻辑：** 多个 Predicate 之间是 **AND** 关系，全部满足才命中该路由。

### Predicate（断言）

决定"什么样的请求走这条路由"。常用内置 Predicate：

| Predicate | 语法 | 说明 |
|-----------|------|------|
| **Path** | `Path=/api/user/**` | 路径匹配，支持 Ant 风格 |
| **Method** | `Method=GET,POST` | HTTP 方法 |
| **Header** | `Header=X-Token, \d+` | 请求头存在且值匹配正则 |
| **Query** | `Query=name, jack.` | 查询参数存在且值匹配正则 |
| **After** | `After=2024-01-01T00:00:00+08:00` | 在指定时间之后生效 |
| **Before** | `Before=2025-01-01T00:00:00+08:00` | 在指定时间之前生效 |
| **Between** | `Between=时间1, 时间2` | 在两个时间之间生效 |
| **Host** | `Host=**.example.com` | 域名匹配 |
| **Cookie** | `Cookie=sessionId, .+` | Cookie 存在且值匹配 |
| **RemoteAddr** | `RemoteAddr=192.168.1.0/24` | 来源 IP 段 |

**组合使用示例：**

```yaml
predicates:
  - Path=/api/order/**
  - Method=POST
  - Header=Authorization, Bearer .*
# 含义：POST /api/order/** 且带 Authorization 头才走这条路由
```

### Filter（过滤器）

过滤器是 Gateway 的扩展核心，分为**内置 Filter** 和**自定义 Filter**。

**常用内置 Filter：**

| Filter | 语法 | 说明 |
|--------|------|------|
| **AddRequestHeader** | `AddRequestHeader=X-UserId, 123` | 给下游请求加 Header |
| **AddResponseHeader** | `AddResponseHeader=X-Gateway, true` | 给响应加 Header |
| **StripPrefix** | `StripPrefix=1` | 去掉路径前 N 段（`/api/user/1` → `/user/1`） |
| **PrefixPath** | `PrefixPath=/v2` | 给路径加前缀 |
| **RewritePath** | `RewritePath=/api/(?<segment>.*), /$\{segment}` | 正则重写路径 |
| **SetPath** | `SetPath=/${segment}` | 设置路径（配合 Predicate 变量） |
| **RequestRateLimiter** | 见下方限流配置 | 限流 |
| **Retry** | `Retry=3, 500, GET` | 重试（次数、间隔、方法） |
| **CircuitBreaker** | `CircuitBreaker=myCircuitBreaker` | 熔断 |

**限流 Filter 配置示例：**

```yaml
filters:
  - name: RequestRateLimiter
    args:
      redis-rate-limiter.replenishRate: 10    # 每秒放 10 个令牌
      redis-rate-limiter.burstCapacity: 20    # 令牌桶容量 20
      key-resolver: "#{@userKeyResolver}"     # 限流维度（按用户/IP/接口）
```

```java
// 限流 Key 解析器（按 IP 限流）
@Bean
public KeyResolver userKeyResolver() {
    return exchange -> Mono.just(
        exchange.getRequest().getRemoteAddress().getAddress().getHostAddress()
    );
}
```

### 自定义 Filter

**GlobalFilter（全局过滤器）** — 对所有路由生效：

```java
@Component
@Order(-1)  // 值越小越先执行，-1 保证在大多数 Filter 之前
public class AuthGlobalFilter implements GlobalFilter {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");

        // 前置逻辑：鉴权
        if (token == null || !token.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        // 放行，继续执行后续 Filter
        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            // 后置逻辑：响应处理（如果需要）
        }));
    }
}
```

**GatewayFilterFactory（路由过滤器工厂）** — 仅对配置了该 Filter 的路由生效：

```java
@Component
public class LogGatewayFilterFactory extends AbstractGatewayFilterFactory<LogGatewayFilterFactory.Config> {

    public LogGatewayFilterFactory() {
        super(Config.class);
    }

    @Override
    public GatewayFilter apply(Config config) {
        return (exchange, chain) -> {
            if (config.isPreLog()) {
                log.info("请求进入：{}", exchange.getRequest().getPath());
            }
            return chain.filter(exchange).then(Mono.fromRunnable(() -> {
                if (config.isPostLog()) {
                    log.info("响应状态：{}", exchange.getResponse().getStatusCode());
                }
            }));
        };
    }

    @Data
    public static class Config {
        private boolean preLog = true;
        private boolean postLog = true;
    }
}
```

```yaml
# YAML 中使用自定义 Filter
filters:
  - name=Log
    args:
      preLog: true
      postLog: false
```

### Filter 执行顺序

```
请求进入
  │
  ▼
GlobalFilter（按 @Order 排序，值小先执行）
  │
  ▼
GatewayFilter（按路由配置中的顺序）
  │
  ▼
转发到下游
  │
  ▼
GatewayFilter（反向执行后置逻辑）
  │
  ▼
GlobalFilter（反向执行后置逻辑）
  │
  ▼
返回客户端
```

> Filter 的 `chain.filter(exchange)` 是分界线：之前的代码是"前置"，之后的 `.then()` 是"后置"。

### Java DSL 路由配置

除了 YAML，也可以用 Java 代码配置路由：

```java
@Configuration
public class RouteConfig {

    @Bean
    public RouteLocator customRoutes(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-route", r -> r
                .path("/api/user/**")
                .and()
                .method(HttpMethod.GET)
                .filters(f -> f
                    .stripPrefix(1)
                    .addRequestHeader("X-From", "gateway")
                )
                .uri("lb://user-service"))
            .build();
    }
}
```

**YAML vs Java DSL 选择：** 简单路由用 YAML（配置清晰、热更新方便）；复杂路由逻辑（动态路由、条件组装）用 Java DSL。

| 维度 | Spring Cloud Gateway | Zuul 1.x | Nginx | Kong | APISIX |
|------|---------------------|----------|-------|------|--------|
| **语言** | Java | Java | C | Lua + Nginx | Lua + Nginx |
| **模型** | 响应式（WebFlux） | Servlet 阻塞 | 事件驱动 | 事件驱动 | 事件驱动 |
| **性能** | 中高 | 中 | 极高 | 高 | 高 |
| **配置方式** | Java 代码 / YAML | Java 代码 | conf 文件 | Admin API + 插件 | Admin API + 插件 |
| **服务发现** | 原生集成 Nacos/Eureka | 原生集成 | 需手动配置 | 需插件 | 内置 |
| **扩展方式** | 写 Java Filter | 写 Java Filter | 写 Lua 脚本 | 插件市场 | 插件市场 + 自定义 |
| **适用场景** | Spring Cloud 体系 | 已淘汰 | 静态资源 / 简单代理 | 多语言 / 独立网关 | 多语言 / 高性能 |
| **学习成本** | 低（Java 开发者） | 低 | 中 | 中 | 中 |

**选型建议：**

- **Spring Cloud 体系** → Spring Cloud Gateway，和项目无缝集成，Java 开发者零学习成本
- **需要极高性能 / 纯转发** → Nginx，但业务逻辑要写 Lua，维护成本高
- **多语言 / 非 Java 体系** → Kong 或 APISIX，通过插件实现鉴权限流，不绑定语言
- **APISIX vs Kong**：APISIX 用 etcd 存储配置（热更新），Kong 用 PostgreSQL（需重启）。APISIX 性能略优，国内社区更活跃

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

对发散的自由捕捉、精确化

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

记录回顾、使用文档时，遇到的困惑。风格要求：Q&A 并列排布，每个问题直击要害，用分隔线区分，语言简洁朴素。适当情况下可增加简单推导或推理过程，但不堆砌。

```markdown
**Q1：一句话描述困惑？**

结论或方案，不绕弯。

---

**Q2：一句话描述困惑？**

简要推导过程 → 结论。
```

## 🗺️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思

## ⚙️ prompt

探究该文档模块过程中的 prompt 记录

## 调研

AI 创建笔记时，调研结果追加到此处。仅记录相关经验和信息，由用户自行整理。
