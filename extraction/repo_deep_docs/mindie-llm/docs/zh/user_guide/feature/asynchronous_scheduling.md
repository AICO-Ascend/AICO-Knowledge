# 异步调度

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/asynchronous_scheduling.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/asynchronous_scheduling.md

# 异步调度 (Asynchronous Scheduling) 文档深度解读

## 【定位】

本文档描述昇腾自研大模型推理引擎 MindIE LLM 中"异步调度"特性的能力——通过让 CPU 与 NPU 任务并行执行,利用模型推理耗时掩盖数据处理耗时,以提升系统整体资源利用率与吞吐量的调度算法。

## 【技术要点】

- **核心机制**:基于"模型推理耗时掩盖数据处理耗时"的调度思路,利用 CPU 与 NPU 任务在不同计算资源上可并行的特性,使用多线程实现异步调度,打破同步推理下 CPU/NPU 串行使用造成的等待浪费。
- **同步推理三阶段划分**:
  - 阶段一:请求调度与准备阶段(CPU 上执行)
  - 阶段二:模型推理与采样阶段(NPU 上执行)
  - 阶段三:结果判断与响应阶段(CPU 上执行)
- **已知代价**:进入 EOS(终止推理)状态的请求会被重复计算一次,带来 NPU 计算资源和内存资源的微小浪费。
- **适用场景**:max_batch_size 较大,且输出长度较长的场景。
- **互斥约束**:不可与 Look Ahead、Memory Decoding 同时使用;暂不支持 `n`、`best_of`、`use_beam_search` 等多序列推理相关后处理参数。
- **部署范围**:支持 PD 混部和 PD 分离两种场景;PD 分离部署时仅需在 D 节点开启环境变量。

## 【关键机制与数据】

- **工作原理(原文)**:在同步推理场景下,一次推理被划分为"请求调度与准备(CPU)→ 模型推理与采样(NPU)→ 结果判断与响应(CPU)"三个阶段;其中 CPU 与 NPU 任务因计算资源不同可并行执行,异步调度正是利用这一并行性,以多线程方式让 CPU 端的数据处理与 NPU 端的模型推理重叠运行,从而提高整体资源利用率与吞吐量。
- **代价说明(原文)**:异步调度模式下,已进入 EOS 状态的请求会被"重复计算一次",导致 NPU 计算资源与内存资源存在"微小"浪费——文档明确以"微小"二字限定其程度,未给出具体百分比/数值。
- **适用边界(原文)**:仅当 max_batch_size 较大、且输出长度较长时,该特性的收益才足以覆盖 EOS 重复计算带来的开销。
- **性能数据**:原文未提供具体的 TPS、时延、加速比等量化指标,也未提供任何 benchmark 数字。

## 【表格解读】

**原文无表格。** 文档中未出现任何参数表、性能对比表或配置项表格。

## 【公式解读】

**原文无公式。** 文档中未给出 LaTeX 或伪代码形式的数学公式或调度公式。

## 【关联】

根据文末信息,本文与以下外部特性/模块/文档存在关联:

- **PD 混部与 PD 分离部署**:本文特性是支持这两种部署形态的;在 PD 分离场景下需特别注意"仅在 D 节点开启环境变量"。
- **互斥特性**:
  - **Look Ahead**:与异步调度不可同时使用。
  - **Memory Decoding**:与异步调度不可同时使用。
- **受限参数(后处理相关)**:`n`、`best_of`、`use_beam_search`——这些多序列推理相关后处理参数在异步调度模式下暂不支持,意味着若启用异步调度,涉及 beam search 多序列输出或 `n>1`、`best_of>1` 的请求将无法走通。
- **配套工具**:调优阶段使用 **AISBench** 工具,详细说明位于《MindIE Motor 开发指南》中的"配套工具 > 性能/精度测试工具"章节(原文未给出该文档的具体内部链接路径)。
- **下游配置文档(内部链接)**:[配置参数说明(服务化)](../user_manual/service_parameter_configuration.md)——本文"执行推理"步骤 3 要求按该章节配置服务化参数,因此该文档是异步调度特性的必要上游/配套参考。

## 【使用方法】

原文给出了完整启用流程,逐条如下:

1. **设置环境变量(开启异步调度)**:
   ```bash
   export MINDIE_ASYNC_SCHEDULING_ENABLE=1
   ```
   - **PD 分离部署特别说明**:请仅在 **D 节点** 设置上述环境变量,P 节点不设置。

2. **打开服务配置文件 `config.json`**:
   - **whl 包安装方式**:
     ```bash
     cd {MindIE安装目录}/mindie_llm/
     vi conf/config.json
     ```
   - **run 包安装方式**:
     ```bash
     cd {MindIE安装目录}/latest/mindie-service
     vi conf/config.json
     ```

3. **配置服务化参数**:具体参数说明见[配置参数说明(服务化)](../user_manual/service_parameter_configuration.md)章节(原文未在本文件内列出具体配置项)。

4. **启动服务**:
   - **whl 包安装方式**:
     ```bash
     mindie_llm_server
     ```
   - **run 包安装方式**:
     ```bash
     ./bin/mindieservice_daemon
     ```

5. **性能调优**:使用 **AISBench** 工具开始调优;AISBench 的详细说明需参见《MindIE Motor 开发指南》中"配套工具 > 性能/精度测试工具"章节(原文未给出该文档的直接内部链接)。

> **汇总开关**:整篇文档中真正涉及"打开/关闭"异步调度的唯一开关是环境变量 `MINDIE_ASYNC_SCHEDULING_ENABLE=1`;`config.json` 内的具体服务化参数项未在原文中给出,需跳转至 `service_parameter_configuration.md` 查看。
