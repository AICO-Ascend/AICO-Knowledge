# 快速入门

> 仓 `pytorch` · 路径 `docs/zh/user_guide/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docs/zh/user_guide/quick_start.md

# 一体化深度解读：TorchNPU 快速入门

## 【定位】
本文档是 TorchNPU（昇腾 PyTorch 适配插件）的入门级实操指南，面向希望将 GPU 训练脚本迁移到昇腾 NPU 上的开发者，通过"环境准备 + 模型迁移训练 + 进阶开发"三步路径，给出一条以 MNIST CNN 为例的最简自动迁移示范线。

---

## 【技术要点】

1. **目标硬件平台**：以 Atlas 800T A2 训练服务器为示例，需配套安装 NPU 驱动固件与 CANN 软件（Toolkit、ops、NNAL 三件套），安装类型选择"离线安装"，操作系统需通过"兼容性查询助手"匹配。
2. **软件栈组装**：需源码编译安装 PyTorch + TorchNPU 插件（详见 building_from_source.md），并安装与 PyTorch 版本配套的 torchvision（详见 installing_torchvision.md）。
3. **自动迁移触发**：仅需在 GPU 原始脚本上追加三行 import —— `torch_npu`、`torch_npu.npu.amp`、`torch_npu.contrib.transfer_to_npu`，即可启用自动迁移框架；不启用时可走"手工迁移"路径。
4. **AMP 混合精度策略差异**：Atlas 训练系列产品**必须**开启混合精度（架构特性要求）；Atlas A2 训练系列、Atlas A3 训练系列、Ascend 950DT 三类硬件**可选**开启混合精度。
5. **AMP 接入三要素**：在模型与优化器定义之后声明 `scaler = amp.GradScaler()`；将前向计算包裹于 `with amp.autocast():` 上下文；将原 `loss.backward()`/`optimizer.step()` 替换为 `scaler.scale(loss).backward()`、`scaler.step(optimizer)`、`scaler.update()` 三连。
6. **示例训练规模**：MNIST 手写数字识别 CNN，batch_size=64，优化器 SGD(lr=0.1)，epochs=10，保存权重至 `checkpoint.pth.tar`。

---

## 【关键机制与数据】

- **原文:** 训练数据流为「MNIST → DataLoader(batch=64) → imgs/labels.to(device) → CNN(Conv→Pool→Conv→Pool→Flatten→Linear→ReLU→Linear) → CrossEntropyLoss → 反向传播 → 优化器更新」，全程基于 device（GPU 时为 `cuda:0`）调度张量。
- **原文:** 自动迁移机制通过 `from torch_npu.contrib import transfer_to_npu` 触发，使 GPU 风格的 device / 算子调用被透明重定向到 NPU，无需重写模型结构。
- **原文:** AMP 链路工作原理为「`amp.autocast()` 在前向时自动选择 FP16/BF16 算子 → `scaler.scale(loss)` 对 loss 做无损缩放防止下溢 → `scaler.step(optimizer)` 自动 unscaling 后判断是否更新参数 → `scaler.update()` 基于动态 Loss Scale 更新 loss_scaling 系数」。
- **原文:** 训练启动命令为 `python3 train.py`；训练结束后生成 `checkpoint.pth.tar` 权重文件作为迁移成功的判定标志。
- **原文:** 性能数据未在文档中给出（仅有示意配图 `figures/illustration.png`）。

---

## 【表格解读】

| 大模型 | 组件 | 迁移指导 |
|---|---|---|
| Megatron-LM 分布式大模型 | MindSpeed Core 亲和加速模块 | 请参见《[分布式训练加速库迁移指南](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/user-guide/model-migration.md)》。 |
| Megatron-LM 大语言模型 | MindSpeed LLM 套件 | 请参见《[MindSpeed LLM 文档导读](https://gitcode.com/Ascend/MindSpeed-LLM/blob/master/docs/zh/docs_guide.md)》。 |
| Megatron-LM 多模态模型 | MindSpeed MM 套件 | 请参见《[MindSpeed MM 迁移调优指南](https://gitcode.com/Ascend/MindSpeed-MM/blob/master/docs/zh/pytorch/model-migration.md)》。 |
| 大语言模型或多模态模型 | veRL 套件 | 请参见《[veRL 迁移指南](https://github.com/verl-project/verl/blob/main/docs/ascend_tutorial/zh/dev_guide/model_dev/transfer_to_npu_guide.md)》。 |

**逐行解读：**
- 第 1 行：面向分布式大模型场景，使用 MindSpeed Core 进行亲和加速，定位为底层训练加速库。
- 第 2 行：面向 LLM 场景，使用 MindSpeed LLM 套件，覆盖大语言模型完整生命周期。
- 第 3 行：面向多模态模型，使用 MindSpeed MM 套件，提供专门的迁移调优指导。
- 第 4 行：跨模型形态（LLM/多模态）通用方案，使用 veRL 强化学习套件，需到 verl-project 官方仓库获取迁移指南。

四行共同构成 TorchNPU 的"大模型迁移矩阵"——以 Megatron-LM 为底座模型族，按 MindSpeed Core / LLM / MM 与 veRL 四类加速/编排组件横向分流。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游安装路径**：环境准备章节直接引用 `../installation_guide/references/building_from_source.md`（源码编译 PyTorch + TorchNPU）与 `../installation_guide/references/installing_torchvision.md`（配套 torchvision 安装），构成"先安装 → 再跑快速入门"的线性依赖。
- **横向迁移方案分支**：在自动迁移之外提供两条平行路径——一是[混合精度适配](https://gitcode.com/Ascend/ModelZoo-PyTorch/blob/master/PyTorch/docs/zh/mixed_precision_adaptation/adaptation_introduction.md)详解 AMP；二是[手工迁移](https://gitcode.com/Ascend/ModelZoo-PyTorch/blob/master/PyTorch/docs/zh/model_migration/manual_migration.md)作为非自动迁移的备选。
- **下游能力延伸**：进阶开发指向两条主线——[PyTorch 训练模型迁移调优指南](https://gitcode.com/Ascend/ModelZoo-PyTorch/blob/master/PyTorch/docs/zh/README.md)负责训练通用调优；表 1 中 MindSpeed Core / LLM / MM / veRL 四个组件分别链接至分布式训练、大语言模型、多模态、强化学习四大下游迁移文档。
- **硬件产品族耦合**：文档中显式区分了 Atlas 训练系列（必须开 AMP）与 Atlas A2 / A3 / Ascend 950DT（可选 AMP）两条产品线，AMP 启用策略与硬件架构特性强耦合。

---

## 【使用方法】

1. **环境初始化**（原文）：
   - 安装 NPU 驱动固件 + CANN（Toolkit / ops / NNAL），离线安装方式；
   - 源码编译安装 PyTorch 与 TorchNPU 插件；
   - 安装版本对齐的 torchvision。
2. **模型迁移代码注入**（原文 diff）：
   ```python
   import torch_npu
   from torch_npu.npu import amp
   from torch_npu.contrib import transfer_to_npu
   ```
3. **AMP 启用**（原文）：
   ```python
   scaler = amp.GradScaler()           # 模型/优化器之后声明
   with amp.autocast():                # 包裹前向
       outputs = model(imgs)
       loss = loss_func(outputs, labels)
   scaler.scale(loss).backward()       # 缩放后反向
   scaler.step(optimizer)              # 自动 unscaling 更新
   scaler.update()                     # 动态 Loss Scale 系数刷新
   ```
4. **训练启动命令**（原文）：
   ```bash
   python3 train.py
   ```
5. **跳过 AMP 的条件**（原文）：使用 Atlas A2 训练系列、Atlas A3 训练系列或 Ascend 950DT 时可选择跳过步骤 3。
6. **关闭自动迁移的备选**（原文）：未调用 `transfer_to_npu` 时，需参考手工迁移文档进行 device、算子、数据格式等手动适配。

## 图文联合解读

- `illustration.png`: **图文联合解读：**

1) **图像内容**：终端执行`ll`命令的输出，显示当前目录（quick_exp）共712 KB块，其中生成了一个`checkpoint.pth.tar`模型检查点文件（权限`-rw-r--r--`，大小123023字节，时间Mar 24 10:26）。

2) **技术结论**：证明GPU脚本经自动迁移后，在昇腾NPU上成功完成训练并正常保存了模型权重，输出与GPU训练一致的checkpoint产物。

3) **文档关系**：作为"模型迁移训练"章节的结果佐证，配合train.py代码演示"一键迁移"流程的可行性，呼应文档"快速体验GPU→NPU迁移"的论点。
