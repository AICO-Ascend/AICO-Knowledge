# AOTI 特性介绍

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/aoti/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/aoti/overview.md

# AOTI 特性深度解读

## 【定位】

这篇文档介绍 TorchNPU 中 **AOTInductor (AOTI) 在昇腾 NPU 平台上的特性能力**——即如何将 PyTorch 模型通过 `torch.export` 捕获后，利用 AOTI 编译打包为可在服务端非 Python 环境下运行的动态链接库产物，并提供 Python 与 C++ 两种加载推理接口。

## 【技术要点】

1. **核心 API 三件套**：
   - `torch.export.export()` — 将模型捕获为计算图（支持通过 `dynamic_shapes` 声明动态维度，如 `torch.export.Dim("batch", min=1, max=1024)`）。
   - `torch._inductor.aoti_compile_and_package(exported, package_path=..., inductor_configs=...)` — 执行 AOT 编译并将产物打包为 `.pt2` 文件。
   - `torch._inductor.aoti_load_package(path)` — Python 端加载运行入口。

2. **C++ 加载依赖**：除了 PyTorch 原生库外，Inductor NPU 比 GPU 版本额外依赖 `libtorch_npu.so`，该 `.so` 由 TorchNPU 的编译脚本 `build_libtorch_npu.py` 生成；运行结束需显式调用 `torch_npu::finalize_npu()`。

3. **C++ 加载核心类**：`torch::inductor::AOTIModelPackageLoader` 用于加载 `.pt2`，通过 `loader.get_runner()` 获得 `AOTIModelContainerRunner*`，再以 `runner->run({inputs})` 执行推理。

4. **支持范围**：
   - 各类 NPU 基础算子、自动融合算子、模板类算子、用户手写算子；
   - 动态形状（dynamic shapes）、图下沉叠加；
   - AOTI 产物运行时**自定义解压路径**；
   - C++ 运行环境的动态形状**分档策略**（padding、split）。

5. **构建配置**：使用 `CMakeLists.txt` 模板，`cmake_minimum_required(VERSION 3.18)`，`CXX_STANDARD 17`，通过 `python -c "import torch; print(torch.__path__[0])"` 自动定位 `TORCH_PATH` 与 `TORCH_NPU_PATH`。

6. **使用约束**：
   - **暂不支持叠加 Catlass**，仅做功能兼容支持；
   - 不推荐使用社区已废弃的 `torch._export.aot_compile()` / `torch._export.aot_load()` 接口，若使用应避免在同一进程内多次调用；
   - 示例中示例输入维度为 `(8, 10)`（batch=8, in_features=10），动态 batch 范围 `[1, 1024]`。

## 【关键机制与数据】

**工作原理（原文描述提炼）**：

- **数据流路径**（Python → 产物 → C++）：
  1. 在训练/导出平台用 `torch.export.export(model, example_inputs, dynamic_shapes=...)` 捕获 FX Graph；
  2. 通过 `aoti_compile_and_package` 触发 Inductor 对图的 NPU 后端编译（依赖 Runtime、Triton-Ascend 等 NPU 组件），并将生成的共享库等产物打包进 `model.pt2`；
  3. 推理平台用 Python 的 `aoti_load_package` 或 C++ 的 `AOTIModelPackageLoader("model.pt2")` 加载；
  4. C++ 中通过 `get_runner()` 拿到 `AOTIModelContainerRunner`，再以 `std::vector<at::Tensor>` 作为输入调用 `runner->run(inputs)`。

- **性能数据（原文）**：原文 C++ 示例使用 `std::chrono::system_clock::now()` 对**第二次** `runner->run(inputs)` 计时（即首次 warm-up 之后），输出 `"Inference time: " << elapsed_seconds.count() << "s"`，但**未给出具体数值**。

- **可选 inductor 配置**：示例中演示 `{"max_autotune": True}`，原文称其作用是"turn on more extensive kernel autotuning for better performance"。

- **产物存放路径**：若不指定 `package_path`，原文说明产物"is stored in your system temp directory"。

- **训练-推理解耦建议**：原文提示"if your training platform and inference platform are different, you may choose to save the exported model using `torch.export.save` and then load it back using `torch.export.load` on your inference platform to run AOT compilation"。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

原文文末未提供内部链接列表（"内部链接: (无)"），文档自身涉及但未给出跳转链接的关联点如下：

- **`torch.export.export` / `torch.export.save` / `torch.export.load`** — PyTorch 社区导出工具链，是 AOTI 编译的前置环节；
- **`torch._inductor.aoti_compile_and_package` / `aoti_load_package`** — TorchInductor 社区 AOTI 基础架构，TorchNPU 在此基础上叠加 NPU 依赖；
- **Runtime、Triton-Ascend** — TorchNPU 的 NPU 运行时与算子编译组件，作为 AOTI 编译产物所依赖的底层后端；
- **Catlass** — 昇腾算子库，原文声明暂不支持 AOTI 与 Catlass 叠加；
- **`build_libtorch_npu.py`** — TorchNPU 提供的编译脚本，用于产出 C++ AOTI 推理所必需的 `libtorch_npu.so`；
- **`libtorch_npu.so`** — TorchNPU 在 C++ 环境下的运行时链接库；
- **`max_autotune`** — Inductor 配置项，控制 kernel autotuning 强度。

## 【使用方法】

**1. Python：编译并打包（原文示例代码摘录）**

```python
device = "npu"
model = Model().to(device=device)
example_inputs = (torch.randn(8, 10, device=device),)
batch_dim = torch.export.Dim("batch", min=1, max=1024)
exported = torch.export.export(
    model, example_inputs,
    dynamic_shapes={"x": {0: batch_dim}}
)
output_path = torch._inductor.aoti_compile_and_package(
    exported,
    package_path=os.path.join(os.getcwd(), "model.pt2"),
    inductor_configs={"max_autotune": True},
)
```

**2. Python：加载并运行**

```python
model = torch._inductor.aoti_load_package(os.path.join(os.getcwd(), "model.pt2"))
print(model(torch.randn(8, 10, device=device)))
```

**3. C++：加载并运行（关键调用）**

```cpp
c10::InferenceMode mode;
torch::inductor::AOTIModelPackageLoader loader("model.pt2");
torch::inductor::AOTIModelContainerRunner* runner = loader.get_runner();
torch::Device npu_device(torch::DeviceType::PrivateUse1);
torch::Tensor input = torch::randn({8, 10}, torch::dtype(torch::kFloat32)).to(npu_device);
std::vector<at::Tensor> inputs = {input};
std::vector<torch::Tensor> outputs = runner->run(inputs);
// ... warm-up 后计时:
outputs = runner->run(inputs);
torch_npu::finalize_npu();
```

**4. CMake 构建（关键配置项）**

- `cmake_minimum_required(VERSION 3.18)`；
- 通过 `python -c "import torch; ..."` 自动探测 `TORCH_PATH`、`TORCH_NPU_PATH`；
- `include_directories(${TORCH_NPU_PATH}/include)`；
- `link_directories(${TORCH_PATH}/libs)`；
- `link_directories("/path/to/your/libtorch_npu/lib")`（需替换为真实路径）；
- `target_link_libraries(aoti_example torch_npu "${TORCH_LIBRARIES}")`；
- `CMAKE_CXX_STANDARD 17`；
- 编译产物名：`aoti_example`（来源 `add_executable(aoti_example inference.cpp)`）。

**5. 设备支持**：`Atlas A5 系列产品`。

**6. 使用约束**：
- 暂不支持叠加 Catlass；
- 避免在同进程内多次调用已废弃的 `torch._export.aot_compile()` / `torch._export.aot_load()`。
