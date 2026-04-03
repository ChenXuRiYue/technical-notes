# Lab 1.3: Trait 实现 Capability 接口

**Phase 1 — Rust 基础与 Serde**
**预计耗时：** 2-3 天
**前置：** Lab 1.1（PluginManifest 类型）、Lab 1.2（PluginError 类型）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 定义 trait 作为能力抽象接口
- [ ] 为同一 trait 编写多个实现（mock + real）
- [ ] 使用 trait bound（`fn foo<T: GitRead>`）编写泛型函数
- [ ] 使用 trait object（`Box<dyn GitRead>`）实现运行时多态
- [ ] 理解泛型 vs trait object 的取舍

## 2. Background

GitTributary 的核心设计之一是 **Capability API**：插件通过宿主提供的 trait 访问系统能力（Git 操作、文件读取等），而不是直接调用系统 API。

这实现了：
- **隔离**：插件只能访问被授权的能力
- **可测试**：可以用 mock 实现替代真实实现
- **统一接口**：内部插件和 WASM 插件使用相同的 trait

**关键概念：**
- trait 定义行为契约，不包含实现
- trait bound 在编译时单态化（零运行时开销）
- trait object 在运行时分发（有 vtable 开销，但支持异构集合）
- `Box<dyn Trait>` 是最常见的 trait object 使用方式

## 3. Procedure

### Step 1: 定义数据类型

```rust
#[derive(Debug, Clone, PartialEq)]
pub struct GitStatus {
    pub modified: Vec<String>,
    pub added: Vec<String>,
    pub deleted: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct GitCommit {
    pub hash: String,
    pub message: String,
    pub author: String,
}

#[derive(Debug, Clone, PartialEq)]
pub struct DirEntry {
    pub name: String,
    pub is_dir: bool,
}
```

### Step 2: 定义 Capability Traits

```rust
use crate::error::PluginError;

pub trait GitRead {
    fn status(&self, repo_path: &str) -> Result<GitStatus, PluginError>;
    fn log(&self, repo_path: &str, limit: usize) -> Result<Vec<GitCommit>, PluginError>;
    fn diff(&self, repo_path: &str, from: &str, to: &str) -> Result<String, PluginError>;
}

pub trait FileRead {
    fn read(&self, path: &str) -> Result<String, PluginError>;
    fn list_dir(&self, path: &str) -> Result<Vec<DirEntry>, PluginError>;
}
```

### Step 3: 实现 MockGitRead

```rust
pub struct MockGitRead;

impl GitRead for MockGitRead {
    fn status(&self, _repo_path: &str) -> Result<GitStatus, PluginError> {
        Ok(GitStatus {
            modified: vec!["README.md".to_string()],
            added: vec![],
            deleted: vec![],
        })
    }

    fn log(&self, _repo_path: &str, limit: usize) -> Result<Vec<GitCommit>, PluginError> {
        Ok(vec![
            GitCommit {
                hash: "abc123".to_string(),
                message: "Initial commit".to_string(),
                author: "Test".to_string(),
            }
        ].into_iter().take(limit).collect())
    }

    fn diff(&self, _repo_path: &str, _from: &str, _to: &str) -> Result<String, PluginError> {
        Ok("mock diff output".to_string())
    }
}
```

### Step 4: 编写泛型函数

```rust
fn process_plugin<G: GitRead>(git: &G, plugin_name: &str) -> Result<String, PluginError> {
    let status = git.status(".")?;
    Ok(format!(
        "{}: {} modified, {} added, {} deleted",
        plugin_name,
        status.modified.len(),
        status.added.len(),
        status.deleted.len()
    ))
}
```

**思考：** 为什么这里用 trait bound `G: GitRead` 而不是 `&dyn GitRead`？

### Step 5: 使用 Trait Object

```rust
use std::collections::HashMap;

pub struct CapabilityRegistry {
    git_readers: HashMap<String, Box<dyn GitRead>>,
    file_readers: HashMap<String, Box<dyn FileRead>>,
}

impl CapabilityRegistry {
    pub fn new() -> Self {
        Self {
            git_readers: HashMap::new(),
            file_readers: HashMap::new(),
        }
    }

    pub fn register_git(&mut self, name: &str, impl_: Box<dyn GitRead>) {
        self.git_readers.insert(name.to_string(), impl_);
    }

    pub fn get_git(&self, name: &str) -> Option<&dyn GitRead> {
        self.git_readers.get(name).map(|b| b.as_ref())
    }
}
```

### Step 6: 编写测试

```rust
#[test]
fn test_mock_git_read() {
    let mock = MockGitRead;
    let result = process_plugin(&mock, "test-plugin").unwrap();
    assert!(result.contains("1 modified"));
}

#[test]
fn test_trait_object_registry() {
    let mut registry = CapabilityRegistry::new();
    registry.register_git("default", Box::new(MockGitRead));

    let git = registry.get_git("default").unwrap();
    let status = git.status(".").unwrap();
    assert_eq!(status.modified, vec!["README.md"]);
}

#[test]
fn test_generic_accepts_both_implementations() {
    // 同一个函数接受不同的实现
    let mock = MockGitRead;
    // let real = RealGitRead; // 你实现了 RealGitRead 后取消注释

    let r1 = process_plugin(&mock, "mock").unwrap();
    // let r2 = process_plugin(&real, "real").unwrap();
    assert!(r1.contains("mock"));
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 类型定义 | `src/types.rs` | GitStatus, GitCommit, DirEntry |
| Trait 定义 | `src/capability.rs` | GitRead, FileRead |
| Mock 实现 | `src/mock.rs` | MockGitRead |
| 注册表 | `src/registry.rs` | CapabilityRegistry |
| 测试 | 各模块 `#[cfg(test)]` | ≥ 3 个测试 |

## 5. Evaluation Criteria

- [ ] `cargo test` 全部通过
- [ ] 同一个 `process_plugin` 函数能接受 mock 实现
- [ ] `Box<dyn GitRead>` 能存入 `HashMap` 并正确调用
- [ ] 代码结构清晰：trait 定义、mock 实现、使用方分离

## 6. Extensions (Optional)

- [ ] 实现 `RealGitRead`（调用 `git2` crate，不需要完整实现，能编译即可）
- [ ] 实现 `FileRead` trait 及其 mock
- [ ] 尝试用 `impl Trait` 语法重写 `process_plugin` 的参数类型
- [ ] 比较编译后的二进制大小：trait bound vs trait object

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- 泛型和 trait object 各自适合什么场景？ -->

**可复用的代码：**

<!-- GitRead, FileRead trait 定义和 CapabilityRegistry 可以直接搬到 GitTributary -->
