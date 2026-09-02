# 模型编译缓存功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/compile_cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/compile_cache.md

# 模型编译缓存功能 — 一体化深度解读

> 注: 原文在 Ascend IR 编译缓存章节末尾处被截断 (`import lo...`), 以下解读仅基于完整可读段落, 不臆测未给出的代码。

---

## 【定位】

这篇文档描述 TorchAir 在 Ascend NPU 上提供的**模型编译缓存能力** — 通过 `cache_compile` 接口把 `torch.compile` 图模式首次成图中耗时占比最大的 **Dynamo 编译** 与 **Ascend IR(GE) 图编译** 两段结果显式落盘, 在二次加载时跳过 JIT/Guards/GE 编译阶段, 显著缩短大模型推理服务(以 LLaMA 2-70B 为例)的冷启动首推理时延, 适用于推理服务与弹性扩容场景。

---

## 【技术要点】

1. **缓存范围**: 同时缓存 Dynamo 阶段(原文: "通过缓存Dynamo、Ascend IR图编译两个耗时占比最大环节, 实现模型的加速启动"); 在 max-autotune 模式下, 通过 `ge_cache` 参数可额外启用 Ascend IR(GE)图编译子缓存。
2. **核心 API**: `torchair.inference.cache_compile(func, config=config)` — 调用后**原先脚本中的 `torch.compile` 编译流程不再需要**(原文 NOTE), 直接执行 `model(...)` 即可。
3. **使用约束(原文)**: 仅适用于 GE 图模式; 暂不支持同时配置 [Dynamo导图功能](dynamo_export.md)、[RefData类型转换功能](ref_data.md); 图中含 RNG 算子(`randn`、`bernoulli`、`dropout` 等)不支持。
4. **跳过环节与新增限制**: 跳过 Dynamo JIT、Guards、Ascend IR 图编译三个环节; 要求**生成模型的脚本和加载缓存的脚本一致**(原文); CANN 跨版本缓存不保证兼容, 需清理缓存目录并重新编译生成缓存。
5. **缓存路径规则(原文)**: 绝对路径 → `${cache_dir}/${model_info}/${func}`; 相对路径 → `${work_dir}/${cache_dir}/${model_info}/${func}`; 多机多卡 → `${work_dir}/${cache_dir}/${model_info}/world${world_size}global_rank${global_rank}/${func}/`。默认 `cache_dir` 为 `.torchair_cache`(无则新建)。
6. **func 封装硬性要求(原文 NOTE)**: ① func 只能被触发一次 Dynamo trace(重编译即放弃缓存); ② 多次 trace 的函数需用一次函数封装使缓存生效; ③ func 必须是 module 实例对象的 method, 且未被其他装饰器修饰; ④ func 必须能形成整图(full graph)。

---

## 【关键机制与数据】

### 工作原理(原文 5 阶段执行链)
原始 `torch.compile` + max-autotune 推理任务的执行被划分为 5 个阶段:
1. **Dynamo** — Python 级 JIT, 重写字节码把 PyTorch 操作提取到 FX 图, 再用可定制后端编译。
2. **Guards** — Dynamo 编译生成的 Guard 在每次执行前执行, 用于判断是否需要重新捕获/编译。
3. **Ascend IR 图编译** — max-autotune 模式下将 Ascend IR 计算图编译为可执行二进制。
4. **Input 转换** — 更新图内 input 类参数的输入地址为图实际运行时的输入地址。
5. **图执行** — Device 基于给定输入真正计算得到输出。

### 缓存机制要点
- **匹配标识**: `cache_compile` 根据函数/模型标识、编译配置、动态或静态模式、NPU 确定性等级、分布式 rank 等计算缓存路径; 该标识**不是模型源码文件的完整 hash**, 模型内部源码、依赖模块或外部输入语义变化时不一定被自动发现(原文)。
- **失效触发**(原文): ① 缓存路径不存在; ② 缓存加载/恢复失败; ③ 重编译; ④ CANN 包版本升级; ⑤ 模型代码/结构/输入输出约束/确定性设置/控核设置/编译配置发生变更(需手动 `rm` 旧缓存后重跑 `cache_compile`)。
- **分布式扩展路径**: 多机多卡场景下路径内嵌 `world_size` 与 `global_rank`, 保证不同集合通信配置独立缓存。

### 性能参考(原文有据可查)
- 文档以 **LLaMA 2-70B** 为例给出"图 1 max-autotune 模式执行时间分布示意图"(对应图片 `figures/execution_time_1.png`), 对比"启动与未开启模型编译缓存的耗时分布"; 原图未提供具体毫秒数, 仅说明**该图不呈现与本功能无关的耗时细节**。

### 日志可观测点(原文 INFO 日志样例)
首次运行(`saved to ...`)与命中(`loaded from ...`)均打印 `ModelCacheMeta(name=..., date=..., version='1.0.0', fx=None)`, 日志格式可对照原文样例:
```
Cache ... saved to /home/workspace/.torchair_cache/Model_dynamic_f2df0818d06118d4a83a6cacf8dc6d28/prompt/compiled_module
Cache ... loaded from /home/workspace/.torchair_cache/Model_dynamic_f2df0818d06118d4a83a6cacf8dc6d28/prompt/compiled_module
```

---

## 【表格解读】

**原文无表格**。

(文档全部以文字 + 代码块 + 一张执行时间分布示意图(`execution_time_1.png`)承载信息, 未出现 markdown/HTML 表格。)

---

## 【公式解读】

原文未出现数学公式, 但在"缓存路径"一节给出了若干**路径表达式**(类似模板字符串), 逐式保留并解释:

**式 1**(原文, 绝对路径):
```
${cache_dir}/${model_info}/${func}
```
- `${cache_dir}`: `cache_compile` 的 `cache_dir` 参数值; 若用户不指定, 默认为 `.torchair_cache`(原文: "若无会新建, 请确保有读写权限")。
- `${model_info}`: 模型信息(原文未细化命名规则, 仅给出样例值 `Model_dynamic_f2df0818d06118d4a83a6cacf8dc6d28`)。
- `${func}`: 用户封装的 func 函数名(样例中为 `prompt`、`decode`)。

**式 2**(原文, 相对路径):
```
${work_dir}/${cache_dir}/${model_info}/${func}
```
- `${work_dir}`: 当前工作目录(原文: "为当前工作目录")。
- 其余符号同式 1。

**式 3**(原文, 多机多卡路径):
```
${work_dir}/${cache_dir}/${model_info}/world${world_size}global_rank${global_rank}/${func}/
```
- `${world_size}`: 集合通信的进程总数。
- `${global_rank}`: 全局进程 rank 标识。
- 加入这两个维度可避免不同并行配置之间缓存串扰。

---

## 【关联】

依据文末链接与正文引用, 本特性与以下模块/特性存在耦合关系:

| 关联对象 | 关系性质 | 说明 |
|---|---|---|
| [`cache_compile`](../../api/inference/cache_compile.md) | **核心接口(被引用 3 次)** | 本特性唯一对外暴露的 API; 也是 Ascend IR 子缓存(`ge_cache` 参数)的载体 |
| [`dynamo_export`](dynamo_export.md) | **互斥(原文)** | "暂不支持同时配置 Dynamo 导图功能" |
| [`ref_data`](ref_data.md) | **互斥(原文)** | "暂不支持同时配置 RefData 类型转换功能" |
| [`python_log_print`](../basic/python_log_print.md) | **配套使用** | 首次/命中日志(INFO 级)需开启该特性后才能看到 `saved to / loaded from` 行 |
| [`readable_cache`](../../api/inference/readable_cache.md) | **下游辅助** | 把 `compiled_module` 反序列化为可读文件(如 `prompt.py`)用于问题定位(原文) |
| `torch.compile` | **被替代** | 使用 `cache_compile` 后, 原先脚本中的 `torch.compile(model, backend=npu_backend)` 流程不再需要(原文 NOTE) |
| `torchair.get_npu_backend` / `CompilerConfig` | **上游依赖** | `cache_compile(self.prompt, config=config)` 中的 `config` 即 `CompilerConfig` 实例 |

---

## 【使用方法】

### 1. 启用编译缓存(原文标准流程)

**(a) 提取 forward 为可缓存函数**: 把原 `forward` 实现移出到 `_forward`, 在 `forward` 中加入 `@torch.inference_mode()` 与分支判断(原文示例):
```python
@torch.inference_mode()
def forward(self, x: InputMeta, kv: List[torch.Tensor]):
    return self._forward(x, kv)
def _forward(self, x, kv):
    return self.linear2(x.data) + self.linear2(kv[0])
```

**(b) 封装新 func 并挂上 `cache_compile`**(原文示例):
```python
self.cached_prompt = torchair.inference.cache_compile(self.prompt, config=config)
self.cached_decode  = torchair.inference.cache_compile(self.decode,  config=config)

def forward(self, x, kv):
    if x.is_prompt:
        return self.cached_prompt(x, kv)
    return self.cached_decode(x, kv)

def prompt(self, x, y): return self._forward(x, y)
def decode(self, x, y): return self._forward(x, y)
```
随后**直接执行 `model(x, kv)`**(无需再 `torch.compile`)。

### 2. 生成缓存(原文命令)
```bash
cd /home/workspace
python3 test.py
```
首次执行会按 `${cache_dir}/${model_info}/${func}` 规则落盘; 若 `cache_dir` 缺省则默认使用 `.torchair_cache`。

### 3. 验证命中(原文步骤 4)
再次执行同一脚本, 配合 [Python 层日志打印](../basic/python_log_print.md) 开启 INFO 级日志, 观察 `loaded from ...` 行确认命中。

### 4. 检视缓存内容(原文步骤 5, 可选)
```python
torchair.inference.readable_cache(
    "/home/workspace/.torchair_cache/Model_dynamic_f2df0818d06118d4a83a6cacf8dc6d28/prompt/compiled_module",
    file="prompt.py",
)
```

### 5. 启用 Ascend IR 子缓存(原文 Ascend IR 章节, **正文被截断, 关键参数仍可见**)
- 通过 [`cache_compile`](../../api/inference/cache_compile.md) 的 `ge_cache` 参数控制。
- 原文明确约束: ① **默认 `ge_cache=False`(功能不开启)**, 用户需根据实际情况手动开启; ② CANN 包跨版本缓存无法保证兼容, 升级需清理缓存目录并重新 GE 编译; ③ 单算子和图混跑场景下开启会增加通信域资源开销与额外显存消耗。

### 6. 强制失效(原文规则)
当模型代码/结构、I/O 约束、确定性设置、控核设置或编译配置发生变更时, **必须手动删除原有缓存并重新执行 `cache_compile`**, 否则可能命中与新配置不一致的旧缓存。

## 图文联合解读

- `execution_time_1.png`: **图示解读：**

1. **画面结构**：横向时间轴对比，分"原始推理任务执行"与"开启模型编译缓存"两行，分别展示首次执行和再次执行各阶段的耗时占比。

2. **技术结论**：原始流程首次需经历 Dynamo编译→Guards→Ascend IR图编译→Input转换→图执行；开启缓存后，前三大耗时环节被合并为一个 "Time save" 块，Input转换与图执行不变，再次执行亦跳过 Dynamo 重编译。

3. **与文档论点关系**：直观印证了文档所述"通过缓存 Dynamo 与 Ascend IR 图编译两大耗时环节实现加速启动"的结论，量化呈现缓存带来的首跳延迟削减效果。
