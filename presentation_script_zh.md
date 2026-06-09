# 课程展示中文讲稿

主题：Queues under Stochastic Priority Switching 的复现结果、诊断与扩展  
建议时长：10-12 分钟  
对应 slides：`slides/main.tex` 共 13 页，包括标题页和结束页

## 总体叙事线

这次展示不要按“我跑了哪些脚本”的顺序讲，而要围绕一个核心问题展开：

> 这篇论文的复现是否成功？如果不是完全成功，哪些部分被可靠复现，哪些部分只得到部分支持，原因可能是什么？

推荐主线是：

1. 先给总判断：工程链路完整，但数值结论是 mixed replication。
2. 解释为什么需要两套参数：论文文本和原始 notebook 存在差异。
3. 逐项看证据：Figure 5、稳定性、bounded Markov、effect-of-H、MC-vs-sim、variance、扩展校准。
4. 最后强调贡献：本项目不仅复现图表，也识别了复现敏感点和参数不一致点。

---

## Slide 1: Title

**建议时间：30 秒**  
**核心作用：说明研究对象和展示目标。**

大家好，我今天展示的是对论文 *Queues under Stochastic Priority Switching* 的复现工作。

这篇论文研究的是一种带随机优先级切换的队列模型。直观地说，系统中的顾客或者患者在等待过程中，优先级不是固定不变的，而是可能随机上升或下降。论文用这个机制解释现实中非 FIFO 的服务顺序，比如医疗等待列表中有些患者会被提前，有些会被推后。

我这次展示的重点不是重新介绍整篇论文，而是回答一个复现问题：基于原论文、原始代码和当前仓库的实验结果，我们到底复现到了什么程度？哪些结论是稳的，哪些结论需要谨慎？

过渡：我先给出总判断，然后再展开每一项证据。

---

## Slide 2: Executive Assessment

**建议时间：1 分钟**  
**核心作用：先给结论，避免后面像流水账。**

这页是我对整个复现结果的总体判断。

我的结论是：当前复现工程链路已经基本完整，主要实验都能跑出 CSV 指标表和图像，因此从工程角度看复现是完成的。但是从数值结论角度看，它不是一个“完全成功”的复现，而是一个 mixed replication。

具体来说，bounded Markov approximation 是最可靠的一部分。两套参数下，随着截断边界增加，平均系统人数、平均逗留时间以及边界量都表现出稳定收敛。

稳定性实验是部分成功：如果使用原始 notebook 中的参数，stable 和 unstable 两种情形可以通过 ADF 检验区分；但如果使用论文文本中的参数，stable-like 轨迹虽然看起来没有爆炸，但 ADF 检验没有通过。

Figure 5 的 overtaking distribution 也只能算部分成功。复现实验可以运行，也能生成类似的分布比较；但是论文候选点 `(3,1)` 在当前实验中不是最优点。

所以这次展示的主结论是：复现框架是完整的，但复现结果需要分层解释，不能简单写成“全部复现成功”。

过渡：要理解为什么会出现这种 mixed result，首先要看复现架构和参数来源。

---

## Slide 3: Replication Architecture

**建议时间：1 分钟**  
**核心作用：说明复现不是手工拼图，而是有可审计流程。**

这页展示的是我搭建的复现架构。

输入主要有四类：第一是原论文；第二是原始仓库中的 source code；第三是原始手术等待列表数据；第四是两套参数来源，一套来自论文文本，一套来自原始 notebook。

在复现层，我没有直接重写原始模型，而是在 `reproduction/` 下面写了一层包装脚本。这样做的好处是，模型核心仍然尽量使用原作者代码，复现脚本负责统一数据处理、参数传递、指标计算和结果输出。

比如 `utils.py` 负责处理原始数据、仿真和指标；每一个 `reproduce_*.py` 对应一个论文实验；`run_parameter_variants.py` 专门用于同时运行论文文本和原始 notebook 两种参数口径。

所有结果都输出为 CSV 和 PNG。CSV 是更重要的，因为它能追溯具体数值；PNG 主要用于展示。

过渡：这里最关键的设计是“参数口径分离”，下一页解释为什么这是必要的。

---

## Slide 4: Why Two Parameter Variants Were Needed

**建议时间：1 分钟 10 秒**  
**核心作用：为后续“同一个实验两种结论”建立逻辑基础。**

这次复现里一个很重要的问题是：论文文本和原始 notebook 中有些参数并不完全一致。

最典型的是稳定性实验。论文文本里使用的是 `theta12=3, theta21=1`，但是原始 notebook 中更接近的是 `theta12=2, theta21=1`。这个差异看起来不大，但对 ADF 检验结论会有影响。

另一个例子是 bounded Markov 以及相关验证实验。论文文本使用的第二类服务率是 `mu2=2.5`，而 notebook 中有一处使用的是 `mu2=1.6667`。两者都可以收敛，但平均人数和平均等待时间的数值水平不同。

所以我没有把它们混在一起，而是分别跑了 paper-text variant 和 original-notebook variant。这样做有两个好处：第一，可以公平地对照论文叙述；第二，也可以检查作者原始代码路径本身能否复现。

最后这行 reporting rule 很重要：复现部分必须使用论文原始指标，比如 Wasserstein 和 MAPE 分别报告；新增的 composite calibration loss 只能放在扩展部分，不能替代论文指标。

过渡：接下来从 Figure 5 开始看具体结果。

---

## Slide 5: Figure 5 Overtaking Distribution

**建议时间：1 分钟 20 秒**  
**核心作用：说明第一个关键复现没有完全成功，并解释为什么。**

Figure 5 的目标是复现论文中 overtaking distribution 的拟合。这里的 overtaking 可以理解为一个患者在服务顺序中被提前或推后的程度。

实验做法是：用原始手术等待列表作为 observed data，然后在一个粗网格上改变 `(theta12, theta21)`，通过 Ciw 离散事件仿真生成模拟分布，再和 observed distribution 比较。

我这里报告两个指标：一个是 Wasserstein distance，主要衡量 overtaking 分布形状差异；另一个是 MAPE，衡量 bumped-up 和 bumped-down 两类等待时间均值的相对误差。

当前结果显示，最小 Wasserstein 出现在 `(1,1)`，值是 3.038；最小 MAPE 出现在 `(2,2)`，值是 0.0946。论文候选点 `(3,1)` 的 Wasserstein 是 3.053，确实非常接近最优 Wasserstein，但它的 MAPE 是 0.366，明显更差。

所以这里不能说论文 Figure 5 的参数结论完全复现。更准确的说法是：复现实验支持“随机优先级切换可以产生类似 overtaking 分布”这个方向性结论，但没有稳定支持 `(3,1)` 是当前设置下的最佳拟合点。

这可能和仿真随机性、trial 数、Ciw 版本或者原论文是否使用更多重复仿真有关。为了进一步确认，需要更多 seeds 和置信区间。

过渡：Figure 5 是经验数据拟合，接下来我们看更偏理论性质的稳定性实验。

---

## Slide 6: Stability ADF Diagnostics

**建议时间：1 分钟 15 秒**  
**核心作用：突出“notebook 参数成功，paper-text 参数不充分”。**

稳定性实验检验的是队列长度轨迹是否表现为平稳。这里使用的是 ADF test，也就是 augmented Dickey-Fuller test。简单来说，如果 p-value 小于 0.05，我们更倾向于认为轨迹是 stationary-like；如果 p-value 很大，就不能拒绝非平稳。

这里我同时报告两套参数。

在 paper-text variant 中，stable-like case 的 p-value 是 0.156，大于 0.05，所以严格来说没有通过平稳性检验。unstable-like case 的 p-value 是 0.856，符合非平稳预期。

但在 original-notebook variant 中，stable-like case 的 p-value 是 0.00385，明显小于 0.05；unstable-like case 是 0.864，仍然非平稳。因此 notebook 参数下可以复现 stable 和 unstable 的区分。

因此这部分的结论是部分成功：稳定性机制本身是能复现的，但它依赖参数口径。不能只用论文文本参数就声称 ADF 结论完全复现。

过渡：相比仿真和统计检验，bounded Markov approximation 的复现结果更稳。

---

## Slide 7: Bounded Markov Approximation

**建议时间：1 分钟 10 秒**  
**核心作用：展示最强复现证据。**

这页是当前复现中最强的一项。

原模型的状态空间是无限的，因此论文采用有限边界截断，也就是 bounded Markov approximation。核心问题是：截断边界 b 增大时，关键指标是否收敛，边界误差是否足够小。

这里看两个参数版本在 `b=22` 时的结果。论文文本口径下，平均系统人数 `L=1.620`，平均逗留时间 `W=1.620`，边界量 `Q(b)=5.88e-5`。原始 notebook 口径下，`L=1.916`，`W=1.916`，`Q(b)=7.61e-5`。

虽然两套参数的数值水平不同，但它们都表现出同样的收敛模式：随着 b 增大，L 和 W 稳定，边界量下降到非常小。

所以这部分可以比较有信心地说复现成功。它支持论文使用有限截断 Markov 链近似无限状态队列的做法。

需要注意一个小 caveat：低 bound 下的某些边界量可能不适合直接解释为概率；最终结论应主要依据较大 bound 下的小边界量。

过渡：有了 Markov 计算框架后，我们可以系统考察 switching matrix H 的影响。

---

## Slide 8: Effect of Switching Matrix H

**建议时间：1 分钟 10 秒**  
**核心作用：讲清楚 B/C 成功，A 有边界问题。**

这页展示的是切换率矩阵 H 对系统指标的影响。

这里有三个 scenario：A 是高优先级类服务更慢，B 是两类服务率相同，C 是高优先级类服务更快。我们在 `h12` 和 `h21` 的网格上计算平均人数、平均逗留时间、sojourn-time variance，以及两个边界检查量 `Q(16)` 和 `P(16)`。

论文中希望在 bound=16 时边界量足够小，比如小于 0.012。当前结果显示，Scenario B 和 C 都满足这个要求：它们的最大 `Q(16)` 分别是 0.00753 和 0.0102，`P(16)` 也很小。

但是 Scenario A 不满足。它的最大 `Q(16)` 达到 0.0822，而且有 181 个网格点超过 0.012。虽然 `P(16)` 基本在阈值附近，但仅看 `Q(16)`，这个边界并不充分。

所以这部分的结论也是部分成功：我们复现了 H 会显著影响系统表现的定性现象，也复现了 B/C 的边界充分性；但不能说所有 scenario 都满足论文的边界检查。

过渡：接下来用 simulation 和 Markov chain 做一个交叉验证。

---

## Slide 9: Markov Chain vs Simulation

**建议时间：55 秒**  
**核心作用：说明这是 sanity check，不是最强证据。**

这页比较 bounded Markov chain 和离散事件仿真的结果。

这里有两个误差：一个是 sojourn time 的相对误差，也就是 W-error；另一个是状态分布之间的 Wasserstein 距离。

从结果看，paper-text variant 的 W-error 大约在 5.93% 到 7.68% 之间，notebook variant 大约在 4.43% 到 6.29% 之间。状态分布误差随着 bound 增大整体下降，notebook variant 的状态分布误差更小一些。

这说明 Markov 链计算和仿真方向上是一致的，至少没有明显矛盾。但因为当前仿真时长相对有限，W-error 还在几个百分点，所以我不会把它作为非常强的收敛证明。

更严谨的说法是：这是一个有用的 sanity check，支持模型实现没有明显错位；如果要作为严格验证，需要更长 simulation、更多 seeds 和置信区间。

过渡：除了均值，论文模型还可以计算 sojourn time 的二阶矩。

---

## Slide 10: Sojourn-Time Variance

**建议时间：55 秒**  
**核心作用：解释 variance 不是乱加指标，而是和吸收链矩公式一致。**

这页展示 sojourn-time variance。

之前的指标主要是平均等待或平均逗留时间，也就是一阶矩。但队列系统中只看均值不够，因为等待时间的波动也很重要。论文中的吸收 Markov 链框架本身可以计算二阶矩，因此 variance 是与原模型一致的。

当前结果中，paper-text variant 在 bound=16 时 `W=1.622`，`Var(W)=5.649`；notebook variant 在 bound=16 时 `W=1.918`，`Var(W)=7.231`。

这些结果和 bounded Markov 的均值结果相互一致。更重要的是，它展示了不同 H 参数不仅会改变平均等待，也会改变等待时间的不确定性。

所以这部分我会归类为成功且合理的扩展可视化：它不是脱离论文的新模型，而是把论文已有的吸收链矩计算更系统地展示出来。

过渡：最后一个实验是 fine-grid calibration，它是扩展，不是原论文复现指标。

---

## Slide 11: Extension Fine-Grid Calibration

**建议时间：1 分钟 15 秒**  
**核心作用：清楚回答“综合指标是否合理”。**

这页是扩展实验，不是原论文复现指标。

原论文 Figure 5 使用的是比较粗的参数网格。我们扩展为更细的 `11x7` 网格，并定义了一个 composite calibration loss，也就是 Wasserstein 加 MAPE。

这个综合指标的意义是筛选参数：Wasserstein 看 overtaking 分布形状，MAPE 看等待时间均值尺度。如果一个点分布形状很好但等待时间均值很差，或者反过来，综合指标可以提醒我们不要只看单一指标。

当前结果显示，最小综合 loss 出现在 `(3,2)`；最小 Wasserstein 出现在 `(1,2)`；最小 MAPE 出现在 `(3.5,2)`；论文点 `(3,1)` 在这个扩展 run 中并不突出。

但是这个指标必须谨慎解释。因为它不是论文定义的指标，而且 Wasserstein 和 MAPE 没有做归一化，`alpha=beta=1` 只是一个简单选择。当前 trials 也只有 3。因此它适合做 sensitivity analysis，不适合替代论文 Figure 5 的原始指标。

一句话总结：综合指标是合理的扩展工具，但不是复现成功与否的判据。

过渡：最后总结这次复现的贡献和局限。

---

## Slide 12: Main Takeaways

**建议时间：1 分钟 20 秒**  
**核心作用：收束所有证据，给出严谨结论。**

最后总结一下。

第一，工程层面，这个仓库已经能够完整生成当前实现范围内的复现结果。每个实验都有对应的脚本、CSV 指标和图像，结果是可追踪的。

第二，数值层面，bounded Markov approximation 是最成功的复现；原始 notebook 参数下的稳定性实验也能复现 stable 和 unstable 的区分；sojourn-time variance 的计算与吸收链公式一致，是合理的结果分析。

第三，也有几处必须谨慎。Figure 5 没有确认 `(3,1)` 是当前 run 中的最佳拟合点；paper-text 参数下的稳定性 ADF 检验没有通过；Scenario A 的 effect-of-H 边界量不满足论文阈值；MC-vs-sim 验证也需要更长仿真才能更有说服力。

因此我对本次复现的最终判断是：这不是一个简单的“成功或失败”二分。更准确地说，它是一个完成度较高的复现工程，并且发现了论文文本、原始 notebook 和随机仿真之间的若干敏感差异。

这也是复现工作的价值所在：不仅是把图画出来，而是检查哪些结论真的稳定，哪些结论依赖参数、随机性或实验设置。

过渡：谢谢大家，下面可以讨论问题。

---

## Slide 13: Thank You

**建议时间：10 秒**  
**核心作用：自然结束。**

我的展示到这里，谢谢大家。欢迎提问。

---

# 可能的提问与回答

## Q1: 你认为这篇论文到底复现成功了吗？

建议回答：

我会说是“部分成功”或者“mixed replication”。工程层面成功，因为所有主要实验链路都能运行并输出结果；理论计算层面，bounded Markov approximation 复现得很好；但是经验拟合和部分统计检验没有完全复现，比如 Figure 5 的最优参数和 paper-text 稳定性 ADF。因此不能写成完全复现成功。

## Q2: 为什么要同时跑论文文本参数和原始 notebook 参数？

建议回答：

因为两者在关键参数上存在不一致。比如稳定性实验的切换率，以及 bounded Markov 中第二类服务率。只跑其中一套会把参数差异误判为代码错误。分开跑以后，我们能更清楚地判断：哪些结论是论文文本支持的，哪些结论是原始代码路径支持的。

## Q3: 新增综合指标是否合理？

建议回答：

合理，但只能作为扩展校准指标。它把 Wasserstein 和 MAPE 合并，用于筛选同时兼顾分布形状和等待时间均值的候选参数。但是它不是论文定义的指标，而且没有做尺度归一化，所以不能替代论文原始复现指标。复现部分仍应分别报告 Wasserstein 和 MAPE。

## Q4: Figure 5 没有完全复现，是否说明论文错了？

建议回答：

不能直接这样说。当前结果只能说明，在我们的代码环境、trial 数和随机种子下，论文候选点不是最优点。它的 Wasserstein 其实很接近最优，只是 MAPE 较差。要判断论文是否有问题，需要更多 seeds、更长仿真、置信区间，以及完全确认原论文的数据处理和仿真设置。

## Q5: 哪个结果最有说服力？

建议回答：

bounded Markov approximation 最有说服力。因为它不是只依赖单次随机仿真，而是通过 Markov 链计算，并且在两套参数下都表现出随截断边界增大而收敛，边界量也下降到很小。

## Q6: Scenario A 的边界量超阈值意味着什么？

建议回答：

它意味着在 high-priority class 服务更慢的 scenario 下，bound=16 对某些 H 参数组合可能不够大。此时有限截断可能截掉了仍然有意义的状态质量，因此不能无保留地使用这个 bound 得出的所有结果。B 和 C 的边界检查通过，但 A 需要更大的 bound 或更细致的边界分析。

## Q7: 如果继续改进，你会优先做什么？

建议回答：

我会优先做三件事。第一，对 Figure 5 增加 seeds 和 trials，报告置信区间；第二，对稳定性实验增加仿真时长并检查 ADF lag sensitivity；第三，对 Scenario A 增大 bound，确认边界量是否能下降到论文阈值以下。这样能把目前的 partial replication 推向更可靠的结论。

---

# 备用短版总结

如果课堂时间只剩 30 秒，可以这样总结：

本次复现的结论是 mixed replication。代码和实验链路已经完整，bounded Markov approximation 复现效果最好，原始 notebook 参数下的稳定性实验也能复现。但是 Figure 5 的论文候选参数没有成为当前 run 的最优点，paper-text 稳定性 ADF 没有通过，Scenario A 的边界量也超过论文阈值。新增综合指标适合作为扩展校准工具，但不应替代论文原始指标。因此，这次复现的主要价值不仅在于生成图表，也在于识别出论文文本、原始 notebook 和随机仿真设置之间的敏感差异。
