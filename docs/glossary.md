# 术语表

<span class="status validating">持续补充</span>

| 术语 | 中文理解 | 关联页面 |
| --- | --- | --- |
| Agent | 会持续观察、决策、行动并检查结果的系统 | [Agent 与 Harness](foundations/agent-and-harness.md) |
| Agent Harness | 让 Agent 能接收输入、调用工具和维护状态的运行框架 | [Agent 与 Harness](foundations/agent-and-harness.md) |
| Eval Harness | 准备、运行、记录、评分和汇总评测的基础设施 | [总体结构](system/overview.md) |
| Benchmark | 一整套任务、数据、环境、成功标准和评分协议 | [总体结构](system/overview.md) |
| Task | 一项有明确输入和成功标准的测试任务 | [总体结构](system/overview.md) |
| Trial | 同一 Task 的一次独立试跑 | [总体结构](system/overview.md) |
| Transcript | 一次 Trial 的完整执行轨迹 | [Transcript](system/transcript.md) |
| Observation | Agent 从当前多模态输入中提取的事实 | [Transcript](system/transcript.md) |
| Strategy / Policy | 根据任务、证据、状态和风险选择下一步行动的策略层 | [Strategy](system/strategy-actions.md) |
| Speak | 主动输出文本、语音、告警或解释 | [Strategy](system/strategy-actions.md) |
| Silence / Silent | 暂不输出并继续观察 | [Strategy](system/strategy-actions.md) |
| Delegate | 委托预先配置的工具、模型或子 Agent | [Strategy](system/strategy-actions.md) |
| Tool Call | 对工具或后台能力发起调用 | [Transcript](system/transcript.md) |
| Tool Return | 工具返回的数据、状态或错误 | [Transcript](system/transcript.md) |
| State | Agent 内部记忆和外部环境的当前状态 | [Transcript](system/transcript.md) |
| Fallback | 主路径失败后的重试、降级、转人工或安全拒绝 | [Strategy](system/strategy-actions.md) |
| Outcome | Task 结束后的真实外部结果 | [Outcome 与 Grader](system/outcome-grader.md) |
| Grader | 检查某个评测维度的评分逻辑 | [Outcome 与 Grader](system/outcome-grader.md) |
| LLM Judge | 使用语言模型评价开放性结果的 Model-based Grader | [Outcome 与 Grader](system/outcome-grader.md) |
| Pass@k | k 次尝试中至少成功一次的概率 | [指标](system/metrics.md) |
| Pass-to-the-k | 连续 k 次全部成功的概率 | [指标](system/metrics.md) |
| Capability Eval | 测试当前能力上限 | [模型评测](foundations/model-evaluation.md) |
| Regression Eval | 检查原有能力是否退化 | [模型评测](foundations/model-evaluation.md) |
| Bad Case | 能帮助定位问题和推动优化的典型失败案例 | [最小评测](practice/build-minimum-eval.md) |

