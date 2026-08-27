# 第二轮全文润色与审稿适配审计

日期：2026-08-27  
稿件：paper/source.tex  
处理路线：algorithmic / full manuscript / English / generic high-impact journal

## 1. 本轮目标

- 将核心主张从某个 DQN 变体转为 DQN 家族相对于 MPC-4 的一致优势。
- 让摘要、引言、结果、讨论与结论形成同一条最短充分证据链。
- 压缩审稿驱动的重复防御文字，并把边界的解释和解决路线集中到 Future work。
- 保留方法、图注中影响可复现性或结论解释的必要事实，不以语言包装掩盖证据范围。

## 2. 术语账本

| 规范形式 | 使用规则 |
|---|---|
| DQN family | 名词 |
| DQN-family | 复合修饰语 |
| DQN objectives | 指六种训练目标 |
| MPC-4 | 四步精确滚动时域规划器 |
| exact H-step receding-horizon planner | 方法首次定义或规划深度比较 |
| model-seed block | 独立训练模型构成的配对推断区组 |
| episode total cost | 主评价指标 |
| centered full-action | 仅作为家族成员或辅助监督机制，不作为论文唯一贡献 |

## 3. 贡献链重构

1. 题目直接陈述资源耦合基准中的“DQN-family advantage”，同时用“statistically supported”限定证据强度。
2. 摘要以 30 个目标—情景配对比较为主证据，并报告最不利均值差和家族级同时上界。
3. 引言把贡献明确分为基准、受控 DQN 家族、家族级推断和可执行证据链。
4. Results 先回答 DQN 家族是否一致优于 MPC-4，再讨论家族内部目标设计差异。
5. Discussion 解释共同的序列价值学习结构为何比目标细节更能概括结果，不指定单一获胜变体。
6. Conclusion 仅保留家族级主张、证据强度和未来验证入口。

## 4. 主文本纪律

- 删除主文中的 seed-effect 图和非配对 bootstrap 表引用，避免重复证明同一主张；底层文件未删除。
- 将 centered full-action 的主推断表移到家族内部比较小节，使其承担“目标设计微调”而非“唯一贡献”的功能。
- 压缩训练曲线、工程分解、参数敏感性和预览扰动段落，只保留改变结论解释的结果。
- MPC 深度结果保留成本与决策时间的核心关系，不重复逐项防御。
- Results 的原始 LaTeX 词项由 2,133 降至 1,619，减少 514 个，约 24.1%。
- 全文原始 LaTeX 词项由 9,155 降至 8,387，减少 768 个，约 8.4%。

## 5. 边界集中与科研诚信

Future work 统一组织三类边界及对应路线：

1. 运行验证：量纲化任务效用、硬约束、动作屏蔽、终止条件、遥测和硬件在环、多星多站拓扑。
2. 机制识别：目标特异权重、梯度归一化、centering/bootstrapping/discounting 因子分离、独立耦合系数、结构化预览误差。
3. 比较前沿：树搜索、动态规划、混合整数优化和卫星专用调度器，以及匹配的信息、计算、延迟和能耗预算。

为保持证据边界，摘要仍保留一次“synthetic, soft-constrained”范围限定；Methods 与自足图注仍保留裁剪规则、训练分布和规划器信息条件。这些是可复现性事实，不属于可删除的局限讨论。

## 6. 一致性与编译检查

- 30 个 DQN--MPC-4 对比的统计文件、联合 bootstrap 结果和验证清单已由锁定原始 CSV 重新生成。
- 术语一致性检查中，“this work”仅用于 Funding，“this study”用于科学叙述；数值精度差异对应不同参数或表格显示精度。
- 未发现已删除图表的残留引用、em dash、未定义引用、未定义交叉引用、overfull box 或 LaTeX 错误。
- 最终 PDF 为 27 页；抽查首页、家族图、核心结果页、Future work 与 Conclusion，未见裁切、溢出或错位。
- 编译仅报告既有窄列与参考文献的 underfull box，不影响内容完整性。

## 7. 有意保留的待办

- 按作者指示，本轮不新增或加强非 DQN 基线实验；更广且计算匹配的比较被列为 Future work。
- Data and Code Availability 中的永久归档标识仍需作者在投稿前填写。
