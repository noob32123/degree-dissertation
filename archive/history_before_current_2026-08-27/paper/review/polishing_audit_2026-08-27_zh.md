# 全文润色与主文本纪律审计

日期：2026-08-27  
适用稿件：`paper/source.tex`  
路线：algorithmic / full manuscript / English / generic high-impact journal

## 1. 术语账本

| 规范术语 | 使用规则 |
|---|---|
| DQN family | 名词形式 |
| DQN-family | 仅作复合修饰语 |
| centered full-action DQN objective | 指完整目标或方法 |
| centered full-action supervision | 仅指辅助监督机制 |
| four-step exact planner (MPC-4) | 首次定义，后文使用 MPC-4 |
| model seeds | 独立训练模型的种子 |
| seed blocks | 配对推断中的随机化区组 |

## 2. 最短充分证据链

1. 资源跨任务延续，使卫星地面调度成为序列决策问题。
2. 六个 DQN 目标在相同状态、架构、训练预算和测试轨迹下比较。
3. 五个完全耦合情景中的 30 个 DQN 均值全部低于相应 MPC-4 均值。
4. 名义情景中，DQN 家族为 77.66--78.40，MPC-4 为 90.83，MPC-6 为 89.35，contextual bandit 为 101.00。
5. 家族内部差异小于家族与非 DQN 对照之间的差异，因此主张落在 DQN 家族层面。
6. 软约束、任务真实性、机制识别与更广基线被组织为未来验证路线。

## 3. 结果分配

| 结果 | 分类 | 位置与处理 |
|---|---|---|
| 30/30 DQN 组合优于 MPC-4 | core discovery | 摘要、首个 Results 小节、Discussion、Conclusion，各承担不同功能 |
| DQN 家族内部差异 | necessary support | Results 保留完整统计，Discussion 仅综合解释 |
| MPC 深度与时间 | necessary support | Results 保留 H=1--6 数值，Discussion 强调六步完美预见下的比较 |
| 能量归零与软阈值 | qualification | Results 保留结论改变型边界，详细解决方案转入 Future work |
| 参数敏感性和预览缩放 | robustness | Results 压缩为方向稳定性及后续结构误差验证入口 |
| 动作比例 | descriptive | Results 保留一段，不提升为家族机制结论 |

## 4. 删除、替换与迁移记录

- 将摘要中的局限清单替换为一条必要范围限定和一条未来验证句。
- 删除引言贡献列表中的固定系数防御性说明，完整信息仍保留在 Experimental Design。
- 将 Related Work 从“逐项声明不新”改为“现有路线—本文受控家族评估贡献”。
- 将 Results 中重复的“不能证明”句改为结果导向解释；影响结论的统计限定仍保留。
- 将原 Discussion and Limitations 重构为 Discussion + Future work。
- Future work 按部署约束、机制识别和算法比较三条路线组织。

## 5. 统计与主张位置

- 家族级描述量：30 个目标—情景均值和名义均值范围保留在摘要与首个 Results 小节。
- 家族内主要推断：配对区间、Holm 调整、独立种子 bootstrap 保留在 Results，不在 Discussion 重复完整统计。
- 规划量：成本和每决策时间保留在规划 Results 小节；Discussion 仅综合 H=6 与 DQN 家族的关系。
- 清稿与表格中的数值、宏和统计检验均未改动。

## 6. 词数变化

| 部分 | 润色前 | 润色后 | 变化 |
|---|---:|---:|---:|
| Front matter | 235 | 189 | -46 |
| Introduction | 381 | 312 | -69 |
| Related Work | 269 | 218 | -51 |
| Results | 913 | 747 | -166 |
| Discussion | 564 | 466 | -98 |
| Conclusion | 278 | 249 | -29 |
| 全文合计 | 5,121 | 4,662 | -459 |

方法和实验部分未为追求简短而删除复现信息。全文检查结果为：无超过 30 词的句子、无破折号式 prose、无缺失引文或交叉引用。
