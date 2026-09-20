# 什么是模型评测

<span class="status understood">已理解</span>

模型评测的目的不是得到一个“看起来很专业的分数”，而是回答三个问题：

1. 这个模型现在能完成什么任务？
2. 在什么条件下会失败？
3. 下一次应该优化模型、数据、策略、工具还是交互？

## 从单轮模型到 Agent

普通模型评测经常是：

```text
Prompt → Response → Score
```

但 Agent 会在多个时刻观察环境、保存状态、选择行动、调用工具，并根据返回结果继续执行：

```text
Observation → Strategy → Action → Tool Return → State Update → Next Observation
```

所以 Agent 评测的对象不是孤立模型，而是：

```text
模型 + Prompt + Agent Harness + 工具 + 记忆 + 运行环境 + 交互策略
```

## 多模态评测还多了什么

当输入包含视频、图像、音频和文字时，需要额外检查：

- 模型是否真正看见了关键视觉事件；
- 是否把相似动作误判为目标事件；
- 是否在正确的时间响应；
- 输出是否与画面证据一致；
- 视频、语音、工具和前端链路是否带来额外延迟；
- 持续观察时，模型是否知道什么时候应该保持安静。

## 两类评测

| 类型 | 回答的问题 | 使用方式 |
| --- | --- | --- |
| Capability Eval | 当前能力上限在哪里 | 保留困难题，观察能力是否增长 |
| Regression Eval | 原来会做的任务是否仍然稳定 | 版本更新后持续回归，防止旧能力退化 |

## 下一步

继续阅读 [Agent 与 Harness](agent-and-harness.md)，理解为什么 Agent 需要运行框架，以及评测系统为什么还需要另一套 Harness。

