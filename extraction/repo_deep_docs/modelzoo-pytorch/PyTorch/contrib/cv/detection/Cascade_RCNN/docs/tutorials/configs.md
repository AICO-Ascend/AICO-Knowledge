# Configs

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/configs.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/configs.md

## 【定位】

这篇文档介绍 Detectron2 基于 **YAML、yacs 和 CfgNode** 的键值配置系统，说明其基础操作、配置继承、版本兼容、命令行覆盖、外部项目扩展及最佳实践。

## 【技术要点】

1. **配置格式与实现**
   - Detectron2 使用 **YAML** 和 [yacs](https://github.com/rbgirshick/yacs) 实现配置系统。
   - 配置以键值对形式组织，基础操作通过 `CfgNode` 完成，包括读取、更新、加载和输出配置，详见 `CfgNode` API。

2. **基础配置操作**
   ```python
   from detectron2.config import get_cfg
   cfg = get_cfg()    # obtain detectron2's default config
   cfg.xxx = yyy      # add new configs for your own custom components
   cfg.merge_from_file("my_cfg.yaml")   # load values from a file

   cfg.merge_from_list(["MODEL.WEIGHTS", "weights.pth"])   # can also load values from a list of str
   print(cfg.dump())  # print formatted configs
   ```
   - `get_cfg()` 获取 Detectron2 默认配置。
   - 通过属性赋值添加自定义配置项。
   - 支持从 YAML 文件或字符串列表合并配置。
   - `cfg.dump()` 输出格式化后的配置。

3. **基础配置继承**
   - 子配置可以通过以下字段先加载基础配置：
     ```yaml
     _BASE_: base.yaml
     ```
   - 如果子配置与基础配置存在同名项，**子配置中的值会覆盖基础配置中的值**。
   - Detectron2 为标准模型架构提供了若干基础配置，以复用公共设置。

4. **配置版本管理**
   - 配置文件可以包含版本字段：
     ```yaml
     VERSION: 2
     ```
   - 即使 Detectron2 后续修改某些配置键，带版本的配置仍然能够被识别，以保证向后兼容。
   - 读取没有版本号的配置时，Detectron2 会输出警告。
   - 官方配置不包含版本号，因为官方配置被定位为始终保持最新。

5. **命令行覆盖**
   - Detectron2 的许多内置工具接受命令行配置覆盖。
   - 命令行传入的键值对会覆盖配置文件中的现有值。
   - 原文示例为：
     ```shell
     ./demo.py --config-file config.yaml [--other-options] \
       --opts MODEL.WEIGHTS /path/to/weights INPUT.MIN_SIZE_TEST 1000
     ```
   - 该命令使用 `MODEL.WEIGHTS` 指定权重路径，并使用 `INPUT.MIN_SIZE_TEST 1000` 设置测试输入尺寸为 `1000`。

6. **配置系统边界**
   - 配置是一种表达能力有限的语言，并非 Detectron2 的全部功能都能通过配置项开放。
   - 如果某个需求无法在配置空间中表达，应直接使用 Detectron2 API 编写代码。

## 【关键机制与数据】

- **原文:** `get_cfg()` 首先获得 Detectron2 的默认配置，用户可以添加自定义键，也可以调用 `merge_from_file()` 从 YAML 文件加载配置，或调用 `merge_from_list()` 从字符串列表加载配置，最后通过 `dump()` 查看完整配置。

- **原文:** 含有 `_BASE_: base.yaml` 的配置会先加载 `base.yaml`。基础配置与子配置发生键冲突时，子配置值覆盖基础配置值，由此实现公共设置的复用和差异化配置。

- **原文:** 配置版本由 `VERSION` 字段标识。Detectron2 即使在未来修改部分配置键，也会继续识别已经版本化的配置，从而维持向后兼容；缺少版本号则会触发警告。

- **原文:** 命令行配置覆盖发生在配置文件加载之后，以命令行传入的键值对为准。因此，`MODEL.WEIGHTS` 和 `INPUT.MIN_SIZE_TEST` 等设置可以直接覆盖 `config.yaml` 中已有的同名配置。

- **原文:** 外部项目如果定义了自己的配置项，需要先将这些配置注册到 `CfgNode`。示例通过 `add_pointrend_config(cfg)` 加载 PointRend 的默认配置，然后才能使用该项目的配置空间。

- **原文:** 文档没有提供吞吐量、精度、显存、训练时间或其他性能对比数据。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **`CfgNode` 基础操作**
  - 文档中的 `get_cfg()`、属性赋值、`merge_from_file()`、`merge_from_list()` 和 `dump()` 均建立在 `CfgNode` 的访问与更新能力之上。
  - 内部链接：`../modules/config.html#detectron2.config.CfgNode`

- **命令行与 demo 工具**
  - `demo.py` 是配置系统的下游使用入口之一，能够读取 `--config-file`，并通过 `--opts` 对已有配置执行运行时覆盖。
  - 内部链接：`../../demo/demo.py`

- **配置参考体系**
  - `Config References` 汇总 Detectron2 可用配置及其含义，是查阅配置键、配置层级和值用途的主要入口。
  - 内部链接：`../modules/config.html#config-references`

- **标准模型基础配置**
  - Detectron2 提供的标准模型架构基础配置位于配置继承机制的上游：子配置加载这些基础文件，只覆写自身需要调整的设置。

- **外部项目扩展**
  - 项目位于 Detectron2 库之外时，可以定义自己的配置，并通过 `add_pointrend_config(cfg)` 一类注册函数将默认配置加入 Detectron2 的 `CfgNode`；配置系统因此可以承载项目级功能，但仍受“配置表达能力有限”这一边界约束。

- **API 回退路径**
  - 当目标能力无法通过配置表达时，应从配置层转向 Detectron2 API 编写实现代码；因此配置系统不是所有功能的唯一入口。

## 【使用方法】

1. **获取默认配置并添加自定义配置**
   ```python
   from detectron2.config import get_cfg
   cfg = get_cfg()    # obtain detectron2's default config
   cfg.xxx = yyy      # add new configs for your own custom components
   ```

2. **从 YAML 文件加载配置**
   ```python
   cfg.merge_from_file("my_cfg.yaml")
   ```

3. **从字符串列表加载或覆盖配置**
   ```python
   cfg.merge_from_list(["MODEL.WEIGHTS", "weights.pth"])
   ```

4. **使用基础配置并在子配置中覆盖设置**
   ```yaml
   _BASE_: base.yaml
   ```

5. **为自定义或实验配置声明版本**
   ```yaml
   VERSION: 2
   ```

6. **通过命令行运行 demo 并覆盖配置**
   ```shell
   ./demo.py --config-file config.yaml [--other-options] \
     --opts MODEL.WEIGHTS /path/to/weights INPUT.MIN_SIZE_TEST 1000
   ```

7. **为外部项目注册默认配置**
   ```python
   from point_rend import add_pointrend_config
   cfg = get_cfg()    # obtain detectron2's default config
   add_pointrend_config(cfg)  # add pointrend's default config
   # ... ...
   ```

8. **输出当前配置**
   ```python
   print(cfg.dump())
   ```

9. **查看 Detectron2 可用配置及其含义**
   - 使用文档提供的 `Config References` 内部链接；原文未给出单独的命令。
