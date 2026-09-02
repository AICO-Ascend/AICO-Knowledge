# 图编译多级优化选项

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/oo_level.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/oo_level.md

# 「图编译多级优化选项」深度解读

## 【定位】

这篇文档描述了 TorchAir 中图编译阶段的多级优化能力——用户可通过 `compiler_config` 中的 `oo_level`、`oo_constant_folding`、`oo_dead_code_elimination` 三个开关，在 GE 图模式下控制图融合、UB 融合、常量折叠、死边消除、静态下沉等编译期优化策略的开启与关闭。

## 【技术要点】

1. **三级优化开关 `oo_level`**：字符串类型，提供 O3 / O1 两档；O3 为默认值，开启所有优化（常量折叠、死边消除等）；O1 关闭所有图融合和 UB 融合 Pass，仅保留静态下沉相关优化（如 InferShape、常量折叠、死边消除）。
2. **常量折叠 `oo_constant_folding`**：布尔类型，控制是否在编译阶段直接计算并替换常量表达式；默认 `None`（跟随 `oo_level`，O1/O3 下默认开启），可手动置 `True/False` 强制覆盖。
3. **死边消除 `oo_dead_code_elimination`**：布尔类型，控制对条件控制算子（If、Case 等）在 `cond` 编译期已确定时删除未执行分支的优化；默认 `None`（跟随 `oo_level`），同样支持手动覆盖。
4. **适用场景约束**：原文明确"本功能仅适用于 GE 图模式场景"。
5. **O1 例外保留项**：当 `oo_level=O1` 时，会关闭所有图融合与 UB 融合 Pass，但 `${INSTALL_DIR}/x86_64-linux/lib64/plugin/opskernel/fusion_pass/config/fusion_config.json` 中 `ExceptionalPassOfO1Level` 字段下列出的图融合 Pass 仍会开启（关闭可能影响功能）。
6. **试验性质**：原文标注为"试验功能，后续版本可能存在变更，暂不支持应用于商用产品中"。

## 【关键机制与数据】

### 常量折叠（Constant Folding）
- **原文**："其核心是在编译阶段直接计算并替换常量表达式的值，从而减少运行时的计算负担。"
- 作用时机：编译期；作用对象：常量表达式；效果：减少运行时计算负担。

### 死边消除（Dead Code/Edge Elimination）
- **原文**："当图中存在条件控制算子（如 If、Case 等）时，会根据输入条件（cond）判断执行哪个分支。若 cond 在编译时已确定，即可明确执行的分支，此时可删除不执行的分支，从而减少算子编译、图编译耗时。"
- 作用对象：含 If、Case 等条件控制算子的图；触发条件：`cond` 在编译期已确定；效果：删除未执行分支，减少算子编译与图编译耗时。

### O3 vs O1 行为差异（基于原文参数说明）
- **O3（默认）**：开启所有优化，含常量折叠、死边消除等。
- **O1**：关闭所有图融合与 UB 融合 Pass；仅开启静态下沉相关优化（含 InferShape、常量折叠、死边消除等）。

### 数值/路径数据
- CANN 安装路径（root 安装示例）：`/usr/local/Ascend/cann`（即 `${INSTALL_DIR}`）。
- 融合 Pass 例外配置文件路径：`${INSTALL_DIR}/x86_64-linux/lib64/plugin/opskernel/fusion_pass/config/fusion_config.json`，关键字段 `ExceptionalPassOfO1Level`。

## 【表格解读】

原文表 1 逐字还原如下：

|参数名|说明|
|--|--|
|oo_level|图编译多级优化选项，字符串类型。<br>O3（默认值）：开启所有优化，包括开启常量折叠、死边消除等优化。<br>O1：关闭所有图融合和UB（Unified Buffer）融合Pass，只开启静态下沉相关的优化，如InferShape（输出Tensor的shape推导）、常量折叠、死边消除等优化。|
|oo_constant_folding|是否开启常量折叠优化。<br>None（默认值）：依赖oo_level取值，当优化级别为O1或O3时，默认开启。<br>True：开启。<br>False：不开启。|
|oo_dead_code_elimination|是否开启死边消除优化。<br>None（默认值）：依赖oo_level取值，当优化级别为O1或O3时，默认开启。<br>True：开启。<br>False：不开启。|

**逐行解读**：
- **`oo_level`**：顶层开关，字符串型，定义两档优化等级。O3 是全量优化（默认），适合追求最终性能的场景；O1 是"瘦身"档，关闭图融合与 UB 融合，但保留静态下沉所需的基础优化（InferShape、常量折叠、死边消除），适合调试、缩短编译耗时或排查融合相关问题的场景。
- **`oo_constant_folding`**：常量折叠的独立开关。`None` 表示"听命于 `oo_level`"——只要 `oo_level` 为 O1 或 O3 即默认开启；若用户希望脱离 `oo_level` 单独控制（强制开/关），可显式置 `True`/`False`。
- **`oo_dead_code_elimination`**：死边消除的独立开关。语义与 `oo_constant_folding` 对称：`None` 时跟随 `oo_level`（O1/O3 默认开启），也可独立置 `True/False` 覆盖。

## 【公式解读】

原文无公式。

## 【关联】

- **`torchair.get_npu_backend`**：本文所有配置项均通过 `get_npu_backend(compiler_config=config)` 注入编译后端，因此本特性依赖并扩展了 `get_npu_backend` 的 `CompilerConfig` 配置入口，详见文末内部链接 [`../../api/torchair/get_npu_backend.md`](../../api/torchair/get_npu_backend.md)。
- **`CompilerConfig` 与 `ge_config`**：配置以 `config.ge_config.oo_level` / `config.ge_config.oo_constant_folding` / `config.ge_config.oo_dead_code_elimination` 的层级挂载，说明这三个开关属于 GE（Graph Engine）图后端的专属配置。
- **GE 图模式**：本特性仅在 GE 图模式下生效，因此与文档上文提到的"图模式"及 GE 后端相关的其它编译开关存在联动（如静态下沉相关 Pass）。
- **CANN 图融合规则**：原文末尾提及"更多融合规则相关介绍请参见《CANN图融合和UB融合规则参考》"，表明 `oo_level=O1` 所关闭的"图融合 / UB 融合 Pass"由 CANN 侧定义，本文档受其约束。

## 【使用方法】

**入口**：`torchair.get_npu_backend` 的 `compiler_config` 参数，配置路径为 `config.ge_config.<开关名>`。

**示例代码**（原文给出，注明"仅供参考不支持直接拷贝运行"）：

```python
import torch_npu
import torchair
config = torchair.CompilerConfig()
# 多级编译优化配置
config.ge_config.oo_level = "O3"
# 常量折叠优化配置
config.ge_config.oo_constant_folding = True
# 死边消除优化配置
config.ge_config.oo_dead_code_elimination = False
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**配置项速查**（详见上文表格解读）：
- `config.ge_config.oo_level`：取值 `"O3"`（默认，全量优化）或 `"O1"`（关闭图融合与 UB 融合 Pass，仅保留静态下沉相关优化）。
- `config.ge_config.oo_constant_folding`：取值 `None`（默认，跟随 `oo_level`）/ `True` / `False`。
- `config.ge_config.oo_dead_code_elimination`：取值 `None`（默认，跟随 `oo_level`）/ `True` / `False`。

**补充注意事项**（原文 NOTE）：
- 用户可将 `oo_constant_folding` 或 `oo_dead_code_elimination` 手动置 `True/False` 实现独立开启/关闭。
- `oo_level=O1` 时，`fusion_config.json` 中 `ExceptionalPassOfO1Level` 字段下列出的图融合 Pass **仍会**开启（关闭可能影响功能）。
- `${INSTALL_DIR}` 需替换为实际 CANN 安装路径；root 安装示例路径为 `/usr/local/Ascend/cann`。
