# Ultralytics HUB Quickstart

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/hub/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/hub/quickstart.md

# Ultralytics HUB Quickstart 一体化深度解读

## 【定位】

这篇文档是 Ultralytics HUB 的入门指引（Quickstart），面向首次接触该平台的用户，介绍如何注册登录、熟悉 Home 页面布局、以及如何通过首页快捷入口完成 Dataset 上传、Project 创建、Model 训练三大核心动作，从而将训练好的 YOLO 模型在 Ultralytics HUB App 中预览并部署用于分类、目标检测、实例分割等实时任务。

---

## 【技术要点】

1. **平台定位**：Ultralytics HUB 是一款用户友好、可视化直观的 Web 平台，支持用户快速上传数据集并训练新的 YOLO 模型，同时提供多种预训练模型供选择。
2. **三种模型任务**：训练完成的模型可部署用于三类实时任务——**classification（分类）**、**object detection（目标检测）**、**instance segmentation（实例分割）**。
3. **注册方式**：提供四类登录入口——**Google 账号**、**Apple 账号**、**GitHub 账号**、**邮箱地址**。
4. **资料完善**：注册流程中要求用户填写 profile（资料表单），注册后仍可通过 `https://hub.ultralytics.com/settings` 的 **Account** Tab 更新资料。
5. **Home 页三大入口模块**：侧边栏提供三大模块链接——**Datasets**（`/datasets`）、**Projects**（`/projects`）、**Models**（`/models`）。
6. **Home 页三大快捷卡片**：Recent（最近访问卡片）、Upload Dataset（上传数据集卡片）、Create Project（创建项目卡片）、Train Model（训练模型卡片）——均直接挂在 Home 页 (`/home`) 上。
7. **支持与反馈渠道**：Bug 报告 / Feature 请求 / 问题咨询统一走 `https://github.com/ultralytics/hub/issues/new/choose`；社区讨论走 Discord (`https://discord.com/invite/ultralytics`)；环境详情（Environment Details）通过 `https://hub.ultralytics.com/support` 页的 Copy Environment Details 按钮复制提交。

---

## 【关键机制与数据】

> 原文无性能数据、无算法机制说明，本文属 UI/操作型 Quickstart，仅按原文梳理其"页面—卡片—流程"数据流：

- **原文：登录态流转** → 注册 → 完成 Profile → 跳转 `https://hub.ultralytics.com/home` (Home)。
- **原文：Home 页结构** = 顶栏全局搜索 + 侧边栏模块导航（Datasets / Projects / Models）+ 内容区四张快捷卡（Recent / Upload Dataset / Create Project / Train Model）。
- **原文：Recent 卡行为** → 支持全局搜索 / 直达最近更新的 Datasets、Projects、Models。
- **原文：模型输出闭环** → 在 HUB 上训练 → 在 Ultralytics HUB App 中预览 → 部署用于实时 classification / object detection / instance segmentation。
- **原文：反馈可见性** → 仅 Ultralytics 团队内部可见，用于平台改进。

---

## 【表格解读】

**原文无表格**（全文为流程描述 + 截图说明，未出现任何参数表、对比表或配置表）。

---

## 【公式解读】

**原文无公式**（属操作引导型文档，未涉及任何 LaTeX 公式或伪代码算法）。

---

## 【关联】

文档作为 Quickstart 入口页，向上承接 Ultralytics HUB 的三大模块详细文档，向下衔接 HUB App 预览能力：

| 文中提到 / 链接的对象 | 关系方向 | 说明 |
|---|---|---|
| [Ultralytics HUB App](app/index.md) | 下游 / 预览侧 | 文末内部链接，指向 HUB App 文档，作用是让用户在模型训练后于 App 内"effortlessly preview"（无缝预览） |
| [datasets](https://docs.ultralytics.com/hub/datasets/) | 横向模块 | "Upload Dataset" 卡片跳转的详细文档 |
| [projects](https://docs.ultralytics.com/hub/projects/) | 横向模块 | "Create Project" 卡片跳转的详细文档 |
| [models](https://docs.ultralytics.com/hub/models/) | 横向模块 | "Train Model" 卡片跳转的详细文档 |
| Home 页 (`/home`) | 中心枢纽 | 是 Recent / Upload Dataset / Create Project / Train Model 四大卡片的承载页 |
| Settings (`/settings`) → Account Tab | 配置侧 | 资料更新的入口 |
| Support (`/support`) | 反馈侧 | 提供 Environment Details 复制的报错辅助页 |
| GitHub Issues (`ultralytics/hub/issues/new/choose`) | 反馈侧 | 外部 issue 入口 |
| Discord (`discord.com/invite/ultralytics`) | 社区侧 | 外部社区入口 |

可以看出，本 Quickstart 是"导航总览页"——它本身不教具体功能怎么用，而是把用户分流到 **datasets / projects / models 三大模块文档** 以及 **HUB App 预览文档**（`app/index.md`）这两类下游页面。

---

## 【使用方法】

原文为 Web UI 操作型指引，启用方式以"页面访问 + 按钮点击"为主，无代码命令、无配置文件。逐条列出原文中明确给出的可执行入口：

1. **注册 / 登录**：访问 `https://www.ultralytics.com/hub`，使用 Google / Apple / GitHub 账号，或邮箱地址完成注册登录。
2. **完善 / 更新资料**：注册时填写 Profile 表单；注册后通过 `https://hub.ultralytics.com/settings` 的 Account Tab 更新。
3. **进入主页**：登录后自动跳转 `https://hub.ultralytics.com/home`。
4. **查看最近访问**：在 Home 页的 **Recent** 卡片中全局搜索或直接打开最近更新的 Datasets / Projects / Models。
5. **上传数据集**：在 Home 页点击 **Upload Dataset** 卡片（详见 `https://docs.ultralytics.com/hub/datasets/`）。
6. **创建项目**：在 Home 页点击 **Create Project** 卡片（详见 `https://docs.ultralytics.com/hub/projects/`）。
7. **训练模型**：在 Home 页点击 **Train Model** 卡片（详见 `https://docs.ultralytics.com/hub/models/`）。
8. **预览模型**：训练完成后在 Ultralytics HUB App 中预览（详见 `app/index.md`）。
9. **提交反馈**：在 Home 页点击 Feedback 按钮留言（仅 Ultralytics 团队可见）。
10. **报错 / 提问**：在 `https://github.com/ultralytics/hub/issues/new/choose` 提交 issue，提交前请从 `https://hub.ultralytics.com/support` 页复制 Environment Details 一并附上。
11. **社区交流**：加入 Discord `https://discord.com/invite/ultralytics`。

> 注：原文中**未涉及**任何命令行、YAML/JSON 配置、API 调用或编程接口的使用方式——这些属于 HUB 平台之外或更深层文档的范畴。
