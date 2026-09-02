# 特性设计

> 仓 `msit` · 路径 `docs/design/msprechecker-security-simplification.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msit/docs/design/msprechecker-security-simplification.md

# msprechecker 安全校验简化设计文档深度解读

## 【定位】

本文档描述对 msprechecker 预检工具文件与路径安全策略的简化改造——剥离对 msguard 第三方安全库的属主/权限位/软链接拦截等过严预检查，将其与 MindStudio 工具链统一原则对齐，使预检、落盘、规则执行在 Docker 容器、NFS 共享挂载、多用户协作、跨 UID 映射等真实 AI 开发场景下不再误判中断。

## 【技术要点】

1. **移除读取侧属主与权限位校验**：取消原 msguard `open_s` 对 inode 属主与权限位的固定模板检查，文件是否可读完全交给操作系统权限机制；不再递归修正第三方文件或目录权限。
2. **放宽软链接策略**：用户显式传入的路径若为软链接不再拦截（由内核解析后只做存在性与大小检查）；目录递归遍历时不跟随软链接（跳过以避免循环引用），输入根路径本身允许为软链接。
3. **放宽长度上限**：命令行参数与配置文件路径不再使用 msguard 固定上限；若工具代为创建的文件或环境变量超出 `PATH_MAX`/`ARG_MAX`，以 EAFP 方式捕获系统错误并返回明确失败信息。
4. **替换 msguard 文件 API 为 pathlib**：约 15 处 `open_s` 调用改为 `pathlib.Path` 的 `open`、`read_text`、`write_text`；权重采集的 `walk_s` 改为 `path_io.iter_regular_files` 栈式递归遍历，并在每个普通文件上校验大小不超过 **10 GiB**（`DEFAULT_MAX_FILE_BYTES = 10 * 1024 ** 3`）；全改造过程禁止新增 `os.path` 调用，路径在 CLI 边界一次性转为 `Path` 后向内传递。
5. **替换参数校验 API**：`validate_args(Rule.input_file_read)` 改为 `path_io.readable_file` 或 `as_arg_type` 组合；`Rule.input_file_exec.is_satisfied_by` 改为模块级一次性 `os.access` 判定。
6. **输出侧权限遵循当前进程 umask**：落盘 JSON、`msprechecker_env.sh` 及输出目录均按当前进程 umask 创建；README 建议非 root 用户安装前执行 `umask 0027`，权限由用户与管理员自行管理。
7. **依赖与文档清理**：从 `pyproject.toml` 删除 `msguard` 包，清理全部 import 语句及相关测试 mock 路径；更新 README 文档约束说明。

## 【关键机制与数据】

**入口层集中校验机制**：所有用户可见的路径类 argparse 参数在 CLI 入口一次性接入 `as_arg_type`（组合 normalize + 若干 PathCheck），完成后下游只接受 `Path` 类型，不再重复 `is_file` 或权限位判断。

**路径规范化流程**（原文：`normalize_user_path`）：`Path(value).expanduser().resolve()`——先展开 `~` 与用户主目录，再解析符号链接并消除 `..` 分量，返回绝对真实路径。

**可组合校验链**（原文：第 1 步落地代码）：`check(predicate, message)` 把具名谓词或 `partial` 绑定后的谓词包装为 `PathCheck`；`as_arg_type(*checks)` 串联 normalize 与若干 `PathCheck`；预置 `readable_file = as_arg_type(is_file, is_readable)`、`existing_dir = as_arg_type(is_dir)`；其余场景可直接 `as_arg_type(is_file, has_suffix(".txt"))`。

**栈式递归遍历**（原文：`iter_regular_files`）：维护 `stack = [root]`，pop 出 `current`，对 `current.is_dir()` 失败的项跳过；`iterdir()` 抛 `OSError` 时跳过；对每个 entry，先 `is_symlink()` 跳过，再若是目录则压栈，若是文件且 `suffix` 匹配且 `st_size <= max_bytes` 则 yield；中途 `OSError` 一律 `continue`；约束根 root 须为入口已 normalize 的 Path。

**读取侧 EAFP 改造**：12 个源文件删除 `open_s` 及重复存在性判断；collector/checker/cmate 构造函数参数类型标注为 `Path`，实现体直接 `path.open`/`read_text`；异常由 `error_handler` 捕获标准 `OSError`/`PermissionError`。

**configs 复合参数分量收口**（原文：`_parse_config_entry`）：以 `:` 分隔 name 与 raw_path，再对 `raw_path.split("@", 1)[0]` 调用 `readable_file`，返回 `(name, Path)` 元组。

**性能/验收目标**（原文）：权重哈希采集、规则文件加载等操作的启动延迟预计降低（因不再执行 msguard 附带的权限与软链接全量扫描）；在 Docker、NFS、共享集群多用户及 root 运行场景测试中功能用例中断率目标为零。

## 【表格解读】

原文无表格（文档以功能点编号列表、代码块、文字段落形式呈现）。

## 【公式解读】

原文中的显式算式仅一处（常量定义）：

```python
DEFAULT_MAX_FILE_BYTES = 10 * 1024 ** 3
```

- 符号含义：`DEFAULT_MAX_FILE_BYTES` 是单文件大小上限常量；右侧 `10 * 1024 ** 3` 即 10 × (1024)³ 字节。
- 数值：`1024 ** 3 = 1 073 741 824`，乘以 10 得 **10,737,418,240 字节 ≈ 10 GiB**。
- 作用：在 `iter_regular_files` 中作为 `max_bytes` 默认值，对每个普通文件执行 `entry.stat().st_size <= max_bytes` 校验，超出则跳过，保证权重采集不会因异常巨大的单个文件耗尽内存或长时间阻塞。

## 【关联】

原文未提供内部链接（"(无)"）。依据文档中提及的上下游关系，可梳理出以下结构关联：

- **上游改造对象**：`msguard` 安全库（原属主/权限位/软链接/长度上限逻辑的承担者），本次完全脱离其作为 msprechecker 的依赖。
- **本工具子命令**：`precheck`、`dump`、`compare`、`run`、`inspect`（以及 `_cmate.py`、`legacy.py`），其 argparse 参数在 CLI 层一次性接入新校验器。
- **落盘输出文件**：`msprechecker_env.sh`、落盘 JSON（`msprechecker_output_name`）、输出目录——均按 umask 创建。
- **下游数据流**：`Coordinator.execute` / `Dump 策略` / `RunStrategy` 从 `args` 取出的路径字段类型为已 `resolve` 的 `Path`，向下游 `collector`、`checker`、`cmate` 引擎传递时不再调用 `Path()` 或 `is_file`。
- **横向模块一致性**：与 MindStudio 工具链统一安全策略、Python 编码规范（pathlib、EAFP、禁止新增 `os.path` 调用）保持一致；与上游"读取侧存在性与大小底线校验"原则保留对齐。
- **测试与文档**：相关测试 mock 路径需同步清理；README 需补充 `umask 0027` 等权限管理说明。

## 【使用方法】

**启用方式**：本次改造为 msprechecker 自身行为的重构，无需用户主动开关，按既定六步落地后自动生效。

**关键配置项 / 命令 / 环境变量**（原文涉及）：

- **CLI 层 argparse type**（推荐写法示例，原文）：
  - `type=readable_file` —— 用于 `--mies-config-path` 等配置文件路径（normalize + 是文件 + 可读三合一）。
  - `type=existing_dir` —— 用于 `--weight-dir` 等目录路径（normalize + 是目录）。
  - `type=normalize_user_path` —— 仅需 normalize、无需存在性校验的参数可直接使用。
- **环境变量 / 权限设置**：
  - `umask 0027` —— README 建议非 root 用户安装前执行，以自行管控输出暴露面。
- **内部约束**：
  - 输入根路径可为软链接（权重目录），但 `iter_regular_files` 遍历时跳过子项中的软链接。
  - 单个权重/规则文件大小上限 `DEFAULT_MAX_FILE_BYTES = 10 * 1024 ** 3`（≈ 10 GiB），超出即跳过。
  - 全改造过程禁止新增 `os.path` 调用，路径在 CLI 边界一次性转为 `Path` 后向内传递。
  - 落盘输出目录在写入侧通过 `output_dir.mkdir(parents=True, exist_ok=True)` 创建，不在 argparse 层 mkdir。
  - 内部固定路径（如 `/proc/cpuinfo`）以 `Path` 常量定义，不经过 `normalize_user_path`。
  - 手动拼接相对路径时须对拼接结果再次 `resolve`，必要时以 `relative_to` 确认未逃逸根目录。

## 图文联合解读

- `image.png`: 图绘msprechecker三支子流：CLI入口经`path_io`+`as_arg_type`一次性normalize校验后由Coordinator分发；读取侧采EAFP、跳软链接、不预检属主与权限位；输出统一以mode 640落盘。论证了"校验前移CLI边界、读写两侧权限策略对称（输入由OS决定、输出由umask 0o027决定）"的改造结论，呼应文档"脱离msguard、对齐MindStudio工具链统一原则"的核心论点。
- `image.png`: 图绘msprechecker三支子流：CLI入口经`path_io`+`as_arg_type`一次性normalize校验后由Coordinator分发；读取侧采EAFP、跳软链接、不预检属主与权限位；输出统一以mode 640落盘。论证了"校验前移CLI边界、读写两侧权限策略对称（输入由OS决定、输出由umask 0o027决定）"的改造结论，呼应文档"脱离msguard、对齐MindStudio工具链统一原则"的核心论点。
- `image.png`: 图绘msprechecker三支子流：CLI入口经`path_io`+`as_arg_type`一次性normalize校验后由Coordinator分发；读取侧采EAFP、跳软链接、不预检属主与权限位；输出统一以mode 640落盘。论证了"校验前移CLI边界、读写两侧权限策略对称（输入由OS决定、输出由umask 0o027决定）"的改造结论，呼应文档"脱离msguard、对齐MindStudio工具链统一原则"的核心论点。
- `image.png`: 图绘msprechecker三支子流：CLI入口经`path_io`+`as_arg_type`一次性normalize校验后由Coordinator分发；读取侧采EAFP、跳软链接、不预检属主与权限位；输出统一以mode 640落盘。论证了"校验前移CLI边界、读写两侧权限策略对称（输入由OS决定、输出由umask 0o027决定）"的改造结论，呼应文档"脱离msguard、对齐MindStudio工具链统一原则"的核心论点。
