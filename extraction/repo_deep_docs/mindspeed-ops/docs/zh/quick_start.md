# 快速入门

> 仓 `mindspeed-ops` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-ops/docs/zh/quick_start.md

## 【定位】

本文档面向初次使用 MindSpeed Ops 的开发者，提供从环境安装验证、首个 Triton 融合算子调用、ACLNN 融合算子调用到单元测试执行的完整入门路径。

## 【技术要点】

1. **适用范围与基础要求**
   - MindSpeed Ops 支持 `Ascend 950 系列产品`、`Atlas A3 训练系列产品`等昇腾产品，具体支持范围见[算子清单](supported_operators.md)。
   - 开发者需要具备基础 PyTorch 使用经验和初级 Python 开发能力。

2. **环境准备与安装验证**
   - 先按照[软件安装](install_guide.md)安装驱动固件、CANN、PyTorch、`torch_npu`、Triton-Ascend，并完成 MindSpeed Ops 源码安装。
   - 执行算子前加载默认 CANN 环境变量：
     ```shell
     source /usr/local/Ascend/ascend-toolkit/latest/set_env.sh
     ```
     该路径是 root 用户默认安装场景，若 `set_env.sh` 实际位置不同，需要替换路径。
   - 使用以下命令分别验证 NPU 和 MindSpeed Ops：
     ```shell
     npu-smi info
     python -c "import mindspeed_ops; print('MindSpeed Ops loaded successfully')"
     ```

3. **首个 Triton 融合算子**
   - 通过 `FusedCrossEntropyLossFunction.apply(logits, loss_weight, labels)` 调用 `FusedCrossEntropyLoss`。
   - 示例使用 `torch.float16`，并设置：
     ```python
     torch.manual_seed(42)
     N, vocab_size = 1024, 16384
     ```
   - `logits` 形状为 `[N, vocab_size]`，即 `[1024, 16384]`；`loss_weight` 形状为 `[1024]`；`labels` 为 `torch.int32`。
   - 融合算子完成前向损失计算后，示例调用 `loss.backward()`，并打印 `logits.grad.float().norm().item()`。

4. **Triton 示例的精度对照**
   - 融合算子将交叉熵、逐项损失权重和归约合并计算。
   - PyTorch 基准先使用 `logits.float()` 和 `loss_weight.float()`，再计算交叉熵并求和。
   - 文档强调示例输出是随机数据结果，实际运行可能变化；融合算子结果应与基准结果基本一致。

5. **ACLNN 融合算子**
   - `AddRmsNormBias` 将残差加法与 RMS 归一化融合为单 Kernel 执行。
   - ACLNN 算子依赖 C++ 扩展和自定义算子包；源码安装时，检测到 NPU或设置 `SOC_VERSION` 环境变量即可完成 ACLNN 编译。
   - 示例在 NPU 上创建两个形状为 `4 × 256` 的 `float16` 输入，以及形状为 `256` 的 `gamma`，调用：
     ```python
     y, rstd, x = npu_add_rms_norm_bias(x1, x2, gamma)
     ```
   - 快速入门示例通过 `torch.allclose(..., rtol=1e-3)` 验证残差结果 `x`，没有在该示例中给出 `y` 和 `rstd` 的独立数值断言。

6. **单元测试**
   - 运行完整测试集：
     ```shell
     cd MindSpeed-Ops
     pytest tests/unit_tests
     ```
   - 运行单个融合交叉熵算子测试：
     ```shell
     pytest tests/unit_tests/triton/test_fused_cross_entropy_loss.py
     ```
   - 单元测试以 CPU 高精度实现和 PyTorch 小算子实现作为双精度标杆。

## 【关键机制与数据】

**原文：**整体流程为“环境安装与生效 → NPU及 MindSpeed Ops 可用性验证 → Triton 融合交叉熵前向与反向 → ACLNN 融合 RMSNorm → 单元测试”，每一步都提供独立命令或示例脚本，便于首次调用时逐层定位问题。

**原文：**Triton 示例的数据流是：随机生成 `logits`、`loss_weight` 和 `labels`，通过 `FusedCrossEntropyLossFunction.apply(...)` 得到标量损失，再执行反向传播取得 `logits.grad`，最后使用 PyTorch `F.cross_entropy` 构建独立参考结果。

**原文：**示例随机数据和主要配置为：

- 随机种子：`42`
- 数据类型：`torch.float16`
- `N=1024`
- `vocab_size=16384`
- `logits`：`[1024, 16384]`
- `loss_weight`：`[1024]`
- `labels`：`torch.int32`

**原文：**文档给出的随机示例输出为：

```text
fused loss: 12.65625
grad norm of logits: 127.521484375
reference loss: 12.656312942504883
fused_cross_entropy_loss operation exec successfully!
```

这些数值只用于展示运行格式，文档明确要求以实际运行为准，并未将其定义为固定性能或精度数据。

**原文：**ACLNN 示例的数据流是：先计算 `x1 + x2` 得到残差结果 `x`，再根据 `x` 的均方值计算 `rstd`，最后完成归一化并乘以 `gamma` 得到 `y`。函数按 `y, rstd, x` 顺序返回三个结果。

**原文：**ACLNN 示例的输入配置和校验条件为：

- `x1`、`x2`：形状 `[4, 256]`，`float16`
- `gamma`：形状 `[256]`，`float16`
- 执行设备：固定为 `"npu"`
- `x` 的比较容差：`rtol=1e-3`

**原文：**文档没有提供算子耗时、吞吐率、加速比或不同实现的性能对比，因此没有可用于判断性能提升比例的数据。

## 【表格解读】

|接口名|说明|
|----|----|
|`get_available_device()`|自动探测当前可用的计算设备，NPU环境下返回`"npu"`，便于脚本在无NPU环境时回退到CPU调试。|
|`FusedCrossEntropyLossFunction.apply(logits, loss_weight, labels)`|融合交叉熵损失算子入口，`torch.autograd.Function`形式，支持自动微分。|

1. **`get_available_device()`**
   - 负责自动识别当前可用计算设备。
   - NPU 环境下返回 `"npu"`。
   - 在没有 NPU 时可用于回退到 CPU 调试，使快速入门脚本不必把设备类型完全写死。

2. **`FusedCrossEntropyLossFunction.apply(logits, loss_weight, labels)`**
   - 是 Triton `FusedCrossEntropyLoss` 算子的调用入口。
   - 三个参数分别对应融合交叉熵输入、损失权重和标签。
   - 接口采用 `torch.autograd.Function` 形式，示例随后通过 `loss.backward()` 验证反向计算，并读取 `logits.grad`。

## 【公式解读】

原文中的计算公式以代码注释形式给出。

```text
loss = (cross_entropy(logits, labels) * loss_weight).sum()
```

- `cross_entropy(logits, labels)`：对输入 `logits` 和标签 `labels` 计算交叉熵。
- `logits`：融合算子的主要输入张量，示例形状为 `[1024, 16384]`。
- `labels`：交叉熵对应的标签张量，示例使用 `torch.int32`。
- `loss_weight`：与交叉熵结果逐项相乘的损失权重，示例形状为 `[1024]`。
- `*`：逐项乘法，将交叉熵结果与损失权重组合。
- `sum()`：对逐项结果求和，生成最终标量损失 `loss`。
- 整体含义：先计算交叉熵，再乘以 `loss_weight`，最后归约得到反向传播所使用的标量损失。

```text
x = x1 + x2; rstd = 1/sqrt(mean(x^2) + eps); y = (x * rstd) * gamma
```

- `x1`：第一个残差输入，示例形状为 `[4, 256]`。
- `x2`：第二个残差输入，示例形状为 `[4, 256]`。
- `x`：两个残差输入相加后的结果。
- `x^2`：对 `x` 的各元素求平方。
- `mean(x^2)`：对平方结果求均值；原文没有指定具体的归约维度。
- `eps`：加在均方值上的 epsilon 项；原文未给出其数值或进一步定义。
- `sqrt(...)`：计算 `mean(x^2) + eps` 的平方根。
- `rstd`：`1/sqrt(...)` 的结果，即原式中的逆均方根缩放因子。
- `rstd`：作为归一化缩放因子参与后续计算。
- `gamma`：归一化后的缩放参数，示例形状为 `[256]`。
- `y`：最终输出，由 `x * rstd` 归一化后再乘以 `gamma` 得到。
- 原式完整表达了 `AddRmsNormBias` 的三段处理：残差相加、计算逆均方根、执行带 `gamma` 的归一化。

## 【关联】

1. **[软件安装](install_guide.md)**
   - 是环境准备部分的上游依赖。
   - 负责驱动固件、CANN、PyTorch、`torch_npu`、Triton-Ascend 和 MindSpeed Ops 的安装。
   - ACLNN 源码安装还需要参考[方式二源码安装](install_guide.md#方式二源码安装)，以完成 ACLNN 编译。

2. **[算子清单](supported_operators.md)**
   - 在概述中用于说明 MindSpeed Ops 支持的昇腾产品。
   - 在文档末尾用于查阅当前提供的全部算子及其详细说明。
   - `FusedCrossEntropyLoss` 和 `AddRmsNormBias` 都属于该清单所覆盖的算子范围。

3. **[fused_cross_entropy_loss算子](triton/fused_cross_entropy_loss.md)**
   - 是快速入门中 Triton 示例的详细算子说明。
   - 快速入门只展示最小调用和精度对照脚本，算子级介绍以该链接为准。

4. **[AddRmsNormBias算子](aclnn/add_rms_norm_bias.md)**
   - 是 ACLNN 示例的详细算子说明。
   - 快速入门侧重展示安装依赖、调用形式和基础结果验证。

5. **[FAQ](FAQ.md)**
   - 位于使用流程末端。
   - 当安装、导入、设备调用或算子执行遇到问题时，用于进一步排查。

## 【使用方法】

1. **准备环境并加载 CANN 变量**
   ```shell
   source /usr/local/Ascend/ascend-toolkit/latest/set_env.sh
   ```
   如果 CANN 安装路径不同，需要改用实际 `set_env.sh` 路径。

2. **验证 NPU 和 MindSpeed Ops**
   ```shell
   npu-smi info
   python -c "import mindspeed_ops; print('MindSpeed Ops loaded successfully')"
   ```

3. **运行 Triton 融合交叉熵示例**
   - 在 MindSpeed Ops 根目录创建 `quick_start_example.py`。
   - 自动获取设备并初始化示例数据：
     ```python
     device = get_available_device()
     torch.manual_seed(42)
     dtype = torch.float16
     N, vocab_size = 1024, 16384
     ```
   - 调用融合算子并执行反向传播：
     ```python
     loss = FusedCrossEntropyLossFunction.apply(logits, loss_weight, labels)
     loss.backward()
     ```
   - 运行：
     ```shell
     python quick_start_example.py
     ```

4. **运行 ACLNN 融合算子**
   - 使用 `"npu"` 设备。
   - 创建两个 `[4, 256]` 的 `float16` 输入和一个 `[256]` 的 `float16` `gamma`。
   - 调用：
     ```python
     y, rstd, x = npu_add_rms_norm_bias(x1, x2, gamma)
     ```
   - 残差结果按 `rtol=1e-3` 验证：
     ```python
     expected_x = x1 + x2
     assert torch.allclose(x.float(), expected_x.float(), rtol=1e-3)
     ```

5. **运行单元测试**
   ```shell
   cd MindSpeed-Ops
   pytest tests/unit_tests
   ```

   单个算子测试：
   ```shell
   pytest tests/unit_tests/triton/test_fused_cross_entropy_loss.py
   ```
