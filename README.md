# 多模态 Agent 评测学习手册

这是一个面向初学者、持续生长的个人学习知识库，用来梳理：

- 模型评测到底在评什么；
- Agent 与普通模型有什么区别；
- Benchmark、Task、Trial、Transcript、Outcome、Grader 如何连接；
- Speak、Silence、Delegate 等策略如何被记录和评分；
- 如何从零搭建一套最小可用的多模态 Agent 评测系统。

内容首先服务于个人学习和复盘，也公开分享给有相同需要的人。它不代表任何公司的内部 SOP，也不把学习研究包装成真实项目经历。

## 我的评测方法与 Skill

除了学习笔记，这里也整理我用于 T2V/T2AV 成对视频评测的通用方法：从数据审计和人工 GT，到人员可靠性、评分强度偏差、题目等权统计与 Badcase 证据分析。

- [我如何开展成对视频评测](docs/practice/pairwise-video-evaluation.md)
- [我如何用 Skill 辅助评测](docs/practice/evaluation-skill.md)
- [可复用的 GSB Skill](skills/analyze-pairwise-video-evals/SKILL.md)

公开材料保留评测方法与流程，已移除内部人员、系统链接、项目版本及真实数据；Skill 是方法指令，不是完整自动化程序。

## 本地预览

```bash
python -m pip install -r requirements.txt
mkdocs serve
```

## 构建

```bash
mkdocs build --strict
```

