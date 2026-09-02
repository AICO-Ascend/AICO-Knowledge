# Batch MLA backend architecture

> 仓 `flashinfer` · 路径 `docs/design_docs/batch_mla_backend_architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/flashinfer/docs/design_docs/batch_mla_backend_architecture.md

# 一体化深度解读:docs/design_docs/batch_mla_backend_architecture.md

## 【定位】

这篇文档定义 `BatchMLAPagedAttentionWrapper` 在 `flashinfer.mla` 公共入口之下,与 FA2、FA3、CUTLASS 三个具体后端之间的职责边界与 plan/run 生命周期契约,目的是把"成熟的公共 API""多种 metadata 表示""多种 tensor 布局""后端专属约束""持久 plan 状态""CUDA Graph 指针生命周期"等关注点显式分层,避免后端改动串扰公共行为,也防止 plan 工作量泄漏到对延迟敏感的 run 路径。

---

## 【技术要点】

1. **公共/私有边界**:`BatchMLAPagedAttentionWrapper` 与 `MLAPlanMetadata` 经 `flashinfer.mla` 暴露;`_batch_mla` 包及其具体后端类(`_batch_mla.fa2`、`_batch_mla.fa3`、`_batch_mla.cutlass`)为私有实现细节,不向应用层开放,也不作为扩展接口。
2. **plan/run 双阶段生命周期**:wrapper 拥有公共生命周期与兼容性策略;`plan()` 阶段输出后端无关的 plan 请求并由选定后端的 `plan_from_wrapper()` 完成规划;`run()` 在已规划上下文下仅做运行期校验、零拷贝输入降级、输出准备,再调用选定后端 `run_from_wrapper()` 启动 kernel。
3. **三种 metadata 入口**(均通过 `MLAPlanMetadata` 的类方法构造):
   - `MLAPlanMetadata.csr(...)`:便携式 CSR 输入,接受 `qo_indptr`、`kv_indptr`、`kv_indices`、`kv_len_arr`。
   - `MLAPlanMetadata.dense(...)`:稠密输入,接受 `cum_seq_lens_q`、`block_tables`、`seq_lens`、`max_q_len`。
   - `MLAPlanMetadata.dual(...)`:同时提供 CSR 与 dense 两套描述,planner 校验其描述同一组请求与页映射。
4. **运行时布局契约**:`query_layout` 与 `kv_cache_layout` 可为 `"packed"` 或 `"split"`;一个 packed plan 可零拷贝接受来自同一 packed 父张量的相邻 row-major 视图作为 split 输入,独立分配张量、非稠密视图、任意 stride 切片会被 plan 拒绝。`MLAInputContract` 记录 plan 所固定的运行时选项与布局。
5. **plan 状态发布语义**:plan 状态在执行模型允许之处以事务方式发布;后端选择、模块加载、metadata 转换、持久化分配均显式落在"正常规划后的 run 路径"之外。
6. **三后端的差异化形状/缩放契约**(原文示例中体现):
   - FA2/FA3(CSR+packed 路径):`sm_scale = 1.0 / math.sqrt(head_dim_ckv + head_dim_kpe)`,其中 `head_dim_ckv=512`、`head_dim_kpe=64`。
   - CUTLASS(当前 dense+packed 路径):`sm_scale = 1.0 / math.sqrt(qk_nope_head_dim + 64)`,其中 `qk_nope_head_dim=128`(原文注明"今日支持形态示例,非永久支持矩阵")。

---

## 【关键机制与数据】

**Plan/Run 数据流(原文逐字):**

```
flashinfer.mla.BatchMLAPagedAttentionWrapper
  -> normalize canonical or deprecated plan inputs
  -> build one backend-neutral plan request
  -> selected backend.plan_from_wrapper()
  -> publish the completed backend and run contract
  -> normalize and validate run inputs
  -> selected backend.run_from_wrapper()
  -> kernel
```

各环节职责:
- **normalize canonical or deprecated plan inputs**:wrapper 接受规范输入与历史废弃输入并归一化。
- **build one backend-neutral plan request**:产出与具体后端解耦的 plan 请求对象。
- **selected backend.plan_from_wrapper()**:由选定后端完成专属校验、状态持久化、模块加载、输出准备与 launch 装配。
- **publish the completed backend and run contract**:仅在 plan 成功时发布后端实例与 `MLAInputContract`。
- **normalize and validate run inputs**:run 阶段输入归一化与校验。
- **selected backend.run_from_wrapper()**:对已经规划的后端触发 launch。
- **kernel**:进入具体 GPU kernel。

**CSR 示例的关键张量数值(原文):**
- `qo_indptr = [0, 1, 2]`(2 个 query 请求,各 1 token,`max_q_len=1`)
- `kv_indptr = [0, 1, 3]`、`kv_indices = [0, 1, 2]`(共 3 个物理页)
- `kv_len_arr = [16, 24]`(两个请求的 KV 长度)
- `query` 形状:`(2, 128, 512+64) = (2, 128, 576)`,bfloat16,设备 CUDA
- `kv_cache` 形状:`(3, 16, 512+64) = (3, 16, 576)`,bfloat16
- `workspace`:`128 * 1024 * 1024` 字节 uint8(workspace 与 query、kv_cache 同 CUDA 设备;metadata 张量可留 CPU)

**Dual 与 dense 输入共享同一组结构输入(原文示例):**
- `dual` 路径在 `csr` 字段之外附加 `cum_seq_lens_q`、`block_tables`、`seq_lens`、`max_q_len=1`,planner 校验两套描述指向同一请求与页映射。
- 切换为 `backend="cutlass"` 的 dense 路径时,metadata 通过 `MLAPlanMetadata.dense(...)` 构造,所有张量需驻留 CUDA 设备(如 `device=device` 所示),且 `head_dim_ckv=512`、`head_dim_ke=64` 不变,但 `qk_nope_head_dim=128` 与不同的缩放公式随 CUTLASS 当前形状契约生效。

**Split 视图的零拷贝语义(原文):**
- `q_nope = query[..., :head_dim_ckv]`、`q_pe = query[..., head_dim_ckv:]` 来自同一 packed `query`;`ckv_cache`、`kpe_cache` 同理。
- 这些相邻视图被 wrapper 重新解释为 packed 张量,**不分配新内存**;独立分配的同名视图、非稠密视图、任意 stride 切片不享受此保证,packed plan 将拒绝;有此类输入需求者应改用 split layout 规划。
- 这是输入表示契约,非具体后端保证。

**性能数据**:原文未给出任何 benchmark 数字、时延或吞吐测量值;性能相关表述仅限于"plan 工作量不应进入延迟敏感 run 路径"这一架构约束,不含量化指标。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无 LaTeX 公式,仅以 Python 表达式给出两个 `sm_scale` 计算式,逐字保留并解释符号含义:

**FA2/FA3 路径(CSR + packed 示例):**
```python
sm_scale = 1.0 / math.sqrt(head_dim_ckv + head_dim_kpe)
```
- `head_dim_ckv`:压缩 KV 头维度,原文示例取 `512`。
- `head_dim_kpe`:位置编码头维度,原文示例取 `64`。
- `math.sqrt(...)`:对二者之和开平方根作为注意力缩放分母。
- 作用:将注意力 logits 的数值范围归一化,匹配多头注意力中 `1/√d` 的标准做法;此处 `d` 取 `head_dim_ckv + head_dim_kpe` 即 query 向量全长(576)。

**CUTLASS 路径(dense + packed 示例,原文标注"今日支持形态示例,非永久支持矩阵"):**
```python
sm_scale = 1.0 / math.sqrt(qk_nope_head_dim + 64)
```
- `qk_nope_head_dim`:无位置编码部分的 Q/K 头维度,原文示例取 `128`。
- 字面常量 `64`:对应 `head_dim_kpe`,此处在代码中以数值常量出现而非符号参数。
- 作用:与上一式同构,但分母基于无位置编码头维度加位置编码维度(`128 + 64 = 192`),反映 CUTLASS 当前形状契约下不同的有效缩放范围。

两式的对比说明:同一个 wrapper 名称与同一份结构输入,在不同后端配置下需要使用不同的 `sm_scale`,因为后端的形状契约不同;原文示例刻意把这两个公式分别在 FA2/FA3(CSR)与 CUTLASS(dense)片段中给出,凸显后端专属约束归属后端模块而非 wrapper。

---

## 【关联】

- **公共命名空间层**:`flashinfer.mla` 暴露 `BatchMLAPagedAttentionWrapper` 与 `MLAPlanMetadata`;`_batch_mla` 包及其具体后端类为私有实现细节,文档明确"它们不是应用扩展接口"。
- **具体后端模块**:`_batch_mla.fa2`、`_batch_mla.fa3`、`_batch_mla.cutlass`,各自承担专属校验、持久状态、模块加载、输出准备与 launch 装配;FA2 与 FA3 在文档示例中共享 CSR+packed 路径,CUTLASS 在文档示例中采用 dense+packed 路径。
- **规划与契约模块**:`MLAPlanMetadata`(元数据入口与表示形式 csr/dense/dual)、`_MLAPlanMetadataResolver`(请求局部 metadata 的校验与翻译)、`MLAInputContract`(plan 所固定的运行时选项与布局记录)。
- **运行期支撑**:wrapper 在 run 阶段做零拷贝输入降级与运行期校验,与"CUDA Graph 指针生命周期"的兼容性政策同属 wrapper 拥有的公共生命周期关切。
- **明确不在本架构边界内的概念**:仓库级通用 attention 后端基类、功能式 `batch_mla_paged_attention` 入口与功能式 runner 生命周期、后端注册表/候选循环/类型化 fallback/选择 trace/自动调优策略、超出 FA2/FA3/CUTLASS 的额外 Batch MLA 后端、`_batch_mla` 的公共暴露、稠密 Batch MLA 包内的 Sparse DSV4 编排。
- **历史兼容性**:wrapper 接受规范与废弃输入,历史兼容行为被隔离并标记为 deprecated;废弃与规范的归一化在 wrapper 内完成,而非散落到各后端。
- **关于"CSR 与 dense"的派生关系**:二者之间的派生仅在选定后端需要时才发生,避免在无关路径上做无意义转换;这与 `_MLAPlanMetadataResolver` 的角色直接相关。

原文文末未提供任何内部链接(链接列表为"(无)"),因此上下游指引仅限于文档文本本身所引用的上述模块/包/后端名称,无外部 wiki/Cross-reference。

---

## 【使用方法】

**wrapper 构造(原文):**
```python
wrapper = BatchMLAPagedAttentionWrapper(workspace)               # FA2/FA3 路径(默认)
wrapper = BatchMLAPagedAttentionWrapper(workspace, backend="cutlass")  # CUTLASS 路径
```
- `workspace`:`torch.empty(128 * 1024 * 1024, dtype=torch.uint8, device=device)`(原文示例规模,与 query/kv_cache 同设备)。

**plan 步骤(原文公共调用形态):**
```python
wrapper.plan(
    metadata=metadata,            # MLAPlanMetadata.csr / .dense / .dual 之一
    num_heads=num_heads,          # 原文示例:128
    head_dim_ckv=head_dim_ckv,    # 原文示例:512
    head_dim_kpe=head_dim_kpe,    # 原文示例:64
    page_size=page_size,          # 原文示例:16
    causal=False,                 # 原文示例取值
    sm_scale=...,                 # FA2/FA3:1/sqrt(head_dim_ckv+head_dim_kpe);CUTLASS:1/sqrt(qk_nope_head_dim+64)
    q_data_type=dtype,            # 原文示例:torch.bfloat16
    kv_data_type=dtype,           # 原文示例:torch.bfloat16
    query_layout="packed",        # 原文示例取值,亦可 split
    kv_cache_layout="packed",     # 原文示例取值,亦可 split
)
```

**run 步骤(原文两种输入形态):**
- Packed 输入:`output = wrapper.run(query=query, kv_cache=kv_cache)`。
- Split 输入(零拷贝,要求来自同一 packed 父张量的相邻 row-major 视图):
  ```python
  output = wrapper.run(
      query=(q_nope, q_pe),
      kv_cache=(ckv_cache, kpe_cache),
  )
  ```
  独立分配、非稠密视图、任意 stride 切片下的 split 输入会被 packed plan 拒绝,需要改用 split layout 重新 plan。

**metadata 构造选项(原文给出三选一的语义):**
- `MLAPlanMetadata.cr(qo_indptr, kv_indptr, kv_indices, kv_len_arr)`:便携 CSR 输入。
- `MLAPlanMetadata.dense(cum_seq_lens_q, block_tables, seq_lens, max_q_len)`:稠密输入。
- `MLAPlanMetadata.dual(...)`:同时携带 CSR 与 dense 两套字段,planner 校验其描述同一请求与页映射;原文提示"不要为不同实现维护独立、未校验的 metadata 路径"。

**应用扩展指引(原文):** 调用方应只表达所需的 metadata 与输入契约,实现选择由 wrapper 决定;后端选择与具体后端类为实现细节而非扩展接口。

**文档截断说明:** 原文在 CUTLASS dense 示例的最后一行(`q_dat...`)处截断,未给出该片段 `wrapper.plan(...)` 与 `wrapper.run(...)` 的完整收尾;本节按原文已给出的字段进行解释,未补全被截断的代码。

原文未涉及:CLI 入口、环境变量、性能调优开关、自动调优策略、版本兼容矩阵、`backend` 可选字符串的完整列表(原文仅出现 `"cutlass"`,未列举其他合法取值)。
