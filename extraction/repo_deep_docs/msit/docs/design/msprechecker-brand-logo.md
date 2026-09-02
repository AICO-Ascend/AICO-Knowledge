# 特性设计

> 仓 `msit` · 路径 `docs/design/msprechecker-brand-logo.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msit/docs/design/msprechecker-brand-logo.md

# msprechecker 统一品牌 Logo 改造 — 设计文档深度解读

---

## 【定位】

本文档描述为 MindStudio 预检工具 msprechecker 在子命令执行业务逻辑前自动向 stderr 输出四行居中统一品牌 Logo、清理 `BannerPresenter` 旧标题式横幅并保留 `run` 子命令环境横幅输出的改造方案，解决"子命令启动输出无统一品牌标识、品牌显性化不足、帮助文本与品牌输出混杂"的问题。

---

## 【技术要点】

1. **输出通道分流**：Logo 固定写入 `stderr`，环境信息横幅保留写入 `stdout`，日志采集脚本可基于通道分别过滤品牌与业务数据。
2. **渲染双模**：`_supports_color()` 依据 `sys.stderr.isatty()` 与 `TERM` 环境变量判定，输出 `TERM` 未设置、或为 `dumb` / `unknown` 时走无色 ASCII；正常交互终端走 ANSI 彩色版（边框暗灰、正文亮白、`MindStudio` 字样绿字蓝底）。
3. **触发时机收口**：`print_logo()` 调用点统一在 `Coordinator.execute` 内 `parse_args` 成功后、`args.command` 非空且非 `--help`、策略 `execute` 之前；无子命令的裸调用与各级 `--help` 均抑制 Logo。
4. **命令差异化输出**：仅 `run` 子命令路径额外由 `RunStrategy.execute` 内部调用 `BannerPresenter.print_banner()` 输出环境横幅至 stdout；`precheck`、`dump`、`compare`、`inspect` 仅输出 Logo。
5. **旧品牌头部清理**：`BannerPresenter.render` 删除以 `TITLE` 常量居中填充等号的标题行及相关类常量；`Coordinator` 无子命令分支不再调用 `BannerPresenter`，职责与 stderr Logo 分离不出现重复。
6. **性能与资源开销**：Logo 模块为纯字符串渲染 + 一次 stderr 写入，额外内存低于 **2 KiB**，启动时延增加小于 **1 ms**，不触发子进程或网络 I/O；stdout 字节量因删除标题行减少约 **60 至 80 字符**。

---

## 【关键机制与数据】

**渲染数据流（纯函数 + 副作用分离）**：
- 模块 `msprechecker/commands/logo.py` 暴露 `render_logo(*, color: bool) -> str`（纯函数）与 `print_logo() -> None`（imperative shell）。
- `_supports_color()` 读取 `sys.stderr.isatty()` 与 `os.environ.get("TERM")`，命中 `_NO_COLOR_TERMS = frozenset({"dumb", "unknown"})` 或 `term is None` 或非 TTY 时返回 `False`。
- 固定四行模板 `_LINE_TOP` / `_LINE_BRAND` / `_LINE_SLOGAN` / `_LINE_BOTTOM` 均为模块级 `Final` 常量，`_PLAIN_LOGO` 由 `"\n".join(...)` 预拼接。

**性能与覆盖数据（原文标注）**：
- 原文：5 类子命令（precheck、compare、inspect、dump、run）在非 help 场景下 stderr Logo 覆盖率由约 **20%** 提升至 **100%**。
- 原文：单次辨认耗时预计降低约 **80%**（原 5–10 秒阅读帮助首段或横幅标题收敛为扫视 Logo 首行）。
- 原文：自动化流水线日志中品牌识别错误率估计高于 **30%**（现状），改造后目标归零。
- 原文：Logo 模块额外内存占用低于 **2 KiB**，启动时延增加小于 **1 ms**，stdout 字节量因删除标题行减少约 **60 至 80 字符**。

**已知约束（原文）**：四行"居中"指固定宽度 ASCII 模板内已对齐，非按终端列宽动态居中；列宽不足时可能折行。

---

## 【表格解读】

**原文无表格。** 文档以 plantuml 流程图、数据流图、时序图、类结构图及代码示例承载设计信息，未使用 markdown 表格形式呈现参数表或对比表。

---

## 【公式解读】

**原文无公式。** 文档中的 ANSI 控制序列（如 `\033[38;5;240m`、`\033[1;97m`、`\033[48;5;21;38;5;46m`、`\033[0m`）属于字符串字面量而非数学/逻辑公式，未以 LaTeX 或伪代码形式给出可独立解读的方程。

---

## 【关联】

**改造涉及的模块/类（按文档引用梳理）**：
- **新增模块**：`msprechecker/commands/logo.py`（含 `_supports_color`、`render_logo`、`print_logo` 三个核心符号）。
- **新增测试**：`tests/test_commands/test_logo.py`（参数化覆盖 `render_logo` 有色/无色路径，mock `_supports_color` 的 `isatty` 与 `os.environ`，monkeypatch `stderr.write` 断言尾部空行）。
- **修改类**：`msprechecker/commands/coordinator.py` 中 `Coordinator.execute`（挂载 `print_logo`、删除无子命令分支的 `BannerPresenter` 调用）。
- **修改类**：`msprechecker/commands/banner.py` 中 `BannerPresenter.render`（删除 `TITLE` 居中等号标题行与相关类常量，保留 `InfoSection` 采集逻辑与末尾分隔线）。
- **保留类**：`RunStrategy.execute`（继续在 stdout 输出环境横幅，与 stderr Logo 职责分离）。
- **上游依赖**：`argparse.ArgumentParser`（`--help` 在 `parse_args` 阶段被处理并直接退出，协调器无需额外解析 help 标志）。
- **上游依赖**：`CommandStrategyFactory.create_strategy`、`CommandType`（用于在 `Coordinator.execute` 内将 `args.command` 字符串映射为策略）。
- **上游调用**：`cli.main`（进程入口，调用 `Coordinator.execute`）。
- **无关模块**：环境横幅数据流独立于 Logo 数据流，仍由各 `InfoSection`（平台、Python 依赖、CPU、NPU、Ascend 组件）采集后写入 stdout。

文末内部链接标注为「(无)」，未提供 Git 路径或交叉引用。

---

## 【使用方法】

**启用方式（原文）**：用户无需额外参数或配置，在交互式终端执行以下任一子命令且未携带 `--help` 时自动触发：
- `msprechecker precheck`
- `msprechecker dump`
- `msprechecker compare`
- `msprechecker run`
- `msprechecker inspect`

**抑制场景（原文）**：
- 裸调用 `msprechecker`（无子命令）：仅输出帮助文本至 stdout，返回码 1，不输出 Logo。
- 任意层级 `--help`：由 `argparse` 在 `parse_args` 阶段处理并退出，不进入 `Coordinator.execute` 后续逻辑，不输出 Logo。
- 非 TTY 或 `TERM` 为 `dumb` / `unknown` / 未设置：自动降级为无色 ASCII 版 Logo，仍输出至 stderr。

**配置项 / 命令（原文未涉及）**：文档未给出独立配置开关、环境变量或 CLI flag 用于开关 Logo；Logo 的触发、降级、抑制均由代码内逻辑依据 `sys.stderr.isatty()`、`TERM` 环境变量与子命令路径自动判定。
