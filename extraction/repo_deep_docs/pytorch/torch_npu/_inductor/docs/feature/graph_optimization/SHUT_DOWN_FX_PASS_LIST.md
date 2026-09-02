# SHUT_DOWN_FX_PASS_LIST

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/graph_optimization/SHUT_DOWN_FX_PASS_LIST.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/graph_optimization/SHUT_DOWN_FX_PASS_LIST.md

# 深度解读：SHUT_DOWN_FX_PASS_LIST

## 【定位】

这篇文档描述的是 TorchNPU 中用于精确控制 Inductor FX Graph Pass 注册行为的环境变量 `SHUT_DOWN_FX_PASS_LIST`，通过该变量可对昇腾自定义 FX Pass 的启用/关闭进行细粒度开关控制，主要用于问题排查与回归定位。

## 【技术要点】

1. **环境变量语义**：变量名为 `SHUT_DOWN_FX_PASS_LIST`，采用字符串列表形式 `xxx,yyy`，按 pass 函数名匹配，匹配粒度为单个 pass（函数级别）。
2. **默认值**：原文明确"环境变量默认为""，即所有 pass 都生效"。
3. **三种取值模式**：
   - `""`（空串）→ 所有 pass 生效；
   - `xxx,yyy`（逗号分隔的 pass 名列表）→ 关闭名单内的指定 pass，其余仍生效；
   - `all` → 关闭全部 pass。
4. **生效判定的日志信号**：原文指出"只要某个 pass 生效，日志会打印 `[inductor_fx_pass] xxx works`"，即通过日志关键词 `[inductor_fx_pass]` + pass 名 + `works` 来判定某个 pass 是否实际被启用。
5. **注册阶段的 DEBUG 日志格式**：`Registering function <pass_name> from module torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass with pass_type=<PassType>, fx_pass_level=<FxPassLevel>`，用于观察每个 pass 是否被注册（注册发生在生效之前，是被关闭名单拦截的判断点）。
6. **Pass 类型与级别枚举**：从日志可见 pass 注册时同时携带 `pass_type`（`POST` 或 `PRE`）和 `fx_pass_level`（全部为 `LEVEL1`），这两类维度构成了 Inductor FX Pass 调度框架的二维分类（时机+层级）。

## 【关键机制与数据】

**工作原理（原文视角）**：

原文将该变量的工作机制描述为一个**白名单/黑名单控制点**：

- 当 `SHUT_DOWN_FX_PASS_LIST` 为空字符串 `""` 时，框架按默认流程注册并执行所有 pass，日志中能看到完整的 `Registering function ...` DEBUG 行，对应文档中 "开启所有 pass" 示例列出的 25 条注册记录。
- 当设为 `xxx,yyy` 时，对应名称的 pass 在注册阶段被跳过，因此日志中相应 DEBUG 行缺失，但其他 pass 的注册不受影响——这正是 "通过关闭某几个 pass，可以用来精确控制，排查问题" 的含义。
- 当设为 `all` 时，所有 pass 都被关闭，原文验证方式写为 "观察日志所有 pass 均未注册"。

**数据流（基于日志可观察到的路径）**：

`pass 函数定义` → `fx_passes.ascend_custom_passes.ascend_graph_pass 模块` → `Registering function <name> DEBUG 日志` → 若未在 SHUT_DOWN 名单中 → `[inductor_fx_pass] <name> works` 运行日志。

**性能数据**：原文未提供任何量化性能指标（如加速比、内存收益、耗时数字），仅给出行为层面的开关说明，因此不在此节补造。

## 【表格解读】

原文并未以 markdown 表格形式呈现参数表或对比表，但其配置示例中的日志块本质上是一张"Pass 注册清单表"。现将其按原文**逐字还原**并解读如下：

| pass_type | fx_pass_level | Registering function（pass 名） | 归属模块 |
|---|---|---|---|
| POST | LEVEL1 | `cat_to_view_pass` | `torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass` |
| POST | LEVEL1 | `repeat_to_expand_pass` | 同上 |
| POST | LEVEL1 | `fold_iota_arithmetic_pass` | 同上 |
| POST | LEVEL1 | `broadcast_const_mask_compress` | 同上 |
| POST | LEVEL1 | `masked_add_compose_pass` | 同上 |
| POST | LEVEL1 | `bool_cast_mul_to_where_pass` | 同上 |
| POST | LEVEL1 | `sign_diff_hamming_fuse_pass` | 同上 |
| POST | LEVEL1 | `batch_embedding_fusion_pass` | 同上 |
| PRE | LEVEL1 | `cat_slice_cat_fold_pass` | 同上 |
| PRE | LEVEL1 | `pad_slice_fold` | 同上 |
| POST | LEVEL1 | `fold_four_op_pass` | 同上 |
| POST | LEVEL1 | `fold_cast` | 同上 |
| POST | LEVEL1 | `fold_cat` | 同上 |
| POST | LEVEL1 | `fold_clone` | 同上 |
| POST | LEVEL1 | `fold_detach` | 同上 |
| POST | LEVEL1 | `fold_expand` | 同上 |
| POST | LEVEL1 | `fold_reduce` | 同上 |
| POST | LEVEL1 | `fold_sink_view` | 同上 |
| POST | LEVEL1 | `fold_slice` | 同上 |
| POST | LEVEL1 | `fold_squeeze` | 同上 |
| POST | LEVEL1 | `fold_to_copy` | 同上 |
| POST | LEVEL1 | `view_fold_pass` | 同上 |
| POST | LEVEL1 | `fold_where` | 同上 |
| POST | LEVEL1 | `fold_redundant_ops` | 同上 |
| PRE | LEVEL1 | `dtype_optimal_pass` | 同上 |

**逐行解读**：

- 该清单即为 "开启所有 pass" 配置下框架默认会注册的 25 个 FX Pass 全集，名称即 `SHUT_DOWN_FX_PASS_LIST` 可填入的合法 token。
- 多数为 `POST` 类型（在 inductor 主流程之后做尾端图变换），少数为 `PRE`（前置图变换），从命名上可分为四类语义：
  - **视图/形状规约类**：`cat_to_view_pass`、`repeat_to_expand_pass`、`view_fold_pass`、`fold_sink_view`、`fold_expand`、`fold_squeeze`、`fold_slice`、`pad_slice_fold`、`cat_slice_cat_fold_pass`；
  - **算子折叠/常量传播类**：`fold_cat`、`fold_clone`、`fold_detach`、`fold_cast`、`fold_reduce`、`fold_where`、`fold_to_copy`、`fold_four_op_pass`、`fold_redundant_ops`、`fold_iota_arithmetic_pass`；
  - **融合/替换类（POST 域内的高层改写）**：`masked_add_compose_pass`、`bool_cast_mul_to_where_pass`、`sign_diff_hamming_fuse_pass`、`batch_embedding_fusion_pass`、`broadcast_const_mask_compress`；
  - **数据类型优化类**：`dtype_optimal_pass`（唯一在 PRE 时机做 dtype 选择的 pass，也是文档中作为 "关闭指定 pass" 的示例对象）。
- 所有 pass 的 `fx_pass_level` 均为 `LEVEL1`，即这些都属于 LEVEL1 优先级的注册项，关闭它们不会影响其他更高级别 pass 的注册（原文未出现 LEVEL2/LEVEL3 等更高优先级 pass 的日志样本）。

> 注：原文末尾的日志输出被截断（出现 `fold_squee` 截断），但根据 "开启所有 pass" 完整列表与 "关闭指定 pass" 示例可对照确认，两段日志在 `fold_squeeze` 之前完全一致，因此可推断文档在结尾部分本应继续罗列剩余注册项直至 `dtype_optimal_pass`。

## 【公式解读】

原文无公式。

## 【关联】

原文无内部链接信息，但根据文档内容可识别出以下关联关系（仅基于原文可证实的事实）：

- **与 `torch_npu._inductor.fx_passes.ascend_custom_passes.ascend_graph_pass` 模块强耦合**：所有受该变量控制的 pass 均注册自该模块，路径在每条 `Registering function` 日志中显式给出。
- **与 Inductor FX Pass 调度框架关联**：每个 pass 都携带 `pass_type`（`PRE`/`POST`）和 `fx_pass_level`（`LEVEL1`），表明该变量作用于上游的 FX Pass 注册/调度层，而非算子实现层。
- **与日志通道 `[inductor_fx_pass]` 关联**：变量关闭的最终判定信号是运行日志中的 `[inductor_fx_pass] <name> works`，因此该日志通道是验证变量生效的可观测依据。
- **与问题排查流程关联**：文档明确将其定位为 "排查问题" 工具，配合 `dtype_optimal_pass` 等具体 pass 的关闭，可以做 pass 级 A/B 定位。

## 【使用方法】

原文给出的使用方式如下（按原文直接列出）：

**1. 开启所有 pass（默认行为）**：
```bash
export SHUT_DOWN_FX_PASS_LIST=""
```
验证方式：观察日志，25 条 `Registering function ...` DEBUG 行均应出现（见上文表格全集）。

**2. 关闭所有 pass**：
```bash
export SHUT_DOWN_FX_PASS_LIST=all
```
验证方式：观察日志，所有 pass 均未注册（无 `Registering function ...` DEBUG 行出现）。

**3. 关闭指定 pass**：
```bash
export SHUT_DOWN_FX_PASS_LIST=dtype_optimal_pass
```
验证方式：观察日志，`dtype_optimal_pass` 未注册（日志中缺少对应 `Registering function dtype_optimal_pass ...` 那一行），其他 pass 仍正常注册。

**多 pass 关闭**：按原文语法 `xxx,yyy` 用逗号分隔，例如 `SHUT_DOWN_FX_PASS_LIST=fold_cat,fold_clone,dtype_optimal_pass`，即可同时关闭 `fold_cat`、`fold_clone`、`dtype_optimal_pass` 三个 pass（原文未显式给出该多值示例，但由变量定义 `SHUT_DOWN_FX_PASS_LIST=xxx,yyy` 推得）。

**判定 pass 实际生效的日志关键词**：`[inductor_fx_pass] <pass_name> works`（原文直接给出）。
