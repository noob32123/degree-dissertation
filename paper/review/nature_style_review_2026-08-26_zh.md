# MD-CBAD-DQN 投稿前独立审稿报告

## Review setup

- **Input scope** 当前英文论文全文、最终 PDF、主结果表、七场景汇总与配对 bootstrap、验证清单，以及 `agent.py`、`environment.py` 和通用 `experiment.py`。
- **Assessment boundary** 本轮不检索外部文献全文，因此不能确认全球首创性。真实飞行数据、硬件在环结果和未公开运行环境不可评估。主结果专用入口 `reviewer_experiments.py` 未进入冻结盲审包，因此关于通用入口与结果文件不一致的意见只能解释为复现入口说明不足，不能直接推断结果来源错误。
- **Shared manuscript claim summary** MD-CBAD-DQN 利用训练期可得的一步全动作解析预览，构造反事实 Bellman 目标，并蒸馏状态内中心化动作优势。在保持标准 DQN factual target、网络、回放和探索设置不变的条件下，该方法被报告为在五个完全耦合场景中取得最低平均成本。
- **Visible evidence base** 七个场景、八个参数敏感性配置、五个独立训练种子、每种子二十条共享测试轨迹、种子级配对 bootstrap、MPC-4 边界比较、训练曲线及核心算法实现。
- **Missing materials affecting confidence** 外部文献优先权证据、真实任务校准数据、模型失配实验、更长时域或计算预算匹配的规划比较，以及明确指向主结果专用入口的一键复现清单。

三位审稿人的侧重点在审阅前固定。Reviewer 1 侧重技术有效性，Reviewer 2 侧重原创性和科学意义，Reviewer 3 侧重跨学科影响和非专业读者可读性。三份报告在相互隔离的上下文中形成，之后才进行综合。

## Reviewer 1

### Overall assessment

稿件的问题设定清楚，方法公式简洁，耦合控制、短时域规划器和以模型种子为推断单位的配对评价均有价值。但当前数学成本模型、物理生成分支、机制归因和统计强度尚未共同支撑主要结论。尤其是论文给出的切线屏障成本并非 `physics_correlated` 分支实际使用的即时成本。五个训练种子和频繁能量违规也限制了统计与工程解释。

### Who would be interested in the results, and why

卫星边缘计算、星地任务调度、模型辅助强化学习以及滚动时域规划研究者会直接关注该工作。训练阶段利用全部动作解析结果而部署阶段不调用预览，具有潜在的一般方法学意义。

### Major strengths

- factual Huber 损失与中心化辅助损失的职责区分清楚。
- 稿件明确限定 MPC-4 不是 64 步全局最优，没有宣称超越全部优化方法。
- 共享测试轨迹和种子内聚合避免把一百条轨迹误当成一百个独立训练重复。
- 静态与弱耦合控制对强化学习适用边界提供了有意义的反例。
- 对合成生成器、精确预览和外部有效性的限制已有主动说明。

### Major Concerns

#### R1-M1 [reproducibility]

- **Severity** Major
- **Blocking** Yes
- **Claim pointer** 修订实验使用物理相关生成器和 MPC-4，并由代码、统计文件与验证共同支撑。
- **Evidence pointer** `source.tex` 的 Experimental Design and Settings、Results、Data and Code Availability；`experiment.py`；`validation.json`；七场景结果文件。
- **Concern** 冻结盲审包中的 `experiment.py` 默认使用历史生成器，也不含 MPC-4 和完整辅助指标，无法直接生成论文主结果。`validation.json` 的 4,900 行与八策略主结果所需的 5,600 行也不一致。基于提供给本审稿人的证据，结果生成链没有闭合。
- **Why it matters** 复现者容易运行错误入口，或误把基础验证清单当成论文八策略主结果的端到端验证。
- **Resolution test** 提供单一、冻结且可执行的生成管线，从指定源码和固定配置重新生成原始评价、种子级汇总、bootstrap、表格、宏和验证文件。策略数、情景数、原始行数、单元格数、字段、种子、哈希与主表数值必须一致。

#### R1-M2 [mechanism-evidence]

- **Severity** Major
- **Blocking** Yes
- **Claim pointer** 第 3 节切线屏障成本及动作成本方程是修订实验实际优化的、可审计的即时成本模型。
- **Evidence pointer** `source.tex` 的 Cost factors、Action-specific immediate costs 和 Reward；`environment.py` 的 `_immediate_costs_from` 第 220 至 274 行。
- **Concern** 论文使用 (Q/Q_{\max}) 和 (B/B_{\max}) 的正切屏障、显式 \(\rho\) 与 \(\omega\)、共置开销和服务器成本。`physics_correlated` 分支实际使用归一化变量的固定线性加权和，没有这些屏障、阈值、无穷成本或同形式服务器成本。
- **Why it matters** 即时成本决定训练目标、策略排序以及全部 1.03% 至 3.38% 的效果。公式与代码不一致使结果的物理含义和“解析精确性”无法成立。
- **Resolution test** 二选一。将论文改写为实现中真实使用的完整线性成本方程，并给出全部系数、单位和逐动作映射；或者修改实现以严格执行论文方程，然后重新训练和评价。必须增加代表状态、阈值附近和越界状态的公式与代码数值一致性测试。

#### R1-M3 [experimental-design]

- **Severity** Major
- **Blocking** Yes，针对当前中心化机制主张。
- **Claim pointer** 实验隔离了 factual、未中心化全动作监督和中心化更新的贡献，并把增益归因于 centered advantage distillation。
- **Evidence pointer** Introduction 的贡献第 3 项；Method 开头；Experimental Design；Discussion；`agent.py` 的 `VARIANTS`；主结果表。
- **Concern** 当前只有 standard DQN、CBAD 和 contextual bandit，没有未中心化全动作对照。DQN 与 CBAD 只能检验完整复合目标，不能区分收益来自全动作监督、中心化或二者交互。贡献列表和方法段仍声称已分离两个阶段，而 Discussion 又明确承认不分解中间方法。
- **Why it matters** 中心化是标题和方法命名的核心。没有可识别对照，中心化的具体有效性没有被证实。
- **Resolution test** 若坚持中心化机制主张，需要一个真正有研究意义且严格匹配的信息对照。若作者决定不再加入该实验，则必须删除所有 “isolate”“separate the contribution” 及未中心化比较表述，并把结论严格限定为完整 CBAD 复合目标相对标准 DQN 有效。仅删除表格而保留机制因果语言不能解决问题。

#### R1-M4 [statistical-rigor]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 五个完全耦合场景及八个敏感性配置均获得统计支持。
- **Evidence pointer** Inference、Sensitivity 和 Results；`seven_regimes_paired_bootstrap.csv`，每项 `n_pairs=5`。
- **Concern** 10,000 次重采样不能增加五个独立训练种子所提供的信息。百分位 bootstrap 在 (n=5) 时覆盖不稳定，且跨五场景和八配置的全称陈述没有主检验层级或多重性处理。最小效应仅 1.03%。
- **Why it matters** 当前区间可能高估跨训练随机性的确定性，尤其是 link-limited 场景的小效应。
- **Resolution test** 增加独立训练种子，公开逐种子差值和留一种子敏感性。预先指定主要场景，其余作为次级或探索性分析，并使用适合小样本的稳健区间、置换或层级分析。若不增加种子，应把“统计支持”改为“在五个固定种子上方向一致”。

#### R1-M5 [experimental-design]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 能量受限和热应激情景支持受约束卫星调度的工程稳健性。
- **Evidence pointer** Seven evaluation regimes、Results、Discussion；`seven_regimes_summary.csv` 的违规指标。
- **Concern** CBAD 在五个完全耦合场景平均每个 64 步回合约有 23.29 至 38.38 次能量违规。所有策略的热违规均为零，thermal-stress 并未触及定义的热违规边界。当前实验更像软惩罚标量优化，而不是满足明确安全约束的调度。
- **Why it matters** 对卫星系统，频繁资源违规可能使较低总成本缺乏部署意义。未触发目标失效模式的压力场景也不能证明边界鲁棒性。
- **Resolution test** 预先定义工程可行性标准，报告可行回合率、任一违规概率和最大越界幅度。若要求硬约束，应引入动作屏蔽或安全回退并重新比较。热应激情景需要覆盖合理的热边界，或改名并收窄解释。

### Minor Comments

- **R1-m1 [reproducibility]** `target_interval=250` 与每四交互调用更新共同产生 500 个真实交互的有效同步间隔。应直接按真实交互记录，或在文稿和检查点元数据中解释该换算。
- **R1-m2 [writing-clarity]** 表中 8 至 64 Mbit 和 0.25 至 4.0 GFLOP 只适用于 nominal 生成范围。burst 和 thermal-stress 乘以 1.45 后会超出，应另列压力范围。
- **R1-m3 [data-resource-quality]** 结果完全依赖仿真与固定种子统计，建议提供带 DOI 或不可变提交哈希的公开归档，而不是仅按需索取。

### Technical failings that need to be addressed before the case is established

R1-M2 必须解决。R1-M3 若保留中心化的特定因果和原创性主张也必须解决。R1-M1 需要通过明确主入口和端到端验证闭合。

### Assessment against Nature-style criteria

- **Originality** 组合思路具有潜力，但中心化这一标题级成分缺少独立证据，外部优先权未核验。
- **Scientific importance** 时间耦合调度有实际意义，但 1% 至 3% 的合成环境效应和频繁能量违规限制工程重要性。
- **Interdisciplinary readership** 卫星系统、强化学习与在线规划读者会关注，更广影响尚未由模型误差或现实验证建立。
- **Technical soundness** 当前不满足，首要原因是实际成本函数与论文方程不一致。
- **Readability for nonspecialists** 叙事总体清楚，但状态坐标、成本权重和资源函数仍难以由非代码读者重建。

### Recommendation posture

在统一成本模型、校准机制主张并加强复现入口之前，主要结论尚未建立。完成重大技术修订后可重新评价。

## Reviewer 2

### Overall assessment

本稿的新颖性定位相对克制，且耦合控制和 MPC-4 边界使实验不只是单一仿真排名。然而，当前证据只能说明完整 CBAD 复合目标相对标准 DQN 的差异，不能说明中心化是有效成分。五种子小效应、同模型精确预览以及较弱的竞争性基线也限制了科学重要性。

### Who would be interested in the results, and why

模型辅助强化学习、资源约束序列决策、卫星边缘计算及研究训练期特权信息的读者会感兴趣。跨学科影响取决于方法在模型不准确和其他工程系统中能否保持价值。

### Major strengths

- 明确承认反事实学习和 advantage learning 并非一般意义上的新概念。
- DQN 与 CBAD 的网络、事实目标、回放、探索和预算匹配。
- 静态、弱耦合和全耦合结果给出了有意义的适用边界。
- 以训练种子而非测试轨迹作为推断单位。
- 对短时域规划、合成分布和单星拓扑的限制表述较克制。

### Major Concerns

#### R2-M1 [reproducibility]

- **Severity** Major
- **Blocking** Yes
- **Claim pointer** 修订实验使用物理相关生成器，并报告包含 MPC-4、传输量、规划时间及特定配对 bootstrap 的七情景结果。
- **Evidence pointer** Experimental Design、Results、`experiment.py`、`environment.py`、七场景 CSV 与 `validation.json`。
- **Concern** 提供给本审稿人的实验入口默认使用 `legacy_independent`，没有 MPC-4 路径，其指标和 bootstrap 输出也与结果文件不一致。现有验证清单不能消除该差异。
- **Why it matters** 物理生成器、MPC-4 边界和统计输出构成中央证据。冻结实现不能直接生成这些结果时，主表来源无法由当前材料核验。
- **Resolution test** 提供与当前结果完全对应的单一代码版本和运行清单，从干净环境显式启用 `physics_correlated`，实现 MPC-4，并在容差内重现主表、区间、规划时间与验证清单。

#### R2-M2 [novelty-significance]

- **Severity** Major
- **Blocking** Yes，针对中心化原创性主张。
- **Claim pointer** 中心化反事实 Bellman 优势蒸馏是主要原创贡献，实验区分了全动作监督与中心化贡献。
- **Evidence pointer** Introduction、Related Work、Method、Design principles、Discussion；`agent.py`；主表。
- **Concern** 没有未中心化全动作基线，且文稿同时存在“隔离机制”和“不分解中间方法”两种相互矛盾的陈述。
- **Why it matters** 全动作模型监督本身被文稿承认并非新概念。若不能识别中心化的贡献，标题级原创成分未被实验建立。
- **Resolution test** 增加有意义的最接近机制对照，或删除中心化独立有效性的主张，把创新定位为完整训练目标的组合设计。

#### R2-M3 [claim-moderation]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 精确一步模型监督可改善长期卫星地面调度。
- **Evidence pointer** Abstract、Generator、Sensitivity、Discussion。
- **Concern** 预览由训练环境自身确定性转移函数产生，八个敏感性配置没有检验预览模型的结构或动作相关偏差。
- **Why it matters** 方法以额外解析模型信息换取性能。在同模型仿真中成功不能说明工程模型误差下仍然有效。
- **Resolution test** 分离训练预览模型和评估环境，对转移、成本和动作后果加入系统性与随机偏差，报告性能退化和失效边界。否则明确限定为精确已知一步模型下的合成概念验证。

#### R2-M4 [statistical-rigor]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 所有场景和敏感性配置的改善均有统计支持。
- **Evidence pointer** Inference、Results 和 bootstrap 文件。
- **Concern** 五个独立种子不足以支持 10,000 次 bootstrap 所呈现的精度，也没有多重性控制。link-limited 的均值差仅 -1.067。五个方向一致的差值在精确双侧符号检验下最小 (p=0.0625)。
- **Why it matters** “全部支持”的措辞高度依赖所选的区间方法。
- **Resolution test** 增加种子、显示逐种子差值、采用小样本稳健分析并区分主要与探索性比较。

#### R2-M5 [experimental-design]

- **Severity** Major
- **Blocking** No
- **Claim pointer** CBAD 在全耦合条件下的排名支持其长期调度意义。
- **Evidence pointer** Design principles、Planning comparator、Results、Discussion。
- **Concern** 基线适合受控比较，却不足以建立竞争性算法意义。MPC-4 远短于 64 步资源持续时间，也没有计算预算或时域曲线以及更强 RL 基线。
- **Why it matters** 当前结果回答完整目标是否优于基础 DQN，但不能回答 1% 至 3% 的增量能否在合理的值估计增强或更长规划预算下保持。
- **Resolution test** 加入至少一个更强但预算匹配的 RL 基线，并给出规划时域或计算预算曲线。若研究只做机制控制，应进一步收窄竞争性性能定位。

### Minor Comments

- **R2-m1 [writing-clarity]** 摘要应写成“每个学习方法训练五个独立种子模型”，避免误读为全研究只有五个模型。
- **R2-m2 [writing-clarity]** “factual update remains unchanged”不精确。事实 target 和事实损失项不变，但总参数更新增加辅助梯度。
- **R2-m3 [claim-moderation]** 区分名义物理范围与压力情景乘以 1.45 后的范围。
- **R2-m4 [reproducibility]** 提供永久版本化归档、依赖锁定、许可证与可引用 DOI。

### Technical failings that need to be addressed before the case is established

中心化原创性归因 R2-M2 是阻断项。模型误差、五种子统计和较弱竞争基线限制结论强度。通用入口问题需要通过专用脚本的明确归档解决。

### Assessment against Nature-style criteria

- **Originality** 有潜力，但中心化具体贡献未被决定性验证，外部优先权不可评估。
- **Scientific importance** 当前主要是受控仿真概念验证，尚未形成广泛工程意义。
- **Interdisciplinary readership** 训练期解析模型监督具有潜在普适性，但没有第二系统或模型失配证据。
- **Technical soundness** 匹配训练和耦合控制较好，成本方程、机制消融和小样本推断仍不足。
- **Readability for nonspecialists** 总体结构清楚，但 factual update 与工程范围表述需要更精确。

### Recommendation posture

当前核心原创性与较广科学意义尚未建立，需重大修订。最低要求是统一实际成本模型、校准中心化机制语言、闭合复现入口，并加强统计证据。

## Reviewer 3

### Overall assessment

稿件的核心思想容易识别，也诚实限定了 RL 与短时域规划的边界。但对非专业读者而言，当前最严重的问题是论文叙述的工程成本并非程序实际优化的成本。复合总成本又没有充分分解为能量、时延、传输和违规后果，因此 1% 至 3% 的优势难以转化为任务意义。

### Who would be interested in the results, and why

卫星边缘计算、模型辅助强化学习、全动作监督以及滚动规划研究者会关注。更广泛工程读者需要知道该结果是否代表更少违规、更低能耗或可部署任务收益。

### Major strengths

- 相关工作没有把一般反事实学习据为己有。
- 静态、弱耦合和全耦合设置使“何时需要长期决策”成为可检验问题。
- 标准 DQN 与 CBAD 的声明性匹配设计合理。
- 推断单位原则上设置正确。
- 局限性和 MPC-4 的边界陈述较克制。
- PDF 的应用、模型、算法、实验和局限顺序清楚。

### Major Concerns

#### R3-M1 [reproducibility]

- **Severity** Major
- **Blocking** Yes
- **Claim pointer** 所有修订实验使用物理耦合生成器，七场景比较包含 MPC-4，并报告能量、时延、传输量和规划时间。
- **Evidence pointer** Experimental Design、Results、`experiment.py`、`environment.py`、结果 CSV 和 `validation.json`。
- **Concern** 冻结包中的核心实验入口不能生成报告的主要结果链。默认生成器、策略集合、指标字段、结果文件名和验证单元数均与论文主结果不一致。
- **Why it matters** 表 2、图 6 至图 9以及主要区间构成中央证据。若提供的核心入口不能重现它们，结果来源链在当前材料中未闭合。
- **Resolution test** 提供并冻结能够从指定检查点和测试种子直接再生所有主结果、MPC-4、图表和八策略验证的实际脚本，并记录文件哈希和端到端一致性。

#### R3-M2 [technical-soundness]

- **Severity** Major
- **Blocking** Yes
- **Claim pointer** 五类成本和动作成本方程是物理耦合实验采用的可审计系统模型。
- **Evidence pointer** System Model、Reward、Results；`environment.py` 的 `physics_correlated` 即时成本分支。
- **Concern** 论文正切屏障、显式权重和服务器成本与实现中的固定线性加权和不一致。
- **Why it matters** 读者会误以为算法在非线性安全屏障下验证，而程序实际优化另一个无量纲目标。
- **Resolution test** 完整公开实际成本方程和权重，并进行公式到代码的数值一致性测试；若保留原方程则重新实现、训练和评价。

#### R3-M3 [mechanism-evidence]

- **Severity** Major
- **Blocking** No，若删除中心化独立因果语言；若保留该语言则为 Yes。
- **Claim pointer** 两阶段设计分离全动作监督和中心化贡献。
- **Evidence pointer** Contributions、Method、Design、Discussion 和主结果表。
- **Concern** 结果只比较标准 DQN 与完整 CBAD，不能支持中心化相对未中心化监督的增益。
- **Why it matters** 中心化是方法命名与解释的核心。
- **Resolution test** 加入真正能识别中心化作用的严格对照，或删除所有分离贡献的表述，仅报告完整组合目标。

#### R3-M4 [statistical-rigor]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 五场景和八敏感性配置均得到统计支持。
- **Evidence pointer** Inference、Sensitivity、Results 和 paired bootstrap。
- **Concern** 五个独立训练种子、多个相关比较和约 1% 的最小改善，不足以支撑强全称推断。
- **Why it matters** 非统计读者容易把 10,000 次重采样误解为大量独立重复。
- **Resolution test** 增加种子、报告逐种子差值与留一敏感性、指定主比较并处理同时推断。

#### R3-M5 [interdisciplinary-readership]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 最低平均总成本支持长期卫星地面任务调度的广泛意义。
- **Evidence pointer** Abstract、Results、Discussion、Conclusion 和主表。
- **Concern** 结果限于单星、单链路、三动作合成环境。总成本为未充分公开权重的复合量，且没有把优势翻译为关键违约、时延、能量或任务收益。规划只比较 H=4。
- **Why it matters** 当前更充分支持“该复合目标在本模拟器中优于匹配 DQN”，尚未支持一般自主系统结论。
- **Resolution test** 增加独立验证层、模型偏差盲测、工程分量绝对效应和更长时域规划基线；否则收窄摘要和结论。

### Minor Comments

- **R3-m1 [writing-clarity]** 在摘要中用非公式语言说明“训练时比较另外两个未执行动作会发生什么”，降低 Bellman 和 centered advantage 的进入门槛。
- **R3-m2 [claim-moderation]** 把 “exact” 统一改为 “simulator-exact” 或 “exact under the specified deterministic transition model”。
- **R3-m3 [figures-and-tables]** 增加 nominal 和至少一个 stress 场景的成本分解，显示即时成本、延迟罚项、能量、时延、传输量和违规的绝对差值及单位。
- **R3-m4 [reproducibility]** 给出 15 个任务输入的名称、单位、范围、归一化常数以及关键资源函数的数据字典。

### Technical failings that need to be addressed before the case is established

R3-M2 是明确阻断项。R3-M3 决定标题级机制主张是否成立。统计强度和工程分解决定稿件能否从领域内概念验证上升为更广影响结论。

### Assessment against Nature-style criteria

- **Originality** 组合具有可识别新颖性，但中心化成分缺少可区分证据。
- **Scientific importance** 耦合控制有方法学价值，当前现实与广泛意义仍不足。
- **Interdisciplinary readership** 卫星、强化学习和规划群体可能关注，复合成本尚未翻译成跨领域可理解的工程结果。
- **Technical soundness** 成本方程与实现不一致是中央技术阻断问题。
- **Readability for nonspecialists** 主线可跟随，但缩写密度、“exact”的含义、15 维输入及复合成本分解仍不充分。

### Recommendation posture

当前不能从可见证据建立中央技术结论。统一成本模型后，本工作可被重新评价为一个主张边界较克制的专门领域算法研究；若希望更广意义，还需模型失配、工程分量和更强规划比较。

## Cross-review synthesis (post-review; not shown to reviewers)

### Consensus strengths

- 三份报告均认可问题具有真实的时间耦合结构，静态与弱耦合控制有解释价值。
- 三份报告均认可标准 DQN 与 CBAD 的 backbone 匹配设计有助于评价完整辅助目标。
- 三份报告均认可作者对 MPC-4、合成分布、单星拓扑和外部有效性的边界总体克制。
- 三份报告均认为方法对卫星调度和模型辅助强化学习读者有直接兴趣。

### Consensus blocking concerns

1. **论文成本方程与实际物理分支不一致**，对应 R1-M2 和 R3-M2，Reviewer 2 也在技术可靠性评价中认可该风险。该问题直接改变优化目标和结果含义，是当前最优先的阻断项。
2. **中心化的独立机制主张没有可识别证据**，对应 R1-M3、R2-M2 和 R3-M3。若论文坚持“中心化贡献已被隔离”，该问题为阻断项。若作者删除相应因果和分解表述，则完整组合目标相对 DQN 的经验主张仍可保留。

### Other consensus major concerns

1. **五个独立训练种子不足以支撑强全称统计表述**，对应 R1-M4、R2-M4 和 R3-M4。10,000 次 bootstrap 不是 10,000 个独立重复。
2. **精确同模型预览没有检验模型失配**，Reviewer 2 和 Reviewer 3 均认为这限制工程外推，Reviewer 1 的工程可行性意见与此一致。
3. **竞争性与规划边界仍有限**，现有 MPC-4 只能界定一个短时域完美预测规划器，不能代表更长视界或可扩展优化方法。
4. **主结果入口和验证映射不够清楚**。三位审稿人都因冻结包只包含通用入口而独立判定结果链不闭合。审后核查确认专用 `reviewer_experiments.py` 存在，因此这不是已证实的数据来源错误，但必须通过明确命令、文件哈希和八策略 5,600 行验证消除歧义。

### Where emphasis differs across reviewers

Reviewer 1 最关注工程约束，指出 CBAD 在完全耦合场景中仍有大量能量违规，且 thermal-stress 没有触发热违规。Reviewer 2 更关注科学意义，要求模型失配与更强 RL 或规划基线。Reviewer 3 更关注复合成本能否被非专业读者理解，建议分解能量、时延、传输与违规代价。

### Minor revision checklist

- 明确每个学习方法各有五个训练种子。
- 把 “factual update unchanged” 改为 factual target 和 factual loss term 不变，总梯度增加辅助项。
- 把 “exact” 限定为指定模拟器和确定性转移模型内精确。
- 区分 nominal 参数范围与 1.45 倍压力情景范围。
- 解释 250 配置值如何对应 500 个真实交互的同步间隔。
- 给出 15 个任务输入的数据字典和归一化常数。
- 提供永久版本化代码与结果归档。

### Broad-interest / significance readout

当前稿件具有明确的领域内方法价值，但尚未建立 Nature-style 的广泛科学重要性。最有潜力的跨领域结论是“训练时可得的解析全动作结果可以监督部署所依赖的动作间相对价值”。要把这一结论推广到更广自主系统，至少需要模型失配或独立验证环境，以及能解释工程收益而非仅报告无量纲总成本的结果分解。

### Most important issues to resolve before a strong Nature-style case is established

1. 统一论文和 `physics_correlated` 实现的即时成本函数，并重新验证所有数值。
2. 决定中心化机制主张的证据策略。增加真正有意义的识别性对照，或彻底删除“已分离中心化贡献”的语言。
3. 增加独立训练种子，公开逐种子效应，并重新设计主要与次要统计推断。
4. 检验预览模型误差和结构偏差，报告失效边界。
5. 明确安全或可行性要求，解释大量能量违规和未触发热边界的压力场景。
6. 发布唯一主结果入口、依赖锁定、结果哈希和 5,600 行端到端验证。

## Risk / unsupported claims

- “实验隔离了未中心化全动作监督与中心化贡献”不受当前结果支持，且与 Discussion 自相矛盾。
- “论文成本方程是修订实验实际优化目标”与 `environment.py` 不一致。
- “所有场景均有统计支持”依赖五种子 percentile bootstrap 和未校正的多个相关比较，证据强度被高估。
- “thermal-stress 验证热边界鲁棒性”不受零热违规结果支持。
- “长期卫星地面调度具有部署意义”尚未由真实轨迹、硬件在环、模型误差或硬约束可行性验证。
- 全球首创性未进行外部文献全文核验，本轮只能评价稿件内部的新颖性定位。
