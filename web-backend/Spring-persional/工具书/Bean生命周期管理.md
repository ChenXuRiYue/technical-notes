# 📝 Bean 生命周期管理

该工具书聚焦 Spring Bean 的生命周期管理。在 Bean 创建、初始化、使用和销毁的不同阶段执行自定义逻辑。

## 🔖 @PostContruct

⚙️ 

```java
// 初始化方法
@PostConstruct
public void init() {
    System.out.println("✅ Bean 初始化完成！配置: " + config);
    // 执行：连接数据库、预加载缓存、校验数据等
  
  	// 抛出运行时异常。控制程序退出
    throw new IllegalStateException("Database not available");

}
```

**限制：**

1. 方法必须是 `void`。
2. 不能是 `static`。
3. 只会执行一次（单例Bean）。
4. 推荐使用 `private` 或 `public`。

🪏 **经验**

| 场景                            | 使用                                                         | 频率 |
| :------------------------------ | ------------------------------------------------------------ | :--- |
| 从配置文件中读取配置 Bean<br /> | PostContruct 控制 Bean 的各项依赖属性<br />初始化后调用 @PostContruct 注解修饰的<br />方法。硬编码判断 Configuration Bean 是<br />否合法。 | 1️⃣    |

🔗 引用