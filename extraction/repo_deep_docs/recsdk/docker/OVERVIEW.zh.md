# RecSDK Docker 镜像构建概览与说明

> 仓 `recsdk` · 路径 `docker/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docker/OVERVIEW.zh.md

# RecSDK Docker 镜像构建概览深度解读

## 【定位】
本文档是 RecSDK（面向互联网市场搜索推荐广告的昇腾应用使能 SDK）在 `docker/` 目录下 Dockerfile 文件的官方索引与使用说明，旨在帮助开发者快速理解镜像 tag 命名规范、按需拉取/构建容器镜像、切换底层 Python 框架环境并完成端到端验证。

---

## 【技术要点】

1. **镜像 tag 六段式命名规范**：`{RecSDK版本}-{CANN版本}-{chip}-{OS版本}-{Python版本}-{框架标识}`，例如 `26.1.0-cann9.1.0-910-ubuntu20.04-py3.7-tf`；其中 `{chip}` 通过 `--build-arg CORE_TYPE=a2/a3/a5` 注入：`CORE_TYPE=a2 → 910`、`CORE_TYPE=a3 → a3`、`CORE_TYPE=a5 → 950`。
2. **当前发布矩阵（RecSDK 26.1.0）**：4 个 Dockerfile，覆盖 `tf`/`pt` × `ubuntu20.04`/`ubuntu22.04`/`openEuler22.03` 四种组合，CANN 统一为 9.1.0；芯片字段 `{chip}` 取值 `910`（Atlas 800T A2）、`a3`（Atlas 800T A3）、`950`（昇腾950代际）。
3. **物理架构自动鉴别**：构建早期使用 `ARCH=$(uname -m)` 识别 x86/ARM，依据分支拉取对应 GCC、系统动态库与 whl/run 包。
4. **芯片按需构建**：通过 `--build-arg CORE_TYPE=...` 仅安装目标芯片架构的 CANN toolkit 与 ops 包，避免镜像体积膨胀。
5. **多框架隔离方案**：放弃全局系统 Python 混装，改用 `python3.7 -m venv` 为每个框架创建独立虚拟环境（如 `/opt/buildtools/tf1_env`、`/opt/buildtools/tf2_env`、`/opt/buildtools/torch_v1_pt2.6.0` 等共 5 个 PT 环境 + 2 个 TF 环境）。
6. **关键依赖自源码编译**：与硬件强耦合的 GCC 11.2、CMake、OpenMPI、Python 等不再使用系统包管理器，统一采用 `make install` 源码编译以保证 ABI 一致性。

---

## 【关键机制与数据】

- **数据流/工作原理**：文档不涉及训练数据流本身，而是描述容器化交付链路——`docker build` 通过 `--build-arg CORE_TYPE` 触发芯片分支 → 镜像构建 → `docker run` 挂载宿主驱动（`/usr/local/Ascend/driver:ro`、`/etc/ascend_install.info`）与 NPU 卡（`ASCEND_VISIBLE_DEVICES=0-7`） → 容器内通过 `source /opt/buildtools/*_env/bin/activate` 切换框架 → `npu-smi info` 验证。
- **性能/规模数据（原文）**：RecSDK 稀疏表规模"可超 10TB"，支持"加速卡内存、主机内存、主机磁盘多级存储"以及"多机存储、动态扩容"。
- **环境规格（原文）**：推荐 Docker ≥ 20.10（须支持 `--net=host`）；构建镜像建议预留至少 **60 GB** 可用空间；推荐内存 `-m 300g`（示例值），CANN 建议 ≥ 9.1.0；NPU 卡示例 `0-7`（16 卡时可设为 `0-15`）。
- **支持的宿主 OS（原文）**：Ubuntu 20.04 / 22.04（x86_64 或 ARM）、openEuler 22.03（x86_64 或 ARM）。
- **支持框架版本（原文）**：TF 1.15.0、TF 2.6.5；PyTorch 2.6.0 / 2.7.1 / 2.10.0（对应 `torch_rec_v1` 与 `torch_rec_v2` 两个系列）。
- **支持芯片（原文）**：Atlas 800T A2（训练服务器）、Atlas 800T A3（超节点服务器）、昇腾 950 代际（`a5`）。

---

## 【表格解读】

### 表 1：RecSDK 26.1.0 Dockerfile 归档

| Tag | Dockerfile |
|-----|------------|
|26.1.0-cann9.1.0-{chip}-ubuntu20.04-py3.7-tf|[Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-ubuntu20.04-py3.7-tf)|
|26.1.0-cann9.1.0-{chip}-ubuntu22.04-py3.11-pt|[Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-ubuntu22.04-py3.11-pt)|
|26.1.0-cann9.1.0-{chip}-openEuler22.03-py3.7-tf|[Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-openEuler22.03-py3.7-tf)|
|26.1.0-cann9.1.0-{chip}-openEuler22.03-py3.11-pt|[Dockerfile](https://gitcode.com/Ascend/RecSDK/blob/develop/docker/Dockerfile.26.1.0-cann9.1.0-openEuler22.03-py3.11-pt)|

**逐行解读**：
- 第 1 行：TF + Ubuntu 20.04 + Python 3.7 组合，对应传统 TF 1.15 / 2.6 用户的最小阻力路径。
- 第 2 行：PT + Ubuntu 22.04 + Python 3.11 组合，为 PyTorch 2.6/2.7/2.10 用户的默认推荐栈。
- 第 3 行：TF + openEuler 22.03 + Python 3.7 组合，面向部署在 openEuler 服务器上的 TF 训练场景。
- 第 4 行：PT + openEuler 22.03 + Python 3.11 组合，覆盖国产化操作系统 + 新版 PyTorch 的全栈方案。
- 四行共同点：`{chip}` 占位符由构建期 `CORE_TYPE` 注入，所有镜像共用同一组 CANN（9.1.0）与 RecSDK（26.1.0）基线版本。

### 表 2：前提条件

| 项目 | 要求 |
|------|------|
| Docker 版本 | 建议 20.10 及以上，需支持 `--net=host` 网络模式 |
| 宿主操作系统 | Ubuntu 20.04 / 22.04（x86_64 或 ARM）、openEuler 22.03（x86_64 或 ARM） |
| 昇腾驱动与固件 | 宿主机需安装 Ascend NPU 驱动及固件，驱动路径默认为 `/usr/local/Ascend/driver` |
| CANN 版本 | 建议 CANN 9.1.0 及以上（可参照Dockerfile配置下载链接，默认下载9.1.0版本） |
| 磁盘空间 | 构建镜像建议预留至少 60 GB 可用空间 |
| 网络 | 构建过程中需访问外部网络以下载依赖包 |

**逐行解读**：
- Docker 行：`--net=host` 是容器内 RDMA/NPU 通信与分布式集合通信的基础，不可用将直接导致多卡训练失败。
- OS 行：与表 1 镜像矩阵中的 OS 字段一一对应；同时覆盖 x86_64 与 ARM，说明 Dockerfile 已内置架构分支。
- 驱动与固件行：默认路径 `/usr/local/Ascend/driver` 也是 `docker run` 时 `-v` 挂载的只读路径源。
- CANN 行：与镜像内置版本一致，避免 host/容器版本不一致导致算子加载失败。
- 磁盘行：60 GB 是构建期下载、解压、编译（CANN toolkit/ops、GCC、CMake、OpenMPI、Python 源码）的安全阈值。
- 网络行：构建期需要联网获取所有 whl/run 包，构建机不可断网。

### 表 3：CORE_TYPE 与 tag 芯片标识映射

| CORE_TYPE | 适用平台 | tag 芯片标识 |
|-----------|----------|-------------|
| `a2` | Atlas 800T A2 训练服务器 | `910` |
| `a3` | Atlas 800T A3 超节点服务器 | `a3` |
| `a5` | 昇腾950代际产品 | `950` |

**逐行解读**：
- 第 1 行：当前默认与主推的 A2 训练服务器，对应昇腾 910 系列芯片。
- 第 2 行：A3 超节点服务器，使用 `a3` 而非数字标识，体现超节点平台差异化（与普通 A2 不可混用 CANN toolkit）。
- 第 3 行：昇腾 950 代际产品（含 `a5` 内部代号），代表下一代的算子与内存层级。
- 注意：tag 中的 `910` 与 `CORE_TYPE=a2` 不是字面相等——文档通过命名映射来对齐硬件代号与软件发布代号。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档内部与外部链接指向以下上下游模块/资源：

- **仓库主入口**：`https://gitcode.com/Ascend/RecSDK`（RecSDK 代码）与 `https://gitcode.com/Ascend/RecSDK/issues`（问题反馈）——容器使用的根社区。
- **文档根目录**：`https://gitcode.com/Ascend/RecSDK/tree/develop/docs`——RecSDK 主体功能文档（特征保存/加载、特征准入、特征淘汰、稀疏表多级存储等）。
- **4 个 Dockerfile 路径**：分别对应 TF/PT × Ubuntu/openEuler 四个组合（见上方表格 1 的链接），是本文档直接管理的对象。
- **little demo（TF）**：`https://gitcode.com/Ascend/RecSDK/blob/develop_examples_and_tools/examples/demo/README.md`——端到端验证 TF 镜像的训练链路。
- **little demo（PT）**：`https://gitcode.com/Ascend/RecSDK/blob/develop_examples_and_tools/torch_examples/little_demo/README.md`——端到端验证 PT 镜像的训练链路。
- **许可证**：`https://gitcode.com/Ascend/RecSDK/blob/develop/LICENSE`——RecSDK 与 Mind 系列软件的法律条款。
- **英文版镜像概览**：`https://gitcode.com/Ascend/RecSDK/blob/develop/docker/OVERVIEW.md`——本文档的英文对照。
- 与 RecSDK 主体的关系：本文档不描述训练框架本身（单机单卡、多机多卡、稀疏表 10TB+ 规模），仅描述其容器化交付形态；功能细节需回查 RecSDK 主文档。

---

## 【使用方法】

### 1. 拉取并运行已有镜像

```bash
docker run -it \
    --name {容器名} \
    --net=host \
    -m 300g \
    -e ASCEND_VISIBLE_DEVICES=0-7 \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver:ro \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v {挂载目录}:{挂载目录} \
    {镜像名}:{镜像tag} \
    /bin/bash
```

关键参数：`--net=host`（RDMA 通信）、`-m 300g`（内存限制）、`ASCEND_VISIBLE_DEVICES=0-7`（指定可见 NPU 卡范围）、驱动目录只读挂载。

### 2. 本地构建镜像

```bash
# PyTorch + Ubuntu 22.04（推荐）
docker build --build-arg CORE_TYPE=a2 \
  -t recsdk_pt:26.1.0-cann9.1.0-910-ubuntu22.04-py3.11-pt \
  -f docker/Dockerfile.26.1.0-cann9.1.0-ubuntu22.04-py3.11-pt .

# TensorFlow + Ubuntu 20.04
docker build --build-arg CORE_TYPE=a2 \
  -t recsdk_tf:26.1.0-cann9.1.0-910-ubuntu20.04-py3.7-tf \
  -f docker/Dockerfile.26.1.0-cann9.1.0-ubuntu20.04-py3.7-tf .
```

`CORE_TYPE` 默认 `a2`，可选 `a2/a3/a5`，对应 tag 中的 `910/a3/950`。

### 3. 切换 Python 框架虚拟环境

TF 容器：
```bash
source /opt/buildtools/tf1_env/bin/activate   # TF 1.15.0
source /opt/buildtools/tf2_env/bin/activate   # TF 2.6.5
```

PT 容器（共 5 个环境）：
```bash
source /opt/buildtools/torch_v1_pt2.6.0/bin/activate
source /opt/buildtools/torch_v1_pt2.7.1/bin/activate
source /opt/buildtools/torch_v1_pt2.10.0/bin/activate
source /opt/buildtools/torch_v2_pt2.7.1/bin/activate
source /opt/buildtools/torch_v2_pt2.10.0/bin/activate
deactivate   # 退出
```

### 4. 二次开发（在基础镜像上叠加业务层）

```dockerfile
FROM recsdk_tf:26.1.0-cann9.1.0-910-ubuntu20.04-py3.7-tf
RUN apt update -y && apt install ...
```

### 5. 端到端验证流程

1. 构建镜像（见 §2）→ 2. `docker run` 启动容器（同 §1）→ 3. 容器内 `npu-smi info` 验证 NPU 可见 → 4. `source` 激活对应虚拟环境 → 5. 参考 little demo（TF 链 `examples/demo/README.md` 或 PT 链 `torch_examples/little_demo/README.md`）跑通训练任务。

### 6. 故障排查要点（原文摘要）

- **NPU 不可见**：检查宿主机驱动、`-v` 驱动挂载、`ASCEND_VISIBLE_DEVICES` 取值范围。
- **非特权容器 NPU 占用冲突（错误码 -8020）**：方案 1——不同容器挂载不同 NPU 卡（修改 `ASCEND_VISIBLE_DEVICES`）；方案 2——加 `--privileged`（需评估安全风险）。
- **容器内存不足**：增大或移除 `-m`。
- **环境切换后框架版本未生效**：`deactivate` 后再 `source`，并用 `which python` 确认指向 `/opt/buildtools/` 下虚拟环境。
