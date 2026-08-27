# 润色后审稿意见修订追踪

日期：2026-08-27  
处理范围：除“非 DQN 基线仍偏弱”之外的全部可执行问题  
当前包状态：needs_author_input

| 问题 | 状态 | 采取的修改 | 证据 |
|---|---|---|---|
| DQN 家族与 MPC-4 缺少直接推断 | VERIFIED_DONE | 在相同工况、模型种子命名空间和测试轨迹上配对；每种子先平均 20 条轨迹，以 20 个模型种子块为独立单位；对 30 个目标–工况单元执行一次联合 10,000 次种子块 bootstrap；对精确双侧符号检验在 30 个单元上做 Holm 校正；增加最大统计量与同时 95% 上界 | md_cbad_dqn/results/reviewer_revision_state_complete/dqn_vs_mpc_inference.csv；dqn_vs_mpc_family_inference.csv；dqn_vs_mpc_seed_differences.csv；paper/generated/table_dqn_vs_mpc_family_inference.tex |
| 家族层面结论仍仅由均值支持 | VERIFIED_DONE | 30/30 个均值差、单元配对区间和 Holm 校正检验均支持 DQN；每个单元 20/20 个种子块为负；最不利均值差为 -5.92，全家族同时 95% 上界为 -5.03 | paper/source.tex 的统计方法、表 5、结果与讨论；paper/figures/fig_dqn_family_summary.pdf |
| 软约束状态与工程可行性界限不够醒目 | VERIFIED_DONE | 题目明确 synthetic soft-constrained；摘要明确无动作屏蔽或资源耗尽终止；结果与讨论将结论限定为维度无关固定权重目标；硬约束、任务标定和实测轨迹集中列为未来验证 | paper/source.tex |
| 图形摘要突出单一 centered 变体，与家族贡献不一致 | VERIFIED_DONE | 使用 Python 重做图 1：研究设计条带、5×6 家族差值矩阵、各工况最不利成员和全家族同时上界；不再把单一变体作为视觉中心 | paper/figures/plot_dqn_family_summary.py；fig_dqn_family_summary.pdf/.svg/.tiff/.png |
| 长时程机制表述过强 | VERIFIED_DONE | 将 identify/show 类因果措辞改为 consistent with；明确 contextual bandit 差距不能单独隔离长时程价值估计，机制作为未来可检验解释 | paper/source.tex 的摘要、讨论和结论 |
| 规划器计算效率暗示缺少 DQN 推理计时 | VERIFIED_DONE | 将 quality–computation frontier 改为测试范围内的 horizon–cost–runtime curve；明确未进行同路径 DQN 推理延迟与能耗比较 | paper/source.tex 的规划深度结果、讨论和未来工作 |
| 动作比例图无不确定性且再次突出单一变体 | VERIFIED_DONE | 从正文删除该非中心图与小节；将带种子级不确定性的家族动作机制分析列入未来工作 | paper/source.tex |
| 工程分解与家族–MPC 主结论不一致 | VERIFIED_DONE | 表 12 改为常规代表 standard DQN 相对 MPC-4；正文解释惩罚、即时成本、能耗、时延、传输量及软阈值暴露，并避免宣称硬可行性 | md_cbad_dqn/reviewer_reporting.py；paper/generated/table_engineering_outcomes.tex；paper/source.tex |
| 规划器命名不精确 | VERIFIED_DONE | 统一为 exact H-step receding-horizon model-based planner，并保留“仅对其完美预测有限时域目标精确”的限制 | paper/source.tex |
| 陈旧固定策略表与当前 CSV 冲突 | VERIFIED_DONE | 删除两份未引用的旧 table_fixed_policies.tex；最终生成表只来自当前锁定 CSV | paper/generated；md_cbad_dqn/tables |
| 源哈希与当前稿件不一致 | VERIFIED_DONE | 更新主验证和扩展验证源清单，纳入直接推断模块与 Python 图脚本；重新生成两份验证 JSON；逐项核对当前哈希一致 | validation.json；extended_revision_validation.json；paper/output/pdf/SHA256SUMS.txt |
| 非 DQN 基线仍偏弱 | OUT_OF_SCOPE | 按作者本轮明确要求不新增基线、不重跑该实验；保留为剩余投稿风险 | paper/source.tex 的 Future work |
| 永久公开归档号 | AUTHOR_INPUT_NEEDED | 未虚构 DOI/仓库编号；保留提交前占位符 | paper/source.tex 的 Data and Code Availability |

## 关键统计核验

- 30/30 个 DQN 目标–工况均值差低于零。
- 30/30 个单元的配对 95% bootstrap 区间低于零。
- 30/30 个单元通过 30 重 Holm 校正后的预设支持规则。
- 每个单元均为 20/20 个模型种子块方向一致。
- 最大 Holm 校正符号检验值为 5.722×10⁻⁵。
- 全家族最不利均值差为 -5.92；同时单侧 95% 上界为 -5.03。

## QA

- Python 图源码严格预检：20 PASS，0 WARN，0 FAIL。
- 图 PDF 最小文字：5.4 pt；低于 5 pt 的文字为 0。
- 图渲染碰撞审计：0 FAIL，0 WARN。
- Tectonic 最终编译：成功，30 页。
- 最终日志：无未定义引用、缺失引文、overfull box 或编译错误。
- 主验证状态：passed。

## 剩余提交门槛

1. 作者补充永久公开仓库/归档 DOI。
2. 作者确认本轮明确不处理的强非 DQN 基线风险是否可由目标期刊接受。
