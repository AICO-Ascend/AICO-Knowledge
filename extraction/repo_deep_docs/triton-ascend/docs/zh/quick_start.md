# 快速入门

> 仓 `triton-ascend` · 路径 `docs/zh/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-ascend/docs/zh/quick_start.md

```markdown
# Triton-Ascend 快速入门文档深度解读

## 【定位】
这篇文档面向初次接触 Triton-Ascend 的开发者,系统性回答"如何在华为昇腾 NPU 上从零搭建 Triton 编程环境并跑通第一个向量加法示例",覆盖环境要求、Docker/Python 双路线安装、示例运行以及 GPU→NPU 的 API 平移迁移方法。

---

## 【技术要点】

1. **硬件/系统兼容边界**:支持 linux(aarch64/x86_64)、Ascend Atlas A2/A3 系列;推荐最小显存 32GB(单卡);Python 限定 **3.9–3.13**,其中 py3.9 **不**支持 aarch64;CANN 优先选 **9.0.0**。
2. **软件依赖项**:Python + CANN_TOOLKIT + CANN_OPS + [`requirements.txt`](../../requirements.txt) + [`requirements_dev.txt`](../../requirements_dev.txt);安装命令为 `pip install -r requirements.txt -r requirements_dev.txt`。
3. **两种安装路径**:(a) `pip install triton-ascend` 拉取稳定版;(b) Docker 镜像通过 `--build-arg` 注入 `CHIP_TYPE`、`CANN_VERSION`。
4. **依赖覆盖机制(自 3.2.1 起)**:安装 Triton-Ascend 会先装社区 Triton,再由 Triton-Ascend **覆盖同名 `triton` 包目录**;x86 依赖 `triton==3.2.0`,arm 依赖 `triton==3.5.0`(社区 3.5 才提供 arm 包);若后续显式升级社区 Triton 仍可能冲突,需先同时卸载两者再重装。
5. **Docker 设备透传要求**:容器启动需透传 `/dev/davinci0..7`、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,并挂载 `/usr/local/dcmi`、`npu-smi`、Ascend driver、`/home`、ascend_install.info;`--shm-size=512g` 与 `--privileged`。
6. **GPU→NPU API 平移**:仅需替换 4 处接口 —— `device='cuda' → 'npu'`、`.cuda() → .npu()`、`torch.cuda.current_device() → torch.npu.current_device()`、`torch.cuda.synchronize() → torch.npu.synchronize()`;`@triton.jit` 核函数与 Launch grid 调用方式保持不变。
7. **示例验证标准**:向量加法示例对照 `assert_close(..., rtol=1e-3, atol=1e-3)`,并打印 "The maximum difference between torch and triton is 0.0"。

---

## 【关键机制与数据】

- **自动调优/编译/部署三层能力(原文)**:文档开篇指出 Triton-Ascend 在兼容 Triton 核心语法的基础上,做了"自动解析核函数参数、优化内存访问逻辑、完善安全部署机制"三类深度优化,以适配昇腾 NPU 特性。
- **CANN 安装环境变量生效(原文)**:`source ${HOME}/Ascend/ascend-toolkit/set_env.sh` 仅在当前 shell 窗口生效,推荐写入 `.bashrc`;root 默认安装路径 `/usr/local/Ascend`,非 root 为 `${HOME}/Ascend`;安装耗时约 **5–10 分钟**(原文)。
- **依赖覆盖工作流(原文)**:`pip install triton-ascend` 触发"先安装社区 Triton,再由 Triton-Ascend 覆盖同名目录",目的是缓解"安装其他依赖 Triton 的包时再次安装 Triton 而覆盖 Triton-Ascend"。该机制被作者显式标注为"并不能彻底消除冲突"。
- **向量加法示例与对照(原文)**:运行 `python3 ./triton-ascend/third_party/ascend/tutorials/01-vector-add.py` 后预期两条 `tensor([0.8329, 1.0024, 1.3639, ..., 1.0796, 1.0406, 1.5811], device='npu:0')` 完全相同,差异归零打印 "The maximum difference between torch and triton is 0.0"。
- **核函数运行参数(原文)**:示例 `@triton.jit add_kernel(x_ptr, y_ptr, output_ptr, n_elements, BLOCK_SIZE)` 在测试中被实例化为 `SIZE=98432, BLOCK_SIZE=1024`(原文 `@pytest.mark.parametrize('SIZE,BLOCK_SIZE', [(98432, 1024)])`),Launch grid 通过 `triton.cdiv(SIZE, meta['BLOCK_SIZE'])` 动态生成,核函数本体不需修改。
- **mask 安全访问机制(原文)**:核函数中通过 `mask = offsets < n_elements` 与 `tl.load(..., mask=mask)` / `tl.store(..., mask=mask)` 完成边界安全访问,这是 Triton→NPU 迁移时无需改动的通用语义。

---

## 【表格解读】

### 表 1:Docker 构建参数(原文逐字还原)

| 参数名称      | 默认值          | 可选值                                                  |
| ----------- | ------------ | ---------------------------------------------------- |
| CHIP_TYPE   | A3           | A3、910b                                              |
| CANN_VERSION| 9.0.0(推荐)    | 9.0.0、8.5.0、8.3.RC1、8.3.RC2、8.2.RC1、8.2.RC2      |

**逐行解读**:
- `CHIP_TYPE=A3` 是默认(也是文档示例采用)的目标芯片型号,可选项 `A3` 与 `910b` 表明目前 Docker 镜像同时覆盖 Atlas A3 与 910b 系列;用户可通过 `npu-smi` 查看自家 NPU 型号后再选取。
- `CANN_VERSION=9.0.0` 为推荐默认值,可选版本跨度从 9.0.0 到 8.2.RC2 共 6 档,说明 CANN 版本需要与昇腾固件/驱动匹配;任意一档都不与 `CHIP_TYPE` 互相约束,默认组合即可满足 A3 + CANN 9.0.0 这一文档推荐的部署形态。

### 表 2:CHIP_TYPE 与整机/产品系列对应关系(原文逐字还原)

| 选项序号 | CHIP_TYPE 参数值 | 对应机器/产品系列 | 典型整机 |
| :---: | :---: | :---: | :---: |
| 1 | `A3` | Atlas A3 训练系列产品 | Atlas 900 A3 SuperPoD |
| 2 | `A2` | Atlas A2 训练系列产品 | Atlas800T A2 |

**逐行解读**:
- 选项 1 给出 `A3` 对应 Atlas A3 训练系列,典型机型为 Atlas 900 A3 SuperPoD;这是文档示例与默认 `CHIP_TYPE` 取值,也是 CANN 9.0.0 推荐的部署形态。
- 选项 2 给出 `A2` 对应 Atlas A2 训练系列,典型机型为 Atlas800T A2;但表 1 中可选项并未列出 `A2`,意味着此行更多作为产品族族谱参考,实际 Docker 构建时需以表 1 为准。

### 表 3:GPU → NPU API 替换对照(原文逐字还原)

| GPU 写法                         | NPU 写法                        |
| ------------------------------- | ------------------------------- |
| `device='cuda'`                 | `device='npu'`                  |
| `tensor.cuda()`                 | `tensor.npu()`                  |
| `torch.cuda.current_device()`   | `torch.npu.current_device()`    |
| `torch.cuda.synchronize()`      | `torch.npu.synchronize()`       |

**逐行解读**:
- 第 1 行:`torch.randn`/`torch.device` 等张量构造函数上的设备串,直接做字符串替换即可。
- 第 2 行:张量搬运方法 `.cuda()` → `.npu()`,可链式使用在任何 `Tensor` 上。
- 第 3 行:查询当前进程所在设备索引的接口,迁移前要确保 NPU runtime 已被 torch-npu 注入。
- 第 4 行:同步阻塞接口,在 `assert_close` 这类需要确定性结果比较时必须替换,否则 NPU 上的异步流可能让 CPU 侧读到未完成的结果。

---

## 【公式解读】

原文无 LaTeX 数学公式。文档中出现的"伪代码形式"主要是 `@triton.jit` 标注的向量加法核函数(原文逐字保留):

```
@triton.jit
def add_kernel(
    x_ptr, y_ptr, output_ptr,
    n_elements,
    BLOCK_SIZE: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    x = tl.load(x_ptr + offsets, mask=mask)
    y = tl.load(y_ptr + offsets, mask=mask)
    tl.store(output_ptr + offsets, x + y, mask=mask)
```

符号含义:
- `x_ptr / y_ptr / output_ptr`:输入与输出张量的设备端首地址(运行时传入的 `Tensor` 由 Triton 桥接为指针)。
- `n_elements`:参与运算的总元素数,本示例为 `98432`(原文)。
- `BLOCK_SIZE: tl.constexpr`:编译期常量,每块处理的元素数,本示例为 `1024`(原文)。
- `pid = tl.program_id(axis=0)`:当前程序实例在 axis=0 方向的 ID,用于按 block 切分数据。
- `block_start = pid * BLOCK_SIZE`:当前 block 处理区间的起始下标。
- `offsets = block_start + tl.arange(0, BLOCK_SIZE)`:构成长度为 `BLOCK_SIZE` 的下标向量 `[block_start, block_start+1, ..., block_start+BLOCK_SIZE-1]`。
- `mask = offsets < n_elements`:对超出 `n_elements` 的尾部 block 做边界保护,避免越界读写。
- `tl.load(..., mask=mask)` / `tl.store(..., x + y, mask=mask)`:按掩码安全完成两路加载与一路加法回写。

侧向关联的宿主侧调用(原文逐字保留):

```
def grid(meta):
    return (triton.cdiv(SIZE, meta['BLOCK_SIZE']),)
add_kernel[grid](x, y, output, SIZE, BLOCK_SIZE=BLOCK_SIZE)
```

符号含义:
- `triton.cdiv(SIZE, meta['BLOCK_SIZE'])`:向上取整除法,以本示例 `SIZE=98432, BLOCK_SIZE=1024` 计算,得到 grid 长度 `97`,表示将整个输入切分为 97 个 block 并行处理。
- `meta['BLOCK_SIZE']`:从 autotuner/`constexpr` 反射出的块大小元数据。
- `add_kernel[grid](x, y, output, SIZE, BLOCK_SIZE=BLOCK_SIZE)`:通过 Launch grid 语法发起 NPU 上的核函数调用。

---

## 【关联】

依据文末及文档中给出的内部链接可见的能力串联:

- **[`../../requirements.txt`](../../requirements.txt) 与 [`../../requirements_dev.txt`](../../requirements_dev.txt)**:Python 与 Triton-Ascend 运行期/开发期依赖清单,文档在"环境要求 → 软件依赖"和"requirements 安装"两处显式 pip 调用。本文档不展开列项,但在文末"环境搭建"环节再次被引用。
- **[`installation_guide.md`](installation_guide.md)**:文档在"环境搭建"小节明确"可根据[安装指南](installation_guide.md)的环境准备章节步骤搭建 Triton-Ascend 环境",本文档承担"快速试用"与该详尽安装文档之间的引导关系。
- **[`../../third_party/ascend/tutorials/01-vector-add.py`](../../third_party/ascend/tutorials/01-vector-add.py)**:既是"运行 Triton 示例"章节的最小可运行实例入口,也是"从 GPU 到 NPU:迁移 Triton 示例"章节中两段代码(原始 GPU 版本与 diff 形式迁移版本)所共享的核函数原型来源。文档中的核函数与 Launch grid 调用(`add_kernel[grid](x, y, output, SIZE, BLOCK_SIZE=BLOCK_SIZE)`)正是出自该文件。
- **在线文档链 `https://triton-ascend.readthedocs.io/zh-cn/latest/index.html`**:覆盖环境搭建、算子开发、调优实践与 FAQ,被作为"完整的在线文档与网络资料"的总入口,本文档是其下的"快速入门"分篇。
- **CANN 社区下载链 `https://www.hiascend.com/cann/download`**:在"软件依赖"小节被引用,负责按 CPU 架构/OS/CANN 版本/安装方式给出确切安装命令。
- **PyPI 镜像链 `https://test.pypi.org/project/triton-ascend/#history`**:与"也可以自行下载 nightly 包"步骤绑定,对应"注意 2/3"对 nightly 风险的提示。
- **迁移小节中的"`x, y, output`"与"`SIZE, BLOCK_SIZE`"**:在"运行 Triton 示例"与"从 GPU 到 NPU"两节中复用同一组核函数参数命名,体现"同一份 Triton 代码,更换设备标识即可在 NPU 上运行"的最小改动论断。

---

## 【使用方法】

### A. 直接 pip 安装(原文给出)
```shell
pip install triton-ascend
# 配套依赖:
pip install -r requirements.txt -r requirements_dev.txt
```
- 自 3.2.1 起该安装会自动覆盖同名 `triton` 包目录。
- 如需 nightly 包,从 `https://test.pypi.org/project/triton-ascend/#history` 自行下载并选择匹配 Python 版本与 aarch64/x86_64 架构的包。

### B. Docker 安装(原文给出)
```bash
git clone https://gitcode.com/Ascend/triton-ascend.git && cd triton-ascend
docker build \
--build-arg CHIP_TYPE=A3 \
--build-arg CANN_VERSION=9.0.0 \
-t triton-ascend-image:latest -f ./docker/Dockerfile .
```
- 可选 `CHIP_TYPE`:A3 / 910b;`CANN_VERSION`:9.0.0 / 8.5.0 / 8.3.RC1 / 8.3.RC2 / 8.2.RC1 / 8.2.RC2。
- 启动容器需透传 davinci 系列设备节点、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,挂载 `/usr/local/dcmi`、`npu-smi`、Ascend driver、`/home`、`/etc/ascend_install.info`,并设置 `--shm-size=512g --privileged --security-opt seccomp=unconfined --net=host`(原文命令)。

### C. 验证环境(原文给出)
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
git clone https://triton-ascend/README.md  # 拉源码仓(源码编译安装运行示例时需拉)
python3 ./triton-ascend/third_party/ascend/tutorials/01-vector-add.py
```
预期输出(原文):两条 `device='npu:0'` 的相同 `tensor` + `The maximum difference between torch and triton is 0.0`。

### D. GPU→NPU 迁移步骤(原文给出的可复用 diff)
1. `torch.cuda.current_device()` → `torch.npu.current_device()`
2. `device='cuda', dtype=torch.float32` → `device='npu', dtype=torch.float32`(对 `x`、`y`、`output_cpu` 同样处理)
3. `output_cpu.cuda()` → `output_cpu.npu()`
4. `torch.cuda.synchronize()` → `torch.npu.synchronize()`
5. `@triton.jit` 核函数与 `add_kernel[grid](x, y, output, SIZE, BLOCK_SIZE=BLOCK_SIZE)` Launch 调用 **保持不变**(原文 diff 中未改动该部分)。

### E. 配置项与命令汇总(原文未涉及)
- 文档未给出 Triton-Ascend 自身的运行时配置开关(如环境变量、CLI flag)、autotuner 参数或 NPU 设备选择(`DEVICE_ID` 等)的环境变量;`CHIP_TYPE`/`CANN_VERSION` 仅为 Docker 构建参数;运行时配置项**原文未涉及**。
```
