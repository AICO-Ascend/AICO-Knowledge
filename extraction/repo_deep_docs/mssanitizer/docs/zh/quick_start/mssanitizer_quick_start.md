# msSanitizer 算子检测工具快速入门

> 仓 `mssanitizer` · 路径 `docs/zh/quick_start/mssanitizer_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mssanitizer/docs/zh/quick_start/mssanitizer_quick_start.md

# msSanitizer 快速入门 · 一体化深度解读

---

## 【定位】

本文档是面向昇腾 AI 处理器场景下,**单算子开发过程中运行时缺陷检测的入门实操指南**。它以"简易加法算子 AddCustom"为载体,演示 msSanitizer 工具在**内存越界、竞争条件、未初始化变量、同步异常**四类隐蔽缺陷上的快速检测能力,目的是让初学者在最短路径上感知该工具为算子开发带来的"高效与便捷"。

---

## 【技术要点】

1. **四大检测子功能并列存在**(原文:"包含单算子开发场景下的内存检测、竞争检测、未初始化检测和同步检测四个子功能"),但本文档仅实际演示了其中三类命令:`memcheck`、`racecheck`、`initcheck`,同步检测子工具的命令未在文中给出。
2. **强前置环境约束**:仅支持标准化 CANN 容器环境,裸机/虚拟机/其他非标准容器均不兼容;环境变量必须存在 `ASCEND_HOME_PATH` 与 `ATB_HOME_PATH`;示例代码仓必须位于 `~/ot_demo/msot/example/quick_start`;外网可达时安装耗时约 3 分钟。
3. **检测能力的注入机制**:通过在 Kernel 侧 `op_kernel/CMakeLists.txt` **首行**插入 `-sanitizer` 编译选项(原文:"为启用检测能力,需在 Kernel 侧的 CMakeLists.txt 首行插入 sanitizer 编译选项,注入检测桩代码"),使能工具的检测桩。
4. **构造演示型缺陷**:在 `op_kernel/add_custom.cpp` 的 `CopyOut` 函数中,把 `DataCopy` 的拷贝长度由 `this->tileLength` 改为 `2 * this->tileLength`(原文:"将 DataCopy 内存拷贝长度增加一倍,触发'非法读取'"),作为可复现的内存越界用例。
5. **三段式工具调用语法**:`mssanitizer --tool=<subtool> -- bash run.sh`,通过 `--tool` 选择检测子功能,以 `--` 分隔后跟实际算子运行脚本。
6. **环境变量冲突的容错**:重新部署时若提示 `ASCEND_CUSTOM_OPP_PATH` 含冒号分隔的多路径(原文报错内容已逐字给出),需执行 `unset ASCEND_CUSTOM_OPP_PATH` 后再重试。

---

## 【关键机制与数据】

### 工作原理(整合解读,均基于原文)

整篇文档展示的是**"改一行代码 → 注入检测桩 → 跑三类检测 → 看三类报错 → 还原文件"**的闭环:

- **检测桩注入**:`add_ops_compile_options(ALL OPTIONS -sanitizer)` 或 `npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)` 二选一,前者优先(由 `if/elseif` 分支决定)。
- **缺陷构造**:把 `DataCopy(... , this->tileLength)` 改为 `DataCopy(... , 2 * this->tileLength)`,等价于把单次拷贝长度翻倍,从而越过 `zGm` 的合法范围,制造可被 `memcheck` 抓到的越界读/写。
- **构建部署链路**:`bash ./build.sh` 生成 `build_out/custom_opp_*.run` 安装包,再用 `bash $MY_OP_PKG` 完成部署;`run.sh` 在 `~/ot_demo/workspace/src/caller` 下驱动算子运行。
- **三类错误报告的共同结构**:`======` 分隔的标题行(WARNING/ERROR + 缺陷类型 + 大小) → 位置行(地址 + 存储对象 + 算子 hash 名 + 设备/Block/aiv + pc + serialNo) → 5 帧调用栈(`#0` ~ `#5`,均落到 `/usr/local/Ascend/.../tikcpp/tikcfw/impl/dav_c220/kernel_operator_data_copy_impl.h` 等底层 + 用户算子 `add_custom.cpp` 的具体行号)。

### 关键数据(原文标注)

| 维度 | memcheck 输出 | racecheck 输出 | initcheck 输出 |
|---|---|---|---|
| 严重级别 | WARNING | ERROR | ERROR |
| 缺陷类型 | out of bounds | Potential WAR hazard | uninitialized read |
| 大小 | 256 | (以 PIPE_MTE3 Read at WAR()+0x400 描述) | 256 |
| 存储对象 | GM(writing) | UB | UB |
| 算子 hash | AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 | AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 | AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 |
| Block/Device | block aiv(1) on device 0 | block 0 (aiv) on device 0 | block aiv(0-7) on device 3 |
| pc / serialNo | 0x1e28 / 87 | 0x1e28 / 31 | 0x1e34 / 241 |
| 栈顶调用栈命中行 | `add_custom.cpp:128` | `add_custom.cpp:128` | `add_custom.cpp:126` |
| CANN 版本路径(原文呈现) | `ascend-toolkit/8.3.RC1/aarch64-linux/tikcpp/tikcfw/impl/dav_c220` | `ascend-toolkit/8.3.RC1/...` | `cann-8.5.0/aarch64-linux/asc/impl/basic_api/dav_c220` |

> 原文数据点补充说明:同一次"越界缺陷"在三类工具上分别呈现为不同语义——`memcheck` 抓到的是 GM 上的越界写(WARNING 级别,`block aiv(1) on device 0`),`racecheck` 把它解读为 UB 上的 WAR(Write-After-Read)竞争危险(`block 0 (aiv) on device 0`),`initcheck` 把它解读为 UB 上 256 字节的未初始化读(`block aiv(0-7) on device 3`,注意 device 号与 block 范围都不同于前两者,体现三类检测的并行探针视角)。

### 重要差异点:`-sanitizer` 在底层框架链路中的两个备选 API

- `add_ops_compile_options(ALL OPTIONS -sanitizer)`:面向新版本 msopgen 工程的统一编译选项注入入口。
- `npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)`:面向旧版本工程或仅 NPU Kernel 子集的注入入口。
- 文档用 `if/elseif` 串联两段,意在兼容两类工程模板——任意版本都能落地检测桩。

---

## 【表格解读】

**原文无表格。**(文中全部以代码块、diff 块、纯文本错误报告形式呈现,未出现任何参数表/性能对比表/配置项表,因此按要求标注"原文无表格"。)

---

## 【公式解读】

**原文无公式。**(全文唯一的算术表达式为 `2 * this->tileLength`,这是 C++ 代码中的乘法字面量,不是数学/性能公式形式,故按要求标注"原文无公式"。)

---

## 【关联】

虽然文档结尾"内部链接"为空,但文中明确**外部引用**了以下两份上游/伴生文档,这些引用决定了 msSanitizer 体验链路的边界:

1. **《算子开发工具链快速入门》(`op_tool_quick_start.md`)**——本文档的逻辑前置:
   - 第二节"概述"明确:本文档"以您已完成该文档的全流程操作为前提"。
   - 第二节"算子工程准备完成"进一步指向其 **2.3 节"开发构建算子工程 msopgen"**——本文档演示的 `AddCustom` 工程、`build.sh`、`custom_opp_*.run`、`run.sh` 等产物均由该节产出。
2. **《昇腾 AI 算子开发工具链学习环境安装指南》(`installation_guide.md`)**——本文档的物理前置:
   - 强制前置步骤,2.1.1 节唯一引用点;安装完成后才能进入容器自检脚本(`/.dockerenv` + 环境变量 + 代码仓目录三件套 PASS 校验)。

**与算子开发主链路的关系**(基于原文链式推断):

```
installation_guide.md  →  op_tool_quick_start.md (2.3 msopgen 生成 AddCustom 工程)
        ↓
   mssanitizer_quick_start.md  ← (本文档,基于已完成工程做四类检测体验)
        ↓
   检测结果反馈至 op_kernel/add_custom.cpp 源码行(128/126/63/169 等)
```

**工具内部的子模块关系**:msSanitizer 是一个伞形工具(`mssanitizer` 二进制),下挂 4 个子工具——`memcheck`、`racecheck`、`initcheck`,以及**文中只提到存在但未演示命令**的同步检测(从行文"建议先跟随操作体验效果,原理部分可稍后阅读"可知,完整能力不止三类)。

---

## 【使用方法】

### 启用前的硬性准备(原文 2.1)

1. 在标准化 CANN 容器内安装好对应环境(指引见 `installation_guide.md`)。
2. 执行 2.1.2 的两段自检 bash 脚本,容器检查 + 代码仓检查两行输出都必须为 `[PASS]`;任一为 `[FAIL]` 不得继续。

### 检测能力启用(原文 2.3.1)

在 `~/ot_demo/workspace/src/AddCustom/op_kernel/CMakeLists.txt` 的**首行**之前插入(原文中用 `printf ... | cat - CMakeLists.txt > tmp && mv -f tmp CMakeLists.txt` 的方式前置):

```cmake
if(COMMAND add_ops_compile_options)
  add_ops_compile_options(ALL OPTIONS -sanitizer)
elseif(COMMAND npu_op_kernel_options)
  npu_op_kernel_options(ascendc_kernels ALL OPTIONS -sanitizer)
endif()
```

### 构造可复现缺陷(原文 2.3.2)

修改 `op_kernel/add_custom.cpp` 的 `CopyOut`:

```diff
- AscendC::DataCopy(zGm[progress * this->tileLength], zLocal, this->tileLength);
+ AscendC::DataCopy(zGm[progress * this->tileLength], zLocal, 2 * this->tileLength);
```

### 重新编译部署(原文 2.3.3)

```bash
cd ~/ot_demo/workspace/src/AddCustom
bash ./build.sh
MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
```

若报 `ASCEND_CUSTOM_OPP_PATH` 含冒号多路径错误,执行 `unset ASCEND_CUSTOM_OPP_PATH` 后重试。

### 三类检测命令(原文 2.3.4 / 2.3.5 / 2.3.6)

```bash
cd ~/ot_demo/workspace/src/caller
mssanitizer --tool=memcheck -- bash run.sh     # 内存检测
mssanitizer --tool=racecheck -- bash run.sh    # 竞争检测
mssanitizer --tool=initcheck -- bash run.sh    # 未初始化检测
```

### 还原现场(原文 2.3.7)

```bash
cd ~/ot_demo/workspace/src/AddCustom
\cp -f ~/ot_demo/msot/example/quick_start/msopgen/code/op_kernel/add_custom.cpp \
      ~/ot_demo/workspace/src/AddCustom/op_kernel/
\cp -f op_kernel/CMakeLists.txt.bak op_kernel/CMakeLists.txt
```

### 配置项速查(基于原文 `--tool=` 取值与编译选项)

| 配置/参数 | 取值 | 作用 |
|---|---|---|
| `--tool=memcheck` | 内存检测子工具 | 捕获 GM/UB 等地址上的越界读/写,输出 WARNING |
| `--tool=racecheck` | 竞争检测子工具 | 捕获 WAR/WAW 等流水线冒险,输出 ERROR |
| `--tool=initcheck` | 未初始化检测子工具 | 捕获 UB 等地址上的未初始化读,输出 ERROR |
| 编译选项 `-sanitizer` | 注入到 Kernel 编译流程 | 在编译产物中埋入检测桩,使运行时检测成为可能 |
| `ASCEND_CUSTOM_OPP_PATH` | 部署期环境变量 | 多路径冒号分隔时会触发报错,需 `unset` 后重部署 |

> 同步检测(`synccheck` 或同类)子工具的命令与配置:**原文未涉及**(仅在概述中列名,未给出命令)。
