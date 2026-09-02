# Hetero Parallel

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/hetero_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/hetero_parallel.md

# Hetero Parallel 文档深度解读

## 【定位】

这篇文档面向多模态大模型（MLLM / Omni）在 Megatron 框架下训练时，因**模型异构**（不同子模块计算/显存规模差异）与**数据异构**（不同模态 token 数量差异且动态变化）导致的存算失衡问题，提出 **hetero-parallel（异构并行）** 方案，通过解耦各子模块的并行配置来消除 LLM bound / encoder bound 等计算空泡。

---

## 【技术要点】

1. **问题根源**：将 MLLM 视为单一整体并对 Encoder / LLM / Generator 施加相同的 DP/TP/PP 策略，会引发两类失衡——模型层面的 `LLM bound` / `encoder bound`，以及数据层面的 `Intra-microbatch` / `inter-microbatch` 不均衡。

2. **方案核心**：解耦子模块的并行配置，使每个模块可独立设置 DP/TP/PP/CP/mbs；与 `dist-train` 不同，采用**编码器与骨干网络混合部署**，避免独立部署导致的资源浪费。

3. **实现四件套**：
   - 在线 `parallel_state` 转换器：保存各子模块的 snapshot，运行时动态切换 mpu 状态；
   - 数据分发 util：负责 encoder → LLM 的数据流正确性与通信掩盖；
   - 模型 hook：在 forward / backward 前后挂载，实现数据流转换与 mpu 切换；
   - 异构 pp：`forward_backward_func_list` 调度。

4. **场景一·异构 DP/TP/CP**（典型：QwenVL 系列）：encoder 规模小、静态显存小，LLM 规模大；encoder 开 DP/CP，LLM 开 DP/TP/CP。原文给出 **Qwen2.5Omni 7B 短序列**的具体配比：**ViT、Audio = DP8，LLM = TP4DP2** 可获最佳性能。

5. **场景二·异构 PP**：适用于小 mbs 大 gas 且 LLM 参数量大的场景；ViT / Audio encoder 用大 DP，LLM 开 PP，且 encoder 与 LLM 可使用不同 mbs，推荐 **encoder mbs ≈ 4–8 × LLM mbs**。

6. **关键差异**：骨干网络不再支持通过 shell 脚本 initial 并行策略；shell 端 TP/PP/CP 全部置 1，子模块并行度全部在 `model.json` 中配置。

---

## 【关键机制与数据】

- **数据流路径**：原文中描述为 `encoder → LLM` 的数据分发 util 负责数据流正确，并实现通信掩盖。
- **状态切换机制**：运行时通过 snapshot + hook 在 fw/bw 前后动态切换 `mpu` 状态，使同一进程组在不同时刻呈现不同的并行拓扑。
- **调度机制**：通过异构 pp 的 `forward_backward_func_list` 调度不同子模块的前向/反向计算。
- **性能配比（原文）**：
  - Qwen2.5Omni 7B 短序列：**ViT、Audio: DP8，LLM: TP4DP2** 获最佳性能。
  - 异构 PP 场景 encoder 与 LLM 的 mbs 比例：**encoder mbs ≈ 4–8 × LLM mbs**。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档明确指出，针对**模型异构与数据异构**两大类问题，MindSpeed MM 设计了两套互补方案：

- **hetero-parallel**（本文档主题）——解决**模型异构**导致的存算失衡；
- **[在线数据重排方案](./online_data_rearrange.md)**——解决**数据异构**（动态分辨率、不同模态 token 数差异）导致的负载不均衡。

二者构成 "模型异构 + 数据异构" 的完整应对链路：hetero-parallel 在并行拓扑层面解耦子模块，在线数据重排在样本/token 层面动态调度，二者通常联合使用以同时缓解计算空泡与负载不均。

---

## 【使用方法】

**1. 训练启动脚本参数**（原文）：
```shell
GPT_ARGS="
    ...
    --hetero-parallel \
    --hetero-encoder-mbs-scale {num} \   # 将图像/音频编码器的mbs调整为文本解码器的num倍
"
```

**2. `model.json` 子模块并行配置**（原文：骨干网络并行策略需在 json 中设置，shell 端统一置 1）：
```json
{
   ...
    "image_encoder": {
        "vision_encoder": {
            ...
            "tp": 1,
            "pp": 1,
            "cp": 1
       },
    },
   "audio_encoder": {
        ...
        "tp": 1,
        "pp": 1,
        "cp": 1
    },
    "text_decoder": {
        ...
        "tp": 1,
        "pp": 1,
        "cp": 1
    }
   ...
}
```

```shell
TP=1
PP=1
CP=1
```

**3. 适用范围（原文）**：当前仅支持 **Megatron 后端** + `pretrain_vlm` 训练任务；**FSDP2 后端不支持**。
