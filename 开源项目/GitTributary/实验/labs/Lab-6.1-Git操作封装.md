# Lab 6.1: Git 操作封装

**Phase 6 — 专项功能**
**预计耗时：** 3-5 天
**前置：** Lab 1.3（Trait 定义）、Lab 2.2（Workspace 中的 git-ops crate）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 用 `git2` crate 执行基本的 Git 操作
- [ ] 封装 trait 为统一的 Git 操作接口
- [ ] 用 `tempfile` 创建临时 Git 仓库做单元测试
- [ ] 理解 Git 内部概念（Oid, Reference, Remote）

## 2. Background

Git 数据加工是 GitTributary 的核心功能之一。插件需要通过 Capability API 访问 Git 数据，而不是直接调用 `git` 命令行。

`git2` 是 libgit2 的 Rust binding，提供了完整的 Git 操作 API。

**关键概念：**
- `Repository::open()` 打开仓库
- `StatusOptions` 获取工作区状态
- `Revwalk` 遍历提交历史
- `Diff` 比较差异
- 临时目录测试（`tempfile::TempDir`）

## 3. Procedure

### Step 1: 添加依赖

```toml
# crates/git-ops/Cargo.toml
[dependencies]
git2 = "0.19"
core = { path = "../core" }

[dev-dependencies]
tempfile = "3"
```

### Step 2: 定义 GitOps trait

```rust
// crates/git-ops/src/lib.rs
use std::path::Path;

pub struct GitStatus {
    pub modified: Vec<String>,
    pub added: Vec<String>,
    pub deleted: Vec<String>,
}

pub struct Commit {
    pub oid: String,
    pub message: String,
    pub author: String,
    pub timestamp: i64,
}

pub trait GitOps {
    fn status(&self, repo: &Path) -> Result<GitStatus, git2::Error>;
    fn log(&self, repo: &Path, limit: usize) -> Result<Vec<Commit>, git2::Error>;
    fn diff(&self, repo: &Path, spec: &str) -> Result<String, git2::Error>;
    fn commit(&self, repo: &Path, msg: &str) -> Result<String, git2::Error>;
}
```

### Step 3: 实现 Git2Ops

```rust
pub struct Git2Ops;

impl GitOps for Git2Ops {
    fn status(&self, repo_path: &Path) -> Result<GitStatus, git2::Error> {
        let repo = git2::Repository::open(repo_path)?;
        let mut opts = git2::StatusOptions::new();
        opts.include_untracked(true);

        let statuses = repo.statuses(Some(&mut opts))?;
        let mut result = GitStatus {
            modified: Vec::new(),
            added: Vec::new(),
            deleted: Vec::new(),
        };

        for entry in statuses.iter() {
            if let Some(path) = entry.path() {
                let s = entry.status();
                if s.contains(git2::Status::WT_MODIFIED) {
                    result.modified.push(path.to_string());
                }
                if s.contains(git2::Status::INDEX_NEW) || s.contains(git2::Status::WT_NEW) {
                    result.added.push(path.to_string());
                }
                if s.contains(git2::Status::WT_DELETED) || s.contains(git2::Status::INDEX_DELETED) {
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

        let mut commits = Vec::new();
        for (i, oid) in revwalk.enumerate() {
            if i >= limit { break; }
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

    fn diff(&self, _repo: &Path, _spec: &str) -> Result<String, git2::Error> {
        // TODO: 实现 diff
        Ok("TODO: implement diff".to_string())
    }

    fn commit(&self, repo_path: &Path, msg: &str) -> Result<String, git2::Error> {
        let repo = git2::Repository::open(repo_path)?;
        let mut index = repo.index()?;
        let tree_id = index.write_tree()?;
        let tree = repo.find_tree(tree_id)?;

        let sig = repo.signature()?;
        let head = repo.head()?;
        let parent = repo.find_commit(head.target().unwrap())?;

        let oid = repo.commit(
            Some("HEAD"),
            &sig,
            &sig,
            msg,
            &tree,
            &[&parent],
        )?;

        Ok(oid.to_string())
    }
}
```

### Step 4: 编写测试

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn init_test_repo() -> TempDir {
        let dir = TempDir::new().unwrap();
        let repo = git2::Repository::init(dir.path()).unwrap();

        // 创建初始提交
        let file_path = dir.path().join("README.md");
        std::fs::write(&file_path, "# Test Repo").unwrap();

        let mut index = repo.index().unwrap();
        index.add_path(std::path::Path::new("README.md")).unwrap();
        let tree_id = index.write_tree().unwrap();
        let tree = repo.find_tree(tree_id).unwrap();
        let sig = git2::Signature::now("Test", "test@example.com").unwrap();
        repo.commit(Some("HEAD"), &sig, &sig, "Initial commit", &tree, &[]).unwrap();

        dir
    }

    #[test]
    fn test_status() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        // 添加一个新文件
        std::fs::write(dir.path().join("new.txt"), "new").unwrap();

        let status = ops.status(dir.path()).unwrap();
        assert!(status.added.iter().any(|f| f == "new.txt"));
    }

    #[test]
    fn test_log() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        let commits = ops.log(dir.path(), 10).unwrap();
        assert_eq!(commits.len(), 1);
        assert_eq!(commits[0].message, "Initial commit");
    }

    #[test]
    fn test_commit() {
        let dir = init_test_repo();
        let ops = Git2Ops;

        std::fs::write(dir.path().join("file.txt"), "content").unwrap();
        let mut index = git2::Repository::open(dir.path()).unwrap().index().unwrap();
        index.add_path(std::path::Path::new("file.txt")).unwrap();
        index.write().unwrap();

        let oid = ops.commit(dir.path(), "Add file.txt").unwrap();
        assert_eq!(oid.len(), 40); // SHA-1 hex
    }
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| GitOps trait | `crates/git-ops/src/lib.rs` | trait 定义 |
| Git2Ops 实现 | 同上 | 基于 git2 |
| 单元测试 | 同上 `#[cfg(test)]` | ≥ 3 个测试 |

## 5. Evaluation Criteria

- [ ] 能对一个真实 git 仓库执行 status/log/commit
- [ ] 所有测试独立、可重复（用 tempdir）
- [ ] `cargo test -p git-ops` 全部通过

## 6. Extensions (Optional)

- [ ] 实现 `diff` 方法
- [ ] 实现 `push`（用 mock，避免真实推送）
- [ ] 比较 `git2` vs `gix`：用 `gix` 重写一个方法

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- git2 的 API 设计和 Git 内部概念 -->

**可复用的代码：**

<!-- git-ops crate 是 GitTributary 的核心依赖 -->
