# 环境变量列表

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/environment_variables_summary.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/environment_variables_summary.md

# 一体化深度解读：inductor-ascend 环境变量列表

---

## 【定位】

本文档是 **Ascend for PyTorch 社区中 inductor-ascend 模块的开发者环境变量参考手册**，系统罗列了在 inductor-ascend 编译优化全流程（Catlass 后端、FX 图优化、多流并行、离散访存、自动 Tiling、CostModel 预筛选、精度调试等）中所有可调用的环境变量名称、所属类别、默认值及简要语义，供开发者按需启用/微调以控制编译行为。

---

## 【技术要点】

1. **Catlass 后端开关组（6 个变量）**：通过 `CATLASS_EPILOGUE_FUSION`、`TORCHINDUCTOR_CATLASS_ENABLED_OPS`（默认 `"mm,addmm,bmm"`）、`TORCHINDUCTOR_MAX_AUTOTUNE`（默认 `0`）、`TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS`（默认 `"ATEN,TRITON,CPP"`，加入 Catlass 后端需追加 `"CATLASS"`）、`TORCHINDUCTOR_NPU_CATLASS_DIR`（默认 `""`）、`TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING`（默认 `0`）将社区 CUTLASS 体系的能力映射到昇腾 Catlass。
2. **FX Graph 图优化粒度控制**：`SHUT_DOWN_FX_PASS_LIST` 用于精确控制生效的 pass，默认为 `""`（即所有 pass 都生效），可裁剪 pass 集合。
3. **计算图多流并行调度**：`ENABLE_PARALLEL_SCHEDULER` 控制是否开启计算图多流并行调度策略，默认 `False`，置 `True` 时开启多流并行。
4. **离散访存融合策略**：`INDUCTOR_INDIRECT_MEMORY_MODE`（默认 `"simd_simt_mix"`）控制是否开启离散访存的融合及融合方式；`USE_STORE_IN_CAT`（默认 `False`）控制 Inductor 对 cat 融合的行为。
5. **自动 Tiling 与多进程编译**：`FASTAUTOTUNE`（默认 `0`）、`INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE`（默认 `0`）、`TORCHINDUCTOR_COMPILE_THREADS`（默认 `32`）、`TORCHNPU_PRECOMPILE_THREADS`（默认 `os.cpu_count() // 2`，即最大核数的一半；大于 `1` 时使用并发编译）。
6. **分核/限核与 CostModel 预筛选**：`NPU_DEVICE_LIMIT` 控制最多可使用的 Cube 与 Vector 核数（默认全部核）；`INDUCTOR_ASCEND_ENABLE_COSTMODEL`（默认 `0`）+ `INDUCTOR_ASCEND_COSTMODEL_RATIO`（默认 `0.25`）实现 CostModel 预筛选。
7. **精度/调试与日志开关**：`INDUCTOR_ASCEND_CHECK_ACCURACY`（启用 Triton 后端精度对比工具，dump 单算子用例；启用时自动开启 `INDUCTOR_ASCEND_DUMP_FX_GRAPH`）、`INDUCTOR_ASCEND_DUMP_FX_GRAPH`（在 `INDUCTOR_ASCEND_CHECK_ACCURACY` 或 `AOTI_ASCEND_DEBUG_KERNEL` 启用时自动开启）、`INDUCTOR_ASCEND_LOG_LEVEL`（默认 `WARNING`）。
8. **Triton-Ascend nddma 转置能力**：`TORCHINDUCTOR_NDDMA` 启用 Triton-Ascend load 随路转置能力，文档指出"A2、A3 代际理论性能无差异，A5 代际通过底层 nddma 特性做转置加速，转置性能有明显增益"。

---

## 【关键机制与数据】

- **多进程/多线程编译模型（原文）**：`TORCHINDUCTOR_COMPILE_THREADS` 默认 `32`，`TORCHNPU_PRECOMPILE_THREADS` 默认 `max_precompiled_thread_num = os.cpu_count() // 2`，大于 `1` 时启用并发编译。
- **CostModel 预筛选（原文）**：`INDUCTOR_ASCEND_ENABLE_COSTMODEL` 默认 `0`（不启用），启用后通过 `INDUCTOR_ASCEND_COSTMODEL_RATIO` 控制预筛选后保留的 config 比例，默认 `0.25`。
- **Catlass 后端集成（原文）**：Catlass 是社区 CUTLASS 体系的昇腾映射，库路径通过 `TORCHINDUCTOR_NPU_CATLASS_DIR` 指定，若路径配置错误会给出 WARNING 并跳过尝试引入 Catlass 后端。
- **max autotune 后端候选（原文）**：`TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS` 默认 `"ATEN,TRITON,CPP"`；若需将 Catlass 纳入候选，需追加 `"CATLASS"`。
- **精度调试链式触发（原文）**：启用 `INDUCTOR_ASCEND_CHECK_ACCURACY` 会自动启用 `INDUCTOR_ASCEND_DUMP_FX_GRAPH`；`INDUCTOR_ASCEND_DUMP_FX_GRAPH` 同样会在 `AOTI_ASCEND_DEBUG_KERNEL` 启用时被自动启用。
- **nddma 代际性能差异（原文）**：`TORCHINDUCTOR_NDDMA` 启用 Triton-Ascend load 随路转置能力——A2、A3 代际理论性能无差异，A5 代际通过底层 nddma 特性做转置加速，转置性能有明显增益。
- **多流并行调度开关（原文）**：`ENABLE_PARALLEL_SCHEDULER` 默认 `False`，开启后切换到多流并行调度策略。
- **分核/限核语义（原文）**：`NPU_DEVICE_LIMIT` 控制最多可使用的 Cube 与 Vector 核数，默认值为全部 Cube 与 Vector 核。
- **离散访存融合模式（原文）**：`INDUCTOR_INDIRECT_MEMORY_MODE` 默认 `"simd_simt_mix"`，用于同时控制是否开启离散访存融合以及融合方式。

---

## 【表格解读】

下表为原文 **表 1 环境变量列表** 的逐字还原：

| 环境变量类型     | 环境变量名称 | 简介                                                                                                                                                                                              |
|------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Catlass          | CATLASS_EPILOGUE_FUSION | 是否开启 catlass cv 融合，与社区 CUTLASS_EPILOGUE_FUSION 保持一致，社区环境变量为 CUTLASS_EPILOGUE_FUSION，默认值为 `0`                                                                                    |
| Catlass          | TORCHINDUCTOR_CATLASS_ENABLED_OPS | catlass 可作用于的矩阵乘类的算子类型，与社区 TORCHINDUCTOR_CUTLASS_ENABLED_OPS 保持一致，社区环境变量为 TORCHINDUCTOR_CUTLASS_ENABLED_OPS，默认值为 `"mm,addmm,bmm"`                                  |
| Catlass          | TORCHINDUCTOR_MAX_AUTOTUNE | 开启 max autotune 功能，该环境变量与社区一致，默认值为 `0`                                                                                                                                          |
| Catlass          | TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS | 确认 max autotune 可尝试的后端有哪些，该环境变量与社区一致，若想尝试 Catlass 的后端，请在该环境变量中配置上 `"CATLASS"`，默认值为 `"ATEN,TRITON,CPP"`                                                  |
| Catlass          | TORCHINDUCTOR_NPU_CATLASS_DIR | 环境中 catlass 库的路径，与社区 TORCHINDUCTOR_CUTLASS_DIR 保持一致，社区环境变量为 TORCHINDUCTOR_CUTLASS_DIR，若路径配置错误，会有 WARNING 信息提示，并跳过尝试引入 catlass 后端的功能，默认值为 `""` |
| Catlass          | TORCHINDUCTOR_PROFILE_WITH_DO_BENCH_USING_PROFILING | 该环境变量与社区一致，用于管理 autotune 过程中是否使用 profiling 进行 autotune，`"0"` 为不使用 profiling，`"1"` 为使用 profiling，默认值为 `0`                                                       |
| FXGraph 图优化   | SHUT_DOWN_FX_PASS_LIST | 用于精确控制生效的 pass，默认为 `""`，即所有 pass 都生效                                                                                                                                             |
| 计算图多流并行   | ENABLE_PARALLEL_SCHEDULER | 是否开启计算图多流并行调度策略，默认为 `False`，即不开启计算图多流并行调度策略，设置为 `True`，表示开启计算图多流并行调度策略                                                                          |
| 离散访存         | INDUCTOR_INDIRECT_MEMORY_MODE | 是否开启离散访存的融合以及配置融合方式，默认值为 `"simd_simt_mix"`                                                                                                                                    |
| 离散访存         | USE_STORE_IN_CAT | 用于控制 Inductor 针对 cat 融合的行为，当前默认为 `False`                                                                                                                                            |
| 自动 Tiling 优化 | FASTAUTOTUNE | 控制是否使用 fast autotune，默认值为 `0`                                                                                                                                                             |
| 自动 Tiling 优化 | INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE | 控制是否启用 batch profiler，默认值为 `0`                                                                                                                                                            |
| 自动 Tiling 优化 | TORCHINDUCTOR_COMPILE_THREADS | 多进程编译进程数量，与社区保持一致，默认值为 `32`                                                                                                                                                    |
| 自动 Tiling 优化 | TORCHNPU_PRECOMPILE_THREADS | 控制多线程编译线程数量，默认为最大核数的一半（`max_precompiled_thread_num = os.cpu_count() // 2`），大于 `1` 时，使用并发编译                                                                          |
| 分核 / 限核     | NPU_DEVICE_LIMIT | 控制最多可使用的 Cube 和 Vector 的核数，默认值为全部 cube 和 vector 核                                                                                                                                |
| CostModel        | INDUCTOR_ASCEND_ENABLE_COSTMODEL | 控制是否启用 CostModel 预筛选，默认值为 `0`                                                                                                                                                          |
| CostModel        | INDUCTOR_ASCEND_COSTMODEL_RATIO | 控制 CostModel 预筛选后保留的 config 比例，默认值为 `0.25`                                                                                                                                            |
| 其他             | INDUCTOR_ASCEND_CHECK_ACCURACY | 开启 triton 后端精度对比工具，dump 单算子用例。当启用时，会自动启用 `INDUCTOR_ASCEND_DUMP_FX_GRAPH` 功能，默认值为空。                                                                                  |
| 其他             | INDUCTOR_ASCEND_DUMP_FX_GRAPH | dump 可执行的单算子用例，用于调试和问题排查。当 `INDUCTOR_ASCEND_CHECK_ACCURACY` 或 `AOTI_ASCEND_DEBUG_KERNEL` 启用时，会自动启用此功能，默认值为空。                                                  |
| 其他             | INDUCTOR_ASCEND_LOG_LEVEL | 设置 Inductor-Ascend 日志等级，控制日志输出的详细程度，默认值为 `WARNING`。                                                                                                                           |
| 其他             | TORCHINDUCTOR_NDDMA | 启用 Triton-Ascend load 随路转置能力。在 A2、A3 代际理论性能无差异。在 A5 代际会通过底层 nddma 特性做转置加速，转置性能有明显增益。                                                                     |

**逐行解读**：

- **Catlass 类**：把 PyTorch 社区 CUTLASS 体系的 6 个开关平移到昇腾 Catlass，覆盖 epilogue 融合、算子白名单、max autotune 启停、autotune 候选后端、库路径、是否使用 profiling autotune。`TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS` 默认不含 `"CATLASS"`，开发者必须显式追加才能让 Catlass 进入 autotune 候选。
- **FXGraph 图优化**：通过 `SHUT_DOWN_FX_PASS_LIST` 字符串（pass 列表）裁剪 FX pass 子集，默认全开，是细粒度调试 FX pass 的"白/黑名单"式开关。
- **计算图多流并行**：`ENABLE_PARALLEL_SCHEDULER` 是布尔型总开关，决定是否进入多流并行调度路径。
- **离散访存**：`INDUCTOR_INDIRECT_MEMORY_MODE` 是枚举型（默认 `"simd_simt_mix"`），同时控制"是否启用"与"融合方式"两个维度；`USE_STORE_IN_CAT` 是布尔开关，决定 Inductor 对 cat 的融合行为。
- **自动 Tiling 优化**：`FASTAUTOTUNE` 与 `INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE` 决定是否走快速 autotune 与 batch profiler；后两个变量控制并行编译规模（`TORCHINDUCTOR_COMPILE_THREADS=32` 是社区默认的进程级并行，`TORCHNPU_PRECOMPILE_THREADS=os.cpu_count()//2` 是 NPU 侧的线程级并行）。
- **分核 / 限核**：`NPU_DEVICE_LIMIT` 通过限制可用 Cube/Vector 核数实现手工降配，默认全开。
- **CostModel**：`INDUCTOR_ASCEND_ENABLE_COSTMODEL=0` 时关闭预筛选；启用后 `INDUCTOR_ASCEND_COSTMODEL_RATIO=0.25` 决定保留 25% 的 config 用于后续精确调优。
- **其他**：精度调试与日志/转置三类。其中 `INDUCTOR_ASCEND_CHECK_ACCURACY` 与 `INDUCTOR_ASCEND_DUMP_FX_GRAPH` 之间存在**联动**——前者会自动启用后者；后者还会在 `AOTI_ASCEND_DEBUG_KERNEL` 启用时联动开启，构成"调试链"。
- **`TORCHINDUCTOR_NDDMA`**：跨代际的转置优化开关，特别标注 A5 代际受益。

---

## 【公式解读】

**原文无公式**。

（仅出现一处伪代码式表达式 `max_precompiled_thread_num = os.cpu_count() // 2`，含义为"最大预编译线程数等于 CPU 逻辑核数整除 2"，已在上一节随 `TORCHNPU_PRECOMPILE_THREADS` 一并解读，此处不算独立公式。）

---

## 【关联】

- **TorchNPU 环境变量体系**：本文档明确把 TorchNPU 的环境变量参考外链至《TorchNPU 环境变量参考》，说明 inductor-ascend 的开关运行在 TorchNPU 插件之上，PyTorch 框架 → TorchNPU 适配层 → inductor-ascend 编译后端 三者形成栈式依赖。
- **CANN 环境变量体系**：基于 CANN 构建 AI 应用的通用环境变量参考外链至《CANN 环境变量参考》，意味着 inductor-ascend 最终落地的算子执行仍受 CANN 运行时环境变量影响。
- **PyTorch 社区 CUTLASS 体系**：Catlass 类的 6 个变量中有 5 个明确"与社区 TORCHINDUCTOR_CUTLASS_* 保持一致"，说明 inductor-ascend 选择以"环境变量重命名 + 默认值对齐"的方式桥接 CUTLASS 命名规范。
- **`AOTI_ASCEND_DEBUG_KERNEL`**：在 `INDUCTOR_ASCEND_DUMP_FX_GRAPH` 的简介中被引用为联动触发条件，提示 AOTI（Ahead-Of-Time Inductor）调试路径与 dump 功能存在耦合。
- **内部链接**：文末提供的内部链接为 0，所有跳转均为外链（TorchNPU / CANN 官方文档），本文档不依赖本仓其他 markdown 文档。

---

## 【使用方法】

本文档为**环境变量速查表**，未涉及具体启用命令或 API 调用方式。所有 21 个环境变量的启用方式统一为在运行 Python 脚本前通过 shell export 或 `os.environ` 设置，例如下面给出几个**原文直接给出的配置示例**：

1. **启用 max autotune 并纳入 Catlass 后端**（原文组合）：
   - `TORCHINDUCTOR_MAX_AUTOTUNE=1`
   - `TORCHINDUCTOR_MAX_AUTOTUNE_GEMM_BACKENDS="ATEN,TRITON,CPP,CATLASS"`（原文：在该环境变量中配置上 `"CATLASS"`）
2. **指定 Catlass 库路径**（原文）：`TORCHINDUCTOR_NPU_CATLASS_DIR=<catlass_install_path>`，原文明确"若路径配置错误，会有 WARNING 信息提示，并跳过尝试引入 catlass 后端的功能"。
3. **开启 CostModel 预筛选**（原文）：`INDUCTOR_ASCEND_ENABLE_COSTMODEL=1`，并按需调整 `INDUCTOR_ASCEND_COSTMODEL_RATIO`（默认 `0.25`）。
4. **开启多流并行**（原文）：`ENABLE_PARALLEL_SCHEDULER=True`。
5. **裁剪 FX pass**（原文）：`SHUT_DOWN_FX_PASS_LIST` 设为非空字符串以精确控制生效的 pass。
6. **精度调试链路**（原文）：启用 `INDUCTOR_ASCEND_CHECK_ACCURACY` 即自动启用 `INDUCTOR_ASCEND_DUMP_FX_GRAPH`；也可直接启用 `INDUCTOR_ASCEND_DUMP_FX_GRAPH`；或在启用 `AOTI_ASCEND_DEBUG_KERNEL` 时联动触发 dump。
7. **调整日志级别**（原文）：`INDUCTOR_ASCEND_LOG_LEVEL=DEBUG/INFO/WARNING/...`（默认 `WARNING`）。
8. **启用 nddma 转置**（原文）：`TORCHINDUCTOR_NDDMA=1`，A5 代际将获得转置性能增益。
9. **调整预编译并发**（原文）：`TORCHNPU_PRECOMPILE_THREADS=<n>`（默认 `os.cpu_count() // 2`），`>1` 时使用并发编译；`TORCHINDUCTOR_COMPILE_THREADS=<n>`（默认 `32`）控制多进程编译进程数。

> 注：以上为根据原文 21 个变量的"简介/默认值"列整理的配置示例；原文**未**给出 `export`、`.env` 文件或 Python `os.environ` 等具体命令模板，也未给出 API 层调用方式。
