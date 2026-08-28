# MD-CRGR-DQN：方法、创新边界与确认性实验

## 1. 方法定位

MD-CRGR-DQN（Counterfactual Resource-Divergence-Gated Ranking DQN）在项目原有
MD-DQN 上只增加一个训练期辅助损失。网络结构、标准 DQN Bellman target、uniform
one-step replay、epsilon-greedy、训练轨迹和更新预算均保持不变。方法不使用 Double
DQN、Dueling、PER、n-step、Noisy Network 或 Distributional DQN。

在每个训练状态，环境以无副作用方式预演星上、地面、协同三个动作的一步总成本与
动作后资源。若两个动作造成的资源后果接近，则即时成本排序可作为可靠的弱监督；若
资源后果差异过大，门控关闭该排序，让长期 TD 回报决定 Q 值关系。测试和部署仍只输入
原来的 21 维状态，不调用环境预演。

实现位于：

- `environment.py`: `_transition()` 与 `preview_all_actions()`；
- `crgr_agent.py`: 标准 DQN 与 CRGR 损失；
- `run_crgr_study.py`: 泄漏隔离的校准、配置锁定和确认实验；
- `verify_crgr_archive.py`: 逐模型算法不变量与归档审计；
- `test_crgr.py`: 预演、门控和基础 DQN 等价性测试。

## 2. 创新性边界

Double DQN、Dueling、优先经验回放及其组合均为已有方法，不能作为本文创新：

- van Hasselt et al., *Deep Reinforcement Learning with Double Q-Learning*, AAAI 2016;
- Wang et al., *Dueling Network Architectures for Deep Reinforcement Learning*, ICML 2016;
- Schaul et al., *Prioritized Experience Replay*, ICLR 2016;
- Hessel et al., *Rainbow: Combining Improvements in Deep Reinforcement Learning*, AAAI 2018.

反事实经验生成、动作偏好/排序损失和模型预测辅助任务也分别存在前人工作。本文可主张
的区别不是这些元素本身，而是：**以同一状态下动作后资源向量的分歧作为可信度，只在
资源后果相近时施加解析一步成本的 Q 值排序监督。** 截至 2026-08-25，在 IEEE Xplore、
ACM、PMLR、AAAI、arXiv 与 ScienceDirect 的本轮关键词检索中，未发现相同机制或其在
卫星—地面任务处理模式选择中的应用。

论文应使用“据我们检索，尚未发现相同机制”或“据我们所知”措辞，不能写成无法证明的
绝对全球首创。投稿前还应在 Web of Science、Scopus 和 CNKI 复核题名、摘要、关键词及
前向/后向引文。

## 3. 实验协议

校准使用模型种子 100--103、1,100,000 系列测试轨迹，搜索：

- `ranking_lambda` = 0.1, 0.3, 1.0；
- `gate_tau` = 0.04, 0.06, 0.08。

候选必须在 nominal、burst、link-limited、energy-limited、thermal-stress 五个完整耦合
场景中的平均成本都低于同种子基础 DQN，再以五场景最差相对改善最大者胜出。锁定配置
为 `lambda=1.0, tau=0.08`，锁定哈希见 `outputs_crgr_confirmatory/selected_config.json`。

确认实验使用主实验模型种子 0--4和原 500,000 系列轨迹。每个种子训练 600 回合、每回合
64 步，并对每种设置的 20 条轨迹先求均值。推断单位为五个独立模型种子；95% 区间来自
固定种子 20260825 的 10,000 次配对 percentile bootstrap。

## 4. 确认性结果

完整 CRGR 相对基础 MD-DQN：

| 场景 | 平均成本差 | 95% 配对区间 | 相对改善 | 结论 |
|---|---:|---:|---:|---|
| nominal | -1.6367 | [-2.6480, -0.7096] | 0.5014% | 显著改善 |
| burst | -1.9311 | [-2.7791, -1.0832] | 0.5517% | 显著改善 |
| energy-limited | -1.9823 | [-2.7021, -1.2624] | 0.5497% | 显著改善 |
| thermal-stress | -1.7692 | [-2.6685, -0.8141] | 0.5049% | 显著改善 |
| link-limited | +2.8728 | [-1.4781, 6.6619] | -0.6537% | 未改善 |

因此，预设的“五个场景全部显著改善”总判据未通过。不得写成 CRGR 在所有压力场景稳定
优于 MD-DQN。可以准确表述为：CRGR 在名义、突发、能量受限和热压力四个场景取得稳定
的小幅改善，但在链路受限分布下没有建立优势。

无门控排序在 nominal 和 energy-limited 中显著降低成本，但在 link-limited 中显著变差。
完整 CRGR 将 link-limited 相对无门控排序改善 2.7555，但区间跨零，尚不足以抵消无门控
排序对该场景造成的全部损害。这是后续研究门控定义时最重要的机制证据。

## 5. 复现与验证

```powershell
H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\run_crgr_study.py `
  --stage all --resume --episodes 600 --horizon 64 `
  --calibration-seeds 4 --confirmatory-seeds 5 --test-traces 20 `
  --output H:\degree-dissertation\md_dqn_rsf\outputs_crgr_confirmatory

H:\anaconda\envs\yolo\python.exe H:\degree-dissertation\md_dqn_rsf\verify_crgr_archive.py `
  --output H:\degree-dissertation\md_dqn_rsf\outputs_crgr_confirmatory `
  --reference-models H:\degree-dissertation\md_dqn_rsf\outputs_archive_final_v1\models `
  --report H:\degree-dissertation\md_dqn_rsf\outputs_crgr_confirmatory\verification.json

H:\anaconda\envs\yolo\python.exe -m unittest -v test_crgr.py
```

正式审计通过 55 个模型、4000 条校准记录和 2100 条确认记录。确认阶段五个基础 DQN
检查点与原主实验归档逐权重一致。科学成功判据的真假独立记录在
`outputs_crgr_confirmatory/success_criterion.json`，不能由归档验证结果替代。
