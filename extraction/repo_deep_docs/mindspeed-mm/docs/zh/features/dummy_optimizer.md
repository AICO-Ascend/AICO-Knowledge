# dummy optimizer

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/dummy_optimizer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/dummy_optimizer.md

# mindspeed-mm 「dummy_optimizer」Feature 文档深度解读

---

## 【定位】

本篇文档针对朴素的 pipeline parallel 实现中"某 pipeline stage 全部 parameter 不需要参数更新或反向计算"的特殊场景，介绍了通过创建空 tensor + 反向跳过判断来规避该场景的 dummy optimizer 能力。

---

## 【技术要点】

1. **触发场景**：pipeline parallel 中某个 stage 的所有 parameter 都不需要参数更新或不需要反向计算，这是朴素实现的盲区（原文："朴素的 pipeline parallel 实现中，不支持某个 pipeline stage 的 parameter 都不需要参数更新或不需要反向计算"）。
2. **核心解法一**：在 optimizer 层面创建空 tensor，从而绕过"所有 parameter 都不需要更新"导致的异常路径（原文："创建空 tensor，规避 optimizer 中所有 parameter 都不需要更新的场景"）。
3. **核心解法二**：在 pipeline parallel 的反向前增加判断条件，若没有 `grad_fn` 则跳过该 stage 的反向计算（原文："在 pipeline parallel 的反向前加判断，若没有 grad_fn 则不进行反向计算"）。
4. **启用方式**：通过 `mindspeed_mm.patchs.dummy_optimizer_patch` 模块打补丁，并在启动 shell 中传入 `--enable-dummy-optimizer` 参数。
5. **已支持模型**：InternVL 与 Qwen2VL 已在模型入口脚本侧完成 patch 导入适配（原文："InternVL/Qwen2VL 已支持"）。
6. **参数位置**：启用参数 `GPT_ARGS` 属于 Megatron 风格的启动参数集合，与模型训练脚本并行配置。

---

## 【关键机制与数据】

- **问题识别机制**：朴素 pipeline parallel 隐含假设每个 stage 都至少存在一个需要更新的 parameter 与一条可反向传播的计算图。原文并未给出具体 stage 数 / 显存节省量 / 吞吐对比等性能数据。
- **数据流 / 工作原理**（基于原文描述还原）：
  1. **optimizer 阶段**：当检测到某 stage 无 parameter 需要更新时，dummy optimizer 创建空 tensor 占位，保持 optimizer.step() 调用路径合法。
  2. **backward 阶段**：在 pipeline parallel 的反向前置判断 `grad_fn` 是否存在；若不存在（占位 tensor 无梯度函数），则跳过该 stage 的反向计算，避免空图反向报错。
- **性能数据**：原文未提供任何 benchmark 数字、显存收益或加速比，原文标注："原文未涉及性能数据"。

---

## 【表格解读】

**原文无表格。** 整篇文档未出现任何参数表、性能对比表或配置项表格，所有信息均以段落与代码片段形式呈现。

---

## 【公式解读】

**原文无公式。** 文档未包含任何 LaTeX 公式或伪代码形式的数学表达式，机制描述完全采用自然语言 + 代码片段。

---

## 【关联】

- **与模型入口脚本的关系**：dummy_optimizer 需要在模型入口脚本中显式 `from mindspeed_mm.patchs import dummy_optimizer_patch` 完成 patch 注入，原文明确指出"InternVL/Qwen2VL 已支持"，意味着这两类模型的入口脚本已包含该 import 行；其他模型若要使用，需自行添加 patch 导入。
- **与 pipeline parallel 的关系**：dummy_optimizer 是对 pipeline parallel 行为的一层修补（patch），并非替换 pipeline parallel 本身，其判断点（"在 pipeline parallel 的反向前加判断"）嵌于 pipeline parallel 的反向流程中。
- **与启动参数集合的关系**：启用开关 `--enable-dummy-optimizer` 挂在 `GPT_ARGS` 这一 Megatron 风格启动参数字符串中，与其他训练超参同一层级配置。
- **上下游模块**：上游为 `mindspeed_mm.patchs` 包（patch 模块的载体），下游为 Megatron 风格的 optimizer 与 pipeline parallel scheduler。原文未给出其它内部链接，故更细粒度的上下游调用关系原文未涉及。

---

## 【使用方法】

**步骤一：在模型入口脚本中导入 patch 模块**（原文已明确 InternVL/Qwen2VL 支持）

```python
from mindspeed_mm.patchs import dummy_optimizer_patch
```

**步骤二：在模型启动 shell 中追加 `--enable-dummy-optimizer` 参数**

```shell
GPT_ARGS="
    ...
    --enable-dummy-optimizer \
"
```

**注意事项**（基于原文信息整合）：
- 两步缺一不可：仅导入 patch 不传参数、或仅传参数不导入 patch，均无法生效。
- 非 InternVL / Qwen2VL 的模型需先确认 patch 模块已适配，原文未涉及更广泛的模型支持列表。
- 启用条件由具体 stage 是否所有 parameter 都无需更新决定，原文未给出自动检测逻辑的进一步说明。
