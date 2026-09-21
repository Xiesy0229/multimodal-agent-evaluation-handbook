# 2026-09-22｜多模态模型每日情报

> 今日先记录 3 条与“视频理解、模型效率、评测可信度”最相关的公开更新。后续每天沿用同一结构：事实 → 影响 → 可评测问题。

## 1. Gemini 引入 Agentic Video Understanding

- 来源：[Google Blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/)
- 时间：2026-09-01
- 发生了什么：Gemini 3.7 Flash、3.6 Flash 和 3.5 Flash-Lite 可以主动决定查看视频的哪些片段、采用多高的采样率，以及使用画面、音频还是字幕。官方称在测试中最多可减少 88% token、降低 66% 成本，并提升最多 7% 的准确率。
- 对我的启发：这与 JoyAI-VL-Interaction 的“持续观察、关键时刻响应”很接近。评测时不能只问最终答案，还要测它是否找到了关键时间段、是否漏掉瞬时事件、成本是否随视频长度稳定增长。
- 可转成评测题：给定 30 分钟监控视频，要求模型定位一次不到 1 秒的异常，并记录检索时间段、采样策略、准确性和 token 消耗。

## 2. NeoMME：单塔多模态、多语言编码器

- 来源：[Hugging Face Blog](https://huggingface.co/blog/Hcompany/neomme)
- 时间：2026-09-03
- 发生了什么：H Company 发布 260M 和 800M 两个规模的 NeoMME。它不依赖单独预训练的视觉塔或因果语言模型，而是用一个双向 Transformer 同时处理文字 token 和图像 patch，并提供视觉文档检索版本。
- 对我的启发：多模态模型不只有“看图后生成文字”的 VLM，也有更适合检索、分类和重排的编码器。评测维度要根据任务变化：检索看 Recall、nDCG、延迟和索引大小，不能套用生成式问答指标。
- 可转成评测题：用同一批图文文档比较不同模型的 nDCG@10、单页编码速度、索引存储占用和跨语言查询表现。

## 3. Google 试点双盲 AI 评测

- 来源：[Google DeepMind](https://deepmind.google/blog/piloting-the-worlds-first-double-blind-ai-evaluations/)
- 时间：2026-08-27
- 发生了什么：Google 与外部机构在隐私保护环境中，把模型权重和评测题目分别保护起来，减少模型提前见到 benchmark 题目造成的污染，让外部评测更接近真实能力测量。
- 对我的启发：评测系统本身也要被评测。除了 Outcome 和 Grader，还要记录测试集是否泄露、模型是否见过题、评测方是否能复核结果。对多模态模型尤其重要，因为视频、图像和提示词数据很容易被重复使用。
- 可转成评测题：把一套隐藏的视频测试集放在模型提供方不可读取的环境中，比较公开测试集与隐藏测试集的差距，并记录数据访问审计日志。

## 今日关键词

`agentic video understanding` · `dynamic sampling` · `multimodal encoder` · `visual retrieval` · `benchmark contamination` · `double-blind evaluation`
