# Tutorial 13: Useful Hooks

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/useful_hooks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/useful_hooks.md

# 一体化深度解读: Tutorial 13 - Useful Hooks

## 【定位】
本文档是 MMDetection "Useful Hooks" 教程（Tutorial 13），集中介绍训练过程中可在关键时机插入的自定义回调机制（hooks），重点说明 YOLOX/MMDetection 内置的若干常用 hook 的功能、调用方式与扩展方法，使训练流程可观测、可控制、可扩展。

---

## 【技术要点】

1. **Hook 总览分层**：MMDetection 与 MMCV 共同提供 hook 体系，涵盖日志、评测、类别校验、内存剖析等；本文重点介绍 MMDetection 层实现的 hook，MMCV 部分需查阅 MMCV 的 `runner.md` 文档。

2. **10 个可插入点位**：
   - 全局：`before_run`、`after_run`
   - 训练：`before_train_epoch`、`before_train_iter`、`after_train_iter`、`after_train_epoch`
   - 验证：`before_val_epoch`、`before_val_iter`、`after_val_iter`、`after_val_epoch`

3. **Hook 列表（标题级提及）**：`CheckInvalidLossHook`、`EvalHook`、`DistEvalHook`、`ExpMomentumEMAHook`、`LinearMomentumEMAHook`、`NumClassCheckHook`、`MemoryProfilerHook`（带外部源码链接）、`SetEpochInfoHook`、`SyncNormHook`、`SyncRandomSizeHook`、`YOLOXLrUpdaterHook`、`YOLOXModeSwitchHook`。

4. **MemoryProfilerHook**：基于 `memory_profiler` + `psutil` 第三方依赖，记录虚拟内存、swap 内存及当前进程的内存占用，帮助定位内存泄漏。需先 `pip install memory_profiler psutil`。

5. **配置启用方式**：
   ```python
   custom_hooks = [
       dict(type='MemoryProfilerHook', interval=50)
   ]
   ```
   同款写法也用于自定义 `CheckInvalidLossHook`。

6. **自定义 Hook 三步法**：① 继承 MMCV 中 `Hook` 类并实现（如 `after_train_iter`）的检查逻辑；② 通过 `@HOOKS.register_module()` 注册到 `HOOKS` 注册表；③ 在 config 的 `custom_hooks` 列表中按 `dict(type='CheckInvalidLossHook', interval=50)` 形式挂载。

---

## 【关键机制与数据】

**MemoryProfilerHook 的工作原理**：

原文: Hook 以指定 `interval`（示例中为 `interval=50`，即每 50 个 iteration 记录一次）抓取系统的内存状态，并以日志条目形式输出到 mmdet logger 中。

**数据流 / 输出字段（原文日志样例逐字段还原）**：

原文日志原文（逐字保留）：
```
2022-04-21 08:49:56,881 - mmdet - INFO - Memory information available_memory: 246360 MB, used_memory: 9407 MB, memory_utilization: 4.4 %, available_swap_memory: 5740 MB, used_swap_memory: 2452 MB, swap_memory_utilization: 29.9 %, current_process_memory: 5434 MB
```

**原文描述的具体数值（逐字标注来自该样例日志）**：
- 系统总内存：250 GB（≈ 246360 MB 可用 + 9407 MB 已用）
- Swap 总内存：8 GB（5740 MB 可用 + 2452 MB 已用）
- 当前 swap 占用率：29.9%
- 当前内存占用率：4.4%
- 当前训练进程内存占用：5434 MB
- 日志时间戳示例：`2022-04-21 08:49:56,881`

原文叙述还点明其用途为 "grasp the memory usage of the system and discover potential memory leak bugs"。

**自定义 `CheckInvalidLossHook` 关键机制（原文代码逐字提取）**：
- 继承基类：`mmcv.runner.hooks.Hook`
- 检查函数：`torch.isfinite(runner.outputs['loss'])`
- 触发失败处理：`assert` 触发后通过 `runner.logger.info('loss become infinite or NaN!')` 记录日志
- 默认检查间隔：`interval (int): Default: 50`

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文用文字形式提到的上下游资源（无 markdown 链接，由括号中的 URL 自然呈现）：

- **MMCV Runner / Hook 基类**：所有 hook 的基类 `Hook`、注册表 `HOOKS` 来源于 `mmcv.runner.hooks`；hook 行为与生命周期由 MMCV 的 Runner 调度（外部文档：MMCV `runner.md`）。
- **MMDetection 源码中的具体 hook 实现**：例如 `MemoryProfilerHook` 指向 `mmdet/core/hook/memory_profiler_hook.py`。其余标题级 hook（`EvalHook`、`DistEvalHook`、`ExpMomentumEMAHook`、`LinearMomentumEMAHook`、`NumClassCheckHook`、`SetEpochInfoHook`、`SyncNormHook`、`SyncRandomSizeHook`、`YOLOXLrUpdaterHook`、`YOLOXModeSwitchHook`）均为 MMDetection core 中的 hook 模块。
- **进阶教程**：`customize_runtime`（外部文档 `customize_runtime.html#customize-self-implemented-hooks`）讲解如何更系统地自定义运行时 hook，与本文 "How to implement a custom hook" 部分形成上下游。
- **训练调度关系**：hook 插入点与 Runner 的训练循环（epoch/iter 级别）以及验证循环紧密耦合，因此自定义 hook 通常与 config 中的 `custom_hooks` 列表、`runner` 配置协同生效。
- **本文件目录内的姊妹教程**：作为 Tutorial 13，与其他 MMDetection tutorial（customize_runtime 等）属于同一教程体系，但本文正文未列出其他 tutorial 的具体链接。

---

## 【使用方法】

**启用 `MemoryProfilerHook`**（原文给出完整配置）：
- 依赖安装：`pip install memory_profiler psutil`
- 配置文件：
  ```python
  custom_hooks = [
      dict(type='MemoryProfilerHook', interval=50)
  ]
  ```

**启用自定义 `CheckInvalidLossHook`**（原文给出完整代码与配置）：
- 实现类：继承 `Hook`，重写 `after_train_iter`，使用 `torch.isfinite` 校验 loss（详见原文代码块）。
- 注册：使用 `@HOOKS.register_module()` 装饰器。
- 配置挂载：
  ```python
  custom_hooks = [dict(type='CheckInvalidLossHook', interval=50)]
  ```

**其他 hook（`EvalHook`、`DistEvalHook`、`ExpMomentumEMAHook`、`LinearMomentumEMAHook`、`NumClassCheckHook`、`SetEpochInfoHook`、`SyncNormHook`、`SyncRandomSizeHook`、`YOLOXLrUpdaterHook`、`YOLOXModeSwitchHook`）**：
- 原文仅以二级标题列出，未给出具体启用配置与参数；其配置项原文未涉及，需查阅 MMDetection 源码或 `customize_runtime` 教程（原文已给出该链接）。
