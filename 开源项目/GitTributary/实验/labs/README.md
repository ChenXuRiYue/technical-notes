# GitTributary Lab Manual

> 通过 17 个渐进式实验，以工程课程的方式构建 GitTributary 的核心技术栈。

---

## 1. Course Framing

这套实验按“MIT 风格工程实验课”的要求重构为以下原则：

- **以能力为中心**：每个 Lab 必须对应明确、可观察、可验收的学习成果。
- **以证据为中心**：完成 Lab 的依据不是“我感觉做完了”，而是代码、测试、演示记录与反思。
- **以系统构建为中心**：所有 Lab 都指向同一条主线，即逐步得到一个可运行、可维护的 GitTributary 原型。
- **以工程纪律为中心**：接口命名、测试覆盖、错误处理、提交说明和实验记录，都是课程产出的一部分。

## 2. Expected Background

在开始本手册前，学生应具备以下基础：

- 能使用 `cargo`、`rustup`、`npm` / `pnpm` 完成基础开发工作流
- 对 Rust 所有权、借用、`Result`、`trait` 有基本概念
- 能阅读 React + TypeScript 基础组件代码
- 能在 macOS 或 Linux 上完成 Tauri 开发环境配置

如果上述能力不稳定，建议先完成一个热身任务：

- 用 Rust 读取一个 JSON 文件并输出结构化结果
- 用 React 写一个包含列表、按钮、状态切换的页面
- 用 `cargo test` 和前端包管理器完成一次最小工程运行

---

## 3. Lab Sequence

### Phase 1: Rust Foundations and Serde

| Lab | 名称 | 前置 | 估计耗时 | 核心能力 |
|-----|------|------|---------|---------|
| [1.1](Lab-1.1-插件Manifest解析器.md) | 插件 Manifest 解析器 | — | 2-3 天 | Serde 反序列化、目录扫描、基础测试 |
| [1.2](Lab-1.2-自定义错误类型.md) | 自定义错误类型 | 1.1 | 1-2 天 | thiserror、错误建模、错误输出 |
| [1.3](Lab-1.3-Trait实现Capability接口.md) | Trait 实现 Capability 接口 | 1.1, 1.2 | 2-3 天 | trait 设计、trait object、依赖抽象 |

### Phase 2: Tauri Project Skeleton

| Lab | 名称 | 前置 | 估计耗时 | 核心能力 |
|-----|------|------|---------|---------|
| [2.1](Lab-2.1-Tauri-Hello-World与IPC双向通信.md) | Tauri IPC 双向通信 | — | 1-2 天 | `invoke`、`emit`、事件监听 |
| [2.2](Lab-2.2-Cargo-Workspace多Crate结构.md) | Cargo Workspace 多 Crate | 1.1, 1.2, 2.1 | 1-2 天 | workspace 拆分、crate 边界、依赖组织 |

### Phase 3: Plugin System Core

| Lab | 名称 | 前置 | 估计耗时 | 核心能力 |
|-----|------|------|---------|---------|
| [3.1](Lab-3.1-Plugin-Host-Manager.md) | Plugin Host Manager | 1.1, 1.2, 1.3, 2.2 | 3-4 天 | 注册表设计、调度模型、单元测试 |
| [3.2](Lab-3.2-Tauri集成-前端调用插件.md) | Tauri 集成 | 2.1, 3.1 | 2-3 天 | 状态注入、命令桥接、前后端契约 |
| [3.3](Lab-3.3-前端PluginHost与PluginRegistry.md) | 前端 PluginHost | 3.2 | 2-3 天 | 类型建模、前端注册表、自定义 Hook |
| [3.4](Lab-3.4-AppShell布局-Manifest驱动渲染.md) | AppShell 布局 | 3.3 | 2-3 天 | Manifest 驱动 UI、布局组合、条件渲染 |

### Phase 4: WASM Plugins

| Lab | 名称 | 前置 | 估计耗时 | 核心能力 |
|-----|------|------|---------|---------|
| [4.1](Lab-4.1-Extism-Hello-World.md) | Extism Hello World | 1.3 | 2-3 天 | 插件 ABI、WASM 构建、宿主调用 |
| [4.2](Lab-4.2-Host-Function-宿主向WASM暴露能力.md) | Host Function | 4.1 | 2-3 天 | Host function、内存模型、权限边界 |
| [4.3](Lab-4.3-PHM接入WASM插件.md) | PHM 接入 WASM | 3.1, 4.1, 4.2 | 3-4 天 | 统一插件接口、适配器模式、端到端调度 |

### Phase 5: Frontend and Backend Integration

| Lab | 名称 | 前置 | 估计耗时 | 核心能力 |
|-----|------|------|---------|---------|
| [5.1](Lab-5.1-完整的插件CRUD流程.md) | 完整 CRUD 流程 | 3.2, 3.4, 4.3 | 3-4 天 | 端到端链路、错误传播、联调验证 |
| [5.2](Lab-5.2-事件推送-后端驱动前端更新.md) | 事件推送 | 2.1, 5.1 | 2-3 天 | 异步任务、进度事件、UI 更新 |
| [5.3](Lab-5.3-命令面板.md) | 命令面板 | 3.3, 3.4 | 2-3 天 | 命令建模、交互设计、过滤与快捷键 |

### Phase 6: Focused Engineering Topics

| Lab | 名称 | 前置 | 估计耗时 | 核心能力 |
|-----|------|------|---------|---------|
| [6.1](Lab-6.1-Git操作封装.md) | Git 操作封装 | 1.3, 2.2 | 3-5 天 | `git2`、仓库测试、领域接口抽象 |
| [6.2](Lab-6.2-文件系统监听与防抖.md) | 文件监听 + 防抖 | 5.2 | 2-3 天 | `notify`、事件收敛、前后端同步 |
| [6.3](Lab-6.3-权限系统雏形.md) | 权限系统 | 1.3, 4.2 | 3-4 天 | 权限模型、装饰器模式、最小授权原则 |

---

## 4. Dependency Graph

```text
Phase 1
  1.1 Manifest Parser
  1.2 Error Types
  1.3 Capability Traits

Phase 2
  2.1 Tauri IPC
  2.2 Cargo Workspace

Phase 3
  3.1 Plugin Host Manager
  3.2 Tauri Integration
  3.3 Frontend Plugin Registry
  3.4 AppShell

Phase 4
  4.1 Extism Hello World
  4.2 Host Functions
  4.3 PHM + WASM

Phase 5
  5.1 End-to-End CRUD
  5.2 Event Push
  5.3 Command Palette

Phase 6
  6.1 Git Operations
  6.2 File Watching
  6.3 Permissions
```

建议遵守前置关系，不要跳过基础 Lab 直接做后续系统集成。

---

## 5. Standard Workflow for Every Lab

每个 Lab 都应按以下流程执行：

1. **Preparation**
   阅读实验目标，确认前置能力、工具链和仓库状态。
2. **Implementation**
   按 Procedure 实现最小可运行版本，不要一开始追求“最终形态”。
3. **Verification**
   运行文档要求的测试、示例命令和手工验证步骤。
4. **Reflection**
   记录设计选择、踩坑点、尚未解决的限制。
5. **Submission**
   提交代码、测试证据和实验反思。

---

## 6. What a High-Quality Submission Looks Like

每个 Lab 的提交至少应包含以下证据：

- 代码实现：功能完整，能被他人复现
- 自动化验证：`cargo test`、前端测试或手工验证记录
- 简短实验记录：说明你改了什么、验证了什么、仍有什么限制
- 反思：至少写下一个设计选择及其权衡

推荐提交格式：

- `README` 或实验记录中写出运行命令
- 给出测试通过的摘要
- 说明边界条件是否覆盖
- 说明后续可改进之处

---

## 7. Assessment Rubric

所有 Lab 默认使用同一套四维评分标准，每项 0-4 分，总计 16 分：

| 维度 | 4 分 | 3 分 | 2 分 | 1 分 |
|------|------|------|------|------|
| Correctness | 功能完整且边界情况处理合理 | 主路径正确，少量边界未覆盖 | 只能跑通演示路径 | 核心功能不成立 |
| Code Quality | 命名清晰，模块边界合理，可维护 | 结构基本清楚，局部欠打磨 | 耦合偏高或重复较多 | 结构混乱，难以复用 |
| Verification | 测试充分，验证证据完整 | 有测试或验证，但覆盖一般 | 仅手工验证 | 几乎无验证 |
| Reflection | 能说明设计取舍与失败模式 | 有简短总结 | 反思流于表面 | 无反思 |

通过线建议为 11/16。若 Correctness 低于 2 分，则该 Lab 不建议判定为通过。

---

## 8. Engineering Norms

本课程要求的工程纪律如下：

- 所有示例代码都应尽量做到“复制后仅需最小改动即可运行”
- 文档中的路径、crate 名称、类型名必须前后一致
- 如果示例是伪代码，必须显式标注为“伪代码”
- 所有实验至少包含一种自动化验证方式
- 所有错误处理实验都应给出一个失败案例
- 所有系统集成实验都应明确数据流入口、出口和观察点

---

## 9. Recommended Pace

| 节奏 | 每周 Lab 数 | 总周期 | 适合情况 |
|------|-------------|--------|---------|
| 快速 | 3-4 个 | 4-5 周 | 全职投入、已有 Rust 背景 |
| 常规 | 2 个 | 8-10 周 | 兼顾工作或其他课程 |
| 慢速 | 1 个 | 16 周 | 边学边做、以理解为优先 |

**原则：先完成一个可验证的 Lab，再开启下一个。**

---

## 10. Standard Lab Structure

现在每个 Lab 应尽量包含以下部分：

1. **Learning Objectives**
2. **Why This Lab Matters**
3. **Preparation**
4. **Procedure**
5. **Deliverables**
6. **Assessment and Rubric**
7. **Common Failure Modes**
8. **Extensions**
9. **Notes and Reflection**

如需重写旧 Lab，请优先参照 [_Lab-Template-MIT.md](_Lab-Template-MIT.md)。

---

## 11. Final Outcome

完成全部实验后，你应获得：

- 一个可运行的 GitTributary 原型
- 一套贯穿 Rust、Tauri、React、WASM 的工程实践路径
- 一组可复用的核心模块，而不是仅有文档草稿
- 一份足以支撑求职、答辩或内部分享的工程实验档案
