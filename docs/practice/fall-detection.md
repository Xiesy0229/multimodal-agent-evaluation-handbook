# 跌倒预警：一次完整多模态 Trial

<span class="status validating">正在验证</span>

## Task

当监控视频中出现真实跌倒时，在事件发生后 2 秒内发出一次明确提醒，并成功通知家属；弯腰、坐下和躺到床上不能误报。

## 测试数据设计

| 类型 | 示例 |
| --- | --- |
| 正例 | 正常行走时突然摔倒 |
| 困难正例 | 缓慢跌倒、部分遮挡、弱光、画面边缘 |
| 相似负例 | 弯腰、坐下、蹲下、躺到床上 |
| 系统异常 | 通知接口超时、TTS 失败、网络抖动 |

## 一段 Transcript

```text
00.00s  Input        开始接收监控视频流
08.40s  Observation  人体重心快速下降，出现疑似跌倒
08.45s  Policy       证据不足，误报风险较高
08.46s  Decision     Silence，继续观察 0.5 秒
08.96s  Observation  人员倒地后未起身
09.00s  Policy       置信度提高，但高风险事件需要复核
09.01s  Decision     Delegate
09.02s  Tool Call    调用动作复核模型，timeout=800ms
09.31s  Tool Return  fall=true, confidence=0.94
09.33s  Decision     Speak
09.35s  Output       “检测到人员可能摔倒，正在通知家属。”
09.38s  Tool Call    调用通知服务
09.62s  Tool Return  notification_id=7281, status=delivered
09.63s  State        alert_pending → alert_delivered
09.65s  Final        Trial 完成
```

## Outcome 检查

- Ground Truth：视频中确实发生跌倒；
- 检测延迟：09.35 − 08.40 = 0.95 秒；
- 通知状态：delivered；
- 通知次数：1；
- 错误状态：无；
- Outcome：Success。

## Grader 组合

1. Code-based：检查延迟、通知状态、重复告警；
2. Visual Grader：核对画面中是否真实跌倒；
3. Policy Grader：检查第一次 Silence 和后续 Delegate 是否合理；
4. Human Grader：评价告警内容是否清楚、及时且不过度恐慌；
5. Cost Grader：统计视觉复核、TTS 和通知服务成本。

## 如果后台复核失败

高风险情况下可采用以下 Fallback：

```text
复核超时
→ 保留“疑似”表述
→ 向家属发送需要人工确认的低风险提醒
→ 保持持续观察
→ 记录工具错误与人工升级状态
```

这不一定算完整成功，需要根据 Task 的预设成功标准标为 Partial Success 或 Failure。

