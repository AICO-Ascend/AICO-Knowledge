# 🟩 NvidiaInfra · NVIDIA 生态知识货架

> AICO-Knowledge 三入口之三 · 货架式呈现（知识分类 + 链接 + 练习代码索引）。
> 内容当前偏少，先上架后优化——主打两条线：
> ① 社区优质实操内容收录（**BasicCUDA**（GitHub 开源练习库）：CUDA/NCCL/PyTorch 显存手把手内容，每篇配可编译代码（仓名即项目名，GitHub 搜索直达））；
> ② 本库 GPU 侧论文深读（Megatron/ZeRO/vLLM 等系统论文本质上是 NVIDIA 栈知识）。
> 配套入口：[📚 知识书架](SHELF.md) · [♨️ AscendInfra 昇腾专区](ascend_infra.html)

## GPU 硬件基础

| 📚 知识源 | 📖 知识分类 | 📜 摘要/备注 |
|---|---|---|
| [GPU硬件: Tesla 经典架构详解](https://zhuanlan.zhihu.com/p/508862848) | GPU 架构 | BasicCUDA 系列 · Tesla→Ampere 演进 |
| [GPU硬件：AI 算力 GPU 发展简史](https://zhuanlan.zhihu.com/p/515584277) | GPU 架构 | 算力代际梳理 |
| [GPU硬件：Tensor Core 和 CUDA Core 区别](https://www.zhihu.com/question/451127498/answer/1813864500) | GPU 架构 | 对位昇腾 Cube/Vector 双单元（见 AscendInfra L6） |
| [GPU硬件: Ampere 架构硬件分析与 A100 测试](https://zhuanlan.zhihu.com/p/559578692) | GPU 架构 | 配 matrixMul 实测 |
| [GPU硬件: MIG 简介与 A100-MIG 实践](https://zhuanlan.zhihu.com/p/558046644) | 虚拟化 | GPU 切分实例 |
| [GPU组网：一图了解 GPU 网络拓扑](https://zhuanlan.zhihu.com/p/678903640) | 集群组网 | NVLink/PCIe/IB 拓扑速览 |

## CUDA 编程（配可编译练习）

| 📚 知识源 | 📖 知识分类 | 📜 摘要/备注 |
|---|---|---|
| [CUDA 入门：矩阵乘从 CPU 到 GPU](https://zhuanlan.zhihu.com/p/573271688) | CUDA C++ | matrix_multiply 代码（GitHub: BasicCUDA 仓）（渐进优化版本） |
| [CUDA 全局坐标计算 & Grid/Block/threadIdx 映射](https://zhuanlan.zhihu.com/p/675603584) | CUDA C++ | 代码（GitHub: BasicCUDA 仓） |
| [CUDA 实践：ScaledMaskSoftmax 融合算子](https://zhuanlan.zhihu.com/p/675794183) | CUDA C++ | fused_softmax 代码（GitHub: BasicCUDA 仓） |
| CUDA 入门：虚拟地址 VMM 基本使用（GitHub: BasicCUDA 仓） | 显存 | vmm 代码（GitHub: BasicCUDA 仓） |
| [CUDA 入门：常用技巧/方法](https://zhuanlan.zhihu.com/p/584501634) | CUDA C++ | common_methods（GitHub: BasicCUDA 仓） |
| [20 行代码入门 PyTorch 自定义 CUDA/C++ 扩展](https://zhuanlan.zhihu.com/p/579395211) | PyTorch 扩展 | torch_ext 代码（GitHub: BasicCUDA 仓） |
| BasicCUDA 仓主页（GitHub: BasicCUDA 仓） | 总入口 | 每模块独立文件、`make && ./` 即跑 |

## NCCL 集合通信

| 📚 知识源 | 📖 知识分类 | 📜 摘要/备注 |
|---|---|---|
| [NCCL 算法的拓扑建立与通路选择](https://zhuanlan.zhihu.com/p/735606197) | GPU 网络 | Ring/Tree 拓扑 · 对位昇腾 HCCL（见 AscendInfra L5） |
| [NCCL 初始化日志解读](https://zhuanlan.zhihu.com/p/719917835) | GPU 网络 | 排障入门 |
| [NCCL C++ 示例（一）基础用例](https://zhuanlan.zhihu.com/p/718639633) · [（二）socket 多机](https://zhuanlan.zhihu.com/p/718040976) · [（三）多流并发](https://zhuanlan.zhihu.com/p/716805174) · [（四）AlltoAll_Split](https://zhuanlan.zhihu.com/p/718765726) | GPU 网络 | nccl 代码（GitHub: BasicCUDA 仓） |

## PyTorch 显存管理

| 📚 知识源 | 📖 知识分类 | 📜 摘要/备注 |
|---|---|---|
| [PyTorch 显存管理源码解析（一）](https://zhuanlan.zhihu.com/p/680769942) · [（二）](https://zhuanlan.zhihu.com/p/681651660) · [（三）](https://zhuanlan.zhihu.com/p/692614846) | PyTorch | torch1.13_mem_rationale（GitHub: BasicCUDA 仓） |
| [PyTorch 显存可视化与 Snapshot 数据分析](https://zhuanlan.zhihu.com/p/677203832) | PyTorch | torch_mem_snapshot（GitHub: BasicCUDA 仓） · 书架[辅助工具区](SHELF.md#辅助工具)有配套在线工具 |

## 系统论文（本库深读 · GPU 栈）

| 📚 知识源 | 📖 知识分类 | 📜 摘要 |
|---|---|---|
| [Megatron-LM（TP/PP 原点）](https://arxiv.org/abs/1909.08053) | 训练系统 | [萃取总结](../extraction/deep/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.md) |
| [ZeRO 显存优化](https://arxiv.org/abs/1910.02054) | 训练系统 | [萃取总结](../extraction/deep/zero-memory-optimizations-toward-training-trillion-parameter-models.md) |
| [MegaScale 万卡工程](https://arxiv.org/abs/2402.15627) | 训练系统 | [萃取总结](../extraction/deep/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.md) |
| [PagedAttention（vLLM 原点）](https://arxiv.org/abs/2309.06180) | 推理系统 | [萃取总结](../extraction/deep/efficient-memory-management-for-large-language-model-serving-with-pagedattention.md) |
| [SGLang / RadixAttention](https://arxiv.org/abs/2312.07104) | 推理系统 | [萃取总结](../extraction/deep/sglang-efficient-execution-of-structured-language-model-programs.md) |
| [CUDA-Agent（Agentic RL 生成 kernel）](https://arxiv.org/abs/2602.24286) | 前沿 | [萃取总结](../extraction/deep/cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation.md) |

---

*货架管理说明：本页手工维护（内容少，暂不进生成器）；后续按 bookshelf_build.py 同规格自动化。
收录标准：GPU/CUDA/NCCL 侧的实操型内容（带可跑代码优先）+ 本库 GPU 栈论文深读。*
