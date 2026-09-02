# Printf&Dump_Tensor

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/print.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/print.md

# 「Printf&Dump_Tensor」深度解读

## 【定位】
本文档描述 TileLang-ascend 在 Ascend NPU 上提供的两类**设备侧调试接口**：`T.printf`（格式化字符串输出）与 `T.dump_tensor`（张量内容转储），用于在 kernel 运行期观测变量、地址、各层级 buffer（UB / L1 / L0C / Global）的内容。

---

## 【技术要点】

1. **环境开关 `TL_PTO_DEBUG`**：必须在 **kernel 编译之前** 设置为 `"1"`，否则 printf/dump 基础设施会在编译期被优化掉；开启后会自动追加 `-D_DEBUG` 与 `--cce-enable-print` 两条编译选项。
2. **设备/宿主分离**：`T.printf`、`T.dump_tensor` 是 **device-side** 工具；host 侧调试应直接使用 Python 的 `print`。
3. **`T.printf` 接口**：`printf(format_str: str, *args)`，通过 `%` 格式说明符控制转换类型，支持：
   - `%d` / `%i`：十进制整数
   - `%f`：浮点数
   - `%x`：十六进制整数（可用于输出地址信息）
   - `%s`：字符串
   - `%p`：指针地址（文档建议**优先用 `%x` 直接输出地址**）
4. **`T.dump_tensor` 接口**：`dump_tensor(tensor: Buffer, desc: int, dump_size: int, shape_info: tuple=())`，支持 `ub_buffer / l1_buffer / l0c_buffer / global_buffer`，无需区分 buffer 类型，直接传 tensor 名即可。
5. **buffer 上限**：每个 tile 的 printf/dump 缓冲区上限为 **1 MB**；同时该功能仅供调试，开启后会降低 kernel 性能。
6. **自动打印信息头**：`dump_tensor` 输出首部自动包含 CANN 版本号、时间戳、kernel 类型、算子信息、内存信息、数据类型、位置信息等。

---

## 【关键机制与数据】

- **工作原理**（原文）：
  > "This appends the compiler flags `-D_DEBUG` and `--cce-enable-print`, which activate the device-side printf infrastructure that is otherwise compiled out for performance reasons."
  
  即：环境变量仅作为**编译期**开关，通过注入宏与编译选项来激活原本被优化的设备侧 printf 基础设施；运行时打印本身仍发生在 device 上。

- **`shape_info` 与 `dump_size` 的关系**（原文）：
  - 当 `shape` 元素数 **大于** `dump_size` 时，按 `shape_info` 打印，**缺失的 dump 数据用 `-` 占位**。
  - 当 `shape` 元素数 **小于等于** `dump_size` 时，按 `shape_info` 打印，**超出 shape 维度范围的 dump 数据不显示**。

- **示例输出数据**（原文）：
  > `opType=AddCustom, DumpHead: AIV-0, CoreType=AIV, block dim=8, total_block_num=8, block_remain_len=1046912, block_initial_space=1048576, rsv=0, magic=5aa5bccd`
  
  其中 `block_initial_space=1048576` 即 **1 MB** 缓冲区，与正文警示一致。

  > `DumpTensor: desc=111, addr=0, data_type=float16, position=UB, dump_size=32`

- **性能约束**（原文）："Leaving it enabled degrades kernel performance and each tile's printf/dump buffer is capped at 1 MB."

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- 文档末尾提示 "See the *TileLang-Ascend Programming Guide* for full details."——即 `T.printf` 与 `T.dump_tensor` 的更深入用法、限制与示例应参考 **TileLang-Ascend Programming Guide** 这一上游/平级文档。
- 与**编译流程**的关系：`TL_PTO_DEBUG` 在 kernel **编译前**生效，通过注入 `-D_DEBUG` 与 `--cce-enable-print` 影响最终产物，因此它属于编译期开关而非运行期开关。
- 与**多层 buffer 模型**的耦合：`dump_tensor` 直接覆盖 `ub_buffer / l1_buffer / l0c_buffer / global_buffer` 四级存储，是 Ascend 硬件层级化内存结构的调试观测点。

---

## 【使用方法】

### 启用方式（编译前）
```python
import os
os.environ["TL_PTO_DEBUG"] = "1"
```
随后再进行 kernel 编译；该变量开启后会自动追加 `-D_DEBUG` 与 `--cce-enable-print`。

### `T.printf` 调用
```python
T.printf("fmt %s %d\n", "string", 0x123)
```

### `T.dump_tensor` 调用
```python
# 不带 shape_info：依次 dump 四类 buffer
T.printf("A_L1:\n")
T.dump_tensor(A_L1, 111, 64)   # l1_buffer

T.printf("B_L1:\n")
T.dump_tensor(B_L1, 222, 64)   # l1_buffer

T.printf("C_L0C:\n")
T.dump_tensor(C_L0C, 333, 64)  # l0c_buffer

T.printf("a_ub:\n")
T.dump_tensor(a_ub, 444, 64)   # ub_buffer

T.printf("A_GLOBAL:\n")
T.dump_tensor(a_global, 555, 64) # global_buffer

# 带 shape_info：用于更清晰的格式化输出
T.dump_tensor(A_L1,    111, 64, (8, 8))
T.dump_tensor(B_L1,    222, 64, (8, 9))
T.dump_tensor(C_L0C,   333, 64, (8, 7))
T.dump_tensor(a_ub,    444, 64, (8, 8))
T.dump_tensor(a_global,555, 64, (8, 8))
```

### 注意事项（原文警示）
- `TL_PTO_DEBUG` **仅用于调试**，保持开启会降低 kernel 性能。
- 每个 tile 的 printf/dump buffer 上限为 **1 MB**。
- `desc` 参数仅支持 `uint32_t` 类型，常用于打印当前行号等自定义信息。
