# 当前稿旧版叙事遗留审计

日期：2026-08-28

## 锁定的论文主线

当前稿的中心贡献是：在定义完整的合成软约束卫星—地面调度基准中，六种 DQN 目标相对 MPC-4 表现出具有统计支持、跨资源压力工况一致的家族级优势。DQN 变体之间的差异属于次级机制分析，不将任何单一变体指定为本文唯一方法或统一优选方法。

## 发现并修正的遗留

1. **Table 1 的作者中心式标签**：删除 “Relation to this study” 和 “This study”，将该表重新定位为四种模型辅助 DQN 目标所共享的训练时监督接口，并明确标准 DQN 与 Double DQN 是仅使用事实转移的家族对照。
2. **相关工作中的单一变体中心叙事**：不再把 centered full-action 描述为全文唯一构造，也不再把 full-action Q 称为最接近的经验对照；改为先说明四种模型辅助目标的共享接口，再说明家族级比较与次级目标设计分析。
3. **方法章节标题与开头**：将章节改为 “DQN Objective Family and Full-Action Supervision”，并准确区分标准 DQN 与 Double DQN 的目标评估方式；删除 “complete method” 等暗示某一变体代表完整方法的表述。
4. **实验设计的主次层级**：首先陈述六种 DQN 目标相对 MPC-4 的 30 个主要比较，再将 centered full-action、full-action Q、immediate advantage 和 Double-DQN 组件比较列为次级家族内分析。
5. **旧协议图**：从英文主稿和双语稿正文中移除未被正文引用、且视觉上仍以 centered full-action 的辅助权重校准为中心的协议图。其对应资产未删除，可作为历史记录保留。
6. **默认方法宏与比较器称谓**：删除将 centered full-action DQN 设为默认 `method` 的宏，改称 “the centered full-action family member”。
7. **结果证据边界**：将标准 DQN 与 MPC-4 的工程分解明确为代表性单项比较，不再外推为整个家族的资源使用模式；将两种代表性成员的训练曲线限定为记录指标达到经验平台，不宣称整个家族收敛。
8. **比较术语与排版**：统一 centered full-action 与 standard DQN 的差值称谓，修复 Table 1 的列宽与左对齐，并在双语 PDF 中消除方法章节及三个结果小节的孤立页末标题。

## 保留内容及理由

- centered full-action 与 standard DQN 的配对推断、参数敏感性和预览误设分析继续保留，因为它们是透明的次级家族内证据；正文已明确其不决定家族级结论。
- 辅助权重的早期校准说明继续保留，因为它界定了固定系数组件比较的解释边界；仅移除重复且变体中心化的协议图。
- 所有实验数值、统计检验、图表数据、参考文献及实验脚本均未因本轮语言和叙事修订而改变。

## 最终校验

- 英文稿：缺失引用 0，缺失交叉引用 0，超过 30 词的句子 0。
- 旧版叙事关键词扫描：未再命中 `Relation to this study`、`complete method`、`primary centered-full-action`、旧 `method` 宏、旧协议图引用及旧章节标题。
- 双语阅读器严格数学与来源映射验证：通过。
- 英文 PDF 与双语 PDF 均已重新编译并完成关键页面目视检查。
