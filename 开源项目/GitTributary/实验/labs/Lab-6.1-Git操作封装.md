# Lab 6.1: Git Operations with `git2`

**Phase:** 6 - Focused Engineering Topics  
**Estimated Time:** 3-5 days  
**Prerequisites:** Lab 1.3, Lab 2.2  
**Recommended Submission:** `git-ops` crate, tests, short API design note

---

## 1. Learning Objectives

完成本实验后，你应能够：

- 用 `git2` 为仓库状态、日志和提交建立最小封装
- 设计一个对插件友好的 `GitOps` trait
- 用临时仓库编写可重复的单元测试
- 处理 Git API 中的常见边界条件
- 比较“命令行调用 git”和“直接使用库”的工程差异

## 2. Why This Lab Matters

GitTributary 的核心能力之一，是让插件在受控接口中访问 Git 数据。课程里我们不希望插件直接执行任意 shell 命令，而是希望它们依赖一个清晰、可测试、可权限控制的能力接口。

这个 Lab 的目标不是覆盖 Git 的全部细节，而是建立一个足够小、足够清晰、足够可扩展的基础层。

## 3. Preparation

开始前请确认：

- 你理解 Git 中的工作区、索引区、提交历史和 `HEAD`
- 你知道 `git2` 与系统 `git` 命令不是同一套接口
- 你能在本地创建和删除临时目录

依赖建议：

```toml
[dependencies]
git2 = "0.19"
core = { path = "../core" }

[dev-dependencies]
tempfile = "3"
```

建议先执行：

```bash
cargo test -p git-ops
```

## 4. Procedure

### Step 1: Define the Domain Types

在 `crates/git-ops/src/lib.rs` 中先定义稳定的数据类型：

```rust
use std::path::Path;

#[derive(Debug, Default, PartialEq, Eq)]
pub struct GitStatus {
    pub modified: Vec<String>,
    pub added: Vec<String>,
    pub deleted: Vec<String>,
}

#[derive(Debug, PartialEq, Eq)]
pub struct Commit {
    pub oid: String,
    pub message: String,
    pub author: String,
    pub timestamp: i64,
}

pub trait GitOps {
    fn status(&self, repo: &Path) -> Result<GitStatus, git2::Error>;
    fn log(&self, repo: &Path, limit: usize) -> Result<Vec<Commit>, git2::Error>;
    fn commit_all(&self, repo: &Path, msg: &str) -> Result<String, git2::Error>;
}
```

这里将 `commit` 明确命名为 `commit_all`，因为本实验的实现会“加入所有已修改文件并创建提交”。名称应反映真实语义。

### Step 2: Implement `Git2Ops`

```rust
pub struct Git2Ops;

impl GitOps for Git2Ops {
    fn status(&self, repo_path: &Path) -> Result<GitStatus, git2::Error> {
        let repo = git2::Repository::open(repo_path)?;
        let mut opts = git2::StatusOptions::new();
        opts.include_untracked(true)
            .recurse_untracked_dirs(true);

        let statuses = repo.statuses(Some(&mut opts))?;
        let mut result = GitStatus::default();

        for entry in statuses.iter() {
            if let Some(path) = entry.path() {
                let status = entry.status();

                if status.contains(git2::Status::WT_MODIFIED)
                    || status.contains(git2::Status::INDEX_MODIFIED)
                {
                    result.modified.push(path.to_string());
                }

                if status.contains(git2::Status::WT_NEW)
                    || status.contains(git2::Status::INDEX_NEW)
                {
                    result.added.push(path.to_string());
                }

                if status.contains(git2::Status::WT_DELETED)
                    || status.contains(git2::Status::INDEX_DELETED)
                {
                    result.deleted.push(path.to_string());
                }
            }
        }

        Ok(result)
    }

    fn log(&self, repo_path: &Path, limit: usize) -> Result<Vec<Commit>, git2::Error> {
        let repo = git2::Repository::open(repo_path)?;
        let mut revwalk = repo.revwalk()?;
        revwalk.push_head()?;
        revwalk.set_sorting(git2::Sort::TIME)?;

        let mut commits = Vec::new();
        for oid in revwalk.take(limit) {
            let oid = oid?;
            let commit = repo.find_commit(oid)?;
            commits.push(Commit {
                oid: oid.to_string(),
                message: commit.message().unwrap_or("").to_string(),
                author: commit.author().name().unwrap_or("unknown").to_string(),
                timestamp: commit.time().seconds(),
            });
        }

        Ok(commits)
    }

    fn commit_all(&self, repo_path: &Path, msg: &str) -> Result<String, git2::Error> {
        let repo = git2::Repository::open(repo_path)?;
        let mut index = repo.index()?;
        index.add_all(["*"].iter(), git2::IndexAddOption::DEFAULT, None)?;
        index.write()?;

        let tree_id = index.write_tree()?;
        let tree = repo.find_tree(tree_id)?;
        let sig = git2::Signature::now("GitTributary Lab", "lab@example.com")?;

        let parents = match repo.head() {
            Ok(head) => {
                let parent = repo.find_commit(
                    head.target().ok_or_else(|| git2::Error::from_str("HEAD has no target"))?
                )?;
                vec![parent]
            }
            Err(_) => Vec::new(),
        };

        let parent_refs: Vec<&git2::Commit<'_>> = parents.iter().collect();
        let oid = repo.commit(Some("HEAD"), &sig, &sig, msg, &tree, &parent_refs)?;

        Ok(oid.to_string())
    }
}
```

设计说明：

- `status()` 关注工作区观测，不做业务判断
- `log()` 返回课程定义的领域结构，而不是直接暴露 `git2::Commit`
- `commit_all()` 明确包含“索引写入 + 提交”两个动作

### Step 3: Build Reliable Test Helpers

用 `tempfile` 初始化测试仓库：

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn init_test_repo() -> TempDir {
        let dir = TempDir::new().unwrap();
        let repo = git2::Repository::init(dir.path()).unwrap();

        std::fs::write(dir.path().join("README.md"), "# Test Repo\n").unwrap();

        let mut index = repo.index().unwrap();
        index.add_path(std::path::Path::new("README.md")).unwrap();
        index.write().unwrap();

        let tree_id = index.write_tree().unwrap();
        let tree = repo.find_tree(tree_id).unwrap();
        let sig = git2::Signature::now("Test", "test@example.com").unwrap();
        repo.commit(Some("HEAD"), &sig, &sig, "Initial commit", &tree, &[])
            .unwrap();

        dir
    }
```

### Step 4: Write Core Tests

```rust
    #[test]
    fn status_reports_untracked_files() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        std::fs::write(dir.path().join("new.txt"), "new file").unwrap();

        let status = ops.status(dir.path()).unwrap();
        assert!(status.added.iter().any(|item| item == "new.txt"));
    }

    #[test]
    fn status_reports_modified_files() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        std::fs::write(dir.path().join("README.md"), "# Changed\n").unwrap();

        let status = ops.status(dir.path()).unwrap();
        assert!(status.modified.iter().any(|item| item == "README.md"));
    }

    #[test]
    fn log_returns_latest_commits() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        let commits = ops.log(dir.path(), 10).unwrap();
        assert_eq!(commits.len(), 1);
        assert_eq!(commits[0].message, "Initial commit");
    }

    #[test]
    fn commit_all_creates_a_new_commit() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        std::fs::write(dir.path().join("file.txt"), "content").unwrap();

        let oid = ops.commit_all(dir.path(), "Add file.txt").unwrap();
        assert_eq!(oid.len(), 40);

        let commits = ops.log(dir.path(), 10).unwrap();
        assert_eq!(commits[0].message, "Add file.txt");
    }
}
```

### Step 5: Verify on Realistic Scenarios

运行：

```bash
cargo test -p git-ops
```

然后做两项手工验证：

1. 修改已跟踪文件，确认 `status().modified` 正确
2. 新建未跟踪文件，确认 `commit_all()` 可以创建新提交

### Step 6: Discuss Boundaries and Production Considerations

本实验刻意没有覆盖：

- `diff` 和 patch 渲染
- 分支、远程仓库、push/pull
- merge conflict 处理
- 用户身份配置读取

这是刻意的教学收束。第一步先把“本地读取与提交”做对，再扩展更复杂的 Git 场景。

## 5. Deliverables

| Item | Path | Requirement |
|------|------|-------------|
| Domain types | `crates/git-ops/src/lib.rs` | `GitStatus`、`Commit`、`GitOps` |
| `git2` implementation | 同上 | `status`、`log`、`commit_all` |
| Tests | 同上 `#[cfg(test)]` | 至少 4 个测试 |
| Design note | 任意实验记录位置 | 说明为什么 trait 不直接暴露 `git2` 原始类型 |

## 6. Assessment and Rubric

- **Correctness**
  `status`、`log`、`commit_all` 的主路径工作正常
- **Code Quality**
  trait 命名反映真实行为，领域类型清晰，不泄漏过多底层细节
- **Verification**
  使用临时仓库测试新增、修改和提交路径
- **Reflection**
  能说明 `git2` 封装的边界与未来扩展方向

## 7. Common Failure Modes

- `repo.signature()` 失败
  测试环境中通常没有全局 Git 身份配置，因此教学版本请直接使用 `Signature::now(...)`
- 调用了 `write_tree()` 但没有 `index.write()`
  索引状态可能与预期不一致，建议先显式写入
- 方法名与行为不匹配
  如果实现的是“自动加入所有改动再提交”，就不要把方法命名成泛泛的 `commit`

## 8. Extensions

- 增加 `diff()` 并返回统一的文本结果
- 比较 `git2` 与 `gix` 的 API 设计差异
- 为错误类型增加更贴近业务的包装层

## 9. Notes and Reflection

至少记录：

- 你如何划定 `GitOps` trait 的职责边界
- `git2` 中哪一个 API 最容易误用
- 如果未来要做权限控制，哪些方法最应该先被限制
