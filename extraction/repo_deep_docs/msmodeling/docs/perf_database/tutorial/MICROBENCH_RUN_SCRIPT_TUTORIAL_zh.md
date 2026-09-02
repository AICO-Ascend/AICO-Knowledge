# Microbench `xxx_run.py` 生成教程

> 仓 `msmodeling` · 路径 `docs/perf_database/tutorial/MICROBENCH_RUN_SCRIPT_TUTORIAL_zh.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/perf_database/tutorial/MICROBENCH_RUN_SCRIPT_TUTORIAL_zh.md

# 深度解读：Microbench `xxx_run.py` 生成教程

---

## 【定位】

本指南解决的是"如何为 msmmodeling 中某一条 profiling kernel 在 NPU 上生成可真实回放算子的 `<KernelType>_run.py` 脚本"这一问题，使该脚本能作为 `run_all_op.py` 与 `profile_and_update_db.py` 的下游消费者，对 `op_mapping.yaml` + CSV profiling 数据做端到端的算子真实重放。

---

## 【技术要点】

1. **脚本定位与链路**：目标产物是 `tools/perf_data_collection/op_replay/<KernelType>_run.py`，上游数据为 `tensor_cast/performance_model/profiling_database/data/<device>/vllm_ascend/<version>/<KernelType>.csv` 与同版本 `op_mapping.yaml`，下游被 `run_all_op.py` 与 `profile_and_update_db.py` 调用。

2. **`op_mapping.yaml` 是真值源**：必须先查 `torch_npu_reference.<KernelType>.microbench_api` 字段，禁止先猜接口名。原文给出的接口映射例子：
   - `AscendQuantV2 -> torch_npu.npu_quantize`
   - `DynamicQuant -> torch_npu.npu_dynamic_quant`
   - `TensorMove -> torch.Tensor.copy_`
   - `split_qkv_rmsnorm_rope_kernel -> torch.ops.vllm.qkv_rmsnorm_rope`

3. **跨仓搜索顺序固定**：推荐的工作区布局为同级并列 `msmodeling / vllm / vllm-ascend / op-plugin / pytorch / cann-ops-nn / cann-ops-transformer / cann-ops-math / ascend-transformer-boost`；搜索顺序依次为 `op-plugin/docs/context/` → `op-plugin/test/` → `vllm-ascend` Python/Triton 实现 → `OpPlugin/TorchNPU` 注册代码 → CANN/ATB 语义。常用 `git grep -n "torch_npu.npu_dynamic_quant"`、`git grep -n "npu_kv_rmsnorm_rope_cache"`、`git grep -n "qkv_rmsnorm_rope"`、`git grep -n "reshape_and_cache"`。

4. **脚本模板与六大函数**：`xxx_run.py` 固定从 `common` 引入 `build_input_tensor / build_standard_argparser / ensure_npu_available / get_runtime_modules / get_target_data_dir / iter_csv_rows / parse_list_field / parse_shape`，并包含 `build_argparser()`、`build_row_case(row)`、`run_row(csv_path, row_index, row)`、`main()` 四个核心结构。运行时序为：解析 metadata → `build_input_tensor` 重建 Tensor → 最小推导非 Tensor 参数 → 调真实 API → `runtime_torch.npu.synchronize()` → 打印 `[OK]`。

5. **缺失参数必须补但不能泛化**。原文列出六个具体补参规则：
   - `AscendQuantV2`：`axis=-1`、`div_mode=False`、输出 dtype 由 `Output Data Types` 推导；
   - `DynamicQuant`：当前 CSV 只有 `x`，直接 `torch_npu.npu_dynamic_quant(x)`；
   - `TensorMove`：按源 shape/dtype/format 重建 dst 后执行 `dst.copy_(src)`；
   - `ReshapeAndCacheNdKernel`：`slot_mapping` 必须合法且不越界，根据 cache capacity 构造；
   - `KvRmsNormRopeCache`：可能 12 个输入槽位（含空槽位不能丢），`cache_mode / epsilon / is_output_kv` 需从测试/输出 shape 推导；
   - `split_qkv_rmsnorm_rope_kernel`：先注册 `torch.ops.vllm.*`，并处理 `vllm_ascend` 的 import fallback。

6. **Format 与自定义 op 的处理边界**：
   - `Input Formats` 优先看 `ND / FRACTAL_NZ / NCL`：`ND` 直接走 `build_input_tensor`；`FRACTAL_NZ` 优先用 `common.py` 的 `normalize_shape` 与 `npu_format_cast`，除非算子有特殊缓存布局才自写 NZ 展开；`NCL` 类记录值在 `build_input_tensor` 中不做特殊 cast。
   - 当 `microbench_api` 形如 `torch.ops.vllm.*` / `torch.ops._C_ascend.*` / `atb.*` 时，必须额外检查自定义 op 是否已注册、是否需手动 import、`VLLM_ASCEND_PATH` 环境变量或 sibling repo 路径 fallback。

7. **最小验证 + 最小提交**：验证序列为 `py -3 -m py_compile tools/perf_data_collection/op_replay/<KernelType>_run.py` → `py -3 ... --help` → 有 NPU 时 `python ... --device ATLAS_800_A3_752T_128G_DIE --vllm-ascend-version 0.13.0`；提交时只 `git add -- tools/perf_data_collection/op_replay/<KernelType>_run.py`，不携带上游 clone、临时数据、profiling 输出。

---

## 【关键机制与数据】

- **工作原理（端到端数据流）**：CSV 一行 → `parse_list_field / parse_shape` 解析 metadata → `build_input_tensor` 重建 Tensor → 用 `op_mapping.yaml` 中 `microbench_api` 对应的真实 API 执行 → `torch.npu.synchronize()` 强制 NPU 同步 → 输出 `[OK]`。整个回放脚本在 NPU 设备 `ATLAS_800_A3_752T_128G_DIE` 上以 `vllm-ascend` 版本 `0.13.0` 作为目标运行环境（原文: `--device ATLAS_800_A3_752T_128G_DIE` + `--vllm-ascend-version 0.13.0`）。

- **脚本职责契约（5 步）**：原文列出 1) 读取 CSV 每一行；2) 按 `Input Shapes / Input Data Types / Input Formats` 重建输入；3) 调用真实接口执行算子；4) `torch.npu.synchronize()`；5) 输出单行 `[OK]` 日志。

- **CSV 列决策五问**：在写脚本前必须先回答 1) 该 kernel 一行有几个输入槽位？2) 有无空槽位？3) 输出一个还是多个？4) CSV 是否记录了全部参数（含非 Tensor）？5) 当前版本是否只有一种形态。原则是优先支持"当前 CSV 真实存在的行"，不为泛化复杂化。

- **可信度优先级（推断时遵守的层级）**：原文给出的判断原则顺序为 — 先信 `op_mapping.yaml` 给出的 `microbench_api`，再信测试用例，再信实现文件，最后才做必要推断；并且推断必须只为"当前 CSV 真实存在的 case"，并选最小、最稳定、最不容易跑偏的规则。

- **性能数据**：原文无 profiling 数字 / 延迟 / 吞吐数据，本文档只描述生成脚本的方法学，不提供基准性能数据。

---

## 【表格解读】

原文无表格。

（原文中的代码块、YAML 片段与目录树结构不属于"参数表/性能对比/配置项"意义上的表格，因此不在此处以 markdown 表格逐字还原；如需完整保留，请直接参见原文第 2、5、7、8、9、10 节。）

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **下游消费者**：本脚本生成后由 `run_all_op.py` 与 `profile_and_update_db.py` 调用，是 profiling 数据"真实 NPU 回放"环节的可执行载体。

- **上游数据源**：
  - `tensor_cast/performance_model/profiling_database/data/<device>/vllm_ascend/<version>/<KernelType>.csv` — 提供每行 `Input Shapes / Input Data Types / Input Formats / Output Shapes / Output Data Types`。
  - 同版本目录下的 `op_mapping.yaml` — 提供 `torch_npu_reference.<KernelType>.microbench_api` 真值映射。

- **配套工具模块（`common.py`）**：提供 `build_input_tensor / build_standard_argparser / ensure_npu_available / get_runtime_modules / get_target_data_dir / iter_csv_rows / parse_list_field / parse_shape / normalize_shape / npu_format_cast`。所有 `xxx_run.py` 都从 `common` 导入，是脚本结构稳定的基石。

- **同级依赖仓库**：脚本运行时可能 import 的来源 — `vllm`、`vllm-ascend`、`op-plugin`、`pytorch`、`cann-ops-nn`、`cann-ops-transformer`、`cann-ops-math`、`ascend-transformer-boost`；这些通常以同级目录或环境变量 `VLLM_ASCEND_PATH` 方式可达，处理自定义 op（`torch.ops.vllm.*` / `torch.ops._C_ascend.*` / `atb.*`）时尤其需要这些仓库作为语义/测试/实现的真值。

- **Git 提交流程关联**：脚本是 `tools/perf_data_collection/op_replay/` 目录下的独立条目，与 profiling 输出目录、`profiling_database/data/...` 的临时数据以及上游 clone 的内容在 git 层面是隔离的（原文: `git add -- tools/perf_data_collection/op_replay/<KernelType>_run.py`）。

- **设备与版本绑定**：脚本通过 `--device` 与 `--vllm-ascend-version` 两个 CLI 参数与具体 NPU 设备 + vllm-ascend 版本耦合，间接关联到 `op_mapping.yaml` 中版本目录结构。

---

## 【使用方法】

启用方式与命令（原文逐字保留）：

- **语法检查（无需 NPU）**：
  ```bash
  py -3 -m py_compile tools/perf_data_collection/op_replay/<KernelType>_run.py
  ```

- **参数自检（无需 NPU）**：
  ```bash
  py -3 tools/perf_data_collection/op_replay/<KernelType>_run.py --help
  ```

- **真实 NPU 回放（需 NPU 环境，示例设备与版本）**：
  ```bash
  python tools/perf_data_collection/op_replay/<KernelType>_run.py \
    --device ATLAS_800_A3_752T_128G_DIE \
    --vllm-ascend-version 0.13.0
  ```

- **提交前审视与精准提交**：
  ```bash
  git status --short
  git add -- tools/perf_data_collection/op_replay/<KernelType>_run.py
  ```

- **跨仓源码搜索（用于补参与查接口）**：
  ```bash
  git grep -n "torch_npu.npu_dynamic_quant"
  git grep -n "npu_kv_rmsnorm_rope_cache"
  git grep -n "qkv_rmsnorm_rope"
  git grep -n "reshape_and_cache"
  ```

- **配置文件 / 环境变量**（原文有则列出）：
  - `op_mapping.yaml` 中 `torch_npu_reference.<KernelType>.microbench_api` 字段为唯一权威 API 真值。
  - 处理 `vllm_ascend` 自定义 op 时使用 `VLLM_ASCEND_PATH` 环境变量做 fallback（原文仅提及，未给具体变量值定义）。
  - CLI 参数 `--device`（取值例：`ATLAS_800_A3_752T_128G_DIE`）、`--vllm-ascend-version`（取值例：`0.13.0`）。

- **其他配置项**：原文未涉及具体配置文件路径、阈值、batch size 等运行时调参项；本文档定位为脚本生成方法学而非运行期调优文档。
