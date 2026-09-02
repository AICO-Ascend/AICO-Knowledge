# 智能防抖函数（SmartDebounce）

> 仓 `msinsight` · 路径 `docs/zh/development_guide/design/SmartDebounce.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msinsight/docs/zh/development_guide/design/SmartDebounce.md

# 智能防抖函数（SmartDebounce）文档深度解读

---

## 【定位】

本文档描述前端公共库 `modules/lib` 中智能防抖函数（`createSmartDebounceRequestFunc`）的设计与使用，用于对**高频异步请求**进行防抖控制，提供 trailing / leading 两种模式与三种封装形态以适配不同调用场景。

---

## 【技术要点】

1. **两种防抖模式**：`trailing`（默认，`leading: false`）延迟结束后用最终参数发请求；`leading`（`leading: true`）首次调用立即执行、delay 窗口内共享同一结果。
2. **统一延迟默认值**：所有示例与签名中 `delay` 默认均为 **300ms**。
3. **三种封装层级**：
   - `createSmartDebounceRequestFunc`：底层工具函数，最灵活；
   - `useSmartDebounceRequest`：React Hook 封装，基于 `useRef` 稳定实例并自动 `cancel()`；
   - `createDebounceRequest`：请求层封装，基于 `createRequest` + `createSmartDebounceRequestFunc`，内置 `keyFn`（按 `command:params` 隔离）。
4. **生命周期回调**：`onBeforeRequest(...args)`、`onAfterRequest(result, ...args)`，分别在请求前/请求后触发。
5. **控制方法集**：返回实例支持 `cancel(key?)` / `flush(key?)` / `getPendingCount()` / `getPendingKeys()` 四个控制接口。
6. **竞态安全保证**：原文明确声明"内部所有异步回调都检查 state 是否仍然有效，不会出现旧 timer/请求误操作新状态的问题"。

---

## 【关键机制与数据】

### trailing 模式状态流转（原文）

```
idle ──调用──► pending ──timer到期──► inflight ──请求完成──► idle
                │                      │
                │ delay内再次调用        │ delay内再次调用
                │ 替换参数，重置timer    │ 新state重新进入pending
                ▼                      ▼
```

- **典型场景**：搜索框输入 `"k" → "ke" → "key" → "keyword"`，原文表述："只有 'keyword' 会真正发出请求"。
- **行为要点**：等待期间持续替换参数；timer 每次重置；请求完成后回到 idle。

### leading 模式状态流转（原文）

```
idle ──调用──► inflight（立即执行请求）
                 │
                 │ delay内再次调用 → 加入队列，不触发新请求
                 │
                 ├──请求在delay内完成──► delay到期 → 统一resolve队列 → idle
                 │
                 └──请求耗时>delay──► past_delay → 请求完成 → 立即resolve队列 → idle
```

- **典型场景**：原文："用户快速点击 3 次 → 第 1 次立即发请求，后 2 次共享结果"。
- **关键分叉**：
  - 请求在 delay 内完成 → 等待 delay 到期再统一 resolve 队列；
  - 请求耗时超过 delay → 进入 `past_delay` 状态，请求完成立即 resolve 队列。

### 关键参数（原文）

| 参数 | 默认 / 说明 |
|---|---|
| `delay` | 默认 **300ms** |
| `leading` | 默认 **`false`** |
| `keyFn` | 按 key 隔离不同请求 |
| `onBeforeRequest` / `onAfterRequest` | 生命周期回调 |

### 性能 / 内存相关（原文）

- 原文未提供基准测试数据或性能数字；
- 关于内存：原文第 1 条注意事项指出"若调用方创建了大量不同 key 的请求但从未 `await` 或调用 `cancel()`/`flush()`，内部状态会持续占用内存"，建议"定期调用 `getPendingCount()` 监控"。

---

## 【表格解读】

### 表 1：两种防抖模式（原文 §1，逐字还原）

| 模式 | `leading` 值 | 行为 | 最适合场景 |
| --- | --- | --- | --- |
| trailing（默认） | `false` | 等待期间持续替换参数，延迟结束后用**最终参数**发请求 | 搜索框输入、筛选条件变更等只关心最终状态的场景 |
| leading | `true` | 第一次调用**立即执行**请求，delay 窗口内所有调用方共享同一结果 | 按钮/交互响应等首次触发就要立即反馈的场景 |

**逐行解读**：

- **trailing（默认）行**：`leading` 取值为布尔 `false`，行为关键在于"持续替换参数 + 用最终参数发请求"，适用对象是"只关心最终状态"的场景——即中间过程的参数无需触发网络请求，典型如搜索框边输入边联想。
- **leading 行**：`leading` 取值为布尔 `true`，行为核心是"首次立即 + 窗口内共享"，适用对象是"首次触发就要立即反馈"的交互型场景——按钮类动作对响应延迟敏感，但又需要避免 3 连击触发 3 次请求的资源浪费。

---

### 表 2：控制方法（原文 §3.3，逐字还原）

| 方法 | 说明 |
| --- | --- |
| `.cancel(key?)` | 取消指定 key 或所有等待中的请求 |
| `.flush(key?)` | 立即发送指定 key 或所有等待中的请求（跳过延迟） |
| `.getPendingCount()` | 获取当前等待中的请求数量 |
| `.getPendingKeys()` | 获取所有等待中的请求 key 列表 |

**逐行解读**：

- **`.cancel(key?)` 行**：`key` 参数为可选，不传则作用于全部 pending 请求；用于终止尚未发出的请求。
- **`.flush(key?)` 行**：同样支持按 key 粒度或全局；与 `cancel` 相反——"跳过延迟"意味着把等待中的请求立刻发出去，而不是丢弃。
- **`.getPendingCount()` 行**：无参数，返回 `number`，对应原文注意事项 1 中提到的内存监控手段。
- **`.getPendingKeys()` 行**：无参数，返回 `string[]`，与 `keyFn` 返回的 key 对应，用于诊断具体哪些请求仍在等待。

---

## 【公式解读】

原文无公式。

> 备注：原文中出现的两段"状态流转"为文本框图（ASCII 流程图），并非数学公式或伪代码算法，已在【关键机制与数据】节中完整保留并解读。

---

## 【关联】

> 备注：原文未提供内部链接（`(无)`），以下关联均基于文档正文的交叉提及。

- **源码位置**：`modules/lib/src/utils/createSmartDebounceRequestFunc.ts`（原文 §顶部"源码位置"）。
- **导出包路径**：
  - `@insight/lib/utils` → 导出 `createSmartDebounceRequestFunc`、`createDebounceRequest`；
  - `@insight/lib/hooks` → 导出 `useSmartDebounceRequest`。
- **依赖关系**：
  - `useSmartDebounceRequest`（React Hook）基于 `createSmartDebounceRequestFunc`，叠加 `useRef` 稳定实例 + 组件卸载自动 `cancel()`；
  - `createDebounceRequest`（请求层封装）基于 `createRequest` + `createSmartDebounceRequestFunc` 组合，已内置 `keyFn`（按 `command:params` 隔离）。
- **适配场景的上下游**：
  - 与项目统一 `ClientConnector` 通信层配合（典型为 Electron 主进程 RPC/IPC 通信）；
  - 与 React 组件生命周期配合（依赖 `useRef` 与组件卸载清理机制）；
  - 与状态管理 / Loading 指示配合（通过 `onBeforeRequest` / `onAfterRequest` 钩子联动 `setLoading(true/false)`）。

---

## 【使用方法】

> 以下内容均直接源自原文代码示例与 API 签名。

### 方式一：底层工具函数 `createSmartDebounceRequestFunc`

```typescript
import { createSmartDebounceRequestFunc } from '@insight/lib/utils';

const debouncedQuery = createSmartDebounceRequestFunc(
    async (keyword: string) => {
        return fetchData('/api/search', { keyword });
    },
    {
        delay: 300,
        leading: false,
        keyFn: (keyword) => keyword[0],
        onBeforeRequest: (keyword) => setLoading(true),
        onAfterRequest: (result, keyword) => setLoading(false),
    }
);

const result = await debouncedQuery('hello');
debouncedQuery.cancel();
debouncedQuery.flush();
```

**选项（原文 §3.1）**：
- `delay?: number` — 默认 `300ms`
- `keyFn?: (...args) => string` — 按 key 隔离不同请求
- `leading?: boolean` — 默认 `false`
- `onBeforeRequest?: (...args) => void`
- `onAfterRequest?: (result, ...args) => void`

**返回实例方法（原文 §3.2）**：`(...args)`、`cancel(key?)`、`flush(key?)`、`getPendingCount()`、`getPendingKeys()`。

---

### 方式二：React Hook `useSmartDebounceRequest`

```typescript
import { useSmartDebounceRequest } from '@insight/lib/hooks';

function SearchComponent() {
    const debouncedSearch = useSmartDebounceRequest(
        async (keyword: string) => fetchData('/api/search', { keyword }),
        { delay: 300, leading: false }
    );

    const handleChange = (e) => {
        debouncedSearch(e.target.value).then(setResults);
    };

    return <input onChange={handleChange} />;
}
```

**说明**：原文指出该封装"在 `createSmartDebounceRequestFunc` 基础上增加了 `useRef` 稳定实例和组件卸载自动 `cancel()`"。

---

### 方式三：请求层封装 `createDebounceRequest`

```typescript
import { createDebounceRequest } from '@insight/lib/utils';

const debouncedRequest = createDebounceRequest(connector, {
    delay: 300,
    leading: false,
});

const result = await debouncedRequest('communication/matrix/group', params);
```

**说明**：原文指出"已内置 `keyFn`（按 `command:params` 隔离不同接口）"，适用于"使用项目统一 `ClientConnector` 通信层的场景"。

---

### 注意事项（原文 §4，原文逐条摘录）

1. **内存泄漏**：若调用方创建了大量不同 key 的请求但从未 `await` 或调用 `cancel()`/`flush()`，内部状态会持续占用内存。长时间运行场景建议定期调用 `getPendingCount()` 监控。
2. **React 组件**：优先使用 `useSmartDebounceRequest`，组件卸载时自动清理。
3. **竞态安全**：内部所有异步回调都检查 state 是否仍然有效，不会出现旧 timer/请求误操作新状态的问题。
