# secure_h2d功能使用指导

> 仓 `mindie-motor` · 路径 `examples/features/security/secure_h2d/secure_h2d_user_guide.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/examples/features/security/secure_h2d/secure_h2d_user_guide.md

# secure_h2d 功能使用指导 — 一体化深度解读

---

## 【定位】

本文档描述 mindie-motor 中 **secure_h2d**（即 secure_patch）能力的**用户侧使用指导**：在不改变推理服务原有拉起流程的前提下，通过 Python 层 patch + KMSAgent 协同的方式，为 host↔device 之间的数据传输（H2D、D2H、权重加载可选）提供**应用层密钥协商与加解密保护**，解决"明文数据跨 host/device 边界传输"的安全问题。

---

## 【技术要点】

1. **保护范围明确边界**：本文档将"安全"严格限定在 **host ↔ device 跨边界传输** 这一范围；**host 内进程间安全不在覆盖范围**，默认通过 socket 文件访问控制作为信任域边界（谁能访问 socket 文件，谁就被认为能拿到密钥）。
2. **部署形态受限**：仅支持 **docker 模式**拉起的推理服务；**不支持模型并行**（一张卡不能被多个模型同时使用）；且仅适配特定版本的 **HDK** 与 **vllm-ascend**（具体版本指向 README.md）。
3. **三段式使用流程**：进入容器 → `source env_aes_ctr_a2.sh`（或同类 env 文件）→ 用正常方式拉起推理服务即可，不需要修改推理调用脚本。
4. **加解密算法可配**：通过 `SECURE_PATCH_ALG_ID` 切换，`1 = AES-CTR-128`，`2 = AES-GCM-128`；IV 长度默认 16 字节，H2D 与 D2H 方向各自维护 IV counter 以避免 IV 复用。
5. **双触发密钥轮换**：同时支持"按数据量（`SECURE_PATCH_ROTATE_BYTES = 34359738368` ≈ 32 GiB）"与"按加解密次数（`SECURE_PATCH_ROTATE_OPS = 100000000` ≈ 1 亿次）"两种轮换阈值，并通过 `SECURE_PATCH_ROTATE_PREFETCH_RATIO = 0.8` 实现提前异步预取下一组密钥以隐藏轮换延迟。
6. **密钥容灾与异步化**：每个方向缓存最多 `2` 把密钥（H2D/D2H 各保留新旧两把）；支持 fallback（`SECURE_PATCH_KEY_FALLBACK_ENABLE=1`）、失败降级（`SECURE_PATCH_KEY_FAILURE_DEMOTE_THRESHOLD=3`）、KMS 异步队列（`SECURE_PATCH_KMS_ASYNC_QUEUE_SIZE=128`），降低主路径阻塞概率。

---

## 【关键机制与数据】

### 工作原理（基于原文可推断的链路）

1. **密钥来源**：PyTorch 侧通过 UDS（Unix Domain Socket）向 **KMSAgent** 请求初始密钥与轮换密钥，路径由 `SECURE_PATCH_KMS_SOCKET`（示例 `/run/kmsagent/socket/kmsagent.sock`）指定。
2. **patch 注入点**：secure_patch 在进程内对 vLLM 的关键 IO 路径进行替换：
   - **H2D 路径**：`SECURE_PATCH_PATCH_VLLM_COPY_TO_GPU=1` → CPU→NPU 的 token 数据**Host 端加密 → Device 端解密**；
   - **D2H 路径**：`SECURE_PATCH_PATCH_ASYNC_OUTPUT_D2H=1` → NPU→CPU 的 token 输出**Device 端加密 → Host 端解密**；
   - **权重加载路径**：`SECURE_PATCH_PATCH_WEIGHT_LOADER` 默认 `0`（不加密），可按需开启走加解密流程。
3. **加解密执行**：通过 `SECURE_PATCH_HOST_CTR_MODULE`（`aes_ctr_crypt`）与 `SECURE_PATCH_HOST_CTR_FUNCTION`（`aes_ctr_cryption`）动态加载 Host 侧的 CTR 加解密函数；Device 侧加解密由算子侧承担。
4. **IV/计数器**：H2D 与 D2H 各自维护 IV counter，避免单密钥 + IV 复用带来的安全风险。
5. **轮换触发**：当某一方向累计处理数据量或加解密次数达到阈值时触发密钥轮换；`ROTATE_PREFETCH_RATIO=0.8` 使新密钥在使用量达到 80% 时即开始异步预取。
6. **轮换切换**：缓存新旧两把密钥（`MAX_KEYS_PER_DIRECTION=2`），切换窗口期内仍可解密对端使用旧密钥加密的数据；若新密钥未就绪且 `ROTATE_ALLOW_STALE=1`，允许短暂使用旧密钥以避免业务阻塞。
7. **失败兜底**：单密钥连续失败次数达到 `KEY_FAILURE_DEMOTE_THRESHOLD=3` 时被降级或从优先路径移除；启用 `KEY_FALLBACK_ENABLE=1` 时，可回退到同方向缓存中的旧密钥。
8. **KMS 容错**：连接超时 `200 ms`、接收超时 `500 ms`、总超时 `10 s`、最多重试 `3` 次、每次重试前等待 `3000 ms`，并可按 `RETRY_BACKOFF=1.0` 退避系数调节间隔。

### 数据 / 参数（原文给出的）

> 原文未提供吞吐量、延迟等性能数据；下文均为原文明确给出的**配置型参数值**，非性能测试结果。

| 参数项 | 原文值 | 原文语义 |
|---|---|---|
| `SECURE_PATCH_ROTATE_BYTES` | `34359738368`（= 32 GiB） | 数据量轮换阈值 |
| `SECURE_PATCH_ROTATE_OPS` | `100000000`（= 1 亿次） | 次数轮换阈值 |
| `SECURE_PATCH_ROTATE_PREFETCH_RATIO` | `0.8` | 预取触发点为阈值的 80% |
| `SECURE_PATCH_KMS_TIMEOUT` | `10.0 s` | 单次 KMS 请求总超时 |
| `SECURE_PATCH_KMS_RETRY_MAX` | `3` | 最大重试次数 |
| `SECURE_PATCH_KMS_RETRY_WAIT_MS` | `3000 ms` | 每次重试前等待 |
| `SECURE_PATCH_KMS_CONNECT_TIMEOUT_MS` | `200 ms` | UDS 连接超时 |
| `SECURE_PATCH_KMS_RECV_TIMEOUT_MS` | `500 ms` | 响应接收超时 |
| `SECURE_PATCH_MAX_KEYS_PER_DIRECTION` | `2` | 每方向缓存新旧 2 把密钥 |
| `SECURE_PATCH_KMS_ASYNC_QUEUE_SIZE` | `128` | 异步请求队列上限 |
| `SECURE_PATCH_IV_BYTES` | `16` | IV 长度（AES-CTR 常见 16 字节） |
| `SECURE_PATCH_DEVICE_ID_MODE` | `A3`（默认 `A2`） | device_id 映射模式（`A3` 对应 Atlas 800I A3 超节点服务器编号规则） |

> 原文：**未提供**推理 TPS、首 token 延迟、加解密吞吐等性能数据。

---

## 【表格解读】

### 表 1：基础开关与运行模式

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_DEVICE_ID_MODE` | `A3` | 指定 device_id 映射模式。用于适配不同硬件/部署形态下 PyTorch 侧 device_id 与 KMS/算子侧 device_id 的映射关系。`A3` 表示按 Atlas 800I A3 超节点服务器 设备编号规则处理。（默认是A2） |
| `SECURE_PATCH_ENABLE` | `1` | 是否启用 secure_patch。`1` 表示启用，`0` 表示关闭。关闭后不安装 H2D/D2H/权重加载相关 patch。 |
| `SECURE_PATCH_DEBUG` | `0` | 是否开启调试日志。`1` 输出更详细日志，便于联调；`0` 关闭调试日志，适合性能测试或生产运行。 |

**逐行解读：**

- `SECURE_PATCH_DEVICE_ID_MODE`：解决"PyTorch 看到的 device_id"与"KMS/算子看到的 device_id"在超节点等拓扑下可能不一致的问题；示例为 `A3`（Atlas 800I A3 超节点），缺省为 `A2`，部署不同形态服务器时需正确设置，否则密钥/算子侧的 device 寻址会错位。
- `SECURE_PATCH_ENABLE`：总开关；关闭后**所有 H2D/D2H/权重加载的 patch 都不安装**，推理服务将以原生明文路径运行，相当于完全旁路本特性。
- `SECURE_PATCH_DEBUG`：仅控制日志详细程度，不影响数据通路；联调阶段建议开启，性能/生产阶段关闭以减少日志开销。

---

### 表 2：KMSAgent 通信配置

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_KMS_SOCKET` | `/run/kmsagent/socket/kmsagent.sock` | KMSAgent 的 UDS socket 路径。PyTorch 侧通过该路径向 KMSAgent 请求初始密钥和更新密钥。 |
| `SECURE_PATCH_KMS_TIMEOUT` | `10.0` | KMS 请求的总超时时间，单位为秒。用于限制一次密钥请求/更新请求的最大等待时间。 |
| `SECURE_PATCH_KMS_RETRY_MAX` | `3` | KMS 请求失败后的最大重试次数。这里表示最多重试 3 次。 |
| `SECURE_PATCH_KMS_RETRY_WAIT_MS` | `3000` | 每次重试前的等待时间，单位为毫秒。这里表示每次失败后等待 3 秒再重试。 |
| `SECURE_PATCH_KMS_RETRY_BACKOFF` | `1.0` | 重试退避系数。`1.0` 表示固定间隔重试；如果设置为大于 1 的值，则每次重试等待时间按比例增加。 |
| `SECURE_PATCH_KMS_CONNECT_TIMEOUT_MS` | `200` | 连接 KMSAgent UDS socket 的超时时间，单位为毫秒。 |
| `SECURE_PATCH_KMS_RECV_TIMEOUT_MS` | `500` | 等待 KMSAgent 响应数据的接收超时时间，单位为毫秒。 |

**逐行解读：**

- `KMS_SOCKET`：唯一指向 KMSAgent 的本地通道，必须保证容器内进程对该 socket 文件具备访问权限（与文档第一节"信任域"的约束呼应）。
- `KMS_TIMEOUT`：单次请求的"总闸门"，防止 KMS 异常时业务长等。
- `KMS_RETRY_MAX` + `KMS_RETRY_WAIT_MS` + `KMS_RETRY_BACKOFF`：构成完整的"重试三件套"——`3` 次 × `3000 ms` × 系数 `1.0`（固定间隔），调高 `BACKOFF` 可实现指数退避。
- `KMS_CONNECT_TIMEOUT_MS` vs `KMS_TIMEOUT`：前者仅约束 TCP/UDS 建连阶段（`200 ms`），后者约束整个请求生命周期（`10 s`），二者是分层关系。
- `KMS_RECV_TIMEOUT_MS`：单次接收等待 `500 ms`，与连接超时解耦，便于单独诊断"建连成功但无回包"的场景。

---

### 表 3：算法与 IV 配置

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_ALG_ID` | `1` | 加解密算法 ID。 `1` 表示 AES-CTR-128  `2` 表示 AES-GCM-128 |
| `SECURE_PATCH_IV_BYTES` | `16` | IV 长度，单位为字节。AES-CTR 场景通常使用 16 字节 IV。H2D 和 D2H 方向会分别维护 IV counter，避免 IV 复用。 |
| `SECURE_PATCH_HOST_CTR_MODULE` | `aes_ctr_crypt` | Host 侧 CTR 加密模块名。secure_patch 会从该模块加载 Host 侧加解密函数。 |
| `SECURE_PATCH_HOST_CTR_FUNCTION` | `aes_ctr_cryption` | Host 侧 CTR 加解密函数名。H2D 场景用于 Host 加密，D2H 场景用于 Host 解密。 |

**逐行解读：**

- `ALG_ID`：以枚举 ID 切换算法，`1=AES-CTR-128`、`2=AES-GCM-128`；选择 GCM 可额外获得认证标签，但开销更高。
- `IV_BYTES`：CTR 模式下 IV 等同于初始 counter；双方向各自维护 counter 是规避"同密钥 + 同 IV"致命复用的关键设计。
- `HOST_CTR_MODULE` / `HOST_CTR_FUNCTION`：通过模块名 + 函数名的形式动态导入加解密入口，便于在不同硬件/软件栈下替换实现（例如对接国产加密库）。

---

### 表 4：密钥轮换配置

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_ROTATE_BYTES` | `34359738368` | 按数据量触发密钥轮换的阈值，单位为字节。该值为 32GB，表示单方向累计处理数据量达到阈值后触发密钥更新逻辑。 |
| `SECURE_PATCH_ROTATE_OPS` | `100000000` | 按加解密次数触发密钥轮换的阈值。这里表示单方向累计加解密操作达到 1 亿次后触发密钥更新逻辑。 |
| `SECURE_PATCH_ROTATE_PREFETCH_RATIO` | `0.8` | 密钥预取比例。表示当使用量达到轮换阈值的 80% 时，提前异步请求下一组密钥，降低真正轮换时的同步等待开销。 |
| `SECURE_PATCH_ROTATE_ALLOW_STALE` | `1` | 是否允许在新密钥尚未准备好时继续使用当前旧密钥。`1` 表示允许短暂使用当前密钥，避免业务阻塞；`0` 表示轮换点必须等待新密钥就绪。 |

**逐行解读：**

- `ROTATE_BYTES`：数据量维度上限，`34359738368 B ≈ 32 GiB`，按业务流量大小可调。
- `ROTATE_OPS`：操作次数维度上限，`1×10^8` 次；二者满足其一即触发轮换。
- `ROTATE_PREFETCH_RATIO = 0.8`：在阈值 80% 处提前发起异步预取，使真正跨越阈值时新密钥大概率已就绪，配合 `KMS_ASYNC` 可显著降低轮换延迟。
- `ROTATE_ALLOW_STALE`：在安全与可用性之间的权衡开关；`1` 偏可用（容忍短暂旧密钥使用），`0` 偏严格（强制同步等待新密钥就绪）。

---

### 表 5：密钥缓存与 fallback 配置

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_MAX_KEYS_PER_DIRECTION` | `2` | 每个方向最多缓存的密钥数量。这里表示 H2D 和 D2H 每个方向各保留新旧两把密钥，用于密钥切换窗口内的兼容和回退。 |
| `SECURE_PATCH_KEY_FALLBACK_ENABLE` | `1` | 是否启用密钥 fallback。`1` 表示当最新密钥加解密失败时，可以尝试同方向缓存中的旧密钥。 |
| `SECURE_PATCH_KEY_FAILURE_DEMOTE_THRESHOLD` | `3` | 密钥失败降级阈值。某把密钥连续失败达到该次数后，可将其降级或从优先路径中移除，避免反复使用异常密钥。 |

**逐行解读：**

- `MAX_KEYS_PER_DIRECTION=2`：H2D 和 D2H 各自保留新旧两把密钥，正好覆盖"密钥切换窗口期"两端对端的兼容需求。
- `KEY_FALLBACK_ENABLE`：开启后，最新密钥出错可回退旧密钥，提高可用性；关闭则更严格（出错即上报）。
- `KEY_FAILURE_DEMOTE_THRESHOLD=3`：连续失败 3 次即降级，避免个别异常密钥反复污染主路径。

---

### 表 6：vLLM Patch 控制

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_PATCH_VLLM_COPY_TO_GPU` | `1` | 是否 patch vLLM 的  token H2D 数据拷贝路径。`1` 表示对 CPU 到 NPU 的 token数据路径执行 Host 加密、Device 解密。 |
| `SECURE_PATCH_PATCH_ASYNC_OUTPUT_D2H` | `1` | 是否 patch vLLM 的 D2H 输出路径。`1` 表示对 NPU 到 CPU 的token输出数据路径执行 Device 加密、Host 解密。 |
| `SECURE_PATCH_PATCH_WEIGHT_LOADER` | `0` | 是否 patch 权重加载路径。`0` 表示当前不对权重 H2D 加载路径加密；`1` 表示权重加载时也走 secure_patch 加解密流程。 |

**逐行解读：**

- `PATCH_VLLM_COPY_TO_GPU`：控制**推理请求的 token 输入**是否走 secure 通道，启用后由 Host 端加密、Device 端解密。
- `PATCH_ASYNC_OUTPUT_D2H`：控制**推理返回的 token 输出**是否走 secure 通道，方向相反，由 Device 端加密、Host 端解密。
- `PATCH_WEIGHT_LOADER`：控制**模型权重加载**是否加密；默认 `0`（权重通常被认为是非敏感、且一次性加载开销敏感），按需开启。

---

### 表 7：KMS 异步预取配置

| 环境变量 | 示例值 | 含义 |
|---|---|---|
| `SECURE_PATCH_KMS_ASYNC_ENABLE` | `1` | 是否启用 KMS 异步请求能力。`1` 表示密钥预取和部分更新请求可以异步执行，减少业务主路径阻塞。 |
| `SECURE_PATCH_KMS_ASYNC_QUEUE_SIZE` | `128` | KMS 异步请求队列大小。用于限制最多排队的异步密钥请求数量，避免异常情况下无限堆积。 |

**逐行解读：**

- `KMS_ASYNC_ENABLE`：与第 4 节的预取比例配合，把"等待新密钥"从同步路径挪到后台线程。
- `KMS_ASYNC_QUEUE_SIZE=128`：限制并发排队上限，防止 KMS 抖动或被攻击时无限制堆积请求导致内存膨胀。

---

## 【公式解读】

**原文无公式**（文档为使用指导性质，仅包含自然语言与配置表，不涉及数学公式、伪代码或 LaTeX 表达式）。

---

## 【关联】

根据原文出现的内部链接与上下文，本特性与以下模块/上下游存在关系：

1. **README.md**（文末内部链接）
   - 出现在第二节"二、secure_patch 环境部署说明"：部署阶段细节（如何构建镜像、如何挂载 `/run/kmsagent/socket`、HDK/vllm-ascend 版本兼容性矩阵等）由 [secure_h2d功能部署](README.md) 提供；本文档定位为**使用指导**，不重复部署细节。
   - 同时在第一节"约束"中被再次点名：HDK 与 vllm-ascend 的**特定版本适配列表**详见 README。

2. **KMSAgent**（文中反复出现，但不在仓库内）
   - 作为密钥提供方，通过 UDS socket（`/run/kmsagent/socket/kmsagent.sock`）对外服务；本文档的所有密钥相关配置（超时、重试、异步、预取）均围绕与 KMSAgent 的交互展开。
   - 安全信任域边界由 KMSAgent 的 socket 文件访问权限界定（见第一节约束 1）。

3. **vLLM-Ascend**（外部组件）
   - patch 注入对象：H2D 的 token 拷贝路径、D2H 的输出路径、权重加载路径均位于 vLLM-Ascend 中；本特性需配合其特定版本（详见 README）。

4. **Atlas 800I A3 超节点 / A2 硬件形态**
   - 通过 `SECURE_PATCH_DEVICE_ID_MODE` 区分设备编号规则，说明本特性需要感知底层 NPU 拓扑；不同硬件形态需要选择不同的 device_id 映射模式。

5. **下游 env 文件**（示例 `env_aes_ctr_a2.sh`）
   - 是上述环境变量的具体打包形式，使用者只需 `source` 即可，无需逐个设置。

---

## 【使用方法】

> 以下命令与配置均来自原文；为便于阅读合并呈现。

### 启用步骤（原文第三节）

```bash
# 1) 进入指定容器
# 2) 选择对应的配置进行 source（以下为示例，文件名以实际分发为准）
source env_aes_ctr_a2.sh

# 3) 用正常方式拉起推理服务即可
```

### 配置项汇总（原文第四节全部环境变量）

```bash
# ===== 1. 基础开关与运行模式 =====
export SECURE_PATCH_DEVICE_ID_MODE=A3          # 默认 A2；A3 = Atlas 800I A3 超节点编号规则
export SECURE_PATCH_ENABLE=1                    # 1=启用, 0=关闭（关闭后不安装 H2D/D2H/权重 patch）
export SECURE_PATCH_DEBUG=0                     # 1=详细调试日志, 0=关闭（适合性能/生产）

# ===== 2. KMSAgent 通信配置 =====
export SECURE_PATCH_KMS_SOCKET=/run/kmsagent/socket/kmsagent.sock
export SECURE_PATCH_KMS_TIMEOUT=10.0
export SECURE_PATCH_KMS_RETRY_MAX=3
export SECURE_PATCH_KMS_RETRY_WAIT_MS=3000
export SECURE_PATCH_KMS_RETRY_BACKOFF=1.0
export SECURE_PATCH_KMS_CONNECT_TIMEOUT_MS=200
export SECURE_PATCH_KMS_RECV_TIMEOUT_MS=500

# ===== 3. 算法与 IV 配置 =====
export SECURE_PATCH_ALG_ID=1                    # 1=AES-CTR-128, 2=AES-GCM-128
export SECURE_PATCH_IV_BYTES=16
export SECURE_PATCH_HOST_CTR_MODULE=aes_ctr_crypt
export SECURE_PATCH_HOST_CTR_FUNCTION=aes_ctr_cryption

# ===== 4. 密钥轮换配置 =====
export SECURE_PATCH_ROTATE_BYTES=34359738368    # 32 GiB
export SECURE_PATCH_ROTATE_OPS=100000000        # 1 亿次
export SECURE_PATCH_ROTATE_PREFETCH_RATIO=0.8
export SECURE_PATCH_ROTATE_ALLOW_STALE=1

# ===== 5. 密钥缓存与 fallback 配置 =====
export SECURE_PATCH_MAX_KEYS_PER_DIRECTION=2
export SECURE_PATCH_KEY_FALLBACK_ENABLE=1
export SECURE_PATCH_KEY_FAILURE_DEMOTE_THRESHOLD=3

# ===== 6. vLLM Patch 控制 =====
export SECURE_PATCH_PATCH_VLLM_COPY_TO_GPU=1    # token H2D：Host 加密 / Device 解密
export SECURE_PATCH_PATCH_ASYNC_OUTPUT_D2H=1    # token D2H：Device 加密 / Host 解密
export SECURE_PATCH_PATCH_WEIGHT_LOADER=0       # 权重加载：0=不加密, 1=走 secure_patch

# ===== 7. KMS 异步预取配置 =====
export SECURE_PATCH_KMS_ASYNC_ENABLE=1
export SECURE_PATCH_KMS_ASYNC_QUEUE_SIZE=128
```

### 使用前必须满足的约束（原文第一节）

- 仅支持 **docker 模式**拉起的推理服务；
- **不支持模型并行**（一张卡不能被多个模型同时使用）；
- 必须使用与之适配的 **HDK** 与 **vllm-ascend** 特定版本（详见 README.md）；
- 主机内的进程通过 socket 文件访问控制构成信任域；跨主机/跨信任域保护不在本特性覆盖范围。
