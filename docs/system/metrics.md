# 指标与稳定性

<span class="status validating">正在验证</span>

## 多模态实时交互常见指标

| 指标 | 含义 |
| --- | --- |
| Event Recall | 真实事件中被成功识别的比例 |
| False Negative Rate | 漏报率 |
| False Positives / Hour | 每小时误报次数 |
| P50 / P95 Latency | 中位数与长尾响应延迟 |
| Duplicate Alert Rate | 重复告警比例 |
| Silence Accuracy | 应保持安静时正确 Silence 的比例 |
| Delegate Success Rate | 委托成功并正确接回结果的比例 |
| Tool Error Recovery | 工具失败后正确恢复的比例 |
| Visual Groundedness | 输出与画面证据一致的程度 |
| Cost per Successful Task | 每个成功任务的平均成本 |

## Pass@k

尝试 k 次后，至少成功一次的概率。适合允许多次探索、只需要得到一个可用方案的任务。

## Pass-to-the-k

连续 k 次每次都成功的概率。适合监控预警、持续计数和高可靠业务。

如果单次成功率为 75%，并且各次相互独立：

```text
连续三次都成功 = 0.75 × 0.75 × 0.75 ≈ 42%
```

这说明能力上限和运行稳定性不是同一个问题。

## 不要只看平均值

实时多模态系统还应检查：

- P95、P99 长尾延迟；
- 最困难场景表现；
- 不同光照、遮挡、机位和人群差异；
- 连续运行时的状态漂移；
- 工具超时和网络异常；
- 高风险类别的漏报。

