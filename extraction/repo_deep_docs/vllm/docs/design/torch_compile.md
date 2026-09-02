# `torch.compile` integration

> 仓 `vllm` · 路径 `docs/design/torch_compile.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/torch_compile.md

# `torch.compile` integration 文档深度解读

## 【定位】
本篇文档聚焦 vLLm V1 架构下 `torch.compile` 的集成实践,通过一份 Llama-3.2-1B 的 `vllm serve` 调试日志逐段解读,帮助读者理解 vLLM 中编译缓存目录的生成与复用、动态形状 (Dynamic Shapes) 的三种模式选择,以及 Python 层 (Dynamo) 图捕获所产生的可追踪文件清单。

## 【技术要点】
1. **默认启用**: 在 vLLM V1 架构中, `torch.compile` 默认处于开启状态 (原文: "enabled by default and is a critical part of the framework")。
2. **调试命令**: `VLLM_LOGGING_LEVEL=DEBUG vllm serve meta-llama/Llama-3.2-1B`,用于输出最详尽的编译日志。
3. **缓存目录路径**: `~/.cache/vllm/torch_compile_cache/1517964802/rank_0_0`,其中 `1517964802` 是根据所有相关因素计算得到的哈希值,后缀 `rank_0_0` 标识 rank 信息。直接复制该目录可显著减少启动耗时。
4. **缓存失效因素三件套**:
   - 所有相关 config 的哈希 (见 `config` 目录下的 `compute_hash`)
   - PyTorch 配置的哈希 (见 `compiler_interface.py` 的 `compute_hash`)
   - 模型 `forward` 函数及其调用到的相关函数的源码
5. **缓存关闭与切换**:
   - 关闭:`VLLM_DISABLE_COMPILE_CACHE=1`
   - 切换保存格式为可读源码:`compile_cache_save_format=unpacked` (配置项) 或环境变量 `VLLM_COMPILE_CACHE_SAVE_FORMAT=unpacked`
6. **动态形状三模式**: `BACKED` (默认)、 `UNBACKED` (最强无 guard 保证)、 `BACKED_SIZE_OBLIVIOUS` (实验性,介于二者之间)。配置入口为 `CompilationConfig.dynamic_shapes_config.type`,在线服务侧亦可用 `--compilation-config` JSON 或 `-cc.dynamic_shapes_config.type=unbacked` 点号语法。
7. **关键不变量**: vLLM 保证所有编译在服务请求之前完成 (原文: "we guarantee all the compilation finishes before we serve any requests"),避免请求触发新编译导致响应时间尖刺。
8. **Dynamo 追踪起点**: `xxx/vllm/model_executor/models/llama.py` 第 339 行的 `forward` 函数,Dynamo 会内联展开大量 torch.nn 与 vLLM 自定义模块文件。

## 【关键机制与数据】
- **缓存目录生成流程 (原文: "vLLM will take all the available factors into consideration, and decide a directory to store all the compilation artifact")**: 通过综合 config 哈希、PyTorch 哈希、模型 forward 源码三方面因素,生成如 `1517964802` 这样的数字目录名,保证哈希变化即缓存失效,反之可安全复用。
- **Traced files 列表 (原文日志)**: Dynamo 在追踪 `llama.py:339` 的 `forward` 时,把以下文件纳入编译缓存考量:`polyfills/builtins.py`、`nn/modules/container.py`、`nn/modules/module.py`,以及 vLLM 的 `attention/layer.py`、`distributed/communication_op.py`、`distributed/parallel_state.py`、`model_executor/custom_op.py`、`layers/activation.py`、`layers/layernorm.py`、`layers/linear.py`、`layers/rotary_embedding.py`、`layers/vocab_parallel_embedding.py`、`models/llama.py`。
- **缓存产物文件 (原文日志)**: 日志中可见两类持久化产物: 计算图 `computation_graph.py` 与 Dynamo 变换后代码 `transformed_code.py`,均落在 `~/.cache/vllm/torch_compile_cache/1517964802/rank_0_0/` 目录下。
- **BACKED vs UNBACKED 行为差异 (原文)**:
  - BACKED: dynamo、inductor、autograd 与用户代码均可添加 guard;且 0/1 会被无条件特化到 `0/1/≥2`。
  - UNBACKED: 保证不被 guard、不会 0/1 特化;但分支依赖其值且未定义显式 unbacked 处理时可能抛 Data Dependent Error (DDE);框架正趋向"走通用路径而非抛 DDE"。
  - BACKED_SIZE_OBLIVIOUS: 把 backed 符号当作 unbacked 处理,大多数 0/1 特化被关闭;PyTorch 中仍属实验性,可能被废弃;概率上比 UNBACKED 更不易掉性能。
- **不同模式取舍 (原文: "Choosing the Right Mode")**: BACKED 追求极致性能但 guard 可能被不安全地丢弃;UNBACKED 最保守;BACKED_SIZE_OBLIVIOUS 折中。

## 【表格解读】
原文无表格。文档以代码块 + 日志块为主,未出现 markdown 或纯文本表格。

## 【公式解读】
原文无公式。文档未涉及 LaTeX 公式或伪代码公式,所有机制均以散文与日志示例说明。

## 【关联】
- **`../../vllm/config`**: 缓存哈希考虑因素之一,各 config 文件的 `compute_hash` 函数被用于目录命名与失效判定,本文档将"config 是否变化决定缓存是否安全"这一链路显式落到该目录的实现上。
- **`../../vllm/compilation/compiler_interface.py`**: 文档点名该文件中的 `compute_hash` 函数,负责把 PyTorch 配置侧的因素也纳入缓存键,确保 PyTorch 升级或配置变更后旧缓存不会误用。
- **`cuda_graphs.md`**: 作为同属 V1 编译栈的兄弟文档, `torch.compile` 与 CUDA Graph 在 vLLM 中通常协同工作——前者负责 Python 层图捕获与算子融合,后者负责 CUDA 层 kernel 级图录制。理解 `torch.compile` 路径是理解 CUDA Graph 何时、如何被纳入执行回路的前提。
- **上游博客**: 文档首部 `!!! note` 引用的 [Blog Post](https://blog.vllm.ai/2025/08/20/torch-compile.html),作为"最新进展与更多信息"的入口,与本文档构成 design↔overview 的互补。

## 【使用方法】
- **开启调试日志 (原文)**:
  ```
  VLLM_LOGGING_LEVEL=DEBUG vllm serve meta-llama/Llama-3.2-1B
  ```
- **离线推理切换动态形状 (原文 Python 示例)**:
  ```python
  from vllm import LLM, SamplingParams
  from vllm.config.compilation import CompilationConfig, DynamicShapesConfig, DynamicShapesType

  llm = LLM(
      model="meta-llama/Llama-3.2-1B",
      compilation_config=CompilationConfig(
          dynamic_shapes_config=DynamicShapesConfig(
              type=DynamicShapesType.BACKED_SIZE_OBLIVIOUS  # 或 UNBACKED
          )
      )
  )
  ```
- **在线服务切换动态形状 (原文 Bash 示例)**:
  ```bash
  vllm serve meta-llama/Llama-3.2-1B \
    --compilation-config '{"dynamic_shapes_config": {"type": "unbacked"}}'

  # 或点号简写
  vllm serve meta-llama/Llama-3.2-1B -cc.dynamic_shapes_config.type=unbacked
  ```
- **关闭编译缓存 (原文)**:`export VLLM_DISABLE_COMPILE_CACHE=1`。
- **将缓存导出为可读源码而非二进制 (原文)**:在 `CompilationConfig` 中设置 `compile_cache_save_format=unpacked`,或设置环境变量 `VLLM_COMPILE_CACHE_SAVE_FORMAT=unpacked`。
- **复用已有缓存**: 将整个 `~/.cache/vllm/torch_compile_cache` 目录拷贝到新部署节点即可。
