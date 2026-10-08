# 我如何用 Skill 辅助视频评测

我把评测过程中容易出错的方向映射、GT 覆盖、人员强度偏差、题目权重和证据表达整理成 Skill，让 Agent 在处理不同项目时沿用同一套检查方法。

## 文件结构

```text
skills/analyze-pairwise-video-evals/
├── SKILL.md
└── references/
    ├── methodology.md
    └── reporting.md
```

- [SKILL.md](https://github.com/Xiesy0229/multimodal-agent-evaluation-handbook/blob/main/skills/analyze-pairwise-video-evals/SKILL.md)：任务边界、执行流程与交付检查。
- [methodology.md](https://github.com/Xiesy0229/multimodal-agent-evaluation-handbook/blob/main/skills/analyze-pairwise-video-evals/references/methodology.md)：GT 计分、人员指标、风险信号、题目等权与敏感性分析。
- [reporting.md](https://github.com/Xiesy0229/multimodal-agent-evaluation-handbook/blob/main/skills/analyze-pairwise-video-evals/references/reporting.md)：主观报告、人员报告与 Badcase 证据表达。

这三份文件已按公开用途整理，不包含内部链接、真实人员或项目结果。仓库中的 Skill 不一定会被每个 Agent 环境自动发现，需要明确提供文件路径或按所用工具的方式加载。

## 示例任务

```text
请先完整读取 skills/analyze-pairwise-video-evals/SKILL.md，
以及其中引用的 methodology.md 与 reporting.md。

分析本轮 T2V/T2AV 成对四档盲评：
先审计模型方向、数据结构与题目对齐，再生成分维度 GT 候选。
GT 未经人工确认时，不发布正式人员剔除结论。
人工 GT 回收后，检查人员一致性及同方向评分强度偏差，
结合逐人剔除敏感性确认过滤名单，再按题目等权重算。
输出独立的人员报告、主观报告、分析明细与白盒追溯表。
未观看视频时，具体缺陷只作为待复核项。
```

## 人与 Agent 的分工

| Agent 可以辅助 | 需要人工确认 |
| --- | --- |
| 审计结构、对齐字段、筛候选 | 模型方向及评价标准 |
| 计算人员指标与结果敏感性 | GT 参考答案 |
| 按题目等权汇总四档结果 | 人员剔除与档位校准决定 |
| 按影响因素聚类、组织报告 | 视频中的实际失败现象与最终决策 |

Skill 是可复用的方法指令，不是已经交付的通用评测软件。公开版本没有项目脚本或示例数据；实质影响阈值、强败局阈值等仍需针对每轮评测明确配置。

[返回完整评测流程](pairwise-video-evaluation.md)
