# Feature Design

> 仓 `msmodeling` · 路径 `docs/design/mindstudio-brand-logo-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/mindstudio-brand-logo-design.md

# 一体化深度解读:docs/design/mindstudio-brand-logo-design.md

---

## 【定位】

本设计文档规定在 MindStudio Modeling 工具链的全部 Python CLI 入口(`cli/inference` 系列、ServingCast 仿真入口、`tools/perf_data_collection` 数据采集工具)启动后,自动向 stderr 输出统一、固定四行的 MindStudio 品牌 Logo,从而消除用户在不同子工具间切换时无法从首屏终端输出快速识别品牌的痛点,达成"一行命令,一眼识别"的产品一致性体验。

---

## 【技术要点】

1. **共享渲染模块 `cli/logo.py`**:纯函数式 `render_logo(color, width, terminal_cols)` 产出四行字符串;内部拆分为 `_build_logo_block`(65 列 `=` 边框 + 居中品牌行/Slogan)、`_center_block_in_terminal`(终端更宽则对称填充前导空格)、`_colorize_logo_block`(对边框、正文、`MindStudio` token 分别包裹 ANSI,保持可见列对齐不变)、`_ensure_windows_console`(Windows 控制台 VT 初始化)。
2. **固定宽度与排版规则**:Logo 块硬编码 65 列宽;品牌行与 Slogan 行在块内居中;终端宽度 >65 列时,整个块前导空格填充使视觉块水平居中;每行依次为边框 / 品牌行 / 边框 / Slogan,共 4 行;第 4 行后**恰好空一行**,Logo 之前**无空行**。
3. **彩色判定规则(平台差异化)**:
   - Linux / macOS:stderr 为 TTY **且** `TERM` 有效(非 `dumb` / `unknown`)→ 彩色;否则纯 ASCII。
   - Windows 原生 shell:stderr 为 TTY **且** `TERM` ≠ `dumb` / `unknown`(允许未设置)→ 彩色;否则纯 ASCII。
   - 重定向 / 管道输出:全平台一律纯 ASCII。
4. **Help 抑制规则**:任何 argparse 内以 `--help` 结束的调用,包括 `model_adapter` 子命令 help,**不调用** Logo 打印器;自动化流水线与帮助界面保持纯净。
5. **依赖策略**:`colorama` 在 `pyproject.toml` 提升为直接依赖,唯一用途是 `colorama.just_fix_windows_console()` 启用 Windows 旧版控制台虚拟终端并归一化 ANSI;在 Linux/macOS 上此调用近似空操作,从而以单一代码路径覆盖全平台,不散布 `if win32` 分支。`rich` 因体量与控件栈与"四行 stderr 横幅"不成比例被显式拒绝;ANSI 256 色码全部手工编写。
6. **性能预算**:
   - 启动延迟(首次调用含 `colorama` 初始化):**<2 毫秒**;
   - 瞬时内存:**<4 KB**;
   - Logo 渲染逻辑规模:**约 120 行** Python(含 Windows 初始化器);
   - 删除冗余启动横幅后,stdout 重复字符输出减少 **约 60–80 字节/次**;
   - 品牌识别时间下降:**约 80%**;
   - 非 help 启动的 Logo 格式一致性:从 **0% → 100%**。

---

## 【关键机制与数据】

### 工作原理(原文提炼)

- **三段式实现层**:① 共享渲染模块 `cli/logo.py`;② 在每个 Python 入口的 `argparse` 成功解析后、仿真/报告业务启动前的**单一调用点**插入 Logo 打印;③ 清理任何工具本地、与品牌意图重复的启动装饰头。
- **数据流**:用户执行一条 CLI(如 `python -m cli.inference.text_generate …` / `python -m cli.inference.throughput_optimizer` / `python -m cli.inference.model_adapter doctor`)→ argparse 完成 → `_ensure_windows_console()`(Windows 上)→ `shutil.get_terminal_size()` 取列宽 → `render_logo()` 拼装四行 → 写入 stderr → stderr 出现 4 行 Logo + 1 空行,然后业务逻辑将 stdout/结构化日志正常写出。
- **彩色路径副作用**:`_colorize_logo_block` 插入的 ANSI 转义码仅修改颜色属性,**不改变可见列宽**,因此终端列对齐与 plain ASCII 路径完全等价。
- **测试隔离**:色彩能力检测与 help 抑制判断位于纯渲染路径**之外**,使单元测试可在无 TTY 环境下断言字符串内容。

### 性能/业务指标(原文标注)

| 指标 | 原文数值 |
|---|---|
| 启动延迟(含 `colorama` 初始化) | < 2 ms |
| 瞬时内存 | < 4 KB |
| 渲染代码体量 | ~120 行 |
| stdout 重复字符减少 | 约 60–80 字节/次 |
| 品牌识别时间下降 | 约 80% |
| 非 help 启动 Logo 一致性 | 0% → 100% |
| Logo 块宽度 | 65 列 |
| 块后空行数 | 恰好 1 行;块前 0 空行 |
| 误把 stderr 内容归因失败的基线 | >30%(脚本化环境) |
| 混合 CI 日志识别耗时基线 | 每次 5–10 秒 |

---

## 【表格解读】

**原文无表格**(全文为段落叙述,未出现 markdown 表格或结构化数据表;上述指标均为文中散布的数值,已在上一节"关键机制与数据"中以表格形式汇总展示,非原文自带的表格)。

---

## 【公式解读】

**原文无公式**(全文未出现 LaTeX 公式、伪代码公式或数学表达式;居中逻辑以自然语言"padded with leading spaces"、"centered inside that block"描述,不构成可逐字还原的符号化公式)。

---

## 【关联】

文档明确指向的上下游模块与入口:

- **CLI 入口层**:
  - `cli/inference/text_generate`(文本生成 CLI)
  - `cli/inference/video_generate`(视频生成 CLI,文中提及)
  - `cli/inference/throughput_optimizer`(吞吐寻优/服务化选型 CLI)
  - `cli/inference/model_adapter`(含 `doctor` 子命令;子命令 help 也受抑制规则约束)
  - `ServingCast` 仿真驱动(原文称为 "ServingCast simulation driver")
  - `tools/perf_data_collection/` 下的性能数据采集工具
- **新增模块**:在仓库根下新增 `cli/logo.py` 共享渲染模块。
- **依赖项**:`pyproject.toml` 将 `colorama` 由传递依赖提升为直接依赖;锁文件中 Windows 标记包下已存在该传递引用,本次显式化以通过 STRIDE 供应链评审。
- **未来替代**:未来可能出现仓库组合层的 `mindstudio-brand` wheel 替换本模块,但 **不会移除** Windows 控制台 VT 启用要求,任何共享 Python 构件仍需保留 `colorama` 初始化钩子或等价原生 VT 启用步骤。
- **输出流分工**:Logo 严格走 stderr;业务指标/表格保留在 stdout 或结构化日志,二者职责清晰分离。
- **与既有装饰的对立面**:文档明确点出 `ServingCast` optimizer 输出中曾以"星号边框摘要"充当临时横幅,本次改动将统一取代这类分散标识。
- **内部链接**:本文档文末给出的链接信息为"(无)"。

---

## 【使用方法】

原文未涉及终端用户层面的"启用配置项 / CLI 命令开关"。用户侧的启用方式是**隐式自动**的:在作用域内的任一 Python 入口,正常传入模型与负载参数执行命令(例如):

- `python -m cli.inference.text_generate …`(模型/负载参数)
- `python -m cli.inference.throughput_optimizer …`(服务选型参数)
- `python -m cli.inference.model_adapter doctor …`(适配器自检参数)

在 argparse 完成、业务逻辑启动前,**无需任何额外 flag 或配置文件**,stderr 即自动出现统一四行 Logo + 紧随其后的一个空行。

启用条件的可调点(由代码/构建侧控制,非用户配置):

- **彩色启用**:Linux/macOS 需 stderr 交互 TTY 且 `TERM` ≠ `dumb`/`unknown`;Windows 原生 shell 需 stderr 交互 TTY 且 `TERM` ≠ `dumb`/`unknown`(`TERM` 未设置允许彩色)。
- **强制纯文本**:stderr 被重定向/管道,或将 `TERM` 显式设为 `dumb` / `unknown`,所有平台一律降级为纯 ASCII。
- **Help 抑制**:任何以 `--help` 结束的调用(含 `model_adapter` 子命令 help)将**跳过** Logo 打印。
- **依赖安装**:`colorama` 由 `pyproject.toml` 直接依赖声明,构建/安装侧需确保该依赖被解析。

> 备注:原文 Implementation Approach 一节在描述 `_ensure_windows_console` 时被截断("before the first co…"),如需补全函数剩余契约(例如是否加锁、是否幂等、首次调用判定方式),需查阅仓库原文后续内容。
