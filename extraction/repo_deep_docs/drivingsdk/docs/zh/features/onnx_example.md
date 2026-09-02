# 训推一体示例

> 仓 `drivingsdk` · 路径 `docs/zh/features/onnx_example.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docs/zh/features/onnx_example.md

# ONNX 训推一体示例 深度解读

## 【定位】

本文档以 MSDA（MultiScaleDeformableAttn）算子为载体，演示 mx_driving 自定义算子从 PyTorch 模型 ONNX 导出 → domain 统一 → ATC 转 OM → 离线推理 → 精度对齐 的完整工程闭环，为本仓库 ONNX 使用提供可复制的最小工程范本。

---

## 【技术要点】

1. **算子载体与依赖**：示例使用 `mx_driving.multi_scale_deformable_attn`，需提前安装 `torch_npu` 与 `mx_driving`，并在模型侧通过 `model.npu()` 与 `tensor.npu()` 将计算图强制放到 NPU 上，确保 ONNX 导出时算子落域为昇腾自定义实现而非默认 ATen。
2. **ONNX 导出规范**：`torch.onnx.export` 调用时显式设置 `opset_version=11` 与 `OperatorExportTypes.ONNX`，输入名固定为 `["value", "shapes", "level_start_index", "sampling_locations", "attention_weights"]`，输出名为 `["outputs"]`，为后续 ATC 解析提供稳定接口契约。
3. **domain 统一策略**：默认经 `torch.onnx.export` 导出的模型可能携带多个 domain，需借助 MagicONNX（`OnnxGraph.keep_default_domain()`）将其收敛到默认域，否则 ATC 会因多 `domain_version` 报错（FAQ 中明确指出）。
4. **ATC 转换关键参数**：转换命令显式启用 `--framework 5`（ONNX）、`--soc_version Ascend910B2`、`--op_select_implmode high_precision`、`--precision_mode must_keep_origin_dtype`、`--log debug`，并通过 `ASCEND_CUSTOM_OPP_PATH` 与 `LD_LIBRARY_PATH` 指向 `mx_driving/packages/vendors/customize/` 下的 op_api 与 opp 路径，使 ATC 能识别仓库自定义算子。
5. **输入数据落盘约定**：依据导出脚本的形状约定构造 `.bin` 输入，`input1/value` 为 float16，`input2/shapes` 与 `input3/level_start_index` 为 int64，`input4/sampling_locations` 与 `input5/attention_weights` 为 float16，与 ONNX 模型输入 dtype 完全对齐。
6. **精度对齐方法**：通过 msame 生成的 `msda_output_0.bin` 与 NPU 端直接调用 `multi_scale_deformable_attn` 的 `golden` 张量进行 shape/dtype 对齐后人工对比，作为离线推理可信度的判定依据。

---

## 【关键机制与数据】

- **原文：MSDA 输入形状约定**：`bs, num_levels, num_heads, num_points, num_queries, embed_dims = 2, 1, 8, 4, 40000, 32`；`shapes = torch.tensor([[200, 200] * num_levels]).reshape(num_levels, 2).long()`，即 1 层特征图、每层 200×200；`num_keys = 200*200 = 40000`，与 `num_queries` 数值上相同。
- **原文：张量 dtype 转换链路**：`value`、`sampling_locations`、`attention_weights` 在 NPU 上跑前显式 `.half()`（float16），而 `shapes` 与 `level_start_index` 保持 `long`（int64），与后文 ATC `--precision_mode must_keep_origin_dtype` 形成 dtype 不被改写的约束闭环。
- **原文：随机化策略**：`value = rand(...) * 0.01`（小幅度）、`sampling_locations = rand(...) * 1.2 - 0.1`（覆盖负值，符合归一化坐标语义）、`attention_weights = rand(...) + 1e-5`（避免全零），三者共同保证算子数值路径被有效触发。
- **原文：环境变量桥接**：ATC 阶段通过 `pip3 show mx_driving` 解析安装路径 `$mx_driving_path`，并拼接 `$mx_driving_path/mx_driving/packages/vendors/customize/` 作为 `ASCEND_CUSTOM_OPP_PATH`，同时把 `op_api/lib/` 注入 `LD_LIBRARY_PATH`，这是 mx_driving 自定义算子被 ATC 识别的必要前置。
- **原文：执行工具栈**：OM 推理使用 msame 工具（仓库 `https://gitee.com/ascend/tools/tree/master/msame`），命令形如 `./msame --model ./msda.om --input ./inputs/input1.bin,.../input5.bin --output ./msame/out/ --outfmt BIN --loop 1`，输出落盘为 `msda_output_0.bin`。
- **原文：成功判据**：ATC 输出包含 “ATC run success, welcome to the next use.” 即视为 OM 生成成功；精度对齐阶段通过对比 `golden` 与 `output` 完成。
- **原文：性能/吞吐数据**：文档未给出 msda 算子的时延、吞吐或精度误差等量化性能指标，仅提供精度对齐脚本，无基准数据可引用。

---

## 【表格解读】

**原文无表格**。本文档以代码块 + 命令行片段为主，未出现参数表、性能对比表或配置项表。所有配置信息（如 ATC 命令、环境变量、形状常数）均散落在代码与文字说明中，已在「技术要点」与「关键机制与数据」中按原文逐项保留。

---

## 【公式解读】

**原文无公式**。文档未给出 LaTeX 数学公式或伪代码形式的算子定义；MSDA 的数学定义依赖 `mx_driving.multi_scale_deformable_attn` 接口自身，文档仅给出其调用方式与输入形状约束，相关形状推导（如 `num_keys = Σ H_i · W_i`、`level_start_index = cumsum`）以 PyTorch 张量操作形式呈现，而非符号化公式。

---

## 【关联】

- **安装前置依赖**：FAQ 中 “No parser is registered for Op” 问题指向 `../installation/installation.md#前置依赖-1`，说明本文档依赖安装章节中关于 protoc 编译、ONNX 插件构建的指引；若 docker 中 `mx_driving` 包未带 ONNX 插件，需按安装文档补齐。
- **算子实现位置**：FAQ “Can not find Node xxx custom infer_datatype func” 指向 `kernels/multi_scale_deformable_attn/op_host/` 下的 cpp 文件与 `IMPL_OP_INFERSHAPE` 宏，说明 ONNX→OM 路径上的形状/类型推导由算子 Host 侧实现提供，本文档示例所选 MSDA 算子在该目录下具备完整支持，其他算子需参照此模式补齐。
- **上下游工具链**：
  - 上游：依赖 `torch_npu`（将算子绑定到 NPU 设备域）与 `mx_driving` 自定义 OP 包（提供 MSDA 实现及 opp 注册信息）。
  - 下游：经 ATC 生成 OM 模型后，接 msame 离线推理工具，最终与 NPU 上 `multi_scale_deformable_attn` 直调结果做精度对账。
- **外部仓库依赖**：
  - MagicONNX（`https://gitee.com/Ronnie_zheng/MagicONNX`）用于多 domain 收敛，仅在模型存在多 `domain_version` 时介入。
  - msame（`https://gitee.com/ascend/tools/tree/master/msame`）为 OM 离线执行入口。

---

## 【使用方法】

1. **环境准备（原文涉及）**
   - 安装 `mx_driving` 与 `torch_npu`，并将模型/张量 `.npu()` 化。
   - 如 docker 内包缺失 ONNX 插件，按 `../installation/installation.md#前置依赖-1` 编译 protoc 重新构建。
   - 多 domain 模型需先 `pip` 安装 MagicONNX。

2. **ONNX 导出（原文命令）**
   ```shell
   python export_msda_onnx.py    # 生成 ./msda.onnx
   ```

3. **domain 统一（原文命令，多 domain 时执行）**
   ```python
   from magiconnx import OnnxGraph
   graph = OnnxGraph('msda.onnx')
   graph.keep_default_domain()
   graph.save('msda.onnx')
   ```

4. **ATC 转 OM（原文命令）**
   ```shell
   pip3 show mx_driving                                          # 记为 $mx_driving_path
   export ASCEND_CUSTOM_OPP_PATH=$mx_driving_path/mx_driving/packages/vendors/customize/
   export LD_LIBRARY_PATH=$mx_driving_path/mx_driving/packages/vendors/customize/op_api/lib/:$LD_LIBRARY_PATH
   atc --framework 5 --output msda --soc_version Ascend910B2 \
       --model msda.onnx --op_select_implmode high_precision \
       --precision_mode must_keep_origin_dtype --log debug
   ```
   成功标志：“ATC run success, welcome to the next use.”

5. **离线推理（原文命令）**
   - 先按 msame 仓库 readme 安装；生成输入：
     ```shell
     python gen_inputs.py    # 在 ./inputs/ 下生成 input1~input5.bin
     ```
   - 执行：
     ```shell
     ./msame --model ./msda.om \
             --input ./inputs/input1.bin,./inputs/input2.bin,./inputs/input3.bin,./inputs/input4.bin,./inputs/input5.bin \
             --output ./msame/out/ --outfmt BIN --loop 1
     ```

6. **精度对齐（原文命令）**
   - 运行文档末尾提供的 Python 脚本，将 `msda_output_0.bin` 与 `multi_scale_deformable_attn` 直调 golden 进行对比。

7. **常见报错（原文 FAQ 提示）**
   - “No parser is registered for Op”：① docker 中 mx_driving 缺 ONNX 插件，按安装文档重编 protoc；② 未设置 `ASCEND_CUSTOM_OPP_PATH` / `LD_LIBRARY_PATH`。
   - “Can not find Node xxx custom infer_datatype func”：参考 `kernels/multi_scale_deformable_attn/op_host/` 的 `IMPL_OP_INFERSHAPE` 行补齐 inferShape/inferDtype。
   - “Optype xxx of ops kernel is unsupported”：核对模型输入 dtype 与算子支持类型是否一致。
   - “The model has 2 domain_version fields, but only one is allowed”：未执行 domain 统一步骤，按上文 MagicONNX 流程处理。
