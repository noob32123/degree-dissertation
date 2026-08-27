# 最新稿三人盲审综合报告

日期 2026-08-27

## Review setup

**Input scope**

完整 27 页最新版 PDF、对应 LaTeX 源稿、正文内嵌图表、方法和参考文献。

**Assessment boundary**

本次评审不包含独立补充材料、外部公共归档或作者回复信。原创性判断仅基于稿件自身的相关工作与参考文献，没有进行外部文献检索。

**Shared manuscript claim summary**

稿件主张，在一个完全指定的合成软约束资源耦合卫星地面调度基准中，六种 DQN 目标在五个完全耦合情景的 30 个配对比较中均优于 MPC-4。稿件将这种家族级一致性、联合统计推断和可执行证据链作为主要贡献。

**Visible evidence base**

可见证据包括完整模拟器方程、三种处理动作、六类持续资源、六个 DQN 目标、20 个模型种子块、共享持出轨迹、联合 bootstrap、Holm 校正、家族级同时上界、MPC 规划深度分析、参数敏感性、预览误差扰动和训练信息核算。

**Missing materials affecting confidence**

Data and Code Availability 仍含永久归档标识占位符。公共代码、锁定原始 CSV、检查点和验证清单未作为独立审稿材料提供。稿件也未提供任务级真实数据、遥测或硬件在环验证。

## Frozen individual reports

- Reviewer 1 强调 technical soundness 与 technical failings。完整冻结报告见 latest_blind_reviewer_1_2026-08-27_zh.md。
- Reviewer 2 强调 originality 与 scientific importance。完整冻结报告见 latest_blind_reviewer_2_2026-08-27_zh.md。
- Reviewer 3 强调 interdisciplinary readership 与 readability。完整冻结报告见 latest_blind_reviewer_3_2026-08-27_zh.md。

三份报告在相互隔离的上下文中完成。综合阶段没有把任何报告或共识提示反馈给审稿人。

## Cross-review synthesis (post-review; not shown to reviewers)

### Consensus strengths

1. 三位审稿人都认可固定模拟器内部的中心数值结论。30 个 DQN 与 MPC-4 比较的均值方向、联合种子块 bootstrap、多重性校正和同时上界构成了清楚的统计证据。
2. 三位审稿人都认可稿件对模拟器、状态、动作、训练预算、配对单位和信息量差异的披露较完整。
3. 三位审稿人都认可家族内部结论较克制。稿件没有指定一个统一最优 DQN 变体，也承认固定辅助权重不能识别 centering 与 bootstrapping 的独立作用。
4. 三位审稿人都认可作者已主动披露软约束、MPC 截断时域、DQN 推理时间未测量和运行验证缺失等边界。

### Consensus blocking concerns

没有形成至少两位审稿人共同标记为 Blocking Yes 的共识阻断项。

Reviewer 1 将比较器边界 R1-M1、时间机制识别 R1-M2 和公共证据链 R1-M4 标记为 Blocking Yes。Reviewer 2 和 Reviewer 3 将相同底层问题评为 Major、Blocking No，因为他们认为这些问题不否定固定合成基准中的狭义排序，但会阻止更广泛的 Nature-style 论证。

### Other consensus major concerns

1. **比较器前沿与计算匹配不足**

对应 R1-M1、R2-M1、R3-M2 和 R3-M3。DQN 的有效学习时域、离线训练和部署成本没有与更长时域规划、动态规划、树搜索、混合整数方法或卫星专用调度器形成匹配前沿。当前证据最严格地支持“优于所实现的 MPC-4，并在 nominal 条件下优于 MPC-6”，不足以支持一般性的 DQN 家族优越性。

2. **合成软约束基准的工程效度有限**

对应 R1-M3、R2-M2 和 R3-M1。无量纲固定权重、裁剪资源状态和软惩罚决定了主要成本排序。DQN 和 MPC-4 在全部完全耦合情景中都达到裁剪后的零能量状态，因此更低成本不能自动转换为任务可行性、安全性或部署收益。

3. **时间耦合机制尚未被独立识别**

对应 R1-M2、R2-M3 和 R3-M2。耦合系数 c 同时改变状态转移与延迟惩罚，低耦合实验还包含未重新训练的分布转移。Bandit 与规划深度结果与长时程价值解释相容，但不能排除奖励塑形、规划截断和其他状态特征造成排序。

4. **原创性和广泛科学重要性仍不足**

对应 R1-M5、R2-M1 和 R3-M3。Centered full-action 的家族内增益较小，完整支持规则并未覆盖所有情景，组件设计也不能独立识别具体机制。把主要贡献转移为“六种 DQN 都优于 MPC-4”仍不足以显示一般性的算法原理或广泛工程突破。

5. **可执行证据链尚不能由审稿人独立检查**

对应 R1-M4、R2-M4 和 R3-M4。运行命令和本地文件描述较详细，但公共永久归档尚未提供。可复现性是稿件明确列出的主要贡献，因此投稿前必须使原始种子级数据、代码、环境、检查点或重建流程、表图脚本和哈希清单可访问。

### Where emphasis differs across reviewers

- Reviewer 1 对中心结论采取最严格的技术解释，将有限时域比较器、机制混杂和缺失归档视为阻断项。
- Reviewer 2 认为固定基准中的排序可信，但 Nature-style 原创性和科学重要性不足是主要问题。
- Reviewer 3 更强调跨学科读者无法把无量纲成本差转换为任务价值，并指出缺少贯穿全文的具体决策轨迹。
- Reviewer 1 单独提出训练目标与未折扣确认终点不一致的问题 R1-M6。DQN 和 MPC 以 gamma 0.97 优化，但主要终点是未折扣 64 步总成本。该问题需要折扣率敏感性或目标一致的重新训练。

### Minor revision checklist

1. 解释均值 bootstrap 区间与种子方向符号检验回答不同问题，并报告正负种子数。对应 R1-m1、R3-m6。
2. 将训练曲线的“optimization stability”改为经验平台期，或补充 TD 误差、Q 值和异常种子诊断。对应 R1-m3、R2-m1。
3. 改善全宽缩放表、缩写和多面板纵轴的可读性。对应 R1-m2、R3-m2、R3-m5。
4. 在摘要首次解释 MPC-4、seed block 和 simultaneous upper bound。对应 R3-m1、R2-m5。
5. 让主结果视觉单元直接显示 DQN 家族范围或最差成员，减少跨页核对。对应 R3-m3。
6. 将 standard DQN 的工程分解持续限定为 representative case，不推广到全家族。对应 R2-m2。
7. 同时报告相对改进、每任务平均差异和主要组成项，帮助解释无量纲效应。对应 R2-m3。
8. 解释 24 维状态中的确定性派生或冗余坐标。对应 R2-m4。
9. 将 delayed feasibility penalty 改为更准确的 post-decision resource penalty，或明确其观测时序。对应 R3-m4。
10. 补全不完整参考文献字段。对应 R1-m4。

### Broad-interest / significance readout

当前稿件对卫星边缘计算、强化学习基准和资源耦合调度研究者具有明确的专业兴趣。固定模拟器内部的统计结果扎实，复现意识也较强。然而，跨学科重要性尚未建立。无量纲软约束成本没有映射到任务完成、安全裕量或系统设计决策，算法优势也没有经过匹配的长期优化方法与外部任务环境检验。

从 Nature-style 标准看，稿件目前更接近严谨的专业领域合成基准研究。若补充硬约束与工程标定、匹配的长时程比较、机制分离和公共归档，其科学重要性可以重新评估。

### Most important issues to resolve before a strong Nature-style case is established

1. 在相同信息条件和明确计算预算下建立更强的长时程比较器前沿，并测量 DQN 的部署时间和能耗。
2. 分别操纵状态携带、惩罚尺度、折扣率和终端代价，确定时间耦合解释何时成立。
3. 在硬能量和热约束、动作可行性与失败终止条件下验证家族排序，并报告尾部风险和失败率。
4. 用任务来源明确的效用、独立任务分布、不同接触拓扑、遥测或硬件在环数据建立工程意义。
5. 冻结并公开完整可执行归档，使独立环境能够重建中央 30 项比较、Table 5 和 Figure 1。
6. 明确论文的唯一首要原创贡献。它应是新方法、新基准或可推广经验原理之一，而不是在三种定位之间移动。

## Risk / unsupported claims

1. **支持充分**

在当前固定合成软约束模拟器和所实现比较器下，六种 DQN 目标在五个完全耦合情景中的平均总代价均低于 MPC-4。

2. **支持较弱**

DQN 家族相对于更广泛调度、规划或非 DQN 方法具有一般性优势。

3. **尚未建立**

观察到的优势由时间耦合本身产生，而不是奖励塑形、规划截断、折扣选择或状态特征共同造成。

4. **尚未建立**

无量纲成本下降代表真实卫星任务完成率、可行性、安全性或部署收益的提高。

5. **当前不可独立评估**

稿件宣称的完整可执行证据链。原因是永久公共归档尚未提供。

6. **评估范围限制**

原创性判断仅基于稿件列出的相关工作和参考文献，不构成独立的系统文献检索或优先权判定。
