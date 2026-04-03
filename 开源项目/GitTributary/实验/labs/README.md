# GitTributary 实验手册

> 通过 17 个渐进式实验，从零构建 GitTributary 的核心技术栈。

---

## 实验总览

### Phase 1：Rust 基础与 Serde

| Lab | 名称 | 前置 | 耗时 | 核心知识点 |
|-----|------|------|------|-----------|
| [1.1](Lab-1.1-插件Manifest解析器.md) | 插件 Manifest 解析器 | — | 2-3 天 | Serde Deserialize、目录遍历 |
| [1.2](Lab-1.2-自定义错误类型.md) | 自定义错误类型 | 1.1 | 1-2 天 | thiserror、错误序列化 |
| [1.3](Lab-1.3-Trait实现Capability接口.md) | Trait 实现 Capability 接口 | 1.1, 1.2 | 2-3 天 | trait、trait object、泛型 vs dyn |

### Phase 2：Tauri 项目骨架

| Lab | 名称 | 前置 | 耗时 | 核心知识点 |
|-----|------|------|------|-----------|
| [2.1](Lab-2.1-Tauri-Hello-World与IPC双向通信.md) | Tauri IPC 双向通信 | — | 1-2 天 | invoke、emit、listen |
| [2.2](Lab-2.2-Cargo-Workspace多Crate结构.md) | Cargo Workspace 多 Crate | 1.1, 1.2, 2.1 | 1-2 天 | workspace、path 依赖 |

### Phase 3：插件系统核心

| Lab | 名称 | 前置 | 耗时 | 核心知识点 |
|-----|------|------|------|-----------|
| [3.1](Lab-3.1-Plugin-Host-Manager.md) | Plugin Host Manager | 1.1, 1.2, 1.3, 2.2 | 3-4 天 | HashMap 注册表、Box<dyn Trait> |
| [3.2](Lab-3.2-Tauri集成-前端调用插件.md) | Tauri 集成 | 2.1, 3.1 | 2-3 天 | app.manage()、State 管理 |
| [3.3](Lab-3.3-前端PluginHost与PluginRegistry.md) | 前端 PluginHost | 3.2 | 2-3 天 | TypeScript 类型、自定义 Hook |
| [3.4](Lab-3.4-AppShell布局-Manifest驱动渲染.md) | AppShell 布局 | 3.3 | 2-3 天 | 条件渲染、组合模式 |

### Phase 4：WASM 插件

| Lab | 名称 | 前置 | 耗时 | 核心知识点 |
|-----|------|------|------|-----------|
| [4.1](Lab-4.1-Extism-Hello-World.md) | Extism Hello World | 1.3 | 2-3 天 | PDK、Host SDK、wasm32 编译 |
| [4.2](Lab-4.2-Host-Function-宿主向WASM暴露能力.md) | Host Function | 4.1 | 2-3 天 | WASM 内存模型、权限校验 |
| [4.3](Lab-4.3-PHM接入WASM插件.md) | PHM 接入 WASM | 3.1, 4.1, 4.2 | 3-4 天 | Adapter 模式、统一 dispatch |

### Phase 5：前后端联动

| Lab | 名称 | 前置 | 耗时 | 核心知识点 |
|-----|------|------|------|-----------|
| [5.1](Lab-5.1-完整的插件CRUD流程.md) | 完整 CRUD 流程 | 3.2, 3.4, 4.3 | 3-4 天 | 端到端链路、错误传播 |
| [5.2](Lab-5.2-事件推送-后端驱动前端更新.md) | 事件推送 | 2.1, 5.1 | 2-3 天 | 异步 command、进度事件 |
| [5.3](Lab-5.3-命令面板.md) | 命令面板 | 3.3, 3.4 | 2-3 天 | 键盘事件、模态框、过滤 |

### Phase 6：专项功能

| Lab | 名称 | 前置 | 耗时 | 核心知识点 |
|-----|------|------|------|-----------|
| [6.1](Lab-6.1-Git操作封装.md) | Git 操作封装 | 1.3, 2.2 | 3-5 天 | git2 crate、临时仓库测试 |
| [6.2](Lab-6.2-文件系统监听与防抖.md) | 文件监听 + 防抖 | 5.2 | 2-3 天 | notify crate、防抖/节流 |
| [6.3](Lab-6.3-权限系统雏形.md) | 权限系统 | 1.3, 4.2 | 3-4 天 | 声明式权限、Decorator 模式 |

---

## 依赖关系

```
Phase 1 (Rust 基础)
  ├── Lab 1.1  Manifest 解析器 ──────────────────────┐
  ├── Lab 1.2  自定义错误类型 ───────────────────┐   │
  └── Lab 1.3  Trait Capability ─────────────┐   │   │
                                              │   │   │
Phase 2 (Tauri 骨架)                          │   │   │
  ├── Lab 2.1  Tauri IPC 双向通信 ────────┐   │   │   │
  └── Lab 2.2  Cargo Workspace ───────┐   │   │   │   │
                                      │   │   │   │   │
Phase 3 (插件核心)                      │   │   │   │   │
  ├── Lab 3.1  Plugin Host Manager ◄───┼───┼───┼───┘   │
  ├── Lab 3.2  Tauri 集成 ◄────────────┼───┼───┘       │
  ├── Lab 3.3  前端 PluginHost ◄───────┼───┘           │
  └── Lab 3.4  AppShell 布局 ◄─────────┘               │
                                                       │
Phase 4 (WASM)                                        │
  ├── Lab 4.1  Extism Hello World                      │
  ├── Lab 4.2  Host Function                           │
  └── Lab 4.3  PHM 接入 WASM ◄────────────────────────┘

Phase 5 (联动)
  ├── Lab 5.1  完整 CRUD 流程
  ├── Lab 5.2  事件推送
  └── Lab 5.3  命令面板

Phase 6 (专项，可并行)
  ├── Lab 6.1  Git 操作封装
  ├── Lab 6.2  文件监听 + 防抖
  └── Lab 6.3  权限系统
```

---

## 建议节奏

| 节奏 | 每周 Lab 数 | 总周期 | 适合情况 |
|------|-----------|--------|---------|
| 快速 | 3-4 个 | 4-5 周 | 全职投入 |
| 正常 | 2 个 | 8-10 周 | 业余时间 |
| 慢速 | 1 个 | 16 周 | 碎片时间 |

**核心原则：做完一个再开始下一个。**

---

## 每个 Lab 的结构

每个 Lab 报告包含以下固定章节：

1. **Objectives** — 清单式的可检查目标
2. **Background** — 为什么要做，关键概念是什么
3. **Procedure** — 分步骤的实现指南（含完整代码）
4. **Deliverables** — 产出物清单
5. **Evaluation Criteria** — 验收标准
6. **Extensions** — 可选的进阶挑战
7. **Notes & Reflection** — 记录卡住的地方、学到的关键点、可复用代码

---

## 完成后你会获得什么

- 一个**可运行的** GitTributary 原型（不是文档，是代码）
- 对 Tauri + Rust + React 技术栈的**实战掌控力**
- 17 份实验笔记，记录你的技术成长轨迹
- 直接复用到 GitTributary 主项目的核心代码
