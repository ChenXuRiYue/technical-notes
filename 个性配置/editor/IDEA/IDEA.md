# IDEA

该文档描述 IDEA 相关的基础配置，包括了工作工程中积累的不同环境，工具效率技巧。

## 🪜 快捷键

 [IDEA快捷键—Mac.md](IDEA快捷键—Mac.md) 

## ⚙️ 激活破解

```txt
订单编号：4824870482602614210   "你好，该订单包含的商品为虚拟商品，发货后将不支持退换，如无异议可点击下方链接确认发货。"第一种方式（激活命令，可永久激活）：
1.Windows 使用 Win+x 按键，选择WindowsPowerShell(管理员)运行
复制下面命令运行即可全自动激活！！！！
irm ckey.run|iex

2.Linux 打开终端复制下面指令运行即可激活
wget --no-check-certificate ckey.run -O ckey.run && bash ckey.run

3.mac 打开终端复制下面指令运行即可激活
curl -L -o ckey.run ckey.run && bash ckey.run

第二种激活方式（激活工具，可永久激活）
激活工具（百度网盘）：jetbrain…
链接:https://pan.baidu.com/s/1G__QgRiHKyzHLJKgjVKXYw 
提取码:r3z1

第三种激活方式（激活码）
激活码地址:  全家桶激活

温馨提示：
建议使用第一种激活方式，可以永久激活任何版本
包售后，激活不成功包退，有问题随时联系
咸鱼不在线可联系客服扣扣 296859110
在线时间（8 - 12）（14 - 20）虚拟商品不退不换，感谢支持
```

## 🎨 主题配置

1. Material





## ⚙️ 其它配置

- 配置自动去除无效 import
  https://developer.aliyun.com/article/1349713



## ⚙️ 配置文件

### ❓ .idea 文件夹是什么？

> .idea 是 IntelliJ IDEA（以及基于 IntelliJ 平台的 IDE）在“目录型项目”下保存项目配置的专用目录。

**观察自己的一个文件夹产物**

1. Workspace.xml：记录个人工作区状态，比如打开了哪些文件、窗口布局、光标位置、本地更改列表等。这些是私有的，不应该提交到 Git。
2. Compiler.xml，encoding.xml `编译、文本解析方式等解读参数`
3. jarRespositories.xml `maven jar 包的远程下载地址`
4. material_theme_project_new.xml  `(material 插件产生的配置信息)`
5. misc.xml `杂项 miscellaneous 重点关注的是 JDK 版本，编译输出路径，一些小没必要放一个文件划开，但是经常用到的信息。`
6. Vcs.xml `版本控制系统配置信息`

**结论及观点**

可以使用：可再生部分，资产部分来理解这个内容

1. 对于一个 Maven 结构来说是一个翻译层，IDEA 将 Maven 解析成一种方便 软件工具读取的格式，它是可再生的，具有一定的工具缓存作用，减小解析工作。
2. 团队、个人资产：用户开发效率
   - 一键启动：配置了形如 `VM Options: -Denv=dev` 的启动参数。
   - 统一 IDEA 代码格式分析的相关规范
   - 数据库/工具配置等

**作为一名追求高效的工程师，应该这样看待 .idea：**

1. **对于构建（Build）**：它是**从属**的。pom.xml 才是老大，.idea 里的依赖配置只是 pom.xml的影子。不要手动改 .idea 里的依赖。

2. **对于运行（Run）与 规范（Style）**：它是**核心**的。它是 Maven 管辖范围之外的补充，承载了团队的“开发环境配置”。

##  📝 prompt

```markdown
# 背景
我是一名工作了半年的Java 后端开发工程师。我在努力的提升自己的效率。当前方向是学习怎么使用 IDEA 进行高效开发编码。

# 阶段
目前我在学习一个经典的 Spring 仓库结构生成时， IDEA 的支持。 

# 问题
我想知道 IDEA 中的 .IDEA 的文件夹是什么。有什么作用

# 历史问题以及关键结论

```

