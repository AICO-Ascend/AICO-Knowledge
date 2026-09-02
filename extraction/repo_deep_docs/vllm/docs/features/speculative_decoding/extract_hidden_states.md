# Hidden State Extraction

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/extract_hidden_states.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/extract_hidden_states.md

# Hidden State Extraction 文档深度解读

## 【定位】

这篇文档描述 vLLM 提供的一项"隐藏状态提取"(Hidden State Extraction) 能力——在推理过程中从目标模型(target model) 的指定中间层抓取并落盘 activations,用于训练 EAGLE 风格的 draft model、知识蒸馏、或对模型内部表征做离线分析。

---

## 【技术要点】

1. **入口伪装为 speculative decoding**: 通过 `speculative_config.method = "extract_hidden_states"` 与 `num_speculative_tokens = 1` 把"提取"挂进 vLLM 的投机解码框架(原文: `num_speculative_tokens: 1`)。
2. **层选择机制**: 用 `draft_model_config.hf_config.eagle_aux_hidden_state_layer_ids` 指定要抽取的层编号列表,原文示例为 `[1, 2, 3, 4]`。
3. **末层输出的特殊取法**: 原文 note 指出,把 `num_hidden_layers` 当作 layer id 传入即可保存最后一层输出,且明确这些 hidden states **不会**经过 output norm 归一化。
4. **传输机制**: 借助 KV Transfer 基础设施——`kv_connector = "ExampleHiddenStatesConnector"`、`kv_role = "kv_producer"`、`shared_storage_path` 作为落盘目录,文件后缀 `.safetensors`。
5. **在线模式优化**: 原文建议在线使用 `/dev/shm/` 这类 RAM-mounted 文件系统,因为客户端会"soon after they are generated"清理。
6. **每请求可调项**: 通过 `kv_transfer_params` 控制 `hidden_states_path`(自定义路径,需服务端允许)和 `include_output_tokens`(是否同时保存 prompt + 生成 token 的 hidden states)。
7. **兼容性约束**: 原文明确"Chunked prefill is not compatible with this feature and must be disabled"。
8. **服务侧安全/性能旋钮**: `allow_custom_save_path`(默认 False,仅受信客户端开启)、`num_writer_threads`(默认 8 异步写盘线程)、`use_synchronization_lock`(默认 True,文件锁让并发读者阻塞到写完)。

---

## 【关键机制与数据】

**工作原理 / 数据流**(以原文描述为准):

- 输入: 用户调用 `LLM.generate()`(offline) 或通过 `vllm serve`(online)启动一个 Qwen3-8B 这类目标模型。
- 配置生效层: 在 `LLM(...)` 构造期传入 `speculative_config` 选定 `extract_hidden_states` 方法与 `eagle_aux_hidden_state_layer_ids = [1, 2, 3, 4]`,让 vLLM 在前向过程中把第 1/2/3/4 层的 activations 截留出来。
- 落盘层: 通过 `KVTransferConfig` 把这些 activations 通过 `ExampleHiddenStatesConnector` 以 `kv_producer` 身份写入 `shared_storage_path`。
- 路径返回: `output.kv_transfer_params["hidden_states_path"]` 把每条请求对应文件路径回传给客户端;客户端调用 `example_hidden_states_connector.load_hidden_states(path)` 读回,内部利用文件锁做同步。
- 文件内容: 每个 `.safetensors` 含两块张量——`hidden_states [num_tokens, num_extracted_layers, hidden_size]` 与 `token_ids [num_tokens]`。

**原文出现的关键数字 / 阈值**(逐项标注,均为原文):

- 默认线程池: `num_writer_threads = 8`(原文 Configuration 表)。
- 默认文件锁: `use_synchronization_lock = True`(原文 Configuration 表)。
- 默认保存目录: `shared_storage_path = /tmp`(原文 Configuration 表)。
- 默认路径模板: `<shared_storage_path>/<request_id>.safetensors`(原文 Per-Request Options 表描述)。
- `num_speculative_tokens = 1`(原文 Offline / Online 示例)。
- 示例层列表: `[1, 2, 3, 4]`(原文 Offline / Online 示例)。
- 模型: `Qwen/Qwen3-8B`(原文示例)。
- 推荐 RAM 挂载点: `/dev/shm/`(原文 Online Example)。

**性能 / 安全相关原文陈述**:

- "For improved performance, it is recommended to use a RAM-mounted file system such as `/dev/shm/` for online usage"(原文 Online Example)。
- "Enable only with trusted clients — custom paths can write to arbitrary locations on the server."(原文 Configuration 表 `allow_custom_save_path` 描述)。

---

## 【表格解读】

### 表 1:Per-Request Options(原文逐字还原)

| Parameter | Default | Description |
| --- | --- | --- |
| `hidden_states_path` | Auto-generated | Custom file path for saving hidden states. If not set, files are saved to `<shared_storage_path>/<request_id>.safetensors`. Requires `allow_custom_save_path` to be enabled in the server config. |
| `include_output_tokens` | `False` | When `True`, save hidden states for both prompt and generated output tokens. When `False`, only prompt token hidden states are saved. |

**逐行解读**:

- **`hidden_states_path`**:默认自动生成,实际路径模板是 `<shared_storage_path>/<request_id>.safetensors`(由服务端 `shared_storage_path` 配置决定)。若用户想覆盖成自定义路径(如 `/tmp/my_output.safetensors`),前提是服务端把 `allow_custom_save_path` 打开——这是一种"客户端可控写路径"的安全开关。
- **`include_output_tokens`**:默认 `False`,此时只保存 prompt 部分的 token hidden states;设为 `True` 后,生成阶段新产生的 token 也会写入。该参数决定了 `.safetensors` 中 `hidden_states` 第一维 `num_tokens` 是否包含生成段。

### 表 2:Server-level Configuration(原文逐字还原)

| Parameter | Default | Description |
| --- | --- | --- |
| `shared_storage_path` | `/tmp` | Directory where hidden state files are saved (used when `hidden_states_path` is not set per-request) |
| `allow_custom_save_path` | `False` | Allow API clients to specify custom file paths via `hidden_states_path`. When disabled, client-provided paths are ignored with a warning. Enable only with trusted clients — custom paths can write to arbitrary locations on the server. |
| `num_writer_threads` | `8` | Thread pool size for async disk writes |
| `use_synchronization_lock` | `True` | Use file locks so concurrent readers block until writes complete. Can be disabled for batch generation where synchronization is not needed. |

**逐行解读**:

- **`shared_storage_path`**:作为"未指定 `hidden_states_path` 时"的兜底落盘根目录,默认 `/tmp`;在线场景下官方建议换成 `/dev/shm/` 之类 RAM-backed 路径。
- **`allow_custom_save_path`**:安全门控。默认关闭,关闭时即使请求里带了 `hidden_states_path`,服务端也只是 "ignored with a warning",防止 API 客户端把任意路径写入服务端。
- **`num_writer_threads`**:异步落盘的线程池容量,默认 8;决定了多个请求并行写 `.safetensors` 的并发上限。
- **`use_synchronization_lock`**:默认启用文件锁,目的是让"读端" `load_hidden_states()` 在写端尚未完成时阻塞等待;在批量生成(没有并发读者)时可关掉以节省开销。

---

## 【公式解读】

**原文无公式**。

文档仅以自然语言+张量 shape 描述输出格式:`hidden_states` 形状 `[num_tokens, num_extracted_layers, hidden_size]`,`token_ids` 形状 `[num_tokens]`。这些是 shape 描述,不是公式。

---

## 【关联】

- **与 EAGLE draft model 的关系**(原文: `eagle.md`):Hidden State Extraction 的核心动机之一是为训练 EAGLE 风格 draft model 提供中间层 activations。配置项 `eagle_aux_hidden_state_layer_ids` 这一命名本身就沿用 EAGLE 的训练约定;末层特例"passing `num_hidden_layers` as a layer id"也与 EAGLE 的训练输入格式呼应。
- **与 KV Transfer 基础设施的关系**(原文: `vllm.distributed.kv_transfer.kv_connector.v1.example_hidden_states_connector`):虽然名字带 "kv_transfer",但这里被复用作为"任意 tensor 的 producer/consumer 通道"——`ExampleHiddenStatesConnector` 充当 producer,`load_hidden_states(path)` 充当 reader;路径由 `kv_transfer_params` 回传,而不是放在传统 `request_output` 字段里。
- **与 speculative decoding 框架的关系**:该特性借道 `speculative_config` 触发(`method = "extract_hidden_states"`),但 `num_speculative_tokens = 1` 表明并不真正做投机解码,只是复用前向钩子。
- **示例代码入口**(原文链接):完整离线示例见 `examples/features/speculative_decoding/extract_hidden_states_offline.py`。
- **不兼容性**:文档末尾明确 chunked prefill 必须关闭,提示该能力依赖逐请求完整前向、显式截留 activations 的实现假设。

---

## 【使用方法】

**Offline**(原文逐字还原):

```python
import tempfile

from vllm import LLM, SamplingParams
from vllm.config.kv_transfer import KVTransferConfig
from vllm.distributed.kv_transfer.kv_connector.v1 import (
    example_hidden_states_connector,
)

with tempfile.TemporaryDirectory() as tmpdir:
    llm = LLM(
        model="Qwen/Qwen3-8B",
        speculative_config={
            "method": "extract_hidden_states",
            "num_speculative_tokens": 1,
            "draft_model_config": {
                "hf_config": {
                    "eagle_aux_hidden_state_layer_ids": [1, 2, 3, 4],
                },
            },
        },
        kv_transfer_config=KVTransferConfig(
            kv_connector="ExampleHiddenStatesConnector",
            kv_role="kv_producer",
            kv_connector_extra_config={
                "shared_storage_path": tmpdir,
            },
        ),
    )

    outputs = llm.generate(
        ["The future of AI is"],
        SamplingParams(max_tokens=1),
    )

    for output in outputs:
        path = output.kv_transfer_params["hidden_states_path"]
        obj = example_hidden_states_connector.load_hidden_states(path)
        print(f"token_ids: {obj['token_ids'].shape}")
        print(f"hidden_states: {obj['hidden_states'].shape}")
```

**Online**(原文逐字还原):

```bash
vllm serve Qwen/Qwen3-8B \
    --speculative_config '{"method": "extract_hidden_states", "num_speculative_tokens": 1, "draft_model_config": {"hf_config": {"eagle_aux_hidden_state_layer_ids": [1, 2, 3, 4]}}}' \
    --kv_transfer_config '{"kv_connector": "ExampleHiddenStatesConnector", "kv_role": "kv_producer", "kv_connector_extra_config": {"shared_storage_path": "/dev/shm/hidden_states"}}'
```

**Offline 每请求参数**(原文逐字还原):

```python
SamplingParams(
    max_tokens=32,
    extra_args={
        "kv_transfer_params": {
            "hidden_states_path": "/tmp/my_output.safetensors",
            "include_output_tokens": True,
        }
    },
)
```

**Online 每请求参数**(原文逐字还原):

```json
{
    "model": "Qwen/Qwen3-8B",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 32,
    "kv_transfer_params": {
        "hidden_states_path": "/tmp/my_output.safetensors",
        "include_output_tokens": true
    }
}
```

**启动 / 启用要点汇总**(均为原文出现):

- 设置 `speculative_config.method = "extract_hidden_states"`。
- 设置 `draft_model_config.hf_config.eagle_aux_hidden_state_layer_ids = [...]`,或用 `num_hidden_layers` 作为 id 取末层。
- 设置 `kv_transfer_config.kv_connector = "ExampleHiddenStatesConnector"`、`kv_role = "kv_producer"`。
- 在 `kv_connector_extra_config` 至少给出 `shared_storage_path`(在线推荐 `/dev/shm/` 之类 RAM-mounted 路径)。
- 可选地打开 `allow_custom_save_path` 以允许每请求覆盖路径。
- 必须关闭 chunked prefill(原文 note 强制要求)。
