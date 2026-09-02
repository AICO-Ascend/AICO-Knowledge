# Verl+Megatron后端后训练加载和保存ckpt时间优化

> 仓 `mindspeed` · 路径 `docs/zh/features/verl-ckpt-acceleration.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/verl-ckpt-acceleration.md

# 深度解读: Verl+Megatron后端后训练加载和保存ckpt时间优化

## 【定位】

这篇文档针对 verl + Megatron 后端在后训练场景下 **checkpoint（ckpt）加载与保存耗时过长** 的问题，描述了通过跳过原生 Megatron 与 PyTorch 中耗时严重的校验逻辑来加速 ckpt load/save 的能力。

---

## 【技术要点】

- **问题场景**：verl + Megatron 后端进行后训练时，save 和 load ckpt 时间较长，影响训练效率。
- **核心思路**：针对原生 Megatron 和 PyTorch（torch）中比较耗时严重的部分校验逻辑做**跳过处理**。
- **控制方式**：通过参数 `ckpt_acceleration` 控制是否跳过校验逻辑，从而加速 load 和 save ckpt。
- **启用命令**：在训练脚本中加入参数 `+actor_rollout_ref.actor.megatron.override_transformer_config.ckpt_acceleration=True`。
- **验证环境**：在 `qwen3-30b-dapo`、`16卡 × 2机` 场景下进行实测（具体加速倍数需参考附图，原文以图片形式呈现）。
- **适用场景**：仅限 verl + Megatron 后端的后训练场景。

---

## 【关键机制与数据】

- **工作原理**（原文：原生 Megatron 与 PyTorch 在保存/加载 ckpt 时存在耗时的校验逻辑，本方案通过 `ckpt_acceleration=True` 参数绕过这些校验步骤，从而减少 I/O 与计算开销）。
- **数据流**（原文：未给出具体数据流/流水线描述）。
- **性能数据**（原文：在 `qwen3-30b-dapo` 模型、`16卡 × 2机` 硬件配置下"显著提高"了 load 和 save ckpt 的效率；具体加速数值由附图 `figures/verl-ckpt-acceleration.png` 提供，文中未以文字形式给出数字）。

---

## 【表格解读】

**原文无表格。**

性能对比以图片（`verl-ckpt-acceleration.png`）形式呈现，文档正文未包含可逐字还原的 markdown 表格。

---

## 【公式解读】

**原文无公式。**

本文档为特性说明性质，未涉及任何数学公式或伪代码。

---

## 【关联】

文档为孤立特性文档，文末标注"内部链接: (无)"。从内容上看：

- **上游框架依赖**：依赖 verl 框架的 actor/rollout/ref 角色配置体系（通过 `actor_rollout_ref.actor.megatron.override_transformer_config` 路径传入参数）。
- **后端依赖**：依赖 Megatron 后端 + PyTorch 原生 ckpt 逻辑。
- **下游影响**：加速 ckpt load/save，可缩短后训练流程的整体时长，间接提升训练吞吐。
- 由于无内部链接，无法判断其与仓库内其他特性模块的直接耦合关系。

---

## 【使用方法】

在训练脚本中加入以下参数即可开启 ckpt load 和 save 加速：

```bash
+actor_rollout_ref.actor.megatron.override_transformer_config.ckpt_acceleration=True
```

**使用场景**（原文限定）：
- verl + Megatron 后端进行后训练

**配置项说明**：
| 参数路径 | 取值 | 作用 |
|---|---|---|
| `actor_rollout_ref.actor.megatron.override_transformer_config.ckpt_acceleration` | `True` | 跳过原生 Megatron 与 torch 中的耗时校验逻辑，加速 ckpt load/save |
| 同上 | `False`（默认） | 保留完整校验逻辑（原文未显式说明默认值，但暗示 `True` 为启用加速的状态） |

原文未涉及 `ckpt_acceleration` 之外的其他相关配置项。

## 图文联合解读

- `verl-ckpt-acceleration.png`: **图文联合解读：**

表格对比四种配置下的load/save ckpt耗时。开启ckpt_acceleration后，load从7237s降至362s（约20×加速），save从10861s降至94s（约115×加速）；再叠加异步保存，save进一步降至44s。该数据直接验证文档论点——跳过校验逻辑可显著提升Verl+Megatron后端ckpt效率。
