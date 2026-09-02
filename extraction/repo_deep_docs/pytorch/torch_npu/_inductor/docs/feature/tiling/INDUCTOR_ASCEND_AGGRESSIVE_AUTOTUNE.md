# INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/tiling/INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/tiling/INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE.md

# INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE 深度解读

## 【定位】

本文档描述 Inductor 在昇腾后端的 **batch profiler 开关能力** —— 通过环境变量 `INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE` 控制是否启用 batch profiler,默认值为 `0`(关闭)。

---

## 【技术要点】

1. **功能本质**:该特性是一个**二元开关**(on/off),控制 Inductor 编译流程中 batch profiler 的启用状态。
2. **取值范围**:仅两个有效取值 —— `"0"` 表示关闭,`"1"` 表示开启。
3. **默认值**:`"0"`(关闭),即在用户未显式设置时,batch profiler 不参与编译过程。
4. **配置方式**:通过 shell 环境变量 `INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE` 设置,数值以字符串形式赋值。
5. **使用约束**:原文标注为"无",即文档未声明额外的使用限制条件。
6. **支持硬件**:仅在昇腾 Atlas A2 / A3 / A5 系列产品上提供该能力,非昇腾后端不受此环境变量控制。

---

## 【关键机制与数据】

- **核心机制**:开关控制的对象是 **batch profiler** —— Inductor 在昇腾后端执行编译期自动调优(auto-tuning)时所依赖的一类 profiling 子模块。开启后,Inductor 会在编译过程中执行更激进的 profiling 采集,以支撑 autotune 决策。
- **数据流**:文档原文未给出数据流图、采集指标、采样次数、profile overhead 等具体细节;仅声明"开启/关闭"这一行为差异。
- **性能数据**:原文**未提供**任何定量性能数据(无时延对比、无加速比、无显存收益),仅做开关式描述。

> 原文:"控制是否启用batch profiler,默认值为0。"
> 原文:"'0'为关闭","'1'为开启"

---

## 【表格解读】

**原文无表格**。整篇文档不含任何参数表、性能对比表或配置矩阵。

---

## 【公式解读】

**原文无公式**。整篇文档不包含 LaTeX 公式或伪代码表达式。

---

## 【关联】

文档内部链接信息标注为"(无)",原文未显式建立与其他特性/模块的引用关系。

不过从命名与上下文可推断的隐含关联(仅为推断,**非原文明确陈述**):
- **Inductor 自动调优框架**:环境变量名中 `AGGRESSIVE_AUTOTUNE` 暗示其与 Inductor 的 autotune 流程耦合,开启后应影响 autotune 阶段的策略激进程度。
- **batch profiler 自身**:作为开关的目标对象,该特性需依赖 batch profiler 子模块的存在与可用性。

> 严格按原文:无内部链接、无交叉引用、无上下游模块名列举。

---

## 【使用方法】

**启用 batch profiler**:

```shell
export INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE=1
```

**关闭/恢复默认**:

```shell
unset INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE
# 或
export INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE=0
```

**生效条件**:需运行于 **Atlas A2 / Atlas A3 / Atlas A5 系列产品** 之上,PyTorch 通过 TorchNPU 后端调用 Inductor 编译流程时方可生效。

**配置项**:原文仅给出唯一环境变量 `INDUCTOR_ASCEND_AGGRESSIVE_AUTOTUNE`,未涉及 `torch.compile()` 参数、config 字典或其他配置文件入口。
