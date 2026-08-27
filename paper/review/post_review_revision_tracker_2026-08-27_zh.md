# 三审后论文修订追踪表

本文件为作者内部追踪，不作为 reviewer-facing 回复文件。当前任务按投稿前内部大修处理，不代表期刊编辑决定。

## 修订主线

论文不再强调某一个 DQN 变体普遍更优。主结果改为，六种 DQN 目标在五个完全耦合场景中的全部 30 个均值均低于本文实现的所有非 DQN 比较器。每个场景中最强的非 DQN 比较器均为 MPC-4。该结论严格限定于当前合成模拟器和已实现比较器，不外推为 DQN 普遍优于规划或真实卫星调度系统。

## 已完成并核验

| ID | 审稿问题 | 论文处理 | 状态 |
|---|---|---|---|
| R1-M1 | 参数 c 同时改变转移与奖励，不能单独识别 carryover | 将 static 与 reduced coupling 改称复合边界条件，明确其同时改变动力学和延迟惩罚，删除因果式 carryover 解释 | VERIFIED_DONE |
| R1-M2 / R3-M3 | λ 针对 centered objective 选择，却用于不同尺度的辅助损失 | 在摘要、贡献、实验设计、表 8、讨论和结论中明确这是 fixed-λ 实现比较，不再声称隔离 centering 或 bootstrapping | VERIFIED_DONE |
| R1-M3 / R3-M1 | 能量归零后仍执行，不能代表物理剩余电量 | 将 e 明确定义为软约束裁剪记账状态，说明裁剪隐藏赤字且不能支持物理可执行性 | VERIFIED_DONE |
| R1-M4 | threshold 和 fixed policies 定义或结果不完整 | 写入完整阈值规则和 fixed-action 定义，正文补充 nominal fixed-policy 结果，并指向机器可读七场景结果 | VERIFIED_DONE |
| R1-M5 | episode total cost 缺少正式定义 | 新增未折扣 episode cost 公式、终端步处理以及与 γ=0.97 折扣训练和规划目标的区别 | VERIFIED_DONE |
| R1-m1 | 重复统计区间端点不一致 | 报告脚本统一从主推断表读取重复 reference 与 simulator-exact 行 | VERIFIED_DONE |
| R1-m2 / R3-m3 | 学习策略和确定性策略 SD 含义不同 | 表 4 和图 6 图注明确两类 SD 不可作为同一推断尺度直接比较 | VERIFIED_DONE |
| R1-m4 | DQN family 成员计数不一致 | 固定六个 DQN 目标清单，将 γ=0 contextual bandit 单列为比较器 | VERIFIED_DONE |
| R2-M1 | 贡献类型和原创性不清 | 题目改为 controlled synthetic comparison，贡献改为家族比较和边界刻画，不宣称一般算法原理 | VERIFIED_DONE |
| R2-M3 / R3-M2 | 有限视野规划器不足以代表规划方法 | 强调家族优势仅针对已实现比较器，声明未测 DQN 同协议推理时间，也未比较近似规划或数学规划 | VERIFIED_DONE |
| R3-M4 | 家族结果和家族内部结果证据层级不清 | Results 首段和 Discussion 首段明确把 30 个 DQN 均值低于 MPC-4 作为主结果，把家族内部差异降为次要结果 | VERIFIED_DONE |
| R3-m1 | 正文残留返修过程语言 | 删除 revised experiments、reviewer-revision、second-round controls 和 earlier formulation 等措辞 | VERIFIED_DONE |
| R3-m2 | 术语和统计判据对非专业读者不清 | 摘要直接说明 paired interval 与 Holm-adjusted sign-test 判据，统一 DQN family 与 contextual bandit 的定义 | VERIFIED_DONE |

## 仍需新实验或作者输入

| 项目 | 当前处理 | 状态 | 是否阻止当前 PDF 生成 |
|---|---|---|---|
| 每种辅助目标独立调优 λ 或执行损失及梯度尺度归一化 | 已收缩机制主张，尚未新增训练 | PARTIAL | 否，但阻止 centering 或 bootstrapping 的因果归因 |
| 纯动力学耦合控制，固定奖励仅改变 carryover | 已删除单因素机制解释，尚未新增训练 | PARTIAL | 否，但阻止独立 carryover 结论 |
| 硬能量约束、动作屏蔽或 constrained MDP | 已限制工程和部署主张，尚未新增实验 | PARTIAL | 否，但阻止硬约束可部署性主张 |
| 更强长视野规划、数学规划或现代卫星调度基线 | 已严格限制比较范围，尚未新增实现 | PARTIAL | 否，但阻止一般优于规划的主张 |
| 替代效用权重、Pareto 或第二任务验证 | 已限制科学意义和外部有效性，尚未新增实验 | PARTIAL | 否，但阻止可迁移规律主张 |
| 永久代码与数据归档标识 | 正文保留醒目占位符 | AUTHOR_INPUT_NEEDED | 是，阻止 submission-ready |

## 验证记录

- `python -m md_cbad_dqn.reviewer_reporting` 成功。
- `python -m md_cbad_dqn.extended_reporting` 成功。
- `python -m unittest md_cbad_dqn.tests.test_core` 通过 22 项测试。
- `paper/audit_manuscript.py` 未发现缺失引用、缺失交叉引用或长破折号。
- 清稿和标改稿均由 Tectonic 成功生成。

## 包状态

`draft_with_placeholders`

原因是永久归档标识仍缺失，且若希望恢复机制、部署或一般规划优越性主张，仍需新增实验。
