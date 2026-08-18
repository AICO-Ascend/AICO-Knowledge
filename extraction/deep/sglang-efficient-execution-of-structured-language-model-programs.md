# SGLang — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记：文本技术点提炼 + 跨论文关系。独立文件，extract_phase1 重跑不丢。
> 论文：SGLang: Efficient Execution of Structured Language Model Programs · arXiv:2312.07104

## 核心问题

LLM 应用从"单轮聊天"转向"程序化多调用"（LM Programs = 多次生成 + 控制流 + 结构化输入输出），但现有系统（vLLM/TGI/TRT-LLM）按单请求优化、不感知多调用结构，导致：
- **KV cache 跨调用无法复用**（用完即弃，重复 prefill）
- 约束解码逐 token、**结构化输出（JSON/regex）慢**
- 编程侧痛苦：字符串操纵、脆弱解析、并行控制全靠手写。

**解决思路**：系统化利用 LM Program 的多调用结构做协同优化——前端 DSL 简化编程 + 后端 runtime 三项创新加速执行，前后端协同设计（frontend hint）。

## 关键创新点

### 1. RadixAttention（核心，§3）——KV cache 当 radix tree LRU cache
- **机制**：请求 KV cache 不再用完即弃，按 token 序列存入 radix tree 边；新请求先 prefix-match 复用已有 KV，未命中的追加为新节点。叶子优先 LRU 驱逐（先赶叶子→祖先变叶子再赶）。节点带引用计数，运行批次在用的不驱逐。缓存与运行请求**共享同一内存池**（非固定池），队列积压时宁可赶光缓存换更大 batch。
- **四级共享模式**（Fig.9）：few-shot 共享、self-consistency 多采样、multi-turn 历史、tree-of-thought 搜索历史——现有系统只能手工处理单一模式，RadixAttention 运行时全自动。
- **cache-aware 调度**：等待队列按"已匹配前缀长度"排序（最长共享优先 ≡ DFS 序），定理 3.1 证明在 cache≥最长请求时这是离线最优命中率。在线情形近似 DFS。
- **效果**：cache 命中率 50%-99%，调度达最优命中率 96% 均值；无命中场景开销 <0.3%（74.3s 跑 100 请求，树管理仅 0.2s）→ 可默认开启。生产部署（Chatbot Arena）Vicuna-33B 命中 74.1%、首 token 延迟均降 1.7×。

### 2. Compressed FSM（§4）——约束解码多 token 一次前向
- **机制**：正则→FSM；把 FSM 中**单转移边（singular transition，唯一后继+唯一字符）递归压缩**成单边（compressed edge），一次 forward pass 解码压缩边上的多 token（jump-forward）。tokenization 错位靠 retokenize 对齐。
- **效果**：JSON 解码吞吐 ×1.6；预处理 FSM 必须跨请求复用，否则重做慢 ×2.4。

### 3. API Speculative Execution（§5）——黑盒 API 模型多调用优化
第一次调用忽略 stop 条件多生成几 token，interpreter 保留输出与后续 primitive 匹配复用，省一次 API 调用的延迟+输入费用。

### 4. 前端-后端协同设计
interpreter 把 prompt 当异步流提交原语（extend/gen/select/fork/join），**frontend hint**——fork 时先发前缀提示，runtime 提前插入树、简化调度匹配。消融显示关掉 frontend 并行/hint 都掉性能。

### 5. Compiler Mode（附录 D）
SGLang 程序可 trace 成计算图 IR（ConstantText/Gen/Select/Fork/Join 节点 + 流内/流间依赖），图执行器消除重解释、支持图重写优化。case study：GPT-4 做"代码移动"重排常量节点到前缀以增共享前缀（15 模板中 12 个成功，均增 60 token 共享前缀）——把 LLM 当编译器优化器用。

## 表格（原文结构化）

### Table 1：LMQL / Guidance / SGLang 对比
| 系统 | 语法 | 语言原语 | Runtime 后端 |
|---|---|---|---|
| LMQL | 自定义 | extend, gen, select | HF Transformers, llama.cpp, OpenAI |
| Guidance | Python | extend, gen, select, image | HF Transformers, llama.cpp, OpenAI |
| **SGLang** | Python | extend, gen, select, image, video, **fork, join** | **SGLang Runtime (SRT)**, OpenAI |

SGLang 原语最全（多 fork/join/video），自带 runtime，是唯一带自研 runtime 的低层系统。

### Table 2：多模态 LLaVA 吞吐
| 模型 | 作者原实现 | SGLang |
|---|---|---|
| LLaVA-v1.5-7B (image) | 0.18 image/s | **1.15 image/s** |
| LLaVA-NeXT-34B (video) | 0.02 frame/s | **0.10 frame/s** |

## 与同类对比
- **vs vLLM/Guidance/LMQL**：SGLang 原语最全（多 fork/join/video），自带 runtime；端到端吞吐最高 **6.4×**、延迟最低 3.7×。
- **vs vLLM prefix cache**：vLLM 后来才部分集成 RadixAttention 为实验特性（对比用旧版）；vLLM/ChunkedAttention 只做系统提示等简单共享，无多级树结构+LRU。PromptCache 模块化复用非前缀，但精度可掉 43%。

## 跨论文关系（→ MOC 谱系）
- **继承/改进 vLLM PagedAttention**：vLLM 分页 KV 是奠基，SGLang RadixAttention 把"简单系统提示共享"升级为"多级树结构 LRU 自动复用"。
- **互补 Sarathi/Sarathi-Serve**：SGLang 做"多调用间前缀复用"，Sarathi 做"prefill-decode 混合调度"——正交可叠加。
- **互补 Mooncake**：SGLang 是同机多调用复用，Mooncake 是跨节点 disagg + 分层 KV 迁移（GPU/CPU/DRAM/SSD）。
- **互补 IndexCache**：IndexCache 做层间索引复用，正交于 SGLang 前缀复用。
- **演进 Prefill-as-a-Service**：Mooncake 跨节点思想的进一步跨数据中心规模化。

## 局限与边界
- cache-aware 贪心调度可能**饥饿**（未集成公平调度，列为 future）。
- 长输出场景几乎无加速（解码时间主导、会话间共享少）。
- compressed FSM 的**概率扭曲**（broad 选项如 Excellent|Fair 映射错位），future 研究。
- compiler mode 不支持数据依赖控制流的 trace。
- 多模态 baseline 用作者原 HF 实现（其他系统不支持好），客观比较受限。
