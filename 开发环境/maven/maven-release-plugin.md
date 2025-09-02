# 📌 Maven  Release Plugin



> This plugin is used to release a project with Maven, saving a lot of repetitive, manual work. Releasing a project is made in two steps: prepare and perform.

官方给出定义：该插件致力于发布一使用 Maven 的项目过程中，节省大量重复、手工的工作。发布工作被划分为两步：准备 和 执行。

**插件提供的工具箱**

1. **release:clean** 清理上次 release 失败留下的文件
2. **release:prepare** 准备发布（在 SCM 中完成版本升级、打标签等）
3. **release:prepare-with-pom** prepare + 生成 release 专用 pom 文件，记录当时完全解析的依赖版本
4. **release:rollback** 版本回滚（执行 perform 之前）
5. **release:perform** 从 SCM 的 tag 构建并部署到远程仓库
6. **release:stage** 发布暂存到一个本地或远程的 staging
7. **release:branch** 创建一个新的分支，并且更新该分支版本号
8. **release:update-versions** 手动更新 pom.xml 中的版本号

**经典命令组合：**

```bash
# 1. 如果上次失败，先清理
mvn release:clean

# 2. 准备发布（改版本、打 tag、升级开发版）
mvn release:prepare

# 3. 执行发布（从 tag 构建并部署）
mvn release:perform
```

## 📄 Goals

### 🔖 release:prepare

[prepare](https://maven.apache.org/maven-release/maven-release-plugin/prepare-mojo.html)

> Prepare for a release in SCM. Steps through several phases to ensure the POM is ready to be released and then prepares SCM to eventually contain a tagged version of the release and a record in the local copy of the parameters used. This can be followed by a call to `release:perform`. 

为在版本控制系统发布做准备。分阶段的执行一系列检查工作确保 POM 已经可以发布。

1. 将当前开发版本的版本号升级为一个正式发布版本号（如1.0.0）并提交到 SCM。并且在 SCM 为正式版本的代码打上标签如（v1.0.0）。
2. 自动将版本号升级为下一个开发周期的版本（如 `1.0.1-SNAPSHOT`），并且提交。
3. 为了确保发布过程可重现、可追溯，插件在本地生成一个记录 **（release.properties 文件）**。该文件记录了本次发布的所有参数如：原版本号、发布版本号、下一个开发版本号、标签名。它可以用于回滚操作。

注意 prepare 只是在准备阶段，它只在源代码层做好发布准备（改版本号、打标签）。后续还需要执行 perform流程实现**真正的发布**。

**工作副本：** （方便理解 clean 操作）

1. release.properties: 包含了用于该次发布的核心配置文件和工作记录：

```properties
# release.properties
project.scm.url=scm:git:https://github.com/mycompany/my-app.git
project.scm.tag=HEAD
project.dev.com.mycompany:my-app=1.1.0-SNAPSHOT
project.rel.com.mycompany:my-app=1.0.0
scm.commentPrefix=[maven-release-plugin]
preparationGoals=clean verify
executionRoot=true
pushChanges=true
# ... 其他配置
```

2. Pom.xml.releaseBackup(备份文件)

将原始的 pom.xml 复制一份作为备份方便后续使用回退。

**可选参数**：

关键参数的背后逻辑产生于以下几步：

1. **检查（Check）**: 确保工作目录是干净的，没有未提交的代码，并且所有依赖都是可用的。
2. **交互（Interactive）**: 与用户交互，确认或输入版本号、标签名等关键信息。
3. **转换（Transform）**: 将 POM 中的 SNAPSHOT 版本号转换为 Release 版本号，并提交到 SCM。
4. **标记（Tag）**: 在 SCM 中创建一个标签（Tag），永久记录发布时刻的代码状态。
5. **迭代（Iterate）**: 将版本号更新为下一个开发版本（通常是一个新的 SNAPSHOT），并提交到 SCM。

| Name    | Type    | Since   |description|
| ------- | ------- | ------- | ---- |
| `<addSchema>` | `boolean` | `——` | Whether to add a schema to the POM if it was previously missing on release. (如果在发布前 POM 文件缺少 schema 声明，是否为其添加一个。)<br /> 默认为 true<br />schema 文件即定义 maven 规则。该概念产生于 xml 配置规范性产生的技术 |
| `<allowTimestampedSnapshots>` | `boolean` | 2.0-beta-7 |Whether to allow timestamped SNAPSHOT dependencies. Default is to fail when finding any SNAPSHOT.<br />（这个参数决定）是否允许（项目）依赖时间戳格式的 SNAPSHOT 包。（插件的）默认行为是：当发现（项目中存在）任何类型的 SNAPSHOT 依赖时，就让发布过程失败。如果设置为 true：将不理会照常拉取（非常不建议！！！ 带有时间戳的被Maven 认定为 SNAPSHOT 包，会被自动清理仅保留最新几个）。|
|`<argument>`|`String`|-|Additional arguments to pass to the Maven executions, separated by spaces.<br/>**User Property**: `arguments`<br/>**Alias**: `prepareVerifyArgs`<br/>传递参数给 Maven 运行测试阶段。prepare 过程中会进行 pom 运行测试，这将会进行一次完整的 Maven 构建生命周期。这和 Maven 构建相关：常见的参数有， -Ds kipIts 跳过集成测试，-Dcheckstyle.skip=true 跳过代码质量检查，激活特定 Profile -P prod 等。|
|`<dryrun>`|`boolean`|`-`|Dry run: don't checkin or tag anything in the scm repository, or modify the checkout. Running `mvn -DdryRun=true release:prepare` is useful in order to check that modifications to poms and scm operations (only listed on the console) are working as expected. Modified POMs are written alongside the originals without modifying them.<br/>**Default**: `false`<br/>**User Property**: `dryRun`<br />**开启 `dryRun=true` 后，`release:prepare` 会执行所有“只读”的检查和非破坏性操作，但会跳过所有“写入”操作**。<br />它会产生一个副本，通常命名方便检查测试。它将会模拟重要的 SCM 操作（提交、打包等）不会真正执行。|
|`<generateReleasePoms>`|`boolean`|`-（已废弃）`|**Deprecated.** Please use release:prepare-with-pom instead.<br />No description. **Default**: `false` **User Property**: `generateReleasePoms`<br />控制是否为发布版本生成一个 独立的、冻结状态的 pom.xml 文件。将在target 目录中生成一个额外的名为 pom.xml.release 的文件<br />已经废弃，引入了**`release:prepare-with-pom`** 解决|
|`password`|`String`|`-`|The SCM password to use. **User Property**: `password`|
|`<pomFileName>`|`String`|`-`|The file name of the POM to execute any goals against. As of version 3.0.0, this defaults to the name of POM file of the project being built.<br/>**Default**: `${project.file.name}`<br/>**User Property**: `pomFileName`<br />指定一个自定义名称的 POM 文件，让 `maven-release-plugin` 针对这个指定的文件来执行其所有操作（如版本号更新、SCM 操作等），而不是默认的 `pom.xml`|
|`<preparatioGoals>`|`String`|`-`|Goals to run as part of the preparation step, after transformation but before committing. Space delimited.<br/>**Default**: `clean verify`<br/>**User Property**: `preparationGoals`<br />作为准备步骤的一部分，在转换之后、提交之前，要运行的目标。以空格分隔。<br />相当于对发布版本代码选择 Maven 构建流程。默认值 clean veritfy 清理目标、集成测试验证结果。<br />通过该参数可以选择执行其它阶段：<br />validate、compile、test、package、certify|
|`completionGoals`|`String`|`2.2`|Goals to run on completion of the preparation step, after transformation back to the next development version but before committing. Space delimited.<br/>**User Property**: `completionGoals`<br />定义发布准备阶段即将完成时的指令序列。<br />当前插件已经将本地的 pom.xml 从发布版本回退并转换成新的开发版本（e.g. 1.2.0 -> 1.3.0-SNAPSHOT）但还没有将包含这个新开发版本的 POM 文件提交到开发分支上。<br />**应用**<br />在这个钩子中，可以定制在开启新一轮开发迭代钱执行的一些最后的验证、部署、集成操作<br />1. 部署快照版本到公司仓库<br />    `<completionGoals>deploy</completionGoals>`<br />2. 执行集成测试<br />`    <completionGoals>verify -DskipUnitTests</completionGoals>`<br />3. 生成并提交文档站点：<br />    `<completionGoals>site site:deploy</completionGoals>`|
|`<resume>`|`boolean`|`-`|Resume a previous release attempt from the point where it was stopped.<br/>**Default**: `true`<br/>**User Property**: `resume`<br />它允许你让一个之前被中断（失败）的 `release:prepare` 过程从中断的地方继续执行，而不是从头开始。如最后一步因为网络抖动连接 SCM 服务器提交和打标签失败。运行test 集成测试成功但是已经花费了将近 半个小时，（如果成功判断流程可重用）提供为 resume 可以直接执行 SCM 的提交打标签步骤。|
|`<scmShallowClone>`|`boolean`|`-`|When cloning a repository if it should be a shallow clone or a full clone.<br/>**Default**: `true`<br/>**User Property**: `scmShallowClone`<br />  **`scmShallowClone=true` (默认值)**：进行 **“浅克隆”** 。只下载最近的历史记录，通常只包含指定标签（tag）或分支（branch）的最新提交，而不包含整个项目的所有历史记录。 **`scmShallowClone=false`**：进行 **“完整克隆”** 。下载仓库的完整历史记录，包括所有分支、所有标签的所有提交。<br /> `scmShallowClone` 参数只在执行 `release:perform` (或 `release:stage`) 目标时，在该目标内部的第一步——即“从SCM仓库克隆代码到临时目录”这一步——才起作用。它对 `release:prepare` 目标基本上没有影响。（日常不需要关心该参数）|
|`<tag>`|`string`|`-`|The SCM tag to use.<br/>**User Property**: `tag`<br/>**Alias**: `releaseLabel`<br/>|
|`<tagBase>`|`String`|`-`|The tag base directory in SVN, you must define it if you don't use the standard svn layout (trunk/tags/branches). For example, `http://svn.apache.org/repos/asf/maven/plugins/tags`. The URL is an SVN URL and does not include the SCM provider and protocol.<br/>**User Property**: `tagBase`<br/>标签基目录在SVN中，如果您没有使用标准的svn布局（trunk/tags/branches），则必须定义它。例如，http://svn.apache.org/repos/asf/maven/plugins/tags。该URL是一个SVN URL，并且不包含SCM提供者和协议。（使用 SVN 时才需要理会这个参数。一般使用 Git 做版本控制。SVN 是时代的眼泪）|
|`<username>`|`String`|`-`|The SCM username to use.<br/>**User Property**: `username`|
|`<useEditMode>`|`boolean`|`-`|Whether to use "edit" mode on the SCM, to lock the file for editing during SCM operations.<br/>**Default**: `false`<br/>**User Property**: `useEditMode`<br />控制插件在执行版本控制系统操作时，是否先显示锁定要修改的文件。这是一个极具时代特征的参数。在集中式版本控制系统时代，提交代码是 锁定-修改-解锁模型的。而Git 和 现代 SVN 使用 复制-修改-合并模型。（如果多人修改同一个文件，系统会在提交时尝试自动合并这些更改，如果合并失败则会提示解决冲突）|
|`<remoteTagging>`|`boolean`|`2.0-beta-9`|Currently only implemented with svn scm.<br/>. Enables a workaround to prevent issue due to svn client > 1.5.0 (fixed in 1.6.5) (https://issues.apache.org/jira/browse/SCM-406)<br/>.  You may not want to use this in conjunction with suppressCommitBeforeTag, such that no poms with released versions are committed to the working copy ever.<br/><br/>**Default**: true<br/>**User Property**: remoteTagging<br /> SVN 作为 SCM 下的控制参数，主要控制是否直接在远程版本库中创建标签。这样为开发者提供一种更手动、更可控的流程。|
|`<suppressCommitBeforeTag>`|`boolean`|`2.1`|Whether to suppress a commit of changes to the working copy before the tag is created.<br />This requires `remoteTagging` to be set to false.<br />`suppressCommitBeforeTag` is useful when you want to avoid poms with released versions in all revisions of your trunk or development branch.<br />**Default**: `false`<br />**User Property**: `suppressCommitBeforeTag`<br />该参数控制是否提交。当设置为 true 时，插件将会在本地将版本修改为 1.0.0 （原来为1.0.0-SNAPSHOT），但不会将其提交到主干。SVN 会以当前本地工作目录状态为基础创建一个标签将这些为提交的更改大报道一个新的标签目录中，然后再提交这个新目录到 仓库的 tags 位置。接着它将会将本地的 pom 回滚到修改前的状态，继续正常的开发流程(1.0.1-SNAPSHOT)。它的价值在于可以保持主干历史的纯粹性。<br />实验如下：<br />**参数设置为 false**<br />1. `mvn release:prepare`<br />2. 插件提交两次：<br />a. **提交A**： 将 `pom.xml` 版本从 `1.2.0-SNAPSHOT` 改为 `1.2.0` <br />b. **提交B**: 将 `pom.xml` 版本从 `1.2.0` 改为 `1.3.0-SNAPSHOT`<br />3. 创建了一个指向提交 A 的标签 v1.2.0<br />**参数设置为 true**<br />1. `mvn release:prepare` 执行<br />2. 插件没有为 发布版本1.2.0 创建提交。它直接在本地基于未提交的更改创建了标签v1.2.0<br />3.插件只提交了一次：将pom.xml 版本从1.2.0-SNAPSHOT 直接改为 1.3.0-SNAPSHOT （跳过了1.2.0） 这个中间状态<br />|
| `<checkModificationExcludes>` | `String[]` |`2.1`|A list of additional exclude filters that will be skipped when checking for modifications on the working copy. Is ignored, when checkModificationExcludes is set.<br />定制化检查阶段：<br />检查阶段一般会检查所有受版本控制系统控制的文件。而通过该项参数，可以配置白名单。如下：checkModificationExcludes 配置示例<br />|
| `autoVersionSubmodules`       | `boolean`  |`2.0-beta-5`|Whether to automatically assign submodules the parent version. If set to false, the user will be prompted for the version of each submodules.<br/>**Default**: `false`<br/>**User Property**: `autoVersionSubmodules`<br />多模块项目下使用 release 插件，如果设置为false: 发布过程中，插件会**为每个子模块交互式地提示**用户输入版本号。设置为 true时：插件会**自动将所有子模块的版本号设置为与父POM相同的版本号**。|

---
参数的学习选取上：主要挑选了首代命令（首代命令足够经典 + 可以了解代码管理发布控制流程的发展。），以及 AI 推荐可以加深对 Maven 工程、代码管理工程理解的相关命令。 


**引用**
checkModificationExcludes 配置示例

```xml
        <checkModificationExcludes>
            <!-- 排除版本说明文件 -->
            <checkModificationExclude>**/release-notes.txt</checkModificationExclude>
            <!-- 排除版本属性文件 -->
            <checkModificationExclude>**/version.properties</checkModificationExclude>
            <!-- 排除所有IDE的配置文件（通常不建议提交这些，但万一提交了） -->
            <checkModificationExclude>**/.idea/**</checkModificationExclude>
            <checkModificationExclude>**/.vscode/**</checkModificationExclude>
        </checkModificationExcludes>
```

总配置 demo (ai 生成)

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-enterprise-app</artifactId>
    <version>2.5.0-SNAPSHOT</version> <!-- 当前开发版本 -->
    <packaging>jar</packaging>

    <!-- ... 其他项目配置 (dependencies, properties, 等) ... -->

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-release-plugin</artifactId>
                <version>3.0.0</version>
                <configuration>
                    <!-- ############################### -->
                    <!-- 场景一：保持Git历史绝对洁净 (Git用户强推) -->
                    <!-- 作用：避免发布版本号（如2.5.0）的提交污染主干历史 -->
                    <!-- 效果：git log 里看不到 "prepare release ..." 的提交 -->
                    <suppressCommitBeforeTag>true</suppressCommitBeforeTag>
                    <remoteTagging>true</remoteTagging> <!-- Git下可与suppressCommitBeforeTag共存 -->

                    <!-- ############################### -->
                    <!-- 场景二：多模块项目版本管理 -->
                    <!-- 作用：确保所有子模块的版本号与父POM严格同步更新 -->
                    <!-- 效果：无需为每个子模块交互式输入版本号 -->
                    <autoVersionSubmodules>true</autoVersionSubmodules>

                    <!-- ############################### -->
                    <!-- 场景三：预发布验证强化 -->
                    <!-- 作用：在打标签前执行更严格的构建和测试，确保发布质量 -->
                    <!-- 效果：如果集成测试失败，发布流程将中止，不会创建标签 -->
                    <preparationGoals>clean verify</preparationGoals>
                    <!-- 如果集成测试很慢，可以拆分成CI流水线的两个阶段 -->
                    <!-- <preparationGoals>clean package</preparationGoals> -->

                    <!-- ############################### -->
                    <!-- 场景四：发布后自动部署快照 (CI/CD核心) -->
                    <!-- 作用：新的快照版本（2.6.0-SNAPSHOT）立即对团队可用 -->
                    <!-- 时机：在提交回主干前执行，保证部署和代码提交的原子性 -->
                    <completionGoals>deploy</completionGoals>

                    <!-- ############################### -->
                    <!-- 场景五：跳过非关键文件的修改检查 -->
                    <!-- 作用：避免因更新发布说明等文件导致发布流程失败 -->
                    <!-- 效果：即使 release-notes.md 有未提交修改，release:prepare 也会继续 -->
                    <checkModificationExcludes>
                        <checkModificationExclude>**/release-notes.md</checkModificationExclude>
                        <checkModificationExclude>**/docs/version-info.txt</checkModificationExclude>
                    </checkModificationExcludes>

                    <!-- ############################### -->
                    <!-- 场景六：非交互式发布 (用于自动化脚本) -->
                    <!-- 作用：无需手动输入，直接使用预设的版本号进行发布 -->
                    <!-- 效果：mvn release:prepare -Darguments="-DskipTests" 即可全自动运行 -->
                    <releaseVersion>2.5.0</releaseVersion>
                    <developmentVersion>2.6.0-SNAPSHOT</developmentVersion>
                    <arguments>-DskipTests</arguments> <!-- 为 release:perform 传递参数 -->

                    <!-- ############################### -->
                    <!-- 场景七：SCM提交信息定制 -->
                    <!-- 作用：统一提交信息格式，便于审计和追溯 -->
                    <scmCommentPrefix>[RELEASE] </scmCommentPrefix>

                    <!-- ############################### -->
                    <!-- 场景八：安全考虑 - 推送前人工审核 -->
                    <!-- 作用：在推送提交和标签前中断流程，供人工确认 -->
                    <!-- 效果：插件完成所有准备工作后暂停，用户确认无误后再手动推送 -->
                    <pushChanges>false</pushChanges>
                    <!-- 使用方式：mvn release:prepare && mvn release:perform -->

                </configuration>
            </plugin>
        </plugins>
    </build>

    <!-- SCM 配置是 release plugin 工作的前提 -->
    <scm>
        <connection>scm:git:https://github.com/example/my-enterprise-app.git</connection>
        <developerConnection>scm:git:https://github.com/example/my-enterprise-app.git</developerConnection>
        <url>https://github.com/example/my-enterprise-app</url>
        <tag>v${project.version}</tag> <!-- 标签命名规则 -->
    </scm>

    <!-- 分发管理，指定发布到的仓库 -->
    <distributionManagement>
        <snapshotRepository>
            <id>company-snapshots</id>
            <url>https://nexus.example.com/repository/maven-snapshots/</url>
        </snapshotRepository>
        <repository>
            <id>company-releases</id>
            <url>https://nexus.example.com/repository/maven-releases/</url>
        </repository>
    </distributionManagement>

</project>
```

### 🔖  release:prepare-with-pom

[prepare-with-pom](https://maven.apache.org/maven-release/maven-release-plugin/prepare-with-pom-mojo.html)

Prepare for a release in SCM, fully resolving dependencies for the purpose of producing a "release POM".
在版本控制系统（如Git）中执行一系列发布准备工作（版本号变更、打标签等）。在此过程中，它会将项目所有依赖项的具体版本号彻底锁定，并最终生成一个名为 `pom.release.xml` 的文件。这个文件精确记录了发布那一刻所有依赖的真实版本，其唯一目的就是确保未来的任何构建都是完全可重现的。”

**Prepare-with-pom VS prepare**

1. 标准 prepare 流程中的 检查、交互、转换、tag、迭代流程基本一致。

2. Prepare-with-pom 同时生成了 pom.release.xml 文件。该文件详细记录了每个依赖的版本，它确保该次构建是可复现的。关键在于它们对 SNAPTSHOPT 类依赖的处理：

   例如：

   **以下 为 AI 生成：**

   ```xml
   <project>
     <modelVersion>4.0.0</modelVersion>
     <groupId>com.mycompany</groupId>
     <artifactId>my-app</artifactId>
     <version>1.0.0-SNAPSHOT</version> <!-- 自己是SNAPSHOT版本 -->
   
     <dependencies>
       <dependency>
         <groupId>com.otherteam</groupId>
         <artifactId>common-utils</artifactId>
         <version>1.1.0-SNAPSHOT</version> <!-- 依赖也是SNAPSHOT版本 -->
       </dependency>
     </dependencies>
   </project>
   ```

   ${\large {\color[RGB]{250, 157, 30}执行\ mvn \ release:prepare}} $

   1. **目标**：它试图将所有东西都变成正式版。
   2. **过程**：
      - 将 `<version>1.0.0-SNAPSHOT</version>` 改为 `<version>1.0.0</version>`。
      - **同时，它也会尝试将依赖 `<version>1.1.0-SNAPSHOT</version>` 改为 `<version>1.1.0</version>`。**
   3. **结果**：
      - 插件会去Maven仓库里寻找 `common-utils:1.1.0`。
      - 如果 `common-utils` 团队还没有发布 `1.1.0` 正式版，那么这个包**在仓库中不存在**。
      - **构建失败！** 错误信息：`Cannot find artifact com.otherteam:common-utils:jar:1.1.0 in central (https://repo.maven.apache.org/maven2)`

   **结论：`prepare` 要求你的SNAPSHOT依赖必须已经有对应的正式版，否则就失败。**

   ${\large {\color[RGB]{250, 157, 30}执行 \ mvn \ release:prepare-with-pom}} $

   1. **目标**：记录当前成功的状态，而不是改变它。

   2. **过程**：

      - 将 `<version>1.0.0-SNAPSHOT</version>` 改为 `<version>1.0.0</version>`。

      - **但它不会去改动依赖的版本！** 它允许依赖保持 `<version>1.1.0-SNAPSHOT</version>`。

      - 它会询问Maven仓库：“当前 `common-utils:1.1.0-SNAPSHOT` 具体指的是哪个文件？” 仓库返回一个带时间戳的版本，例如 `1.1.0-20240827.102045-1`。

      - **生成 `pom.release.xml`**，在这个新文件里，依赖被**锁定**为解析后的真实版本：

        xml

        ```
        <!-- pom.release.xml 的内容 -->
        <dependency>
            <groupId>com.otherteam</groupId>
            <artifactId>common-utils</artifactId>
            <!-- 版本被锁定为解析后的时间戳版本 -->
            <version>1.1.0-20240827.102045-1</version>
        </dependency>
        ```

   3. **结果**：

      - **发布成功！** Git标签中包含两个文件：
        - `pom.xml` （依赖可能还是 `1.1.0-SNAPSHOT`）
        - `pom.release.xml` （依赖是 **`1.1.0-20240827.102045-1`**）

   **结论：`prepare-with-pom` 不要求依赖已有正式版。它接受SNAPSHOT依赖，并记录下构建时这个SNAPSHOT所对应的确切二进制文件，从而保证发布成功和未来的可重现性。**

### 🔖 release:clean

[clean](https://maven.apache.org/maven-release/maven-release-plugin/clean-mojo.html)

> Clean up after a release preparation. This is done automatically after a successful `release:perform`, so is best served for cleaning up a failed or abandoned release, or a dry run. Note that only the working copy is cleaned up, no previous steps are rolled back
> 

在一次 release preparation 之后的清除阶段。它将会在 release:perform 命令执行成功时自动完成。因此它最适用于清理失败、被放弃的发布，或者一次模拟运行。注意它只清理本地的工作副本，不会回滚之前的任何步骤。

### 🔖 release: rollback

Rollback changes made by a previous release. This requires that the previous release descriptor `release.properties` is still available in the local working copy.



### 🔖 release: perform

> Perform a release from SCM, either from a specified tag, or the tag representing the previous release in the working copy created by `release:prepare`. 

从版本控制系统（SCM）中检出在 release:prepare 阶段打的标签，release:perform 的最终目的，就是把项目构建成一个正式版构建，发布到 Maven 依赖仓库中，供其他项目作为依赖使用。



${\large {\color[RGB]{250, 157, 30}发布过程}} $


## 📄 Usage



## 🌳 生长思考

对发散的自由捕捉、精确化

## 💭 反复绊脚

轮次：1

1. Maven 管理的项目结构下工作逻辑是怎么样的？
2. Maven 在真正工作时和个人使用有什么区别？
3. 如果作为一个架构师，使用 Maven 时，要考虑什么问题？
4. maven schema 怎么理解？
5. 为什么 prepare 也要连接 SCM 服务器进行提交或打标签？
6. 了解 release 参数的意义是什么？
7. 为什么说 remoting tag 仅在 svn 中实现，而 suppressCommitBeforeTag 说前提对 removingTag 设置为false呢？
8. release:prepare-with-pom 和 release:prepare 的区别是什么？
9. clean 清除了什么内容？

## 🗺️ 修订记录



## 🛠️ 实践经历

### 🧸 maven-demo

练习 maven 的 demo 项目：

## ⚙️ Prompt

**初学**

````markdown
# 背景
我是一名初级 Java 后端开发工程师。为了适应标准规范企业项目的开发工作，我正式深入学习 Maven，特别是 Maven Release Plugin.
# 个人经验
我曾经初步搭建过一个简单的 demo 项目。仅仅接触到了以下方面：
1. 独立开发工作者 Maven 环境的配置与下载
2. 独立开发工作者使用 Maven官方中心仓库
3. 简单的标签包括：denpencies management, depencies, depencie, parent, version, propites 等。总体来说可以管理 pom 文件的继承。使用 idea 的依赖分析器管理冲突。
# 问题
我准备更深入的了解 release:perform 命令

# 已解决问题
这里保存了一些已经提问的上下文

## 阶段一：了解prepare
1. 问题一
1.1 **Question**:我在阅读官方文档的 Oveview 模块。其中我遇到了一个模块内容如下：
```txt
Goals Overview
release:clean Clean up after a release preparation.
release:prepare Prepare for a release in SCM.
release:prepare-with-pom Prepare for a release in SCM, and generate release POMs that record the fully resolved projects used.
release:rollback Rollback a previous release.
release:perform Perform a release from SCM.
release:stage Perform a release from SCM into a staging folder/repository.
release:branch Create a branch of the current project with all versions updated.
release:update-versions Update the versions in the POM(s)
```
这似乎非常重要，但是我不明白它们是什么？根源，以及应用背景。请你和我简略讲讲，我发现在文档中它作为一个重要的独立模块。
1.2 answer
我明白了每个命令大概作用
2. 问题二
2.1 目前我打算着重理解 release:clean 命令。
为什么要 clean? 换而言之该插件的运行机制原理是什么？为什么产生了副本？
2.2 answer
我通过更进一步了解 prepare 过程明白了会有一些中间文件产生。为了确保发布过程可重现、可追溯，插件在本地生成一个记录 （release.properties 文件）。该文件记录了本次发布的所有参数如：原版本号、发布版本号、下一个开发版本号、标签名。它可以用于回滚操作。

3. 问题三
我已经知道了 addSchema、allowTimestampedSnapshots、argument、dryrun、generateReleasePoms、password、pomfilename、reparatioGoals、resume、scmShallowClone、tag、tagBase、username、userFileMode这几参数。
## 阶段二：了解 prepare-with-pom
在版本控制系统（如Git）中执行一系列发布准备工作（版本号变更、打标签等）。在此过程中，它会将项目所有依赖项的具体版本号彻底锁定，并最终生成一个名为 `pom.release.xml` 的文件。这个文件精确记录了发布那一刻所有依赖的真实版本，其唯一目的就是确保未来的任何构建都是完全可重现的。

## 阶段三： 了解 clean
... 略

## 阶段四：了解 perform

````

