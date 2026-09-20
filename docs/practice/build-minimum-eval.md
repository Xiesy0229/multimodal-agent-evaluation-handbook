# 从零搭建最小评测系统

<span class="status todo">待补充实践数据</span>

初学者不需要先做几百条任务。第一版可以从 10–20 条真实、多样、判断标准清晰的 Task 开始。

## 第一步：选择明确场景

例如：跌倒预警、实时计数、视频翻译、直播讲解或操作指导。一次只选择一个场景。

## 第二步：写 Task Spec

每条任务至少包含：

```yaml
task_id: fall-001
input: video/fall-001.mp4
instruction: 发现真实跌倒时在 2 秒内提醒并通知家属
success_criteria:
  - event_detected: true
  - alert_latency_ms: <= 2000
  - notification_status: delivered
  - duplicate_alerts: 0
risk_level: high
```

## 第三步：准备正例与负例

- 正例：典型事件；
- 困难正例：遮挡、弱光、缓慢变化；
- 相似负例：视觉上相似但不应触发；
- 系统异常：工具超时、接口失败、权限不足。

## 第四步：定义 Transcript Schema

必须包含时间戳、输入引用、Observation、Policy、Action、Tool Call、Tool Return、State Change、Fallback 和 Final Status。

## 第五步：编写 Grader

- 代码规则检查确定性 Outcome；
- 人工或校准后的模型检查视觉和表达质量；
- 单独检查风险、成本、策略和稳定性。

## 第六步：重复运行

每条 Task 至少运行 3 个 Trial。高风险任务需要更多重复和不同随机种子。

## 第七步：形成 Bad Case

不要只写“失败”。按原因分类：

| 分类 | 例子 |
| --- | --- |
| Perception | 没有看见关键动作 |
| Understanding | 看见了但理解错误 |
| Policy | 应 Speak 时选择了 Silence |
| Tool | Delegate 的对象或参数错误 |
| State | 重复告警或状态没有更新 |
| UX | 内容正确但表达造成恐慌 |
| Infrastructure | 视频流、网络、TTS 或日志链路失败 |

## 第八步：回归验证

每次优化后重新运行旧 Task，确认修复新问题时没有破坏原有能力。

## 第一版交付物

- 10–20 条 Task；
- 每条 3 个 Trial；
- 完整 Transcript；
- Outcome 结果表；
- 多维 Grader；
- 3–5 个典型 Bad Case；
- 一份优化建议；
- 一轮 Regression Eval。

