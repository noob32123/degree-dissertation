## Overall assessment

该稿件在内部模拟结果的报告质量上明显高于通常的算法基准稿。模拟器方程、状态变量、训练预算、随机种子、配对单位、联合 bootstrap、符号检验和多重性校正均有较清楚的说明。稿件也主动承认软约束、目标权重的人为设定、未进行任务级验证以及若干消融无法作因果分解。

现有证据足以支持一个很窄的描述性结论，即六个所实现的 DQN 目标在这个固定的合成模拟器和固定代价函数下，其均值均低于所实现的 MPC-4。现有证据尚不足以支持更强的中心解释，即这种差异由资源的时间耦合产生，代表 DQN 家族相对于具有竞争力的调度或规划方法的稳健优势。主要问题不是显著性计算本身，而是比较边界、基准构造、物理约束和可复核证据链尚未建立到与标题和摘要相称的程度。

## Who would be interested and why

强化学习评估、模型辅助价值学习和卫星边缘计算调度领域的研究者会对该稿件感兴趣。其价值主要在于一个说明充分的三动作顺序决策环境，以及对六种共享 DQN 主干的目标函数进行配对比较的统计设计。研究可复现性和算法基准方法学的读者也会关注联合 seed-block 推断与生成式报告链。若要吸引更广泛的工程、航天系统和跨学科读者，仍需证明结论不依赖当前手工设定的软约束代价函数和有限深度比较器。

## Major strengths

1. 模拟器从任务原语到 24 维状态、六类资源、三种动作和奖励的映射较完整，关键方程能够在正文中定位。

2. 中心的 30 个 DQN 对 MPC-4 对比使用共同的 20 个 seed block、共同测试轨迹、联合 bootstrap 和 Holm 校正。稿件没有把测试轨迹误当作独立模型重复。

3. 稿件正确区分了学习方法的跨模型种子变异与确定性比较器的跨轨迹变异，并明确指出两类标准差不可直接作推断性比较。

4. 对 DQN 家族内部差异的措辞总体克制。稿件承认共享的 \(\lambda=0.3\) 不能分离 centering 与 bootstrapping，也没有宣称存在统一最优的 DQN 目标。

5. 预览模型扰动、规划深度、参数敏感性和工程量分解为结果解释提供了有用的补充边界。

## Major Concerns

### R1-M1

**Severity**

Major

**Blocking**

Yes

**Axis**

experimental-design

**Claim pointer**

标题、摘要和结论所述的 DQN-family advantage，以及引言提出的学习长时程价值能否优于透明的一步和有限时域方法。

**Evidence pointer**

Experimental Design and Settings 中的 Planning comparator, outcomes, and inference。Table 7 的 \(H=1,2,4,6\) 规划结果。Discussion 的第三项 Future work。

**Concern**

中心比较器最多只精确枚举六步，而 DQN 通过 38,400 次真实交互学习折扣后的长时程价值。稿件未提供 64 步全局解、动态规划、可扩展树搜索、混合整数方法、卫星专用调度器或计算预算匹配的强基线。DQN 推理时间和能耗也未测量。因而当前结果严格证明的是这些 DQN 实现在固定模拟器中优于所实现的短时域 MPC，而不是 DQN 家族本身具有一般性优势。

**Why it matters**

有限时域规划在存在超过六步的延迟代价时出现差距是设计上可预期的。若比较器的有效时域和离线计算预算不匹配，中心性能差异无法与基线截断误差分离。标题与摘要当前使用的 family advantage 表述因此超出了可见比较所能支持的范围。

**Resolution test**

在相同信息、目标和明确计算预算下加入至少一种能够覆盖长时程的竞争性规划或优化方法，并测量 DQN 的匹配部署成本。若无法完成，则标题、摘要、讨论和结论都应明确限定为优于所实现的 MPC-4 与 MPC-6，不再据此主张一般性的 DQN 家族优势。

### R1-M2

**Severity**

Major

**Blocking**

Yes

**Axis**

causal-vs-correlative

**Claim pointer**

摘要提出时间结构是否产生可复现的 DQN 家族优势。Discussion 认为 bandit 和规划深度结果与学习到跨任务后果的解释一致。

**Evidence pointer**

Eqs. 4, 9 和 10。Seven evaluation regimes 对 \(c\) 的定义。该节明确说明 \(c\) 同时改变动作依赖转移和延迟惩罚。Table 8 显示 DQN 相对 MPC-4 的差异主要来自延迟惩罚。Prespecified sensitivity 未改变奖励和惩罚系数。

**Concern**

稿件没有将时间耦合强度与奖励尺度独立操纵。\(c=0\) 和 \(c=0.5\) 同时改变动力学与延迟惩罚，因此不能识别时间耦合的作用。五个中心 fully coupled regime 又共享同一组人为固定的即时成本和惩罚权重。敏感性分析只改变任务和资源原语，没有检验惩罚权重、成本权重、折扣率或终端代价。当前证据因此无法区分真正的长时程价值优势与特定奖励塑形对 DQN 行为的偏好。

**Why it matters**

时间耦合产生优势是稿件的机制性解释和中心科学问题，而不仅是局部措辞。若该解释未被可区分的干预支持，显著性检验只能确认固定模拟器输出的稳定排序，不能确认排序产生的原因。

**Resolution test**

进行正交设计，分别改变动作状态携带、延迟惩罚尺度、折扣率和终端资源代价，并预先定义交互效应或排序保持标准。至少应证明在不改变奖励尺度时增强耦合会扩大长时程方法优势，或将全文机制表述降级为仅与时间耦合解释相容。

### R1-M3

**Severity**

Major

**Blocking**

No

**Axis**

claim-moderation

**Claim pointer**

稿件将环境定位为资源耦合的卫星地面调度基准，并称其为未来 operational validation 的可复现基础。

**Evidence pointer**

Complete stochastic generator and action-load specification 对 soft-constrained clipped accounting states 的说明。Table 8 中 DQN 和 MPC-4 在所有 fully coupled regime 的最小能量均为 0。Discussion 的第一项 Future work。

**Concern**

能量为零时动作仍不被屏蔽，回合不终止，能量赤字的幅度在裁剪后丢失。其他资源同样是软约束记账变量。所有核心方法均触及零能量，说明主结果正发生在物理可行性失真的区域。惩罚在裁剪后不能表达继续消耗资源的真实后果。

**Why it matters**

该设计不影响在已定义数值模拟器内重算总成本，却削弱任何工程性能、资源安全或卫星调度可部署性的解释。算法可能通过真实系统中不可执行的动作序列获得相对优势。

**Resolution test**

加入守恒资源、动作可行性、终端条件和明确安全边界，并报告失败率、不可行动作率及性能排序。若仍保留软约束环境，应将工程和 operational 语言限制为抽象算法基准，不把能量、热和通信结果解释为任务级可行性能。

### R1-M4

**Severity**

Major

**Blocking**

Yes

**Axis**

reproducibility

**Claim pointer**

Introduction 第四项贡献所述的 executable evidence chain，以及摘要和结论所述的 fully specified 和 reproducible platform。

**Evidence pointer**

Reproducible result entry point。Data and Code Availability。后者明确写有 “AUTHOR ARCHIVE IDENTIFIER TO BE INSERTED BEFORE SUBMISSION”。本次可见审稿包未包含独立补充材料或外部归档。

**Concern**

正文列出了运行命令和声称存在的本地文件，但中心结果依赖的代码、锁定 CSV、模型检查点、seed-level 差值、联合 bootstrap 输入和验证清单不在可见审稿材料中。可见稿件因此不能独立核验 30 个比较、哈希链或模拟器实现是否与方程一致。

**Why it matters**

可复现性不仅是辅助承诺，而是稿件声明的四项主要贡献之一。中心证据完全来自自建模拟器和自动生成表格，在原始数据与执行环境不可审查时，统计结果和实现一致性仍属不可评估。

**Resolution test**

提供永久、版本化的公开归档，包含代码、锁定原始结果、seed-level 数据、检查点或其可重建路径、环境文件、测试和逐文件哈希。由干净环境从归档重新生成所有中心表格和联合推断，并使生成值与稿件一致。

### R1-M5

**Severity**

Major

**Blocking**

No

**Axis**

novelty-significance

**Claim pointer**

Introduction 的四项贡献，以及 Discussion 将 family-level consistency 作为主要贡献。

**Evidence pointer**

Table 1 的 closest method families。Tables 4 至 6 的家族内部结果。Related Work 中列出的卫星调度研究。

**Concern**

中心新意目前主要是六个共享 DQN 主干在一个新建环境中均优于短时域 MPC。Centered full-action 相对标准 DQN 的增益约为 0.45% 至 0.85%，完整支持规则只在五个 regime 中的三个成立。最接近的卫星专用调度器和更广泛的现代强化学习基线没有进入实验。因而统计稳定性尚未转化为明确的算法创新或可推广的调度发现。

**Why it matters**

Nature-style 重要性需要超出一个自建基准中的排序。若主要算法差异较小且非统一支持，稿件需要说明读者从 family-level pattern 中获得了什么新的普遍原理。

**Resolution test**

明确区分基准贡献、方法贡献和经验发现。将最接近的卫星调度方法及至少一种非 DQN 长时程方法纳入匹配比较，并在跨任务或独立环境中验证 family-level pattern。否则应将新意限定为基准报告，而不是广泛的调度算法优势。

### R1-M6

**Severity**

Major

**Blocking**

No

**Axis**

statistical-rigor

**Claim pointer**

Results 按 undiscounted episode total cost 判断方法排序，同时将 DQN 与 MPC 描述为优化相同调度目标。

**Evidence pointer**

Eq. 17 及其后文字。DQN 与 planner 均以 \(\gamma=0.97\) 优化，主结果报告未折扣总成本，且稿件明确说明未做 discount sensitivity analysis。

**Concern**

训练和规划优化的是折扣目标，确认性终点却是未折扣总成本。对于 64 步并含延迟惩罚的任务，两种目标可能给出不同策略排序。当前没有证明所报告优势对该目标不一致稳健。

**Why it matters**

这不会使已观测的未折扣均值无效，但会削弱将差异解释为对声明工程目标的优化优势。它也可能与有限时域比较器的截断共同影响方法排序。

**Resolution test**

使用与主终点一致的 \(\gamma=1\) 重新训练和规划，或预先给出覆盖合理折扣率的完整敏感性分析。应报告方法排序、效应大小和最不利差值是否保持。

## Minor Comments

### R1-m1

**Severity**

Minor

**Axis**

statistical-rigor

**Affected element**

Table 5 和 centered full-action 对 standard DQN 的结果解释。

**Evidence pointer**

Immediate advantage 的均值差为 \(-0.49\)，bootstrap interval 为 \([-0.90,-0.12]\)，Holm \(p=1\)。Table 6 中两个 regime 的均值区间排除零，但符号检验未通过完整规则。

**Issue**

均值 bootstrap 与符号检验回答不同问题，但正文没有充分解释为何区间排除零而方向一致性检验完全不支持。读者容易把 support rule 当作互相矛盾的显著性判定。

**Required correction**

明确说明 bootstrap 针对均值差，符号检验针对种子方向一致性，并给出对应的正负种子数。避免仅用 interval below zero 概括稳健支持。

### R1-m2

**Severity**

Minor

**Axis**

figures-and-tables

**Affected element**

PDF 中多张全宽缩放表格和复合图，尤其是 Tables 3 至 10 与 Figs. 6 至 9。

**Evidence pointer**

PDF 第 16 至 22 页。若干表通过 `\resizebox{\textwidth}{!}` 压缩，标签和数值字号明显小于正文。

**Issue**

图表信息完整，但当前字号和密度妨碍非专业读者快速读取关键比较，也削弱主次层级。

**Required correction**

主文保留中心效应量、最不利区间和关键工程结果。将完整矩阵移入补充材料或扩展数据，并确保最终印刷尺寸下的轴标签和表格文字可辨认。

### R1-m3

**Severity**

Minor

**Axis**

claim-moderation

**Affected element**

Representative DQN training diagnostics show empirical stabilization。

**Evidence pointer**

Fig. 8 及其后关于 empirical optimization stability 的文字。

**Issue**

25 episode 平滑后的成本、能耗、延迟和惩罚进入平台期只能说明观测曲线趋于平稳，不能单独证明优化稳定或收敛。图中也未显示 Q 值、TD 误差、梯度异常或失败种子。

**Required correction**

将措辞改为训练指标在后期进入经验平台期，或加入预定义的稳定性诊断和跨种子失败标准。

### R1-m4

**Severity**

Minor

**Axis**

writing-clarity

**Affected element**

参考文献表的完整性与一致性。

**Evidence pointer**

PDF 第 24 至 27 页。RN23 和 RN27 的最终条目只列期刊和年份，缺少卷、页码或文章号及 DOI，而相邻期刊条目包含这些信息。

**Issue**

不完整的书目信息降低相关工作定位的可追踪性。

**Required correction**

补全所有可用的卷期、页码或文章号和 DOI，并统一会议与期刊条目的大小写和标点格式。

## Technical failings that need to be addressed before the case is established

阻止中心论证成立的问题是 R1-M1、R1-M2 和 R1-M4。必须先证明优势不是有限规划时域和不匹配计算预算的产物，必须将时间耦合与奖励缩放的作用分离，并必须提供可独立复核的原始结果和执行归档。

R1-M3 和 R1-M6 不直接否定固定软约束模拟器中的数值排序，但它们阻止将结果解释为物理可行的卫星调度优势或对所声明未折扣工程目标的稳健优化。

## Assessment against Nature-style criteria

**Originality**

中等偏低。完整基准描述和 seed-block 联合推断有方法学价值，但中心经验结论仍是已知 DQN 主干相对短时域比较器在自建环境中的排序。Centered full-action 的独立算法贡献较小且并非所有 regime 均满足完整支持规则。

**Scientific importance**

目前有限。没有任务数据、遥测、硬件在环、物理可行约束或独立环境验证。若修复比较器和基准有效性问题，该工作可能成为有用的调度评测资源。

**Interdisciplinary readership**

当前主要面向强化学习基准和卫星边缘调度的小范围读者。跨航天系统、运筹优化和自主系统读者需要更真实的约束、任务效用和竞争性优化基线。

**Technical soundness**

固定模拟器内部的统计分析总体认真，推断单位、多重性和配对结构说明充分。中心技术案例仍被比较器截断、奖励与耦合混杂、软约束失真、目标不一致以及不可访问的证据链所限制。

**Readability for nonspecialists**

文字组织清楚，作者也主动陈述多项边界。27 页正文中的方程、缩放表格和统计规则非常密集。非专业读者较难区分已证明的数值排序、与机制相容的解释及尚未验证的工程含义。

## Recommendation posture

建议在形成可支持 Nature-style 广泛科学论证之前进行实质性重构和补充验证。当前稿件最可信的定位是一个报告严谨的合成算法基准，而不是已经成立的一般性 DQN 家族调度优势。若作者完成匹配的长时程比较、解耦的机制实验、物理可行约束验证和公开归档，再评估其科学重要性与跨领域吸引力会更合适。
