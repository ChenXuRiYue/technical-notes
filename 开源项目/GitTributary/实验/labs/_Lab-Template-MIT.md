# Lab Template for GitTributary

> 用于将单个实验整理为“可教学、可执行、可评分”的工程实验文档。

## Header

- Lab 编号与标题
- 所属 Phase
- 预计耗时
- 前置实验
- 建议提交形式

## 1. Learning Objectives

用 3-5 条可观察的结果描述学习目标。优先使用以下动词：

- design
- implement
- verify
- compare
- refactor

避免写成空泛目标，例如“理解某某技术”。

## 2. Why This Lab Matters

解释这个实验在整条系统主线中的位置：

- 它为后续哪些实验提供基础
- 如果跳过它，系统会缺失什么能力
- 学生将第一次接触哪些关键工程概念

## 3. Preparation

至少写清楚以下内容：

- 需要安装的工具链
- 需要先完成的前置实验
- 需要阅读的接口或模块
- 开始前应执行的环境检查命令

示例：

```bash
rustc --version
cargo --version
pnpm --version
```

## 4. Procedure

要求：

- 步骤粒度适中，每一步都应有明确产出
- 区分“可直接复制的代码”和“需要学生补全的练习”
- 如果给出伪代码，必须显式写明“伪代码”
- 所有路径、crate 名称、类型名称必须保持一致

推荐写法：

- Step 1: 建立最小骨架
- Step 2: 实现核心数据结构
- Step 3: 接入错误处理
- Step 4: 编写测试
- Step 5: 运行验证

## 5. Deliverables

交付物必须具体：

- 文件路径
- 代码模块
- 测试文件
- 运行截图或日志摘要
- 简短实验记录

## 6. Assessment and Rubric

至少从以下维度给出通过标准：

- Correctness
- Code Quality
- Verification
- Reflection

如果有额外要求，可以增加：

- API Design
- UI Clarity
- Error Handling

## 7. Common Failure Modes

至少列出 3 个常见错误：

- 工具链或环境问题
- 类型或接口不匹配
- 运行时边界条件

每个错误都应给一个排查方向。

## 8. Extensions

扩展题应满足：

- 不影响主线通过
- 能延展设计深度
- 能鼓励比较不同实现方案

## 9. Notes and Reflection

要求学生至少记录：

- 一个最重要的设计决策
- 一个失败案例或调试过程
- 一个未来重构方向

## Review Checklist

发布前，用下面的清单自查：

- 文档中的示例代码是否基本可运行
- 是否存在与正文矛盾的命名
- 是否写清了验证命令
- 是否给出了失败路径
- 是否说明了该 Lab 在课程主线中的角色
