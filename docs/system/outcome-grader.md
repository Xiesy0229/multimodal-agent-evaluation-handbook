# Outcome 与 Grader

<span class="status understood">已理解</span>

## Outcome：外部世界真的发生了什么

Outcome 是 Trial 结束后的真实结果，不是模型最后说出的内容。

例如模型说“我已经通知家属”，评测系统仍然需要检查：

- 通知接口是否真实成功；
- 是否生成了通知 ID；
- 家属端状态是否变为 delivered；
- 是否在规定时间内完成；
- 是否重复通知；
- 是否通知了正确对象。

Outcome 常见状态：

| 状态 | 含义 |
| --- | --- |
| Success | 所有关键成功标准都满足 |
| Partial Success | 核心目标部分完成，但存在缺失 |
| Failure | 未完成关键目标 |
| Timeout | 超过规定时间仍未完成 |
| Aborted | 因风险、权限或人工中止 |

## Grader：如何从不同维度评分

同一个 Task 可以配置多个 Grader。

| 维度 | 问题 | 适合的 Grader |
| --- | --- | --- |
| 任务结果 | 外部状态是否真的达标 | Code-based |
| 视觉正确性 | 判断是否符合画面证据 | Human / Model-based |
| 时序与延迟 | 是否在正确时间响应 | Code-based |
| 策略质量 | Speak、Silence、Delegate 是否恰当 | Rule + Human / Model-based |
| 工具调用 | 工具、参数、权限和返回处理是否正确 | Code-based / Transcript rule |
| 安全风险 | 是否漏报、误报、越权或隐瞒不确定性 | Rule + Human |
| 交互体验 | 是否清晰、自然、不过度打扰 | Human / calibrated LLM Judge |
| 成本效率 | Token、GPU、耗时和调用次数 | Code-based |
| 稳定性 | 多次运行能否可靠复现 | Aggregate |

## 三种 Grader

### Code-based Grader

快速、便宜、可重复，适合时间戳、状态、参数、计数、延迟和成本。缺点是规则覆盖不到的正确表达可能被误判。

### Model-based Grader / LLM Judge

适合开放性内容，例如视觉忠实度、完整性和表达质量。需要用人工样本校准，不能直接当绝对真值。

### Human Grader

适合主观体验和高风险判断，最接近真实用户与专家标准，但速度慢、成本高，也需要检查评审者一致性。

## Outcome 优先，Transcript 用于诊断

能直接验证真实 Outcome 时，不要强迫 Agent 完全复刻唯一标准路径。Transcript 更适合检查效率、安全和失败原因。只要替代路径安全且真正完成任务，就可能是有效方案。

