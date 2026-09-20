# 初学者学习路线

<span class="status validating">正在验证</span>

如果你刚开始接触模型评测，不需要一次记住所有术语。建议沿着“先理解对象，再理解过程，最后动手搭建”的顺序学习。

## 第一阶段：知道评测在解决什么问题

1. 阅读[什么是模型评测](foundations/model-evaluation.md)；
2. 区分普通模型和 Agent；
3. 理解为什么不能只给最终回答打分；
4. 能用自己的话解释 Task、Trial、Transcript、Outcome 和 Grader。

完成标志：你能解释“模型说自己成功了，为什么不代表任务真的成功”。

## 第二阶段：看懂 Agent 的执行过程

1. 阅读[总体结构](system/overview.md)；
2. 学习 [Transcript](system/transcript.md) 的记录字段；
3. 理解 [Strategy / Policy](system/strategy-actions.md)；
4. 分清 `Speak / Silence / Delegate`；
5. 理解工具返回、状态更新和 Fallback。

完成标志：你能复盘一次多模态 Agent 为什么成功或失败。

## 第三阶段：学会定义“成功”

1. 阅读 [Outcome 与 Grader](system/outcome-grader.md)；
2. 把主观的“效果不错”拆成可验证指标；
3. 区分代码评分、模型评分和人工评分；
4. 理解漏报、误报、延迟、成本和稳定性之间的权衡。

完成标志：你能为一个视频理解任务写出成功标准和评分表。

## 第四阶段：搭建最小评测

1. 完成[跌倒预警案例](practice/fall-detection.md)；
2. 按照[最小评测搭建指南](practice/build-minimum-eval.md)准备 10–20 条真实任务；
3. 每条任务重复运行至少 3 次；
4. 保存 Transcript、Outcome 和评分结果；
5. 输出 3 个 Bad Case 和下一轮优化建议。

完成标志：你拥有一套能重复运行、能解释问题、能比较版本的评测闭环。

## 学习原则

!!! tip "先用真实问题，再补术语"
    遇到不懂的词，先问它在真实任务中解决什么问题。不要为了背概念而背概念。

!!! warning "不要把公开研究写成亲历项目"
    学习笔记可以展示分析能力，但需要明确资料来源、个人推断和真实实践的边界。

