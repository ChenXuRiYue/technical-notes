# Spring boot

在Spring 开发的过程中、怎么区分框架中的哪些组件使用了Spring boot? Spring boot 究竟带来了什么样的便利？



## 在项目中从哪看出使用了 Spring boot?

使用Spring boot 的体现：

1. web 服务封装

    ```java
    package com.example.demo;

    import org.springframework.boot.SpringApplication;
    import org.springframework.boot.autoconfigure.SpringBootApplication;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RequestParam;
    import org.springframework.web.bind.annotation.RestController;

    @SpringBootApplication
    @RestController  // 表示这个类是一个 REST 控制器
    public class DemoApplication {

        public static void main(String[] args) {
            SpringApplication.run(DemoApplication.class, args);
        }

        // 一个简单的 GET 接口
        @GetMapping("/hello")
        public String sayHello(@RequestParam(value = "name", defaultValue = "World") String name) {
            return "Hello, " + name + "!";
        }
    }
    ```

2. 封装了JPA

3. 主应用类
   ```java
   package com.example.demo;
   
   import org.springframework.boot.SpringApplication;
   import org.springframework.boot.autoconfigure.SpringBootApplication;
   
   @SpringBootApplication
   public class DemoApplication {
       public static void main(String[] args) {
           SpringApplication.run(DemoApplication.class, args);
       }
   }
   ```


4. 配置
   ```properties
   spring.datasource.url=jdbc:h2:mem:testdb
   spring.datasource.driverClassName=org.h2.Driver
   spring.datasource.username=sa
   spring.datasource.password=
   spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
   spring.h2.console.enabled=true
   ```

5. 依赖
   ```xml
   <dependency>
       <groupId>org.springframework.boot</groupId>
       <artifactId>spring-boot-starter-data-jpa</artifactId>
   </dependency>
   <dependency>
       <groupId>com.h2database</groupId>
       <artifactId>h2</artifactId>
       <scope>runtime</scope>
   </dependency>
   ```

6. 配置文件属性注入：
   ```java
   package com.example.demo;
   
   import org.springframework.beans.factory.annotation.Value;
   import org.springframework.boot.SpringApplication;
   import org.springframework.boot.autoconfigure.SpringBootApplication;
   import org.springframework.web.bind.annotation.GetMapping;
   import org.springframework.web.bind.annotation.RestController;
   
   @SpringBootApplication
   @RestController
   public class DemoApplication {
   
       @Value("${app.message:Default Message}")
       private String message;
   
       public static void main(String[] args) {
           SpringApplication.run(DemoApplication.class, args);
       }
   
       @GetMapping("/message")
       public String getMessage() {
           return message;
       }
   }
   ```

7. 异常处理
   ```java
   package com.example.demo;
   
   import org.springframework.boot.SpringApplication;
   import org.springframework.boot.autoconfigure.SpringBootApplication;
   import org.springframework.http.HttpStatus;
   import org.springframework.http.ResponseEntity;
   import org.springframework.web.bind.annotation.ExceptionHandler;
   import org.springframework.web.bind.annotation.GetMapping;
   import org.springframework.web.bind.annotation.RestController;
   import org.springframework.web.bind.annotation.RestControllerAdvice;
   
   @SpringBootApplication
   public class DemoApplication {
       public static void main(String[] args) {
           SpringApplication.run(DemoApplication.class, args);
       }
   }
   
   @RestController
   class TestController {
       @GetMapping("/test")
       public String test() {
           throw new IllegalArgumentException("Something went wrong!");
       }
   }
   
   @RestControllerAdvice
   class GlobalExceptionHandler {
       @ExceptionHandler(IllegalArgumentException.class)
       public ResponseEntity<String> handleIllegalArgumentException(IllegalArgumentException ex) {
           return new ResponseEntity<>("Error: " + ex.getMessage(), HttpStatus.BAD_REQUEST);
       }
   }
   ```

## 如果没有Spring boot

Spring boot 的理念是约定大于配置

1. 配置上：需要配置所有的 web 组件

   ```java
   @Configuration
   @EnableWebMvc
   public class WebConfig implements WebMvcConfigurer {
       @Bean
       public InternalResourceViewResolver viewResolver() {
           InternalResourceViewResolver resolver = new InternalResourceViewResolver();
           resolver.setPrefix("/WEB-INF/views/");
           resolver.setSuffix(".jsp");
           return resolver;
       }
   }
   ```

2. 依赖管理复杂：
   Spring Boot 的 **Starters**（如 spring-boot-starter-data-jpa）帮你管理依赖版本。例如，你加一个 JPA Starter，Hibernate、Spring Data 和数据库驱动的版本都会自动匹配。

   ```xml
   <dependency>
       <groupId>org.springframework</groupId>
       <artifactId>spring-webmvc</artifactId>
       <version>5.3.9</version>
   </dependency>
   <dependency>
       <groupId>org.hibernate</groupId>
       <artifactId>hibernate-core</artifactId>
       <version>5.4.32.Final</version>
   </dependency>
   ```

3. 部署麻烦：
   Spring Boot 的 **Starters**（如 spring-boot-starter-data-jpa）帮你管理依赖版本。例如，你加一个 JPA Starter，Hibernate、Spring Data 和数据库驱动的版本都会自动匹配。
   需要生成 WAR 文件，部署到外部 Servlet 容器（如 Tomcat、WebLogic）。需要生成 WAR 文件，部署到外部 Servlet 容器（如 Tomcat、WebLogic）。手动安装和启动服务器。

4. 生产就绪功能缺失

5. 开发体验
   @SpringBootApplication 下可以启动应用，配合自动配置，快速启动项目。

   ```java
   public class Main {
       public static void main(String[] args) {
           ApplicationContext context = new ClassPathXmlApplicationContext("spring-config.xml");
           // 手动获取 Bean 并启动应用
       }
   }
   ```

6. web 服务器相关

   会变成：
   看上去就是要配置 servlet,  web、web app 插件等。

   ```java
   // Web 配置
   @Configuration
   @EnableWebMvc
   @ComponentScan(basePackages = "com.example")
   public class WebConfig implements WebMvcConfigurer {
   }
   
   // 控制器
   @Controller
   public class HelloController {
       @RequestMapping(value = "/hello", method = RequestMethod.GET)
       @ResponseBody
       public String sayHello(@RequestParam(value = "name", defaultValue = "World") String name) {
           return "Hello, " + name + "!";
       }
   }
   
   // 初始化 Servlet
   public class ServletInitializer extends AbstractAnnotationConfigDispatcherServletInitializer {
       @Override
       protected Class<?>[] getRootConfigClasses() {
           return new Class<?>[]{WebConfig.class};
       }
       @Override
       protected Class<?>[] getServletConfigClasses() {
           return null;
       }
       @Override
       protected String[] getServletMappings() {
           return new String[]{"/"};
       }
   }
   ```

   ```xml
   <web-app>
       <servlet>
           <servlet-name>dispatcher</servlet-name>
           <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
           <init-param>
               <param-name>contextClass</param-name>
               <param-value>org.springframework.web.context.support.AnnotationConfigWebApplicationContext</param-value>
           </init-param>
           <init-param>
               <param-name>contextConfigLocation</param-name>
               <param-value>com.example.WebConfig</param-value>
           </init-param>
       </servlet>
       <servlet-mapping>
           <servlet-name>dispatcher</servlet-name>
           <url-pattern>/</url-pattern>
       </servlet-mapping>
   </web-app>
   ```

   

## 优缺点

优点： 约定大于配置，简化了 spring mvc的配置。通过起步依赖快速配置。方便对Spring 生态组件的集成。Spring boot application ，减少项目启动复杂度。

缺点：资源占用较高，提供嵌入式服务器以及大量默认的功能。过度封装，如果偏离默认配置，进一步定制化将会变得非常复杂。