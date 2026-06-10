---
name: git-workflow
description: Git 工作流。多环境并行开发：创建分支、cherry-pick 同步、比对遗漏、压缩提交、发布打 tag、tag 比对。
argument-hint: '[git 操作描述]'
---

## 分支命名

feature 分支：`feature/<需求名>_<环境后缀>`
环境后缀对应基础分支：release、preview、staging

## 创建需求分支

从三个基础分支各拉一条 feature 分支。fetch → checkout 基础分支 → pull → checkout -b feature 分支。基础分支不存在则跳过，feature 分支已存在则提示无需创建。

```bash
git fetch origin
git checkout release && git pull origin release && git checkout -b feature/<name>_release
git checkout preview && git pull origin preview && git checkout -b feature/<name>_preview
git checkout staging && git pull origin staging && git checkout -b feature/<name>_staging
```

## 同步到并行分支

在一条 feature 分支提交阶段性成果后，切到其他并行分支执行 cherry-pick。高频重复操作。

```bash
# 确认差哪些 commit
git log <target>..HEAD --oneline

# 逐个目标分支 cherry-pick
git checkout feature/<name>_preview && git cherry-pick <commit>
git checkout feature/<name>_staging && git cherry-pick <commit>
```

### 冲突处理（Java Spring 项目）

cherry-pick 冲突时，按文件类型分策略处理：

```bash
# 先 --no-commit，预览变更
git cherry-pick --no-commit <commit>
```

| 文件类型 | 策略 | 原因 |
| ---- | ---- | ---- |
| `.java` 业务代码 | `git checkout --theirs <file>` | 业务逻辑以源分支为准 |
| `application*.yml/properties` | 手动合并 | 环境相关配置不可覆盖 |
| `pom.xml` | 手动检查依赖版本 | 环境可能依赖不同版本 |
| `*Test*.java` | 手动检查 | 测试类可能存在环境差异 |

安全验证：

```bash
git diff --cached          # 检查所有待提交变更
mvn compile                # 编译验证
git commit                 # 确认无误后提交
```

冲突过多（>5 个文件）或关联复杂，放弃 cherry-pick，改用 merge：

```bash
git cherry-pick --abort
git merge <source-branch> --no-commit
# 同样按上表策略处理冲突
```

## 比对并行分支遗漏

在某个分支上混改后，检查是否遗漏有效业务代码到其他并行分支。不要直接 diff（基础分支差异巨大），cherry-pick 不保留原始时间戳。长期项目 commit 累积多，需加时间窗口限定近期修改。

```bash
# 限定时间范围，只看自己近期的 commit
git log feature/<name>_release..feature/<name>_staging \
  --author="<自己>" --since="3 days ago" \
  --oneline --format="%h  %ad  %s" --date=short
```

反向亦然，逐一比对各并行分支。`--since` 按实际开发起止调整。

## 压缩提交

阶段性开发完毕（联调完 + 提测 / review 前），将 feature 分支上的多个 commit 压缩成一个。压缩后分支命名为 `feature/<name>_squash`。

```bash
# 从当前 feature 分支创建 squash 分支
git checkout -b feature/<name>_squash

# 以基础分支为基准，交互式 rebase
git rebase -i release
```

在编辑器中，保留第一个 `pick`，其余改为 `s`（squash），合并为一个干净 commit。

如果 commit 数量已知，可直接：

```bash
git rebase -i HEAD~<n>
```

## 发布打 Tag

准备发布时打 tag。默认从 release 分支打，特殊情况从并行兼容分支打（避免多带代码），需向用户确认。

命名规则：参照项目已有 tag 列表风格和最新 tag 的分隔方式，格式为 `版本号 + 日期 + 需求描述`。根据修改内容推荐名称。

```bash
# 先看已有 tag 风格
git tag --sort=-v:refname | head -10

# 打 tag
git tag -a <tag名> -m "<描述>"

# 推送
git push origin <tag名>
```

## 发布前比对 Tag

发布生产前，比对目标 tag 和线上当前 tag 之间的差异。检查是否夹带了其他人的提交，列出每个需求涉及的 commit 和负责人，告知用户需要联系谁。

```bash
# 两个 tag 之间的 commit 差异
git log <线上tag>..<目标tag> --oneline --format="%h  %an  %ad  %s" --date=short
```

按需求分组，标注非本人提交的作者，提醒用户确认是否应包含这些提交。