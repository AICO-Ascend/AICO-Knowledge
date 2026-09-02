# verl_npu 框架 - 快速开始

> 仓 `mindspeed-rl` · 路径 `verl_npu/docs/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/verl_npu/docs/quick_start.md

# verl_npu 框架快速开始 — 一体化深度解读

---

## 【定位】

这篇文档解决"如何把对上游 verl/transformers 等依赖库的 NPU 适配改动，以 patch 文件 + 插件注入的方式打入 verl_npu 框架，并自动以结构化摘要输出 patch 结果"的问题，描述的是 verl_npu 框架的 patch 注入、版本管理、结果摘要与探测这一整套能力。

---

## 【技术要点】

1. **Patch 注入机制**：通过 `verl_npu/plugin.py` 作为 patch 注入核心逻辑，将 `verl_npu/patch/` 下按仓库分目录（`transformers/`、`verl/`）组织的 `.patch` 文件在运行时打入目标仓库源码，无需 fork 上游仓库。
2. **Patch 生成方式**：使用 `git diff [文件名] > [patch文件名].patch` 命令将改动重定向为 patch 文件，再放入 `verl_npu/patch/` 对应仓库目录下（原文以 `verl/workers/megatron_workers.py` 为例）。
3. **多版本统一管理**：`patch_summary.yaml` 中通过 `versions` 列表管理同一上游仓库的多个 commit 版本，每条记录以 `rev`（commit id）+ `dir`（verl_npu/patch/ 下子目录名）+ `files`（该版本对应的 patch 文件清单）三段式描述；原文示例 `rev: 8365f70e9259c21058bf18f876006f945d2a99de`、`dir: 8365f70e9`。
4. **patch 改动四元化建模**：每个 patch 文件改动被分解为 `class_changes`（类级改动，可多次出现，对应一个文件中可能修改多个类）与 `module_changes`（模块级属性/方法改动）；每个改动动作 `action` 取值可参考 `[added, replaced, deleted, updated]`，也可自定义；类内改动 `kind` 取值可参考 `[method, attribute]`。
5. **Patch Summary 自动打印**：源码安装（`pip install -e .`）后，执行 verl 训练会在日志中输出形如 `================================ NPU Patch Summary ==================================` 的多段摘要，按 `verl` 与 `transformers` 两大块分别列出每个 patch 文件、类名、改动类型与对象（如 `replaced method compute_log_prob`）。
6. **安装前置依赖**：启用 patch 注入前必须先源码安装 `verl` package（原文："需要提前源码安装 verl package"），否则 patch 注入无从生效。

---

## 【关键机制与数据】

**工作原理（原文叙述整合）：**
- 运行时序：开发者在 verl 上游分支完成 NPU 适配改动 → `git diff` 生成 patch → 移入 `verl_npu/patch/<repo>/` 对应目录 → 在 `patch_summary.yaml` 中登记该 patch 的元信息（仓库名、commit id、版本目录、文件清单、改动类型）→ `pip install -e .` 安装插件 → 启动 verl 训练时由 `plugin.py` 触发 patch 注入 → 日志中自动打印分类化 patch summary。
- 摘要打印粒度：Patch Summary 文本中每个 patch 文件独立成段（`Patch File1` … `Patch FileN`），段内进一步分 `Module Changes`（模块级 attribute/method 增减）与 `Class Changes`（每个被改类独立编号 `(1) Patch class: …`、`(2) Patch class: …`，下挂改动的 `action kind name` 三元组）。

**数据流 / 性能数据：**
- 原文日志中可观察到的实际 patch 文件清单（按仓库分类）：
  - **verl 侧 5 个 patch 文件**：
    - `verl.workers.sharding_manager.hybrid_tp_config.py`（新增 6 个 module_attr：`Dict`、`DictConfig`、`HybridTPConfig`、`List`、`Optional`、`dataclass`）
    - `verl.workers.megatron_workers.py`（替换 `ActorRolloutRefWorker.compute_log_prob`、`update_actor` 两个方法）
    - `verl.utils.seqlen_balancing.py`（仅占位，无显式 class/module 改动列出）
    - `verl.workers.rollout.vllm_rollout.vllm_rollout_spmd.py`（替换 `vLLMRollout.__init__`、`_init_dp_env`）
    - `recipe.dapo.dapo_ray_trainer.py`（`RayDAPOTrainer`，仅 1 个类被 patch，未列出 action/kind/name 三元组）
  - **transformers 侧 3 个 patch 文件**：
    - `src.transformers.models.qwen2.modeling_qwen2.py`：模块级 `added method fused_apply_rotary_pos_emb`；类级替换 `Qwen2RMSNorm.forward`、`Qwen2MLP.forward`
    - `src.transformers.models.qwen3_moe.modeling_qwen3_moe.py`：模块级 `added method apply_rotary_pos_emb`；类级替换 `Qwen3MoeSparseMoeBlock.__init__`、`Qwen3MoeRMSNorm.forward`、`Qwen3MoeMLP.forward`
    - `src.transformers.integrations.npu_flash_attention.py`：模块级 `added method unpad_input`、`_prepare_from_posids`；类级新增 `IndexFirstAxis`、`IndexPutFirstAxis`、`pad_input` 共 3 个类
- 性能数据：原文未涉及任何训练吞吐/时延/显存等性能数字。

---

## 【表格解读】

原文无表格（正文以目录树、YAML/代码块、命令行和日志形式呈现，无 markdown 表格）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档明确围绕 verl_npu 框架与其所 patch 的上游仓库之间的关系展开：

- **与上游 verl 框架**：verl_npu 是 verl 在 NPU 场景下的非侵入式补丁层（patch 层），而非 fork；调用 `plugin.py` 在运行时将 patch 打入已 `pip install` 的 verl 源码中（原文："需要提前源码安装 verl package"）。
- **与 transformers 库**：verl_npu 同时管理对 transformers 的 NPU 适配 patch（如 Qwen2RMSNorm、Qwen3MoeSparseMoeBlock 等类级替换、`npu_flash_attention` 模块新增 `unpad_input`/`_prepare_from_pos_emb`/`pad_input`/`IndexFirstAxis`/`IndexPutFirstAxis`）。
- **与 Recipe 模块**：日志中 `recipe.dapo.dapo_ray_trainer.py` 被 patch，关联到 verl 内置的 DAPO 训练配方 `RayDAPOTrainer`。
- **与 Megatron/VLLM 训练后端**：patch 文件覆盖 `verl/workers/megatron_workers.py`（Megatron 后端的 `ActorRolloutRefWorker`）与 `verl/workers/rollout/vllm_rollout/vllm_rollout_spmd.py`（vLLM SPMD rollout），表明 patch 范围同时贯穿训练（Megatron）与推理（vLLM rollout）两端的 worker。
- **与 Sharding/HybridTP 配置模块**：`hybrid_tp_config.py` 被注入 6 个 module_attr（`Dict/DictConfig/HybridTPConfig/List/Optional/dataclass`），关联到 verl 的分片管理与 HybridTP 并行配置子模块。
- 内部链接：原文未提供内部链接。

---

## 【使用方法】

**1. 生成 patch 文件（在 verl 仓库内）：**
```bash
git diff verl/workers/megatron_workers.py > megatron_workers.patch
```
将生成的 `.patch` 文件移入 `verl_npu/patch/verl/`（transformers 的 patch 移入 `verl_npu/patch/transformers/`）。

**2. 在 `patch_summary.yaml` 中登记 patch 元信息，必填字段：**
- `patches[].repo`：被 patch 的仓库名（`verl` / `transformers`）
- `patches[].current_rev`：当前 patch 所针对的 verl_npu 分支 commit id（示例 `8365f70e9259c21058bf18f876006f945d2a99de`）
- `patches[].versions[].rev`：该上游版本对应 commit id（必填）
- `patches[].versions[].dir`：verl_npu/patch/ 下的子目录名（必填，示例 `8365f70e9`）
- `patches[].versions[].files[].name`：patch 文件名（必填，示例 `npu_flash_attention`）
- `patches[].versions[].files[].diff`：当前文件的具体改动描述

**选填字段（在 `diff` 块下）：**
- `class_changes`（列表）：每个元素含 `action`（`added/replaced/deleted/updated`，可自定义）、`name`（类名，如 `IndexFirstAxis`）、`changes`（类内改动列表，每项含 `action`、`kind` 为 `method` 或 `attribute`、`name`）
- `module_changes`（列表）：结构同 class_changes 元素，针对模块级属性/方法

**3. 安装与验证：**
```bash
# 前置：源码安装 verl
pip install -e .    # 在 verl_npu 仓库根目录下执行
```
安装成功后，执行任意 verl 训练，日志中即会打印 "NPU Patch Summary" 区块，分 `verl` 与 `transformers` 两段列出每个 patch 文件的类/模块级改动明细，用于确认 patch 是否生效。
