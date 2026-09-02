# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/foundation/FlagAI/examples/Aquila/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/foundation/FlagAI/examples/Aquila/changelog.md

# Aquila Changelog 文档深度解读

## 【定位】

本篇 changelog 文档是 FlagAI 项目下 **Aquila 系列模型** 的**检查点 (checkpoint) 发布日志**, 用于追踪自 2023 年 6 月底至 7 月底约一个月内 5 个版本 (v0.5 → v0.9) 的模型权重发布情况, 并通过 **MD5 哈希** 为每一份权重文件提供完整性校验依据。

---

## 【技术要点】

- **5 次版本迭代**: v0.5 (2023/06/26)、v0.6 (2023/06/27)、v0.7 (2023/07/07)、v0.8 (2023/07/13)、v0.9 (2023/07/24), 发布间隔从 1 天逐步过渡到约 10 天, 呈现稳定节奏。
- **涉及的模型共 6 类**: 基础对话底座 **Aquila-7B**、对话微调版 **AquilaChat-7B**、代码模型 **AquilaCode-7B-NV** / **AquilaCode-7B-TS** / **AquilaCode-multi** / **AquilaCode-py** (即 AquilaCode-python)。
- **v0.9 是结构性转折点**: 首次发布 **AquilaCode-multi** 与 **AquilaCode-py**; 同时宣告 **AquilaCode-7B-NV** 与 **AquilaCode-7B-TS** "temporarily not maintained" (暂停维护); Aquila-7B 与 AquilaChat-7B 权重未更新。
- **MD5 校验机制**: 每一个权重文件都附带 md5 摘要, 用户可通过比对哈希确认下载到的文件未被篡改或损坏。
- **权重稳定性证据**: Aquila-7B 的 md5 `18eac56434db0198494b22b321633785`、AquilaChat-7B 的 md5 `465683009c8b536ef4cca85febb0227c` 在 v0.8 与 v0.9 完全一致, 说明 v0.9 未改动这两个权重。
- **AquilaCode-7B-NV/TS 的 md5 在 v0.5 → v0.8 始终不变** (`91115e72a7fc7f780b410696eae6259c` / `5dae2486bc5a885279be87c13872cd5c`), 即这 4 个版本的代码模型权重没有实质性更新。

---

## 【关键机制与数据】

**工作原理 (原文无更多细节, 以下严格基于原文):**

该 changelog 不描述训练流程或推理机制, 只描述**权重文件的版本管理与校验流程**:

1. **数据流**: 每次发布时, 上游维护者重新生成 (或确认未改动) 部分模型的权重文件 → 对每个权重计算 MD5 → 将文件名与 md5 一并写入 changelog → 用户据此下载并校验。
2. **下游消费方式**: 用户拿到 `Aquila-7B md5: 18eac56434db0198494b22b321633785` 后, 即可在本地运行 `md5sum` 校验文件, 一致才表明下载完整。
3. **关键观察 (原文):** AquilaChat-7B 跟随 Aquila-7B 同步迭代, 在 v0.5 → v0.7 期间 md5 不断变化 (`d927752...` → `f39e3eea...` → `650924d0...`), 至 v0.8 才稳定为 `465683009c8b536ef4cca85febb0227c`, 表明在 6 月底到 7 月中这段时间, 底座与对话模型处于密集微调期。
4. **关键观察 (原文):** v0.9 把"按语言细分" (`NV`/`TS` 可能对应 Natural-Variety / Test-Suite 或类似子集命名, 原文未明确) 的代码模型替换为"按能力域" (`multi` 多语言代码、`py` 专注 Python) 的双轨发布, 说明产品定位发生调整。

---

## 【表格解读】

下表按"逐字还原"原则汇总了原文中全部 5 个版本、所有模型的 md5 值 (短横线 `-` 表示该版本未发布对应权重):

| 版本号 | 发布日期 | Aquila-7B md5 | AquilaChat-7B md5 | AquilaCode-7B-NV md5 | AquilaCode-7B-TS md5 | AquilaCode-multi md5 | AquilaCode-py md5 |
|---|---|---|---|---|---|---|---|
| v0.5 | 2023/06/26 | `13d39993743e66081640c6245da3db48` | `d927752ebc543b2e6ae37217403814ef` | `91115e72a7fc7f780b410696eae6259c` | `5dae2486bc5a885279be87c13872cd5c` | - | - |
| v0.6 | 2023/06/27 | `395d01d9de3437e09aefd7d337a21aca` | `f39e3eea73fddcce7845947f56a7717d` | `91115e72a7fc7f780b410696eae6259c` | `5dae2486bc5a885279be87c13872cd5c` | - | - |
| v0.7 | 2023/07/07 | `63819234d772435ed1b0b95a193c3d04` | `650924d045ba7c715c80f5be485dfe2e` | `91115e72a7fc7f780b410696eae6259c` | `5dae2486bc5a885279be87c13872cd5c` | - | - |
| v0.8 | 2023/07/13 | `18eac56434db0198494b22b321633785` | `465683009c8b536ef4cca85febb0227c` | `91115e72a7fc7f780b410696eae6259c` | `5dae2486bc5a885279be87c13872cd5c` | - | - |
| v0.9 | 2023/07/24 | `18eac56434db0198494b22b321633785` | `465683009c8b536ef4cca85febb0227c` | - | - | `07cfce9440a0fa1ac2768b39d2cf4286` | `3faa85fc03d8fda70a73064f48d02d85` |

**逐行解读:**

- **v0.5 → v0.6**: 4 个模型全部列出, 但 Aquila-7B 与 AquilaChat-7B 的 md5 在 v0.6 已被替换, 说明仅隔 1 天就更新了一版底座/对话权重, 节奏极快; 而 AquilaCode-7B-NV/TS 的 md5 在 v0.5、v0.6 之间不变。
- **v0.6 → v0.7**: Aquila-7B 与 AquilaChat-7B 权重再次刷新 (md5 又换了一组), 代码模型仍未动。
- **v0.7 → v0.8**: 底座与对话模型的 md5 **第 3 次** 更新, 并在此次进入稳定态; 代码模型 md5 始终维持同一对值。
- **v0.8 → v0.9**: 底座/对话权重冻结 (与 v0.8 完全一致), 代码模型发生**整体换代**: `NV`/`TS` 两条旧线被移除, 新增 `multi` 与 `py` (即 AquilaCode-python) 两条新线。这是整个 changelog 中最关键的一次产品结构调整。
- **v0.9 行单独观察**: 它是唯一一次出现 `AquilaCode-multi` (`07cfce9440a0fa1ac2768b39d2cf4286`) 与 `AquilaCode-py` (`3faa85fc03d8fda70a73064f48d02d85`) md5 的行, 也是唯一一次不出现 `AquilaCode-7B-NV`/`AquilaCode-7B-TS` md5 的行。

---

## 【公式解读】

**原文无公式。** 整篇 changelog 仅由版本日期、模型名与 MD5 哈希字符串组成, 不涉及任何训练目标、损失函数、采样公式或伪代码。

---

## 【关联】

由于文末标注"内部链接: (无)", 文档本身不提供超链接, 但从内容上可梳理出以下**模型间的演进关系**:

- **Aquila-7B ↔ AquilaChat-7B**: 同一底座权重, AquilaChat-7B 视为对话/指令微调的派生态; 在 v0.5 → v0.7 期间两者**联动更新** (每次 md5 都同步变化), v0.8 之后**双双冻结**, 提示训练阶段在该节点结束。
- **AquilaCode-7B-NV ↔ AquilaCode-7B-TS**: 同属"按代码子集细分"的旧一代代码模型, 在 v0.5 → v0.8 期间一直维持**完全相同的 md5** (即从始至终未被替换), 仅作为历史基线挂出, 并在 v0.9 被 `multi`/`py` 替代并标"暂停维护"。
- **AquilaCode-multi ↔ AquilaCode-py**: v0.9 新发布的两条线, 关系上构成 **"多语言广度" vs "Python 深度"** 的双轨发布; 原文未给出两者命名后缀 `multi` 与 `py` (即 AquilaCode-python) 的内部定义。
- **版本号轴 (v0.5 → v0.9)**: v0.5 → v0.8 是"持续迭代期" (底座/对话频繁刷新, 代码模型保持), v0.9 是"产品定型期" (底座/对话冻结, 代码模型重构)。整个 changelog 实质上描绘了 Aquila 系列在 2023 年 6 月底至 7 月底的一次**功能收敛**过程。

---

## 【使用方法】

- **校验权重文件 (原文未涉及具体命令, 但 md5 字段的常规用法如下)**: 用户下载权重后, 在本地终端执行 `md5sum <权重文件名>`, 将输出结果与本 changelog 中对应模型、对应版本的 md5 字符串逐字比对, 一致即说明文件完整可信。
- **选择合适的版本 (原文):** 截止 v0.9, 仍处于维护状态的模型为 Aquila-7B、AquilaChat-7B、AquilaCode-multi、AquilaCode-py; AquilaCode-7B-NV 与 AquilaCode-7B-TS 已被标为 "temporarily not maintained", 如需最新代码能力应转向 v0.9 的 multi 或 py 版本。
- **配置文件/环境变量/启动命令**: **原文未涉及** 任何 `python` 启动脚本、`config` 文件路径、训练超参或推理 API 调用示例, 本节无法基于原文进一步展开。
