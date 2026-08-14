# NoteAura 测试体系与 TDD 策略

> 记录时间: 2026-07-21  
> 项目目标: 在可行的前提下，用较前沿的测试技术建立可持续演进的 TDD 工作流。
> 时效说明: 测试工具和门禁会随源码演进;执行前以当前 `package.json`、Cargo workspace 和 CI 配置为准。

## 一句话概括

NoteAura 当前采用“快速单元测试 + 性质测试 + 真实浏览器旅程 + Rust 后端契约 + 性能预算 + 变异测试”的分层策略。覆盖率用于防止倒退，但最终追求的是用例能否真正保护用户可观察行为、边界条件、并发语义和性能契约。

## 当前引入的测试技术

| 层级 | 技术 | 在项目中的作用 |
| --- | --- | --- |
| 前端单元/组件 | Vitest 4、React Testing Library、`user-event`、`jest-dom`、jsdom | 验证纯逻辑、Hook、组件交互、加载和错误状态 |
| 前端性质测试 | fast-check 4 | 自动生成大量输入，验证路径、树结构、序列化等不变量，并缩减失败反例 |
| 前端覆盖率 | V8 coverage | 统计全局真实基线，对已细测的关键模块设置 75%~100% 的独立门槛 |
| 浏览器 E2E | Playwright 1.61 + Chromium | 运行完整 React 应用和模拟 Tauri IPC，验证跨组件用户旅程与紧凑窗口布局 |
| Rust 单元/集成 | Rust 原生测试、cargo-nextest | 验证 crate 内部逻辑和公开 API；nextest 提供更快、更稳定的并行执行 |
| Rust 性质测试 | proptest 1.11 | 随机验证 JSON、路径、Flow 文本和持久化契约，失败时自动缩减反例 |
| Rust 覆盖率 | cargo-llvm-cov | 在 CI 生成 Rust workspace 的 LCOV 报告 |
| 变异测试 | cargo-mutants | 主动改坏 Rust 实现，检查现有断言是否真能发现错误，每周执行 |
| Rust 微基准 | Criterion 0.7 | 跟踪 Flow 解析、文件夹归一化和插件协议序列化的性能分布 |
| 性能硬门禁 | 确定性 Git/附件 fixture、IPC 基准、p50/p95/max 预算、相对基线 | 同时判断“用户是否可接受”和“本次是否退化” |

## 测试策略

```text
纯函数/组件行为       -> 单元测试，作为日常最快反馈
输入空间大、有不变量 -> fast-check / proptest
跨组件、跨 IPC 旅程 -> Playwright
Rust crate 公开契约    -> 集成测试 + nextest
性能敏感链路           -> 微基准 + 确定性性能门禁
测试本身的有效性       -> 变异测试
```

这不是追求用 E2E 覆盖一切。大部分行为在更快、更精确的下层测试；E2E 只保留关键用户旅程；性质测试负责人工枚举难以穷尽的边界。

## 测试理念

1. **行为优先**: 从用户动作或公开 API 写断言，避免绑定私有实现。
2. **先复现再修复**: bug 必须先有稳定失败的回归 case，再修实现。
3. **覆盖率是下限，不是目标**: 全局门槛防倒退，关键模块用高门槛；不用排除难测页面制造虚高数字。
4. **属性比样例更接近契约**: 只要能表达不变量，就用生成式输入寻找人工没想到的反例。
5. **可确定、零容忍 flaky**: 不依赖顺序、真实时间或开发者私有环境；不用固定 `sleep`等待异步状态。
6. **Mock 只放在边界**: 主要 mock Tauri IPC、文件系统临时目录和确定性 Git fixture，不 mock 被测模块内部函数。
7. **性能也是契约**: Criterion 用于开发期趋势分析，稳定 fixture 的绝对预算和同环境基线才负责 CI 验收。

## Case 编写标准

一个重要功能完成前，至少应满足:

- 正常路径和主要失败路径都有自动化 case。
- 输入解析、路径、安全边界或状态机有边界表格或性质测试。
- 前后端 command 名和 DTO 变化有契约测试，E2E fixture 同步更新。
- 并发读取考虑成功、失败、取消/过期和乱序响应，旧响应不得覆盖新状态。
- 测试名称描述可观察行为，不复述函数实现；查询 DOM 优先用可访问角色、名称和用户可见文本。
- 测试失败应直接暴露被破坏的契约；性质测试发现的有效 regression seed 应保留。
- 性能敏感改动必须附变更前后数据，同时通过绝对预算和可比环境下的相对基线。

## TDD 日常循环

```text
Red       先写从用户行为/公开 API 出发的失败 case
Green     只实现使当前契约成立的最小改动
Refactor  消除重复和改善边界，运行快速测试集
Hardening 补失败、取消、乱序、安全输入和性质测试
Delivery  运行覆盖率、E2E；敏感链路再运行性能门禁
```

日常最快反馈:

```bash
npm run test:fast
```

该命令会同时生成 `test-reports/latest/report.md`、`report.html`、`results.json` 和分套件日志。只验证当前改动层时，使用 `npm run test:report -- --only frontend`、`--only rust,plugins` 或 `--only e2e`，避免无意义地阻塞开发。

合并前完整验证:

```bash
npm run test:all
npm run test:coverage
npm run perf:ci
```

## CI 门禁与当前状态

Pull Request 和 `main` 推送会运行前端类型检查、Vitest/性质测试/覆盖率、Rust nextest/proptest、Rust 覆盖率和 Playwright。变异测试由每周计划任务或手动触发；性能门禁有独立 workflow。

2026-07-21 本地验证快照:

- Vitest: 145/145 通过；全局 statements 27.55%、branches 27.36%、functions 27.84%、lines 27.88%。
- Playwright: 桌面和紧凑视口共 12/12 通过。
- Rust 核心 workspace 和插件 workspace 测试通过。
- 性能门禁: 4/4 gate、16/16 已采集预算通过。

## 当前边界

- Playwright 当前验证浏览器内的 React 应用与 Tauri IPC 契约，不等于真实 Tauri WebView 全链路 E2E。
- 性能报告已覆盖的指标能正常门禁，但总状态仍是 `INCOMPLETE`: 真实 WebView 端到端延迟、30 分钟资源稳定性等 20 项激进指标暂无数据。
- 全局前端覆盖率仍不高。当前策略是锁住真实基线，新增功能通过测试逐步抬高，而不是一次性用低价值 case 刷数字。

## 项目回链

- [完整测试策略与 TDD 工作流](https://github.com/ChenXuRiYue/NoteAura/blob/main/doc/%E6%9E%B6%E6%9E%84/%E6%B5%8B%E8%AF%95%E7%AD%96%E7%95%A5%E4%B8%8ETDD%E5%B7%A5%E4%BD%9C%E6%B5%81.md)
- [性能目标与测试规范](https://github.com/ChenXuRiYue/NoteAura/blob/main/doc/%E6%9E%B6%E6%9E%84/%E6%80%A7%E8%83%BD%E7%9B%AE%E6%A0%87%E4%B8%8E%E6%B5%8B%E8%AF%95%E8%A7%84%E8%8C%83.md)
- [性能评价体系](https://github.com/ChenXuRiYue/NoteAura/blob/main/performance/README.md)
- [Vitest 配置](https://github.com/ChenXuRiYue/NoteAura/blob/main/vitest.config.ts) / [Playwright 配置](https://github.com/ChenXuRiYue/NoteAura/blob/main/playwright.config.ts)
- [测试 CI](https://github.com/ChenXuRiYue/NoteAura/blob/main/.github/workflows/test.yml) / [Rust 变异测试](https://github.com/ChenXuRiYue/NoteAura/blob/main/.github/workflows/mutation-testing.yml)
