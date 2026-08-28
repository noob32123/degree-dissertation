# 三位模拟审稿意见最终修订核对表（2026-08-27）

本表为作者/编辑侧内部核对材料，不是面向任一审稿人的正式回复信。原审稿属于投稿前模拟审稿，没有编辑决定，因此不虚构 “Major Revision” 或逐审稿人决定措辞。状态采用 `VERIFIED_DONE`、`PARTIAL_EVIDENCE` 和 `AUTHOR_INPUT_NEEDED`。

## 总体状态

- 稿件、代码、结果和自动生成表已同步；清稿与标红稿均成功编译为 25 页。
- 主结果链、敏感性分析和预览失配实验已改用完全相同的名义持出轨迹命名空间；验证文件确认名义行逐项相等。
- 20 项单元测试全部通过；主验证和扩展验证均为 `status: passed`。
- 投稿就绪度为 `draft_with_placeholders`。唯一明确的作者待填项是代码/数据永久归档标识。

## Major Concerns

| 审稿意见 | 状态 | 实际修改与核验证据 |
|---|---|---|
| R1-M1、R2-M1、R3-M1：结果入口与论文主结果链不闭合 | VERIFIED_DONE | 固定核心入口 `reviewer_experiments` 和第二轮入口 `extended_revision`；主评价 22,400 行、敏感性 12,800 行、预览失配 8,000 行、扩展消融 12,000 行；哈希、行数、检查点和有限值均写入验证 JSON。 |
| R1-M2、R3-M2：成本方程与实现不一致 | VERIFIED_DONE | 正文改为实现中的逐动作线性归一化成本、六资源转移、15 个任务输入及其单位/尺度；删除未实现的正切屏障和服务器成本；固定种子转移审计和边界单测证明预览与实际执行逐坐标一致。 |
| R1-M3、R2-M2、R3-M3：无法识别中心化的独立作用 | VERIFIED_DONE | 新增未中心化 full-action Q 和无 bootstrap 的 immediate-advantage 对照。名义场景中 full-action Q 相对 DQN 为 -1.29 [-1.98,-0.73]，CBAD 相对 full-action Q 为 -0.07 [-0.32,0.20]。正文据此明确：证据支持全动作 Bellman 监督，不支持中心化为必要因素。标题同步改为 “Counterfactual Full-Action Bellman Supervision”。 |
| R1-M4、R2-M4、R3-M4：独立训练种子不足、多重性不清 | VERIFIED_DONE | 每种学习目标使用 20 个独立训练种子 800–819；先在种子内平均 20 条共享轨迹，再以种子为推断单位；报告配对 bootstrap、精确双侧符号检验、Holm 校正和留一范围。另以独立种子 bootstrap 丢弃配对信息，只有 nominal 与 energy-limited 区间排除 0，正文明确全场景推断依赖预设共同随机数设计。 |
| R2-M3：模拟器自身精确预演不能代表模型失配 | PARTIAL_EVIDENCE | 保留 0.85/1.15 对称缩放的 40 个额外模型，结果在测试范围内仍有利；正文明确该实验不覆盖结构误差、动作相关误差或真实飞行模型偏差。 |
| R1-M5、R3-M5：工程约束和复合成本解释不足 | VERIFIED_DONE（解释层面） | 新增即时成本、延迟罚项、能量、时延、传输量、低能量暴露、最低能量和最大热状态分解。明确两种主要学习策略均出现零剩余能量，因此只证明软惩罚目标下的模拟器结果，不证明硬约束可部署性。 |
| R2-M5：更强 RL 与更长规划基线不足 | PARTIAL_EVIDENCE | 新增 Double DQN/Double-CBAD 配对。名义差为 -1.04 [-1.90,-0.38]，但 Holm 校正符号检验为 0.059，正文按方向性证据处理。新增 H=1/2/4/6 精确规划：平均成本 99.33/92.80/90.83/89.35，平均决策时间 0.13/0.49/4.70/41.60 ms。未覆盖 dueling、PER、distributional、MILP 或近似树搜索。 |
| R3-M5：单星、单链路、合成环境限制外部有效性 | PARTIAL_EVIDENCE | 增加完整生成器、来源表、压力范围、工程分解和预览误差实验；摘要、讨论和结论均收窄为合成软约束单星模拟器内结论。飞行遥测、硬件在环、多星多链路仍未补充。 |

## 一致性与复现核验

- `validation.json`：主验证通过；60 个主要检查点、40 个预览误差检查点；名义参考行跨三类分析完全一致。
- `extended_revision_validation.json`：120 个六目标检查点、12,000 行扩展评估、全部数值有限、检查点 SHA-256 完整。
- `fixed_transition_audit.csv`：固定种子下三动作的即时成本与六个后状态坐标均与独立实际执行一致。
- 规划深度：400 条唯一持出轨迹，每个深度先执行一条不计时预热轨迹；计时不与其他 GPU 任务并发。
- 自动表格由 CSV 生成，不手工转录统计量。
- `audit_manuscript.py`：超过 30 词句子 0，em dash 0，缺失引文 0，缺失交叉引用 0。
- 清稿与标红稿均为 25 页；日志无未解析引用、重复标签或 overfull box。去除 31 个红色标记块后，标红源稿与清稿逐字符一致（统一换行后）。

## 术语账本

| 规范术语 | 首次定义/用途 | 允许形式 |
|---|---|---|
| MD-CBAD-DQN | 方法全称宏 `\method` | 首次/正式名称使用 MD-CBAD-DQN，正文可简称 CBAD |
| standard DQN | 严格匹配的事实基线 | 句首或表首可写 Standard DQN |
| full-action Q auxiliary | 未中心化 Bellman 对照 | 不写作“去中心化 CBAD” |
| immediate-advantage auxiliary | 无 bootstrap 的即时优势对照 | 不称为完整 Bellman 对照 |
| Double DQN / Double-CBAD | online selection 与 target evaluation 解耦的配对 | 保留连字符形式 Double-CBAD |
| MPC-$H$ / planner horizon $H$ | 完美短期预报下的精确枚举规划器 | 不称为 64 步全局最优 |
| simulator-exact | 指定确定性程序内的一步相等 | 不外推为物理精确或飞行精确 |

## 主文精简与证据放置

- `core_discovery`：CBAD 与严格匹配 DQN 的五场景配对结果保留在主文。
- `qualification`：未中心化对照否定“中心化必要性”，Double 配对经校正后仅为方向性证据，均保留在主文，因为它们改变中心结论的表述。
- `alternative_inference`：独立种子 bootstrap 以一张紧凑表保留，直接限定共同随机数推断边界。
- `necessary_support`：规划深度和计算时间保留，限定与传统优化的比较范围。
- `provenance_detail`：哈希、逐行结果和模型清单留在机器可读结果与仓库，不在正文重复。
- 新增结果段均替换原有泛化表述，没有继续追加“中心化最优”“飞行可部署”或“优于一般规划”的防御性文字。

## 作者投稿前待办

- `AUTHOR_INPUT_NEEDED`：在 `Data and Code Availability` 中用作者创建的永久 DOI、版本号或不可变提交标识替换粗体占位符。
- 若目标期刊要求硬安全保证、真实任务验证或多星扩展，需新增实验；当前稿件已明确不作这些主张。
- 若后续指定具体目标期刊，再按其摘要字数、版式、AI 使用披露和数据/代码政策执行最后一轮格式化。
