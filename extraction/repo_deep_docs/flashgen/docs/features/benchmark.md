# 基准验证

> 仓 `flashgen` · 路径 `docs/features/benchmark.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/flashgen/docs/features/benchmark.md

# FlashGen 基准验证（VBench 评测入口）深度解读

## 【定位】

本文档描述 FlashGen 提供的一个**与模型/算法无关的独立 VBench 评测入口**，解决"如何统一评测 FlashGen 套件下不同算法（DMD2、知识蒸馏、Self-Forcing）或外部模型生成的视频"的问题——只要视频符合标准目录契约，即可复用同一评测入口得到 16 个原始维度及 Quality / Semantic / Total 汇总分数。

---

## 【技术要点】

1. **环境依赖固定三件套**：Ascend NPU + `torch_npu` + AISBench 3.1（需含 VBench 支持）；语义维度还依赖 AISBench 仓内 detectron2 及 VBench 模型缓存（通过 `--vbench_cache_dir` 指定）。
2. **Mini preset 四种组合**：mini_ratio ∈ {`0_01`, `0_05`} × sampling ∈ {`kmeans`, `random`}；默认 `0_05 + kmeans`（43 prompts / 215 videos）；`0_01` 组合为 11 prompts / 55 videos。
3. **每个 prompt 严格 5 个视频**：启动 AISBench 前会严格检查全部 `{prompt}-{0..4}.mp4` 是否存在且非空，输入不完整直接停止，避免有偏得分。
4. **视频目录契约**：平铺布局命名为 `<完整 prompt>-{0..4}.mp4`；同时接受 AISBench 官方维度子目录布局。
5. **metadata 自动查找顺序**：FlashGen 仓库 → FlashGen 父工作区 → 当前目录 → 当前目录父目录；也可显式传入 `final_mini_dataset_*` 的上一级目录或同名目录。
6. **算法无关性**：`--name` 仅作为 AISBench 结果标签（默认取视频目录名），不代表算法类型——任何产出符合目录契约的视频均可复用该入口。

---

## 【关键机制与数据】

- **原文**：评测只读取符合标准目录契约的视频并调用 AISBench，不感知视频使用的模型或生成算法，因此 DMD2、知识蒸馏、Self-Forcing 以及外部模型生成的视频都可以复用同一入口。
- **原文**：默认 preset 是 `0_05 + kmeans`。每个 prompt 固定需要 5 个视频。
- **原文**：启动 AISBench 前会严格检查全部 `{prompt}-{0..4}.mp4` 是否存在且非空；输入不完整时直接停止，避免输出有偏得分。
- **原文**：评测结果位于 `work_dir/results/` 和 `work_dir/summary/`，包括 16 个原始维度以及 Quality、Semantic、Total 汇总分数。
- **数据流（基于原文推断）**：`OUTPUT_ROOT/<mini_ratio>_<sampling>/videos/` 中已生成的视频 → `benchmark.py evaluate` → 检查 `{prompt}-{0..4}.mp4` 完整性 → 调用 AISBench VBench（使用 `--vbench_cache_dir` 提供的本地模型缓存）→ 产出 `work_dir/results/` 与 `work_dir/summary/`。

---

## 【表格解读】

### 表 1：Mini preset 四种组合（原文逐字还原）

| `--mini_ratio` | `--sampling` | 唯一 prompt 数 | 视频数 |
|---|---|---:|---:|
| `0_01` | `kmeans` | 11 | 55 |
| `0_01` | `random` | 11 | 55 |
| `0_05` | `kmeans` | 43 | 215 |
| `0_05` | `random` | 43 | 215 |

**逐行解读**：

- 第 1 行 `0_01 + kmeans`：从完整 VBench prompt 池中以 kmeans 聚类方式采样 1% 子集，对应 11 个唯一 prompt × 每 prompt 5 视频 = 55 视频；用于快速 sanity check。
- 第 2 行 `0_01 + random`：同样 11 prompts / 55 videos，但采样策略为随机；与 kmeans 行形成"采样方法差异 vs. 集合大小相同"的对照实验。
- 第 3 行 `0_05 + kmeans`（默认 preset）：5% 子集，43 prompts / 215 videos；原文明确将其标注为"默认 preset"，代表常规精度验证量级。
- 第 4 行 `0_05 + random`：与第 3 行同量级（43/215）但改用随机采样，可用于评估 kmeans 采样的代表性偏差。

注：原文数字严格表明 prompt 数与 mini_ratio 直接挂钩（0_01→11、0_05→43），sampling 仅影响采样方式不改变集合大小。

### 表 2：常用参数（原文逐字还原）

| 参数 | 说明 |
|---|---|
| `--videos_dir` | 待评测的标准视频目录 |
| `--work_dir` | AISBench 工作目录；默认使用视频目录同级的 `evaluation` |
| `--mini_ratio` | `0_01` 或 `0_05` |
| `--sampling` | `kmeans` 或 `random` |
| `--dataset_root` | 外部 mini metadata 根目录 |
| `--vbench_cache_dir` | 本地 VBench 模型缓存目录 |
| `--max_num_workers` | AISBench 并行任务数，默认 1 |
| `--max_workers_per_gpu` | 每张 GPU/NPU 的并行任务数，默认 1 |

**逐行解读**：

- `--videos_dir`：唯一指向待评测视频的入口，必须满足 `{prompt}-{0..4}.mp4` 契约。
- `--work_dir`：若未指定，默认与 `videos_dir` 同级并命名为 `evaluation`，原命令示例中显式给出 `0_05_kmeans/evaluation` 路径。
- `--mini_ratio` / `--sampling`：二者组合唯一确定 metadata 子集（见表 1）。
- `--dataset_root`：覆盖默认 metadata 自动查找路径，允许直接指向 `final_mini_dataset_0_05` 目录或其父目录。
- `--vbench_cache_dir`：本地离线缓存，避免每次启动都重新下载 VBench 模型。
- `--max_num_workers` / `--max_workers_per_gpu`：两级并行控制；原文示例使用 `--max_num_workers 16 --max_workers_per_gpu 4`，提示在多卡 NPU 环境下可线性扩展吞吐。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

- **算法兼容性层**：文档明确指出 DMD2、知识蒸馏、Self-Forcing 产生的视频均可走该入口，说明本评测模块与 FlashGen 套件中**生成加速算法层**解耦；它是"上游任意算法 → 标准视频 → 下游统一评测"链路中的归一化评测节点。
- **AISBench 依赖**：评测实际工作由 AISBench 3.1 完成（含 detectron2 与 VBench 模型缓存），因此本入口是 AISBench VBench 在 FlashGen 项目内的薄封装。
- **NPU 栈**：与项目对 Ascend NPU + `torch_npu` 的整体要求一致，文档未提供内部链接；上游生成的视频目录需遵循相同契约。
- **结果汇总结构**：`work_dir/results/`（16 个原始维度）与 `work_dir/summary/`（Quality / Semantic / Total）构成 AISBench 标准输出，但具体在 FlashGen 中的二次消费流程原文未涉及。

---

## 【使用方法】

**安装**：

```bash
pip install -e /path/to/AISBench/benchmark --no-deps
```

并按 AISBench VBench 文档准备 detectron2 与 VBench 模型缓存。

**典型运行命令**（原文给出）：

```bash
OUTPUT_ROOT=/path/to/benchmark_outputs
DATASET_ROOT=/path/to/final_mini_dataset_0_05
VBENCH_CACHE=/path/to/vbench-cache

python benchmark.py evaluate \
    --videos_dir "${OUTPUT_ROOT}/0_05_kmeans/videos" \
    --work_dir "${OUTPUT_ROOT}/0_05_kmeans/evaluation" \
    --dataset_root "${DATASET_ROOT}" \
    --mini_ratio 0_05 \
    --sampling kmeans \
    --vbench_cache_dir "${VBENCH_CACHE}" \
    --max_num_workers 16 \
    --max_workers_per_gpu 4 \
    --name wan_dmd_3step
```

**目录布局示例**（原文给出）：

```text
/path/to/vbench-mini/
└── final_mini_dataset_0_05/
    ├── VBench_kmeans_info.json
    └── VBench_random_info.json
```

`--dataset_root` 可传入 `/path/to/vbench-mini` 或 `/path/to/vbench-mini/final_mini_dataset_0_05`，二者皆有效。

**视频命名契约**（原文给出）：

```text
videos/
├── <完整 prompt>-0.mp4
├── <完整 prompt>-1.mp4
└── ...
```

**结果位置**：`work_dir/results/` 与 `work_dir/summary/`，含 16 个原始维度 + Quality / Semantic / Total 汇总分数。
