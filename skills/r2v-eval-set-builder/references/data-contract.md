Warning: fs was declared with const; use let for reassignable variables.
# 数据格式与检查

## 规划与成品分开

仅做规划或尚未取得图片时，使用独立的规划表，记录题号、计划语言/风格/镜头、`planned_ref_count`、选图需求、候选考察点和待确认事项。计划图数不等于已取得图数，不填写假refs路径、假校验值或假授权记录。

以下JSONL格式与检查器用于已经开始实质制作的题目。`draft`表示已配素材题目的未定稿检查，不是没有图片的规划模式。规划表无需通过题目检查器；在图片、题干和证据实际就绪后再转为正式记录。

## 交付结构

推荐生成如下项目输出，名称可由团队调整：

```text
dataset/
  cases.jsonl
  images/
    R2V-001/
      ref01.jpg
  evaluation.xlsx
  coverage-and-review.md
  checks.json
```

Excel是交付视图，JSONL保留完整信息。不要在单个“备注”单元格中丢失多图顺序、来源或改写记录。若环境无法生成Excel，如实提供CSV/JSONL与图片包，不假称已生成或已上传。

主表至少包含：题号、题名、prompt、语言、时长、题目类型、主体题材、能力类别、镜头数、描述风格、长度标签、语义复杂度、参考图数量、图序及用途、来源、主考察点、成功/失败标准、复核和上传状态。

题集只允许图片输入。若题干要求输出环境声或简短对白，需标明这是输出约束而不是音频输入，且不能据此声称已经覆盖独立音频输入专项。

## 每题字段

| 字段 | 类型及内容 |
|---|---|
| id / title / prompt | 非空字符串；id唯一；prompt为最终模型输入正文 |
| input_modalities | 固定为`["text", "image"]` |
| language / duration_s | zh或en / 默认10 |
| task_type / style | 自然任务说明 / user_casual、natural_detailed、structured、ultra_long |
| shots | 1-15整数；1为单镜头 |
| subject_tags | 主体标签ID列表，首项为主要题材 |
| primary_capability | 一个能力标签ID |
| secondary_capabilities | 0-2个不重复的辅助能力ID |
| capability_evidence | 对象：每个能力ID对应prompt中的原文片段 |
| complexity | simple / medium / hard，依明确能力数判断 |
| word_count / word_count_method | 非负整数 / 实际分词方法说明，中文项目内保持一致 |
| length_label | tiny / short / long |
| main_test | 主考察点 |
| pass_criteria / failure_signals | 非空字符串列表，可观察表现 |
| daily_human / handwriting | 布尔值，分别标记日常人物场景和书写专项 |
| timeline | 连续覆盖0-10秒的数组；每项有start_s、end_s、shot、event |
| refs | 实际参考图数组，数量按此数组计算 |
| source | 来源记录，见下文 |
| rewrite | 改写记录，见下文 |
| boundary | is_boundary布尔值；超过10张必须为true并有type任务说明 |
| review | 真实复核记录，见下文 |
| upload | 上传验收记录，见下文 |
| supplemental_tags | 可选字符串列表，不替代正式类别 |

`refs`每项要求：

- `index`：从1连续编号；`asset_id`：项目内稳定的素材编号。
- `path`：相对素材根目录的图片路径，不得逃逸到目录外。
- `sha256`：实际文件的SHA-256，64位十六进制。
- `source_url`：可追溯的来源页面或文件；`source_repo`：公开仓库URL。
- `role`：在本题中的参考用途。
- `license_note`：本次使用依据及必要归属信息。
- `rights_status`：`cleared`或`pending`；完成题目需要cleared，不能仅因有开源代码许可证就填cleared。
- `visual_check`：passed或pending；由实际查看图片的复核者填写。

用户明确提供的授权素材可以用`user-provided:`加本地来源记录编号表示source_url，并将source_repo留空；不能以此伪装没有来源的网络图片。

`source`：

- `type`：arena / past_hardcase / user_prompt / business / handwritten。
- `origin_url`：有真实外部来源时填写；纯原创手写可以为空。
- `adaptation`：如何改编、是否原创；非空。
- 真实用户prompt需要来源链接，不能把口语风格伪装成真实用户数据。

`rewrite`：

- 未改写：`{"used": false}`。
- 已改写：used为true，method为product_skill/public_template/custom_skill，提供source、version、before、after、evidence。
- after必须与最终prompt相同；before不能与after相同。evidence是实际使用方式记录，不得含敏感日志。

`review`：

- `status`：passed / pending / failed。
- `reviewer`：真实角色标识即可，不要求个人姓名。
- `mode`：independent_agent / independent_human / single_agent。
- `notes`：具体审核理由。
- 以下五项逐项记录passed/pending/failed：ten_second_feasibility、reference_alignment、prompt_label_alignment、language_naturalness、semantic_dedup。

`upload`：

- `status`：not_requested / pending / blocked / verified。
- `target`：目标工作表说明；`verified_by`：实际验收角色。
- `remote_images`：数组，每项有index、asset_id、location。
- verified仅在全部图片实际回填并复查后使用。location可以是远端文件位置或可定位的表格附件位置，不得为本地路径。

## 检查器行为

`scripts/validate_cases.py`接受JSON数组或逐行JSON对象。默认配置位于assets/default_config.json，可通过`--config`指定副本。

- `--check-config`：检查配额内部是否自洽。
- `--stage draft`：检查已有条目结构、素材文件、证据和时间安排；不要求完整题数或复核通过。
- `--stage pilot`：要求12题，覆盖两种语言、超长、书写、1-3/4-6/7-10/11-18/大于18张档位，并要求逐题复核通过。
- `--stage full`：要求150题和完整交叉配额，逐题复核通过。
- `--require-uploaded`：额外要求每题上传验收映射完整；用户要求线上交付时必须加此检查。
- `--report`：将检查结果写入指定JSON文件；不自动改写题目。

图片检查包括路径、扩展名、文件头、非空文件、字节校验和同题字节重复；不替代完整图片解码、视觉去重或内容检查。

机械检查不能识别全部拼贴、重编码重复图、虚构的授权记录、假的复核声明、无意义长文或不自然英文。不得把“检查器通过”写成“实际内容已经全面正确”。

修改总题数时，必须同时修改languages、shot_modes、styles、reference_counts及相关小样/边界/覆盖配置；检查器不会静默重新分配。首次调整请先运行--check-config。

中文分词器不属于本包依赖：由执行环境提供，需真实运行并记录版本。检查器只核对报告词数与长度标签、中文方法的一致性；英文词数规则为拉丁字母词（允许内部撇号）。

## 启动请求示例

```text
使用 r2v-eval-set-builder。
读取本包默认配置，制作仅含文本和参考图输入的10秒视频评测题。
先完成12题带真实图片的小样并报告检查结果，待我确认后扩展至150题。
暂时只交付本地文件，不上传到任何在线表格。
```

```text
使用 r2v-eval-set-builder，按我提供的项目配置制作题集。
先读取我的正式标签文档，对照本包默认口径，报告差异。
图片只从公开GitHub项目及我明确提供的授权素材中选择。
```

纯Markdown版读者可以使用以上完整规则手动组织和复核数据；需要运行检查工具时使用ZIP版本。支持SKILL.md目录的执行环境可读取整个skill目录，其他环境可把完整Markdown作为任务规范，不承诺所有产品都有自动安装入口。
