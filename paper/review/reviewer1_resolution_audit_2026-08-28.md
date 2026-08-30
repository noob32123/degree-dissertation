# Reviewer 1 审稿意见解决情况核查

## 核查对象与判定口径

- 当前权威稿件：`paper/source.tex`
- 当前清稿：`paper/output/pdf/dqn_variants_satellite_ground_manuscript.pdf`
- 当前题目：*A Statistically Supported DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark*
- 核查日期：2026-08-28
- 判定仅依据当前修改稿、当前生成表图和可检查的复现材料，不依据作者对修改完成情况的口头说明。

判定标识：

- **已解决**：意见涉及的实质问题均已由正文、方法、实验、图表或可访问材料直接解决。
- **部分解决**：已完成重要修改，但意见中的一个或多个实质要求仍未完全满足。
- **未解决**：当前稿件中没有足够修改或证据支撑问题已经解决。

## Reviewer 1 总体评价

### English

> This paper focuses on the task scheduling problem in satellite-ground edge computing, and the theme meets the needs of the field. Although it attempts to propose a solution by combining cost modeling with reinforcement learning, there are significant flaws in key parts such as model construction and simulation experiment analysis, resulting in insufficient overall innovation and rigor. The specific issues are as follows:

### 中文翻译

> 本文聚焦卫星地面边缘计算中的任务调度问题，选题符合该领域的需求。尽管论文尝试通过结合成本建模与强化学习提出解决方案，但模型构建和仿真实验分析等关键部分存在明显缺陷，导致整体创新性和严谨性不足。具体问题如下：

## 总体结论

| 意见编号 | 核心问题 | 是否解决 |
|---|---|---|
| 1 | 静态单星单站问题过于简单，强化学习动机和适用性不足 | **部分解决** |
| 2 | 参数独立随机采样、缺少耦合与通信模型、可能违反物理规律 | **部分解决** |
| 3 | 参数范围设置不合理 | **部分解决** |
| 4 | “accuracy”定义不清且与研究动机冲突 | **已解决** |
| 5 | 收敛证据不足，缺少收敛前过程及能耗、时延曲线 | **已解决** |
| 6 | 缺少标准 DQN 对比与关键机制消融 | **已解决** |
| 7 | 摘要中的上标“1”格式错误 | **已解决** |
| 8 | 非开源情况下不应声称测试数据见项目源文件 | **已解决** |

**统计：5 条已解决，3 条部分解决，0 条未解决。**

---

## Comment 1

### English

> The paper focuses on the static scheduling problem of a single satellite and a single ground station, and the problem construction is relatively simple. Traditional algorithms can quickly obtain the optimal solution. As the authors also mentioned in the reinforcement learning algorithm that "there is no dynamic state transition", the authors need to further clarify the applicability and research motivation of intelligent algorithms such as reinforcement learning for such simple scenarios.

### 中文翻译

> 本文聚焦于单颗卫星与单个地面站的静态调度问题，问题构造相对简单，传统算法可以快速获得最优解。正如作者在强化学习算法部分所提到的“没有动态状态转移”，作者需要进一步阐明在此类简单场景中采用强化学习等智能算法的适用性与研究动机。

### 是否解决

**部分解决**

### 核查依据

当前稿件已经实质性消除了“没有动态状态转移”这一核心缺陷：

- 摘要和引言把问题重新定义为资源跨任务持续传递的时序调度问题，明确指出每个动作会改变热量、能量、队列、计算利用率、带宽和剩余接触时间，并影响后续任务选择，见 `paper/source.tex:48`、`paper/source.tex:64` 和 `paper/source.tex:83`。
- 稿件构建了 24 维状态，并给出六个资源变量的显式动态转移方程，见 `paper/source.tex:237-255`。因此，当前主问题不再是无状态转移的静态决策。
- 七种评估条件明确区分静态边界条件 `c=0`、弱耦合条件 `c=0.5` 和五种完全耦合条件 `c=1`。静态条件仅作为边界测试，不再作为主训练问题，见 `paper/source.tex:365-377`。
- 强化学习动机由“学习跨任务持续后果”支撑，并通过即时成本策略、上下文 bandit、标准 DQN 和不同深度的精确滚动规划进行对照，见 `paper/source.tex:381-388`、`paper/source.tex:477-486` 和 `paper/source.tex:543`。

但该意见尚未完全解决：

- 当前拓扑仍是单星单地面站，稿件将多星、多地面站和可变接触拓扑列为未来工作，见 `paper/source.tex:549`。
- 当前精确规划仅对给定的短时域目标最优，作者明确说明它并非 64 步全局问题的最优解，见 `paper/source.tex:381`。动态规划、混合整数优化等更强传统基线仍被列为未来工作，见 `paper/source.tex:553`。

因此，强化学习的时序动机和动态模型已经建立，但“单星单站问题是否仍可由传统全局优化快速解决”尚未通过全时域最优基线或更复杂拓扑完全排除。

---

## Comment 2

### English

> The key parameters in the paper are generated through random sampling within a certain range, ignoring the coupling characteristics between parameters such as energy consumption, computing resources, and latency. No specific communication model is constructed, nor is reference made to real distributions or correlation fitting. Within a certain range, contradictory samples that violate physical laws may also appear, such as scenarios where energy consumption is large but computing resources are small.

### 中文翻译

> 论文中的关键参数通过在一定范围内随机采样生成，忽略了能耗、计算资源和时延等参数之间的耦合特性。论文既没有构建具体的通信模型，也没有参考真实分布或进行相关性拟合。在给定范围内还可能产生违反物理规律的矛盾样本，例如能耗很大但计算资源很小的情形。

### 是否解决

**部分解决**

### 核查依据

当前稿件已经解决了独立采样、缺少参数耦合和缺少通信模型的大部分问题：

- 数据量与工作负载由相关潜变量共同生成，相关参数设为 0.68；处理时间由工作量除以计算速率得到，而非独立抽样；计算功率随工作负载单调上升；热量由能耗确定，见 `paper/source.tex:161-172`。
- 稿件强制满足 `D_res <= D_feat <= D`，并通过 20,000 个任务的自动审计检查数值有限性、正值性、数据流不等式和经验相关性，见 `paper/source.tex:163-181`。
- 通信部分给出了有效回传速率 `R_link = 2.2 + 217.8b`、传输时间、传输能耗/热量关系，以及带噪声的周期性带宽和接触时间轨迹，见 `paper/source.tex:168-172` 和 `paper/source.tex:207-213`。
- 报告结果只使用新的内部一致生成器，旧的独立采样生成器仅保留为历史复现模式，不用于当前结果，见 `paper/source.tex:361`。

仍未完全满足的部分是“真实分布或相关性拟合”：

- 稿件明确说明这些参数是工程包络而不是由飞行数据拟合的分布，见 `paper/source.tex:172` 和参数表标题 `paper/source.tex:176`。
- 相关系数 0.68、若干比例函数和周期扰动是合成生成器设定，当前稿件没有给出它们来自真实遥测或任务数据拟合的证据。
- 稿件把任务效用、遥测和硬件在环验证列为未来工作，见 `paper/source.tex:549`。

因此，物理矛盾、参数独立性和通信模型问题已被显著修正，但真实分布标定仍未完成。

---

## Comment 3

### English

> The range of parameter settings in the paper is unreasonable, and the authors need to conduct further research.

### 中文翻译

> 论文中的参数设置范围不合理，作者需要进一步调研并修正。

### 是否解决

**部分解决**

### 核查依据

当前稿件新增了参数范围、来源和敏感性分析：

- 参数来源表列出了原始任务数据量 8--64 Mbit、计算工作量 0.25--4.0 GFLOP、计算功率 4--20 W、有效 RF 回传速率 2.2--220 Mbit/s 等范围，见 `paper/generated/table_parameter_provenance.tex`。
- 计算功率和回传速率范围分别引用 NASA SmallSat 航电与地面网络示例；数据压缩比例引用 CCSDS 相关背景，见 `paper/source.tex:172`。
- 稿件明确把这些值界定为透明的合成工程包络，而不是已拟合的飞行分布，见 `paper/source.tex:172` 和 `paper/source.tex:176`。
- 参数敏感性测试覆盖计算需求和原始数据量正负 20%、能耗和热负荷增加 20%、链路容量降低 20%，见 `paper/source.tex:394-396` 和 `paper/source.tex:510-526`。

但仍有多项范围主要是模拟器假设，而不是任务级实证标定，包括任务数据量、工作负载、结果/原始数据比例、特征/原始数据比例、预处理比例、固定计算速率、6 W 发射功率和 1.45 倍突发系数。稿件自身也承认仍需任务效用、遥测和硬件在环验证，见 `paper/source.tex:549`。因此，参数透明度和稳健性检查已经改善，但“范围合理性”的外部实证依据仍不充分。

---

## Comment 4

### English

> The design of algorithm indicators is unreasonable, and the core indicator "accuracy" is ambiguously defined. The authors need to further explain the definition of accuracy. If accuracy refers to the matching degree between the algorithm output and the known optimal strategy, there is a logical conflict with the research motivation of exploring non-optimal solution strategies through reinforcement learning.

### 中文翻译

> 算法指标设计不合理，核心指标“accuracy”的定义含糊。作者需要进一步解释 accuracy 的定义。如果 accuracy 指算法输出与已知最优策略之间的匹配程度，那么它与通过强化学习探索非最优解策略的研究动机存在逻辑冲突。

### 是否解决

**已解决**

### 核查依据

- 当前权威稿件全文已不再使用 `accuracy` 作为指标，检索 `paper/source.tex` 无 `accuracy` 匹配项。
- 主指标已改为明确定义的未折扣 episode 总成本：`C_episode = sum(c_imm + p_t) = -sum r_t`，并说明每个执行步骤均计入一次，见 `paper/source.tex:383-388`。
- 次要指标明确包括即时成本、惩罚、能耗、建模时延、传输数据量、阈值暴露步数、规划时间、最大热量和最小剩余能量，见 `paper/source.tex:388`。
- 算法优劣通过配对均值差、95% bootstrap 区间、Holm 校正符号检验和联合上界判断，而不是与“已知最优动作”的分类匹配率，见 `paper/source.tex:390-392`。

原 `accuracy` 的定义冲突已通过删除该指标并重新定义评价体系解决。

---

## Comment 5

### English

> The results in Figure 8 fail to verify the authors' claim that the algorithm "tends to converge easily". The authors need to supplement images showing the accuracy of episodes before convergence. Additionally, it is recommended to present the convergence of more critical indicators such as energy consumption and latency.

### 中文翻译

> 图 8 的结果无法验证作者关于算法“容易趋于收敛”的说法。作者需要补充展示收敛前各 episode 的 accuracy 图像。此外，建议展示能耗、时延等更关键指标的收敛过程。

### 是否解决

**已解决**

### 核查依据

- 当前训练诊断记录全部 600 个训练 episode，并采用因果 25-episode 移动均值和 20 个模型种子的均值正负标准差，见 `paper/source.tex:357` 和 `paper/source.tex:394-396`。
- 当前训练诊断图完整覆盖早期到后期训练过程，横轴为 1--600 episode，四个面板分别为总成本、能耗、时延和延迟可行性惩罚。图文件为 `paper/figures/fig_training_diagnostics.svg` 和 `paper/figures/fig_training_diagnostics.pdf`。
- 正文不再使用笼统的“tends to converge easily”，而是限定性表述：四项指标约在前 220 个 episode 下降，之后在稳定范围附近波动，仅据此说明两个代表性 DQN 成员出现经验稳定，见 `paper/source.tex:499-508`。
- 图注明确说明这些曲线只描述训练分布，不作为独立测试观测，也不外推为整个 DQN 家族的收敛证据，见 `paper/source.tex:504`。
- 由于 `accuracy` 已从当前评价体系中删除，稿件使用总成本、能耗、时延和惩罚这些与当前目标一致的指标展示收敛前后过程，避免了原意见 4 所指出的逻辑冲突。

---

## Comment 6

### English

> The simulation results fail to verify the effectiveness of the OSDQN-RSF algorithm. Though the paper mentions "Compared with the baseline DQN" multiple times, it only compares with the mode of processing all tasks on the satellite or all on the ground station instead of the baseline DQN. To validate the algorithm's effectiveness, ablation experiments for strategies like epsilon Reset and Flushing replay buffer, or comparisons with the unoptimized DQN, should be supplemented.

### 中文翻译

> 仿真结果未能验证 OSDQN-RSF 算法的有效性。尽管论文多次提到“与基线 DQN 相比”，但实际只与全部任务在卫星端处理或全部任务在地面站处理的模式进行了比较，并未与基线 DQN 比较。为验证算法有效性，应补充 epsilon Reset、刷新经验回放缓冲区等策略的消融实验，或与未优化 DQN 进行比较。

### 是否解决

**已解决**

### 核查依据

该问题通过整体重构算法与实验设计解决，而不是继续保留旧 OSDQN-RSF 框架：

- 当前稿件中已不存在 `OSDQN` 或 `RSF` 名称，也不存在 epsilon reset 或 replay-buffer flushing 机制。当前探索率采用从 1 线性下降到 0.05 的统一日程，经验回放为普通 uniform replay，见 `paper/source.tex:357-359`。因此，对已删除机制进行 epsilon reset 或 buffer flushing 消融已不再适用。
- 当前实验明确加入未附加全动作辅助目标的标准 DQN 和 Double DQN 作为 factual-only 对照，见 `paper/source.tex:68`、`paper/source.tex:89` 和 `paper/source.tex:279`。
- 标准 DQN 与 centered full-action 变体共享网络、回放、探索、优化器、更新频率、目标网络同步和梯度裁剪，唯一差异为辅助目标，见 `paper/source.tex:351`。
- 组件比较包含 Standard DQN、Full-action Q auxiliary、Immediate advantage auxiliary、Centered full-action、Double DQN 和 Double + centered full-action，并采用 20 个预设模型种子、相同真实交互预算和相同留出轨迹，见 `paper/source.tex:452-475` 和 `paper/generated/table_extended_ablation.tex`。
- 除固定卫星端/固定地面端策略外，部署比较还包括即时成本 argmin、上下文 bandit、阈值启发式、标准 DQN、centered full-action DQN 和精确 H 步 MPC，见 `paper/source.tex:379-381`。
- 训练信息表显式报告不同目标的真实交互次数、更新次数、模型化动作结果数和训练时间，见 `paper/source.tex:466-470` 和 `paper/generated/table_training_accounting.tex`。

因此，原稿“声称对比标准 DQN但实际未对比”的问题已经解决。需要注意，解决方式是撤销旧 OSDQN-RSF/RSF 机制并建立新的 DQN-family 对照体系，而不是为旧机制补做消融。

---

## Comment 7

### English

> Abstract contains a format error; remove the superscript "1".

### 中文翻译

> 摘要中存在格式错误，请删除上标“1”。

### 是否解决

**已解决**

### 核查依据

当前摘要位于 `paper/source.tex:47-49`，摘要正文中不存在上标“1”或相应脚注标记。该格式错误已经删除。

---

## Comment 8

### English

> "The detailed test data can be found in the project source files" can be removed because the project source files are not open-source.

### 中文翻译

> “详细测试数据可在项目源文件中找到”这句话可以删除，因为项目源文件并未开源。

### 是否解决

**已解决**

### 核查依据

- 当前权威稿件中已不存在原句 `The detailed test data can be found in the project source files`。
- 当前稿件改为单独的 Data and Code Availability 部分，明确列出复现包包含的模拟器、180 个训练检查点、训练曲线、锁定原始评估、种子级汇总、转移审计、图表生成脚本、manifest 和 SHA-256 校验信息，见 `paper/source.tex:563-565`。
- 稿件提供公开仓库链接：[dqn_family_satellite_ground](https://github.com/noob32123/dqn_family_satellite_ground)。2026-08-28 通过只读远端查询验证该仓库可访问，远端 `HEAD` 为 `f9b3f2f7a93319edd858b16e7cb436a07d2b5b4a`。
- 当前表述使用“publicly available”，没有把缺少许可证的材料直接称为“open-source”。

因此，原有不准确句子已删除，且当前版本提供了可访问、可校验的复现材料。

---

## 仍需优先补强的事项

若目标是尽可能降低 Reviewer 1 再次提出同类质疑的风险，优先级如下：

1. 增加至少一个更强的全时域传统优化基线，或明确证明 64 步全局最优计算为何不可行，并报告计算复杂度与运行时间。
2. 在条件允许时增加多星、多地面站或可变接触拓扑实验；若不能增加，应在题目、摘要和结论中持续把结论限定为单星单站合成基准内部结论。
3. 为任务数据量、工作负载、压缩比例、计算速率、发射功率和突发系数补充任务级文献或真实遥测/硬件测量依据。
4. 将相关系数及周期链路参数由人工设定升级为真实数据拟合，或增加多组相关结构和分布形态的稳健性分析。

## 最终判断

当前修改稿已经解决 Reviewer 1 关于指标定义、训练收敛展示、标准 DQN/消融对照、摘要格式和数据代码可用性的意见，并显著修正了静态建模、参数独立采样和通信模型缺失问题。尚不能判为全部解决的核心原因是，当前研究仍是单星单站的合成软约束基准，尚无 64 步全局最优传统基线、真实任务分布拟合或完整的任务级参数标定。


