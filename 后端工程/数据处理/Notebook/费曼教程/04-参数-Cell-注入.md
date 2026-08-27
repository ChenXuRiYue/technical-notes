# 📌 参数 Cell 怎样把一次实验变成多次运行

急减速规则需要每天换日期，也可能按车型调整阈值。如果把日期和阈值散落在多个 Cell 中，每次调度都要修改源码。参数 Cell 把这些变化集中在一个明确入口中。

学完本篇，你应该能从默认参数和 `Arguments` 推导最终变量值，并说明为什么 Notebook 内不需要 `argparse`。

## 📄 第一个 Cell 只定义默认参数

在 Notebook 开发页面中，把第一个 Cell 写成：

```python
event_date = "2026-08-12"
threshold_kmh = 20
window_seconds = 2
```

然后在页面中把它标记为“调度参数”并保存。这个 Cell 的责任只有变量定义：

- 默认值让交互运行可以立即开始。
- 变量名形成离线作业的参数接口。
- 后续 Cell 只读取这些变量，不重复写死日期和阈值。

不要在参数 Cell 中读取数据、写文件或改变外部系统。离线执行会在它之后插入覆盖 Cell；参数 Cell 带副作用时，会让“先执行默认值，再覆盖参数”的过程产生多余行为。

Scala Notebook 使用 `val date = "..."` 定义参数。本文后续只展示 Python。

## 📄 Arguments 描述要覆盖哪些变量

在 AI 数据开发的 Notebook 作业中，`Arguments` 使用：

```text
-p event_date 2026-08-13 -p threshold_kmh 25 -p window_seconds 2
```

`-p` 是平台识别参数名和值的格式。它不会要求 Notebook 自己读取 `sys.argv`。平台在运行时把参数转成 Python 变量赋值。

集团 skill 的 YAML 示例还出现过结构化 `parameters` 字段。UI 的 `Arguments` 最终如何映射到底层字段，应以目标空间最新插件 Schema 和实际 Flow 源码为准；Notebook 内部仍遵循“参数 Cell 后插入覆盖 Cell”的产品机制。

## 📄 运行时会多出一个 Cell

作业执行前的文件：

```python
# Cell 1：被标记为调度参数
event_date = "2026-08-12"
threshold_kmh = 20
window_seconds = 2
```

平台根据 `Arguments` 在它下面生成一个新 Cell，效果相当于：

```python
# Parameters：运行时注入
event_date = "2026-08-13"
threshold_kmh = 25
window_seconds = 2
```

后续 Cell 再运行：

```python
print(event_date, threshold_kmh, window_seconds)
```

输出：

```text
2026-08-13 25 2
```

Python 从上到下执行赋值，后一次绑定覆盖前一次绑定。默认值负责交互可运行，注入值负责本次调度。最终执行后的 Notebook 可以作为作业输出查看，用于确认平台实际插入了什么。

## 📄 先预测四种情况

假设默认值为 `event_date="2026-08-12"`、`threshold_kmh=20`：

| 条件 | 最终日期 | 最终阈值 | 原因 |
| --- | --- | ---: | --- |
| 没有 Arguments | `2026-08-12` | 20 | 只有默认参数 Cell |
| `-p threshold_kmh 25` | `2026-08-12` | 25 | 只覆盖同名阈值变量 |
| 后续 Cell 又执行 `threshold_kmh = 10` | `2026-08-12` | 10 | 更晚的源码再次覆盖注入值 |
| 参数名误写成 `threshold` | `2026-08-12` | 20 | 新变量没有替换代码实际读取的名字 |

第三种情况说明：调度参数定义之后，业务 Cell 不应再次给同名参数赋值。第四种情况说明：参数名属于作业接口，改名时需要同步更新 Arguments。

## 📄 值的类型需要验证

命令行文本看起来没有类型，但 Notebook 代码会对变量做数值、字符串或布尔运算。日期通常按字符串处理：

```python
event_date = "2026-08-13"
```

阈值通常按数值处理：

```python
threshold_kmh = 25
```

不要只根据 `Arguments` 文本猜测平台最终生成的 Python 表达式。第一次配置新类型时，运行一个最小作业并查看最终 Notebook：

```python
print(type(event_date), repr(event_date))
print(type(threshold_kmh), repr(threshold_kmh))
```

确认输出后再让参数进入 SQL 或路径拼接。这样可以提前发现字符串引号、数字转换和布尔值表示问题。

## 📄 参数与作业版本是两条变化轴

同一份作业快照可以用不同参数运行：

```text
代码版本 V3 + 日期 2026-08-12 + 阈值 20
代码版本 V3 + 日期 2026-08-13 + 阈值 25
```

修改 Notebook 逻辑会产生另一份代码版本：

```text
代码版本 V4 + 日期 2026-08-13 + 阈值 25
```

因此复现结果至少要记录代码/工作流 revision 与实际参数。只记录日期，无法区分同一天由不同规则产生的候选清单。

## 📄 纸面模拟

不用平台，拿纸写四个 Cell：

```python
# Cell A：默认参数
threshold_kmh = 20
```

```python
# Cell B：平台注入
threshold_kmh = 25
```

```python
# Cell C：业务逻辑
speed_drop_kmh = 23
```

```python
# Cell D：输出
print(speed_drop_kmh >= threshold_kmh)
```

预测输出为 `False`。删除 Cell B 后输出为 `True`。如果你能只根据执行顺序推出两次结果，就已经掌握参数注入的核心机制。

## 📄 费曼检查

向一位熟悉 Java `main(String[] args)` 的同事解释：

> 为什么作业界面写了 `-p threshold_kmh 25`，Notebook 代码里却没有参数解析器？默认值为什么仍然需要保留？

答案应该出现“平台解析 Arguments”“插入赋值 Cell”“默认值支持交互运行”三步。若把 `-p` 解释成 Python 自带参数，回到[运行时会多出一个 Cell](#-运行时会多出一个-cell)。

---

[上一篇：把 Notebook 发布为离线作业](03-从-Notebook-到离线工作流.md) | [返回教程目录](README.md) | [下一篇：动手实验与生产排查](05-动手实验与生产排查.md)

## 🌳 生长思考

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 💭 反复绊脚

> ⚠️ 此板块由用户本人填写，AI 创建笔记时只保留占位，不填充具体内容。

## 🗺️ 修订记录

- 2026-08-14：按默认 Cell、注入 Cell、业务 Cell 的执行顺序解释 Notebook 参数化。

## 🛠️ 实践经历

## ⚙️ prompt

## 调研

- [集团：参数配置文档](https://mi.feishu.cn/wiki/BksjwYKrNiSa3MkFwSzcLwKjn8g)
- [集团：AI数据开发-Notebook作业](https://mi.feishu.cn/wiki/NzoRwUNj5iwhomknpk3c3YFMnee)
