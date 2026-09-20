# 评测系统总体结构

<span class="status understood">已理解</span>

这张纵向图展示了多模态 Agent 评测从准备到迭代的完整主链路。每一个节点都可以在本站单独搜索。

```mermaid
flowchart TD
    EH["1. Eval Harness<br/>加载配置、准备环境、调度运行"]
    BM["2. Benchmark<br/>任务集合、数据、成功标准与评分协议"]
    TK["3. Task<br/>一个明确的多模态任务"]
    RS["4. Environment Reset<br/>恢复视频、工具、数据库和初始状态"]
    TL["5. Trial<br/>同一 Task 的一次独立试跑"]
    AH["6. Agent Harness<br/>输入、记忆、策略、工具与状态循环"]
    TS["7. Transcript<br/>记录观察、决策、行动、返回和状态变化"]
    OC["8. Outcome<br/>检查外部真实结果是否达标"]
    GR["9. Graders<br/>结果、过程、质量、风险、成本与体验"]
    AG["10. Aggregate<br/>跨 Trial 汇总成功率与稳定性"]
    BC["11. Bad Case Analysis<br/>定位模型、数据、策略、工具或交互问题"]
    RG["12. Regression Eval<br/>优化后重新运行并防止能力退化"]

    EH --> BM --> TK --> RS --> TL --> AH --> TS --> OC --> GR --> AG --> BC --> RG
    RG --> TK
```

## 每层分别负责什么

| 层级 | 输入 | 主要工作 | 输出 |
| --- | --- | --- | --- |
| Benchmark | 产品目标与真实风险 | 组织任务、数据与规则 | 一套可复用测试包 |
| Task | 一个具体场景 | 定义输入和成功标准 | 可执行任务 |
| Trial | Task 与初始环境 | 独立运行一次 Agent | Transcript 与最终状态 |
| Transcript | 运行中的所有事件 | 保存可审查证据 | 完整执行轨迹 |
| Outcome | 最终外部状态 | 判断任务是否真的完成 | 成功、部分成功或失败 |
| Grader | Outcome 与 Transcript | 按多个维度评分 | 单项分数与解释 |
| Aggregate | 多个 Trial 的结果 | 统计稳定性和版本差异 | 报告与 Bad Case |

## 为什么一个 Task 要运行多个 Trial

Agent 具有随机性。同一个输入可能因为采样、工具延迟、上下文或策略选择产生不同结果。一次成功只能说明“这次成功了”，不能证明系统稳定。

下一步可以深入阅读 [Transcript](transcript.md)，查看一次 Trial 内部究竟记录什么。

