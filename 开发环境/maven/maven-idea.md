

# maven Idea

> IDEA 集成了丰富的 Maven UI 操作。各个 UI 动作对应了什么 Maven 过程？



## Deploy

1. 对 Maven 下的 Spring 在终端使用命令 `mvn deploy` 不成功。Idea UI 中点击 deploye 就。两个操作的差别是什么？


**错误还原：**

- 终端执行 `mvn deploy`
- mvn 推送报错，显示找不到参数符号
  - lombok @Data 生成的 getter、seeter 函数
  - lombok @AllArgsConstructor 生成的全参构造函数

**分析：**

Lombook 属于代码生成器型注解，编译时处理器。Maven 编译项目时，需要通过读取配置获取处理器

| 维度        | 终端执行 `mvn deploy`                                        | IDEA UI 点击 `deploy`                                        |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 执行者      | 原生 Maven (安装在系统上的 mvn 命令)                         | IDEA 内置构建系统 (通常委托给 IDEA 自己的编译器)             |
| Lombok 处理 | 严格模式：必须显式配置 `<annotationProcessorPaths>` 才能识别处理器。 | 智能模式：IDEA 会自动扫描类路径，发现 Lombok 依赖后自动激活注解处理。 |
| 失败原因    | Maven 找不到处理器指令，不执行代码生成，直接编译原代码，导致找不到符号。 | IDEA 先悄悄生成了代码，然后再编译，所以一切看起来正常。      |

**解决：**

- 终端使用了 JDK 14 。降级到 JDK 8 ，和 Lombook 兼容

JDK 14+ 的“变革”：从 JDK 9 开始引入模块化（Project Jigsaw），到 JDK 14、17，Java 官方为了安全，**封锁了 Lombok 赖以生存的某些内部 API**。

TODO：水有点深。日后再深究

## 侧边栏新项目无 Maven 插件按钮

**错误还原：**

- IDEA 打开一个项目（新引入，或者已有项目）
- 侧边栏没有出现 Maven 相关的插件按钮（如 Maven 工具窗口、生命周期按钮等）

**分析：**

IDEA 没有自动识别该项目为 Maven 项目。常见于从外部导入或手动打开的项目，IDEA 未触发 POM 文件的自动解析。

**解决：**

1. 右键 `pom.xml` → `Add as Maven Project`（让 IDEA 识别项目为 Maven 项目）
2. 识别后仍未生效：侧边栏 Maven 面板中点击刷新按钮 reimport
3. 仍不生效：`File → Project Structure → Modules` → `+` → `Import Module` → 选择 `pom.xml` → `Add as Maven Project`

