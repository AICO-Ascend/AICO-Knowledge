# Tilelang-Ascend Vid Reduction & Auto CV Ratio Feature

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/vid_reduction_and_auto_cv_ratio.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/vid_reduction_and_auto_cv_ratio.md

## 【定位】
这篇文档描述 Tilelang-Ascend 如何通过自动 Cube–Vector（CV）匹配隐藏前端表示中的 `vid`：用户仅用 `threads` 选择启用一个或两个 V-core，编译 pass 自动完成 UB 分块及 GM 偏移，从而屏蔽昇腾架构细节并简化编程。

## 【技术要点】

1. **设计目标**  
   昇腾架构可能采用 `C:V=1:1` 或 `C:V=1:2` 的 Cube/Vector 比例。传统前端需要显式使用 `vid` 划分向量侧数据；本功能的目标是自动完成 CV 匹配，使前端返回结果不再包含 `vid`。

2. **启用参数与支持值**  
   原文中使用参数形式：
   ```python
   threads=VECNUM
   ```
   并说明 `VEC_NUM` 只能取 `1` 或 `2`：
   - `1`：启用一个 V-core，对应 `C:V=1:1`。
   - `2`：启用两个 V-core，对应 `C:V=1:2`。

   原文实际示例为：
   ```python
   with T.Kernel(m_num * n_num, threads=2, is_npu=True) as (cid):
   ```
   设置后，前端只返回 `(cid)`，不返回 `(cid, vid)`。

3. **任务与数据块映射**  
   任务总数由 `m_num * n_num` 决定。Cube 任务 ID `cid` 被映射为二维块坐标：
   ```python
   bx = cid // n_num
   by = cid % n_num
   ```
   其中 `cid // n_num` 取得 M 方向块编号，`cid % n_num` 取得 N 方向块编号。

4. **UB 分配与 GM 偏移由编译 pass 自动处理**  
   在 `threads=2` 时，用户侧仍按完整尺寸分配：
   ```python
   d_ub = T.alloc_shared((block_M, block_N), dtype)
   c_ub = T.alloc_shared((block_M, block_N), dtype)
   ```
   不需要把 `block_M` 提前除以 `2`，编译 pass 会完成划分。GM↔UB 复制时也不需要手动加入向量侧偏移：
   ```python
   T.copy(workspace[bx * block_M, by * block_N], c_ub)
   T.copy(D[bx * block_M, by * block_N], d_ub)
   T.copy(c_ub, C[bx * block_M, by * block_N])
   ```

5. **计算流程**  
   示例将 A、B 分块复制到 `A_L1`、`B_L1`，通过 `T.gemm_v0` 累积到 `C_L0`；随后经过 `workspace` 和 UB 中间缓冲完成加法：
   ```python
   T.tile.add(c_ub, c_ub, d_ub)
   ```
   最后将结果写回 C。K 方向分块数由：
   ```python
   loop_k = T.ceildiv(K, block_K)
   ```
   决定，首次迭代通过 `init=True` 初始化 `C_L0`。

6. **适用边界**  
   自动处理基于静态维度规则，当前只处理 UB 分配及 GM↔完整 `ub_buffer` 的数据传输，并涉及数据分块；支持 GM 切片和多维参数，但 UB 必须是完整 buffer。若被消除的 UB 第 `0` 维使用了循环变量，该循环变量会被拆分。由索引确定完整 UB 的 SFA 算子等特殊场景不需要拆分。原文没有说明任意动态维度、任意循环形式或不完整 UB 均可使用。

## 【关键机制与数据】

### 原文工作机制

核心流程是：用户通过 `threads=1` 或 `threads=2` 指定向量核数量，前端仍只暴露 Cube ID `cid`；编译阶段根据该选择执行 CV 匹配，并在需要时把完整 UB 划分给向量核，同时调整 GM 传输参数的首地址偏移。这样，硬件侧的向量核划分和 `vid` 不再进入用户程序。

自动化的重点是 **UB 分配分块** 和 **GM/UB 传输偏移**，而不是让用户在源码中显式编写 `vid` 切分逻辑。原文特别指出，`d_ub`、`c_ub` 仍分配为 `(block_M, block_N)`，相关划分由 compilation pass 完成。

### 原文数据流

按示例调用顺序，数据流为：

1. `A` 的 M/K 分块和 `B` 的 K/N 分块分别通过 `T.copy` 写入 `A_L1`、`B_L1`。
2. `T.gemm_v0` 在 K 方向循环中计算，结果累积到 `C_L0`。
3. `C_L0` 被复制到 `workspace`，随后从 `workspace` 复制到 `c_ub`。
4. D 的对应 M/N 分块被复制到 `d_ub`。
5. `T.tile.add(c_ub, c_ub, d_ub)` 完成逐元素加法。
6. `c_ub` 被复制回输出 C。

其中 GM↔UB 的相关步骤是自动分块和偏移处理的直接对象；`C_L0` 等 fragment 分配不在原文所述的 UB 自动处理范围内。

### 性能数据

原文未提供吞吐量、时延、加速比、占用率或其他性能数据，因此不能据本文推断启用 `threads=2` 必然带来性能提升。

## 【表格解读】

原文无表格

## 【公式解读】

原文没有独立公式推导，但给出了比例关系和编译侧偏移表达式，均按原文保留。

- `C:V=1:1`  
  表示 Cube 与 Vector 的比例为 `1:1`，对应 `threads=1`。其中 `C` 表示比例中的 Cube 侧，`V` 表示 Vector 侧，`:` 表示二者比值，`=`
