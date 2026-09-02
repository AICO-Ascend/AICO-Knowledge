# Tutorial 13: Useful Hooks

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/useful_hooks.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/useful_hooks.md

# 深度解读:Tutorial 13 — Useful Hooks

## 【定位】

这篇文档是 MMDetection 框架中"Hook(钩子)机制"的总览式教程,定位为**罗列并简要说明 MMDetection 已实现的若干常用 Hook 的功能边界,并给出 MemoryProfilerHook 的详细用法和"如何自定义 Hook"的范式**,目的是让用户在不阅读全部源码的前提下理解每一类 Hook 的用途,并掌握通过 `custom_hooks` 接入自定义行为的统一姿势。

## 【技术要点】

- **Hook 的分类框架**:文档以并列一级标题的形式罗列了 MMDetection 中的若干内置 Hook:`CheckInvalidLossHook`、`EvalHook`、`DistEvalHook`、`ExpMomentumEMAHook`、`LinearMomentumEMAHook`、`NumClassCheckHook`、`MemoryProfilerHook`、`SetEpochInfoHook`、`SyncNormHook`、`SyncRandomSizeHook`、`YOLOXLrUpdaterHook`、`YOLOXModeSwitchHook`。其中仅 `MemoryProfilerHook` 给出了完整说明,其余以空标题占位(指向上游 MMCV/MMDetection 的源码或文档)。
- **10 个 Hook 注入点**:文档明确给出训练生命周期内可插入 Hook 的 10 个时序节点,分三组:
  - 全局点:`before_run`、`after_run`
  - 训练阶段点:`before_train_epoch`、`before_train_iter`、`after_train_iter`、`after_train_epoch`
  - 验证阶段点:`before_val_epoch`、`before_val_iter`、`after_val_iter`、`after_val_epoch`
- **MemoryProfilerHook 的三项监控指标**:原文写明该 Hook 记录的是 `virtual memory`、`swap memory` 以及 `current process memory` 三类内存信息,用于发现潜在的内存泄漏。
- **MemoryProfilerHook 依赖与启用命令**:依赖通过 `pip install memory_profiler psutil` 安装;在 config 中通过 `custom_hooks = [dict(type='MemoryProfilerHook', interval=50)]` 启用,示例 `interval=50`。
- **自定义 Hook 的三步法**:①继承 MMCV 中 `Hook` 类并实现对应的 `after_*` 方法;②用 `@HOOKS.register_module()` 注册到 `HOOKS` 注册表;③在 config 中以 `custom_hooks = [...]` 形式挂载。
- **CheckInvalidLossHook 实现要点(范式示例)**:继承 `mmcv.runner.hooks.Hook`,`__init__` 默认 `interval=50`,在 `after_train_iter` 中调用 `self.every_n_iters(runner, self.interval)` 触发定期检查,并用 `torch.isfinite(runner.outputs['loss'])` 判定 loss 是否为 NaN/Inf,触发时打印 `'loss become infinite or NaN!'`。

## 【关键机制与数据】

> **Hook 触发时机机制(原文:)**:"In general, there are 10 points where hooks can be inserted from the beginning to the end of model training." 也就是说 Hook 不主动运行,而是由 Runner 在上述 10 个固定时序点回调查询,因此**新增自定义行为无需修改 Runner 主循环**,只需把 Hook 类注册到 `HOOKS` 即可被调度。

> **MemoryProfilerHook 工作流(原文:)**:"Memory profiler hook records memory information including virtual memory, swap memory, and the memory of the current process." 即它在每个 `interval` 迭代步通过 `psutil`/`memory_profiler` 抓取系统级(虚拟/交换)与进程级内存快照,并通过 mmdet 的 logger 以单行 `INFO` 文本写出,作者明确指出其目的是"grasp the memory usage of the system and discover potential memory leak bugs"。

> **日志样本数据(原文:)** 截取自文档,作为唯一的性能/数据样本:
> 原文:"The system has 250 GB (246360 MB + 9407 MB) of memory and 8 GB (5740 MB + 2452 MB) of swap memory in total. Currently 9407 MB (4.4%) of memory and 5740 MB (29.9%) of swap memory were consumed. And the current training process consumed 5434 MB of memory."
>
> 该样本可解读为该字段含义的样例对照:
> - `available_memory: 246360 MB` ≈ 系统空闲内存
> - `used_memory: 9407 MB` ≈ 已用内存(4.4% 利用率)
> - `available_swap_memory: 5740 MB` ≈ 空闲交换
> - `used_swap_memory: 2452 MB` ≈ 已用交换(29.9% 利用率)
> - `current_process_memory: 5434 MB` ≈ 当前训练进程占用
>
> 时间戳样本:**原文:** `2022-04-21 08:49:56,881 - mmdet - INFO - Memory information ...`

> **Loss NaN 检测的执行频率(原文:)**:`interval` 参数决定每隔多少次迭代检查一次 loss;示例代码默认值为 50,因此每 50 个 train iter 触发一次 `torch.isfinite` 判定,既不过度影响训练吞吐,又能及时捕获异常。

## 【表格解读】

原文无表格。

(文档中存在列表与代码块,但未给出任何参数表、性能对比表或配置项矩阵。)

## 【公式解读】

原文无公式。

(文档中 `torch.isfinite(runner.outputs['loss'])` 为调用语句而非公式;`custom_hooks = [dict(type='MemoryProfilerHook', interval=50)]` 为配置字典字面量,均不属于公式。)

## 【关联】

- **与 MMCV Runner 的关系(原文:)**:"For using hooks in MMCV, please read the API documentation in MMCV." — Hook 调度机制由上游 MMCV 提供,本教程只解释 MMDetection 侧已实现的封装与使用方式,文档显式给出 MMCV runner 文档的外链作为延伸阅读。
- **与 `customize_runtime` 教程的关系(原文:)**:"Please read customize_runtime for more about implementing a custom hook." — 自定义 Hook 的进阶主题(例如优先级、`priority` 字段、`before_run` vs `after_run` 区别等)被外链到 MMDetection 官方 `customize_runtime.html` 文档,**本教程自身不展开**。
- **与具体训练技巧的关系(原文内标题体现)**:文档列出但未展开的 `ExpMomentumEMAHook`、`LinearMomentumEMAHook` 与模型 EMA(指数移动平均)直接相关;`YOLOXLrUpdaterHook`/`YOLOXModeSwitchHook` 专属于 YOLOX 系列配置;`SyncNormHook`/`SyncRandomSizeHook` 涉及分布式同步与多尺度训练;`SetEpochInfoHook` 与 epoch 级信息注入相关。文档均未给出它们的具体 API 与配置示例。
- **关于内部链接**:用户标注 "(无)",但本文档原文实际包含 3 处外链(均指向 mmcv/mmdetection 官方仓库或 readthedocs 文档,非仓内路径),按"原文:"原则这里仅列出,**不臆造仓内路径链接**。

## 【使用方法】

> **启用 MemoryProfilerHook(原文:)**:
> 1. 安装依赖:`pip install memory_profiler psutil`
> 2. 在 config 文件中加入:
> ```python
> custom_hooks = [
>     dict(type='MemoryProfilerHook', interval=50)
> ]
> ```
> 训练日志中即会以 `mmdet - INFO - Memory information ...` 单行格式周期性打印内存快照。

> **启用/实现自定义 Hook 的三步法(原文:)**:
> 1. 自定义类继承 `mmcv.runner.hooks.Hook`,在 `after_train_iter` (或其他 `after_*`/`before_*` 方法) 中写入业务逻辑;
> 2. 用装饰器 `@HOOKS.register_module()` 注册到 MMCV 的 `HOOKS` 注册表;
> 3. 在 config 中以 `custom_hooks = [dict(type='YourHookName', ...)]` 挂载,例如文档示例即写作 `custom_hooks = [dict(type='MemoryProfilerHook', interval=50)]`。
>
> **关于 MMCV 侧 Hook 启用方式**:原文未在本教程中给出(如 `default_hooks`、`hook` 等其他挂载入口),只指向上游 MMCV `docs/en/understand_mmcv/runner.md` 文档,故**不补全**。
