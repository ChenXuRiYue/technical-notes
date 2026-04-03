# Lab 6.3: 权限系统雏形

**Phase 6 — 专项功能**
**预计耗时：** 3-4 天
**前置：** Lab 1.3（Trait）、Lab 4.2（Host Function）

---

## 1. Objectives

完成本实验后，你将能够：

- [ ] 设计基于声明的权限模型
- [ ] 在运行时拦截插件调用，校验权限
- [ ] 实现 Decorator/Middleware 模式包装 trait 实现
- [ ] 将权限信息传递给前端展示

## 2. Background

安全是插件系统的关键考量。插件声明需要哪些 capabilities（如 `git:read`, `file:read`），宿主在调用时校验实际权限是否满足。

Chrome Extension 的 Manifest V3 采用了类似的声明式权限模型。

**关键概念：**
- 声明式权限（manifest 中声明，运行时校验）
- Decorator 模式：包装原始 trait 实现，添加权限检查
- 权限粒度：`git:read` / `git:write` / `file:read` / `file:write` / `network:http`
- 权限拒绝错误：`PermissionDenied { capability, plugin }`

## 3. Procedure

### Step 1: 定义权限模型

```rust
// crates/core/src/permission.rs

/// 权限标识符
pub type Capability = String;

/// 插件的权限集合
pub struct PermissionSet {
    granted: std::collections::HashSet<Capability>,
}

impl PermissionSet {
    pub fn new(capabilities: Vec<String>) -> Self {
        Self {
            granted: capabilities.into_iter().collect(),
        }
    }

    pub fn has(&self, capability: &str) -> bool {
        self.granted.contains(capability)
    }

    pub fn require(&self, capability: &str) -> Result<(), PluginError> {
        if self.has(capability) {
            Ok(())
        } else {
            Err(PluginError::PermissionDenied {
                capability: capability.to_string(),
            })
        }
    }
}
```

### Step 2: Manifest 中声明权限

```json
{
  "name": "git-deploy",
  "version": "0.1.0",
  "capabilities": ["git:read", "git:write", "file:read"],
  "commands": [
    { "id": "deploy", "description": "Deploy notes" }
  ]
}
```

### Step 3: Decorator 模式包装 GitRead

```rust
use core::GitRead;

/// 权限校验装饰器
pub struct PermissionedGitRead<G: GitRead> {
    inner: G,
    permissions: PermissionSet,
}

impl<G: GitRead> PermissionedGitRead<G> {
    pub fn new(inner: G, permissions: PermissionSet) -> Self {
        Self { inner, permissions }
    }
}

impl<G: GitRead> GitRead for PermissionedGitRead<G> {
    fn status(&self, repo_path: &str) -> Result<GitStatus, PluginError> {
        self.permissions.require("git:read")?;
        self.inner.status(repo_path)
    }

    fn log(&self, repo_path: &str, limit: usize) -> Result<Vec<GitCommit>, PluginError> {
        self.permissions.require("git:read")?;
        self.inner.log(repo_path, limit)
    }

    fn diff(&self, repo_path: &str, from: &str, to: &str) -> Result<String, PluginError> {
        self.permissions.require("git:read")?;
        self.inner.diff(repo_path, from, to)
    }
}
```

### Step 4: 在 PluginHostManager 中集成

```rust
impl PluginHostManager {
    pub fn dispatch(&self, plugin_name: &str, command: &str, args: Option<Value>) -> Result<Value, PluginError> {
        let entry = self.plugins.get(plugin_name)
            .ok_or_else(|| PluginError::PluginNotFound(plugin_name.to_string()))?;

        // 检查插件声明的权限
        let permissions = PermissionSet::new(entry.manifest.capabilities.clone());

        // 根据命令需要的权限进行校验
        // 示例：deploy 命令需要 git:write
        if command == "deploy" {
            permissions.require("git:write")?;
        }

        // 执行命令...
        entry.dispatch(command, args)
    }
}
```

### Step 5: 编写测试

```rust
#[cfg(test)] mod tests {
    use super::*;

    #[test]
    fn test_permission_granted() {
        let perms = PermissionSet::new(vec!["git:read".to_string()]);
        assert!(perms.has("git:read"));
        assert!(!perms.has("git:write"));
    }

    #[test]
    fn test_permission_denied() {
        let perms = PermissionSet::new(vec!["git:read".to_string()]);
        let result = perms.require("git:write");
        assert!(matches!(result, Err(PluginError::PermissionDenied { .. })));
    }

    #[test]
    fn test_decorated_git_read() {
        let mock = MockGitRead;
        let perms = PermissionSet::new(vec!["git:read".to_string()]);
        let guarded = PermissionedGitRead::new(mock, perms);

        // 有权限的操作
        assert!(guarded.status(".").is_ok());

        // 无权限的操作（如果 GitRead 有 write 方法）
    }

    #[test]
    fn test_dispatch_permission_check() {
        let mut phm = PluginHostManager::new();
        // 注册一个只有 git:read 权限的插件
        // 尝试调用需要 git:write 的命令 → 应该失败
    }
}
```

### Step 6: 前端权限展示

```tsx
function PluginPermissions({ pluginName }: { pluginName: string }) {
  const plugin = pluginRegistry.get(pluginName);
  if (!plugin) return null;

  return (
    <div className="permissions">
      <h3>Permissions</h3>
      <ul>
        {plugin.manifest.capabilities.map(cap => (
          <li key={cap}>
            <span className={`capability ${cap.split(':')[1]}`}>{cap}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 4. Deliverables

| 产出 | 路径 | 说明 |
|------|------|------|
| 权限模型 | `crates/core/src/permission.rs` | PermissionSet |
| 装饰器 | `crates/plugin-host/src/permissioned.rs` | PermissionedGitRead |
| 集成 | `crates/plugin-host/src/lib.rs` | dispatch 中的权限检查 |
| 测试 | 各模块 `#[cfg(test)]` | ≥ 4 个测试 |
| 前端 | `src/components/PluginPermissions.tsx` | 权限展示 |

## 5. Evaluation Criteria

- [ ] 声明了 `["git:read"]` 的插件尝试调用 `git:write` → 被拒绝
- [ ] 错误信息包含 capability 和 plugin 名
- [ ] 前端能展示插件声明的权限列表
- [ ] `cargo test` 全部通过

## 6. Extensions (Optional)

- [ ] 实现更细粒度的权限（`file:read:/notes/**` 路径级别的权限）
- [ ] 添加用户确认流程（首次使用某个权限时弹窗确认）
- [ ] 实现权限审计日志（记录所有权限检查的结果）

## 7. Notes & Reflection

**卡住的地方：**

<!-- 记录你卡住的地方和解决方案 -->

**学到的关键点：**

<!-- Decorator 模式在权限系统中的应用 -->

**可复用的代码：**

<!-- 权限系统是 GitTributary 安全架构的基础 -->
