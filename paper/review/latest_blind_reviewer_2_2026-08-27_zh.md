以下为冻结的 Reviewer 2 独立报告。

## Overall assessment

稿件建立了一个透明度较高的合成卫星地面调度基准，并在该基准内证明六种 DQN 目标的平均总代价均低于所实现的 MPC-4。20 个模型种子块、共享测试轨迹、联合 bootstrap、多重性校正和最不利上界共同构成了较严谨的内部统计证据。因此，若结论被严格限定为“在这一固定的软约束合成基准中，六种 DQN 实现均优于 MPC-4”，该结果具有可信度。

主要问题出现在原创性和科学重要性层面。当前的大效应主要来自 DQN 与一个有限规划深度基线之间的比较。稿件尚未证明这一差异代表新的算法认识，而不是自定义代价结构、软资源惩罚和有限规划视野共同产生的基准现象。中心化全动作目标的增益仅约 0.5% 至 1.66%，且作者明确承认当前组件比较不能分离中心化、bootstrap 和辅助损失尺度的作用。由此，论文在严谨基准研究层面有价值，但目前不足以建立 Nature-style 的广泛原创性和科学重要性。

评审覆盖冻结 PDF 全部 27 页、最终排版中的逐页正文、方程、表格数值、图表文本与图注，以及全部 25 条参考文献。未提供独立补充材料或公共数据代码档案。当前查看环境未能逐像素确认图像色彩和线型，因此本报告不提出相关视觉缺陷。

## Who would be interested and why

最直接的读者包括卫星边缘计算和任务调度研究者、资源耦合马尔可夫决策过程研究者，以及关注强化学习可重复比较和多重性控制的算法研究者。工程读者可能对三个处理路径、六类持续资源和有限视野规划边界感兴趣。更广泛的控制、运筹和跨学科读者是否会受到影响，取决于作者能否证明结果超越当前自定义模拟器和单一比较器体系。

## Major strengths

1. 模拟器定义较完整。任务生成、三个动作、24 维状态、六类资源转移、即时成本和延迟惩罚均有明确方程。

2. 作者清楚区分真实交互次数与模型生成的动作结果数量，并承认相等的真实交互预算不等于相等的信息或计算预算。

3. 统计分析针对中心结论进行了直接设计。联合种子块 bootstrap 保留 30 个比较之间的相关性，并同时报告个别区间、Holm 校正和全族单侧上界。

4. 稿件主动披露多个边界，包括模拟器并非飞行数据拟合、资源仅为软约束状态、MPC 只对截断视野目标精确、DQN 推理时间未测量，以及组件对照不能完成因素识别。这种限定有助于判断证据边界。

5. 结果没有强行指定一个始终最优的 DQN 目标，而是诚实呈现族内差异较小且依赖场景。

## Major Concerns

### R2-M1

**Severity**

Major

**Blocking**

No

**Axis**

Originality and scientific importance

**Claim pointer**

标题和摘要中的 DQN-family advantage；Introduction 的第二项与第三项贡献；Results 7.1 和 7.3；Discussion 与 Conclusion 的家族级优势表述。

**Evidence pointer**

PDF 第 3 至 4 页的 Table 1；第 14 页的比较器定义；第 16 至 21 页的 Tables 4、5 和 10；第 25 页 Future work。

**Concern**

中心证据只证明六种 DQN 实现优于 MPC-4。更深规划仅在 nominal 条件下测试到六步，仍未覆盖 64 步问题，也没有计算预算匹配的规划器、动态规划、混合整数方法、可扩展树搜索或卫星特定调度方法。DQN 推理时间和能耗也未测量。稿件自身在 Future work 中承认这些比较尚未完成。

与此同时，中心化全动作方法相对标准 DQN 的改进很小，并且只在五个完全耦合场景中的三个达到完整支持规则。由于不同辅助损失没有独立调节权重和尺度，当前实验不能确定中心化或 bootstrap 的原创贡献。论文因而从算法创新退回为一个特定 DQN 族相对于短视野规划器的基准结果。

**Why it matters**

Nature-style 的原创性需要改变对方法、机制或工程能力的认识。一个自定义模拟器中相对于单一有限视野基线的排序，即使统计上稳定，也不足以证明具有广泛算法意义的 DQN 家族优势。

**Resolution test**

在所有完全耦合场景中加入经过合理调节且信息条件明确的强比较器，并报告随规划深度、计算预算和决策延迟变化的完整性能前沿。DQN 推理应在同一部署路径上计时。若广泛优势不能成立，标题、摘要和结论应明确收缩为针对该模拟器和特定 MPC-4 实现的观察，不再将其表述为一般性的 DQN 家族贡献。

### R2-M2

**Severity**

Major

**Blocking**

No

**Axis**

Scientific importance and technical soundness

**Claim pointer**

稿件将基准定位为资源耦合卫星地面调度问题，并将其描述为后续 operational validation 的 rigorous foundation。

**Evidence pointer**

PDF 第 5 至 9 页的 Eqs. 4、10、12 和 13 及 Table 3；第 21 页 Table 11；第 24 至 25 页 Discussion、Future work 和 Conclusion。

**Concern**

工程结论完全依赖固定的无量纲代价权重、人工惩罚阈值和裁剪后的软资源状态。能量达到零既不屏蔽动作，也不终止任务，裁剪还丢失了实际能量缺口的大小。Table 11 显示 DQN 和 MPC-4 在所有完全耦合场景中都达到零能量状态，而 DQN 的主要总代价优势来自较低的延迟惩罚。由此，排序可能强烈依赖惩罚系数、阈值和裁剪规则，而不是可执行任务中的资源可行性。

现有敏感性实验只改变少数生成参数，并没有系统改变效用权重、硬约束、终止条件、失败代价或任务拓扑。单卫星、单接触结构和同一生成器下的持出轨迹也不能建立部署尺度的重要性。

**Why it matters**

卫星调度的工程价值取决于可行性、安全边界、最坏情况和任务效用，而不仅是一个软惩罚总和的均值。当两类方法都耗尽裁剪能量时，更低的人工惩罚不能自动转化为更可靠或更可部署的调度策略。

**Resolution test**

至少应在硬能量与热约束、动作可行性屏蔽、终止失败条件和多组效用权重下重新评估排序。需要报告失败率、尾部总代价、阈值超限持续时间和最坏轨迹，而不仅是均值。更有说服力的证据应包括任务来源明确的效用、独立任务分布、不同接触拓扑，或硬件与遥测支持的参数范围。

### R2-M3

**Severity**

Major

**Blocking**

No

**Axis**

Mechanism evidence and claim moderation

**Claim pointer**

Introduction 提出的长期价值问题；Discussion 关于 learned values capturing persistent consequences 的解释；关于 shared sequential value-learning formulation dominated target design effects 的表述。

**Evidence pointer**

PDF 第 9 页 Eqs. 12 和 13；第 14 页 Seven evaluation regimes；第 17 至 18 页 coupling controls；第 21 页规划深度结果；第 24 至 25 页 Discussion 和 Future work。

**Concern**

当前实验支持时间依赖解释，但不能识别产生优势的机制。耦合系数 \(c\) 同时改变状态转移和延迟惩罚尺度，因此静态与 reduced-coupling 条件不是单一机制干预。模型又只在 \(c=1\) 上训练，低耦合结果同时包含动力学变化、目标变化和分布外迁移。上下文 bandit 与逐渐加深的 MPC 结果表明长期信息可能重要，但不能排除 DQN 主要利用时间、相位或特定惩罚结构的替代解释。

**Why it matters**

如果时间耦合是科学解释，而不只是结果描述，就需要区分状态记忆、惩罚尺度、折扣、训练分布和规划视野的独立作用。否则，稿件只能报告排序，不能解释为何这一排序出现或何时会消失。

**Resolution test**

分别操纵状态转移耦合和惩罚尺度，并在各条件下重新训练。独立改变折扣率、绝对时间与相位输入、任务周期性和规划视野。报告状态条件化动作选择和失败轨迹分析。只有当排序在这些可辨别干预下呈现预期变化时，才能保留当前机制表述。

### R2-M4

**Severity**

Major

**Blocking**

No

**Axis**

Reproducibility and data-resource quality

**Claim pointer**

Introduction 第四项贡献；Reproducible result entry point；Discussion 对可执行证据链的表述；Data and Code Availability。

**Evidence pointer**

PDF 第 3 页、第 16 页和第 25 页。Data and Code Availability 仍含有 “AUTHOR ARCHIVE IDENTIFIER TO BE INSERTED BEFORE SUBMISSION”。

**Concern**

可重复证据链是稿件宣称的主要贡献之一，但评审包没有提供公共档案。读者目前无法独立检查锁定的原始 CSV、种子级差值、训练 checkpoint、结果生成脚本、环境测试和验证哈希。稿件详细描述了本地命令和文件结构，但描述本身不能替代可获取的研究对象。

**Why it matters**

全部统计结论均由内部生成文件汇总。若原始种子级数据和代码不可访问，外部读者无法验证联合 bootstrap、模型解析、轨迹配对或表格生成是否与描述一致，也无法实际使用所谓的可重复平台。

**Resolution test**

在进一步评价可重复性主张前，应提供永久公共档案标识符。档案需包含运行环境、精确版本、原始种子级结果、配对键、代码、配置、checkpoint 或可重建 checkpoint 的流程、表图脚本和验证清单。按照稿件给出的入口命令，应能从锁定数据重建所有中心表格与 Figure 1。

## Minor Comments

### R2-m1

**Severity**

Minor

**Axis**

Claim moderation

**Affected element**

Results 7.4 的优化稳定性表述。

**Evidence pointer**

PDF 第 22 页 Figure 8 及其后正文。

**Issue**

训练总代价、能量、延迟和惩罚曲线进入平台区，只能表明这些训练期观测量经验上趋稳。它们不能单独证明 Q 值估计、Bellman 误差或策略优化稳定。

**Required correction**

将 “evidence of empirical optimization stability” 收缩为训练期指标的平台化描述，或补充 TD 误差、Q 值尺度、策略变化率及异常种子诊断。

### R2-m2

**Severity**

Minor

**Axis**

Claim moderation

**Affected element**

Table 11 和相应的 family-planner gap 解释。

**Evidence pointer**

PDF 第 21 页 Table 11 及其后正文。

**Issue**

工程分解只比较 standard DQN 与 MPC-4，却用于解释家族与规划器之间的差距。Standard DQN 可以作为示例成员，但不能代表六个目标的全部资源使用方式。

**Required correction**

持续使用 representative case 的限定语，避免把该分解推广至整个 DQN 家族。若要作家族结论，应提供六个目标的资源结果或至少报告其范围。

### R2-m3

**Severity**

Minor

**Axis**

Writing clarity

**Affected element**

无量纲总代价及效应量解释。

**Evidence pointer**

PDF 第 1 页摘要；第 5 页 Eq. 4；第 18 页 Table 5；第 25 页 Conclusion。

**Issue**

最不利差值 \(-5.92\) 和 simultaneous upper bound \(-5.03\) 统计上清楚，但非专业读者无法判断其任务尺度意义。成本由不同量纲量经人工权重组合，绝对差值缺乏直观基准。

**Required correction**

同时报告相对改进、主要组成项贡献和每任务平均差异，并明确这些数值不代表物理单位或经济效用。

### R2-m4

**Severity**

Minor

**Axis**

Reproducibility and writing clarity

**Affected element**

24 维状态字典。

**Evidence pointer**

PDF 第 6 页 Table 2；第 8 至 9 页状态与动作负载定义。

**Issue**

若干状态变量看起来可由其他变量和固定速率推导，例如传输时间、数据量、热量和工作量之间存在确定关系。稿件没有解释这些冗余坐标为何保留，以及它们是否影响学习难度或比较公平性。

**Required correction**

标明哪些坐标是确定性派生量，并解释保留它们的工程或学习理由。可增加去除冗余输入的局部敏感性检查，或明确该选择只属于基准定义。

### R2-m5

**Severity**

Minor

**Axis**

Readability for nonspecialists

**Affected element**

摘要、Related Work 和方法部分的算法术语。

**Evidence pointer**

PDF 第 1 至 4 页和第 9 至 12 页。

**Issue**

full-action target、centered advantage、factual target、seed block 和 simultaneous upper bound 对非强化学习读者较密集。各项都有技术定义，但缺少一句式的直观解释，跨学科读者很难把它们与卫星调度决策联系起来。

**Required correction**

在摘要后或方法开头增加简短的非专业解释，说明训练时额外知道什么、部署时不使用什么，以及中心化为何只影响动作相对排序。

## Technical failings that need to be addressed before the case is established

需要优先处理 R2-M1 至 R2-M4。当前稿件尚未建立强比较器条件下的原创性，没有证明软约束代价优势对应工程可行性，未能识别时间耦合机制，也未提供可访问的证据档案。这些问题不否定固定基准内的数值排序，但共同阻止稿件形成具有广泛科学重要性的 Nature-style 论证。

## Assessment against Nature-style criteria

**Originality**

中心化全动作辅助目标具有一定构造性兴趣，但其独立贡献未被因素化实验识别，实际增益也较小。家族级结果主要是六种相近 DQN 实现相对于 MPC-4 的一致排序。当前证据不足以支持广泛原创性。

**Scientific importance**

稿件说明长期策略可能优于短视野规划，但这一认识目前局限于人工定义的软约束模拟器。尚无任务级效用、硬可行性、外部分布或真实系统证据，因此科学和工程重要性有限。

**Interdisciplinary readership**

卫星边缘计算、强化学习和调度研究者会感兴趣。对更广泛的控制、运筹、航空航天系统和资源管理读者，论文尚未说明该结果是否可迁移到其他系统或改变实际设计决策。

**Technical soundness**

固定基准内的方程定义、配对设计、多重性控制和联合上界较强。主要技术不足来自比较器覆盖、软约束工程有效性、机制识别和外部可重复性，而不是中心统计计算的明显错误。

**Readability for nonspecialists**

稿件结构清楚，限制条件披露充分，表格与图注信息量较高。主要障碍是算法和统计术语密度高，以及无量纲成本缺乏工程直觉。

## Recommendation posture

我的倾向是不支持以当前形式按 Nature-style 标准接收。主要理由是原创性与科学重要性不足，而不是基准内统计证据粗糙。若作者能建立计算与信息条件更公平的比较器前沿，引入硬约束和外部工程验证，完成机制分离，并公开完整证据档案，稿件的定位可以被实质性重估。若这些证据无法补充，更合适的方向是将论文明确定位为一个透明、可重复的专业领域合成基准研究。
