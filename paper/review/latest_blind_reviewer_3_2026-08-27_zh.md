## Overall assessment

稿件在自定义合成基准内部提供了较强且透明的统计证据。六种 DQN 目标在五个完全耦合情景中的 30 项比较均优于 MPC-4，联合自举、同时上界和多重性校正也与主要数值结论一致。作者对软约束、固定效用权重、训练信息量不等以及缺乏运行验证等局限有较充分披露。

当前主要困难不在于表中排序是否成立，而在于这一排序对卫星地面调度科学的意义、时间机制的识别和跨学科可解释性。基准的成本函数、资源动力学和压力情景主要由作者设定，MPC 比较又被限制在较短预测深度。因此，稿件清楚证明了“这些 DQN 在这个模拟器中比 MPC-4 得分更低”，但尚未充分证明这是具有广泛工程意义的 DQN 家族优势，也未排除结果主要来自特定效用设计、软约束和比较器边界。

## Who would be interested and why

卫星边缘计算、在轨任务调度、强化学习方法和模型辅助价值学习的研究者会对这个可控基准感兴趣。统计学习研究者也可能关注其以种子块为独立单位的联合推断设计。对更广泛的航天系统、运筹优化和自主系统读者而言，兴趣取决于作者能否把无量纲成本优势转换为可理解的任务收益、风险降低或资源安全裕量，并证明结论不依赖当前模拟器的特定构造。

## Major strengths

1. 模拟器定义较完整。任务生成、通信轨迹、六个资源状态、三种动作和奖励均有明确方程，页 5 至 10 提供了较好的内部可追溯性。

2. 稿件准确区分真实交互预算与模型生成的动作结果数量。表 9 没有把相同真实交互数误称为相同信息预算。

3. 中央统计分析较审慎。30 个比较使用共同种子块的联合自举和同时上界，页 15、18 和 19 对推断单位与多重性处理交代清楚。

4. 作者主动限定了若干重要结论。稿件明确指出能量为裁剪后的软记账状态，不是守恒电池状态。作者也承认低耦合条件同时改变动力学和惩罚，MPC 运行时间与 DQN 推断时间并非匹配比较。

## Major Concerns

### R3-M1

**Severity**

Major

**Blocking**

No

**Axis**

scientific importance，engineering validity，claim moderation

**Claim pointer**

标题、摘要和结论将结果概括为资源耦合卫星地面调度基准中的 DQN 家族优势，并将该基准描述为未来运行验证的严格基础。

**Evidence pointer**

页 1 摘要。页 5 至 9 的成本和资源方程。页 21 表 11。页 24 至 25 的 Future work 与 Conclusion。

**Concern**

所有主要优势都建立在作者设定的无量纲线性成本、固定权重、裁剪资源状态和软惩罚之上。表 11 显示两类方法在全部完全耦合情景中都达到裁剪后的零能量状态，这说明当前“能量”变量并不能表达任务可执行性或能源亏空程度。压力情景也主要是同一生成器内的参数变化。因而，数值优势是否对应更高任务完成率、更少不可行动作、更低真实能耗或更安全的热边界，稿件目前无法回答。

**Why it matters**

跨学科读者无法从 5.92 至 13.15 个无量纲成本单位判断工程重要性。只要改变效用权重、硬约束或终止规则，策略排序就可能改变。当前证据支持模拟器内部排序，但不足以支撑更广泛的卫星调度意义。

**Resolution test**

至少提供一组具有明确工程解释的任务要求和效用标定，并在硬可行性约束下报告任务完成、能量余量、热边界、时限违约和通信占用。验证应包括未参与设计选择的运行情景、遥测驱动轨迹或硬件在环证据。若无法增加此类证据，应把标题、摘要和结论进一步限定为特定合成软约束目标上的算法排序，并避免把该结果推广为一般卫星地面调度优势。

### R3-M2

**Severity**

Major

**Blocking**

No

**Axis**

technical soundness，mechanism evidence，experimental design

**Claim pointer**

引言提出时间耦合能否使学习到的长时程价值优于一步和有限时域方法。讨论部分认为 contextual bandit 与规划深度结果支持 DQN 捕获持续后果的解释。

**Evidence pointer**

页 2 至 3 的中央问题。页 12 至 15 的耦合条件、MPC 和结果定义。页 21 表 10。页 24 Discussion。

**Concern**

现有实验只能说明 DQN 优于所实现的短时域 MPC 和即时奖励学习，不能独立识别优势来自长时程价值。MPC 最深仅观察 6 步，而 DQN 以 64 步任务和折扣目标训练。规划器与 DQN 的信息、计算、近似能力和部署时延没有匹配。更重要的是，参数 \(c\) 同时缩放状态转移和延迟惩罚，因此静态与弱耦合实验不能把时间耦合效应从目标函数重标定中分离出来。一个短时域比较器的不足也可能产生当前差距。

**Why it matters**

时间机制是稿件面向非专业读者最有吸引力的科学解释。如果没有机制分离，读者只能接受算法排序，不能判断 DQN 究竟学习了何种跨任务结构，也不能知道更充分的规划或动态规划是否会消除差距。

**Resolution test**

分别操纵资源携带与惩罚缩放，保持评价目标不变。增加能够利用完整随机模型的长时域或近似动态规划基线，并在匹配的计算或时延约束下比较。提供至少一个可视化任务轨迹，逐步展示即时方法、MPC 和 DQN 在相同状态下的动作、资源演化及后续代价。若这些实验不能完成，应将机制语言严格改为“与长时程价值解释一致”，并把结论限定为对所实现比较器的结果。

### R3-M3

**Severity**

Major

**Blocking**

No

**Axis**

originality，novelty-significance

**Claim pointer**

稿件同时提出 centered full-action 辅助目标和 DQN 家族层面的共同优势，并把前者与 Dyna、反事实增强、credit assignment、Joint MDPs 和 advantage learning 区分。

**Evidence pointer**

页 3 至 4 的相关工作和表 1。页 10 至 12 的方法。页 19 至 20 的表 6 至表 9。

**Concern**

方法层面的新增部分是 centered full-action 辅助损失，但其相对标准 DQN 的收益仅约 0.45 至 0.68 个成本单位，并按完整支持规则仅在五个情景中的三个成立。其他辅助目标没有各自调参，因此实验不能识别 centering 或 bootstrapping 的独立贡献。稿件于是把主要原创性转移到“六种 DQN 都优于 MPC-4”，但在作者设计的合成任务中，长时程学习优于受限短时域规划本身还不足以显示一般性方法突破。

**Why it matters**

对于 Nature-style 稿件，读者需要清楚知道新知识究竟是一个可推广的学习原理、一种有实质增益的新目标，还是一个可复现的测试平台。当前叙事在这三者之间移动，削弱了原创性判断。

**Resolution test**

选择并明确一个主要原创贡献。若核心是 centered full-action，应通过公平调参或因子设计分离 centering、bootstrap 与辅助损失尺度，并证明其效应不仅统计显著而且具有实际意义。若核心是基准，应与最接近的卫星调度和模型辅助强化学习方法做同条件比较，并说明该基准揭示了既有基准无法揭示的现象。

### R3-M4

**Severity**

Major

**Blocking**

No

**Axis**

reproducibility，data-resource quality

**Claim pointer**

贡献 4 声称提供从模拟器方程、检查点和种子级推断到表图及验证哈希的可执行证据链。

**Evidence pointer**

页 3 的贡献列表。页 16 的复现实验入口。页 25 的 Data and Code Availability。

**Concern**

稿件给出了命令和软件版本，但当前审稿包没有可访问的代码、原始 CSV、检查点、验证清单或永久归档。Data and Code Availability 仍包含待插入的归档标识。因此，可执行证据链这一贡献无法从所提供材料独立检查。

**Why it matters**

中央结果高度依赖自定义模拟器、预览接口、种子命名空间和生成式统计流水线。仅有方程与最终表格不足以核查实现是否与描述一致，也不足以验证所称的预览无副作用和联合重采样逻辑。

**Resolution test**

提供永久且版本冻结的归档，包含运行所需代码、环境锁定文件、原始种子级数据、分析脚本、模型清单、测试与校验输出及稿件所用提交哈希。独立环境应能从原始结果重建中央 30 项比较、表 5 和图 1。正式提交前必须移除归档占位符。

## Minor Comments

### R3-m1

**Severity**

Minor

**Axis**

readability for nonspecialists

**Affected element**

摘要和图 1

**Evidence pointer**

页 1 至 2

**Issue**

MPC-4、objective-regime comparison、seed-block bootstrap 和 simultaneous upper bound 在摘要中连续出现，但没有给非专业读者提供直观定义。

**Required correction**

首次出现时用一句自然语言解释 MPC-4 是具有四步完美预见的滚动规划器，并用一句话说明同时上界为何能支持“最差 DQN 成员仍优于 MPC-4”。

### R3-m2

**Severity**

Minor

**Axis**

figures-and-tables，writing clarity

**Affected element**

表 1

**Evidence pointer**

页 4

**Issue**

四列窄表产生大量断词和碎片化句子，方法关系难以快速理解。

**Required correction**

重构为更宽的两级比较表，或把详细解释移至正文。保留三项最关键区别即可，包括信息来源、是否枚举全部动作、是否改变部署阶段。

### R3-m3

**Severity**

Minor

**Axis**

figures-and-tables，interdisciplinary readership

**Affected element**

表 4 与表 6 的结果组织

**Evidence pointer**

页 17 与页 19

**Issue**

中央结论涉及六种 DQN，但第一张主结果表只列标准 DQN 和 centered full-action。读者需跨页查找其余四种目标，才能验证“家族”概念。

**Required correction**

在第一张主结果表中加入家族范围或最差成员列，并直接链接到完整六成员表。这样可让中央结论在一个视觉单元内自洽。

### R3-m4

**Severity**

Minor

**Axis**

writing clarity，claim moderation

**Affected element**

Discussion 中的术语“delayed feasibility penalty”

**Evidence pointer**

页 9 的奖励定义，页 21 的分解，页 24 的讨论

**Issue**

惩罚在每一步根据 post-decision 状态立即进入奖励，而“delayed”容易让非专业读者误以为惩罚在若干时间步后才观测。

**Required correction**

统一改为“post-decision resource penalty”或明确说明其即时计入奖励，但由先前动作累积的资源状态触发。

### R3-m5

**Severity**

Minor

**Axis**

figures-and-tables，readability for nonspecialists

**Affected element**

图 6、图 7 和图 9

**Evidence pointer**

页 18、19 和 23

**Issue**

图中使用 Centered FA、Stat.、Red.、Link、Energy 等缩写，且图 6 两个面板使用不同纵轴范围。虽然图注有提示，快速浏览仍容易误读相对差异。

**Required correction**

在图内使用完整情景名称，明确标记每个面板的纵轴范围，并考虑用相对 MPC-4 的成本差异作为补充视图。

### R3-m6

**Severity**

Minor

**Axis**

writing clarity

**Affected element**

正文中的“supported”规则

**Evidence pointer**

页 15、20 和 24

**Issue**

“complete support rule”在多个结果段落反复使用，但正文阅读中不容易记住它同时要求均值方向、区间和 Holm 校正符号检验。

**Required correction**

在首次结果出现时用简短括注重述三个条件，后续表格统一使用同一简写。

## Technical failings that need to be addressed before the case is established

没有发现足以否定“在当前固定模拟器中，30 个 DQN 与 MPC-4 的均值比较均为负值”这一狭义数值结论的 Blocking Yes 问题。

若要建立更有广泛意义的科学论证，必须优先解决以下问题。

1. R3-M1 所述工程效度。成本优势需要与真实任务要求、硬约束和可解释运行指标连接。

2. R3-M2 所述机制与比较器边界。必须分离时间耦合和惩罚缩放，并使用更充分或计算匹配的长期比较器。

3. R3-M4 所述可复现性。当前不可访问的执行证据链必须冻结归档并能够独立重建中央结果。

## Assessment against Nature-style criteria

**Originality**

中等。Centered full-action 构造具有明确形式，但其实验增益较小且组成效应未被独立识别。DQN 家族优于 MPC-4 的基准发现本身尚不足以显示广泛方法原创性。

**Scientific importance**

当前偏低至中等。统计排序明确，但工程后果仍由无量纲软约束模拟器决定，尚未连接到任务成功、安全或运行资源边界。

**Interdisciplinary readership**

目前主要面向强化学习与卫星调度专业读者。跨学科价值受到术语密度、缺乏物理任务实例和缺乏实际收益尺度的限制。

**Technical soundness**

模拟器内部的报告、配对设计和多重性处理整体较强。主要薄弱点是比较器时域与计算边界、时间机制未被独立分离、固定效用设计的敏感性，以及执行性材料当前无法检查。

**Readability for nonspecialists**

章节结构清楚，局限披露也较诚实，但正文在页 5 至 16 长时间停留于方程与实现细节。缺少一个贯穿全文的具体任务序列，使非专业读者难以理解 DQN 的决策为何优于即时方法或短时域规划。

## Recommendation posture

建议进行实质性大修后再评估。稿件已经形成可信的合成基准内部结果，但尚未建立足够广泛的科学重要性和跨学科可读性。若作者补充工程标定、机制分离、长期公平基线和可执行归档，论证会明显增强。若这些证据无法提供，更合适的定位是范围严格受限的算法基准或专业卫星调度研究，而不是广泛适用的卫星地面调度优势主张。
