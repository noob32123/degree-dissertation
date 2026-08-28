# 润色后论文三审综合报告

## Review setup

- **Input scope** 完整润色稿、生成表格、本地结果包、检查点、验证元数据与编译 PDF。
- **Assessment boundary** 本报告属于投稿前 Nature-style 模拟预审，不是编辑决定，也不是作者回复。
- **Shared manuscript claim summary** 五个完全耦合情景中，六个 DQN 目标形成 30 个目标与情景组合，其均值均低于相应 MPC-4 均值。家族内部差异较小且依赖情景。
- **Visible evidence base** 20 个独立训练种子，每个种子 20 条共享测试轨迹，配对 bootstrap、Holm 调整、独立种子敏感性分析、四种规划深度、参数与预览误差扰动、训练诊断和动作比例。
- **Missing materials affecting confidence** 永久公开存档编号、任务遥测或硬件在环验证、第二个调度任务、硬约束测试、匹配的长时域基线和 DQN 推理时间。

## Reviewer 1

技术可靠性与技术缺陷权重。完整冻结报告见 [Reviewer 1](post_polish_reviewer_1_2026-08-27.md)。

## Reviewer 2

原创性与科学重要性权重。完整冻结报告见 [Reviewer 2](post_polish_reviewer_2_2026-08-27.md)。

## Reviewer 3

跨学科读者与非专业可读性权重。完整冻结报告见 [Reviewer 3](post_polish_reviewer_3_2026-08-27.md)。

## Cross-review synthesis (post-review; not shown to reviewers)

### Consensus strengths

三位审稿人一致认可以下优点。

1. 模拟器状态、转移、奖励、动作负载和随机生成过程披露充分。
2. 20 个独立模型种子、共享测试轨迹和种子级推断明显强于常见的小种子实验。
3. 论文已正确区分 DQN 家族级结果与较小的变体内部差异，没有宣称唯一最佳 DQN 变体。
4. 信息预算、训练时间、规划深度、软约束和未匹配推理时间均得到明确说明。
5. 本地证据包总体完整，公式、检查点、结果文件、表格生成和转移审计之间具有较强可追溯性。

### Consensus blocking concerns

#### S-B1 家族级优势缺少直接推断

对应 R1-M1、R2-M3 和 R3-M3，三项均为 Blocking Yes。

标题级主张依赖 30 个 DQN 均值全部低于 MPC-4，但论文没有直接报告 DQN 减 MPC-4 的效应量和不确定性。30 个单元共享目标、种子和轨迹，不能视为 30 次独立重复。现有详细推断主要用于较次要的 DQN 家族内部比较。

**关闭条件** 明确定义家族对 MPC 的 estimand，利用共享轨迹及模型种子层级进行分层 bootstrap 或其他合理的重复训练推断。报告最小优势边际及置信区间，并说明跨目标和情景的多重性处理。如果不补分析，标题和结论只能写成“观测均值的一致排序”。

#### S-B2 比较基线不足以支撑较广优势

对应 R1-M2、R2-M2 和 R3-M2，三项均为 Blocking Yes。

当前非 DQN 对照主要由即时策略、手工阈值、contextual bandit 和最多六步的精确滚动规划构成。DQN 训练使用 38,400 次交互，而 MPC-6 仅观察 64 步任务中的未来六步，且没有终端值。现有实验没有覆盖可扩展长时域规划、动态规划、混合整数方法、卫星专用调度器或其他强序列学习方法。

**关闭条件** 至少增加一个经过调参的可扩展长时域对照，并定义共同的信息、预测、调参与计算预算。同步报告 DQN 推理时间。如果无法补充，主张必须严格限定为本文实现的短时域对照集合。

### Other consensus major concerns

#### S-M1 软约束破坏了工程调度解释

对应 R1-M3、R1-M4、R2-M4 和 R3-M1。R3 将其判为 Blocking Yes，其余报告判为 Major but non-blocking。

能量只是经过裁剪的记账状态，达到零后动作仍可继续执行，且进一步能量缺口被裁剪丢失。Table 13 显示主要学习策略在所有展示情景中均达到零能量。相反，thermal-stress 的最大热状态仍明显低于 0.78 的惩罚阈值。固定效用权重、共同生成器和缺乏独立任务也限制了卫星工程意义。

**关闭条件** 首选增加 action masking、能量耗尽终止、保留负债的能量账本或约束控制，并重新验证家族排序。若不新增实验，标题和摘要必须明确写成 synthetic soft-constraint benchmark，不能暗示可执行的卫星调度优势。

#### S-M2 贡献身份和广泛重要性仍不稳定

对应 R2-M1 和 R3-M5，也与 R1 对原创性的总体判断一致。

论文的主要数值发现来自整个 DQN 家族，而不是 centered full-action 方法。图形摘要、方法主体和多个后续分析却仍以 centered full-action 为中心。其相对标准 DQN 的改进不足 1\%，完整规则只支持三个情景，centering 和 bootstrapping 也没有被充分隔离。因此，读者仍难判断主要贡献是新方法、家族级经验规律，还是可复现基准。

**关闭条件** 明确选择一个主贡献。若选择家族级基准，应重做主视觉和开篇层级，并补强基线与推断。若选择新方法，应提供单独调参和更严格的因子控制，并在独立任务上验证。

### Where emphasis differs across reviewers

- Reviewer 1 额外强调 uniform preview scaling 不能代表结构性模型误差，见 R1-M5。
- Reviewer 3 认为“long-horizon value learning”仍只是解释而非被识别机制，见 R3-M4。
- Reviewer 1 将证据包版本不一致判为 Major，见 R1-M6。Reviewer 3 将相同问题判为 Minor，见 R3-m1。
- 对软约束问题，Reviewer 3 判断其阻断卫星工程主张。Reviewer 1 和 Reviewer 2 认为它不阻断纯合成基准结论，但必须阻止操作性外推。

### Minor revision checklist

1. 补充永久代码和数据存档编号，见 R1-m1、R2-m3、R3-m2。
2. 更新验证元数据中的 `paper/source.tex` 哈希，并清理陈旧表格，见 R1-M6、R3-m1。
3. 增加 DQN 同硬件推理时间，或删除部署效率暗示，见 R2-m2、R3-m3。
4. 为 Figure 11 增加种子级不确定性和比较策略，见 R1-m2、R2-m4、R3-m4。
5. 在摘要中说明成本为固定未拟合权重产生的无量纲合成目标，见 R2-m1、R3-m5。
6. 提前解释 soft constraint 的含义及能量归零后仍执行动作，见 R1-m3。
7. 将“exact planner”统一写为“exact H-step receding-horizon planner”，见 R3-m6。
8. 为 DQN 对 MPC 的大差异增加资源和惩罚分解，而非只分解 centered full-action 对标准 DQN，见 R3-m5。

### Broad-interest / significance readout

当前稿件已经是一篇透明、扎实且具有复用价值的 specialist synthetic benchmark study。三位审稿人均认为，其对强化学习、卫星边缘计算和受约束调度研究者具有明确兴趣。尚未建立的部分是跨出该专业圈的科学重要性。缺口主要来自比较基线、家族级统计推断、硬可行性和外部任务验证，而不是英语表达或表格数量。

### Most important issues to resolve before a strong Nature-style case is established

1. 为 DQN 家族对 MPC 的主要主张补充直接不确定性分析。
2. 增加强长时域基线，或把标题与结论严格限定到现有实现。
3. 解决零能量后继续执行的问题，或将论文明确定位为软约束合成控制基准。
4. 在“家族级经验规律”“新 centered 方法”“基准资源”之间选定唯一主贡献。
5. 修复哈希和陈旧生成表格，形成一个可验证的最终证据状态。

## Risk / unsupported claims

- 在完成 S-B1 前，标题中的 `Advantage` 仅由均值排序支持，不具备直接家族级推断。
- 在完成 S-B2 前，不能将结果概括为 DQN 普遍优于 planning 或现代卫星调度方法。
- “long-horizon value learning”尚未通过独立改变 transition carryover、penalty scale 和 discount factor 得到机制识别。
- 当前结果不支持 hard-constrained deployability、flight validity 或实际任务价值。
- `quality-computation frontier` 仅描述 MPC 内部的 horizon-cost-runtime 曲线，不是 DQN 与 MPC 的匹配部署比较。
- 当前验证元数据没有绑定最终润色稿，且工作区存在与主结果状态不一致的陈旧固定策略表格。
