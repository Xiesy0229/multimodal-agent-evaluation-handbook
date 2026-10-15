# R2V Eval Set Builder

用于辅助构建和预检参考图生成视频（R2V）的评测题集，是 R2V Arena 评测项目中的题集工作流组件。

## 能力

- 按评测目标生成、改编和复核“文本 + 静态参考图”案例，并组织标签、考察依据、素材来源与复核记录。
- 检查任务描述在目标时长内的可执行性，提示动作、镜头切换、对话与观察窗口等约束。
- 按配置校验题量、语言、单镜头/多镜头、风格及参考图数量等覆盖配额。
- 用 Python 校验器检查配置、数据结构、素材引用与文件完整性，并支持先跑小样再扩充题集。
- 保留来源、改写和授权信息，便于后续人工复核与追溯。

## 边界

这是题集构建与结构预检工具，不会默认调用视频生成模型、自动判定生成视频质量或替代人工语义/视觉审核。校验通过不等于题目语义正确、素材授权完备或模型效果达标。默认配额是本项目可调整的配置，不是行业通用标准。

## 使用

先读 [SKILL.md](SKILL.md)，随后按需查看 [分类与配额](references/taxonomy-and-quotas.md)、[生成与复核](references/generation-and-review.md)、[素材交付](references/assets-and-delivery.md) 和 [数据契约](references/data-contract.md)。

本地校验示例：

```bash
python scripts/validate_cases.py --check-config assets/default_config.json
python scripts/test_validate_cases.py
```

[返回 R2V Arena 项目说明](../../docs/practice/r2v-arena.md)
