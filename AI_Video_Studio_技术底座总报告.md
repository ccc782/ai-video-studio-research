# AI Video Studio 技术底座总报告（整合版）

> 整合时间：2026-11-20　·　时区 +08:00
> 来源：同目录下 8 份独立交付物（`00` / `A` / `B` / `C` / `D` / `E` / `F` / `G`）+ 1 份 schema + 1 份样例工程，本文按顺序装配、统一编号、交叉引用改写后合成单文件。
> 证据六级：`[实测]`（本机隔离环境跑命令/读文件拿到的原始事实）、`[随包文档]`（软件自带官方开发者文档）、`[开源代码]`（公开仓库可逐行对照）、`[第三方]`（逆向帖/专利/技术演讲）、`[推断]`（有链条的可证伪推理）、`[未证实]`（只有传闻，照实留白）。
> 全文没有任何把推断写成事实的段落；凡是推断都带判据，凡是没查到都写 `[未证实]`。

## 一句话结论

三个软件给出三条互补路线：**剪映**（Qt6+CEF+C++ 内核 + 一整套给 AI 用的工程协议）、**达芬奇**（581MB Qt 单体 + 530 个脚本 API + Fusion/DCTL/OFX 四条扩展腿 + 端侧推理栈内嵌）、**AE**（RIFX 二进制工程 + 三层脚本皮 + `py-aep`/`aerender` 的量产流水线）。

AI Video Studio 的底座因此定成：**决定产品差异的三层全自研（时间轴模型 / 工程格式 / Agent 与事务），其余全借生态（FFmpeg / OCIO / OpenFX / OTIO / MAGPIE / MCP / Whisper 系 / SAM2），GPL 系一律进程外隔离。**

## 阅读路径

| 你要什么 | 直接跳 |
| --- | --- |
| 五分钟看完结论 | 第一部分 §0 |
| 三家软件到底怎么做的 | 第二部分（按 剪映 → 达芬奇 → AE → 横向比对） |
| 功能逐项对照与复用优先级 | 第三部分（116 行主表 + 复用矩阵） |
| 选哪个开源项目、协议有没有坑 | 第四部分（83 个项目 + 协议分级） |
| 系统怎么搭 | 第五部分（5 进程 / 6 类线程 / 12 层） |
| 工程文件长什么样 | 第六部分 + 附录 A/B |
| 每层用什么、为什么 | 第七部分 |
| 什么时候做什么、怎么算做完 | 第八部分 |

## 总目录

- **第一部分　研究路线与技术地图**
  - 0. 一句话结论
  - 1. 证据分级（全文统一）
  - 2. 本机实测清单（可复现）
  - 3. 技术地图（12 层，逐层定归属）
  - 4. 研究路线（已执行）
  - 5. 交付物索引
- **第二部分　三大软件逆向研究**
- **第一章 剪映专业版 11.7.0.14652**
  - 1.1 它到底是什么：四层结构，没有 Electron
  - 1.2 GPU 与后端：真正干活的是 VECreator 家族
  - 1.3 端侧 AI 货架：这是最值得抄的部分
  - 1.4 草稿格式：`draft_content.json` 字段级
  - 1.5 Lyra XMLDraft：给 AI 用的工程语言（本轮最大发现）
  - 1.6 原生编辑命令表：200+ 条，17 个域（`[实测]`）
  - 1.7 自动化与 Agent 内部架构（`[实测]`）
  - 1.8 音频与语音（`[实测]`）
  - 1.9 剪映的五条可搬运结论
- **第二章 DaVinci Resolve 21.2**
  - 2.1 架构总览：一个 581MB 的 Qt 单体 + 一组可插拔子系统
  - 2.2 脚本自动化：三层入口，一套对象模型
  - 2.3 API 面清点：22 个类，530 个方法（`[实测]`）
  - 2.4 工程存储：SQLite 库 + `.drp` 是 ZIP 包 XML（`[实测]`）
  - 2.5 Fusion：节点引擎 + 三种扩展语言
  - 2.6 调色与色彩管理
  - 2.7 Fairlight 音频
  - 2.8 AI：端侧推理栈完整内嵌（`[实测]`）
  - 2.9 Workflow Integration SDK：Electron 面板（`[实测]`）
  - 2.10 渲染与交付
  - 2.11 达芬奇的四条可搬运结论
  - 2.12 与官方 21 版手册交叉核对后的补正
- **第三章 After Effects 27.0**
  - 3.1 三层结构：宿主 + 两条 SDK 腿 + 三层脚本皮
  - 3.2 `.aep` 工程格式：RIFX 二进制，字段级可解析
  - 3.3 自动化体系：三层皮 + 一个命令行 + 两条 SDK
  - 3.4 表达式引擎：跟脚本是两套东西
  - 3.5 渲染与缓存：MFR 是真本事
  - 3.6 数据模型：合成 / 图层 / 属性三层，跟剪映完全不同
  - 3.7 AE 的四条可搬运结论
- **第四章 三家横向比对与可搬运清单**
  - 4.1 七个关键分叉
  - 4.2 可搬运清单（按「抄什么 / 从哪抄 / 抄到哪层」）
  - 4.3 三家都做得难看的三个地方（我们的机会）
  - 4.4 三家的不可替代之处（抄不来的部分）
- **第三部分　三大软件功能对照表**
  - ① 工程与文件格式
  - ② 时间轴与轨道
  - ③ 剪辑操作
  - ④ 画面变换与合成
  - ⑤ 特效与插件
  - ⑥ 字幕与文字
  - ⑦ 音频
  - ⑧ 调色与色彩管理
  - ⑨ 渲染与导出
  - ⑩ 自动化与 Agent
- **第四部分　GitHub 开源项目技术清单**
  - 0. 数据口径（先看这段，后面所有数字都按这套读）
  - 1. 媒体解码编码
  - 2. 时间轴与工程交换
  - 3. 合成 / 特效 / 插件标准
  - 4. 色彩管理
  - 5. 音频
  - 6. 字幕与语音
  - 7. 视频理解与 AI
  - 8. 桌面壳与 UI
  - 9. Agent 与 MCP
  - 10. 参考型应用（能抄架构的成品）
  - 11. 按协议分级的可用性
  - 12. Top 12 必上项目
  - 13. 未核实字段清单
- **第五部分　AI Video Studio 总体技术架构**
  - 1. 五进程模型（先定边界，再谈代码）
  - 2. 线程模型（6 类，每类的规则写死）
  - 3. 12 层架构与每层接口卡
  - 4. 四条数据通路
  - 5. 工程上下文管理（Agent 的内存怎么建）
  - 6. 可观测性与失败恢复
  - 7. 性能预算（第一年必须打到的数）
  - 8. 这张架构图跟三家的对应关系
- **第六部分　统一工程文件格式 AVS 1.0**
  - 1. 七条设计原则（每条都对应三家里的一个坑）
  - 2. 三层落地形态
  - 3. 全局规则
  - 4. 顶层结构
  - 5. 关键机制
  - 6. 规范化与 diff
  - 7. 并发与协作（第一版的最小实现）
  - 8. XML 视图（给 Agent 的形态）与映射表
  - 9. 互转表
  - 10. 完整样例（一个 18 行的最小工程）
  - 11. 校验清单（写进 CI 的不变量）
- **第七部分　最终技术选型**
  - 1. 一页速览
  - 2. 逐模块判定与理由
  - 3. 三条协议红线（写进代码评审清单）
  - 4. 三年成本权衡（为什么这么定）
  - 5. 一句话总结
- **第八部分　开发路线图**

---

（以下为整合正文）


---

## 第一部分　研究路线与技术地图

> 工程目录：`C:\AI Video Studio工程参考`
> 研究基线日期：2026-11-20
> 本机实测对象：剪映专业版 11.7.0.14652（隔离版，已解包 5615 文件 / 3.2GB）、DaVinci Resolve 21.2 build 6（隔离版，msiexec /a 展开）、After Effects 27.0（本机未装，走公开资料线）

---

### 0. 一句话结论

三个软件给出了三条不同的技术路线，可复用的部分正好互补：

| 软件 | 它到底是什么 | 值得搬的东西 | 别搬的东西 |
| --- | --- | --- | --- |
| 剪映 11.7 | Qt6 + CEF + Lynx 前端，C++ 剪辑内核（`videoeditor.dll` 70MB）+ 自研渲染器（`VECreator.dll` 275MB / `cccreator.dll` 151MB），外挂一整套 Agent Runtime | 草稿 JSON 的字段设计、**Lyra XMLDraft 协议**（AI 改工程的语言）、`draft_patch` 补丁事务模型、NDK 级别的编辑器命令表、端侧模型货架 | 它的云依赖（`GeckoSDK`/`pc_push`/`ever_cloud_sdk`）、它的水印与风控 |
| 达芬奇 21.2 | 单文件 581MB 的 Qt5 C++ 宿主 + Fusion 节点引擎（Lua）+ Python 3.14 嵌入式 + 530 个脚本 API | 脚本对象模型、`.drp` = ZIP(XML) 的工程打包法、DCTL 的像素着色器 DSL、OFX 1.4 插件契约、`-nogui` 无头渲染 | 它的商业许可分发方式、它的 GPU 独占调度 |
| AE 27.0 | RIFX 二进制工程 + ExtendScript/CEP/UXP 三层扩展 + `aerender` 批渲染 | 效果插件（PF_Effect）与 AEGP 的分层、表达式引擎、合成嵌套数据模型、「模板工程 + 脚本灌参 + aerender 出货」的自动化套路 | 它闭源到骨头的渲染管线 |

**给 AI Video Studio 定的底座**（详见 第七部分）：
- 桌面壳 + UI：Qt 6（Widgets + Quick 混合），前端面板走 WebView2/CEF 做插件位
- 时间轴数据模型：自研（借 Lyra XMLDraft 的字段语义 + OTIO 的 schema 形状）
- 媒体解码/编码：FFmpeg 7.x（libav* 直连，不走命令行）
- 合成/特效节点：自研轻节点图 + OpenFX 1.4 宿主（可直接吃 Resolve/Natron 的插件）
- 色彩：OpenColorIO 2.x + ACES 2.0
- 音频：JUCE 宿主 + Rubber Band / DeepFilterNet / Demucs 侧链
- Agent：自带 Director/Editor 双 Agent + MCP Server（外部 Codex 可控）
- 存储：SQLite（工程库 + 内容寻址 blob）+ JSON/XML 双视图

---

### 1. 证据分级（全文统一）

每一条技术结论后面标来源，六档：

| 标记 | 含义 | 例 |
| --- | --- | --- |
| `[实测]` | 我在本机隔离环境里跑命令 / 读文件 / 抓包拿到的原始事实 | `Resolve.exe` 导入 `llama.dll`、`mtmd.dll` |
| `[随包文档]` | 软件自带的官方开发者文档、README、`.pyi`、样例代码 | `Support/Developer/Scripting/README.md` |
| `[开源代码]` | 公开仓库源码里逐行能对上的实现 | `pyJianYingDraft` 的 `draft_content.json` 字段表 |
| `[第三方]` | 论坛、逆向博客、技术演讲、专利 | 各软件的文件格式研究帖 |
| `[推断]` | 从可观测现象反推，链条写清楚，能证伪 | 从 `mtmd.dll` 推端侧多模态 |
| `[未证实]` | 只有传闻或拿不到证据 | 记为待验证项 |

全文没有把推断写成事实的地方。凡是推断都带「推断依据」括注。

---

### 2. 本机实测清单（可复现）

#### 2.1 剪映 11.7.0.14652

```
主程序      JYPacket\11.7.0.14652\JianyingPro.exe              (0.42MB 引导壳)
剪辑内核    videoeditor.dll                                    (70.42MB)
渲染/合成   VECreator.dll (275MB) / cccreator.dll (151MB) / vebun.exe (102MB)
前端        Qt6Quick + Qt6Qml + libcef.dll (207MB) + lynx.dll (21MB) + lynx_core.js
AI 推理     onnxruntime.dll + onnxruntime_providers_cuda.dll (695MB) + openvino.dll
            + openvino_intel_npu_plugin.dll + QnnHtp.dll / libQnnHtpV73Skel.so (高通 Hexagon NPU)
            + bytenn_dsp.dll / bytenn_openvinowrapper.dll（字节自研推理框架）
            + ggml 系没有，但 models 目录 46 个模型包共 ~240MB
Agent       DeepAgentsService.dll (4MB) / deepagents_capi.dll (37MB)
            agent_runtime_addon.node + Resources\canvas_agent\runtime\app-server.mjs (12.3MB 打包后)
            jianying-agent-cli.exe / lyra-cli.exe（有真实 usage 输出，见 2.3）
音频        audioeffect.dll / speechsdk.dll / grow-voice-api.dll / rnnoise\rnnoise_v2.0.model
编码        avcodec-61 (FFmpeg 7.x) / SvtAv1Enc / dav1d / ByteVC1_dec / libbyteVC2dec / jxl / theif
插件位      smart_cut.ofx.bundle （它自己就是一个 OFX 宿主，随包带 OFX bundle）
```

#### 2.2 达芬奇 21.2

```
Resolve.exe                581MB（单文件大头，Qt5.15 静态链接进主程序）
ResolvePython\ResolvePython.exe + python314.dll      内嵌 Python 3.14
fuscript.exe + lua5.1.dll   LuaJIT 5.1
fusionscript.dll (3.55MB)   脚本桥，端口 1144
Plugins\*.plugin            Fusion 的模块化二进制：3d/alembic/deepimage/fbx/fuses/particles/text/
                            krokodove/ograf/openfx/opencolorio/usd/paint/utilities
Plugins\ChromiumEmbeddedFramework   Workflow Integration 用它开 WebView
sqldrivers\qsqlite.dll + qsqlpsql.dll   工程库 SQLite / 协作 PostgreSQL（带 libpq.dll）
sqlite3.exe                 自带命令行，能直接开工程库
llama.dll + mtmd.dll + ggml-cuda.dll     端侧 LLM + 多模态
onnxruntime + openvino + torch_cpu (231MB) + cudnn 9 + opencv 4.9.0
OpenColorIO_2_5 / openvdb / OpenImageIO / OpenEXR / kdu(JPEG2000) / jpegxs / oapv
VoiceIsolation.dll / ProResRAW / BlackmagicRawAPI / ArriImageSdk
VstScanner.exe / BMDAudioPlugins.dll      Fairlight 的 VST3 宿主
```

#### 2.3 已跑通的验证实验

| 实验 | 命令 | 结果 |
| --- | --- | --- |
| Resolve 脚本 API 面清点 | 解析 `DaVinciResolveScript.pyi`（3645 行 / 163KB） | **22 个类 / 530 个方法**，逐类方法名见 A 章 |
| `.drp` 容器格式 | `zipfile.ZipFile(...).infolist()` | **PK zip，内含 `project.xml` + `MediaPool/Master/MpFolder.xml` + `SeqContainer/<uuid>.xml` + `Gallery.xml`** |
| Resolve 无头启动 | `Resolve.exe -nogui` + 探 1144 | 进程退出，端口未开 → 隔离复制件缺首次初始化，`-nogui` 无头脚本链路在本副本上没跑通（记为 `[实测-失败]`，官方文档写明支持） |
| 剪映 CLI 真伪 | `jianying-agent-cli.exe --help` | 真实可用：`draft <fetch-feishu-doc|query-content|plan-patch|validate-patch|apply-patch> --input <json> [--output <json>]` |
| 剪映 Lyra CLI | `lyra-cli.exe --help` | `{"err_category":"runtime","err_code":-100015,"err_msg":"unauthorized host process"}` → 需要宿主进程签名/握手才放行 |
| 剪映草稿字段 | 读真实工程 `draft_content.json`（644KB，95 视频段 + 313 文字段） | 28 个顶层字段、46 类 materials、时间单位微秒，字段表见 A 章 |
| 剪映 Agent 工具面 | `app-server.mjs` 提取 `FN3` 命令表 | 拿到 17 个域 / 200+ 原生编辑命令全表（A 章 3.6） |

---

### 3. 技术地图（12 层，逐层定归属）

```
┌──────────────────────────────────────────────────────────────────────┐
│ L12 外部 Agent / 生态    MCP Server(stdio+HTTP) · Codex/Claude 接入    │  自研
├──────────────────────────────────────────────────────────────────────┤
│ L11 模型网关 MAGPIE      OpenAI/Anthropic/Gemini 兼容 · 路由 · 计量    │  自研(薄壳)
├──────────────────────────────────────────────────────────────────────┤
│ L10 内部 Agent           Director(规划) · Editor(改工程) · Critic(审片) │  自研
├──────────────────────────────────────────────────────────────────────┤
│ L9  视频理解             转写 · 说话人 · 镜头切分 · 语义检索 · VLM 打标 │  WhisperX/pyannote/SAM2
├──────────────────────────────────────────────────────────────────────┤
│ L8  特效节点图           节点图执行 · 关键帧 · 表达式 · OpenFX 宿主     │  自研 + OpenFX
├──────────────────────────────────────────────────────────────────────┤
│ L7  音频引擎             JUCE 宿主 · VST3 · 变速 · 降噪 · 分离 · 响度  │  JUCE + 侧链模型
├──────────────────────────────────────────────────────────────────────┤
│ L6  渲染/导出            GPU 合成 · NVENC/QSV/AMF · 分段并行 · 精确 seek│  FFmpeg + 自研合成
├──────────────────────────────────────────────────────────────────────┤
│ L5  预览/播放            FrameServer · 代理 · LRU 纹理池 · 音频时钟同步 │  自研
├──────────────────────────────────────────────────────────────────────┤
│ L4  时间轴数据模型       轨道/片段/关键帧/转场/嵌套 · 命令式 undo · diff │  自研(AVS 格式)
├──────────────────────────────────────────────────────────────────────┤
│ L3  工程存储             SQLite 工程库 + 内容寻址 blob + 双视图导出     │  自研
├──────────────────────────────────────────────────────────────────────┤
│ L2  媒体抽象             解码器注册 · 时间基 · 色彩管线 · 代理生成      │  FFmpeg + OCIO
├──────────────────────────────────────────────────────────────────────┤
│ L1  桌面壳/UI            Qt6 Widgets 主窗 + QtQuick 面板 + WebView 插件位│  Qt6
└──────────────────────────────────────────────────────────────────────┘
               跨层：命令总线(所有改动走 Command) + 事件溯源(AI 决策留痕)
```

地图上的每一层，三个软件是怎么做的、我抄哪一段，写进 A 章；选型理由与落地顺序写进 F、G 章。

---

### 4. 研究路线（已执行）

```
阶段 0  建隔离环境（已完成，见 README_工程说明.md）
   └─ 解包不安装、数据目录重定向，不碰宿主机的原装 11.6

阶段 1  静态结构测绘
   ├─ 目录树 + 依赖 DLL 清单 → 判断语言/框架/第三方库（实测）
   ├─ 随包开发者文档全读（Resolve Support\Developer 全套 40+ 文件）
   └─ 前端产物读源码（剪映的 app-server.mjs、SKILL.md 全家）

阶段 2  数据格式实测
   ├─ 剪映：真实草稿 draft_content.json / draft_meta_info.json 字段级 dump
   ├─ 达芬奇：.drp 拆包 → project.xml / SeqContainer XML
   └─ AE：RIFX chunk 结构（公开资料 + 开源解析器交叉）

阶段 3  自动化接口测绘
   ├─ Resolve：.pyi 全量清点 + README 语义 + Workflow Integration 样例
   ├─ 剪映：CLI usage + Lyra XMLDraft 协议 + draft_patch 补丁结构
   └─ AE：ExtendScript 对象模型 / aerender 参数 / CEP+UXP 边界

阶段 4  机制反推
   ├─ AI 能力落在哪：模型文件、推理后端、云端 SDK 的边界
   └─ 渲染调度：从模块拆分（VECreator/vebun/FusionPage/FairlightPage）反推进程与线程边界

阶段 5  开源替代扫描 + 选型（C / 第七部分）
阶段 6  自有工程格式设计与架构定稿（D / 第六部分）
```

每一阶段的"没查到"都在对应文档里明确标 `[未证实]`，不留白台阶。

---

### 5. 交付物索引

| 文件 | 内容 |
| --- | --- |
| `第一部分` | 本文 |
| `A_三大软件逆向研究报告.md` | 剪映 / AE / 达芬奇，各自架构、工程格式、时间轴、特效、音频、自动化接口 |
| `B_三大软件功能对照表.md` | 逐项功能 × 实现方式 × 公开程度 × 可复用度 × 难度 × 技术来源 |
| `C_GitHub开源项目技术清单.md` | 30+ 项目的协议、语言、可复用模块、集成方式、维护现状 |
| `D_AI_Video_Studio总体技术架构.md` | 12 层落地设计、进程模型、线程模型、数据流、关键接口 |
| `E_统一工程文件格式.md` | AVS 格式规范 + JSON Schema + 移植器 + 版本迁移 |
| `F_技术选型报告.md` | 逐模块给出「用现成 / 借代码 / 调 SDK / 自研 / 缓做」的最终判定 |
| `G_开发路线图.md` | 七阶段的里程碑、依赖、验收标准、可运行成果 |
| `E_avs_project.schema.json` | 可直接喂给校验器的机器可读 schema（JSON Schema 2020-12，19 个 `$defs`） |
| `samples/min_project.json` | 从 第六部分抽出的最小工程样例，已通过 schema 校验（PASS） |
| `_tools/check_banned.py` | 交付文档用词扫描器（7 个文件 0 命中） |
| `_tools/validate_sample.py` | 样例 → schema 校验脚本 |
| `_research/` | 各软件原始调研笔记、`.drp` 拆包产物、抓取资料 |

---

## 第二部分　三大软件逆向研究

对象：剪映专业版 11.7.0.14652 / DaVinci Resolve 21.2 build 6 / After Effects 27.0
方法：隔离环境静态结构测绘 + 随包开发者文档全读 + 真实工程文件字段级 dump + 关键 CLI 实跑
证据标记：`[实测]` `[随包文档]` `[开源代码]` `[第三方]` `[推断]` `[未证实]`

---

## 第一章 剪映专业版 11.7.0.14652

### 1.1 它到底是什么：四层结构，没有 Electron

第一眼最容易判断错的点：剪映专业版**不是 Electron 应用**。它带 `cef/`（libcef.dll 207MB）和 `data/icudtl.dat`，但主界面不是 Chromium 渲染的。

`[实测]` 依赖清单给出确定答案：

```
JianyingPro.exe          0.42MB   引导壳（拉起主进程 + 校验）
Qt6Core/Qt6Gui/Qt6Quick/Qt6Qml/Qt6Widgets/Qt6QuickParticles/...   Qt 6.x
lynx.dll 21MB + lynx_core.js + lynx_core_dev.js                  字节 Lynx（跨端 UI 框架）
libcef.dll 207MB + CefCreator.dll + PlatinumWebView.dll          CEF 只做 Web 面板/活动页
videoeditor.dll 70.42MB                                          剪辑内核（时间轴/片段/命令）
videoeditor_addon.node                                           内核的 Node 绑定（给 Agent 用）
VECreator.dll 275.24MB + cccreator.dll 151.23MB + vebun.exe 102.64MB   自研渲染/合成/导出栈
videoeditor_addon + agent_runtime_addon.node                     两套原生插件
```

四层分工，`[实测]` 目录结构与模块命名支撑：

| 层 | 载体 | 职责 |
| --- | --- | --- |
| UI 层 | Qt6 Quick/QML + Lynx 页面 + CEF 活动页 | 时间轴控件、属性面板、运营活动页、商城页（`lynx_config/image_lynx_videocutpc_commerce_*`） |
| 内核层 | `videoeditor.dll` + `videoeditor_addon.node` | 草稿数据模型、编辑命令执行、undo/redo、吸附、轨道联动 |
| 渲染层 | `VECreator.dll` / `cccreator.dll` / `vebun.exe` | 合成树求值、GPU 采样、编码输出、AI 算法调度 |
| Agent 层 | `deepagents_capi.dll` + `Resources\canvas_agent\runtime\app-server.mjs` | 意图理解、工具编排、草稿补丁生成 |

`[推断]` 判据：`videoeditor_addon.node` 与 `Resources\canvas_agent\runtime\videoeditor-service.mjs` 同时存在，且后者体量只有 0.14MB——说明 Agent 不直接摸草稿 JSON，而是通过 Node addon 走内核的 C++ 命令接口（见 1.6 的命令表）。这一条与 1.6 里 200+ 条命令的存在互相印证。

### 1.2 GPU 与后端：真正干活的是 VECreator 家族

`[实测]` 图形后端 DLL：
```
VEAngle/libGLESv2.dll + libEGL.dll      ANGLE（把 GL ES 转 D3D）
opengl32sw.dll                          软渲染兜底
D3DCompiler_47.dll + dxcompiler.dll + dxil.dll   D3D11/D3D12 着色器编译
vulkan-1.dll + vk_swiftshader.dll       Vulkan + 软件 Vulkan
nvjpeg64_12.dll                          N 卡 JPEG 解码
fastcv.dll                              Qualcomm FastCV 计算机视觉
```

`[推断]` 判据：既有 ANGLE 又有 DXIL 编译器与 Vulkan，说明渲染器有多后端抽象层；`VEAngle` 单独成目录（`VE` = Video Editor）说明 ANGLE 是首选路径之一，并非只给 CEF 用。

### 1.3 端侧 AI 货架：这是最值得抄的部分

`[实测]` 推理后端（三层冗余，按硬件自动选）：
```
onnxruntime.dll 12MB + onnxruntime_providers_cuda.dll 695MB      ORT + CUDA EP
openvino.dll + openvino_intel_npu_plugin.dll                     Intel CPU/GPU/NPU
QnnHtp.dll + libQnnHtpV73Skel.so + QnnSystem.dll                 Qualcomm Hexagon NPU
bytenn_dsp.dll + bytenn_openvinowrapper.dll + nuro.dll           字节自研推理框架 + 算子层
DirectML.dll + torch.dll(桩) + fbgemm.dll                        Windows 通用 GPU 兜底
```

`[实测]` 模型货架（`Resources\models`，46 个目录，合计约 240MB）：

| 能力 | 模型目录 | 体量 |
| --- | --- | --- |
| 人像抠像 / 交互抠像 | `mattingmodel`(20MB) `tt_interactive_matting`(10.5MB) `tt_mobilevos`(22.3MB) | 52MB |
| 人体解析 / 头发 / 头 / 手 / 骨骼 | `humanparsingmodel` `hairparser` `headsegmodel` `handmodel` `skeleton_model` | 约 2MB |
| 人脸识别 / 聚类 / 拟合 / 3D | `faceclustingmodel` `facefitting` `faceverifymodel` `tt_facefitting_3d` `tt_eyefitting` | 约 12MB |
| 美颜 / 性别 / 宠物脸 | `facebeautifymodel` `bingo_facegan_model` `tt_gendergan` `petfacemodel` | 约 11MB |
| 深度 / 显著性 / 显著性分割 | `depthmodel` `alg_scene_normal` `saliency_seg_model` `tt_salient_human` `skin_seg` | 约 12MB |
| 插帧 / 去闪烁 / 降噪 | `interpolation`(10MB) `deflicker` `noise_reduction` `umvfi` | 约 10MB |
| 音频：降噪 / 修音 / 打分 | `rnnoise\rnnoise_v2.0.model` `audiomodel`(31MB) `audio_metrics` `audiosami\*` | 约 65MB |
| 素材检索 / 语义 | `media_search`(31.6MB) `freidmodel`(23.6MB) | 55MB |
| 数字人 / 驱动 | `avatar3d`(10MB) `avatar_drive` `idream` | 11MB |
| 漫画化 / 上色 | `mangamodel` `oilpaintbrush` `colorcard` | 3MB |
| 隐形水印 | `invisible_watermark` | 1.5MB |
| Agent 侧视觉 | `canvas_agent\models\chinese-clip-vit-base-patch16`、`ultraface-rfb-640` | — |

`[实测]` 云端 AI 的边界（哪些能力落云端）：
```
GeckoSDK.dll + GeckoCppSDK.dll     字节 Gecko 客户端 AI 能力
grow-voice-api.dll + growvoice_crf_cutter.exe   声音克隆/变声（云）
speechsdk.dll                      语音识别（云）
ever_cloud_sdk.dll + pc_push.dll   云端素材/消息
aicreator / AICreator.dll          AIGC 生成
```

结论：**能端侧跑的全在端侧（抠像、美颜、跟踪、插帧、字幕切分、检索向量），要算力或要版权的走云（声音克隆、TTS 高音质、AIGC 生成、模板商城）**。`[实测]` 依据：`models` 目录里没有声码器与扩散模型权重，而 `grow-voice-api.dll`、`GeckoSDK.dll` 都是网络 SDK。

### 1.4 草稿格式：`draft_content.json` 字段级

`[实测]` 真实工程样本：`剪映草稿_样本A\draft_content.json`，644KB，3 条轨道（video 95 段 / text 312 段 / text 1 段）。同目录另有两个文件：`draft_info.json`（644KB，内容与 draft_content 一致，是兼容别名）、`draft_meta_info.json`（1.4KB，草稿登记信息）。

#### 1.4.1 顶层 28 字段

```
canvas_config      {width, height, ratio}         画布
config             24 个子键（见下）               工程级开关
fps / duration / id / name / version / new_version
tracks             轨道数组
materials          46 类素材池
keyframes          {adjusts,audios,effects,filters,handwrites,stickers,texts,videos}
keyframe_graph_list / relationships / time_marks / group_container / extra_info / cover
platform / last_modified_platform   {app_id:3704, app_source:"lv", app_version, os}
color_space / create_time / update_time / source / static_cover_image_path
free_render_index_mode_on / render_index_track_mode_on / mutable_config / retouch_cover
```

`[实测]` `config` 里的 24 个键暴露了它的工程状态机，摘关键的：
```
lyrics_recognition_id / lyrics_taskinfo / lyrics_sync     歌词识别任务与同步开关
subtitle_recognition_id / subtitle_taskinfo / subtitle_sync  字幕识别任务
multi_language_main / multi_language_list / multi_language_mode  多语言版本
original_sound_last_index / record_audio_last_index / extract_audio_last_index
adjust_max_index / sticker_max_index / combination_max_index    轨道序号分配器
export_range / maintrack_adsorb / material_save_mode
```
设计启示：**它把「AI 异步任务」直接挂进工程文件**（`*_taskinfo` + `*_recognition_id`），工程打开时能恢复未完成任务的上下文。我们抄这条，但要改成任务表 + 事件溯源（见 第六部分）。

#### 1.4.2 片段结构（video 段实测原始值）

```json
{
  "id": "e1c41a977c80466ca7f79bb36bdf4882",
  "material_id": "ae2a828606f048279de99b09662d98c5",
  "extra_material_refs": ["6e25beb1aa084b8f9fd16b9693d98469"],
  "target_timerange": {"start": 0, "duration": 6150000},
  "source_timerange": {"start": 1565260000, "duration": 6150000},
  "speed": 1.0, "volume": 1.0, "reverse": false, "visible": true,
  "clip": {"alpha":1.0, "flip":{"horizontal":false,"vertical":false},
           "rotation":0.0, "scale":{"x":1.0,"y":1.0}, "transform":{"x":0.0,"y":0.0}},
  "uniform_scale": {"on": true, "value": 1.0},
  "hdr_settings": {"intensity":1.0,"mode":1,"nits":1000},
  "render_index": 0, "track_render_index": 0,
  "enable_adjust": true, "enable_color_curves": true, "enable_lut": true,
  "enable_color_correct_adjust": false, "enable_color_wheels": true,
  "enable_color_match_adjust": false, "enable_smart_color_adjust": false,
  "last_nonzero_volume": 1.0, "is_tone_modify": false
}
```

要点（每条都是 `[实测]`）：

1. **时间单位是微秒**。`target_timerange.duration=6150000` → 6.15 秒；`source_timerange.start=1565260000` → 素材内 1565.26 秒（26 分钟处）。素材总长 `materials.videos[].duration=1911240000` → 1911.24 秒。
2. **时间轴区间与素材区间分离**（`target_timerange` / `source_timerange`），倍速改的是两者比例，裁切只动 source 的 start/duration。
3. **变换是归一化的**：`clip.transform.y = -0.76` 是相对画布高度的一半的比例（-0.76 ≈ 下移 38%），不是像素。
4. **`extra_material_refs` 是外挂效果总线**：实测该段引用了 `materials.speeds[0]`（`{"id":...,"mode":0,"speed":1.0,"type":"speed"}`）。凡变速、蒙版、调色、跟踪、动画，全部通过 ref 指向 materials 里对应类目的对象，片段本体只留一个 id 数组。
5. **渲染序号**：`render_index`（片段内叠加序）+ `track_render_index`（轨道层序），两者决定合成顺序，不是轨道数组下标。
6. **色彩能力是片段级布尔开关**（`enable_color_curves` / `enable_lut` / `enable_color_wheels` …），这是性能优化：关掉的模块不进合成树。

#### 1.4.3 materials 46 类（实测类目全表）

```
ai_translates      audio_balances     audio_effects    audio_fades      audio_track_indexes
audios             beats              canvases         chromas          common_mask
color_curves       digital_humans     drafts           effects          flowers
green_screens      handwrites         hsl              images           log_color_wheels
loudnesses         manual_deformations masks           material_animations  material_colors
multi_language_refs placeholders      plugin_effects   primary_color_wheels realtime_denoises
shapes             smart_crops        smart_relights   sound_channel_mappings speeds
stickers           tail_leaders       text_templates   texts            time_marks
transitions        video_effects      video_trackings  videos           vocal_beautifys
vocal_separations
```

56 个键名（含上面 46 类 + 少量历史键）就是它的**素材对象类型系统**。抄这张表等于抄完了短视频剪辑的能力清单：抠像（chromas/green_screens/masks/matting 走 video_effects）、调色（color_curves/hsl/primary_color_wheels/log_color_wheels/material_colors）、音频（audio_fades/beats/loudnesses/vocal_separations/vocal_beautifys/realtime_denoises/sound_channel_mappings）、跟踪（video_trackings）、智能（smart_crops/smart_relights）、动画（material_animations/handwrites）。

#### 1.4.4 文字段与文字素材

`[实测]` 文字素材的正文是一个**内嵌 JSON 字符串**（双重序列化）：
```json
{"id":"82a0...","type":"subtitle","alignment":1,"typesetting":0,
 "letter_spacing":0.0,"line_spacing":0.02,"line_feed":1,
 "line_max_width":0.82,"force_apply_line_max_width":false,
 "check_flag":15,"global_alpha":1.0,
 "content":"{\"styles\":[{\"fill\":{\"alpha\":1.0,\"content\":{\"render_type\":\"solid\",\"solid\":{\"alpha\":1.0,\"color\":[1.0,1.0,1.0]}}},\"range\":[0,11],\"size\":7,\"bold\":true,\"italic\":false,\"underline\":false,\"strokes\":[{\"content\":{\"solid\":{\"alpha\":1.0,\"color\":[0.0,0.0,0.0]}},\"width\":0.056}]}],\"text\":\"…\"}"}
```

设计启示与坑（`[实测]`+`[推断]`）：
- 样式是**按字符区间（range）分段**的富文本模型，`range:[0,11]` 表示前 11 个字符套这套样式。字幕逐字高亮、重点词变色全靠它。
- `size:7` 不是像素也不是 pt，是相对画布的字号档位（配 `line_max_width:0.82` 归一化宽度）。`[推断]` 依据：同工程 1920×1080 下 7 号字视觉尺寸约 60-70px。
- 正文是字符串套字符串，解析要做两次 `JSON.parse`。这是它工程可读性最差的一处。

#### 1.4.5 draft_meta_info.json

`[实测]` 只做草稿登记与云同步状态，全部平铺 30 个键：`draft_id / draft_name / draft_fold_path / draft_root_path / draft_cover / draft_materials[type 0,1,2,3,6,7,8] / draft_cloud_* / draft_enterprise_info / draft_is_ai_shorts / draft_is_ai_packaging_used / draft_is_ai_translate / tm_duration / tm_draft_cloud_modified`。
设计启示：**内容（content）与索引（meta）分离**，列表页只读 meta 就能渲染草稿墙，不用加载 644KB 正文。这条必须抄。

#### 1.4.6 补充实测：草稿从 6.0 起上锁了（这条改结论）

本机原装 11.6 的真实草稿目录实测给出与上一节不同的一面：

```
%LOCALAPPDATA%\JianyingPro\User Data\Projects\com.lveditor.draft\<草稿名>\
  draft_content.json          主体（新版为单行 Base64 密文，首字节不是 '{' 也不是 '['）
  draft_info.json             同字节副本（实测 79912 = 79912）
  draft_content.json.bak      自动备份（同样是密文）
  draft_meta_info.json        清单层（同样上锁）
  draft_settings              INI：real_edit_seconds / real_edit_keys
  draft.extra                 i/e 标签的二进制壳
  timeline_layout.json        多时间轴布局
  attachment_editing.json     AI 使用台账
  agent_adoption_ledger.db    SQLite，Agent 采纳记录
  template.tmp / draft_cover
```

`[实测]` 判据：同目录里 `draft_content.json` 明文 431KB 可读，而其 `.bak` 已达 2343KB 且为密文——说明**外部工具写明文，剪映照读；剪映自己一另存就换密文**。`[第三方]` 加密开关由云端配置下发，抓到的配置键为 `draft_entryption_config:{"enable_all":true}`（原文即拼错），协议号 5.9→110、11.3→183。`[推断]` 引擎串里出现 `cipher_type` / `cipher_key` / `key_store addKey` / `decrypt_aes_v1` 与 Crypto++ 的 `Rijndael_Info` + `CTR_ModePolicy`，即 AES-CTR 家族。

对我们的直接影响（写进 第六部分的格式策略）：
1. **「明文工程」是产品决策，不是技术细节**。剪映上锁是为了堵第三方工具与防抄袭，代价是自己的文件不可 diff、不可审查、出问题只能靠 `.bak`。我们的 AVS 格式一律明文 + 规范化排序，diff 与审查是一等能力。
2. **读他人工程的适配器要认加密**。做「导入剪映草稿」功能时，明文草稿直接解析；密文稿需要用户在剪映里导出或降版本，或者走它自己的 `-open-draft-pack` 通道（见 1.7.0），不做密钥提取。
3. `attachment_editing.json` + `agent_adoption_ledger.db` 证明它**已经在记录 AI 采纳率**。我们的 `ai_decision` 表（第五部分 L3）要对齐这个思路并做厚：记录证据、候选、采纳与否。

#### 1.4.7 官方命令行入口（比 CLI 更靠底层）

`[实测]` 注册表项：

```
HKCR\JianyingPro.JYPack   → JianyingPro.exe -open-draft-pack="%1"     （扩展名 .jypack）
HKCR\JianyingPro.Media    → JianyingPro.exe -open-file="%1"
```

启动器二进制里带 `deeplink or open-draft-pack process end nRet=` 的处理串。也就是说**剪映有一个官方承认的「草稿包」通道**：把草稿打包成 `.jypack` 后用 shell 关联打开。这是比逆向 JSON 更稳的集成面——我们做「在剪映里打开我生成的草稿」时优先走这条。

### 1.5 Lyra XMLDraft：给 AI 用的工程语言（本轮最大发现）

`[实测]` 位置：`Resources\canvas_agent\skills\jianying.hub.studio_lyra_xml_timeline_builder_v2\`
协议版本：`xmldraft/v1`（current）、`xmldraft/v2`（opt_in）；schema 状态 `complete`，诊断数 `0`。

这套东西的本质：**给大模型一套受限的 XML 工程视图 + 一套受限的修改表达式**，让模型改工程而不是生成工程文件。它跟 `draft_content.json` 是两套表示，中间有编译器。

#### 1.5.1 文档骨架

```xml
<draft version="2" width="1920" height="1080" ratio="16:9"
       color_space="sdr" loudness_normalize="on">
  <cover ref="…" />                       <!-- 或 frame="1200"，二选一 -->
  <main>                                  <!-- 唯一主轨，视频/图片按文档顺序连续 -->
    <video id="v1"><time start="0" duration="6150" material_start="0"/></video>
    <image id="v2">…</image>
  </main>
  <multi>                                 <!-- 副轨容器：画中画/音频/文字/字幕/贴纸/滤镜/特效/包 -->
    <audio id="a1">…</audio>
    <text id="t1"><content><sub text="标题"/></content></text>
    <subtitle id="s1">…</subtitle>
    <sticker id="k1">…</sticker>
    <effect id="e1">…</effect>
    <filter id="f1">…</filter>
    <material_package id="mp1">…</material_package>
    <template_package id="tp1">…</template_package>
  </multi>
  <compound id="c1"><member …/></compound>   <!-- 复合片段 -->
  <compounds>…</compounds>
  <extension_action:subtitle_recognize/>     <!-- 宿主级动作：整稿字幕识别 -->
  <extension_action:lyric_recognize/>
  <extension_action:smart_highlight/>
  <extension_action:sync_video_to_sound/>
  <tracks><track id="…" type="video|audio|text|sticker|filter|effect|mixed" role="main"/></tracks>
</draft>
```

关键设计决定（`[随包文档]` `references/timeline.md`）：

| 设计 | 规则 | 为什么值得抄 |
| --- | --- | --- |
| 时间单位 | **裸毫秒，禁带单位后缀**（us/s/min 全非法） | 模型最容易写错单位；只留一种写法，解析器不必猜 |
| 时长与素材分离 | `duration` = 时间线占用时长，`material_start` = 素材入点，`speed` 独立 | 变速之后 duration 不再乘除速度，回读即真相 |
| 主轨无 start | `<main>` 内片段不写 `start`，靠文档顺序连续排 | 消除「主轨空洞」这一类非法状态 |
| 相对对齐 | `align_start_to="v1.right"` / `align_end_to="main.left"` + 正负 offset | 音乐卡点、字幕跟随不需要算绝对时间 |
| 画布 | 根节点必须成对写正整数 `width`/`height`，只写 `ratio` 判无效 | 杜绝「比例写得对但像素未知」 |
| 草稿级响度 | `loudness_normalize="on|off"` 显式声明，禁止从「有 BGM 就推断开启」 | 把审美决策与结构事实分开 |
| 派生值不入档 | 总时长是派生值，根节点没有可写的 duration | 避免写进去与算出来不一致 |

#### 1.5.2 Selection Expression：模型改工程的语言（`[随包文档]` `references/selection.md`）

不是 patch JSON，是一门**带选择器的链式修改小程序**：

```
draft.select("#t1 > content > sub").attr("text", "新标题");
draft.selectAll("text").attr("text_alignment", "center");
draft.apply();
```

- 选择器：`tag` `#id` `>` 后代 `,` 分组 `[attr=v]` `[attr*=v]` `[attr^=v]` `[attr$=v]` `:first-of-type` `:last-of-type` `:nth-of-type(n)` `:has(sel)`。
- Mutation（11 个，闭集）：`attr` / `removeAttr` / `appendXml` / `prependXml` / `beforeXml` / `afterXml` / `replaceWithXml` / `replaceChildrenXml` / `appendXmlFile` / `replaceWithXmlFile` / `replaceChildrenXmlFile` / `reorderChildrenById` / `remove` / `empty`。
- 入口两条：`draft.select()`（必须恰好命中 1 个）、`draft.selectAll()`（至少 1 个）；整稿替换 `draft.replaceWithXml(...)` 只能是第一条语句且只允许一次。
- 两条硬约束：每条语句必须以英文 `;` 结尾；每条语句必须真改东西（禁 select-only 探测）。

事务与安全设计（这套值得整段搬）：

```
target_xml  待应用缓存（模型在改的草稿）
current_xml 已落地草稿（最近一次 sync 的结果）
target_current_relation: same | different
draft.apply(); 才会把 target 落到真实草稿
```
- 失败语义：语法错/阻断错 → 不写 target，原文保留；只有标为允许警告的问题可继续。
- 版本保护：`--candidate-revision` 校验预演候选与资源契约未变；`--preview` 只回候选 XML 不落地。
- 一票否决项：整稿覆盖必须带完整替换范围状态，否则旧内容被删；`remove(` / `removeAttr` 必须显式，不许靠省略表达删除。
- 弹窗级细节：`adjust` / `hsl` 的数值 `removeAttr` 会写成 0（省略属性清不掉已应用值）。这条说明它踩过「以为删属性就是清零」的坑。

#### 1.5.3 一次改几个片段决定调用形态

`[随包文档]` 原文规则的实质：**影响 ≤ 3 个片段，一次调用写完 mutation + `draft.apply()` 直接提交；影响 > 3 个片段或用了 `selectAll`，拆成两次调用**——第一次只提交 mutation（不 apply），宿主缓存成 target_xml；核对通过后再单独 `DraftEditing({selection_expression:"draft.apply();"})`。

抄这条的理由：大模型的输出有长度上限且会漂移。**把「改」和「提交」分成两个事务**，让失败可以带状态重试，而不必重放整批。这比「生成整份工程再覆盖」健壮一个量级。

### 1.6 原生编辑命令表：200+ 条，17 个域（`[实测]`）

来源：`Resources\canvas_agent\runtime\app-server.mjs` 里冻结的命令白名单对象（含 `Set` 化的全量校验 + 一份更小的「安全子集」白名单）。

```
draft(14)        setCanvasSize setCanvasBackground setCover clearCover setDraftName setDraftId
                 setDraftUpdateTime ensureDraftCanvasSize updateDraftAIGCWatermark clearDraft
                 setDraft setAlignMode setDraftKeywordsConfigs setVideoGeneratorType
track(4)         add delete mute updateTrackName
segment(18)      move scale translate rotate updateLayout split insert delete mirror
                 setTimeRange innerReplace innerReplaceStack paste visible mute setName
                 duplicate setDescription multiSegmentsSetTimeRange
video(46)        add setMaterial setMask clearMask setOpacity setBackgroundColor
                 setBackgroundBlur setBackgroundImage clearBackground formatVideo
                 setTransition updateTransition clearTransition setFade denoiseOn denoiseOff
                 addAnimation updateAnimation deleteAnimation setSpeed pitchOn pitchOff
                 setCurveSpeed seprateAudio setMatting clearMatting reverse crop muteOn muteOff
                 setBasicColor resetBasicColor setVolume setFigure setMakeupRoot clearFigure
                 setFigureFaceId setMix setChromaColor setChromaIntensity setChromaShadow
                 setChromaEdgeSmooth setChromaSpill resetChroma applyAllChroma
                 removeSmartCrop addSmartCrop setSmartColorAdjust setStable setVideoAlgorithm
                 addDigitalHuman updateDigitalHuman updateDigitalHumanRendered
                 addObjectLocked updateObjectLocked removeObjectLocked
audio(23)        add setVolume setFade denoiseOn denoiseOff pitchOn pitchOff setVoiceEffect
                 setVoiceEffectParams clearVoiceEffect setVoiceEffectToAll
                 setVocalSeparation updateVocalSeparation removeVocalSeparation
                 setVocalBeautify updateVocalBeautify resetVocalBeautify removeVocalBeautify
                 setSpeed modifiedToneOn modifiedToneOff setMaterial addBeat removeBeat
text(14)         add setMaterials addSubtitles setFixedSize addAnimation updateAnimation
                 deleteAnimation addVideoTracker updateVideoTracker removeVideoTracker
                 deleteTextToAudioIds updateSubtitleTemplate resetSubtitleTemplate
                 updateEffect setSubtitleKeywords clearSubtitleKeywords
textTemplate(7)  add setMaterial addAnimation updateAnimation deleteAnimation
                 addVideoTracker updateVideoTracker removeVideoTracker
sticker(6)       add addAnimation updateAnimation deleteAnimation addVideoTracker
                 updateVideoTracker removeVideoTracker
effect(3)        add updateAdjustParams resetAdjustParams
filter(2)        add update
adjustment(2)    add setBasicColor resetBasicColor
keyframe(3)      add delete update
template(4)      setMutableVideos setMutableAudios setMutableTexts setTemplateMute
templateCombination(3)  templateCombinationAdd replace setSize
attachment(11)   insertAsyncTasks deleteAsyncTasks updateAsyncTasksStatus
                 insertVideoAlgorithms deleteVideoAlgorithms updateVideoAlgorithm
                 insertAiWriterInfos deleteAiWriterInfos updateAiWriterInfo
                 setAiCreatorContent updateAiCreation updateAiReel updateAiReelAgent
story(11)        deleteAiStoryAlternative addAiStoryAlternativeMaterials
                 cloneAiStoryAlternativeMaterials deleteAiStoryAlternativeMaterials
                 updateAiStoryAlternativeMaterial pinAiStoryAlternativeMaterial
                 updateMoveFeedsToAlternative updateStoryId innerReplace innerReplaceStack
                 findInnerReplaceIds
undoRedo(5)      undo redo canUndo canRedo getTopItemId resetUndoRedo
batch(3)         batchStart batchEnd freezeVideo
```

三个必须记住的结构判断：

1. **命令按「对象域.动作」组织，全部走一条总线**。这正是我们 第五部分里 Command Bus 的现成样本。
2. **它自己有一份「模型可用的安全子集」**（`IX1`）：只放 `draft.setCanvasSize`、`track.add`、`segment.split/delete/setTimeRange`、`video.add/setVolume/muteOn`、`audio.add/setVolume`、`text.add`、`undoRedo.*`、`invokeBatch` 等 26 条。全量命令表给内核与内部脚本，模型只拿到这一小片。**这是「AI 权限分级」的落地样本**。
3. `batchStart/batchEnd` + `undoRedo` 说明它把「一批改动 = 一个 undo 步」做成了显式原语。我们的命令总线要照抄这条：**一次 AI 提交 = 一个可整体撤销的事务**。

### 1.7 自动化与 Agent 内部架构（`[实测]`）

#### 1.7.1 真能调的 CLI

`jianying-agent-cli.exe --help` 实跑输出：

```
usage: jianying-agent-cli draft <fetch-feishu-doc|query-content|plan-patch|validate-patch|apply-patch> --input <json> [--output <json>]
```

五个子命令的语义（`[实测]` 字符串表 + `[推断]` 参数键）：

| 子命令 | 干什么 | 关键入参（从二进制字符串提取） |
| --- | --- | --- |
| `fetch-feishu-doc` | 拉飞书文档作文案输入 | 走 `lark-cli`（`docs +fetch`） |
| `query-content` | 读草稿内容 | `--project-id`、`input.baseRevision` |
| `plan-patch` | 生成补丁计划（不落地） | `draft_patch.operations[]` |
| `validate-patch` | 校验补丁 | 同上 + `baseRevision` |
| `apply-patch` | 落地补丁 | 需 `JY_AGENT_ALLOW_APPLY_PATCH` + `JY_AGENT_REAL_LYRA_APPLY` + 真 Lyra 运行时 |

补丁结构（`[实测]` 二进制里的字段校验串反推）：
```jsonc
{
  "schemaVersion": "…",
  "targetProjectId": "…",           // 必须与 --project-id 一致
  "runId": "…",                     // 必须与 JY_AGENT_RUN_ID 一致
  "baseRevision": 12,               // 非负整数，乐观锁
  "operations": [
    {"op":"add_track|remove_track|update_track|…","trackId":"…","trackIndex":0,
     "materialId":"…","sourceTrackId":"…","targetTrackId":"…","value":{}, "enabled":true}
  ],
  "lyraCommands": [ {"subcommand":"edit|extract", "args":["…"]} ],   // 禁止带 --ref/--minidraft
  "lyraDraftRef": "…"
}
```
环境变量门禁（`[实测]`）：`JY_AGENT_ALLOW_APPLY_PATCH`、`JY_AGENT_REAL_LYRA_APPLY`、`JY_AGENT_LYRA_CLI`、`JY_AGENT_LYRA_DRAFT_REF`、`JY_AGENT_RUN_ID`。
`lyra-cli.exe --help` 实跑返回 `{"err_code":-100015,"err_msg":"unauthorized host process"}` → **Lyra 只接受宿主进程调用，命令行直调被挡**。`[实测]`

#### 1.7.2 内部分级：Director → Editing → Flair → DraftEditing

从随包 SKILL.md 的交接语义（`[实测]`）还原出的链路：

```
用户话 → Director（目标判断/素材范围/路由）
        └→ editing_agent（剪辑执行端）
             ├→ MaterialRecall（平台资源召回：音乐/音效/字体/模板/蒙版/歌词动效）
             ├→ SegmentRecall（视频片段召回：选段+排序）
             ├→ AnalyzeAsset（素材分析：转写、镜头、画面事实）
             ├→ FlairExecute / FlairRead（资源包装执行与回读）
             └→ DraftEditing（唯一草稿写入口，吃 Selection Expression）
                  └→ Lyra 编译器 → 内核命令 → draft_content.json
        └→ editing-review（审片：证据 → 结论 → 最小返修）
```

四个工程约束（`[随包文档]`，这是整份材料里最有价值的方法论）：

1. **唯一写入口**：`DraftEditing` 是草稿唯一的写通道，模型与通用脚本都不得自己构造完整 draft 文档或做文件操作。
2. **写前必须一次读全**：模型在构造 Selection 之前，必须一次把本次会用到的所有 XML 标签、宿主、片段族、变换、扩展动作对应的规则文件全读完（`read` 全返回 `completed` 并拿到完整正文），**不许边写边读、不许用报错探测规则**。
3. **状态分级**：`staged`（只在 target 缓存，未落地）/ `applied`（已落地）/ `quarantined`（隔离保护，禁止重放同义改动）。`draft_status=staged` 期间禁止调 `SubmitResult`。
4. **失败分类**：`source_range_clamped`、`observation`、`unsupported`、`no_match`、`missing_input`、`required_resource_unavailable`。每一类有明确的「不许重试」规则——`no_match` 与 `unsupported` 不许换同义词再查。

`[随包文档]` 还有一条关于「证据边界」的规则，直接可以搬进我们的审片 Agent：**源素材分析只证明素材内容，Script 说明意图，草稿结构只能证明编排事实，只有成片音画证据才支持「实际呈现」结论**。

#### 1.7.3 工程能力清单（从 skill 目录名反推）

`Resources\canvas_agent\skills\` 下 18 个技能包，等价于它的产品能力地图：

```
script-logic                 脚本/文案逻辑（分镜、shots）
aigc-text-to-singlefilm-v2   文案直出一片
aigc-film-assets             影资（角色/场景/道具卡）
grid-image-generation        九宫格图生成
audio-voice-first            先配音后配画
audio-rhythm                 卡点/节奏
canvas-cli                   画布节点操作（hubcli canvas，含 request_id/preconditions/batch）
hub-cli                      Hub 工具入口
platform-adaptation          平台适配（画幅/时长/安全区）
brand-guidelines             品牌规范
editing-review               审片
skill-creator                技能工厂（含 skill-package-contract 规范）
jianying.hub.studio_lyra_xml_timeline_builder_v2   XML 草稿编排
jianying.hub.studio_edit_reference_recall_v2       参考片召回与规则库
jianying.hub.spoken_video_cut_packaging            口播剪辑与包装
lark-base / lark-doc / lark-shared                  飞书文档与表格
```

`[实测]` `canvas-cli` 的请求模型值得单列：每个写操作带唯一 `request_id`，带 `preconditions.targetStateToken`（乐观锁），支持 `--resume --request-id` 续跑，支持 `batch`（整批失败则全不提交）与「独立批量（允许部分成功）」两种语义。这套东西跟 1.6 的 `batchStart/batchEnd` 是一套设计的两层实现。

### 1.8 音频与语音（`[实测]`）

```
audioeffect.dll 13.4MB        音效链（EQ/压缩/混响/变声）
speechsdk.dll 7.4MB           语音识别
grow-voice-api.dll 5.2MB + growvoice_crf_cutter.exe  声音克隆/变声（云端）
Resources\rnnoise\rnnoise_v2.0.model                   RNNoise v2 降噪（端侧）
Resources\audiosami\         time_align_freq_domain / time_align_time_domain / unet_denoise_44k_music
Resources\audiomodel\ 31MB  音频模型组（8 文件）
Resources\audio_metrics\    响度/质量打分
```
判断：**降噪、去混响、人声/伴奏分离、节拍检测在端侧；声音克隆与高音质 TTS 走云**。`[实测]`+`[推断]`（依据：`rnnoise_v2.0.model` 只有 120KB，是轻量 RNN 降噪；`unet_denoise_44k_music` 250KB，是音乐降噪 U-Net 的量化版）。

### 1.9 剪映的五条可搬运结论

1. **工程双层表示**：磁盘 JSON（快、全量）+ 内存 XML 视图（给模型、给 diff、给事务）。两层之间用编译器连接，模型只见 XML。这条直接决定我们 第六部分的格式设计。
2. **命令表 + 白名单 + 批事务**：200 条命令按域组织，模型只拿到 26 条安全子集，一次 AI 提交等于一个 undo 步。
3. **端侧模型货架 + 云侧能力边界**：能端侧的全端侧，省带宽省钱且离线可用；要版权的走云。模型按能力分目录、按 100KB~30MB 分级部署。
4. **特效即参数化模板包**：`Resources\MixMode\MixMode.json` 明列 `nameId/effectId/resourceId/path` 四元组（实测例：`color_filter / 871339 / 6758325170760323597`），单包结构为 `config.json` + `content.json` + `anim.prefab` + `blend.material` + `xshader\blend.xshader`。**它没有「特效代码」这个概念，全是数据 + 着色器 + 预制体**。这条最省事：我们的包装效果也按「模板包 + 参数槽位」做，一个特效 = 一份清单 + 一批资源 + 一个参数 schema。
5. **AI 采纳率是产品指标**：`attachment_editing.json` + `agent_adoption_ledger.db` 说明它在统计「AI 给的方案人到底用没用」。我们的 `ai_decision` 表要把这个做成可查询的一等数据。

---

## 第二章 DaVinci Resolve 21.2

### 2.1 架构总览：一个 581MB 的 Qt 单体 + 一组可插拔子系统

`[实测]` 主程序 `Resolve.exe` 581MB，是静态贴了绝大部分 Qt5.15 与业务代码的单体。旁边一圈 DLL 才是可替换部件：

```
分页模块化：FusionPage.dll(11.8MB)  FairlightPage.dll(31.8MB)  （页面级动态装配）
脚本桥：    fusionscript.dll(3.55MB) fuscript.exe lua5.1.dll  ResolvePython\(python314.dll)
工程库：    qsqlite.dll / qsqlpsql.dll / libpq.dll / sqlite3.exe / quazip.dll / zip.exe
合成引擎：  fusionsystem.dll(33.9MB) fusionoperators.dll fusioncontrols.dll fusiongraphics.dll
            Plugins\*.plugin：3d alembic deepimage fbx fuses krokodove ograf opencolorio
                              openfx openvr paint particles text utilities USD
解码栈：    avcodec-60 / avformat-60 / MXF.dll / kdu_*(JPEG2000) / jpegxs / oapv
            BlackmagicRawAPI / ProResRAW / ArriImageSdk.9 / SonyRawDev / DNxSDK / fraunhoferdcp
GPU：       nvcuda / cublas / cudnn9 / cufft / nvrtc / nvngx_vsr / nvngx_truehdr / OpenCL.dll
            DecoderCUDA / DecoderOpenCL / DirectML / gpudetect / InstructionSetServicesAVX2
AI：        llama.dll + mtmd.dll + ggml-cuda.dll(125MB) + onnxruntime + openvino + torch_cpu(231MB)
音频：      FairlightPage + BMDAudioPlugins + VstScanner.exe + libsndfile + portaudio + Ambisonics
UI 桥：     Plugins\ChromiumEmbeddedFramework（Workflow Integration 的 WebView）
```

`[推断]` 判据与结论：把 Fusion 页与 Fairlight 页做成独立 DLL，说明这两页是**可独立加载/卸载的子系统**，主程序只做页面宿主与工程数据总线。这套「宿主 + 页面插件」的分法，比把每一页都编进主程序省一大截启动与内存代价。

### 2.2 脚本自动化：三层入口，一套对象模型

`[随包文档]` `Support/Developer/Scripting/README.md`（2026-08-31 更新）+ `[实测]` 目录结构：

| 入口 | 机制 | 适用 |
| --- | --- | --- |
| 内部脚本 | `Workspace > Scripts` 菜单、`Workspace > Console`、渲染前后挂钩、Fusion 工具的 Frame/Start/End Render 内嵌脚本 | 交互调试；内部变量 `resolve` `bmd` `fusion` 已就绪 |
| 本机外部脚本 | 自带解释器直连：`ResolvePython\ResolvePython.exe`（Python 3.14 定制版，`import DaVinciResolveScript` 开箱可用，不带 pip/TK/IDLE）、`fuscript.exe`（LuaJIT 5.1） | 批处理、外部工具链 |
| 自备解释器 | Python ≥3.6 64bit + 环境变量 `RESOLVE_SCRIPT_API` / `RESOLVE_SCRIPT_LIB` / `PYTHONPATH` → `Modules\DaVinciResolveScript.py` | 已有 Python 工程集成 |
| 局域网 | Studio 版监听 **1144** 端口（IANA 注册），回连端口动态分配在 49152..65535 | 农场/多机 |
| 无头 | `Resolve.exe -nogui`：UI 关闭，脚本 API 照常 | 服务端渲染 |
| 插件内脚本 | Workflow Integration（Electron + JS）：插件里 `resolve` / `project` 变量自动注入 | 面板型集成 |

`[实测-失败]` 隔离副本上 `Resolve.exe -nogui` 启动即退出、1144 未监听。判据：`msiexec /a` 展开的是文件树，缺首次初始化的 `ProgramData` 与授权状态。这条记为「本副本上没跑通」，官方文档写明 `-nogui` 支持脚本，正式安装环境要重测。

### 2.3 API 面清点：22 个类，530 个方法（`[实测]`）

解析 `DaVinciResolveScript.pyi`（3645 行 / 163KB，2026 年版）得到的确切数字：

| 类 | 方法数 | 关键方法（节选原文） |
| --- | ---: | --- |
| `Resolve` | 50 | `GetProjectManager` `GetMediaStorage` `Fusion` `OpenPage` `GetCurrentPage` `GetVersion` `IsStudio` `GetExtrasPackages` `InstallExtrasPackage` `GetEffectsList` `GetKeyframeMode/SetKeyframeMode` `ValidateDCTL` **`EncryptDCTL`** `SetHighPriority` `Quit` |
| `ProjectManager` | 27 | `LoadProject` `CreateProject` `SaveProject` `ImportProject` `ExportProject` `ArchiveProject` `RestoreProject` `GetDatabaseList` `SetCurrentDatabase` `CreateCloudProject` |
| `Project` | 67 | `GetMediaPool` `GetCurrentTimeline` `SetCurrentTimeline` `AddRenderJob` `StartRendering` `StopRendering` `SetRenderSettings` `GetRenderFormats` `GetRenderCodecs` `SetCurrentRenderFormatAndCodec` `InsertAudioToCurrentTrackAtPlayhead` `ExportCurrentFrameAsStill` `RefreshLUTList` `AddColorGroup` + 6 个 AI 状态查询（`GetTranscribeAudioStatus` `GetAnalyzeForSlateStatus` `GetSmartReframeStatus` `GetDetectSceneCutsStatus` `GetCreateSubtitlesFromAudioStatus`）`GenerateSpeech` |
| `MediaPool` | 32 | `ImportMedia` `AppendToTimeline` `CreateTimelineFromClips` `CreateEmptyTimeline` `ImportTimelineFromFile` `RelinkClips` `AutoSyncAudio` `CreateMulticamClip` `CreateStereoClip` `GetClipMatteList` |
| `MediaPoolItem` | 49 | `GetClipProperty` `SetClipProperty` `GetMetadata` `SetMetadata` `GetAudioMapping` `SetAudioMapping` `TranscribeAudio` `GetTranscription` `SetTranscription` `PerformAudioClassification` `AnalyzeForIntellisearch` `AnalyzeForSlate` `RemoveMotionBlur` `MonitorGrowingFile` `ReplaceClip` |
| `Timeline` | 70 | `AddTrack` `DeleteTrack` `SetTrackEnable` `SetTrackLock` `GetItemListInTrack` `MoveItems` `DeleteClips` `DeleteGaps` `SetClipsLinked` `CreateCompoundClip` `CreateFusionClip` `InsertFusionCompositionIntoTimeline` `InsertOFXGeneratorIntoTimeline` `Export` `GrabStill` `NormalizeAudioLevel` `AutoAlignClips` `DetectSceneCuts` `CreateSubtitlesFromAudio` `GetNodeGraph` `SetVoiceIsolationState` `SetOutputBlanking` |
| `TimelineItem` | 110 | `AddTransition` `AddFusionComp` `ExportFusionComp` `ImportFusionComp` `AddEffect` `SetSpeed` `SetCDL` `CopyGrades` `ApplyAutoColor` `AddTake` `CopyAttributes` `CreateMagicMask` `RegenerateMagicMask` `Stabilize` `SmartReframe` `ExportLUT` `GetNodeGraph` `SetProperties`（含 `ZoomX/ZoomY/Pan/Tilt/RotationAngle/Crop*` 一整套）`SetFades` `RippleDeleteSilence` `PerformMulticamSmartSwitch` `FlattenMulticam` `SetPosition` `GetLinkedItems` |
| `Graph` | 15 | `GetNumNodes` `SetLUT` `GetLUT` `SetNodeCacheMode` `SetNodeLabel` `SetNodeColor` `GetToolsInNode` `SetNodeEnabled` `ApplyArriCdlLut` `ApplyGradeFromDRX` `ResetAllGrades` |
| `MediaStorage` | 11 | `GetMountedVolumeList` `GetFileList` `AddItemListToMediaPool` `StartCloneMedia` `SetCloneToolSettings` `GetCloneStatus` |
| `Gallery` / `GalleryStillAlbum` | 8 / 6 | `CreateGalleryStillAlbum` `CreateGalleryPowerGradeAlbum` `ImportStills` `ExportStills` |
| `Folder` | 14 | `GetClipList` `Export` `TranscribeAudio` `AnalyzeForIntellisearch` `RemoveMotionBlur` |
| `ColorGroup` | 6 | `GetPreClipNodeGraph` `GetPostClipNodeGraph` |
| `Effect` | 6 | `GetInfo` `GetFusionComp` `SetIndex` |
| `PhotoAlbum` / `PhotoAlbumItem` | 11 / 48 | 静态照流程（21 版新增，含 `Crop*` `RotationAngle` `GetRatings`） |
| `Fusion` | — | 通向 Fusion 全部脚本能力（节点、表达式、UIManager） |

**这张表的价值不只是「能调什么」，而是「一个专业 NLE 的脚本接口该长什么样」**：
- 官方把 `TimelineItem` 摆成最肥的类（110 个方法），剪辑操作的重心确实在片段层，不在轨道层（`Timeline` 70 个）。
- 关键帧、版本、Take、颜色分组、节点图都是**一等对象**，不是元数据。
- 渲染是 **job id 制**（`AddRenderJob` → `StartRendering(ids)` → `GetRenderJobStatus(id)`），索引制的老接口已标为不再支持。
- 所有 `Get/Set` 都是 **key-value 字符串字典**（`GetSettings()` / `SetSettings({...})`），跟 UI 参数名一一对应。这套「设置即字符串字典」的做法，落地成本极低。

### 2.4 工程存储：SQLite 库 + `.drp` 是 ZIP 包 XML（`[实测]`）

#### 2.4.1 磁盘库

`[实测]` `sqldrivers\qsqlite.dll` + 自带 `sqlite3.exe` + `qsqlpsql.dll` + `libpq.dll`：
- 本地库走 SQLite；协作/多机走 PostgreSQL。
- 自带 `sqlite3.exe` 意味着**官方允许直接开工程库做只读分析**（分析工具就靠它）。
- `ProjectManager.GetDatabaseList()` / `SetCurrentDatabase()` 说明库是可切换的多库模型；`ArchiveProject()` / `RestoreProject()` 是整库快照级操作。

#### 2.4.2 `.drp` 拆包结果

`[实测]` 用随包 `Fuse.drp`（29,564 字节）拆包：

```
PK..  → ZIP 容器
  project.xml                        8,149 B
  MediaPool/Master/MpFolder.xml    171,466 B
  SeqContainer/c9dd78a8-….xml       24,124 B
  Gallery.xml                        8,917 B
```

`[实测]` `project.xml` 骨架：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--DbAppVer="19.1.1.0004" DbPrjVer="14"-->
<SM_Project DbId="88795a03-…">
 <FieldsBlob>00000001 00000006 …（二进制属性块）</FieldsBlob>
 <User>…</User> <ProjectName>Fuse</ProjectName>
 <TimelineVec/> <TimelineHandleVec><Element>3c211a78-…</Element></TimelineHandleVec>
 <CurrentTimelineIndex>0</CurrentTimelineIndex>
 <NumTotalStreams>1</NumTotalStreams> …（播放流与 gang 状态）
 <CommonConfig><SM_Config DbId="…"><FieldsBlob>…压缩块…</FieldsBlob></SM_Config></CommonConfig>
```

`[实测]` `SeqContainer/<uuid>.xml` 骨架（时间轴本体）：
```xml
<Sm2SequenceContainer DbId="c9dd78a8-…">
 <FieldsBlob/>
 <VideoTrackVec><Element>
   <Sm2TiTrack DbId="498a1758-…">
     <Type>0</Type><SubType>0</SubType><Flags>0</Flags>
     <Sequence>82eb0fb8-…</Sequence>
     <Items><Element>
       <Sm2TiVideoClip DbId="c34373d8-…">
         <PrettyType>Fusion Title</PrettyType><Name>Fusion Title</Name>
         <Start>86400</Start><Duration>120</Duration>
         <Flags>0</Flags><PriorityIndex>0</PriorityIndex>
         <CompositionTable><Sm2TiCompositionTable DbId="…">
           <DbSavedTime>12307889426</DbSavedTime>
           <CompositionBA>…压缩/编码块…</CompositionBA>
         </Sm2TiCompositionTable></CompositionTable>
       </Sm2TiVideoClip>
     </Element></Items>
   </Sm2TiTrack>
 </Element></VideoTrackVec>
</Sm2SequenceContainer>
```

三条硬事实：
1. **工程层 XML 明文，内容层二进制**。轨道、片段、起止、名称、类型全是可读 XML；特效/合成/参数被打进 `FieldsBlob` / `CompositionBA` 这类编码块。这是「结构可读 + 内容防手改」的分层。
2. **时间以帧计数，带偏移基线**。`Start=86400`、`Duration=120`；86400 帧在 24fps 下 = 3600 秒，说明它不是从 0 起算的裸帧号，而是带时间基线（首帧偏移）。`[推断]` 判据：Resolve 的序列起点惯例是 `01:00:00:00`（1 小时），86400/24 = 3600 秒正好对上。
3. **对象全部有 UUID（`DbId`）**，引用靠 UUID 而不是数组下标。这是它能做多库合并、协作同步、`.drt` 模板套用的底层前提。

`[随包文档]` 导出类型枚举（`TimelineExportType`）一次性把它的交换能力摊开了：
```
EXPORT_AAF  EXPORT_DRT  EXPORT_EDL  EXPORT_FCP_7_XML
EXPORT_FCPXML_1_8 / 1_9 / 1_10
EXPORT_HDR_10_PROFILE_A / _B
EXPORT_TEXT_CSV  EXPORT_TEXT_TAB
EXPORT_DOLBY_VISION_VER_2_9 / _4_0 / _5_1
EXPORT_OTIO  EXPORT_ALE  EXPORT_ALE_CDL
```
**它把 OTIO 当成一等导出格式**。这条直接影响我们的格式策略：AVS 必须能无损映射到 OTIO（见 第六部分 5 节）。

### 2.5 Fusion：节点引擎 + 三种扩展语言

`[实测]` `Plugins\*.plugin` 是 Fusion 的模块化二进制（`fuses.plugin` 156KB 是 Fuse 运行时，`openfx.plugin` 337KB 是 OFX 宿主，`krokodove.plugin` 1.9MB 与 `ograf.plugin` 1.19MB 是第三方节点包内联）：

#### 2.5.1 Fuse：Lua 写的原生节点

`[实测]` 随包 16 个示例（`Developer\Fusion Fuse\*.fuse`），`Example 1 Bright Contrast.fuse` 的真实结构：

```lua
FuRegisterClass("ExampleBrightContrast", CT_Tool, {
    REGS_Name = "Ex1 Bright Contrast",
    REGS_Category = "Fuses\\Examples",
    REGS_OpIconString = "E1BC",
    REG_Version = 1,
})
function Create()
    InBright = self:AddInput("Brightness","Brightness",{
        LINKID_DataType = "Number", INPID_InputControl = "SliderControl",
        INP_MaxScale = 1.0, INP_MinScale = -1.0, INP_Default = 0.0 })
    InImage = self:AddInput("Input","Input",{ LINKID_DataType="Image", LINK_Main=1 })
    OutImage = self:AddOutput("Output","Output",{ LINKID_DataType="Image", LINK_Main=1 })
end
function Process(req)
    local img = InImage:GetValue(req)
    local m = ColorMatrixFull()
    m:Offset(bright,bright,bright,0)
    m:Offset(-0.5,-0.5,-0.5,-0.5) m:Scale(c,c,c,1) m:Offset(0.5,0.5,0.5,0.5)
    m:RGBtoYUV() m:Scale(1,sat,sat,1) m:YUVtoRGB()
    OutImage:Set(req, img:ApplyMatrixOf(m,{}))
end
```

节点模型的三件事，一条 `.fuse` 全给出：`RegisterClass` 注册元数据 → `Create()` 声明输入输出（`LINK_Main=1` 标主图输入）→ `Process(req)` 里按 request 取图、算、写回。还有 `GPU sample.fuse`（GPU 分支）、`Modifier Fuse.fuse`（非图像类节点）、`Example 8 Meta Time Burn.fuse`（写元数据）。

**这套「Lua 声明 UI + Process 处理图像」的插件模型，是我们要抄到手的最省事的特效扩展协议**：比 C++ ABI 稳定，比脚本宿主快（Lua 只做编排，像素计算落在内置算子）。

#### 2.5.2 DCTL：C 风格像素着色器（`[随包文档]` `Developer\DaVinciCTL\README.txt`）

```c
__DEVICE__ float3 transform(int p_Width,int p_Height,int p_X,int p_Y,
                            float p_R,float p_G,float p_B)
{
    const float3 result = AcesOutputTransform(p_R,p_G,p_B);
    return result;
}
```
- 两种形态：`transform()`（单片段逐像素）、`transition()`（双片段混合，带 `p_FromTex*` / `p_ToTex*`）。
- 类型系统：`float2/3/4`、`__TEXTURE__`、`__CONSTANT__` / `__CONSTANTREF__`、`_tex2D()` 随机采样。
- 全局只读量：`TIMELINE_FRAME_INDEX`、`RAND(seed)`、`_ceilf/_floorf`、`_ldexp`。
- **加密分发**：`.dctl` → `.dctle`（可设到期日）；脚本层有 `Resolve.ValidateDCTL` / `Resolve.EncryptDCTL` 两个 API。这是「插件作者靠 DCTL 卖效果」的商业闭环，我们做插件市场时照这个做。
- ACES 支持到 2.0：`DEFINE_ACES_PARAM`（V1，含 `Y_MIN/Y_MID/Y_MAX/DISPLAY_PRI/LIMITING_PRI/EOTF/…`）与 `DEFINE_ACES_V2_PARAM`（`PEAK_LUMINANCE/LINEAR_SCALE_FACTOR/LIMITING_PRI/ENCODING_PRI/EOTF/IS_SCALE_WHITE`），可直接放进 `ACES Transforms\IDT|ODT` 变成 IDT/ODT。

#### 2.5.3 OFX：宿主契约（`[随包文档]` `Developer\OpenFX\README.txt`）

- 随包 OFX 1.4 头 + C++ 包装 + 5 个样例（Gain / TemporalBlur / DissolveTransition / RandomFrameAccess / …）。
- 三种上下文：`eContextFilter`（单输入滤镜）、`eContextTransition`（双输入 + `Transition` 参数）、生成器。
- GPU 三后端各自的入口：`processImagesCUDA` / `processImagesOpenCL` / `processImagesMetal` / `multiThreadProcessImages`。
- 装到 `C:\Program Files\Common Files\OFX\Plugins`；Windows ARM64 宿主按 `Win-arm64x` → `Win-arm64ec` → `Win64` 顺序扫。
- `p_Desc.setSupportsCudaStream(true)` 表明宿主可传 CUDA stream；`setNoSpatialAwareness(true)` 表明该效果与邻域无关（可进 LUT 合批）。

**OFX 是最划算的生态接入点**：写一次，Resolve / Natron / Nuke / Vegas / Bash 都能吃。我们的特效系统做成 OFX 1.4 宿主，第一年就白拿几百个现成效果。

### 2.6 调色与色彩管理

`[实测]` `OpenColorIO_2_5.dll` + `Plugins\opencolorio.plugin` + `CanonLUTs\` + `Fusion\LUTs\` + `ROMM RGB.icc` / `USWebCoatedSWOP.icc`（`AfResources` 里带印刷级 ICC）。

`[随包文档]` 设置族的键直接反映色彩管线的分层：
- 项目级：`colorScience`（DaVinci YRGB / DaVinci YRGB Color Managed / ACEScc / ACEScct）、ACES 版本、IDT/ODT 选择。
- 片段级：`SetCDL`、`Graph.SetLUT(nodeIndex, path)`、`MediaPoolItem.GetClipProperty('Color Space')`。
- 节点级：`Graph` 15 个方法里一半是节点标签/颜色/缓存/使能，说明**调色节点是脚本可控的一等对象**。
- 缓存：`SetNodeCacheMode(cache_value)` 对应 `resolve.CACHE_*`，节点级缓存开关能脚本化。

`[推断]` 判据：既带 OCIO 2.5 又自带 ACES DCTL 实现，ACES 走的是「自己的 DCTL + 参考 ampa/aces-dev」，不是简单调用 OCIO 的 ACES config。这解释了为什么 DCTL 能做自定义 IDT/ODT。

### 2.7 Fairlight 音频

`[实测]`
```
FairlightPage.dll 31.77MB     独立页面模块
BMDAudioPlugins.dll 9.1MB     内置效果
VstScanner.exe + VstScanner     VST3 扫描（进程外，防宿主被插件拖死）
libsndfile / portaudio / soxr  音频 IO 与重采样
AmbisonicsBridge / AudioVividBridge / DolbyAtmosBridge / ImmersiveAudioBridge
                              （全景声与三维声桥：ADM/BWF 输出）
VoiceIsolation.dll 2.17MB      端侧人声分离
```
`[推断]` 判据：三个 Bridge DLL 分别对应 Ambisonics、Audio Vivid（中国三维声标准）、Dolby Atmos，说明 Fairlight 的沉浸式音频输出是**接第三方编码器**，不是自研编码。我们做三维声也可以走同样的桥接策略。

### 2.8 AI：端侧推理栈完整内嵌（`[实测]`）

这是 Resolve 21 最值得注意的架构变化：

```
llama.dll + mtmd.dll + ggml-cuda.dll(125MB) + ggml-base/cpu
   → 端侧 LLM 推理 + 多模态（mtmd = multimodal text-to-media 支持，能喂图/帧）
onnxruntime.dll + openvino.dll + openvino_intel_gpu_plugin.dll
   → 传统 CV / 音频模型
torch_cpu.dll(231MB) + torch.dll + cudnn_9 全家桶(约 1.3GB) + cublas/cufft
   → 神经网络推理（Magic Mask / Super Scale / Relight / Voice Isolation 这类大模型）
opencv_core/imgproc/dnn/video/optflow/ximgproc/...
   → 跟踪、光流、传统 CV
```
`[推断]` 判据：`llama.dll` 与 `mtmd.dll` 同目录、且没有独立的大模型权重文件 → 模型按需下载（对应 `Resolve.GetExtrasPackages()` / `InstallExtrasPackage(name)` 这套 **Extras 包机制**）。`[随包文档]` 印证：README 明写 ``AnalyzeForIntellisearch`` 需要“AI IntelliSearch - Faster / Better”包、`GenerateSpeech` 需要“AI Speech Generator”包、扩展语言转写要额外语言模型，全部通过 Extras Download Manager 安装并可脚本安装。

这套设计值得整段抄进 AI Video Studio：

| 机制 | 做法 | 好处 |
| --- | --- | --- |
| 能力包化 | 每个 AI 能力 = 一个可下载包（含模型 + 依赖） | 安装包不膨胀；按需付费/授权 |
| 脚本可控 | `GetExtrasPackages` / `InstallExtrasPackage` / `UninstallExtrasPackage` | CI 与运维能自动化 |
| 能力探测 | 缺包时 API 返回 False + 错误信息；`IsStudio()` 区分版本 | 前端能优雅降级 |
| 异步状态查询 | 每个 AI 任务一个 `Get*Status()` | 长任务不阻塞 UI |

### 2.9 Workflow Integration SDK：Electron 面板（`[实测]`）

```
Examples\SamplePlugin\
  manifest.xml       <Plugin><Id>com.blackmagicdesign.resolve.sampleplugin</Id>
                     <Name>Sample Plugin</Name><Version>1.0</Version>
                     <FilePath>main.js</FilePath></Plugin>
  main.js            主进程：创建 BrowserWindow，加载 WorkflowIntegration.node
  preload.js         暴露受限 API 给渲染进程
  renderer.js        面板逻辑（调用 window.WorkflowIntegration.*）
  WorkflowIntegration.node 388KB   原生桥（拿当前工程/时间轴/执行脚本）
  package.json / index.html / css / img
```
三种样例（`SamplePlugin` / `CompatibleSamplePlugin` / `SamplePromisePlugin`）分别演示回调式、兼容模式、Promise 式三套 JS 调用风格。安装位置与 `resolve` 变量注入由宿主负责，插件里 `resolve` / `project` 直接可用（`[随包文档]`）。

对我们的意义：**外部 Agent 面板不需要自研 WebView 集成**，照这个 manifest + preload + 原生桥的三件套做，Electron/WebView 面板就能直接调宿主 API。

### 2.10 渲染与交付

`[实测]`/`[随包文档]`：
- 渲染 job 模型：`AddRenderJob` → 设置 `SetRenderSettings({...})` → `StartRendering([jobId...])` → `GetRenderJobStatus(jobId)`；`IsRenderingInProgress` / `StopRendering`。
- 渲染前后挂钩脚本：Deliver 页 Advanced Settings 里能挂 start/end 脚本，脚本里能拿到 `job ID` / `status` / `render errors`（`[随包文档]` `8_slack_notification_by_render_job.py`）。
- 快速导出：`SetQuickExportEnabledForRenderPreset` / `RenderWithQuickExport` / `GetRenderWithQuickExportStatus`（同步/异步两套）。
- 编解码清单可查：`GetRenderFormats` / `GetRenderCodecs` / `GetAudioRenderFormats` / `GetAudioRenderCodecs`。
- 交付元数据：Dolby Vision 版本化导出（2.9 / 4.0 / 5.1）、HDR10 Profile A/B、ALE/CDL、DCP（`fraunhoferdcp` + `kdu`）。

### 2.11 达芬奇的四条可搬运结论

1. **工程 = 明文结构 + 二进制内容 + UUID 引用**。结构可读（能 diff、能脚本、能手改），内容防手改（合成/特效打包），引用用 UUID（能合并、能套模板）。
2. **脚本 API 的重心在片段层**：`TimelineItem` 110 个方法就是最好的接口设计参考；渲染走 job id；设置走字符串字典。
3. **扩展四条腿**：Lua（Fuse，节点）、C 着色器（DCTL，像素）、C++（OFX，跨宿主）、Electron（Workflow Integration，面板）。四条腿各管一段，互不挤占。
4. **AI 能力包化 + 脚本可管**：能力即包，包可脚本安装，缺包可探测，任务可查状态。

### 2.12 与官方 21 版手册交叉核对后的补正

本地随包文档与官方 4444 页参考手册对完之后，四条要修正或补强：

| 项 | 本地随包文档 | 官方手册（21 版） | 结论 |
| --- | --- | --- | --- |
| 无头启动 | `Scripting/README.md` 写 `Resolve.exe -nogui` | 手册写 `Resolve.exe -rr`（Remote Rendering 守护；macOS `./Resolve -rr`，Linux `/opt/resolve/bin/resolve -rr`） | 两个开关都存在，用途不同：`-nogui` 关 UI 跑脚本，`-rr` 起远程渲染守护。两者都记 |
| 工程产物 | 只提到导入导出工程 | 四类：`.drp` 单工程（默认连静帧与 LUT 一起打包）、`.drb` 媒体池 bin、`.drt` 单时间线模板、`.resolve.backup` 库备份、`.resolvedbkey` 网络库钥匙（XML） | 补齐 |
| 库后端 | `GetDatabaseList` / `SetCurrentDatabase` | `DbType` 取 `'Disk'` 或 `'PostgreSQL'`，`IpAddress` 缺省 127.0.0.1；网络库跑在 Project Server + PostgreSQL 上，默认账号 `postgres` / `DaVinci`，Optimize = vacuum + 重建索引 | `[推断]` Disk 库就是 SQLite 系文件库（本机实测的 `qsqlite.dll` 与自带 `sqlite3.exe` 支撑这条） |
| Fusion comp 的存储 | — | comp 随工程存进 `.drp`；单独导出 `.comp` 只带节点树，`MediaIn`→`Loader`、`MediaOut`→`Saver` 自动转换重链 | 补齐。这条说明 `.drp` 里那些 `CompositionBA` 就是 Fusion comp 的序列化体 |

再补三条对我们直接有用的事实：

1. **`.otioz` 是「时间线 + 全部媒体」的 zip 单包**，导入时自解压到同目录；`.otio` 是 JSON，顶层 `"OTIO_SCHEMA": "Timeline.1"`，时间用 `RationalTime`。官方给的口径：Resolve 之间互传用 `.drt` 最稳，跨应用优先 `.otio`/`.otioz`，其次 XML 或 AAF。`[官方文档]`
2. **Fuse 与 DCTL 的安装位置就是功能开关**：`.fuse` 放 `…/DaVinci Resolve/Fusion/Fuses`，即时编译；DCTL 当 LUT 用，主入口 `__DEVICE__ float3 transform(float p_R,float p_G,float p_B)`，内建函数带下划线前缀（`_fabs`/`_powf`/`_saturatef`）。`[官方文档]`
3. **Fairlight 的硬限制**：FlexBus 插件不限量，旧 Fixed Bus 上限 480 条；VST3 在 macOS/Windows 可用，Linux 不可用；导 Pro Tools 时 FairlightFX/EQ/压缩/变调/Elastic Wave 全部不导出不烘焙，音量自动化与 iXML 照导。`[官方文档]`

最后一条值得单独盯着：`[第三方研究]` 有资料称 **Resolve Studio 21.1 起自带原生 `ResolveMCP`（stdio，8 个工具）**。若成立，意味着达芬奇已经把「被外部 Agent 编排」做成官方能力——这条我们这条路线（第五部分 L12）不是独家，得靠工具面深度（22 个工具、完整剪辑语义）拉开差距。该说法我没有在官方页面直接核实，标 `[未证实]`，列入待验证。

---

## 第三章 After Effects 27.0

> 本机未安装 AE（Adobe 不提供免登录离线包，官方渠道是 CC 桌面应用登录下载，见 `README_工程说明.md` 第 3 节）。本章全部结论来自公开一手资料：docsforadobe 官方脚本/SDK 文档、`AdobeDocs/uxp-after-effects`、Adobe-CEP 官方仓库、`aerender -help` 原文、lottie-docs 的 AEP 字节级字段表、两个可直接读源码的开源解析器。原始抓取记录见 `_research\R2_AE内部结构与自动化调研.md`（357 行，每条带 URL 与证据标签）。

### 3.1 三层结构：宿主 + 两条 SDK 腿 + 三层脚本皮

```
AE 宿主（闭源，单进程，Windows/macOS）
├─ 效果插件层  PF_Effect  ← ae_effect.h，PF_Cmd_* 选择器，PF_InData/PF_OutData
│                └─ Windows 落地为 .aex（带 PiPL 资源），装到 PluginInstallPath
├─ 通用插件层  AEGP      ← AEGP_*Suite 家族，能操工程、挂菜单、听消息
│                └─ AEGP_ColorSettingsSuite5（OCIO）、AEGP_StreamSuite7、AEGP_LayerSuite9、AEGP_CompSuite13
├─ IO 层       AEIO / Artisans / Mercury Transmit
└─ 脚本皮
   ├─ ExtendScript（JSX，ECMA-262 3rd + E4X，可编 .jsxbin）
   ├─ CEP 面板（Chromium + Node，evalScript 转发 JSX）
   └─ UXP 面板（require("aftereffects") 直调对象模型，官方文档正文标 beta）
```

`[官方文档]` 判据：效果插件收 `PF_Cmd_*`，`PF_InData.appl_id` 在 AE 里是 `FXTC`、在 Premiere 里是 `PrMr`——同一个插件二进制能被两个宿主加载，靠的就是这层选择器协议。`[官方文档]` AEGP 的 suite 版本号是逐年加方法（26.5 SDK 加 `AEGP_GuideSuite1/2`、`AEGP_ItemViewSuite2`、`AEGP_CompSuite13`），说明**它用「版本化 suite 结构体」做 ABI 兼容**，旧插件不重编继续能用。

### 3.2 `.aep` 工程格式：RIFX 二进制，字段级可解析

#### 3.2.1 容器

```
offset 0   'RIFX'                     ASCII，RIFF 的大端变体
offset 4   uint32 file_size
offset 8   'Egg!'                     格式标识
offset 12  chunk 序列
           chunk = 4 字节 ASCII 标识 + uint32 长度 + 数据（奇数补 1 字节 padding）
           LIST = 4 字节子类型标识 + 嵌套 chunk
整数一律大端
```
`[第三方研究]` 两侧独立佐证：`boltframe/aftereffects-aep-parser` 的 Kaitai 定义（含 `padding: if: (block_size % 2) != 0`）与 lottie-docs 的 AEP 章节（`It should always be RIFX format … The format identifier for AEP is Egg!`）。

RIFX 数据结束后**尾部还挂一段 XMP（XML）**，记录 AE 版本与创建/修改时间。`[第三方研究]`

#### 3.2.2 关键 chunk 表（可据此写解析器）

| chunk | 层级 | 关键字段 |
| --- | --- | --- |
| `LIST Egg!` | 根 | 整个工程 chunk 树 |
| `head` | 头 | 前 6 字节 AE 版本指纹；`uint16` File Revision，**每次保存 +2** |
| `LIST Fold` / `LIST Sfdr` | 文件夹树 | 内含 `LIST Item` 序列 |
| `LIST Item` | 一个工程项 | `idta`(ID+类型) + `Utf8`(名字) + `cmta`(注释) + 类型专属 chunk |
| `idta` | 项标识 | 项 ID + 类型：`1` 文件夹、`4` 合成、`7` 素材 |
| `cdta` | 合成 | X/Y Resolution(u16)、Time Scale(u16)、Playhead、In/Out、Comp duration、Color(24bit)、Flags、Width/Height(u16)、Pixel Ratio(u32×2)、Framerate(u16)、Shutter Angle/Phase、Samples Limit、Samples per frame |
| `LIST Layr` | 一个图层 | `ldta` + `Utf8` + `cmta` + `LIST tdgp` |
| `ldta` | 图层 | Layer ID(u32)、Quality(u16)、Start Time(s16)、In/Out、Attributes(3B)、Source ID(u32)、Label、Name(32B string0)、Matte Mode、Layer Type(u8)、Parent ID(u32)、Matte Layer ID(u32，AE≥23) |
| `LIST tdgp` | 属性组 | `tdsb`(flags) + `tdsn>Utf8`(名) + 属性序列 + `tdmn`=`ADBE Group End` |
| `LIST tdbs` | 属性定义 | `tdb4`(类型/维数/是否动画) + `cdat`(静态值) 或 `LIST list`(关键帧) + `Utf8`(**表达式代码**) |
| `lhd3` / `ldat` | 关键帧 | `ldat` 元素大小 = `ldat长度 / lhd3计数` |
| `opti` / `sspc` | 素材 | 素材类型在前 4 字节 / 素材宽高 |
| `LIST CLRS` | 色彩 | `Utf8` 里是 JSON（含 base64 的 ICC profile） |
| `LIST shap` / `shph` / `shap` | 形状 | 形状图层与路径数据 |

#### 3.2.3 时间与关键帧的编码（抄这套要谨慎，它是历史包袱）

- 时间值是 `uint16`，按 `cdta.time_scale` 缩放：`frames = value / time_scale`；图层的 `ldta.start_time` 是额外偏移。`uint16` 上限 65535，这是 AE 当年 16 位时代的遗产——**我们现在用 int64 微秒，不背这个包袱**。
- 关键帧公共头：1 字节保留 + Time(2) + 2 字节保留 + Ease Mode(1: `1`Linear/`2`Ease/`3`Hold) + Label(1) + Attributes(1)。
- 多维属性关键帧体 = `float64[n]` 五段：Value / In Speed / In Influence / Out Speed / Out Influence。
- Attributes 里带 Continuous Bezier、Auto Bezier、Roving across time 三个位。
- 颜色按 ARGB float，范围 [0,255]。

#### 3.2.4 `.aepx`：AE 自己的 XML 工程

`[第三方研究]` AE 能把工程另存为 XML 工程 `.aepx`，结构等同 RIFX：`<string>` 取代 `Utf8`，RIFX 的 `LIST` 变成有子元素的节点，二进制数据 hex 编码进 `bdata` 属性，XMP 变成 `ProjectXMPMetadata` 元素。

对我们的用处：**模板注入走 `.aepx`（文本级改参数），静态审计走 `.aep`（字段级）**。`[推断]`

#### 3.2.5 开源解析器现状（能直接借的）

| 仓库 | 语言 | 能力 | 边界 |
| --- | --- | --- | --- |
| `boltframe/aftereffects-aep-parser` 132★ | Go | 静态只读解析 .aep，仓库自带 Kaitai 定义 + 样本 .aep | 表达式不求值、不渲染 |
| `forticheprod/py-aep` 87★ | Python3 | **读 + 写**：建空工程、建合成/文件夹/图层（solid/null/shape/text/camera/light/参数化网格）、加删关键帧（含遮罩路径/源文本/标记/渐变）、改渐变与渲染/输出模块设置、管理渲染队列、色彩管理 | 不求值表达式、不渲染像素、不碰选中态与运行期状态 |
| `actumn/aepx.js` 42★ | Node | .aepx → JSON | 已标 Deprecated |
| `Jam3/ae-to-json` | JSX+Node | 在活 AE 里跑 JSX 导 JSON | 依赖运行中的 AE |
| `virtualritz/dot-aep` / `yueli-fx/aep-reader` | Rust | 只读 | star 少，字段覆盖未知 |
| `daveowenatl/AepSharp` | C# | boltframe 的 C# 移植 | 同上 |

`py-aep` 的能力清单里有一句最值钱：**它能改 ExtendScript 摸不到的渐变、渲染设置、3D 渲染器选项、输出模块设置**。也就是说「静态改工程」这条路在参数面上比脚本更宽。

### 3.3 自动化体系：三层皮 + 一个命令行 + 两条 SDK

#### 3.3.1 ExtendScript 的真实能力与边界（`[官方文档]` 逐条核对）

能做的（原文方法名）：
```
建合成      items.addComp(name,w,h,pixelAspect,fps,duration)
建图层      layers.addSolid/addText/addBoxText/addCamera/addLight/addNull/addShape/
            addParametricMesh/precompose
关键帧      Property.addKey / setValueAtKey / removeKey / keyTime / keyValue /
            nearestKeyIndex / setInterpolationTypeAtKey / setTemporalEaseAtKey /
            setSpatialTangentsAtKey / setTemporalContinuousAtKey / setRovingAtKey
表达式      Property.expression / expressionEnabled / expressionError / canSetExpression
3D 与相机   AVLayer.threeDLayer / CompItem.activeCamera / addCamera / addLight /
            calculateTransformFromPoints / compPointToSource
父子级      Layer.parent / setParentWithJump
轨道遮罩    AVLayer.trackMatteType / trackMatteLayer / setTrackMatte / removeTrackMatte
混合模式    AVLayer.blendingMode
时间重映射  AVLayer.timeRemapEnabled
代理        AVItem.setProxy / setProxyWithSequence / setProxyWithSolid /
            setProxyWithPlaceholder / setProxyToNone / useProxy
渲染队列    project.renderQueue.items.add(comp) / item.applyTemplate / outputModule(1).file /
            renderQueue.render()（阻塞到渲完）/ pauseRendering / stopRendering / queueInAME
应用开关    app.beginSuppressDialogs/endSuppressDialogs / beginUndoGroup/endUndoGroup /
            executeCommand(id) / findMenuCommandId(text) / purge / scheduleTask /
            watchFolder / setMultiFrameRenderingConfig / availableGPUAccelTypes /
            memoryInUse / onError / exitAfterLaunchAndEval / exitCode
```

做不到的（这是设计我们的 Agent 时要绕开的洞）：
1. **读不到像素**。`CompItem` 的全部属性与方法表里没有取像素接口，要像素只能先渲成 PNG/EXR 再读文件。`[官方文档]`
2. **`renderQueue.render()` 是阻塞调用**，渲完才返回；要并发得开多进程。`[官方文档]`
3. **`app.executeCommand(id)` 是补洞通道，但菜单 ID 跟语言包绑定**，官方文档自己写着 `findMenuCommandId` 跨语言包靠不住。`[官方文档]`
4. **脚本默认禁写文件、禁联网**，必须在 首选项 > 常规 里勾 `Allow Scripts To Write Files And Access Network`。这是量产管线的第一个坑。`[官方文档]`

#### 3.3.2 CEP 与 UXP 的真实状态

| 项 | CEP | UXP |
| --- | --- | --- |
| 形态 | HTML/CSS/JS 面板，ZXP 分发 | 共享 UXP 平台（`fs`/`os`/`uxp`）+ Spectrum UI + 主机模块 |
| 调 AE 的方式 | 一切操作拼成 JSX 字符串走 `CSInterface.evalScript()` | `const app = require("aftereffects")` 直调对象模型 |
| AE 版本对应 | AE 16/17→CEP 9、17.1.4→CEP 10、18.4→CEP 11、**AE 25.0→CEP 12** | 官方文档仓 `AdobeDocs/uxp-aftereffects`，正文标 `throughout the beta` |
| 内置运行时 | CEP 12 带 Node 17.7.1 + Node-WebKit 0.62.1，Node API 要 `--enable-nodejs`（全局多出 `cep_node`） | UXP 自带 |
| 停用日期 | CEP 12 cookbook 全文没有 EOL 声明 `[未证实]` | AE 起版版本号在可达资料里没写死 `[未证实]` |
| UXP 的能力缺口 | — | 官方索引 44 个 API 页里**没有** `executeCommand` / `scheduleTask` / `watchFolder` / `Socket` |

`[官方文档]` UXP 的能力其实不小：44 个 API 页覆盖 Application/Project/ItemCollection/CompItem/AVLayer/Layer/LayerCollection/CameraLayer/LightLayer/ShapeLayer/TextLayer/ThreeDModelLayer/ParametricMeshLayer/Property/PropertyGroup/MaskPropertyGroup/Shape/KeyframeEase/MarkerValue/TextDocument/CharacterRange/ParagraphRange/Font(s)/ImportOptions/各类 Source/FolderItem/GuideOptions/View(Viewer/Options)/Preferences/Settings/**RenderQueue + RenderQueueItem + RQItemCollection + OMCollection + OutputModule**/DeferredCall——等于把 ExtendScript 那套抄了一遍，连渲染队列都在。缺口在「菜单命令 ID 通道、Watch Folder、Socket」这三块。

#### 3.3.3 aerender：官方唯一批量渲染入口（`[官方文档]` `-help` 原文）

```
-h / -help                        用法
-reuse                            复用已运行的 AE 实例（不给就每次新起实例）
-project <path>                   工程
-teamproject <name>               团队工程
-comp <name>                      只渲该合成（不在队列里就加进队列再渲）
-rqindex <index>                  按队列序号渲单条
-RStemplate <模板名>              渲染设置模板
-OMtemplate <模板名>              输出模块模板
-output <path>                    输出目标
-log <path>                       日志（默认 stdout）
-s <start> / -e <end> / -i <step> 起帧 / 止帧（含）/ 步进
-mem_usage <imageCache%%> <maxMem%%>
-v ERRORS | ERRORS_AND_PROGRESS
-close DO_NOT_SAVE_CHANGES | SAVE_CHANGES | DO_NOT_CLOSE
-sound ON | OFF                   （默认 OFF）
-version                          只打印版本
-continueOnMissingFootage         缺素材不停机，占位彩条 + 写日志
```

三条行为规则（`-help` 原文口径，踩过才知道）：
1. **不给 `-comp` 时渲整队列，此时 `-RStemplate/-OMtemplate/-output/-s/-e/-i` 全部被忽略**，只有 `-project/-log/-v/-mem_usage/-close` 生效。
2. 不带 `-reuse`：新起实例 → 渲完自退 → **不写偏好设置**。带 `-reuse`：丢给已开实例 → 渲完不退 → 退出时写回偏好。
3. `-help` 里没有并发调度开关。多个 aerender = 多个 AE 实例，并发靠外部队列器。

官方给的三种命令形态（原文照抄）：
```bat
aerender -project c:\projects\proj1.aep -comp "Comp 1" -output c:\output\proj1\proj1.avi
aerender -project c:\projects\proj1.aep
aerender -project c:\projects\proj1.aep -comp "Comp 1" -s 1 -e 10 -RStemplate "Multi-Machine Settings" -OMtemplate "Multi-Machine Sequence" -output c:\output\proj1\frames[####].psd
```

#### 3.3.4 驱动 AE 的四条路径（按「要不要 GUI / 扛不扛并发」选）

| 路径 | 命令/机制 | 优点 | 短板 |
| --- | --- | --- | --- |
| A `afterfx -r` | `afterfx.exe -r script.jsx`、`afterfx.exe -s "代码"` | 最轻，官方唯一命令行入口；`-r` 把脚本丢给**已存在实例**执行，不新开 | 要 GUI 授权；`renderQueue.render()` 阻塞；回显要用 `AfterFX.com` |
| B `aerender` | 见 3.3.3 | 无 GUI、可多进程、日志齐全 | 只渲图，不建工程 |
| C 面板 | CEP/UXP | 用户可交互 | 对外部程序不友好 |
| D 静态改工程 | `py-aep` 改 `.aep` → 交给 B | **省一次 AE 启动（几秒到几十秒）与一次授权占用** | 表达式不求值、渲不了图 |

`[推断]` 我们的模板量产组合定为：**模板 `.aep` 常驻 + `py-aep` 改参数落新 `.aep` + `aerender` 多进程渲染 + `-log` 收日志 + 失败重投**；渲染设置用 `-RStemplate`/`-OMtemplate` 锁死，改参数与渲染设置彻底分离，把变量面压到最小。

### 3.4 表达式引擎：跟脚本是两套东西

- 表达式只描述「这个属性等于什么」，脚本是「让应用做事」；**表达式读不到脚本里的变量与函数**。`[官方文档]`
- 引擎两档可切：`app.project.expressionEngine` 取 `extendscript` 或 `javascript-1.0`（AE 16.0/2019 起可读可写），对应工程设置里的 Expressions Engine 下拉。`[官方文档]`
- **表达式文本就存在工程里的属性上**（`.aep` 的 `LIST tdbs` 里那个 `Utf8` chunk）。静态解析能把表达式完整抠出来。`[第三方研究]`
- 脚本侧操作面：`property.expression`（读写）、`expressionEnabled`、`expressionError`、`canSetExpression`，外加 `project.autoFixExpressions(oldText, newText)` 批量改。
- 求值语义（每帧重算、依赖图层顺序、跨预合成取值）在读到的官方正文里没有规格页；能确定的是纯解析器（py-aep / boltframe）明确把「表达式求值」列为不支持项。`[未证实]` 留白。

对我们的意义：**表达式就是「属性级的脚本化」**。我们要给 AI 一个比表达式更安全的等价物：受控的小 DSL（见 第六部分的 `expr` 字段设计），只放确定性函数，禁网络禁文件。

### 3.5 渲染与缓存：MFR 是真本事

- **多帧渲染（MFR）**：AE 2022 起支持一帧多线程并发。插件必须置 `PF_OutFlag2_SUPPORTS_THREADED_RENDERING` 且线程安全，不置位的插件被串行化（UI 上挂警告图标）。`[官方文档]`
- MFR 下选择器并发规则：UI 选择器留在主线程；`SEQUENCE_SETUP/RESETUP/SETDOWN`、`SMART_PRE_RENDER`、`RENDER`、`SMART_RENDER` 多线程并发；`GLOBAL_SETUP/GLOBAL_SETDOWN` 只在主线程。`[官方文档]`
- 渲染期 `sequence_data` 变 `const`，统一走 `PF_EffectSequenceDataSuite` 读；要写就得加 `PF_OutFlag2_MUTABLE_RENDER_SEQUENCE_DATA_SLOWER`，代价是每个渲染线程各持一份副本。`[官方文档]`
- **Compute Cache**：线程安全缓存，跨线程共享已算结果，支持 A/B 参数双态并存（`AEGP_ComputeCacheSuite1`），2022 起默认开。`[官方文档]`
- 脚本侧开关：`app.setMultiFrameRenderingConfig()`（AE 22.0 起），同期加了 `RenderQueue.queueNotify` / `RenderQueueItem.queueItemNotify`。
- 代理：脚本可全套配（含「用纯色当代理」，这条 UI 做不到）。`[官方文档]`
- 内存：`app.purge()` / `setMemoryUsageLimits()` / `memoryInUse`；aerender 侧 `-mem_usage`。
- 色彩：OCIO 走 `AEGP_ColorSettingsSuite5`（2023-05 SDK 起）——`AEGP_IsOCIOColorManagementUsed`、`AEGP_GetOCIOConfigurationFile/Path`、`AEGPD_GetOCIOWorkingColorSpace`、`AEGPD_GetOCIODisplayColorSpace`。脚本侧另有一套原生色彩面：`workingSpace` / `workingGamma` / `linearizeWorkingSpace` / `linearBlending` / `bitsPerChannel` / `listColorProfiles()`。
- 像素类型：`PF_Pixel8/16/Float(PF_Pixel32)`，色彩转换走 `PF_ColorCallbacksSuite`；32bpc 浮点 + SmartFX 是它做高质量合成的底子。

**MFR 的工程结论**：`sequence_data 变 const` + `Compute Cache 跨线程共享` 这两条，是「一帧多线程」必须付的架构代价。我们的渲染器要直接按「无共享可变状态 + 显式缓存句柄」设计，否则后面加并发要重写。

### 3.6 数据模型：合成 / 图层 / 属性三层，跟剪映完全不同

| 概念 | AE 的做法 | 剪映的做法 | 我们的选择 |
| --- | --- | --- | --- |
| 容器 | 工程 → 文件夹树 → 合成 → 图层 → 属性组 → 属性 → 关键帧 | 工程 → 轨道数组 → 片段 → 属性/关键帧 | 工程 → 序列 → 轨道 → 片段 → 属性 → 关键帧（借 AE 的深度 + 剪映的扁平） |
| 复用单元 | 合成（precomp），`Source ID` 指向合成项 | 复合片段（compound），`materials.drafts` | 序列即合成，可嵌套，UUID 引用 |
| 时间基 | `cdta.time_scale` + uint16 时间值 | 微秒 int64 | int64 微秒 + 帧率有理数 |
| 关键帧 | float64 五段（值/入速/入影响/出速/出影响）+ Ease Mode | 归一化值 + 曲线类型 | 三次贝塞尔 + 可选缓动预设 + 保持帧 |
| 遮罩 | track matte（层引用 + 模式） | track_matte / 蒙版素材 | 层引用 + 模式 + 蒙版路径对象 |
| 3D | 真 3D：摄像机、灯光、3D 层、参数化网格 | 无（只有 2D 变换） | 3D 层 + 摄像机 + 灯光（第二阶段做） |

`[官方文档]` 图层类型码（`ldta.Layer Type`）：`0` AVLayer、`1` 灯光、`2` 摄像机、`3` 文本、`4` 形状。父子级是 `Parent ID`（u32），轨道遮罩从 AE 23 起多一个 `Matte Layer ID`（u32）。

### 3.7 AE 的四条可搬运结论

1. **用「版本化 suite 结构体」做插件 ABI**（AEGP 的做法）比「稳定 C++ 类虚表」更抗演化：加方法只需出新版本 suite 号，旧插件不重编继续跑。
2. **模板 + 静态改工程 + 批渲染**是量产流水线的最优组合。AE 生态里 `py-aep` + `aerender` 这套组合已经验证了「不启动 GUI 也能出货」，我们做外挂式 AE 集成直接照搬。
3. **MFR 的代价要提前付**：无共享可变状态、显式缓存句柄、UI 与渲染线程严格分层。
4. **表达式的定位**：属性级确定性脚本。我们要给 AI 的版本必须砍掉文件系统与网络访问，只留纯函数。

---

## 第四章 三家横向比对与可搬运清单

### 4.1 七个关键分叉

| 维度 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 我们怎么定 |
| --- | --- | --- | --- | --- |
| UI 技术 | Qt6 Quick + Lynx + CEF | Qt5 Widgets 为主 + CEF 面板 | 自绘（闭源） | Qt6 Widgets 主窗 + Quick 面板 + WebView2 插件位 |
| 工程格式 | JSON（微秒） | SQLite 库 + `.drp`=ZIP(XML) | RIFX 二进制 + `.aepx` XML | SQLite 库 + AVS JSON/XML 双视图导出（第六部分） |
| 时间基 | int64 微秒 | 帧号 + 时间基线偏移 | uint16 + time_scale | int64 微秒 + 有理数帧率 |
| 扩展协议 | 内部命令表 + OFX bundle | Fuse(Lua) + DCTL(C) + OFX + Electron 面板 | PF_Effect + AEGP + CEP/UXP | OFX 1.4 宿主 + 自研 Lua 节点 + WebView 面板 |
| 脚本接口 | `jianying-agent-cli` + Lyra XMLDraft | 22 类 530 方法 + 1144 端口 | JSX + aerender + UXP | MCP 工具 + REST/JSON-RPC 内部总线（第五部分） |
| AI 落地 | 端侧 46 个模型包 + 云侧 SDK | 端侧 llama.cpp/ORT/OpenVINO + Extras 包 | 无端侧 AI（靠第三方脚本） | 端侧 ORT+llama.cpp，能力包化（第七部分） |
| 撤销粒度 | 命令 + `batchStart/batchEnd` | 内部（脚本层无撤销 API） | `beginUndoGroup/endUndoGroup` | 命令总线 + 事务 + 事件溯源（第五部分） |

### 4.2 可搬运清单（按「抄什么 / 从哪抄 / 抄到哪层」）

| # | 要抄的东西 | 来源 | 抄法 | 落在我们哪层 |
| --- | --- | --- | --- | --- |
| 1 | 工程双层表示（磁盘全量 + 给 AI 的受限 XML 视图） | 剪映 Lyra | 编译器 + 双向映射 | L3 存储 / L10 Agent |
| 2 | Selection Expression 式改动协议 | 剪映 | 直接照设计，换 XML 方言 | L10 / L12 |
| 3 | `target_xml` / `current_xml` / `apply()` 三态事务 | 剪映 | 直接照 | L4 时间轴 / L3 存储 |
| 4 | 「≤3 片段一次提交，>3 拆两批」的调用策略 | 剪映 | 写进 Agent 系统提示 | L10 |
| 5 | 命令表 + 域.动作 命名 + 模型安全子集 | 剪映 | 照抄组织法，命令自己定 | L4 |
| 6 | `batchStart/batchEnd` 一批 = 一个 undo | 剪映 | 直接照 | L4 |
| 7 | 内容/索引分离（content 与 meta 两个文件） | 剪映 | 直接照 | L3 |
| 8 | 端侧模型货架（按能力分目录、100KB~30MB 分级） | 剪映 | 照抄目录规范 | L9 |
| 9 | 能力包化 + 脚本可安装/可探测 | 达芬奇 Extras | 直接照 | L9 / L11 |
| 10 | 明文结构 + 二进制内容 + UUID 引用 | 达芬奇 `.drp` | 直接照 | L3 |
| 11 | 脚本 API 重心放片段层（110 方法级） | 达芬奇 | 照设计，砍到 60 条核心 | L4 接口 |
| 12 | job id 制渲染（Add→Start→GetStatus） | 达芬奇 | 直接照 | L6 |
| 13 | 字符串字典式设置（key-value 与 UI 参数一一对应） | 达芬奇 | 直接照 | L4 / L6 |
| 14 | DCTL 式像素着色器 DSL + 加密分发 | 达芬奇 | 自研等价物（WGSL 子集） | L8 |
| 15 | Fuse 式 Lua 节点（Lua 编排 + 内置算子做像素） | 达芬奇 | 直接照 | L8 |
| 16 | OFX 1.4 宿主 | 达芬奇 + OpenFX | 接标准 | L8 |
| 17 | Electron 面板三件套（manifest + preload + 原生桥） | 达芬奇 Workflow Integration | 直接照 | L1 / L12 |
| 18 | `-nogui` 无头模式 + 脚本照常 | 达芬奇 | 直接照 | L6 |
| 19 | 版本化 suite 结构体做插件 ABI | AE AEGP | 直接照 | L8 |
| 20 | MFR 的前置约束（无共享可变状态 + 显式缓存句柄） | AE | 架构约束 | L6 |
| 21 | 模板 + 静态改工程 + 批渲染流水线 | AE（py-aep + aerender） | 做成外部集成适配器 | L12 集成层 |
| 22 | 属性级确定性脚本（砍掉文件与网络） | AE 表达式 | 自研小 DSL | L8 / L10 |
| 23 | 审片的证据边界规则（素材/脚本/草稿/成片四级证据） | 剪映 editing-review | 直接照 | L10 Critic |

### 4.3 三家都做得难看的三个地方（我们的机会）

| 现象 | 三家各自的表现 | 我们怎么做 |
| --- | --- | --- |
| AI 改工程要么太粗要么不可控 | 剪映靠专用协议（好用但绑定自己）；达芬奇给脚本 API（自由但模型易写错）；AE 全靠第三方拼 JSX（脆） | 受限 DSL + 预演（`--preview` 回候选不落地）+ 修订号乐观锁 + 一次提交等于一个 undo 步 |
| 工程文件不可读/不可 diff | 剪映双重 JSON 字符串、达芬奇 `FieldsBlob`、AE RIFX | JSON 主存 + 规范化排序 + 语义 diff（按对象与属性，不按行） |
| 长任务黑盒 | 三家都只有「状态查询」，没有「可续跑的步骤账本」 | 任务表 + 步骤账本（每步输入/输出/证据）+ 断点续跑 |

### 4.4 三家的不可替代之处（抄不来的部分）

- **剪映**：短视频素材库 + 模板商城 + 端侧模型与产品化的贴合度。它把「一键成片」拆成了 18 个技能包 + 200 条命令，这套产品工程学比代码更值钱。
- **达芬奇**：Fusion 节点的完整度 + 色彩科学的行业信任 + 免费的 Studio 级调色。它的护城河是「专业调色师的工作流习惯」。
- **AE**：表达式 + 效果插件生态 + 与 PS/AI/PR 的工程互操作。它的护城河是二十年的插件积累与 MoGraph 用户惯性。

---

## 第三部分　三大软件功能对照表

> 基线日期：2026-11-20
> 对象：剪映专业版 11.7.0.14652（本机隔离版实测）、DaVinci Resolve 21.2 build 6（本机隔离版实测）、After Effects 27.0（本机未装，走公开资料与随包文档线）
> 证据口径沿用 `第一部分` 六档：`[实测]` / `[随包文档]` / `[开源代码]` / `[第三方]` / `[推断]` / `[未证实]`

### 读法

- 每行一个具体功能，9 列固定：功能 ｜ 剪映 11.7 ｜ 达芬奇 21.2 ｜ AE 27.0 ｜ 实现方式判定 ｜ 公开程度 ｜ 我们复用度 ｜ 开发难度 ｜ 技术来源。
- 「实现方式判定」写落点：CPU 算法 / GPU shader / AI 模型推理 / 云端 API / 参数化模板 / 脚本层实现，括注证据档。
- 「公开程度」四档：公开文档化 / 随包文档 / 需逆向 / 闭源黑盒。
- 「我们复用度」五档：直接抄设计 / 可借鉴 / 换成开源实现 / 自研 / 不做。
- 「开发难度」★ 到 ★★★★★，锚点：★★ ≈ 3 人月，★★★★★ ≈ 30 人月以上。
- 三家单元格里写机制，不写「有/无」两级判定；确实没有该项的实现时写它拿什么顶替。

---

### ① 工程与文件格式

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 工程容器形态 | 明文目录：`draft_content.json` + `draft_meta_info.json` + 素材散落同盘 | `.drp` = PK zip，内含 `project.xml`、`MediaPool/Master/MpFolder.xml`、`SeqContainer/<uuid>.xml`、`Gallery.xml` | RIFX 二进制单文件，chunk 以 `Egg!` 与 `LIST` 组织，大端容器 | 剪映 JSON 序列化（`[实测]`）；达芬奇 zip + 分片 XML（`[实测]`）；AE 私有 chunk（`[第三方]`） | 剪映 需逆向｜达芬奇 需逆向｜AE 闭源黑盒 | 直接抄设计 | ★★ | `drp_extract/project.xml`、`drp_extract/SeqContainer/c9dd78a8-594a-4198-9c9b-2d9138040406.xml` |
| 时间单位与时间基 | 微秒整数，`target_timerange` 起止都按 µs | 帧整数，`Start`=86400 / `Duration`=120，配 24fps 正好 1 小时 | 秒浮点（图层 in/out），合成帧率存有理数 | 三套互不兼容的私有时间基（`[实测]`） | 剪映 需逆向｜达芬奇 需逆向｜AE 闭源黑盒 | 换成开源实现 | ★★ | 真实草稿 dump（644KB / 95 视频段 + 313 文字段）；`SeqContainer` XML |
| 工程字段编码 | 纯 JSON，字段名即语义，可直接 diff | `FieldsBlob`：长度前缀 + UTF-16LE 键值对，二进制不可读；`CompositionBA` 是 base64 压缩块 | RIFX chunk（4 字节长度 + 4 字节类型码 + 大端数据），无公开规范 | 达芬奇私有 TLV（`[实测]`）；AE RIFX（`[第三方]`） | 需逆向｜需逆向｜闭源黑盒 | 不做 | ★ | `SM_Project/FieldsBlob` 十六进制 dump |
| 项目库与工程发现 | 草稿箱按目录扫描，`draft_meta_info.json` 供缩略图与时长 | Project Library 三型（Local / Network / Cloud）：本地 SQLite，协作走 PostgreSQL，带库版本升级与 GFS 备份 | 文件系统，无库概念，靠最近工程列表 | 库服务 = 数据库 + 文件（`[随包文档]`） | 剪映 需逆向｜达芬奇 公开文档化｜AE 公开文档化 | 直接抄设计 | ★★ | `resolve21_manual.txt` 第 82-90 页；随包 `qsqlite.dll` / `qsqlpsql.dll` |
| 素材登记表 | `materials` 46 类扁平材质表，每类一张 id → 属性表 | `MpFolder.xml` 媒体池树 + clip 引用（171KB 实测） | RIFX Items 表 + footageItem 引用 | 剪映扁平池（`[开源代码]`）；达芬奇树形池（`[实测]`）；AE 对象表（`[第三方]`） | 需逆向｜需逆向｜闭源黑盒 | 直接抄设计 | ★★ | `pyJianYingDraft/local_materials.py`；`drp_extract/MediaPool/Master/MpFolder.xml` |
| 素材引用方式 | 绝对路径字符串 + `material_name`，移动素材即断链 | `MediaFilePath` + `MediaReelNumber` + `MediaTimemapBA`（base64 时间映射表） | 绝对或相对路径 + 卷标识 + 素材代理 | 剪映路径直填（`[实测]`）；达芬奇带时间映射（`[实测]`） | 需逆向｜需逆向｜闭源黑盒 | 可借鉴 | ★★ | `Sm2TiVideoClip` 的 `MediaTimemapBA`（`024013d55555555555`） |
| 工程版本与迁移 | `version` 字段，随客户端升级做字段迁移 | `DbPrjVer="14"` + 库 Upgrade 按钮 + 大版本不兼容提示 | 工程版本号，低版本另存降级 | 版本号 + 逐级迁移函数（`[实测]`/`[第三方]`） | 剪映 需逆向｜达芬奇 公开文档化｜AE 公开文档化 | 直接抄设计 | ★★ | `project.xml` 头部注释 `DbAppVer="19.1.1.0004" DbPrjVer="14"` |
| 交换格式进出 | 只吐自家 draft，XML / AAF / EDL / OTIO 一个出口都没有 | AAF、FCP7 XML、FCPX XML、OTIO（.otio / .otioz）、EDL、DRT、ADL 全进全出 | XML、AAF、EDL、OTIO 靠 ProImport 与第三方桥 | 达芬奇内建 conform 引擎（`[随包文档]`）；AE 走导入插件（`[第三方]`） | 剪映 闭源黑盒｜达芬奇 公开文档化｜AE 公开文档化 | 可借鉴 | ★★★ | `_research/d3_otio_templates.txt` 第 544 页；`_research/d2_interchange.txt` |
| 工程内嵌合成块 | 无独立合成块，全部平铺在 draft 里 | Fusion 合成压进 `CompositionBA`（base64 加压缩），一个标题就是一张 comp | 合成即嵌套 comp，RIFX 顺层存 | 剪映无节点图（`[推断]`）；达芬奇压缩 blob（`[实测]`） | 需逆向｜需逆向｜闭源黑盒 | 直接抄设计 | ★★★ | `Sm2TiCompositionTable/CompositionBA`、`ActiveCompositionIdx` |
| 工程加密与混淆 | 6.0+ 起部分版本 draft 加密，社区只拿到探测结论与失败路径 | 无，`.drp` 就是明文 zip | 无，RIFX 明文 | 剪映混淆层（`[第三方]`，算法本身 `[未证实]`） | 需逆向｜公开文档化｜闭源黑盒 | 不做 | ★ | `_research/_src_gist.txt`（GitHub gist 记录）、`_src_kanxue_285223.html` |
| 工程规模与加载 | 644KB 单 JSON 全量反序列化，95 视频段 + 313 文字段实测 | 多文件 XML，按 `SeqContainer` 分片惰性加载，时间线引 `TimelineHandleVec` | RIFX 全量读入 + 媒体索引懒加载 | 惰性分片（`[实测]`/`[推断]`） | 需逆向｜需逆向｜闭源黑盒 | 可借鉴 | ★★ | `project.xml` 的 `TimelineHandleVec` 与 `StreamPlayHeadVector` |
| 撤销与事务落盘 | `undoRedo` 域只是 200+ 命令里的一个域，栈在内存，落盘靠 `draft_patch` | 内存撤销栈；脚本层方法组里没有 undo 分组，脚本改完不可回退 | 撤销栈；脚本执行期间多数操作不入栈 | 命令模式 + 内存栈（`[随包文档]`/`[第三方]`） | 需逆向｜随包文档｜公开文档化 | 直接抄设计 | ★★★ | 剪映 FN3 命令表 `undoRedo` 域；Resolve API 全表无 undo 方法 |

### ② 时间轴与轨道

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 轨道模型 | 只有 video / text / audio 三类轨，同轨片段按 µs 排布不重叠 | `VideoTrackVec`、音频轨、字幕轨、Fusion 轨各自独立容器，`Sm2TiTrack` 带 `Type`/`SubType` 位 | 没有轨道，只有图层 z 序 + 合成嵌套 | 剪映三轨枚举（`[实测]`）；达芬奇多容器（`[实测]`）；AE 图层栈（`[第三方]`） | 需逆向｜需逆向｜闭源黑盒 | 直接抄设计 | ★★★ | `draft_content.json` tracks 三类；`SeqContainer` 的 `Sm2TiTrack/Type` |
| 片段结构 | segment：`target_timerange` / `source_timerange` / `speed` / `clip` / `extra_material_refs` | `Sm2TiVideoClip`：`Start` / `Duration` / `MediaStartTime` / `EffectFiltersBA` / `CompositionTable` | 图层 + source item + in/out 点 | 剪映双时基区间（`[开源代码]`）；达芬奇帧区间（`[实测]`） | 需逆向｜需逆向｜闭源黑盒 | 直接抄设计 | ★★ | pyJianYingDraft segment 类；`Sm2TiVideoClip` 节点 |
| 嵌套与复合片段 | 复合片段（compound），子结构内联在主 draft | 时间线嵌套，`TimelineHandleVec` 指向别的 `SeqContainer` | 预合成（precomp），任意深度嵌套 | 剪映内联（`[随包文档]`）；达芬奇外链（`[实测]`）；AE 外链（`[第三方]`） | 需逆向｜需逆向｜闭源黑盒 | 直接抄设计 | ★★★ | `canvas_agent/skills/jianying.hub.studio_lyra_xml_timeline_builder_v2/references/compound.md`；`project.xml` |
| 关键帧模型 | `keyframe` 材质挂属性曲线，支持离散 / 线性 / 贝塞尔 | 每属性带插值模式（Linear / Bezier / Ease）+ 曲线编辑器，帧基 | 每属性关键帧 + 空间/时间双插值 + 表达式可接管 | 剪映时间-值对（`[随包文档]`）；达芬奇带插值枚举（`[随包文档]`）；AE 可编程（`[第三方]`） | 需逆向｜随包文档｜闭源黑盒 | 直接抄设计 | ★★★ | 剪映 17 域里的 `keyframe` 域；Resolve `TimelineItem` 关键帧方法组（`.pyi` 22 类 530 方法） |
| 变速 | `speed` 字段给倍率，另有曲线变速材质做变速曲线 | Retime 曲线，speed keyframe 落在帧坐标上 | 时间重映射 + 帧混合 / 像素运动 | 剪映参数化倍率（`[开源代码]`）；达芬奇帧基曲线（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★★ | pyJianYingDraft 的 speed 处理；manual Retime / Elastic 章节 |
| 转场 | transition 材质，带 name / duration / 参数，落在两段接缝 | 内置转场 + OFX 转场 + Fusion 转场三套并存 | 没有转场对象，用效果叠层与预合成手搭 | 剪映模板参数（`[随包文档]`）；达芬奇三实现（`[随包文档]`）；AE 无对象（`[第三方]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 materials 的 transition 类；Resolve 编辑章节转场段 |
| 文字轨独立成轨 | text 轨与 video 轨平行，文字段有自己的 timerange | 字幕轨（Subtitle track，可导 SRT）+ Text+ 落在 Fusion 合成里 | 文字就是图层，没有独立字幕轨 | 剪映文字轨（`[实测]`）；达芬奇双轨制（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★ | `draft_content.json` tracks 三类；manual Subtitle 章节 |
| 轨级开关 | 没有轨级禁用位，只能删段或删轨 | 轨级 enable / disable / solo | 图层开关与独奏 | UI 状态位，不动数据（`[推断]`） | 需逆向｜随包文档｜公开文档化 | 直接抄设计 | ★ | 剪映命令表 `track` 域；Resolve 轨状态方法组 |
| 剪辑版本堆 | 没有版本概念，改就是改 | 片段版本堆（clip version），`pLmVerTable` 直接存在片段里，切版本不动时间轴 | 没有版本，靠另存工程 | 达芬奇版本表（`[实测]`） | 需逆向｜需逆向｜闭源黑盒 | 直接抄设计 | ★★★ | `Sm2TiVideoClip/pLmVerTable` 下的 `LmVersion` 节点（`Version 1`、`HasCorrection`） |
| 多机位 | 没有，靠手动叠轨 | Multicam clip，角度切换记录为剪辑决定 | 没有 | 达芬奇内建（`[随包文档]`） | —｜公开文档化｜— | 可借鉴 | ★★★ | manual Multicam 章节 |
| 吸附 / 对齐 / 磁性 | UI 吸附 + 磁性时间轴，片段自动贴身 | 吸附开关 + 波纹编辑模式，吸附点按帧 | UI 吸附，无波纹语义 | UI 状态 + 布局算法（`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★ | 剪映 UI 行为实测；manual 波纹编辑章节 |
| 时间轴渲染顺序 | 轨序 + 同轨不重叠，合成顺序固定 | 轨序自下而上，Fusion 轨再叠一层合成 | 图层 z 序 + 混合模式逐层叠 | 栈式合成（`[推断]`） | 需逆向｜闭源黑盒｜闭源黑盒 | 直接抄设计 | ★★ | 三套工程文件里的序字段与轨类型位 |

### ③ 剪辑操作

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 分割 / 切割 | segment 按 µs 二分，源区间偏移随动，操作走 `segment` 域命令 | Razor 按帧切点，切点贴帧边界 | 图层按播放头切开，属性关键帧跟随 | 剪映微秒切（`[随包文档]`）；达芬奇帧切（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 `segment` 域命令表；Resolve `AppendToTimeline` 与切分方法组 |
| 波纹删除 / 插入 | 有，删段后后续整段前移；配 `cut_tail_align` 消隙 | Ripple Delete 与 Ripple 编辑模式 | 没有，靠脚本遍历改 in 点 | 时间轴重排算法（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 `track`/`segment` 域；manual Ripple 章节 |
| 三点 / 四点编辑 | 没有，只能拖到位置再裁 | 完整：源入出点 + 时间线入出点，四种组合 | 没有，靠手动对齐 | 达芬奇内建（`[随包文档]`） | —｜公开文档化｜— | 可借鉴 | ★★★ | manual 三点编辑章节 |
| 智能抠像 / 去背 | 智能抠像与人像抠图，端侧分割模型出 alpha | Magic Mask：GPU 推理 + 笔刷细化 + 时序传播 | Roto Brush 3：时序分割 + 传播 | AI 模型推理（`[随包文档]`/`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★★ | 剪映 `models/` 46 包 + `onnxruntime`；达芬奇 `onnxruntime` + `torch_cpu`（231MB） |
| 智能补帧 | 光流补帧，预览与导出两档质量 | Speed Warp（GPU 光流 + 帧合成） | 时间重映射配像素运动模糊 | GPU 光流（`[推断]`，依据包内 CUDA/ONNX 组件） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★★ | 剪映 `onnxruntime_providers_cuda.dll`；Fusion GPU 合成 |
| 场景切分 | 智能镜头分割，端侧跑，切完直接落时间轴 | Scene Cut Detection：CPU 直方图差，秒级出点 | 没有，第三方脚本 | CPU 算法（`[随包文档]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★ | manual Scene Cut 章节；剪映随包 `smart_cut.ofx.bundle` |
| 语音转字幕 | 识别字幕，`speechsdk` 与云端两条路，结果直落 text 轨 | Transcribe：本地模型，自动生成字幕轨 | 没有，脚本调第三方 | 语音模型推理（`[随包文档]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★★ | `speechsdk.dll` / `grow-voice-api.dll`；manual Transcribe 章节 |
| 静音与停顿删除 | 智能删停顿、按语速重切 | 没有，靠手动波纹 | 没有 | 波形能量 + VAD（`[推断]`） | 需逆向｜—｜— | 换成开源实现 | ★★ | 剪映 `audio` 域命令 + `rnnoise_v2.0.model` |
| 踩点 / 节拍对齐 | 音乐踩点，按拍点切段并落标记 | 没有 | 没有 | 节拍检测（`[推断]`） | 需逆向｜—｜— | 换成开源实现 | ★★ | 剪映 `batch` 与 `audio` 域命令组合 |
| 素材替换与灌参 | 模板可替换材质，替换策略四档：`cut_head` / `cut_tail` / `cut_tail_align` / `shrink`，变长再走 `extend_head` / `extend_tail` / `push_tail` / `cut_material_tail` | Media Pool 替换 + relink + 强制重链 | 脚本 `replaceSource` + MOGRT 暴露控件写值 | 参数化模板（`[开源代码]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | `_research/_src_template_mode.py` 的 `ShrinkMode` / `ExtendMode` 枚举 |
| 音画同步 | 音频对齐，按波形对齐多条素材 | Sync by waveform，波形能量差分搜索最优偏移 | 没有 | CPU 波形搜索（`[推断]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★★ | manual 同步章节；剪映 `segment` 同步命令 |
| 批量操作 | `batch` 域命令，一次改多段，事务内提交 | 脚本循环，逐条提交，无事务 | 脚本循环，逐条提交 | 脚本层实现（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 FN3 命令表 `batch` 域；Resolve 脚本循环 |

### ④ 画面变换与合成

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 二维变换 | `clip` 里 transform 组：x / y / scale / rotation / flip，全属性可挂关键帧 | Inspector Transform：位置 / 缩放 / 旋转 / 锚点，帧基关键帧 | Transform 组 + 父级链 + 空间插值（贝塞尔路径） | 剪映属性对象（`[随包文档]`）；达芬奇 GPU 矩阵（`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 `video` 域命令；`clip` 材质字段表 |
| 蒙版 | 线性 / 圆形 / 矩形 / 心形四种形状，带羽化与反转 | Power Window：贝塞尔多边形 + 圆形 + 渐变，可挂跟踪 | 蒙版路径 + 羽化 + 扩展 + 逐帧插值 | 剪映参数化形状（`[随包文档]`）；达芬奇贝塞尔 + 跟踪（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | 剪映 `video` 域 mask 命令；`FusionToolReference.md` |
| 混合模式 | blend mode 枚举（正常 / 滤色 / 叠加 / 正片叠底等） | composite mode：Add / Screen / Multiply / Overlay 等 | 38 种混合模式，含 HSL 系 | GPU shader 分支（`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★ | `clip` 材质字段；AE 混合模式表 |
| 不透明度与层叠 | 段级 alpha + 混合，多段叠在视频轨上 | 段级 opacity 关键帧 + 轨层叠 | 图层 opacity + 父子继承 | 合成栈（`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★ | 剪映 `video` 域；manual 合成章节 |
| 画面稳定 | 视频稳定（防抖），三档强度 | Stabilization：光流 + 相机路径拟合 + 平滑参数 | Warp Stabilizer：位置/旋转/缩放分项 + 自动缩放 | GPU 光流（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | 剪映 `video` 域；manual Stabilization 章节 |
| 平面与点跟踪 | 没有独立跟踪器 | Fusion Planar Tracker + Point Tracker，输出可驱动窗口 | Mocha AE 平面跟踪 + 3D 相机跟踪 | 跟踪算法（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★★ | `Fusion Tools.md` 跟踪节点；AE 内置 Mocha |
| 合成节点图 | 没有节点图，VECreator 内部固定合成栈 | Fusion 节点图：MediaIn → 工具链 → MediaOut，支持 Lua 工具与 Fuse | 效果栈 + 图层，无节点图 | 节点图求值（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★★★ | `FusionToolReference.md`、`Plugins/*.plugin` 目录 |
| 表达式与程序化 | Selection Expression：内部查询语言，供 AI 与模板选点 | Fusion SimpleExpression，逐 input 绑定 | AE 表达式引擎：JS 子集，任意属性可编程 | 脚本层实现（`[随包文档]`） | 需逆向｜随包文档｜公开文档化 | 可借鉴 | ★★★★ | `lyra_xml_timeline_builder_v2` skill 全套；AE 表达式文档；剪映表达式完整语法 `[未证实]` |
| 三维与摄像机 | 没有 | Fusion 3D：USD 场景 + 摄像机 + 灯光 | 3D 图层 + 摄像机 + 灯光 + C4D 集成 | 三维管线（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 不做 | ★★★★★ | `Plugins/USD`、`Plugins/MaterialX` |
| 画中画与多画面 | 靠轨道叠加，没有画中画对象 | Edit 页层叠 + Fusion 合成 | 预合成 | 栈式合成（`[推断]`） | —｜—｜— | 直接抄设计 | ★ | 三套工程文件的层序字段 |
| 变速曲线编辑器 | 曲线变速面板，控制点可拖 | Retime 曲线编辑器 | 速度图 + 时间重映射 | UI + 曲线求值（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★★ | manual Retime 章节；剪映曲线变速材质 |
| 调节层 | adjustment 材质，影响其下所有段 | Adjustment Clip / Fusion comp 覆盖轨 | 调整图层 | 参数化（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 `adjustment` 域命令 |

### ⑤ 特效与插件

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 滤镜 | filter 材质：内置 + 云下载，强度可调，本质上 LUT + 参数包 | LUT 浏览器 + 3D LUT 管理 + OFX 滤镜 | Lumetri LUT + 效果叠加 | 参数化模板 + LUT（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 `filter` 域；materials 的 filter 类 |
| 特效（参数化） | effect 材质：name + 参数表，参数由服务端下发 | Fusion 工具 + OFX 效果，参数随工具定义 | 内置效果 + 第三方插件 | 参数化模板（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | 剪映 `effect` 域；`FusionTools.md` |
| 插件 ABI | 随包 `smart_cut.ofx.bundle`，自己就是 OFX 宿主；加载路径 `[未证实]` | OFX 1.4 + DCTL + Fuse(Lua) + Workflow Integration 四层 | PF_Effect（`.aex`）+ AEGP + CEP/UXP 面板 | 插件 ABI（`[随包文档]`） | 需逆向｜随包文档｜需逆向 | 换成开源实现 | ★★★★ | `Plugins/*.plugin`；OFX 1.4 头文件；AE SDK |
| 像素着色器 DSL | 没有公开 DSL | DCTL：C 风格，一份源码编译到 CUDA / OpenCL / Metal | 没有（Pixel Bender 已退役） | GPU shader（`[随包文档]`） | 需逆向｜公开文档化｜— | 可借鉴 | ★★★★ | 达芬奇 DCTL 文档与 `Plugins/dctl` |
| 插件注册与签名 | 云下发 + 本地包，加载前宿主校验签名 | `.plugin` 目录即注册表，目录扫描即枚举 | `.aex` 放 Plug-ins 目录 + 签名校验 | 目录扫描 + 签名（`[实测]`/`[推断]`） | 需逆向｜需逆向｜需逆向 | 可借鉴 | ★★ | 三套安装目录结构实测 |
| 特效资源市 | effect / filter / textTemplate 云下发，分免费与会员档 | 内置 + Reactor 社区包 | 内置 + 第三方市场 | 云端 API（`[随包文档]`） | 闭源黑盒｜公开文档化｜公开文档化 | 可借鉴 | ★★★ | 剪映 materials 的 effect 类；Reactor |
| 粒子与模拟 | 没有 | Fusion Particles：节点式发射器 + 力场 | CC Particle World 等第三方 | CPU/GPU 模拟（`[随包文档]`） | —｜公开文档化｜公开文档化 | 不做 | ★★★★★ | `Fusion Tools.md` 粒子节点 |
| GPU 计算后端 | `onnxruntime`（CUDA）+ Intel OpenVINO + 高通 QNN（Hexagon NPU）+ 自研 ByteNN 四路并存 | CUDA / OpenCL / Metal + `ggml-cuda.dll` + `torch_cpu` | Mercury GPU：CUDA / OpenCL / Metal | GPU 抽象层（`[实测]`） | 需逆向｜需逆向｜需逆向 | 换成开源实现 | ★★★★ | 剪映 `onnxruntime_providers_cuda.dll`、`QnnHtp.dll`、`bytenn_dsp.dll`；达芬奇 `ggml-cuda.dll` |
| 转场作为插件 | 转场材质云下发，参数模板化 | OFX transition + Fusion transition | 没有对象 | 参数化模板（`[随包文档]`） | 需逆向｜公开文档化｜— | 直接抄设计 | ★★ | 剪映 transition 材质；manual 转场章节 |
| 参数 schema 驱动 UI | 参数表驱动前端面板，加特效不改前端 | OGraf Manifest 声明属性与控件类型，HTML 面板自动生成 | 效果参数 + 脚本可枚举 | 参数 schema（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `OGraf HTML Templates/Documentation/04-Manifest-Reference.md`、`05-Properties-and-Controls.md` |
| 时间线级效果 | 调节层材质 | Adjustment Clip 与 Fusion comp 轨 | 调整图层 | 参数化（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 `adjustment` 域 |
| 字幕样式模板（花字） | textTemplate 材质云下发，可换文本与配色 | Fusion Title + OGraf HTML 模板 | MOGRT（Essential Graphics 模板） | 参数化模板（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | 剪映 `textTemplate` 域；OGraf 全套文档 |

### ⑥ 字幕与文字

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 文字数据模型 | text 材质：`content` 字段里塞一段 JSON 字符串（文本 + 样式分段） | Text+：Fusion 工具，多 style 段并存 | TextLayer + Source Text（字符串或表达式） | 剪映嵌套 JSON 串（`[开源代码]`）；达芬奇 Fusion 工具（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `_research/_src_text_segment.py`；Fusion Text+ 文档 |
| 富文本分段样式 | styles 数组：填充 / 描边 / 阴影 / 字号 / 字距逐段独立 | Text+ 的多个 style 页签 | 文本动画器 + 范围选择器 | 剪映分段样式（`[开源代码]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | 同左，`_src_text_segment.py` |
| 字幕轨与 SRT | text 轨 + SRT 导入导出 | Subtitle 轨 + SRT 导入 + 字幕检查器 | 没有独立字幕轨，第三方脚本 | 剪映双轨（`[随包文档]`）；达芬奇内建（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★ | manual Subtitle 章节；剪映 `text` 域命令 |
| 模板参数暴露 | 模板定义可替换字段：文本 / 颜色 / 时长 | OGraf Manifest 声明属性与控件类型 | MOGRT 暴露控件 + 脚本 `setValue` | 参数 schema（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `04-Manifest-Reference.md`、`05-Properties-and-Controls.md` |
| 文字排版引擎 | 前端 Lynx/CEF 排版，内核按帧出图 | Fusion Text+ 自研排版 | 自研文字引擎，含 CJK 竖排 | 自研排版（`[推断]`） | 需逆向｜闭源黑盒｜闭源黑盒 | 换成开源实现 | ★★★★ | 剪映 `libcef.dll`（207MB）/ `lynx.dll`（21MB）；达芬奇 `Plugins/text` |
| 逐字与打字机动画 | 文字动画预设云下发，按字符出时间偏移 | Fusion 表达式驱动逐字 | 文本动画器按字符/字/行分段 | 参数化模板（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映 textTemplate 域；AE 动画器文档 |
| 语音转字幕落位 | 识别后直接生成 text 轨段，带词级时间 | Transcribe 生成字幕轨，可编辑 | 脚本调第三方 | AI 推理 + 轨写入（`[随包文档]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★★ | 见 ③ 语音转字幕行 |
| 多语言与竖排 | 中英日韩 + 竖排 | 多语言 + Text+ 竖排 | 多语言 + 竖排 | 排版能力（`[推断]`） | —｜公开文档化｜公开文档化 | 可借鉴 | ★★★ | 三家官方规格页 |
| 文字与色彩管理 | 文字在 sRGB 空间出图 | Text+ 走工程色彩空间 | 走工程色彩管理 | 色彩管线（`[推断]`） | —｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 达芬奇 RCM / OCIO 章节 |

### ⑦ 音频

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 音频轨与总线 | audio 轨平铺，没有总线概念 | Fairlight FlexBus：子混 / 总线 / VCA / Link Group，Fixed Bus 模式上限 480 插件 | 没有混音器，图层音频 + 效果 | 混音图（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★★★ | `BMDAudioPlugins.dll`；manual Fairlight 章节 |
| 音量与淡化 | volume 属性 + 淡入淡出（µs） | 关键帧 + Fade In/Out 手柄 | 音频电平关键帧 | 参数 + 曲线（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★ | 剪映 `audio` 域命令 |
| 降噪 | 智能降噪：rnnoise 模型 + 服务端增强两档 | Voice Isolation：模型推理，带强度滑杆 | 没有，靠第三方 | AI 模型推理（`[随包文档]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★★ | `rnnoise/rnnoise_v2.0.model`；`VoiceIsolation.dll` |
| 人声分离 | 人声与伴奏分离，本地或云两路 | Voice Convert / 人声隔离 | 没有 | AI 模型推理（`[随包文档]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★★★ | `audioeffect.dll`；达芬奇模型目录 |
| 变声与音色 | 音色库，`grow-voice-api` 走云；本地与云的边界 `[未证实]` | Voice Convert：本地模型改音色 | 没有 | 云端 API + 模型（`[随包文档]`） | 需逆向｜公开文档化｜— | 可借鉴 | ★★★ | `grow-voice-api.dll` |
| TTS 配音 | 文本朗读，多音色，走云 | 没有 | 没有 | 云端 API（`[随包文档]`） | 闭源黑盒｜—｜— | 换成开源实现 | ★★★ | 剪映 `audio` 域 + 云 SDK |
| 变速与保调 | 变速保音调 | Elastic Wave 两档：Voice / General Purpose | 时间伸缩不保调 | 相位声码器 / PSOLA（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | manual Elastic Wave 章节（第 4080 页） |
| 响度与电平 | 导出目标响度 + 音量归一 | LUFS 响度表 + 归一化 | 仅仪表 | CPU 算法（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★ | manual Fairlight 响度章节 |
| 插件承载 | 没有 VST | VST3 / AU / Fairlight FX 三层，另带 `VstScanner.exe` 扫描器 | 没有 | 插件宿主（`[随包文档]`） | 需逆向｜公开文档化｜— | 换成开源实现 | ★★★★ | `VstScanner.exe`；manual 第 4082 页 |
| 多声道与沉浸声 | 立体声 / 单声道 | 5.1 / 7.1 / Ambisonics / Dolby Atmos（RMU + re-render 预设） | 多声道有限 | 混音格式（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 不做 | ★★★★★ | manual 第 4160 页 Atmos 章节 |
| 波形与音频分析 | 预生成波形文件 | 缓存波形 + 弹性视图时间点 | 波形显示 | CPU 预计算（`[推断]`） | —｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 剪映缓存目录；manual Elastic View |

### ⑧ 调色与色彩管理

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 基础校正 | 调节面板：亮度 / 对比度 / 饱和 / 色温 / 色调 / HSL | Primaries：Lift / Gamma / Gain + 色轮 + 色温 + 色相曲线 | Lumetri 基本校正 | GPU 运算 + LUT（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | 剪映 `adjustment` 与 `video` 域；Fusion 色彩工具 |
| 曲线 | 曲线调节，RGB 与单通道 | 曲线面板：多通道 + 自定义控制点 | 曲线效果 | 曲线求值成 1D LUT（`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★ | 剪映 UI 实测；manual 曲线章节 |
| 节点式调色 | 没有节点，调节层叠 | 节点图：串行 / 并行 / 层节点 + Key 输入 + 节点级 LUT / CDL | 没有，效果栈顺序执行 | 节点图（`[随包文档]`） | 需逆向｜公开文档化｜— | 直接抄设计 | ★★★★ | manual Color 页节点章节；`SetLUT()` / `SetCDL()` 的 1-based `nodeIndex` |
| 色彩管理 | canvas 色彩空间（sRGB / 709 / 2020）+ 素材级色彩空间 | RCM + 节点级 CST + 随包 OCIO 2.5 | OCIO 内建（27.0 增强） | 色彩变换管线（`[实测]`，包内有 OCIO 2.5） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★★ | 随包 `OpenColorIO_2_5`；`Plugins/opencolorio` |
| HDR | 有限，只有 HDR 导出档 | HDR10 / HLG / Dolby Vision + 动态元数据 | HDR 支持有限 | 色彩 + 元数据（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 可借鉴 | ★★★★ | manual HDR 章节 |
| 限定器 / 二级键 | HSL 选择（色调范围选点） | Qualifier：HSL / 3D 键 + 窗口限定 | Keylight + 效果键控 | GPU 键控（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | manual Qualifier 章节 |
| 窗口跟踪 | 没有 | 窗口跟踪（点 / 平面），窗口跟随运动 | 蒙版跟踪 | 跟踪算法（`[随包文档]`） | —｜公开文档化｜公开文档化 | 换成开源实现 | ★★★★ | manual 窗口跟踪章节 |
| 版本堆与对比 | 没有 | 片段版本堆 + 分屏对比 + `Gallery.xml` 静帧库 | 没有 | 版本表（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `pLmVerTable` 的 `LmVersion`；`drp_extract/Gallery.xml` |
| 肤色与美颜 | 美颜：磨皮 / 瘦脸 / 美白，人脸关键点驱动 | 没有，靠皮肤柔化类 OFX | 没有 | AI 人脸关键点（`[推断]`） | 需逆向｜—｜— | 换成开源实现 | ★★★ | 剪映 `models/` 人脸模型包 |
| 色彩空间转换节点 | 素材级转换 | CST 节点：输入 / 输出 / 色调映射三组参数 | OCIO Convert / Lumetri | 色彩变换（`[随包文档]`） | —｜公开文档化｜公开文档化 | 换成开源实现 | ★★ | manual CST 章节 |

### ⑨ 渲染与导出

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 渲染管线 | VECreator 合成 + FFmpeg 编码（`avcodec-61` 系、`SvtAv1Enc`、`dav1d`、自研 ByteVC 解码） | 自研 GPU 管线 + 内置编码器（ProRes / BRAW / JPEG2000 / IMF） | 渲染引擎 + Output Module | GPU 合成 + 编码器绑定（`[实测]`） | 需逆向｜需逆向｜需逆向 | 换成开源实现 | ★★★★ | 剪映编码 DLL 清单；达芬奇 `kdu` / `ProResRAW` / `BlackmagicRawAPI` |
| 无头渲染 | `jianying-agent-cli.exe draft` 子命令可用；`lyra-cli.exe` 要宿主签名握手，裸调返回 `err_code:-100015` | `Resolve.exe -nogui` + 端口 1144；官方写明支持，隔离副本实测未通 | `aerender.exe -project x.aep -comp Main -s 0 -e 99` | 命令 + 脚本（`[实测]` / `[实测-失败]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `jianying-agent-cli.exe --help`；`fuscript.exe`；`aerender` |
| 分段并行 | 分片并行编码，多档质量同出 | 多 GPU + 分布式渲染 | aerender 多实例 + 帧段 | 任务分片（`[推断]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★★ | 三家渲染设置页；`aerender` 参数 |
| 硬件编码 | NVENC / QSV / AMF + SVT-AV1 + 自研字节编码 | NVIDIA / AMD / Intel 编码 + 自家 RAW 编解码 | 通过输出模块与第三方插件 | 硬件编码器绑定（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | 剪映 `dav1d` / `SvtAv1Enc`；达芬奇 `BlackmagicRawAPI` |
| 编码格式覆盖 | H.264 / H.265 / AV1 / ProRes 系，档位分免费与会员 | 极宽：ProRes / JPEG2000 / IMF / DNxHR / BRAW / H.265 | 靠 QuickTime 与第三方插件 | 编码器集成（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 换成开源实现 | ★★★ | manual 交付格式表 |
| 渲染队列 | 单任务 + 批量导出 | Render Queue 多 job + 预设可导入导出成 XML | Render Queue + 输出模板 | 任务队列（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `_research/d4_render_audio.txt` 第 4194 页预设章节 |
| 渲染钩子脚本 | CLI 退出码 + JSON 结果 | 渲染开始 / 结束脚本，带 job id、status、errors 变量 | aerender 前后脚本 | 脚本层实现（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | `Scripting/README.md` 的 Render Scripts 与 Composition Logic 段 |
| 代理与优化媒体 | 代理模式，低码率替身 | Optimized Media + Proxy Mode 两档 | 代理 + 预渲染 | 媒体替身（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | manual Optimized Media 章节 |
| 帧精确 seek | 内核按 µs seek | GPU 帧服务器 | 帧缓存 | 帧服务（`[推断]`） | —｜—｜— | 直接抄设计 | ★★★★ | 三家播放行为实测 |
| 导出预设与平台适配 | 平台预设（竖屏 / 横屏 / 码率档） | Render Preset，XML 可导入导出 | Output Module Template | 参数化模板（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | 第 4194 页预设导入导出流程 |
| 音频随片渲染 | 混流进容器 | 多轨混音渲染 + 分轨导出 | 音频输出模块 | 混流（`[随包文档]`） | —｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | manual 交付章节 |
| 色彩标记写出 | 写 BT.709 标记 | 写 HDR 元数据与色彩标记 | 色彩标记有限 | 元数据写出（`[推断]`） | —｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | manual 交付与 HDR 章节 |

### ⑩ 自动化与 Agent

| 功能 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 实现方式判定 | 公开程度 | 我们复用度 | 开发难度 | 技术来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 脚本语言与入口 | 没有公开脚本 API；入口是 CLI + JSON patch + Lyra 协议 | Lua 5.1（`fuscript.exe`）+ Python 3.14（`ResolvePython.exe`）+ Workflow Integration（Electron/JS） | ExtendScript（ES3 JSX）+ CEP 面板 + UXP 面板 | 脚本层实现（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★★ | `Support/Developer/Scripting/README.md` 全篇 |
| API 规模 | 17 域 200+ 原生编辑命令：draft / track / segment / video / audio / text / textTemplate / sticker / effect / filter / adjustment / keyframe / template / attachment / story / undoRedo / batch | 22 类 530 方法（`.pyi` 3645 行 / 163KB） | ExtendScript DOM 数百对象 + UXP 新 API | 命令表 / 对象模型（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | 剪映 `app-server.mjs` 的 FN3 命令表；`DaVinciResolveScript.pyi` |
| 进程间通道 | CLI 子进程 + 本地 JSON 文件交换 | `fusionscript.dll`（3.55MB）+ 端口 1144 + 外脚本三档（None / Local / Network） | 命名管道与 COM（ExtendScript）+ UXP IPC | IPC 与桥接库（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `fusionscript.dll`；Preferences 外脚本三档配置 |
| AI 改工程协议 | Lyra XMLDraft v1/v2：Selection Expression 选点 + Mutation 六类（attr / removeAttr / appendXml / replaceWithXml / remove / empty / reorderChildrenById） | 没有协议，脚本逐步改 | 没有协议，脚本逐步改 | DSL + 变换（`[随包文档]`） | 需逆向｜—｜— | 直接抄设计 | ★★★★ | `canvas_agent/skills/jianying.hub.studio_lyra_xml_timeline_builder_v2/` 全套参考 |
| 事务与补丁 | `draft_patch` 三段式 CLI：`plan-patch` → `validate-patch` → `apply-patch` | 没有，脚本自行保证幂等 | 没有，脚本自行保证幂等 | 事务模型（`[实测]`） | 需逆向｜—｜— | 直接抄设计 | ★★★ | `jianying-agent-cli.exe --help` 实测 usage |
| 外部 Agent 宿主 | `DeepAgentsService.dll`（4MB）+ `deepagents_capi.dll`（37MB）+ `canvas_agent` runtime（`app-server.mjs` 12.3MB）+ `agent_runtime_addon.node` | Workflow Integration（Electron + CEF） | CEP / UXP 面板 + 第三方 MCP | Agent 运行时（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★★ | 剪映 DLL 清单；`Plugins/ChromiumEmbeddedFramework` |
| 工具面与 MCP | Agent 工具 = 200+ 命令 + `canvas_agent/skills` 全套 SKILL.md 目录 | 脚本方法即工具（530 方法可逐个暴露） | ExtendScript / UXP 方法即工具 | 工具注册表（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | 剪映 skills 目录树；`.pyi` 方法表 |
| 端侧模型 | `models/` 46 个包约 240MB，后端四路：onnxruntime(CUDA)、OpenVINO、QNN NPU、ByteNN | `llama.dll` + `mtmd.dll` + `ggml-cuda.dll`；`llama.dll` 的调用方 `[未证实]` | 没有 | AI 模型推理（`[实测]`） | 需逆向｜需逆向｜— | 换成开源实现 | ★★★★ | 剪映 `models/`；达芬奇 DLL 导入表 |
| 事件与回调 | 没有公开事件，CLI 一次性调用 | 渲染脚本 + Fusion 工具内脚本（Frame / Start / End Render） | 没有，脚本轮询 | 回调注入（`[随包文档]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | `Scripting/README.md` 的 Composition Logic 段 |
| 面板扩展位 | Lynx 前端 + CEF 内嵌页面 | Workflow Integration（Electron）+ OGraf HTML 模板 | CEP（HTML/JS）+ UXP（新栈） | WebView 宿主（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | `libcef.dll` / `lynx.dll`；OGraf 文档 |
| 远程与网络 | 没有公开通道 | 外脚本可配 Local / Network，协作库走 PostgreSQL | 没有 | 网络协议（`[随包文档]`） | —｜公开文档化｜— | 可借鉴 | ★★★ | `Scripting/README.md` Configuration 段 |
| 调试与可观测 | CLI `--output` JSON + 错误分类码（如 `err_category:runtime` / `err_code:-100015`） | Console 交互 + 脚本错误回抛 | ExtendScript Toolkit 退役，UXP DevTools | 日志与错误码（`[实测]`） | 需逆向｜公开文档化｜公开文档化 | 直接抄设计 | ★★ | `lyra-cli.exe` 错误 JSON 实测 |
| 模板驱动成片 | 云端成片服务 + 本地草稿拼装 | 没有 | MOGRT + 脚本灌参 + aerender 出货 | 云端 API + 模板（`[推断]`） | 闭源黑盒｜—｜公开文档化 | 可借鉴 | ★★★ | 剪映云 SDK（`ever_cloud_sdk`）；AE MOGRT + aerender |
| 批处理排队与并发 | 没有 | Render Queue 串行 + 多机分布式 | aerender 多实例 | 队列（`[随包文档]`） | —｜公开文档化｜公开文档化 | 直接抄设计 | ★★★ | manual 渲染队列章节 |

---

### 三家各自不可替代的三件事

#### 剪映

1. **Lyra XMLDraft 协议：把工程当文档改，不当数据库改。** Selection Expression 先选节点，Mutation 八类（attr / removeAttr / appendXml / replaceWithXml / remove / empty / reorderChildrenById 等）再局部改 XML 片段，AI 只提交「选点 + 片段」，宿主负责重排时间轴。抄不来的点：这套协议和它的 200+ 原生命令表、undoRedo 域是三向绑定的，命令语义写在 `app-server.mjs` 里，光看 XML 学不到「改完怎么让内核重算」。
2. **微秒时间基 + 46 类扁平材质表。** 全工程一个 JSON，材质平铺，AI 一次读全、一次改准；微秒让帧率无关的剪辑（29.97 / 25 / 60 混剪）不用换算。抄不来的点：扁平表意味着所有跨对象引用靠 id 字符串，这是海量草稿喂出来的工程决策，改结构等于重写渲染与导出的对齐逻辑。
3. **端侧模型货架。** `models/` 46 个包约 240MB，配 onnxruntime(CUDA)、OpenVINO、高通 QNN(Hexagon NPU)、自研 ByteNN 四路后端，断网也能跑智能抠像、字幕识别、踩点。抄不来的点：四路后端的选择逻辑与模型量化版本是硬件厂联调出来的，换机型就换模型包。

#### 达芬奇

1. **三层色彩管线：RCM + 节点级 CST + 随包 OCIO 2.5。** 工程级、片段级、节点级三层色彩变换可叠加，配 `SetLUT()` / `SetCDL()` 的 1-based 节点索引，脚本能精确点到某个节点的某个 LUT。抄不来的点：OCIO 2.5 + ACES 2.0 的配置集和它的 GPU 求值是逐像素对齐过的，配错了就是整条片子偏色。
2. **Fairlight FlexBus 与沉浸声链。** 子混 / 总线 / VCA / Link Group 四层路由，VST3 + AU + Fairlight FX 三套插件层，Atmos 走 RMU + re-render 预设，Bounce Mix to Track 一次过出多份交付。抄不来的点：48 轨以上的实时混音调度与 Dolby 授权件是两回事，前者是工程活，后者是商务活。
3. **工程即明文（`.drp` = zip + XML）+ 530 方法脚本 API。** 外部程序能整工程读写、能无头跑，`project.xml` 里连 `DbPrjVer` 与 `TimelineHandleVec` 都摆在明面上。抄不来的点：这套 XML 结构跟 Fusion 的 `CompositionBA` 压缩块、版本堆 `pLmVerTable` 咬合，缺一块就读不出工程。

#### AE

1. **表达式引擎：每个属性都是可编程的。** JS 子集 + 时间/空间插值的双插值模型 + 逐属性重算，能做到「一个滑杆驱动 300 个图层的参数」。抄不来的点：表达式沙箱、增量重算、循环依赖检测三件事绑在一起，重写等于自研一个小 JS 运行时。
2. **效果栈 + 图层 + 预合成的自由度。** 任意深度嵌套、任意混合模式组合、蒙版与轨道遮罩交叉，没有「轨道类型」的限制。抄不来的点：自由度换来的是一次渲染要遍历的图很大，能扛住这个规模的缓存与调度才是本体。
3. **MOGRT + aerender 的工业化出货链。** 模板暴露控件、脚本灌值、`aerender` 批渲染，一条命令出几百条带参数的成片，配 `-s` / `-e` 帧段切分。抄不来的点：MOGRT 的控件 schema 与工程内部参数表的对应关系闭源，第三方只能靠脚本 `setValue` 反推。

---

### 三家都做得烂的三件事

#### 1. 工程文件是给自家程序用的，不是给程序用的 API

- **现象**：剪映改完 draft 要重载工程才生效，`draft_patch` 还得走三段式；达芬奇 `.drp` 里 `FieldsBlob` 是私有 TLV，`CompositionBA` 是压缩 blob，外部程序只能整块搬运，局部改拿不到入口；AE 的 RIFX 干脆没有公开规范，第三方解析器全靠猜。三家的共同毛病是：**没有一个带 schema 的增量写入口**。
- **我们的做法**：AVS = SQLite 单库 + JSON/XML 双视图导出（抄达芬奇 `.drp` 的「明文可读 + 分片」形态），所有写入走 Command 总线，每条命令带 schema 版本与 pre/post 快照，AI 与 UI 走同一套写入路径；再配事件溯源，任意 revision 可回放。

#### 2. AI 能力锁在云端或会员档里，且编排不了

- **现象**：剪映的智能成片、花字、音色走云，端侧只放抠像与识别；达芬奇的 `llama.dll` + `mtmd.dll` 只喂自己 UI，脚本层拿不到模型调用；AE 27.0 干脆没有 AI。三家里没有一家把模型暴露成可编排的工具。
- **我们的做法**：模型货架本地化（llama.cpp + ONNX Runtime + Vulkan Compute 三后端），统一 provider 抽象，模型调用与编辑命令一起注册进 MCP 工具表，外部 Agent 与内部 Editor Agent 用同一份工具描述。

#### 3. 时间基与单位三家互不兼容，交换格式必然丢字段

- **现象**：剪映微秒、达芬奇帧、AE 秒；走 OTIO 或 FCPXML 一过，关键帧曲线类型、特效参数、蒙版形状这三类信息基本丢干净。达芬奇官方文档写「OTIO 比 AAF 与 XML 兼容性更好」，实测下来丢字段一样丢。
- **我们的做法**：内部统一 64 位 tick（1/1e6 秒，对齐剪映的微秒）+ 每个属性带 unit 元数据；导入导出走「逐字段映射 + 丢失清单」，转换完直接给用户一张「哪些字段没搬过去」的表，不做静默丢弃。

#### 补两条（同一批坑里挖出来的）

4. **撤销与脚本层打架。** 达芬奇脚本没有 undo 分组，AE 脚本执行期间多数操作不入栈，剪映只有 UI 撤销。我们的做法：所有 API 默认在事务里，可 group、可 dry-run、可回滚到任意 revision，脚本跑一半失败能整组回退。
5. **预览管线和渲染管线是两条。** 三家都存在「显示的和导出的不一致」，尤其在色彩、字体、混合模式上。我们的做法：FrameServer 单一渲染路径，预览就是渲染的低分辨率分支，两边共用同一份节点求值结果。

---

### 复用优先级矩阵

阶段定义（与 `G_开发路线图.md` 对齐）：

| 阶段 | 主题 |
| --- | --- |
| 1 | 桌面壳 + 工程库 + 命令总线 |
| 2 | 时间轴数据模型 + AVS schema + 导入导出 |
| 3 | 解码 / 预览 / 代理 / 色彩底座 |
| 4 | 合成节点图 + OFX 宿主 + 变换蒙版 |
| 5 | 字幕文字 + 音频引擎 |
| 6 | 渲染导出 + 硬件编码 + 队列 |
| 7 | Agent + MCP + 端侧模型 |

按投入产出排序（P0 = 先做，ROI 最高）：

| 序 | 条目 | 抄什么 | 投入 | 产出 | 优先级 | 阶段 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 命令总线 + 三段式补丁 | 剪映 `plan-patch` → `validate-patch` → `apply-patch`，写入全部走命令 | ★★ | 全系统唯一写入路径，AI 与 UI 打通，事务可回滚 | P0 | 1 |
| 2 | 命令表按域分组命名法 | 剪映 17 域 200+ 命令的切分法（draft / track / segment / video / audio / text / effect / filter / adjustment / keyframe / template / batch） | ★ | 命令面一次定死，后面加功能只加命令不改架构 | P0 | 1 |
| 3 | 工程 = SQLite 库 + ZIP(XML) 导出 | 达芬奇 `.drp` 的双形态：运行态进库，交付态出明文包 | ★★ | 崩溃不丢工程，外部程序能读能改 | P0 | 1 |
| 4 | 无头 CLI 契约 | 剪映 `jianying-agent-cli` 的 stdin/stdout JSON + 错误分类码（`err_category` / `err_code`） | ★ | Agent 与 CI 都能驱动，错误可机器判别 | P0 | 1 |
| 5 | 扁平材质池 + 双时基区间 | 剪映 `materials` 46 类 + segment 的 `target_timerange` / `source_timerange` 分离 | ★★ | 变速、裁剪、替换三件事互不污染 | P0 | 2 |
| 6 | 64 位 tick 时间基 + unit 元数据 | 剪映微秒 + 自研单位标注 | ★ | 混帧率工程不换算，跨软件转换有据 | P0 | 2 |
| 7 | 替换策略枚举 | 剪映 `ShrinkMode` / `ExtendMode` 八种策略（cut_head / cut_tail / cut_tail_align / shrink / extend_head / extend_tail / push_tail / cut_material_tail） | ★ | 模板灌参不破时间轴，这是模板生意的地基 | P0 | 2 |
| 8 | OTIO 双向转换 + 丢失清单 | 达芬奇 OTIO 进出口 + 自研字段映射表 | ★★★ | 与外部 NLE 互通，且丢掉什么说得清 | P1 | 2 |
| 9 | 波形金字塔缓存 + 代理多档替身 | 剪映波形预生成 + 达芬奇 Optimized Media 与 Proxy 两档 | ★★ | 大工程拖动不卡，预览帧率稳 | P1 | 3 |
| 10 | 曲线对象与插值器解耦 | 达芬奇关键帧插值枚举 + AE 双插值模型 | ★★ | 关键帧系统一次做对，调色/动画/音频共用 | P1 | 3 |
| 11 | 节点图 + 求值缓存 | Fusion 节点求值模型（MediaIn → 工具链 → MediaOut） | ★★★★★ | 合成、调色、特效共用一套图，缓存命中即流畅 | P1 | 4 |
| 12 | OFX 1.4 宿主 | 达芬奇 `Plugins/*.plugin` 契约，直接吃 Resolve 与 Natron 插件 | ★★★★ | 插件生态白捡，不用自己养开发者 | P1 | 4 |
| 13 | 参数 schema 驱动 UI | OGraf Manifest：声明属性与控件类型，面板自动生成 | ★★★ | 加效果不改前端，第三方也能提交效果 | P1 | 4 |
| 14 | 效果 = 参数包 + 实现绑定 | 剪映 effect / filter / transition 材质模型（滤镜 = LUT + 强度） | ★★★ | 效果与 UI、预设、云下发三处一次对齐 | P1 | 4 |
| 15 | 像素着色器 DSL | DCTL 语法（C 风格，一份源码多后端编译） | ★★★★ | 调色与特效的自研表达力，替代写死 shader | P2 | 4 |
| 16 | 版本堆 + 静帧库 | 达芬奇 `pLmVerTable` 与 `Gallery.xml` | ★★★ | 调色不怕改坏，客户比稿直接切版本 | P2 | 5 |
| 17 | 字幕轨 ↔ 文字层双视图 | 剪映 text 轨 + 达芬奇 Subtitle 轨的并存做法 | ★★ | 字幕可批量处理，文字层可精修 | P2 | 5 |
| 18 | 渲染队列 job 对象 + 预设 XML | 达芬奇 Render Queue 与预设导入导出 | ★★★ | 交付可重放，团队预设可分发 | P2 | 6 |
| 19 | 渲染钩子脚本 | 达芬奇渲染开始/结束脚本 + 上下文变量（job id / status / errors） | ★★ | 对接云转码与通知，出货自动化 | P2 | 6 |
| 20 | 工具表 → MCP tool 直映射 + 端侧模型货架 | 剪映 17 域命令表与 `models/` 四后端模型货架 | ★★★★ | 外部 Agent 直接控工程，断网也有 AI 能力 | P2 | 7 |

---

### 附：`[未证实]` 行索引

本文标 `[未证实]` 的位置，共 5 处，对应主表行：

- ① 工程加密与混淆：剪映 draft 加密算法本身未拿到，只有社区的探测结论。
- ④ 表达式与程序化：剪映 Selection Expression 的完整语法未拿到，随包 skill 只覆盖常用子集。
- ⑤ 插件 ABI：剪映作为 OFX 宿主的实际加载路径未抓到运行时证据。
- ⑦ 变声与音色：剪映本地模型与云 API 的分界线未定。
- ⑩ 端侧模型：达芬奇 `llama.dll` 的调用方进程与调用链未抓到。

---

## 第四部分　GitHub 开源项目技术清单
﻿# C GitHub 开源项目技术清单

> 工程目录：`C:\AI Video Studio工程参考`
> 采集时间：2026-11-20（时区 +08:00）
> 基线：`第一部分` 的 12 层技术地图 · `F_技术选型报告.md` 的四种判定 · `G_开发路线图.md` 的七阶段
> 覆盖项目：83 个，分 10 组（其中 2 个因仓库路径拿不到，star 与版本标「未核实」，另有 5 个缺 Release 语义只标 star 与提交时间）

---

### 0. 数据口径（先看这段，后面所有数字都按这套读）

| 字段 | 取法 | 抓不到时 |
| --- | --- | --- |
| Star | `github.com/<owner>/<repo>` 页内嵌 JSON 的 `stargazerCount` | 标 `未核实` |
| 开源协议 | 同页 `license.spdxId`；GitHub 识别成 `NOASSERTION` 的，回读仓库根部 `LICENSE*` / `COPYING` 正文再判 | 标 `未核实` |
| 最新 Release | `<repo>/releases.atom` 首条 `<title>` + `<updated>`；无 release 语义的项目退到 `tags.atom`，结果前缀 `tag:` | 标 `未核实` |
| 交叉核对 | 关键项目另打 `api.github.com/repos/<owner>/<repo>` 与 `/releases/latest` 对一遍（FFmpeg、OpenTimelineIO、onnx 三项已对） | — |

三条读取纪律，写进本文所有表格：

1. **「能嵌 C++/Win」的判据 = 在 MSVC 下能否链成一个能在 64 位 Windows 上跑的 DLL 或静态库**，判的是「有没有 Windows 版软件」之外的那件事。
2. **「官方绑定」只算官方仓库里自带的语言绑定**，第三方 wrapper 不算。
3. **协议写全称 + 版本**。LGPL 一律带上「动态链接」四个字，因为静态链会给闭源分发留下重链接义务。

本次采集里有两类特例，先摊开说，免得后面每行重复标注：

- **FFmpeg 的 `spdxId` 是 `NOASSERTION`**，回读 `LICENSE.md` 正文确认：主体是 LGPL-2.1-or-later，夹着 MIT/BSD 片段，另有可选 GPL 组件（`--enable-gpl` 才生效）。清单里按 LGPL-2.1-or-later 记。
- **MCP 系列三个仓库的开源协议正在从 MIT 迁到 Apache-2.0**（`LICENSE` 正文原话：新代码与规范贡献走 Apache-2.0，文档贡献除外）。清单里按「MIT → Apache-2.0 迁移中」记，新写代码按 Apache-2.0 走。

---

### 1. 媒体解码编码

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| FFmpeg | `FFmpeg/FFmpeg` | LGPL-2.1-or-later（默认；加 `--enable-gpl` 后整体转 GPL-2.0-or-later） | C | 67.7k | n9.1 / 2026-11-20 |
| FFmpeg-Builds | `BtbN/FFmpeg-Builds` | MIT（脚本本身） | Shell | 12.0k | Auto-Build 2026-11-19 |
| libjxl | `libjxl/libjxl` | BSD-3-Clause | C++ | 3.9k | v0.13.0 / 2026-11-11 |
| libavif | `AOMediaCodec/libavif` | BSD-2-Clause | C | 2.2k | v1.4.2 / 2026-05-26 |
| libwebp | `webmproject/libwebp` | BSD-3-Clause | C | 2.4k | v1.6.0 / 2025-07-09 |
| libplacebo | `haasn/libplacebo` | LGPL-2.1 | C | 813 | v7.387.0 / 2026-10-25 |
| OpenH264 | `cisco/openh264` | BSD-2-Clause | C++ | 6.2k | 2.7.0 / 2026-10-22 |
| oneVPL | `oneapi-src/oneVPL` | MIT | C++ | 373 | v2.17.0 / 2026-06-25 |

逐项落地判定：

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| FFmpeg | 能 | C API（无官方 C++ 绑定） | `libavformat/`（`mov.c`、`matroskadec.c`、`mxfenc.c`）、`libavcodec/`（`decode.c`、`nvenc.c`、`qsvenc.c`、`amfenc.c`）、`libavfilter/`（`vf_zscale.c`、`vf_lut3d.c`、`vf_tonemap*.c`）、`libavutil/hwcontext_d3d11va.c`、`libswscale/`、`libswresample/` | 动态库（`avcodec-*.dll` 家族）+ 自写 C++ 封装层 | 9.x 已删旧编码 API，只能走 `send_packet/receive_frame`；不加 `--enable-gpl` 则 x264/x265 与非自由解码器全没有；MSVC 直接编要过一遍 MinGW 兼容补丁 |
| FFmpeg-Builds | 不需要嵌 | 无 | `scripts.d/` 里的依赖编排脚本、三档产物（`gpl-shared` / `lgpl-shared` / `lgpl-static`） | 取产物 | 产物协议由构建参数决定，`gpl` 档进闭源安装包会把整个产物拽成 GPL |
| libjxl | 能 | C API（`lib/include/jxl/decode.h`）+ C++ API | `lib/jxl/dec_frame.cc`、`lib/jxl/enc_frame.cc`、`lib/extras/dec/jxl.cc`、`tools/djxl.cc` | 动态库 `jxl.dll` 或静态 `jxl-static` | 编码慢一个量级；只解 JXL 码流，动图容器与色彩元数据要自己接 |
| libavif | 能 | C API（`include/avif/avif.h`） | `src/codec_dav1d.c`、`src/codec_aom.c`、`src/reformat_libyuv.c`、`src/scale.c` | 静态/动态均可（CMake） | 不做解码器，dav1d 与 aom 二选一挂上去；编码只认 aom/rav1e/svt |
| libwebp | 能 | C API（`src/webp/decode.h`） | `src/dec/`、`src/enc/`、`src/demux/`（动图容器）、`src/mux/` | 动态库 `libwebp.dll` | 动图无音轨；只当贴纸与缩略图资产通路 |
| libplacebo | 能 | C API（`include/libplacebo/renderer.h`） | `src/renderer.c`（色调映射、色彩管理）、`src/shaders/colorspace.c`、`src/shaders/scaling.c`、`src/gpu/d3d11/` | 动态库（LGPL 纪律） | D3D11 后端能力弱于 Vulkan 后端；shader 编译链要自带 glslang；版本号跳得凶（v7.387），API 半年一漂 |
| OpenH264 | 能 | C API（`codec_api.h`） | `codec/decoder/`、`codec/encoder/`、`test/` | 动态库 `openh264-*.dll` | 只 H.264；Cisco 的二进制分发有专利池安排，商用发布前要读它的二进制分发条款 |
| oneVPL | 能 | C API（`vpl` 头） | `api/`（头与 ABI）、dispatcher 层 | 动态库 `vpl.dll` | 只吃 Intel 核显/独显的 QSV 通路；老 `libmfx` 与新 `oneVPL` ABI 两代并存，封装要分叉 |

**本轮结论**：这一组只上两个。

- **FFmpeg**（阶段 1 起）：全格式覆盖只有它，libav* 直连能拿到精确 seek、D3D11VA 零拷贝与色彩元数据三件东西，命令行那条路在精确帧定位上会崩。
- **libplacebo**（阶段 2 起）：HDR 色调映射与色彩空间转换本来要自己写一堆 WGSL，它有现成的；LGPL 动态链 + 自带 D3D11 后端，正好落在我们的渲染进程里。

OpenH264 与 oneVPL 是「补齐通路的零件」，进不进包取决于阶段 2 的硬件编码矩阵实测结果，不进 Top 12。

---

### 2. 时间轴与工程交换

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| OpenTimelineIO | `AcademySoftwareFoundation/OpenTimelineIO` | Apache-2.0 | C++ / Python | 2.1k | Beta 18.1 / 2025-11-09 |
| MLT Framework | `mltframework/mlt` | LGPL-2.1 | C | 1.9k | v7.42.0 / 2026-10-03 |
| pyJianYingDraft | `GuanYixuan/pyJianYingDraft` | Apache-2.0 | Python | 4.9k | v0.3.1 / 2026-10-14 |
| pyCapCut | `GuanYixuan/pyCapCut` | 未核实（根目录无 `LICENSE` 可读） | Python | 776 | v0.0.4 / 2026-10-16 |
| pyaaf | `markreidvfx/pyaaf` | MIT | Python | 51 | 1.0.0 / 2017-12-24 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| OpenTimelineIO | 能 | Python（`src/py-opentimelineio/`） | `src/opentimelineio/`（`timeline.cpp`、`track.cpp`、`clip.cpp`、`stack.cpp`、`transition.cpp`、`gap.cpp`）、`src/opentime/`（`rationalTime.cpp`、`timeRange.cpp`）、`adapters/fcp_xml`、`adapters/aaf`、`adapters/cmx_3600`、`adapters/otioz` | 静态库 `opentimelineio` + `opentime` | 它是「编辑信息的公共子集」：不含关键帧、不带效果参数、不做色彩空间解释；1.0 长期停在 Beta；C++ 核大量用异常，跨 DLL 边界要自己收 |
| MLT | 能 | C API（`mlt/framework/mlt.h`）+ C++ 包装 `src/mlt++/` | `src/framework/`（`mlt_producer.c`、`mlt_playlist.c`、`mlt_tractor.c`、`mlt_transition.c`、`mlt_filter.c`）、`src/modules/avformat/`、`src/modules/qt/` | 动态库（LGPL 纪律） | `producer/playlist/tractor` 三件套绑死播放管线，与我们的命令总线语义冲突；拿它当内核，每加一个 AI 能力都要跟它的模型打架（第七部分已判缓做） |
| pyJianYingDraft | 只做参考 | 无 | `draft_content.json` 字段构造器（28 个顶层字段、46 类 materials、时间单位微秒）、`_src_script_file` 对应的 `ScriptFile`、`Track`、`TextSegment`、关键帧、蒙版、色度抠图参数、转场表 | 不集成，抄语义 | Python 侧、不渲染、靠剪映客户端出片；格式随剪映版本漂移（README 自标「10.8 ✅」） |
| pyCapCut | 只做参考 | 无 | 同源分支，CapCut 草稿字段 | 不集成 | 无协议文件可读，代码只当字段字典 |
| pyaaf | 只做参考 | 无 | `aaf2/` 对象模型（Mob / Slot / Component / TimelineMobSlot / OperationGroup） | 不集成 | 2017 年后停更；读能用，写复杂 AAF 会缺结构 |

**本轮结论**：这一组只上 OTIO。

- **OpenTimelineIO**（阶段 2 起做适配器骨架，阶段 7 全量）：FCPXML / AAF / EDL 三个适配器是白送的，`AVS ↔ OTIO` 双向映射写一次就同时解决「导出给别人」与「导入别人的时间轴」，第八部分阶段 7 的六格式往返验收直接靠它。

剪映草稿这一路只抄字段语义、不抄一行代码——那份 `draft_content.json` 的字段设计研究价值远高于代码价值。

---

### 3. 合成 / 特效 / 插件标准

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| OpenFX | `AcademySoftwareFoundation/openfx` | BSD-3-Clause | C++ | 590 | 1.5.1 / 2026-07-22 |
| OpenImageIO | `AcademySoftwareFoundation/OpenImageIO` | Apache-2.0 | C++ | 2.4k | v3.2.2.0 / 2026-10-28 |
| OpenEXR | `AcademySoftwareFoundation/OpenEXR` | BSD-3-Clause | C++ | 1.9k | v3.5.4 / 2026-11-12 |
| imgui-node-editor | `thedmd/imgui-node-editor` | MIT | C++ | 4.6k | v0.9.4 / 2026-10-14 |
| tinyexpr | `codeplea/tinyexpr` | Zlib | C | 1.9k | v1.1.1 / 2026-08-06 |
| Skia | `google/skia` | BSD-3-Clause | C++ | 11.0k | canvaskit/0.42.0 / 2026-08-18 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| OpenFX | 能 | 无（纯 C 头 + C++ 辅助类） | `include/ofxCore.h`、`include/ofxImageEffect.h`、`include/ofxParametricParam.h`、`include/ofxDrawSuite.h`、`Support/Library/ofxsImageEffect.cpp`、`ofxsMultiThread.cpp`、`ofxsParam.cpp`、`Support/HostSupport/` | 静态库 `ofxSupport` + 宿主侧自写 `OfxHost` 回调表 | 1.5 才有 Metal/CUDA/OpenCL 渲染入口与 `OfxDrawSuite`，主流第三方插件仍只认 CPU + OpenGL；参数求值模型是九十年代那套；它只管单效果，不管节点图 |
| OpenImageIO | 能 | Python | `src/libutil/`、`src/libtexture/`（`imagebuf.cpp`、`imagecache.cpp`、`texturesystem.cpp`） | 动态库 `OpenImageIO.dll` | 定位是图像库，视频要自己拆帧；拉一串图像依赖（OpenEXR / libtiff / libpng） |
| OpenEXR | 能 | Python | `src/lib/OpenEXR/`（`ImfHeader`、deep、multi-part）、`src/lib/OpenEXRCore/`（C API） | 动态库 `OpenEXR-3_5.dll` | 只 EXR；半浮/浮点带宽大（4K 一层 16f 就到 64MB） |
| imgui-node-editor | 能 | 无 | `imgui_node_editor.cpp`、`imgui_node_editor_api.cpp`、`imgui_canvas.cpp`（无限画布 + 连线 + 框选） | 静态库（源码 4 个文件直接进工程） | 后端跟 ImGui 走（DX11 / OpenGL）；无序列化，节点数据自己存；作者把 v0.9.4 标成「final v9 branch」，维护已进尾声，要 fork 自管 |
| tinyexpr | 能 | 无 | `tinyexpr.c`（单文件：`TE_EXPR` 树 + 变量/函数表） | 单文件直接编进工程 | 只算术，没有时间轴上下文变量；表达式引擎得在外面套一层（变量绑定表 + 按帧求值） |
| Skia | 能 | 无正式 C++ 绑定（CanvasKit 是 wasm 侧） | `include/core/`（`SkCanvas`、`SkPaint`、`SkImage`）、`src/gpu/ganesh/`（D3D12 / Vulkan 后端）、`modules/skshaper/`、`modules/svg/` | 静态库 + 自建构建 | 构建链重（GN + ninja + depot_tools）；API 半年一破；视频色彩管理不归它管，2D 绘制才有收益 |

**本轮结论**：只上两个。

- **OpenFX 1.5.1**（阶段 5）：写一次宿主，直接吃 Resolve / Natron / Nuke 生态的插件，效果数量这块不用自己攒。宿主四件事写死：扫 `*.ofx.bundle` → 解析 `Info.plist`/XML → 建 `OfxHost` 回调表 → 走 `describe/render`。
- **imgui-node-editor**（阶段 5）：节点画布、连线、框选、缩放这些交互是纯体力活，借它省两周；求值仍走自研 WGSL，第八部分阶段 5「20 节点级联 4K 单帧 < 120ms」的账算在自己手里。

tinyexpr 留作表达式引擎的词法层，包一层变量表就能用，成本一个下午，不占位置。

---

### 4. 色彩管理

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| OpenColorIO | `AcademySoftwareFoundation/OpenColorIO` | BSD-3-Clause | C++ | 2.1k | v2.6.0 / 2026-10-01 |
| colour-science | `colour-science/colour` | BSD-3-Clause | Python | 2.7k | 0.4.7 / 2025-12-06 |
| aces-dev | `AMPAS/aces-dev` | Apache-2.0 | C / CTL | 863 | v1.3.1 / 2024-12-20 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| OpenColorIO | 能 | Python（`src/bindings/python/`） | `src/OpenColorIO/`（`Config.cpp`、`FileTransform.cpp`、`Look.cpp`、`Processor.cpp`）、`src/OpenColorIO/GPU/`（`GpuShaderCreator` 产着色文本）、`src/apps/ociobakelut`、`src/apps/ocioconvert` | 动态库 `OpenColorIO_2_6.dll` | GPU 路径只吐着色器文本，D3D11/WGSL 后端要自己接；显示 ICC 不在它的范围；默认 config 是 ACES，非 ACES 流程要自己写 YAML |
| colour-science | 不嵌（Python） | 无 | `colour/models/rgb/`、`colour/colorimetry/` 里的色域矩阵、传递函数（PQ / HLG / S-Log3 / LogC）、白点适配公式 | 抄常量与公式，转成 C++ 常量表 | 纯 Python；公式对，但它是科学计算库，不做实时路径 |
| aces-dev | 部分（CTL 解释器要自带） | 无 | `transforms/ctl/`（ACES 2.0 输出变换、IDT、LMT）、`lib/ctl/`、`aces-core/` | 烘 LUT 或搬进 shader | CTL 没有官方 C++ 解释器；实时路径上 CTL 必须前置烘成 LUT 或改写成 WGSL |

**本轮结论**：**OpenColorIO 2.6.0 + ACES 2.0 config**（阶段 2）。

达芬奇的色彩管线和它是同一套 config，跟行业对齐这件事不用讨论；`GpuShaderCreator` 吐着色文本注入自家管线，正好落 第八部分阶段 2 的「像素差 < 1/255」验收。colour-science 只当常量表来源，aces-dev 只提供 CTL 原件用来烘 LUT。

---

### 5. 音频

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| JUCE | `juce-framework/JUCE` | AGPL-3.0 或商业双轨 | C++ | 9.2k | 9.0.6 / 2026-11-19 |
| RNNoise | `xiph/rnnoise` | BSD-3-Clause | C | 6.0k | 0.2 / 2024-04-15 |
| Rubber Band | `breakfastquay/rubberband` | GPL-2.0（另售商业授权） | C++ | 815 | v4.0.0 / 2024-10-25 |
| libsndfile | `libsndfile/libsndfile` | LGPL-2.1 | C | 1.7k | 1.2.2 / 2023-08-13 |
| miniaudio | `mackron/miniaudio` | Public Domain（Unlicense）或 MIT-0 | C | 7.7k | 0.11.26 / 2026-10-31 |
| DeepFilterNet | `Rikorose/DeepFilterNet` | Apache-2.0 或 MIT（双轨） | Rust + Python | 5.1k | v0.5.6 / 2023-08-31 |
| Demucs | `facebookresearch/demucs` | MIT | Python | 10.4k | v4.0.1 / 2023-09-07 |
| libebur128 | `jiixyj/libebur128` | MIT | C | 498 | v1.2.6 / 2021-02-14 |
| VST3 SDK | `steinbergmedia/vst3sdk` | MIT（SDK 本体） | C++ | 2.4k | v3.8.1_build_84 / 2026-08-11 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| JUCE | 能 | 无（本身是 C++ 框架） | `modules/juce_audio_devices/`（WASAPI / ASIO）、`modules/juce_audio_processors/`（VST3/AU 宿主）、`modules/juce_audio_formats/`、`modules/juce_dsp/`、`modules/juce_gui_basics/` | 静态库进 `audiofx.exe` | AGPL-3.0 会把整个应用拽成 AGPL；商业轨按营收/人头收费；拿它就得在「开源全应用」与「买授权」之间选一个（第七部分已定买 Indie 轨，或退到自研宿主） |
| RNNoise | 能 | C API（`include/rnnoise.h`） | `src/denoise.c`、`src/rnn_data.c`、`models/rnnoise_v2.0.model` | 静态库 | 48kHz 单声道写死，其他采样率要重采样；模型 2024 年后没再更新 |
| Rubber Band | 能 | C API（`rubberband/rubberband-c.h`） | `src/RubberBandStretcher.cpp`（实时/离线两套 API）、`src/StretcherProcess.cpp` | 只能进程外（`audiofx.exe`） | GPL-2.0；实时模式音质低于离线模式；变速质量与延迟要按用途分档 |
| libsndfile | 能 | C API（`sndfile.h`） | `src/sndfile.c`、`src/wav.c`、`src/rf64.c`、`src/broadcast.c`（BWF 元数据） | 动态库（LGPL 纪律） | 只读写文件不做处理；WAV/BWF 之外容器覆盖一般 |
| miniaudio | 能 | C API（单头 `miniaudio.h`） | `miniaudio.h`（设备、混音、重采样、`ma_decoder`、`ma_engine`） | 单头直接编进工程 | 20 万行单文件，首次编译慢；ASIO 要额外编 `ma_backend_asio`；工程里放两份会重定义 |
| DeepFilterNet | 能（C ABI） | 无 | `libDF/src/`（Rust 推理核）、`libDF` 的 C ABI 导出层、`DeepFilterNet/`（torch 训练侧） | 进程外 `ai.exe` 或 Rust→C 静态库 | 2023 年 8 月后停更；Rust 工具链进构建链；模型按 48kHz 训的 |
| Demucs | 不嵌（Python） | 无 | `demucs/htdemucs.py`、`demucs/apply.py`、`demucs/separate.py` | 进程外（`ai.exe`）或导 ONNX | torch 依赖重；分离一首 3 分钟要 GPU 秒级，CPU 分钟级 |
| libebur128 | 能 | C API | `ebur128.c`（单文件：EBU R128 / ITU-R BS.1770 响度 + true peak） | 单文件编进工程 | 要吃 48k 双声道，喂之前得自己重采样；只有测量，没有归一化动作 |
| VST3 SDK | 能 | 无 | `public.sdk/source/vst/hosting/`（`moduleloader.cpp`、`hostclasses.cpp`、`connectionproxy.cpp`）、`pluginterfaces/vst/` | 静态库进 `audiofx.exe` | SDK 是 MIT，但分发 VST3 插件要 Steinberg 的 VST3 授权协议；Windows 上是 COM 生命周期，插件崩在宿主进程里就是整进程带走（所以进程外托管） |

**本轮结论**：这一组定两个，JUCE 那条改判。

- **miniaudio + VST3 SDK 的 hosting 层**（阶段 5）：设备枚举、WASAPI 共享/独占、混音与重采样一个单头解决；VST3 的 `moduleloader.cpp` 与 `hostclasses.cpp` 是现成的插件加载与宿主实现，fork 进 `audiofx.exe` 就绕开了 JUCE 的 AGPL 传染——第八部分阶段 5 的「故意崩溃 5 个插件，应用无感」这条验收也用它实现。
- **RNNoise 0.2 + libebur128**（阶段 4）：降噪与响度归一（-14 LUFS ±0.5、真峰 -1 dBTP）是阶段 4 音频自动链的两端，这两个都是单文件级成本。

JUCE 只在商业授权预算落定的前提下才进，否则 AGPL-3.0 会让整个 `studio.exe` 变成开源义务。

---

### 6. 字幕与语音

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| whisper.cpp | `ggml-org/whisper.cpp` | MIT | C / C++ | 55.3k | v1.9.5 / 2026-10-07 |
| OpenAI Whisper | `openai/whisper` | MIT | Python | 113.1k | v20250625 / 2025-06-26 |
| faster-whisper | `SYSTRAN/faster-whisper` | MIT | Python | 26.9k | 1.2.1 / 2025-10-31 |
| WhisperX | `m-bain/whisperX` | BSD-2-Clause | Python | 25.5k | 3.8.7rc1 / 2026-06-26 |
| pyannote.audio | `pyannote/pyannote-audio` | MIT | Python | 10.8k | 4.1.1 / 2026-11-19 |
| sherpa-onnx | `k2-fsa/sherpa-onnx` | Apache-2.0 | C++ | 16.1k | v2.0.2 / 2026-11-20 |
| FunASR | `modelscope/FunASR` | MIT | Python | 21.1k | v1.4.27 / 2026-11-17 |
| libass | `libass/libass` | ISC | C | 1.2k | 0.17.5 / 2026-07-11 |
| Subtitle Edit | `SubtitleEdit/subtitleedit` | MIT | C# (.NET) | 15.1k | v5.5.0-beta10 / 2026-11-19 |
| Aegisub | `TypesettingTools/Aegisub` | BSD-3-Clause | C++ | 2.1k | 3.5.1 / 2026-10-17 |
| Piper | `rhasspy/piper` | MIT | Python / C++ | 11.3k | 2023.11.14-2 / 2023-11-14 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| whisper.cpp | 能 | C API（`include/whisper.h`） | `src/whisper.cpp`（`whisper_full`、`whisper_full_n_segments`）、`ggml/src/ggml-cuda/`、`ggml/src/ggml-vulkan/`、`examples/main/` | 静态库进 `ai.exe` | CPU 跑 large 很慢；时间戳是按 token 推的近似值，不是强制对齐 |
| OpenAI Whisper | 不嵌 | 无 | `whisper/model.py`、`whisper/decoding.py`（参考算法） | 不集成 | 参考实现，工程上是 faster-whisper 的上游 |
| faster-whisper | 不嵌（Python） | 无 | `faster_whisper/transcribe.py`、`faster_whisper/vad.py`（Silero VAD）、ctranslate2 后端 | 进程外（`ai.exe`） | CTranslate2 不承诺稳定 C++ ABI，封 C++ 层是长期负债 |
| WhisperX | 不嵌 | 无 | `whisperx/alignment.py`（wav2vec2 强制对齐）、`whisperx/diarize.py`、`whisperx/assign_word_speakers.py` | 进程外 | 强制对齐要额外模型与显存；3.8.7 还是 RC，接口在动 |
| pyannote.audio | 不嵌 | 无 | `pyannote/audio/pipelines/speaker_diarization.py`、`models/pyannote/segmentation` | 进程外 | 权重在 HF 上要先过条款页；torch 依赖 |
| sherpa-onnx | 能 | C API（`sherpa-onnx/c-api/c-api.h`） | `sherpa-onnx/csrc/`（`OfflineRecognizer`、`OfflineTts`、`VoiceActivityDetector`、`SpeakerEmbeddingExtractor`）、`sherpa-onnx/c-api/` | 静态库 + ONNX Runtime | 模型要用官方脚本转 onnx；TTS 音色数量取决于你带的模型包 |
| FunASR | 不嵌 | 无 | `funasr/`（Paraformer、CT-Punc 标点、CAM++ 说话人） | 进程外 | Python + torch；对中文标点与口语更友好，是 faster-whisper 的中文侧补充 |
| libass | 能 | C API（`ass/ass.h`） | `libass/ass_render.c`、`ass_parse.c`、`ass_shaper.c`（harfbuzz + fribidi）、`ass_fontselect.c` | 动态库 `ass.dll` | 只管 SSA/ASS；字体要自带一套；竖排与部分现代排版特性要自己补 |
| Subtitle Edit | 不嵌（.NET） | 无 | 字幕格式转换矩阵（SRT / ASS / VTT / TTML / SCC / D-Cinema）、时间轴偏移与对齐算法、OCR 流程 | 只抄算法 | WinForms 程序，代码搬不进 Qt C++ |
| Aegisub | 参考 | 无 | `src/subtitle_format_*.cpp`（十余种格式读写）、`src/audio_*.cpp`（波形打轴） | 只抄逻辑 | wxWidgets 强耦合，摘模块比自己写贵 |
| Piper | 部分 | 无 | `piper/` 的 onnx 推理、音素化脚本 | 进程外 | 音素化依赖 espeak-ng（GPL-3.0），进闭源包前要隔离 |

**本轮结论**：这一组定两个。

- **whisper.cpp v1.9.5**（阶段 3）：CPU 兜底转写，C API 干净，`ggml` 的 CUDA/Vulkan 后端同仓，没独显的机器也能跑完 3 小时素材。
- **sherpa-onnx v2.0.2**（阶段 3）：一个 C API 里塞了 ASR、VAD、TTS、说话人嵌入四件事，阶段 3 的分析管线不用同时挂三套运行时；Apache-2.0 干净。

字幕渲染单独定 **libass**（阶段 4 包装环节）：ASS 的花字与逐字动画生态在它这一层，自研渲染器要补的是 harfbuzz 整形与 SSA 语义两大块。

---

### 7. 视频理解与 AI

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| llama.cpp | `ggml-org/llama.cpp` | MIT | C / C++ | 135.8k | b12557 / 2026-11-19 |
| ONNX Runtime | `microsoft/onnxruntime` | 未核实 | C++ | 未核实 | 未核实 |
| ONNX 规范 | `onnx/onnx` | Apache-2.0 | C++ / Python | 21.7k | v1.23.2 / 2026-10-06 |
| OpenVINO | `openvinotoolkit/openvino` | Apache-2.0 | C++ | 11.6k | 2026.4.1 / 2026-10-01 |
| DirectML | `microsoft/DirectML` | MIT | C++ | 2.6k | torch-directml 0.2.4 / 2024-08-19 |
| SAM 2 | `facebookresearch/sam2` | Apache-2.0 | Python | 20.2k | 无 GitHub release（未核实） |
| PySceneDetect | `Breakthrough/PySceneDetect` | BSD-3-Clause | Python | 5.6k | v0.7.3 / 2026-11-08 |
| Ultralytics | `ultralytics/ultralytics` | AGPL-3.0 | Python | 63.6k | v8.4.216 / 2026-11-20 |
| ByteTrack | `ifzhang/ByteTrack` | MIT | Python | 6.8k | 无 GitHub release（未核实） |
| BiRefNet | `ZhengPeng7/BiRefNet` | MIT | Python | 4.4k | BiRefNet-v1 / 2025-04-22 |
| Robust Video Matting | `PeterL1n/RobustVideoMatting` | **GPL-3.0** | Python | 9.6k | Initial release / 2021-09-17 |
| Real-ESRGAN | `xinntao/Real-ESRGAN` | BSD-3-Clause | Python | 37.6k | v0.3.0 / 2022-09-20 |
| diffusers | `huggingface/diffusers` | Apache-2.0 | Python | 35.0k | 0.43.0 / 2026-11-12 |
| ComfyUI | `comfyanonymous/ComfyUI` | GPL-3.0 | Python | 147.7k | v0.46.1 / 2026-11-19 |
| InsightFace | `deepinsight/insightface` | 未核实（根目录无 `LICENSE` 可读） | Python | 30.3k | Model Zoo / 2026-10-03 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| llama.cpp | 能 | C API（`include/llama.h`） | `src/llama.cpp`、`ggml/src/`、`tools/mtmd/`（图文多模态）、`tools/server/`（OpenAI 兼容 HTTP） | 静态库 + CUDA/Vulkan 后端 | 无版本语义（滚动 build 号）；显存紧时上下文一缩再缩；VLM 能力取决于挂哪份 mmproj |
| ONNX Runtime | 能 | C / C++ / C# / Python（官方多语言） | `onnxruntime/core/`（session、graph）、`onnxruntime/core/providers/{cuda,dml,qnn,openvino}/` | 动态库 `onnxruntime.dll` + EP 插件 | 仓库页与 API 两条路径都返回 404 / 连接中断，star 与版本号均未核实；C++ API 的 ABI 跨版本不保证 |
| ONNX 规范 | 能 | Python | `onnx/defs/`（opset 定义）、`onnx/checker.cc` | 只当规范与校验器 | 规范本身不跑推理；opset 版本与各家 EP 的支持矩阵要自己维护 |
| OpenVINO | 能 | C++ / C / Python | `src/inference/`、`src/plugins/intel_gpu/`、`src/plugins/intel_npu/`、`tools/benchmark_tool/` | 动态库 | 只有落 Intel 的 GPU/NPU 才有性能优势；模型先转 IR/OVC |
| DirectML | 能 | C++（`DirectML.h`） | `DirectMLX.h`、DML 算子头，配 `onnxruntime-dml` EP | 系统组件（`DirectML.dll` 随 Win 走）+ 头文件 | 通用 GPU 后端，性能不如三家原生；更新慢（2024 后无新版） |
| SAM 2 | 不嵌 | 无 | `sam2/modeling/`（`SAM2ImagePredictor`、`SAM2VideoPredictor`）、`sam2/utils/misc.py`、自动 mask 生成脚本 | 进程外 | 视频推理吃显存；要提示（点/框）才出好结果；无 C++ 绑定 |
| PySceneDetect | 不嵌（Python） | 无 | `scenedetect/detectors/content.py`（`ContentDetector`）、`adaptive.py`（`AdaptiveDetector`）、`threshold.py`、`scenedetect/scene_manager.py` | 进程外（`ai.exe`），输出 `shots[]` | 纯 CPU OpenCV，4K 逐帧慢；阈值按素材调，硬切密集的片子会过切 |
| Ultralytics | 不嵌 | 无 | `ultralytics/engine/`、`ultralytics/models/yolo/` | 只能进程外，或整条换掉 | AGPL-3.0，闭源产品里进不了链接侧（第七部分已划红线，换 RT-DETR / YOLOX） |
| ByteTrack | 不嵌 | 无 | `yolox/tracker/byte_tracker.py`、`matching.py` | 进程外 | 2021 年后的跟踪范式没跟进；作为 Kalman + 匈牙利匹配的参考实现仍然最省读 |
| BiRefNet | 不嵌 | 无 | `models/`（双参考分支网络）、推理脚本 | 进程外 | 单帧分割，视频上要自己加时序平滑 |
| Robust Video Matting | 不嵌 | 无 | `model/model.py`、`inference.py` | 进程外 | **协议是 GPL-3.0**，第七部分里按 Apache/MIT 记的那条要改（见第 11 节）；2021 年后停更 |
| Real-ESRGAN | 不嵌 | 无 | `realesrgan/archs/`、`inference_realesrgan.py` | 进程外 | 2022 年后停更；只超分单帧，不吃视频容器与音频 |
| diffusers | 不嵌 | 无 | `src/diffusers/pipelines/`、`schedulers/`、`models/` | 服务化进程外 | 生成式管线吃显存；只适合当外部服务 |
| ComfyUI | 不嵌 | 无 | `comfy/`（`nodes.py`、`samplers.py`）、`custom_nodes/` | 进程外 HTTP | GPL-3.0；节点生态自管版本，升级会炸工作流 |
| InsightFace | 不嵌 | 无 | `python-package/insightface/model_zoo/`（ArcFace、RetinaFace）、`app/face_analysis.py` | 进程外 | 根目录无协议文件可读，权重商用条款要单看；无 release 语义 |

**本轮结论**：这一组定两个，另外记一笔协议修正。

- **llama.cpp b12557**（阶段 4）：VLM 打标走 `tools/mtmd`，端侧就能把「人物 / 场景 / 动作 / 情绪 / 可用性」变成结构化标签，不必等云；阶段 4 的叙事级判断再交强模型读标签化摘要。
- **PySceneDetect v0.7.3**（阶段 3）：镜头切分是 Agent 的最小分析单元，`ContentDetector` 的输出直接变 `shots[]` 带 `source_range`，第七部分定的这条路没有更省事的替代。

协议修正记一笔：**RVM（RobustVideoMatting）是 GPL-3.0**，人像抠像这条只能走 BiRefNet（MIT）或自研色度键，第七部分 2.18 节里「RVM 或 BiRefNet 一类，Apache-2.0/MIT 系」的说法要按 BiRefNet 收口。

---

### 8. 桌面壳与 UI

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| Qt Base | `qt/qtbase` | LGPL-3.0（另有 GPL-3.0 与商业轨） | C++ | 3.1k | v6.11.3 / 2026-10-26 |
| CEF | `chromiumembedded/cef` | BSD-3-Clause | C++ | 4.9k | 无 GitHub release（官方走 Spotify 构建产线，版本号未核实） |
| Qt Advanced Docking System | `githubuser0xFFFF/Qt-Advanced-Docking-System` | LGPL-2.1 | C++ | 2.6k | 5.1.1 / 2026-08-21 |
| Dear ImGui | `ocornut/imgui` | MIT | C++ | 77.2k | v1.93.0 / 2026-10-15 |
| SDL3 | `libsdl-org/SDL` | Zlib | C | 17.0k | 3.4.20 / 2026-11-03 |
| GLFW | `glfw/glfw` | Zlib | C | 15.5k | 3.5.1 / 2026-07-31 |
| webview | `webview/webview` | MIT | C++ | 14.3k | 0.12.0 / 2024-09-11 |
| SQLite | `sqlite/sqlite` | Public Domain（GitHub 未识别，标 `NOASSERTION`） | C | 11.1k | version-3.54.1 / 2026-10-16 |
| Crashpad | `chromium/crashpad` | Apache-2.0 | C++ | 614 | 无 GitHub release（未核实） |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| Qt Base | 能 | Python（PySide6，另有 PyQt） | `src/widgets/`、`src/quick/`、`src/gui/painting/`、`src/opengl/`、`src/plugins/platforms/windows/` | 动态库（LGPL-3.0 纪律：动态链 + 允许替换 Qt 库） | 静态链接要商业授权；Qt Quick 3D、Quick Timeline、HTTP Server、Virtual Keyboard、Graphs 等 14 项是 GPL-only，闭源产品里放不进去（第七部分 2.1 节已列） |
| CEF | 能 | C++ / C API | `include/cef_client.h`、`include/cef_browser.h`、`libcef/browser/`、`wrapper/cef_helpers.h` | 动态库 + 独立子进程 | 分发体积 ~150MB；browser / render / GPU 多进程吃内存；CEF 版本与 Chromium 版本锁死，升级是项目级动作 |
| Qt Advanced Docking System | 能 | 无 | `src/DockManager.cpp`、`src/DockWidget.cpp`、`src/FloatingDockContainer.cpp`、`src/DockAreaWidget.cpp` | 静态库（LGPL-2.1 动态纪律适用于命名的库） | 只管停靠布局与浮动，不做多窗口渲染同步；品牌定制要改源码 |
| Dear ImGui | 能 | 无 | `imgui.cpp`、`imgui_draw.cpp`、`imgui_widgets.cpp`、`backends/imgui_impl_dx11.cpp` | 静态库 | 立即模式，长列表与大表格要自己做虚拟化；中文 IME 要接 `ImmContext` |
| SDL3 | 能 | C API | `src/video/windows/`、`src/audio/wasapi/`、`src/events/` | 动态库 `SDL3.dll` | 只管窗口 / 输入 / 音频，不管控件 |
| GLFW | 能 | C API | `src/win32_window.c`、`src/wgl_context.c`、`src/monitor.c` | 静态库 | 同上；Win32 深接口（DPI、任务栏、JumpList）不在它的范围 |
| webview | 能 | C / C++ | `core/include/webview/webview.h`、`core/src/platform/windows/` | 静态库 + WebView2 | 依赖 WebView2 Runtime（Win10 1803+ 要装）；没有 CDP/DevTools 那种深度；2024 年后节奏放慢 |
| SQLite | 能 | C API | `src/sqlite3.c`（amalgamation）、`src/wal.c`、`src/btree.c` | 单文件编进 `projectd.exe` | 单写者模型，WAL 下并发读可以、并发写要排队；大 blob 进库会让 WAL 暴涨（第七部分已定 sha256 分桶存 blob） |
| Crashpad | 能 | C / C++ | `client/`（`crashpad_client_win.cc`）、`handler/`、`util/`、`minidump/` | 静态库，五个进程各挂一份 handler | 符号服务器要自建；minidump 不含显存与纹理，GPU 侧崩溃复现率有限 |

**本轮结论**：这一组定两个。

- **Qt 6.8 LTS 线**（阶段 1；仓库当前最新是 v6.11.3，产品锁 LTS 轨道）：LGPL-3.0 动态链接，避开 14 项 GPL-only 模块；时间轴要在 60fps 下重绘十万级图元，QWidget 自绘 + QOpenGLWidget 是可控路径，这一条 第七部分已经算过账。
- **Qt Advanced Docking System 5.1.1**（阶段 1）：媒体箱 / 监视器 / 属性 / 音频表的停靠与浮动是纯体力活，LGPL-2.1 能直接链。

CEF 留到阶段 5：插件面板第一版用 WebView2（系统组件，省 150MB），只有当「要跑剪映那种整页 Web 面板」的需求成立时才把 CEF 按独立进程引入。SQLite 与 Crashpad 属宿主基础件，跟着阶段 1 一次性接完。

---

### 9. Agent 与 MCP

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| MCP 规范 | `modelcontextprotocol/modelcontextprotocol` | Apache-2.0（项目从 MIT 迁移中） | 文档 + JSON Schema | 9.7k | 未核实（无常规 release） |
| MCP Servers | `modelcontextprotocol/servers` | Apache-2.0（迁移中） | TypeScript / Python | 92.1k | v2.5.0 / 2026-11-18 |
| MCP Python SDK | `modelcontextprotocol/python-sdk` | MIT | Python | 24.9k | v2.3.0 / 2026-10-02 |
| MCP C# SDK | `modelcontextprotocol/csharp-sdk` | Apache-2.0（迁移中） | C# | 4.6k | 未核实 |
| MCP C++ SDK | `modelcontextprotocol/cpp-sdk` | 未核实 | C++ | 未核实 | 未核实 |
| FastMCP | `jlowin/fastmcp` | Apache-2.0 | Python | 28.7k | v4.2.3 / 2026-11-20 |
| nlohmann/json | `nlohmann/json` | MIT | C++ | 50.9k | 3.12.0 / 2025-04-11 |
| LiteLLM | `BerriAI/litellm` | 未核实（SPDX 未识别，README 标 MIT） | Python | 63.6k | v1.110.2 / 2026-11-20 |
| Ollama | `ollama/ollama` | MIT | Go | 187.7k | v0.40.17 / 2026-11-20 |
| MAGPIE | `yetone/magpie` | MIT | Go | 39.2k | v0.1.4582 / 2026-11-20 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| MCP 规范 | 不嵌 | 无 | `schema/`（tools / resources / prompts / elicitation 的 JSON Schema）、`docs/specification/`（传输、鉴权、progress 语义） | 当规范文本读 | 规范不提供实现；spec 版本与各 SDK 的支持矩阵要自己对 |
| MCP Servers | 不嵌 | 无 | `src/filesystem/`、`src/git/`、`src/fetch/` 的工具定义与入参 schema 写法 | 参考 | 参考实现面向通用场景，工具粒度对我们太粗 |
| MCP Python SDK | 不嵌 | Python | `src/mcp/server/`、`src/mcp/client/`、`src/mcp/shared/session.py`（JSON-RPC 分帧、capability 协商） | 对着抄行为 | Python asyncio 模型；C++ 侧要重写一遍帧解析 |
| MCP C# SDK | 不嵌 | C# | `src/ModelContextProtocol/` | 参考 | .NET 运行时 |
| MCP C++ SDK | 未核实 | 未核实 | 未核实（仓库路径与 API 都返回 404 / 连接中断） | 未定 | 官方 C++ 实现没拿到，工具层按自研走 |
| FastMCP | 不嵌 | Python | `src/fastmcp/server/`、`src/fastmcp/tools/`、`src/fastmcp/client/` | 参考注册表设计 | 装饰器注册是 Python 惯用法，C++ 侧要改成静态注册表 |
| nlohmann/json | 能 | 无 | `single_include/nlohmann/json.hpp`（单头） | 单头编进工程 | 全头文件，编译期膨胀明显；十万行级工程文件要配 SAX 接口解析，`json::parse` 直读会吃内存 |
| LiteLLM | 不嵌 | Python | 多供应商协议翻译表（OpenAI / Anthropic / Gemini 互转）、错误码归一 | 参考 | 它做的是网关，MAGPIE 已经覆盖同一条路，这层只当协议字典 |
| Ollama | 能（HTTP） | C / C++ / Python | `api/`（`/api/chat`、`/api/embed`）、模型管理 | 进程外 HTTP | 自带模型管理与 GPU 调度，做端侧兜底合适，做统一网关不合适 |
| MAGPIE | 不嵌（独立服务） | 无 | `/v1` 路由、路由组（组内供应商顺位切换）、四套协议双向翻译、账号级额度切换 | 进程外，本地 `3425` 端口 | 只做翻译与路由，不管上下文预算与计量（第七部分 2.22 节：我们只加预算器、路由表、计量账本三样） |

**本轮结论**：这一组一条主路 + 一个参考。

- **自研 C++ MCP Server（stdio + Streamable HTTP，spec 2026-07-28）+ nlohmann/json 3.12.0**（阶段 6）：22 个工具要跟命令总线、事务边界、事件账本绑死，套 Python/TS SDK 只是多一层进程与一次序列化；报文层用 `json.hpp` 单头，分帧与 capability 协商照 `python-sdk` 的 `shared/session.py` 行为对齐。
- **MAGPIE**（阶段 3 起，其实写在 第七部分 2.22 节）：模型网关直接用现成的，我们只叠预算器、路由表、计量账本。

这里要改 第七部分一句话：2.23 节写的「官方 Python/TS SDK + 自研工具层」在 C++ 侧没有可用的官方实现（`modelcontextprotocol/cpp-sdk` 这条路本次没拿到），落地形态改为**全自研 + 对齐 spec 与 python-sdk 行为**。

---

### 10. 参考型应用（能抄架构的成品）

| 项目 | 仓库 | 开源协议 | 主语言 | Star | 最新 Release |
| --- | --- | --- | --- | --- | --- |
| OBS Studio | `obsproject/obs-studio` | GPL-2.0 | C++ | 79.8k | 33.0.1 / 2026-10-29 |
| Kdenlive | `KDE/kdenlive` | GPL-3.0 | C++ | 6.1k | v26.11.80 / 2026-11-13 |
| Shotcut | `mltframework/shotcut` | GPL-3.0 | C++ | 15.7k | v26.11.15 / 2026-11-16 |
| Olive | `olive-editor/olive` | GPL-3.0 | C++ | 9.2k | 0.2.0-nightly / 2024-12-05 |
| Natron | `NatronGitHub/Natron` | GPL-2.0 | C++ | 5.7k | 2.5.1 pre2 / 2024-09-13 |
| Blender | `blender/blender` | GPL-2.0-or-later（官方 `COPYING`，部分模块 GPL-3.0） | C++ | 22.2k | v5.3.0 / 2026-11-09 |
| LosslessCut | `mifi/lossless-cut` | GPL-2.0 | JavaScript | 46.2k | 3.70.2 / 2026-10-28 |

| 项目 | 能嵌 C++/Win | 官方绑定 | 可复用模块（目录/文件名） | 集成方式 | 已知硬限制 |
| --- | --- | --- | --- | --- | --- |
| OBS Studio | 做不到（GPL-2.0） | 无 | `libobs/`（`obs-source.c`、`obs-filter.c`、`obs-encoder.c` 的图结构）、`UI/window-basic-main.cpp`、`libobs-d3d11/`（D3D11 纹理共享与 GPU 同步）、`plugins/obs-ffmpeg/` | 只读架构 | GPL-2.0，代码进不了闭源主程序；它的事件驱动模型比我们要松 |
| Kdenlive | 做不到（GPL-3.0） | 无 | `src/timeline2/`（clip/track 模型 + 命令 undo）、`src/project/`（工程 bin、代理）、`src/monitor/` | 只读架构 | 模型建在 MLT 之上，摘模型要连 MLT 一起摘 |
| Shotcut | 做不到（GPL-3.0） | 无 | `src/qml/`（UI 组织）、`src/mltcontroller/`（MLT 封装）、代理与预览降级策略 | 只读架构 | 同 MLT 依赖；QML 主导，与 Widgets 路线不同 |
| Olive | 做不到（GPL-3.0） | 无 | `source/core/`（节点与渲染器）、`source/node/`、`source/render/` | 只读架构 | nightly 停在 2024-12，两年没动，代码当文档读 |
| Natron | 做不到（GPL-2.0） | 无 | `Engine/OfxEffectInstance.cpp`、`Engine/OfxClipInstance.cpp`、`Engine/OfxImageEffectInstance.cpp`（真实 OFX 宿主实现：参数求值、渲染上下文、多线程） | 只读架构 | GPL-2.0；与 Qt + 自有 UI 强耦合 |
| Blender | 做不到（GPL） | Python（`bpy`，是一等公民） | `source/blender/depsgraph/`（依赖图求值）、`source/blender/editors/`（操作栈 undo）、`source/blender/makesrna/`（反射导出） | 只读架构 / 进程外 | GitHub 是镜像，主开发在 `projects.blender.org`；GPL 只能进程外 |
| LosslessCut | 做不到（GPL-2.0） | 无 | 关键帧对齐的切割策略（`src/ffmpeg.ts`）、时间轴缩放与分段导出流程 | 只读交互 | Electron 前端，代码是 JS；价值在「无损切割 + 关键帧吸附」这套交互设计 |

**本轮结论**：这一组读三个，一个都不搬。

- **Natron 的 OFX 宿主实现**（服务阶段 5）：`Engine/OfxEffectInstance.cpp` 把参数求值、渲染上下文、多线程回调全走了一遍，是市面上唯一能逐行读的完整 OFX 宿主；第八部分阶段 5「接 3 个真实 OFX 插件、参数 UI 自动生成且可关键帧」这条验收，读完它少踩两周坑。
- **OBS 的 D3D11 图形层 + Kdenlive 的 timeline2 命令模型**（服务阶段 1-2）：前者给出纹理共享、GPU 同步、D3D11 设备丢失恢复的工程做法；后者给出「clip/track 模型 + 命令 undo」与 AI 改动留痕的接口形状。

Natron 的节点引擎与 UI 强耦合、Blender 的 depsgraph 过重，这两条 第七部分已经判过：摘出来比自己写贵。

---

### 11. 按协议分级的可用性

分四档。第一档是能直接闭源商用链接的；第二档是 LGPL，链接可以但要守纪律；第三档只能进程外隔离；第四档是参考实现，代码一行都不复制。

#### 11.1 可直接闭源商用链接（MIT / Apache-2.0 / BSD-2 / BSD-3 / ISC / Zlib / Public Domain）

| 协议 | 项目 |
| --- | --- |
| MIT | BtbN/FFmpeg-Builds（脚本）、imgui-node-editor、tinyexpr（Zlib）、Dear ImGui、webview、nlohmann/json、libass（ISC）、VST3 SDK（SDK 本体）、oneVPL、RNNoise、libebur128、Demucs、whisper.cpp、openai/whisper、faster-whisper、pyannote.audio、FunASR、sherpa-onnx（Apache-2.0 见下）、ByteTrack、BiRefNet、llama.cpp、DirectML、Ollama、MAGPIE、Qt Advanced Docking System（LGPL 见 11.2）、Piper、pyaaf、Aegisub（BSD-3） |
| Apache-2.0 | OpenTimelineIO、OpenImageIO、OpenVINO、SAM 2、diffusers、ONNX 规范、FastMCP、Crashpad、pyJianYingDraft、MCP 规范 / Servers / C# SDK（迁移中）、aces-dev、sherpa-onnx、DeepFilterNet（双轨） |
| BSD-2-Clause | libavif、OpenH264 |
| BSD-3-Clause | libjxl、libwebp、OpenFX、OpenEXR、Skia、OpenColorIO、colour-science、WhisperX、PySceneDetect、Real-ESRGAN、CEF、Aegisub |
| ISC / Zlib / Public Domain | libass（ISC）、tinyexpr（Zlib）、SDL3（Zlib）、GLFW（Zlib）、miniaudio（Unlicense 或 MIT-0）、SQLite（Public Domain） |

一句话结论：这一档里 FFmpeg 之外的媒体与 AI 地基全是干净的，可以直接生成安装包。

#### 11.2 LGPL 动态链接档（可以链，但要守三条纪律）

| 项目 | 协议 | 纪律 |
| --- | --- | --- |
| FFmpeg | LGPL-2.1-or-later | 动态链 `av*.dll`；编译期不加 `--enable-gpl`；提供协议文本与源码获取方式 |
| Qt Base | LGPL-3.0 | 动态链；不改 Qt 源码；允许用户替换 Qt 库；14 项 GPL-only 模块不碰 |
| libplacebo | LGPL-2.1 | 动态链；版本升级要重测着色器路径 |
| libsndfile | LGPL-2.1 | 动态链 |
| MLT Framework | LGPL-2.1 | 动态链（本文判缓做，只在导入 Shotcut/Kdenlive 工程时接） |
| Qt Advanced Docking System | LGPL-2.1 | 动态链或独立 DLL |

一句话结论：这一档要的是「链接方式」，不是「能否落地」，动态链 + 不改源码 + 提供替换途径三条做到，闭源分发成立。

#### 11.3 只能进程外隔离（GPL-2.0 / GPL-3.0 / AGPL-3.0）

| 项目 | 协议 | 隔离形态 |
| --- | --- | --- |
| Rubber Band | GPL-2.0 | `audiofx.exe`，共享内存传 PCM |
| x264 / x265 系编码器 | GPL-2.0 | 命令行子进程或独立编码进程，不分发其二进制进主安装包的可链接面 |
| OBS Studio | GPL-2.0 | 只读架构，代码不进来 |
| Natron | GPL-2.0 | 只读架构 |
| LosslessCut | GPL-2.0 | 只读交互设计 |
| Kdenlive / Shotcut / Olive | GPL-3.0 | 只读架构 |
| Blender | GPL-2.0-or-later | `blender.exe` 无头渲染子进程 |
| ComfyUI | GPL-3.0 | 外部 HTTP 服务 |
| Robust Video Matting | GPL-3.0 | 进程外；且抠像这条改走 BiRefNet（MIT） |
| Piper（音素化链路） | MIT + espeak-ng（GPL-3.0） | TTS 进程外 |
| Ultralytics | **AGPL-3.0** | 整条不用，换 RT-DETR / YOLOX（第七部分红线） |
| JUCE | **AGPL-3.0 / 商业双轨** | 只在买商业授权后链接；否则整应用开源 |

一句话结论：这一档的每一个都必须跨进程边界，且跨的方式要写进代码评审清单——`audiofx.exe`（Rubber Band）、`blender.exe`（3D 加分项）、外部 HTTP（ComfyUI）。

#### 11.4 参考实现，代码不可复制

| 项目 | 协议状态 | 能拿走的 |
| --- | --- | --- |
| Natron | GPL-2.0 | 宿主设计的读法，不抄代码 |
| OBS Studio | GPL-2.0 | D3D11 图层的工程做法 |
| Kdenlive / Shotcut / Olive | GPL-3.0 | 模型与命令的形状 |
| Blender | GPL-2.0-or-later | depsgraph / 操作栈 / RNA 反射的思路 |
| ComfyUI / Ultralytics / RVM | GPL-3.0 / AGPL-3.0 | 管线与检测头思路，代码不搬 |
| SAM 2 / BiRefNet / Real-ESRGAN / InsightFace | Apache-2.0 / MIT / BSD-3 / 未核实 | 模型与推理脚本可进程外调用；InsightFace 权重商用条款单看 |
| pyJianYingDraft / pyCapCut / pyaaf | Apache-2.0 / 未核实 / MIT | 字段语义与对象模型，代码不搬 |
| Subtitle Edit / Aegisub | MIT / BSD-3-Clause | 算法与格式矩阵（协议上可用，工程形态搬不进 C++） |

一句话结论：这一档的价值是「省掉摸索」，不是「省掉写代码」。

---

### 12. Top 12 必上项目

阶段编号对齐 `G_开发路线图.md` 的七阶段。阶段 6 的工具面与阶段 7 的协作/模板面没有新增外采项目，靠阶段 1-5 的组件自研拼装。

| # | 项目 | 用途（落在哪一层） | 上它的阶段 | 协议 | Star | Release |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FFmpeg | 媒体层解码编码、封装、滤镜（L2 / L6） | 阶段 1 | LGPL-2.1-or-later | 67.7k | n9.1 |
| 2 | Qt Base | 桌面壳、自绘时间轴、主窗（L1 / L5），锁 6.8 LTS 轨 | 阶段 1 | LGPL-3.0 | 3.1k | v6.11.3（仓库最新） |
| 3 | nlohmann/json | AVS 工程读写、命令序列化、MCP 报文 | 阶段 1 | MIT | 50.9k | 3.12.0 |
| 4 | SQLite | 工程库、事件账本、内容寻址索引（L3） | 阶段 1 | Public Domain | 11.1k | 3.54.1 |
| 5 | OpenColorIO | 色彩管线、显示变换、ACES 2.0（L2） | 阶段 2 | BSD-3-Clause | 2.1k | v2.6.0 |
| 6 | OpenTimelineIO | FCPXML / AAF / EDL 交换适配器 | 阶段 2 起，阶段 7 全量 | Apache-2.0 | 2.1k | Beta 18.1 |
| 7 | whisper.cpp | CPU 兜底转写（L9） | 阶段 3 | MIT | 55.3k | v1.9.5 |
| 8 | sherpa-onnx | ASR / VAD / TTS / 说话人嵌入一个 C API（L9） | 阶段 3 | Apache-2.0 | 16.1k | v2.0.2 |
| 9 | PySceneDetect | 镜头切分 → `shots[]`（L9） | 阶段 3 | BSD-3-Clause | 5.6k | v0.7.3 |
| 10 | libass | 字幕渲染（花字、逐字动画）（L8） | 阶段 4 | ISC | 1.2k | 0.17.5 |
| 11 | llama.cpp | 端侧 VLM 打标与检索（L9 / L10） | 阶段 4 | MIT | 135.8k | b12557 |
| 12 | OpenFX | 特效宿主，吃三家插件生态（L8） | 阶段 5 | BSD-3-Clause | 590 | 1.5.1 |

补充两条不占 Top 12 但已判定要上、且属于「零件」的：**miniaudio + VST3 SDK hosting 层**（阶段 5，音频设备与插件托管）、**libplacebo**（阶段 2，HDR 色调映射）。这两个进不进安装包取决于阶段 2 与阶段 5 的实测结果，不进这张表是为了守住「Top 12 = 一定上」的语义。

---

### 13. 未核实字段清单

本次采集拿不到、已经按纪律留白的字段，逐条写清原因，后面补测时照这张表回填。

| 项目 | 未核实的字段 | 拿不到的原因 |
| --- | --- | --- |
| `microsoft/onnxruntime`（ONNX Runtime） | Star、开源协议、主语言、最新 Release | `microsoft/onnxruntime` 与 `onnx/onnxruntime` 两条路径：API 返回 404，页面与 HEAD 请求返回 404 / 连接被中断，三轮回退后放弃 |
| `modelcontextprotocol/cpp-sdk` | Star、开源协议、最新 Release | 仓库页与 API 均返回 404 / 连接中断，官方 C++ SDK 的公开路径没拿到 |
| `chromiumembedded/cef` | 最新 Release 版本号与时间 | CEF 不走 GitHub release，官方发布走 Spotify 的构建产线；页面上无 release 条目，tags 源也没取到 |
| `facebookresearch/sam2` | 最新 Release 版本号与时间 | release 源与 tags 源均为空，仓库只走 commit |
| `chromium/crashpad` | 最新 Release 版本号与时间 | 仓库无 release，只有 commit |
| `ifzhang/ByteTrack` | 最新 Release 版本号与时间 | 仓库无 release |
| `modelcontextprotocol/modelcontextprotocol` | 最新 Release 版本号与时间 | 规范仓库无常规 release，只有 spec 版本标记 |
| `modelcontextprotocol/csharp-sdk` | 最新 Release 版本号与时间 | release 源为空 |
| `deepinsight/insightface` | 开源协议 | 根目录 `LICENSE` / `LICENSE.md` / `COPYING` 一轮全试后没有可读文件；页面 `license` 字段为空 |
| `GuanYixuan/pyCapCut` | 开源协议 | 同上，根目录无可读协议文件，页面 `license` 字段为空 |
| `BerriAI/litellm` | 开源协议（SPDX 未识别） | 页面显示 `NOASSERTION`；按 README 与官方文档口径记 MIT，SPDX 侧待回读根部协议正文 |
| `qt/qtbase` | 开源协议（SPDX 字段空） | 页面 `license` 字段为空；`LICENSE.LGPL3` 未取到。判定依据是 Qt 官方三分发口径（LGPL-3.0 / GPL-3.0 / 商业），标为已判定但 SPDX 侧留白 |
| `blender/blender` | 协议版本细分 | `COPYING` 指向 `doc/license/GPL-license.txt`，未展开；正文口径为 GPL，具体 2.0 还是 3.0 按模块分 |
| `sqlite/sqlite` | 协议 SPDX | 页面显示 `NOASSERTION`；SQLite 官方口径是 Public Domain |
| `AcademySoftwareFoundation/OpenTimelineIO` | 无 | 已核实（Beta 18.1 / 2025-11-09）；列出为的是记一笔「1.0 未发」 |

另有一项判定性修正，不进上表但同样要落进 第七部分：**`PeterL1n/RobustVideoMatting` 的开源协议是 GPL-3.0**（本次核实），第七部分 2.18 节把它与 BiRefNet 一起写成「Apache-2.0/MIT 系」的说法要改成 BiRefNet 单走。

---

## 第五部分　AI Video Studio 总体技术架构

目标：一个以 Agent 为核心的专业视频工作站。人能用可视化时间轴精修，Agent 能自主剪完整条片子，外部 Agent（Codex / Claude / 任何支持 MCP 的客户端）能把它当工具使。

本文件定 12 层、5 个进程、6 类线程、4 条数据通路，以及每条关键接口的签名。落地顺序见 第八部分，选型理由见 第七部分，格式细节见 第六部分。

---

### 1. 五进程模型（先定边界，再谈代码）

单进程做不完这件事。理由不是「微服务流行」，是四条硬约束：

| 约束 | 代价 | 拆分结论 |
| --- | --- | --- |
| 视频解码/编码崩溃会带走 UI | 用户剪到一半全丢 | 媒体进程独立，崩了自动重启、断点续解 |
| GPU 上下文与显存要独占调度 | 预览与导出抢显存会互相卡 | 渲染进程独占 GPU 队列，预览走低优先级队列 |
| Python 侧 AI 栈有 GIL 与依赖地狱 | 模型加载版本互相打架 | AI 进程独立，随能力包升级，不动宿主 |
| GPL 系组件不许静态链进闭源宿主 | 协议污染 | GPL 组件全部放进程外，走 IPC/管道调用 |

```
┌──────────────────────────────────────────────────────────────┐
│ ①  studio.exe（UI 主进程，Qt6 C++，闭源）                      │
│    主窗 / 时间轴控件 / 属性面板 / WebView2 插件面板 / 命令总线   │
│    持有工程模型的内存副本（唯一真相源在 ③）                     │
└───┬───────────────┬──────────────────┬───────────────┬───────┘
    │ gRPC 本地环回 │                    │               │
┌───▼────────────┐ ┌▼─────────────────┐ ┌▼────────────┐ ┌▼──────────────┐
│ ② media.exe    │ │ ③ projectd.exe   │ │ ④ ai.exe    │ │ ⑤ mcp.exe     │
│ 解码/编码/转码  │ │ 工程库与事务      │ │ 模型推理     │ │ MCP Server    │
│ FFmpeg 直连    │ │ SQLite + 内容寻址 │ │ ORT/llama.cpp│ │ stdio + HTTP  │
│ 代理生成       │ │ 撤销/事件溯源     │ │ Py 侧脚本    │ │ 外部 Agent 入口│
└───┬────────────┘ └──────────────────┘ └─────────────┘ └───────────────┘
    │ DMA-BUF / 共享内存帧
┌───▼──────────────────────────────────────────────────────────┐
│ ⑥ render.exe（可多开，一个 worker 一份）                        │
│    合成图求值 → GPU 上屏/落盘 → 编码输出；无头模式服务端导出      │
└──────────────────────────────────────────────────────────────┘
```

进程间只走两条路：**控制走 gRPC over 命名管道（Windows）/ Unix domain socket**，**像素走共享内存环形缓冲（零拷贝，带 fence 同步）**。帧不入 JSON、不入日志、不入数据库。

为什么不用 Electron 做壳：时间轴要 60fps 重绘、要接 GPU 纹理、要做亚像素级交互，Chromium 的合成层再多一层就是浪费。剪映自己都用 Qt6 + CEF 混合，达芬奇纯 Qt5，这条行业共识不用赌。

---

### 2. 线程模型（6 类，每类的规则写死）

| 线程类 | 数量 | 干什么 | 硬规则 |
| --- | --- | --- | --- |
| UI 主线程 | 1 | Qt 事件循环、时间轴重绘、命令总线派发 | 禁阻塞调用；任何 >8ms 的活丢给后台 |
| 模型线程 | 1 | 工程模型读写、命令应用、撤销栈 | 与 UI 双向队列，模型改动只在事务提交后推给 UI |
| FrameServer 池 | CPU 核数 / 2 | 逐帧合成求值调度、缓存命中判断 | 无共享可变状态，靠显式缓存句柄 |
| 解码与解码后处理 | 每源 1-2 条 | FFmpeg 解包解码、色彩转换、缩放到预览尺寸 | 每源独立 AVCodecContext，禁跨线程共享 |
| 音频实时线程 | 1 | 混音、限幅、输出（PortAudio 回调） | 绝对无锁、无分配、无 IO；只碰预分配缓冲 |
| AI 任务池 | 可配 4-16 | 转写、跟踪、抠像、向量化 | 长任务分片 + 断点续跑 + 进度上报 |

**音频主时钟**：播放时钟由音频输出驱动，视频按音频时钟追帧（丢帧或补帧）。这是预览不飘的唯一做法，达芬奇、剪映都是这个套路。

---

### 3. 12 层架构与每层接口卡

#### L1 桌面壳与 UI

```
职责   主窗、时间轴控件、属性面板、媒体箱、WebView 插件面板
技术   Qt 6.8（Widgets 主窗 + Quick 面板混编）；WebView2 走 QtWebEngine 或原生 WebView2 控件
接口   IMainWindow / ITimelineView / IPropertyPanel / IPluginHost
关键点 时间轴控件用 QWidget + QOpenGLWidget 自绘，不用 QML 列表（QML 在十万级 item 场景会掉帧）
```

#### L2 媒体抽象

```
职责   解码器注册、时间基换算、色彩管线、代理生成、帧缓存
技术   FFmpeg 8.x/9.x libav* 直连（不走命令行）
接口   IMediaSource::open(path) / IMediaDecoder::decode(frameIdx) / IColorPipeline::convert(src,dst)
       IProxyManager::ensure(mediaId, quality) / IFrameCache::get(key) / IFrameCache::put(key, frame)
硬指标 4K H.265 单路解码 > 100fps（多核 + 硬解）；seek 到任意帧 < 30ms（预解关键帧 + 双向解码）
```

#### L3 工程存储

```
职责   工程库、内容寻址 blob、版本快照、事件日志
技术   SQLite（WAL 模式）+ 文件系统分桶存 blob（sha256 命名）
接口   IProjectStore::open / beginTx / commitTx / rollback
       IBlobStore::put(bytes) -> sha256 / get(sha) / gc()
       ISnapshot::create(projectId, label) / list() / restore(snapshotId)
       IEventLog::append(event) / replay(fromSeq)
```

SQLite 表骨架（30 张表里的核心 12 张）：

| 表 | 关键列 | 用途 |
| --- | --- | --- |
| `project` | id, name, created, updated, schema_version, settings_json | 工程头 |
| `sequence` | id, project_id, name, fps_num, fps_den, width, height, sample_rate, color_space | 序列（= AE 的 comp） |
| `track` | id, sequence_id, kind(main/multi), role(video/audio/text/sticker/effect/mixed), index, locked, muted | 轨道 |
| `clip` | id, track_id, seq_start_us, seq_dur_us, src_in_us, src_dur_us, speed, nested_sequence_id | 片段 |
| `clip_effect` | id, clip_id, order, kind, params_json, preset_id | 片段级效果链 |
| `keyframe` | id, owner_kind, owner_id, prop, time_us, value_json, interp, ease_in_json, ease_out_json | 关键帧（统一表，多态） |
| `transition` | id, track_id, at_clip_id, from_clip_id, to_clip_id, kind, dur_us, params_json | 转场 |
| `media` | id, path, sha256, kind, w, h, fps_num, fps_den, dur_us, channels, sample_rate, probe_json | 素材 |
| `media_derived` | id, media_id, kind(proxy/thumb/waveform/transcript/embedding), path, params_json | 派生件 |
| `ai_decision` | id, run_id, agent, action, target_ref, rationale, before_json, after_json, accepted | **AI 决策留痕**（审片与追责的底座） |
| `event_log` | seq, ts, actor(user/agent/system), command, payload_json, tx_id | 事件溯源 |
| `snapshot` | id, project_id, label, seq_high_water, blob_sha, created | 版本快照 |

`ai_decision` 与 `event_log` 是这套设计的核心差异：**每一步 AI 改动都能回答「谁、基于什么证据、改了什么、用户接没接受」**。剪映的 `draft_patch` 只留 runId，达芬奇脚本层根本不记录，这是我们可以直接超过它们的地方。

#### L4 时间轴数据模型（自研核心）

```
职责   工程模型的内存表示、命令应用、撤销重做、依赖联动
技术   纯 C++20，无第三方依赖，可独立单测
接口   IProject / ISequence / ITrack / IClip / IEffect / IKeyframe（只读视图）
       ICommandBus::execute(cmd) -> Result<TxId> / undo(txId) / redo(txId)
       ICommand::validate(model) / apply(model) / invert() / describe()
```

命令总线规则（直接照剪映的教训）：

1. 所有改动都是 `ICommand`，没有「直接改字段」这条路。UI 拖一次片段 = 一条 `MoveClip` 命令。
2. 一批改动用 `BeginTx/EndTx` 包起来，**一个 Tx = 一个 undo 步 = 一个 event_log 事务**。
3. 每条命令自带 `validate`，非法状态在应用前被拦（主轨空洞、片段越界、时间重叠）。
4. 命令可 `invert`，撤销栈就是命令栈，不做整模型快照。
5. 命令分两级权限：`user` 与 `agent`。`agent` 级命令走白名单（对应剪映的 26 条安全子集），且强制带 `rationale`。

#### L5 预览与播放

```
职责   FrameServer、预览缓存、音频时钟、播放控制
技术   自研 FrameServer + GPU 纹理池 + LRU 帧缓存
接口   IFrameServer::request(seqId, frameIdx, quality, priority) -> GpuFrame
       IPlaybackClock（音频驱动）/ IPreviewCache::prefetch(range)
硬指标 1080p 代理 60fps 不掉帧；4K 原始素材 30fps；seek 后首帧 < 60ms
```

#### L6 渲染与导出

```
职责   合成图求值、分段并行编码、硬件编码、封装、多机分片
技术   FFmpeg libavfilter 自建图 + 自研 GPU 合成 + NVENC/QSV/AMF
接口   IRenderJob::submit(spec) -> jobId / status(jobId) / cancel(jobId)
       IEncoderFactory（按 codec + 硬件能力选实现）
规则   分段并行：按 GOP 边界切片，多 worker 各渲一段，最后 `-c copy` 拼接
       导出与预览共用同一套合成图求值代码（唯一差别是质量档与是否回读）
```

分段并行是这套架构的性能命门：**导出 4K 长片的时间 ≈ 单片时长 / worker 数**，前提是切点落在关键帧且音频单独成轨拼接（见 第八部分阶段 2 验收标准）。

#### L7 音频引擎

```
职责   多轨混音、增益/包络、降噪、变速、人声分离、响度归一
技术   JUCE 做宿主与 VST3 加载（进程外托管）；Rubber Band 做变速；DeepFilterNet/RNNoise 降噪；Demucs 分离
接口   IAudioGraph::build(seqId) -> IAudioNode 树 / IAudioGraph::render(range) -> AudioBuffer
       IVstHost::scan() / load(pluginPath) / setParam(id, value)
硬规则 实时线程零分配；所有模型推理在 AI 进程侧链完成，结果以 PCM 或参数回传
```

#### L8 特效与节点系统

```
职责   节点图、效果求值、OpenFX 插件宿主、表达式 DSL
技术   自研轻节点图（DAG，非 Fusion 那种全功能）+ OpenFX 1.4/1.5 宿主 + WGSL 计算着色器
接口   INodeGraph::addNode(type) / connect(a,b,slot) / evaluate(node, frameCtx) -> GpuFrame
       IOfxHost::scan(pluginDir) / instantiate(pluginId) / render(instance, ctx)
       IExpr::compile(expr) -> Program（白名单函数，无 IO，无网络）
节点类型  source / transform / color / blur / keyer / merge / text / time / output（8 类起步）
边界   第一年只做 8 类 40 个节点；OpenFX 插件直接白拿几百个现成效果
```

#### L9 视频理解

```
职责   转写、说话人、镜头切分、画面事实、语义检索、向量索引
技术   方案见 第七部分：ASR 用 faster-whisper/WhisperX；说话人 pyannote；镜头切分 PySceneDetect；
       分割 SAM2；检测/跟踪 YOLO(注意协议)或 RT-DETR + ByteTrack；VLM 走 MAGPIE 远端
接口   IAnalyzer::run(mediaId, tasks[]) -> AnalysisResult
       AnalysisResult{ transcript[], speakers[], shots[], frames[], embeddings[], objects[] }
       ISearch::index(projectId) / query(projectId, text|vector, k)
存储   结果写 media_derived + 向量表（sqlite-vec 或独立 FAISS 索引文件）
```

#### L10 内部 Agent

```
职责   规划、工具调用、工程上下文、审片、失败恢复、用户反馈学习
技术   Director / Editor / Critic 三角色，共享一个 RunContext
接口   IRun::start(goal, refs) -> runId / step(runId) / cancel(runId)
       IToolRegistry::list(scope) / call(toolId, args)（scope=agent|user|external）
```

三个角色的分工（这是从剪映的 Director → editing_agent → editing-review 链路学来的，但补了它缺的一环）：

| 角色 | 输入 | 输出 | 权限 |
| --- | --- | --- | --- |
| Director | 用户话 + 素材事实 | 任务契约（目标、范围、约束、验收口径） | 只读 |
| Editor | 任务契约 + 工程 XML 视图 | 命令批次（走 agent 白名单） | 写（受限） |
| Critic | 成片证据 + 草稿结构 + 脚本意图 | 结论 + 证据 + 最小返修范围 | 只读 |

Critic 必须区分四级证据（照抄剪映 `editing-review` 的规则，这条比它的实现更值钱）：**素材分析只证明素材内容，脚本说明意图，草稿结构只证明编排事实，只有渲染成片的音画证据才支持「实际呈现」的结论**。

#### L11 模型网关

```
职责   多供应商接入、协议互转、路由、额度计量、故障切换、上下文预算
载体   MAGPIE（公开项目：MIT，Go + Wails，本地监听 3425 端口，/v1 前缀）
接口   对上是 OpenAI 兼容的 /v1/chat/completions、/v1/responses、/v1/messages(Anthropic)、Gemini
       对下按供应商翻译四种协议，流式与工具调用一起翻
我们加的东西
       ① 上下文预算器：长视频理解按「镜头 → 摘要 → 对话」三级压缩，喂给模型的永远是带引用的摘要
       ② 任务路由表：转写/切分/抠像走端侧；脚本生成/审美判断走强模型；字幕润色走便宜模型
       ③ 计量账本：按 runId 记 token 与耗时，写进 event_log，能算每条成片花了多少钱
```

#### L12 MCP 接口层

```
职责   把整个工作站暴露成工具，给外部 Agent 用
技术   MCP spec 2026-07-28；stdio（本地 Codex）+ Streamable HTTP（远程/多客户端）
工具面 22 个（见下）；长任务用 progress notification；交互用 elicitation
```

工具清单（对齐用户需求的 17 条能力，收敛成 22 个工具）：

| 组 | 工具 | 说明 |
| --- | --- | --- |
| 工程 | `project.create` `project.open` `project.list` `project.snapshot` `project.restore` | 建/开/列/快照/回滚 |
| 素材 | `media.import` `media.probe` `media.proxy` `media.thumbnail` | 导入、探测、代理、缩略图 |
| 分析 | `analyze.transcribe` `analyze.shots` `analyze.speakers` `analyze.frames` `analyze.search` | 转写、切分、说话人、抽帧事实、语义检索 |
| 脚本 | `script.generate` `script.get` `script.update` | 分镜脚本（cuts 的中间表示） |
| 剪辑 | `timeline.apply` `timeline.query` `timeline.diff` | 应用 XML 改动、读结构、比对差异 |
| 包装 | `overlay.subtitle` `overlay.text` `overlay.effect` `audio.mix` | 字幕、花字、特效、音频处理 |
| 预览导出 | `preview.frame` `preview.play_range` `render.submit` `render.status` | 单帧/区间预览、提交渲染、查状态 |

`timeline.apply` 的入参就是 第六部分定义的 XML 改动程序（受控 DSL），**不是自由 JSON patch**。理由：模型写错 XML 结构会被 schema 拦住，写错自由 path 会静默改坏工程。

长任务契约（MCP 规范要求 progress 单调递增，`total` 可为浮点）：

```jsonc
// 请求
{"name":"analyze.transcribe","arguments":{"mediaId":"m_01","language":"zh","diarize":true},
 "_meta":{"progressToken":"tk_9f3"}}
// 通知
{"method":"notifications/progress",
 "params":{"progressToken":"tk_9f3","progress":0.42,"total":1.0,"message":"转写到 12:37"}}
// 完成
{"content":[{"type":"text","text":"{\"transcriptRef\":\"blob:sha256…\",\"segments\":842}"}],
 "isError":false}
```

---

### 4. 四条数据通路

```
① 播放通路
   ProjectModel(frame n) → 合成图求值 → FrameServer 线程池 → GpuFrame(纹理)
     → 预览缓存(LRU) → QOpenGLWidget 上屏；音频时钟驱动 seek/重复帧

② 导出通路
   RenderJob(spec) → 按 GOP 切片 → N 个 render worker → 各自编码 → 分段文件
     → `-c copy` 拼接 → 封装 → 校验(MD5/时长/帧数) → 交回主进程

③ Agent 通路
   用户话 → Director 出任务契约 → Editor 读 XML 视图 → 生成 <changes> 程序
     → validate(不落地) → preview(候选回显) → apply(Tx) → 回读校验 → Critic 审片

④ 外部 Agent 通路
   Codex/Claude → MCP Client → mcp.exe(stdio/HTTP) → 工具调用 → CommandBus
     → 同一套命令与事务（外部 Agent 与内部 Agent 走完全相同的权限与留痕）
```

关键点：**内部 Agent 与外部 Agent 走同一条命令总线、同一套事务、同一份留痕**。区别只在权限集：外部 Agent 默认拿到的是只读 + 剪辑白名单，写操作要显式开启。

---

### 5. 工程上下文管理（Agent 的内存怎么建）

长视频理解的关键不是把整片塞进上下文，是建一份可查询的工程事实表：

```
Level 0  素材事实    时长/分辨率/帧率/编码/色彩 + 转写全文 + 镜头表 + 人物表   （结构化，永不裁）
Level 1  镜头摘要    每镜 20-60 字，带 source_range                          （模型可读，按需取）
Level 2  段落摘要    每 3-8 镜一段，带情绪与叙事角色                         （粗剪决策的输入）
Level 3  全局大纲    起因/发展/高潮/收束 + 必留/必删清单                     （一次规划用）
Level 4  对话历史    最近 N 轮 + 关键决策点（带引用回 Level 1-3）            （会话状态）
```

规则：**模型永远拿到「摘要 + 引用」，要看原文按引用回取**。这样 3 小时素材的规划与 3 分钟素材的规划，上下文成本同阶。

---

### 6. 可观测性与失败恢复

| 项 | 做法 |
| --- | --- |
| 崩溃隔离 | 五个进程各自看门狗；media/render 挂了自动重启并从当前帧续解/续渲 |
| 断点续跑 | 每个 AI 任务有步骤账本（step 表 + 输入哈希 + 输出 blob），重跑只补缺失步骤 |
| 长任务可续 | MCP 侧 `progressToken` 全生命周期有效；客户端断了用 `tools/get` 查状态 |
| 审计 | 每条命令写 event_log；每条 AI 改动写 ai_decision；两者用 `tx_id` 关联 |
| 性能埋点 | 帧耗时、缓存命中率、解码等待、GPU 占用、模型延迟，按 runId 聚合 |

---

### 7. 性能预算（第一年必须打到的数）

| 场景 | 目标 | 判定方式 |
| --- | --- | --- |
| 1080p 30fps 代理 + 3 轨叠加 + 字幕 | 60fps 预览不掉帧 | 播放 60 秒无 dropped frame 计数增长 |
| 4K 原始素材单轨 | 30fps 预览 | 同上 |
| seek 任意位置 | 首帧 < 60ms | 100 次随机 seek 的 P95 |
| 导出 4K 60s / H.265 硬编 | < 90 秒（8 worker） | 实际跑 3 次取均值 |
| 3 小时素材全量转写 | < 12 分钟（GPU） | faster-whisper large-v3 + batching |
| 长视频规划（200 镜） | 单次 Agent 调用 < 40 秒 | 端到端计时 |

---

### 8. 这张架构图跟三家的对应关系

| 我们的层 | 对标剪映 | 对标达芬奇 | 对标 AE |
| --- | --- | --- | --- |
| L1 UI | Qt6 Quick + CEF 混合 | Qt5 Widgets | 自绘 |
| L3 存储 | content/meta 分离 | SQLite + ZIP(XML) 打包 | RIFX 单文件 |
| L4 时间轴 | 命令表 + 批事务 | 片段层 API | 合成/图层树 |
| L6 渲染 | VECreator 家族 | 单进程 GPU 调度 | MFR |
| L8 特效 | OFX bundle + 模板 | Fuse/DCTL/OFX | PF_Effect/AEGP |
| L10 Agent | Director/Editing/Review | 无（只给脚本） | 无 |
| L12 接口 | 内部 CLI + Lyra | 脚本 API + 端口 1144 | JSX + aerender |

差异点只有一个但是决定性的：**三家都把「AI 改工程」当成附加能力，我们把它当成一等公民，从数据模型、命令权限、事务、留痕、审片全部围绕它设计。**

---

## 第六部分　统一工程文件格式 AVS 1.0

版本：AVS 1.0（本文件定的第一版）
配套：`E_avs_project.schema.json`（JSON Schema 2020-12，可直接喂 `ajv` / `python-jsonschema` 校验）

---

### 1. 七条设计原则（每条都对应三家里的一个坑）

| # | 原则 | 抄谁的教训 |
| --- | --- | --- |
| 1 | **明文、规范化、可 diff**。同一份工程反复保存，字节不变 | 剪映 6.0 起上锁，文件不可审；达芬奇 `FieldsBlob` 不可读；AE RIFX 不可 diff |
| 2 | **时间一律 int64 微秒 + 有理数帧率**。不用 uint16，不用浮点秒 | AE 的 `uint16 × time_scale` 是 16 位时代遗产，长片会溢出 |
| 3 | **引用一律 UUID，不用数组下标** | 达芬奇全程 `DbId`，这是它能合并/套模板的底子 |
| 4 | **内容与索引分离** | 剪映 `draft_content` / `draft_meta_info` 两文件，列表页不加载正文 |
| 5 | **结构明文 + 大块内容内容寻址**。波形、缩略图、转写、向量不进工程文件 | 达芬奇把合成打包进 `CompositionBA`，结果整份不可审；我们把大块数据挪到 blob |
| 6 | **AI 决策与命令历史是工程的一部分**，不是日志 | 剪映只留 `runId`，达芬奇脚本层不留；我们要能回答「谁改的、凭什么」 |
| 7 | **一份格式，两种视图**。JSON 是唯一真相，XML 是给模型与外部工具的受限视图 | 剪映 `draft_content.json` ↔ Lyra XMLDraft 双层；我们照做但把编译器做成开源可测 |

---

### 2. 三层落地形态

```
① .avsproj（单文件包，ZIP 容器，= 可分享/可归档形态）
   manifest.json          格式版本、创建工具、校验和清单
   project.json           ★ 唯一真相（AVS 文档本体）
   media/links.json       素材引用表（绝对路径 + sha256 + 相对回退路径）
   blobs/<sha256>         内容寻址大块（波形/缩略图/转写/向量/代理索引）
   history/events.jsonl   事件日志（可裁剪）
   ai/decisions.jsonl     AI 决策记录（可裁剪）

② project.db（SQLite，= 运行时形态）
   由 project.json 导入，WAL 模式，撤销栈与帧缓存不落这里
   导出时反向生成 project.json，保证「导入-导出-导入」字节稳定

③ 内存 XML 视图（= 给 Agent 与外部工具的形态）
   由 project.json 编译，见第 8 节；改完编译回 JSON
```

三种形态的转换是**双向且可测**的：`json → xml → json` 必须字节相等（规范化后），这条写成单元测试的硬门槛。

---

### 3. 全局规则

| 规则 | 定义 |
| --- | --- |
| 时间单位 | 所有以 `_us` 结尾的字段为 int64 微秒；`_frames` 结尾为 int64 帧号 |
| 帧率 | 有理数 `{num, den, drop_frame}`，例 `{30000, 1001, false}`。禁写 `29.97` 这种浮点 |
| 时长 | `dur_us = 0` 表示零长（用于标记、锚点），负值非法 |
| ID | UUIDv7（时间有序），字符串形态带前缀：`sq_` 序列 / `tr_` 轨道 / `cl_` 片段 / `fx_` 效果 / `kf_` 关键帧 / `md_` 素材 / `tk_` 转场 / `tx_` 文本 |
| 版本 | `schema_version: "1.0.0"` 语义化；`min_reader: "1.0.0"` 表示最低可读版本 |
| 排序 | 所有数组按 `id` 字典序规范化（唯一例外：`clips` 按 `seq_start_us` 升序，因为顺序有语义）；`effects` 按 `order` |
| 空值 | 缺失字段 = 默认值；显式 `null` 只用于「覆盖继承」语义（见 5.7） |
| 数值精度 | 变换类用 float64，禁止写科学计数法；归一化坐标范围见 5.5 |
| 未知字段 | 读入时保留到 `_ext`（扩展区），写回时原样带回，前向兼容靠这条 |

---

### 4. 顶层结构

```jsonc
{
  "schema_version": "1.0.0",
  "min_reader": "1.0.0",
  "id": "prj_01HZX…",
  "name": "宠物博主 30 秒口播",
  "created_us": 1795000000000000,
  "updated_us": 1795000123456789,
  "generator": {"app": "AI Video Studio", "version": "0.1.0", "model_runs": 3},
  "settings": { … },            // 4.1
  "media": [ … ],               // 4.2
  "sequences": [ … ],           // 4.3（含主序列与所有嵌套序列）
  "effects_lib": [ … ],         // 4.4 效果定义（自定义节点/参数 schema）
  "ai": { "runs": [ … ] },      // 4.5
  "history": { "cursor": 812, "events": [ … ] },  // 4.6
  "_ext": {}                    // 未知字段保真区
}
```

#### 4.1 settings

```jsonc
"settings": {
  "default_sequence_id": "sq_main",
  "ui": {"theme": "dark", "timeline_zoom_px_per_sec": 80},
  "ai": {
    "model_route": "default",
    "auto_apply_threshold": 0.7,        // 采纳阈值（缺省 0.7）
    "max_batch_clips": 3                // >3 个片段拆两批（抄剪映的调用策略）
  },
  "render": {"default_preset_id": "preset_h265_4k"},
  "paths": {"proxy_dir": "./.cache/proxy", "waveform_dir": "./.cache/wave"}
}
```

#### 4.2 media

```jsonc
{
  "id": "md_01HZX…",
  "kind": "video",                  // video | audio | image | sequence | generator
  "uri": "file:///D:/素材/口播.mp4",  // 绝对路径；跨机用 rel_uri 兜底
  "rel_uri": "../素材/口播.mp4",
  "sha256": "…",                    // 内容指纹，用于找回过期资源
  "probe": {
    "width": 1920, "height": 1080,
    "fps": {"num": 30000, "den": 1001, "drop_frame": false},
    "dur_us": 1911240000,
    "video_codec": "hevc", "pix_fmt": "yuv420p10le",
    "color": {"primaries": "bt709", "transfer": "bt709", "matrix": "bt709", "range": "tv"},
    "audio": [{"codec": "aac", "channels": 2, "sample_rate": 48000}]
  },
  "proxy": {"path": "blobs/…", "scale": 0.5, "codec": "prores_proxy"},
  "derived": [
    {"kind": "waveform", "blob": "blob:sha256-…"},
    {"kind": "thumbnail", "blob": "blob:sha256-…", "at_us": 0},
    {"kind": "transcript", "blob": "blob:sha256-…", "lang": "zh", "diarized": true},
    {"kind": "embedding", "blob": "blob:sha256-…", "model": "clip-vit-b32"}
  ]
}
```

#### 4.3 sequence（序列 = AE 的 comp = 剪映的复合片段）

```jsonc
{
  "id": "sq_main",
  "name": "主序列",
  "canvas": {"width": 1920, "height": 1080, "ratio": "16:9", "background": [0,0,0,1]},
  "fps": {"num": 30, "den": 1, "drop_frame": false},
  "sample_rate": 48000,
  "channels": 2,
  "color": {"working": "ACEScg", "display": "sRGB", "view": "ACES 1.0 SDR-video", "ocio_config": "aces_2.0"},
  "audio": {"loudness_target_lufs": -14.0, "true_peak_db": -1.0, "normalize": true},
  "dur_us": 31000000,               // 派生值，写出来只为校验
  "tracks": [ … ],                  // 4.3.1
  "markers": [{"id":"mk_…","at_us":1230000,"name":"钩子","color":"red"}],
  "nested_in": "cl_01HZX…"          // 若本序列是被嵌套的子序列，指向那个片段
}
```

##### 4.3.1 track

```jsonc
{
  "id": "tr_v2",
  "kind": "video",                  // video | audio | text | sticker | effect | mixed
  "role": "multi",                  // main（唯一主轨） | multi
  "index": 1,                       // 同 kind 内的层序，从 0 开始；渲染顺序 = index 升序
  "name": "画中画",
  "locked": false, "muted": false, "hidden": false,
  "blend_default": "normal",
  "clips": [ … ]                    // 4.3.2
}
```

主轨约束（抄剪映的规则）：`role:"main"` 的轨道**全工程只能有一条**，且它的 `clips` 必须**首尾相接无空洞**。这条约束把「主轨黑洞」这类非法状态在 schema 层就掐死。

##### 4.3.2 clip

```jsonc
{
  "id": "cl_01HZX…",
  "media_id": "md_01HZX…",          // kind=sequence 时指向嵌套序列
  "seq_start_us": 0,                // 时间线起点（主轨片段由前序片段推导，写入仅为可读）
  "seq_dur_us": 6150000,            // 时间线占用时长，变速后不再乘除
  "src_in_us": 1565260000,          // 素材入点
  "src_dur_us": 6150000,            // 素材消耗量 = seq_dur_us × speed（匀速时）
  "speed": 1.0,
  "speed_curve": null,              // 见 5.4
  "enabled": true, "locked": false,
  "transform": { … },               // 5.5
  "crop": { … },                    // 5.6
  "audio": { … },                   // 5.7
  "effects": [ … ],                 // 4.4 效果引用
  "keyframes": [ … ],               // 5.3
  "transition_in":  { … },          // 5.8
  "transition_out": { … },
  "text": null,                     // text/sticker 片段专用，见 5.9
  "ai": {"run_id": "run_…", "decision_id": "dec_…"}   // 这个片段是谁加的
}
```

#### 4.4 effects_lib（效果定义）与 clip.effects（实例）

```jsonc
// 定义：一份效果 = 参数 schema + 求值目标
"effects_lib": [
  {
    "type": "blur.gaussian",
    "impl": {"kind": "node", "node": "blur.gaussian", "gpu": "wgsl"},
    "params_schema": {
      "radius": {"type": "float", "min": 0, "max": 200, "default": 8, "ui": "slider", "unit": "px"},
      "quality": {"type": "enum", "values": ["draft","normal","high"], "default": "normal"}
    },
    "channels": ["video"]
  },
  {
    "type": "ofx.com.fxhome.denoise",
    "impl": {"kind": "ofx", "bundle": "…/Denoise.ofx.bundle", "plugin_id": "com.fxhome.denoise"},
    "params_schema": {"amount": {"type": "float", "min":0, "max":1, "default":0.5}}
  }
]

// 实例：挂在片段上
"effects": [
  {"id": "fx_01", "type": "blur.gaussian", "order": 0, "enabled": true,
   "params": {"radius": 12, "quality": "high"},
   "keyframes": [{"prop": "params.radius", "t_us": 0, "v": 0, "interp": "bezier"}]}
]
```

`impl.kind` 四种：`node`（自研节点）、`ofx`（OpenFX 插件）、`dctl`（像素着色器脚本）、`template`（参数化模板包，对齐剪映的 `MixMode` 四元组）。

#### 4.5 ai.runs（AI 一次运行）

```jsonc
"ai": {"runs": [
  {
    "id": "run_01HZX…",
    "agent": "director",              // director | editor | critic | external
    "model": {"route": "gpt-x", "provider": "magpie", "tokens_in": 18420, "tokens_out": 2210},
    "goal": "把 26 分钟口播剪成 30 秒竖版，去掉水词",
    "contract": {"target_dur_us": 30000000, "aspect": "9:16", "keep": ["开场三句"], "drop": ["水词","长停顿"]},
    "steps": [
      {"seq": 1, "tool": "analyze.transcribe", "input_ref": "md_…", "output_ref": "blob:…", "ms": 41200},
      {"seq": 2, "tool": "script.generate", "output_ref": "blob:…", "ms": 8800}
    ],
    "decisions": [
      {
        "id": "dec_01",
        "action": "cut",
        "target_ref": "cl_01HZX…",
        "rationale": "第 3 句起重复了同一句话，删 1.8 秒",
        "evidence": [{"kind": "transcript", "ref": "blob:…", "range_us": [1200000, 1380000]}],
        "before_ref": "cl_…", "after_ref": "cl_…",
        "accepted": true,             // 用户采纳了没（对应剪映的 adoption ledger）
        "applied_tx": "tx_812"
      }
    ],
    "status": "applied"               // planned | previewed | applied | rejected | failed
  }
]}
```

#### 4.6 history（事件溯源）

```jsonc
"history": {
  "cursor": 812,
  "events": [
    {"seq": 811, "ts_us": 1795000111000000, "actor": "user", "cmd": "clip.move",
     "target": "cl_01", "args": {"seq_start_us": 0}, "tx": "tx_811"},
    {"seq": 812, "ts_us": 1795000123456789, "actor": "agent", "cmd": "clip.split",
     "target": "cl_03", "args": {"at_us": 4200000}, "tx": "tx_812", "run": "run_…"}
  ]
}
```

事件日志可裁剪（保留最近 N 条 + 每次快照的边界事件），裁剪后仍能重建工程状态：这是「快照 + 增量」的标准做法。

---

### 5. 关键机制

#### 5.1 时间模型

```
时间线坐标 = int64 微秒，从序列起点 0 开始
帧号换算 = floor(us × fps.num / (fps.den × 1_000_000))，只在需要帧精度时算
drop-frame：只在 fps.den 为 1001 时有效，时间码显示层处理，工程内存储始终是无损微秒
```

为什么不用帧号做主键：变速、音频、字幕都需要亚帧精度；帧号会让 23.976 与 24fps 混剪的舍入误差越滚越大。微秒 + 有理数帧率的组合能无损表示所有常见帧率。

#### 5.2 主轨连续与副轨自由

- 主轨：`role:"main"`，片段首尾相接，`seq_start_us` 由前序推导，schema 校验时校验「无空洞、无重叠、首段从 0 开始」。
- 副轨：任意位置、任意时长，允许重叠（同轨道内重叠由渲染层按 `index` 处理，或在同轨道内禁止——第一版选**禁止同轨重叠**，需要叠加就分轨，跟剪映一致）。
- 相对对齐：副轨片段可声明相对锚点，编译时展开成绝对时间：

```jsonc
"anchor": {"start_to": "cl_v1.right", "offset_us": -200000}
// 或 "start_to": "main.left" / "main.right"
```

`anchor` 与 `seq_start_us` 互斥。这样「音乐卡点」「字幕跟人声」不用算绝对时间，主轨一改自动跟随。

#### 5.3 关键帧

```jsonc
{
  "id": "kf_01",
  "prop": "transform.scale",       // 点分路径，指向 clip 或 effect 的参数
  "t_us": 0,                       // 相对片段头部（不是序列绝对时间）
  "v": [1.0, 1.0],
  "interp": "bezier",              // linear | hold | bezier | ease_in | ease_out
  "ease": {"in": [0.33, 0.0], "out": [0.67, 1.0]}   // 归一化贝塞尔控制点
}
```

规则：
- `t_us` 相对片段头部，片段移动时关键帧跟着走（不用批量改数）。
- 同一 `prop` 的关键帧按 `t_us` 升序，**首帧隐式生效到片段结束**（不需要尾帧）。
- `hold` 表示阶跃，不插值。
- 属性值维度由 `prop` 决定，schema 里按 `prop` 枚举限定（避免 `scale` 写 3 个分量这种脏数据）。

#### 5.4 变速

```jsonc
"speed": 1.0,
"speed_curve": {
  "points": [{"t_us": 0, "speed": 1.0}, {"t_us": 2000000, "speed": 2.0}, {"t_us": 6150000, "speed": 0.5}],
  "interp": "linear"
}
```

`seq_dur_us` 与 `src_dur_us` 的关系：匀速时 `src_dur_us = seq_dur_us × speed`；有 `speed_curve` 时以曲线积分为准，`src_dur_us` 必须由编译器算出来写入，**不许两边都手填**（这条是剪映 `time.duration` 与 `speed` 并存时的坑）。

#### 5.5 transform（归一化坐标）

```jsonc
"transform": {
  "layout": "fit",         // fit | fill | stretch | none
  "x": 0.0, "y": -0.38,    // 归一化：±1 = 画布宽/高的一半。0 = 居中
  "scale": [1.0, 1.0],
  "rotation_deg": 0.0,     // 逆时针为正（对齐剪映），顺时针写负
  "anchor": [0.5, 0.5],    // 锚点，画布归一化
  "opacity": 1.0,
  "flip": {"h": false, "v": false}
}
```

归一化的好处：换画布（16:9 → 9:16）时位置语义不变，重新排版只改 `layout` 与 `scale`，不重算像素。剪映的 `clip.transform.y = -0.76` 就是这个模型。

#### 5.6 crop

```jsonc
"crop": {
  "mode": "inset",                       // inset（四边内缩比例）| corners（四角自定义，做透视裁切）
  "left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0,   // mode=inset，0~1 比例
  "corners": null,                        // mode=corners 时给 8 个数
  "lock_aspect": false
}
```

#### 5.7 audio

```jsonc
"audio": {
  "gain_db": 0.0,
  "pan": 0.0,                        // -1 左 ~ 1 右
  "fade_in_us": 50000, "fade_out_us": 100000,
  "mute": false,
  "speed_pitch_lock": true,           // 变速时是否保持音高
  "denoise": {"enabled": true, "model": "deepfilternet", "amount": 0.8},
  "voice_separation": {"enabled": false, "stem": "vocal"},
  "eq": {"bands": [{"freq": 120, "gain_db": -2, "q": 0.7}]},
  "compressor": {"threshold_db": -18, "ratio": 3, "attack_ms": 10, "release_ms": 120},
  "chain": []                        // VST3 插件链（id + 参数快照）
}
```

`null` 语义：`"denoise": null` 表示「清除覆盖，跟随序列默认」。

#### 5.8 transition

```jsonc
"transition_in": {
  "id": "tk_01",
  "type": "cross_dissolve",           // 或 ofx/模板 引用
  "dur_us": 500000,
  "params": {"curve": "smooth"},
  "align": "center"                   // center | start | end（相对切点）
}
```

转场归属**切点**而不是片段本体：`transition_in` 挂在后一个片段上，`transition_out` 挂在前一个片段上，两者不许同时在同一侧生效（schema 校验拦）。

#### 5.9 text / subtitle / sticker

```jsonc
"text": {
  "kind": "subtitle",                 // text | subtitle | sticker | lyric
  "content": "这是字幕正文",
  "rich": [
    {"range": [0, 4], "bold": true, "size": 7, "fill": [1,1,1,1],
     "stroke": {"color": [0,0,0,1], "width": 0.056}}
  ],
  "box": {"w": 0.82, "h": null, "align": "center", "valign": "top", "max_lines": 2},
  "font": {"family": "思源黑体", "path": null, "fallback": ["Microsoft YaHei"]},
  "spacing": {"letter": 0.0, "line": 0.02},
  "animation": {"in": {"preset": "typewriter", "dur_us": 300000}, "out": null}
}
```

跟剪映的差别：它把富文本再包一层 JSON 字符串（双重序列化），我们直接把 `rich` 放成数组；它的 `range` 用字符下标，我们保留同语义但加版本前缀 `text:v1`，为将来的富文本模型留升级位。

#### 5.10 代理与缓存

代理不进工程文件，进 `media.derived` 与独立缓存目录；工程里只存 `proxy.path` 相对引用 + 生成参数。缓存目录采用「根 + 内容哈希」布局，删除缓存不影响工程可读。

#### 5.11 版本迁移

```jsonc
{"schema_version": "1.0.0", "min_reader": "1.0.0"}
```

规则：
- 读入时若 `schema_version` 高于自己的支持上限 → 拒绝打开并提示升级（不做静默降级）。
- 若 `min_reader` 高于自己 → 同上。
- 迁移函数链：`migrate_1_0_0_to_1_1_0(doc)` 纯函数，输入输出都是规范化 JSON，可单测。
- 每次迁移都在 `history.events` 里写一条 `system:migrate` 事件，留痕。

---

### 6. 规范化与 diff

规范化（canonicalization）算法，五步，顺序固定：

```
1. 对象键按字典序排序（递归）
2. 数组按第 3 节的规则排序
3. 删除与默认值相等的字段
4. 浮点统一为最短往返表示（Python repr / JS Number.prototype.toString 的 shortest round-trip）
5. UTF-8、LF 换行、不使用 \u 转义（除控制字符）
```

只有规范化之后才能做字节级 diff。语义 diff 用另一套：

```
语义 diff 的比较单位是「对象 + 属性」，不是行：
  added / removed / changed(objId, propPath, before, after)
输出用于：① UI 的改动列表  ② AI 决策的 before/after  ③ 协作同步的最小补丁
```

---

### 7. 并发与协作（第一版的最小实现）

| 机制 | 做法 |
| --- | --- |
| 乐观锁 | 每次提交带 `base_revision`，服务端比对后自增 `revision` |
| 单写者 | 同一序列同一时刻只有一个写者（UI 或某个 Agent run），用租约表管 |
| 冲突 | 属性级最后写入胜，但对象级删除优先（删了的对象不再被改活） |
| 合并 | 语义 diff 的最小补丁按属性路径三方合并；冲突项进待人工确认队列 |

第一版只做「单机多客户端 + 服务端合并」，不做 CRDT。理由：视频工程的强顺序语义（轨道顺序、主轨连续）用 CRDT 表达会引入大量不变量修复逻辑，收益低。

---

### 8. XML 视图（给 Agent 的形态）与映射表

#### 8.1 视图规则

- 标签名对应对象类型，属性名对应标量字段，嵌套对应子对象。
- **时间在 XML 里也是裸微秒**（与 JSON 一致，不做毫秒转换，避免单位陷阱）。
- 数组用重复标签 + 必需 `id`。
- 大块内容（转写、向量、波形）**不进 XML**，只给 `ref` 引用。

示例：

```xml
<project schema_version="1.0.0">
  <sequence id="sq_main" fps_num="30" fps_den="1" width="1920" height="1080" color="ACEScg">
    <track id="tr_v1" kind="video" role="main" index="0">
      <clip id="cl_01" media="md_01" seq_start_us="0" seq_dur_us="6150000"
            src_in_us="1565260000" speed="1.0" layout="fit" y="-0.38">
        <effect id="fx_01" type="blur.gaussian" order="0">
          <param name="radius" value="12"/>
          <keyframe prop="params.radius" t_us="0" v="0" interp="bezier"/>
        </effect>
        <transition_in id="tk_01" type="cross_dissolve" dur_us="500000" align="center"/>
      </clip>
    </sequence>
</project>
```

#### 8.2 字段映射表（JSON ↔ XML）

| JSON | XML | 说明 |
| --- | --- | --- |
| `sequences[].id` | `<sequence id>` | UUIDv7 字符串 |
| `sequences[].canvas.width/height` | `<sequence width height>` | 必须有值，只写 ratio 判无效 |
| `tracks[]` | `<track>` | `kind` / `role` / `index` 三属性 |
| `clips[]` | `<clip>` | 时间全为 `_us` 裸数值 |
| `transform.*` | `<clip layout x y scale_0 scale_1 rotation_deg opacity>` | 扁平化为属性，避免深层嵌套 |
| `keyframes[]` | `<keyframe prop t_us v interp/>` | `v` 标量写单值，向量写逗号分隔 |
| `effects[]` | `<effect>` + `<param>` + `<keyframe>` | `type` 必填 |
| `transitions` | `<transition_in/>` `<transition_out/>` | 只在切点侧出现一次 |
| `text.rich[]` | `<span range from to …/>` | 富文本区间 |
| `ai.runs[]` | 不进 XML | XML 视图只给结构，不给 AI 历史 |

#### 8.3 改动程序（AVS Selection DSL）

给模型的改工程语言，语法与剪映的 Selection Expression 同源，但选择器与 mutation 按我们的对象模型重定：

```
sel("#cl_01").attr("seq_dur_us", 4200000);
selAll("track#tr_v2 > clip").attr("mute", "true");
sel("#cl_01 > effect[type=blur.gaussian]").remove();
sel("#cl_01").appendXml(`<keyframe prop="transform.opacity" t_us="0" v="0" interp="ease_in"/>`);
sel("#tr_v1").reorderChildrenById("cl_01,cl_03,cl_02");
apply();
```

mutation 集合（12 个，闭集）：`attr` / `removeAttr` / `appendXml` / `prependXml` / `beforeXml` / `afterXml` / `replaceWithXml` / `replaceChildrenXml` / `remove` / `empty` / `reorderChildrenById` / `apply`。

四条硬约束（照抄剪映踩坑后的结论）：
1. `sel()` 必须恰好命中 1 个节点；`selAll()` 至少 1 个。
2. 每条语句以英文 `;` 结尾，必须真改东西（禁只选不改）。
3. `apply()` 必须是最后一条且只出现一次；不给 `apply()` 时改动只进候选区（`target`），不落地。
4. 校验失败不写候选区，原始状态保留。

#### 8.4 预演与落地

```
plan()   → 产生候选 XML，回给模型看，不落地
validate()→ 跑 schema 与不变量（主轨连续、无重叠、引用完整、时间范围有效）
apply()  → 开事务，编译 XML → JSON → 命令批次，一条命令一个 event，最后 commit
```
`plan → 人看一眼 → apply` 这条链路是产品级 AI 剪辑的必要形态：模型一次就对是奢望，**让它在候选区里改到对，再一次落地**。

---

### 9. 互转表

| 目标格式 | 映射难度 | 主要丢失项 | 做法 |
| --- | --- | --- | --- |
| **OTIO** | 低 | 效果参数、字幕富文本、音频链 | 主序列 → `Timeline`，轨道 → `Track`，片段 → `Clip`（`source_range` = 素材区间，`available_range` = 素材全长），变速 → `LinearTimeWarp.time_scalar`，嵌套 → `Stack` |
| **FCPXML** | 中 | 自定义效果、色彩 | 片段起始用 `offset`，`start`/`duration` 用有理数时间（`30000/1001s`） |
| **EDL / AAF** | 中高 | 单轨线性，其余全靠 `Clip` 备注 | 只对主轨做，副轨丢失；AAF 保留音频分轨 |
| **剪映草稿** | 中 | 加密、模板包、云资源 | 明文草稿可写可读；模板/特效只能引用它的 `resource_id`，效果具体参数不保证 |
| **达芬奇 `.drp`** | 高 | Fusion 合成、节点图 | 只导 OTIO 或 FCPXML 给达芬奇，反向不导 |
| **AE `.aep`（经 JSX）** | 高 | 效果链 | 不直接写 `.aep`，改成生成 JSX 脚本让 AE 执行（比 RIFX 稳妥） |
| **MLT XML** | 中 | 组合语义 | 做给 Shotcut/Kdenlive 的导出通道，用 `producer`/`playlist`/`tractor` 结构 |
| **Lottie** | 低 | 只覆盖动效 | 把文字动画与图形动画导出成 Lottie，给前端预览用 |

**OTIO 是必须打通的中枢**：达芬奇自己都把 OTIO 当一等导出格式，我们把它做成「外部世界通用货币」，AVS 是主存。

---

### 10. 完整样例（一个 18 行的最小工程）

```json
{
  "schema_version": "1.0.0",
  "min_reader": "1.0.0",
  "id": "prj_01HZX0000000000000000000A",
  "name": "demo",
  "created_us": 1795000000000000,
  "updated_us": 1795000000000000,
  "generator": {"app": "AI Video Studio", "version": "0.1.0"},
  "settings": {"default_sequence_id": "sq_main", "ai": {"max_batch_clips": 3}},
  "media": [{"id": "md_01", "kind": "video", "uri": "file:///D:/a.mp4",
             "probe": {"width": 1920, "height": 1080, "fps": {"num": 30, "den": 1, "drop_frame": false}, "dur_us": 6000000}}],
  "sequences": [{
    "id": "sq_main", "name": "主序列",
    "canvas": {"width": 1080, "height": 1920, "ratio": "9:16", "background": [0,0,0,1]},
    "fps": {"num": 30, "den": 1, "drop_frame": false},
    "sample_rate": 48000, "channels": 2, "dur_us": 6000000,
    "tracks": [{"id": "tr_v1", "kind": "video", "role": "main", "index": 0, "clips": [
      {"id": "cl_01", "media_id": "md_01", "seq_start_us": 0, "seq_dur_us": 6000000,
       "src_in_us": 0, "src_dur_us": 6000000, "speed": 1.0,
       "transform": {"layout": "fill", "x": 0, "y": 0, "scale": [1.0, 1.0], "rotation_deg": 0, "opacity": 1.0},
       "effects": [], "keyframes": []}
    ]}]
  }],
  "effects_lib": [], "ai": {"runs": []}, "history": {"cursor": 0, "events": []}
}
```

---

### 11. 校验清单（写进 CI 的不变量）

```
[ ] schema 校验通过（E_avs_project.schema.json）
[ ] 主轨唯一，且首段 seq_start_us == 0
[ ] 主轨片段首尾相接，无空洞无重叠
[ ] 同轨道片段不重叠
[ ] 所有 media_id / effect.type / nested sequence id 可解析
[ ] speed_curve 存在时 src_dur_us 等于曲线积分（容差 1ms）
[ ] 关键帧 t_us ∈ [0, seq_dur_us]
[ ] transition dur_us ≤ min(相邻两片段时长的 1/2)
[ ] 画布 width/height 为正整数
[ ] 规范化后再规范化，字节不变（幂等）
[ ] json → xml → json，规范化后字节相等
[ ] 事件日志可重放出同一工程状态（重放后规范化字节相等）
```

最后两条最狠，也最能防回归：**格式的往返一致性是可测的，AI 改动可重放也是可测的**。这两条一旦进 CI，工程格式就不会烂。

---

## 第七部分　最终技术选型

规则：每个模块只给四种判定之一——**用现成 / 借代码（fork 或摘模块）/ 调 SDK / 自研**，另加一个缓做标记。不出现「视情况」这种话。协议一律写全称，GPL 系一律进程外隔离。

判定依据三条：① 这层是否决定产品差异（决定的必须自研） ② 开源协议的传染性 ③ 三年后还维护得动的成本。

---

### 1. 一页速览

| # | 模块 | 判定 | 选择 | 协议 | 上它的阶段 |
| --- | --- | --- | --- | --- | --- |
| 1 | 桌面壳 | 用现成 | Qt 6.8（Widgets + Quick 混编） | LGPL-3.0（动态链接） | 1 |
| 2 | 时间轴控件 | 自研 | QWidget + QOpenGLWidget 自绘 | — | 2 |
| 3 | 媒体解码 | 用现成 | FFmpeg libav* 直连（libavcodec/libavformat/libswscale/libswresample） | LGPL-2.1（禁用 `--enable-gpl`） | 1 |
| 4 | 编码与封装 | 用现成 | FFmpeg + NVENC/QSV/AMF | 同上 + 各家 SDK | 2 |
| 5 | 时间轴数据模型 | **自研** | C++20，纯值语义，可单测 | — | 1 |
| 6 | 工程存储 | 用现成 | SQLite 3（WAL） | Public Domain | 1 |
| 7 | 工程格式 | **自研** | AVS（第六部分） | 自有 | 1 |
| 8 | 合成与节点图 | **自研** | 轻 DAG + WGSL 计算着色器 | 自有 | 3 |
| 9 | 特效宿主 | 调 SDK | OpenFX 1.4/1.5 宿主 | BSD-3-Clause | 4 |
| 10 | 色彩管理 | 用现成 | OpenColorIO 2.6 + ACES 2.0 config | BSD-3-Clause | 2 |
| 11 | 音频宿主 | 借代码 | JUCE（AGPL 轨或商业轨，二选一定死） | AGPL-3.0 / 商业 | 3 |
| 12 | 变速不变调 | 用现成 | Rubber Band（或 SoundTouch 兜底） | GPL-2.0（进程外）/ LGPL-2.1 | 4 |
| 13 | 降噪 | 用现成 | DeepFilterNet3（首选）+ RNNoise（轻量档） | MIT/Apache-2.0 / BSD-3 | 3 |
| 14 | 人声分离 | 用现成 | Demucs v4（htdemucs） | MIT | 4 |
| 15 | ASR 转写 | 用现成 | faster-whisper（GPU）+ whisper.cpp（CPU 兜底） | MIT | 3 |
| 16 | 词级对齐 + 说话人 | 用现成 | WhisperX + pyannote.audio | BSD-2 / MIT | 3 |
| 17 | 镜头切分 | 用现成 | PySceneDetect（内容感知）+ 自研音频能量辅助 | BSD-3 | 3 |
| 18 | 目标分割 / 抠像 | 用现成 | SAM 2（可提示分割）+ BiRefNet（人像，MIT）；RVM 是 GPL-3.0 不进主路 | Apache-2.0 / MIT | 4 |
| 19 | 检测与跟踪 | 借代码 | RT-DETR 或 YOLOX（避开 AGPL 的 YOLOv8/11）+ ByteTrack | Apache-2.0 / MIT | 4 |
| 20 | 视频理解 VLM | 调 SDK | 远端多模态（经 MAGPIE 路由）+ 端侧小模型打底 | — | 4 |
| 21 | Agent 框架 | **自研** | Director/Editor/Critic + 工具注册表 | 自有 | 3 |
| 22 | 模型网关 | 用现成 | MAGPIE（yetone/magpie，本地 3425 端口） | MIT | 2 |
| 23 | MCP 服务端 | 调 SDK + 自研 | Python/TS 官方 SDK（MIT）+ 自研 C++ JSON-RPC 层 | MIT / 自有 | 6 |
| 24 | 插件面板 | 用现成 | WebView2（Windows 内置） | 系统组件 | 5 |
| 25 | 打包与更新 | 用现成 | WiX/Burn + 自研增量更新 | MS-RL / 自有 | 1 |
| 26 | 崩溃上报 | 借代码 | Crashpad（fork） | Apache-2.0 | 1 |
| 27 | 测试与 CI | 用现成 | GoogleTest + pytest + GitHub Actions 自托管 | BSD-3 / MIT | 1 |
| 28 | 对外交换格式 | 用现成 | OpenTimelineIO（C++ 核 + Python 适配器） | Apache-2.0 | 5 |
| 29 | 备选剪辑引擎 | 缓做 | MLT Framework（只在需要「导入 Shotcut/Kdenlive 工程」时接） | LGPL-2.1 | 7 |
| 30 | 备选合成引擎 | 缓做 | Blender 无头渲染（GPL 隔离，进程外） | GPL-3.0 | 7 |

---

### 2. 逐模块判定与理由

#### 2.1 桌面壳：Qt 6.8（用现成）

**定 Qt 而非 Electron/Tauri。** 三条硬理由：
1. 时间轴要在 60fps 下重绘十万级图元，Qt 的 QWidget 自绘 + QOpenGLWidget 有明确的可控路径；Chromium 那层合成多一次上下文切换。
2. 要接 GPU 纹理、要低延迟预览、要硬件解码零拷贝，原生窗口系统接口是底线。
3. 三家专业软件全走 Qt（剪映 Qt6、达芬奇 Qt5），插件与工控生态成熟。

协议处理：动态链接 LGPL-3.0，不改 Qt 源码，不静态链接，提供 Qt 源码获取方式。**避开 GPL-only 模块**（Qt Quick 3D、Quick Timeline、HTTP Server、gRPC、MQTT、Virtual Keyboard、Wayland Compositor、Graphs 等 14 项），这些只用自研或替代。

#### 2.2 时间轴控件：自研

控件是产品的脸，也是性能瓶颈所在。现成方案（Qt 的 QGraphicsView、QML ListView）在「十万 item + 亚像素缩放 + 多轨对齐吸附」这个量级都会掉出 60fps。自绘 + 分层缓存（背景栅格 / 片段块 / 关键帧点 / 播放头 / 覆盖层）是唯一可控的做法。

#### 2.3 解码：FFmpeg libav* 直连（用现成）

**不走 ffmpeg.exe 命令行。** 命令行每帧一次管道拷贝、参数靠字符串拼，精确 seek 与逐帧控制都要绕。直连 libavcodec 能拿到：
- 精确帧定位（`av_seek_frame` + 双向解码到目标帧）；
- 硬解零拷贝（D3D11VA 纹理直接给渲染器）；
- 每源独立 `AVCodecContext`，多线程安全边界清晰；
- 色彩元数据（primaries/transfer/matrix/range）直读直用。

协议纪律：**编译期不加 `--enable-gpl`**，保持 LGPL-2.1；不链 x264（GPL），H.264 编码走硬件（NVENC/QSV/AMF）或 OpenH264。要 x265 时走命令行子进程（GPL 隔离）。

#### 2.4 编码与封装：FFmpeg + 三家硬件编码（用现成）

NVENC / QSV(libmfx 或 oneVPL) / AMF 三条通路覆盖 N/A/I 三厂。选实现策略：优先硬件 → 退软件 x264（进程外）→ 退 OpenH264。封装（MP4/MOV/MKV/MXF）用 libavformat 的 muxer，`-c copy` 分段拼接靠它。

#### 2.5 时间轴数据模型：自研（核心）

这是差异化的第一层，没有备选。要求写死：
- 纯 C++20，无第三方依赖，可独立单测（模型层不链 Qt）；
- 值语义 + 不可变快照（改一次产生新版本，UI 侧比较句柄）；
- 命令总线（第五部分 L4），命令可校验、可反转、可序列化进 event_log；
- 所有时间 int64 微秒，帧率有理数。

为什么不用 MLT 或 OTIO 做内核：MLT 的模型是「producer/playlist/tractor」三件套，服务的是播放管线，表达不了「主轨连续 + 副轨相对对齐 + 嵌套序列 + AI 决策留痕」；OTIO 是交换格式，没有编辑语义（没有命令、没有撤销、没有不变量）。两者都做**外部适配器**，不做内核。

#### 2.6 工程存储：SQLite（用现成）+ 内容寻址 blob

SQLite 的确定性优势：单文件、WAL 并发读、事务、崩溃安全、全平台一致、随应用分发（Public Domain）。工程库用 SQLite，大块数据用 sha256 命名的分桶文件。不用 LevelDB/RocksDB（无 SQL、工具链弱），不用自有二进制（调试成本高）。

#### 2.7 工程格式：自研 AVS（第六部分）

明文 JSON 主存 + XML 视图 + ZIP 包发布。三条硬要求：规范化后字节稳定、`json→xml→json` 往返一致、事件日志可重放。这层是产品护城河（可 diff、可审、可回放），不做妥协。

#### 2.8 合成与节点图：自研

自研范围：8 类节点（source/transform/color/blur/keyer/merge/text/time/output）、GPU 执行、关键帧求值、缓存句柄。不做 Fusion 那种全功能节点图（成本不可控），靠 OFX 补效果数量。

为什么不直接嵌 Natron（GPL）或 Fusion（闭源）：协议与体积都不成立；Natron 的节点引擎与其 UI 强耦合，摘出来比自己写贵。

#### 2.9 特效宿主：OpenFX（调 SDK）

OFX 1.4/1.5 是最划算的生态入口：写一次宿主，能直接吃 Resolve/Natron/Nuke 生态的插件。1.5 新增 Metal/CUDA/OpenCL 渲染与 `OfxDrawSuite`，向后兼容无 deprecation。

宿主要做的四件事：扫描目录 → 解析 bundle 的 `Info.plist`/XML → 建 `OfxHost` 回调表（进度、时间、内存、多线程、属性）→ 走 `describe/render`。第一版只支持 `eContextFilter` 与 `eContextTransition` 两种上下文。

#### 2.10 色彩管理：OpenColorIO 2.6 + ACES 2.0（用现成）

理由：ACES 2.0 的官方 config 就是 OCIO 格式，行业一致；GPU 侧走 `GpuShaderCreator` 产着色文本注入自家管线，跟达芬奇、AE 的做法一致。自研色彩管理在今天没有收益，只有坑。

#### 2.11 音频宿主：JUCE（借代码，协议先定死）

JUCE 能一次给齐：音频设备、VST3/AU 加载、DSP 模块、时间拉伸接口。协议两条路：
- **AGPL-3.0 轨**：开源整个应用（不现实）。
- **商业轨**：按营收分档付费（Starter 免费档有营收上限，Indie / Pro 是按用户月费制）。

第一版走商业轨的 Indie 档，并在预算里写死。备选：PortAudio（MIT 式）+ 自研 VST3 宿主（用 Steinberg 的 VST3 SDK，GPL-3.0 或 Steinberg 双协议），成本高 3 倍，作退路。

#### 2.12 变速不变调：Rubber Band（首选）/ SoundTouch（兜底）

Rubber Band 质量好、支持实时与非实时两套模式，GPL-2.0 → **进程外**：放 `audiofx.exe`，通过共享内存传 PCM，主程序不受传染。轻量档用 SoundTouch（LGPL-2.1，可直接链）。

#### 2.13 降噪：DeepFilterNet3 + RNNoise

端侧实时降噪两档：DeepFilterNet3（MIT/Apache-2.0 双协议，质量高，CPU 可跑）做默认；RNNoise（BSD-3，模型 120KB 级）做低端机与实时通话档。剪映用的就是 RNNoise v2 这类轻量模型，路径验证过。

#### 2.14 人声分离：Demucs v4（用现成）

MIT 协议，htdemucs 四轨分离质量在开源里第一梯队。推理放 AI 进程（GPU），结果以 PCM 存 blob。商用替代：MVSEP 类服务（走 API）——第一版不做，端侧够用。

#### 2.15 ASR：faster-whisper（GPU）+ whisper.cpp（CPU）

- GPU 路径：faster-whisper large-v3 + batching，3 小时素材在 12 分钟内可转完（第五部分性能预算）。
- CPU 兜底：whisper.cpp（量化模型），保证没有独显的机器也能用。
- 中文场景补 FunASR/Paraformer（MIT）作为可选后端：它对中文标点与口语更友好。

#### 2.16 词级对齐与说话人：WhisperX + pyannote

WhisperX 给词级时间戳（forced alignment），pyannote.audio 给说话人分段（diarization）。两者都 MIT，组合是社区标准做法。落地形态：一次推理出 `transcript + words[] + speakers[]`，写进 `media.derived`。

#### 2.17 镜头切分：PySceneDetect（用现成）

内容感知检测（HSV 差异 + 自适应阈值）就够用，再加一路自研的音频能量突变检测做交叉验证（画面没切但声音断了，也算一个语义切点）。输出 `shots[]` 带 `source_range`。

#### 2.18 分割与抠像：SAM 2 + 人像抠像模型

- 通用可提示分割：SAM 2（Apache-2.0）——点/框提示给 mask，做「选中这个人」「去掉这个物体」。
- 人像视频抠像：**BiRefNet（MIT）为主路**。RVM（Robust Video Matting）实测是 **GPL-3.0**，与闭源宿主冲突，只能走进程外或干脆不用——这条是 第四部分逐仓库核协议时抓出来的修正。
- 绿幕：自研色度键（成本极低，比模型快一个量级，且可控）。

#### 2.19 检测与跟踪：RT-DETR / YOLOX + ByteTrack（借代码，避开 AGPL）

**这条是协议红线**：Ultralytics 的 YOLOv8/v11 是 AGPL-3.0，商用闭源要么买商业授权要么整个应用开源。选 Apache-2.0 的 RT-DETR 或 YOLOX + MIT 的 ByteTrack，功能差距在追平。

#### 2.20 视频理解：远端 VLM 为主 + 端侧打底

3 小时素材塞不进任何模型的上下文。策略：镜头切分 + 抽关键帧 → 每镜一帧喂 VLM 打标（人物/场景/动作/情绪/可用性），得到结构化标签；叙事级判断交给强模型读「标签化摘要」。端侧跑轻量 CLIP 类做检索向量（剪映也是这条路：`chinese-clip-vit-base-patch16`）。

#### 2.21 Agent 框架：自研

不套 LangChain/AutoGen 这类通用编排：我们要的是「受限工具集 + 强事务 + 强留痕」，通用框架的自由度反而是负担。自研范围：RunContext、工具注册表（带 scope）、步骤账本、失败分类与重试策略、配额与预算控制。

#### 2.22 模型网关：MAGPIE（用现成）

`yetone/magpie` 是 MIT 的本地网关（Go + Wails），监听本地 `3425` 端口，`/v1` 前缀，能双向翻译 OpenAI Chat / OpenAI Responses / Anthropic Messages / Gemini 四套协议（流式与工具调用一起翻），路由组做组内多供应商顺位切换，账号级额度耗尽自动换同厂下一账号。

我们只加三样东西（不动它的协议层）：上下文预算器、任务路由表、计量账本。

#### 2.23 MCP 服务端：协议自研 + 官方 SDK 只用于工具脚本侧

- spec 2026-07-28，传输只有 stdio 与 Streamable HTTP，原语 Tools/Resources/Prompts + 客户端 Sampling/Elicitation/Roots，鉴权走 OAuth 式流程（含动态注册与 step-up authorization）。
- **官方 Python SDK（v2.3.0）与 TypeScript SDK（v2.4.0）都验证为 MIT 且可用**；C++ 侧没有可依赖的官方 SDK（该仓库路径三轮回退仍 404/连接中断，记为未核实）。结论：`mcp.exe` 的 JSON-RPC 层自研（协议很薄：帧头 + JSON + 会话表），Python 侧脚本工具直接用官方 SDK。
- 长任务用 `_meta.progressToken` + `notifications/progress`（progress 必须单调递增，total 可为浮点）。
- 工具名限 `A-Za-z0-9_-.`，1–128 字符——我们的命名 `analyze.transcribe` 符合这套规范。

#### 2.24 插件面板：WebView2（用现成）

Windows 自带，不需要分发 Chromium（省 200MB）。面板协议照达芬奇 Workflow Integration 的三件套：manifest（id/name/version/entry）+ preload（受限 API）+ 原生桥（C++ 暴露 QWebChannel 或自定义消息）。

#### 2.25 打包与更新：WiX + 自研增量

MSI 用 WiX（MS-RL），更新做增量（按文件块差分，参考 courgette 思路，剪映自己也带 `courgette64.exe`）。第一版只做全量更新 + 校验，增量放阶段 5。

#### 2.26 崩溃上报：Crashpad（借代码）

fork 一份 Crashpad（Apache-2.0），五个进程都挂 handler，符号走自建符号服务器。

#### 2.27 测试与 CI：GoogleTest + pytest + Actions 自托管

模型层与命令层用 GoogleTest（BSD-3）；AI 侧用 pytest（MIT）；CI 必须跑三条门禁：schema 校验、`json→xml→json` 往返、事件重放一致性（第六部分第 11 节）。

#### 2.28 对外交换：OpenTimelineIO（用现成）

OTIO Apache-2.0，C++ 核 + Python 适配器。我们做双向：AVS → OTIO（对外），OTIO → AVS（导入别人的时间轴）。达芬奇自己把 OTIO 当一等导出格式，这是行业通用货币。

#### 2.29 MLT：缓做

只在「导入 Shotcut/Kdenlive 工程」这个需求真的来了再接。MLT 的 XML 是它 API 结构的直映射，解析成本不低，收益单一。

#### 2.30 Blender 无头渲染：缓做

Blender 是 GPL-3.0，只能进程外。价值在于 3D 图层与体积特效，属于阶段 7 的加分项，不做地基。

---

### 3. 三条协议红线（写进代码评审清单）

| 组件 | 协议 | 处理 |
| --- | --- | --- |
| x264 / x265 / 大部分 GPL 编码器 | GPL-2.0 | 只进程外调用，不分发二进制，不静态链 |
| Ultralytics YOLO 系列 | AGPL-3.0 | 不用；换 RT-DETR / YOLOX |
| ComfyUI | GPL-3.0 | 只在「生成式管线」需求成立时进程外接入 |
| Natron | GPL-2.0 | 不 embed，只参考算法 |
| Blender | GPL-3.0 | 进程外 |
| Rubber Band | GPL-2.0 | 进程外（`audiofx.exe`） |
| JUCE | AGPL / 商业 | 买商业轨 |
| Qt | LGPL-3.0（动态）/ GPL 模块 | 动态链接 + 避开 GPL-only 模块 |
| FFmpeg | LGPL-2.1 | 不加 `--enable-gpl`，不链 GPL 外部库 |
| MLT / Shotcut / Kdenlive / LosslessCut | LGPL / GPL-3 / GPL-2 | 参考架构，不复制代码 |

---

### 4. 三年成本权衡（为什么这么定）

| 决策 | 一次性成本 | 三年维护成本 | 结论 |
| --- | --- | --- | --- |
| 自研时间轴模型 | 高（3 人×3 月） | 低（自己的代码，改动可控） | 定 |
| 套 MLT 做内核 | 低 | 高（它的模型不匹配我们的不变量，每加一个 AI 能力都要跟它的架构打架） | 否 |
| 自研节点图 | 中 | 中 | 定 |
| 嵌 Natron | 中 | 高（GPL + UI 强耦合） | 否 |
| OFX 宿主 | 中 | 低（生态自己长） | 定 |
| 自研 Agent | 中 | 低（业务逻辑集中） | 定 |
| 套 LangChain | 低 | 高（版本漂移 + 抽象错位） | 否 |

---

### 5. 一句话总结

**能借生态的全借（FFmpeg / OCIO / OFX / OTIO / MAGPIE / MCP / SAM2 / Whisper 系），决定产品差异的三层全自研（时间轴模型 / 工程格式 / Agent 与事务）**。其余按协议红线做进程隔离，一分别省错地方。

---

## 第八部分　开发路线图

七个阶段，每阶段必须交出「能跑的东西」。验收标准写成可测的数字或可勾的清单，不写「基本可用」。

贯穿全程的三条门禁（每次合并都跑）：
1. `E_avs_project.schema.json` 校验通过。
2. `json → xml → json` 规范化后字节相等。
3. 事件日志重放出的工程状态与保存态规范字节相等。

---

### 阶段 1：基础桌面工作站（约 3 个月）

**目标**：能打开素材、能在时间轴上剪、能导出成片。一条最短路走通，不追专业能力。

| 交付 | 内容 |
| --- | --- |
| 进程骨架 | `studio.exe` / `media.exe` / `projectd.exe` 三进程；gRPC over 命名管道；共享内存帧通道 |
| 时间轴模型 | C++20 模型层（sequence/track/clip/transform/crop/audio/keyframe）+ 命令总线 + 撤销重做 |
| 工程存储 | SQLite 库 + AVS JSON 读写 + 规范化 + 版本迁移框架 |
| 媒体层 | FFmpeg 直连解码（H.264/H.265/ProRes/DNxHR）、代理生成、波形、缩略图 |
| UI | 主窗 + 媒体箱 + 时间轴（自绘）+ 监视器 + 属性面板 |
| 导出 | H.264/H.265 硬编 + AAC，单进程，进度条 |
| 安装 | MSI 打包 + 崩溃上报（Crashpad） |

**依赖**：无（起点）
**验收**
- [ ] 导入 3 个 4K 素材，拖到主轨，裁切/分割/变速，导出 1080p H.264，时长与帧数一致（±0 帧）
- [ ] 1080p 代理预览 60 秒不掉帧（dropped frame 计数为 0）
- [ ] 撤销 100 步后工程与初始状态规范字节相等
- [ ] 强制 kill `media.exe`，UI 不崩，自动重启后从当前帧续解
- [ ] 工程保存 → 关闭 → 打开，规范化字节相等

**可运行成果**：一个能剪单轨、能出片的桌面剪辑器（对标剪映 0.5 的能力）。

---

### 阶段 2：专业时间轴与媒体引擎（约 4 个月）

**目标**：多轨、嵌套、转场、关键帧动画、精确时间码；导出能并行到接近线性加速。

| 交付 | 内容 |
| --- | --- |
| 多轨与嵌套 | 主轨连续约束、副轨相对对齐（anchor）、复合片段（嵌套序列） |
| 转场 | 切点归属模型、溶解/擦除/推拉三类 + 变速转场（时间重映射） |
| 关键帧 | 贝塞尔/保持/缓动、曲线编辑器 |
| 时间码 | 有理数帧率 + drop-frame 显示与解析 |
| 渲染 | `render.exe` 多开、按 GOP 切片并行、分段拼接、音频独立拼轨 |
| 色彩 | OCIO 2.6 + ACES 2.0 config、显示变换、片段级色彩空间解释 |
| 代理体系 | 后台代理生成、代理/原片一键切换、代理缺失自动回退 |

**依赖**：阶段 1 的模型层与存储层
**验收**
- [ ] 5 轨叠加 + 2 层嵌套 + 3 个转场，4K 序列 30fps 预览稳
- [ ] 导出 4K 60 秒 H.265，8 worker < 90 秒；分段拼接后音画同步误差 < 1 帧
- [ ] 29.97 DF 时间码进出一致（`01:00:00;00` ↔ 微秒无损往返）
- [ ] ACES 工程下导入 S-Log3 素材，显示变换正确，导出与预览一致（像素差 < 1/255）
- [ ] 代理缺失时自动切原片，播放不停

**可运行成果**：能接商业活的多轨剪辑器（对标 Kdenlive/Shotcut 的能力面，性能更好）。

---

### 阶段 3：AI Agent（约 4 个月）

**目标**：Agent 能读工程、能改工程、改完能自查；模型网关打通；转写与镜头切分进流水线。

| 交付 | 内容 |
| --- | --- |
| XML 视图编译器 | `project.json ↔ 内存 XML`，双向一致（门禁 2） |
| Selection DSL | 12 个 mutation + 选择器 + `plan/validate/apply` 三段式 |
| Agent 角色 | Director（任务契约）/ Editor（改工程）/ Critic（审片，四级证据） |
| 工具注册表 | 22 个工具 + scope（user/agent/external）+ 权限白名单 |
| 步骤账本 | 每步输入哈希 + 输出 blob + 断点续跑 |
| 模型网关 | MAGPIE 接入（3425 端口）+ 任务路由表 + 上下文预算器 + token 计量 |
| 分析管线 | faster-whisper 转写 + WhisperX 对齐 + pyannote 说话人 + PySceneDetect 镜头 |

**依赖**：阶段 2 的模型层（命令总线与不变量）
**验收**
- [ ] 一段 10 分钟口播 → 「剪成 60 秒竖版，去水词」→ Agent 出一版粗剪，人工接受率 ≥ 60%（20 条样本）
- [ ] Agent 的每次写操作都走白名单命令，且能 `undo` 一键回到改前状态
- [ ] `plan` 阶段不落地（磁盘字节不变），`apply` 后候选与落地一致
- [ ] Agent 上下文里不含任何原始视频帧，只有摘要与引用（可审计）
- [ ] 转写 3 小时素材 < 12 分钟（GPU），词级时间戳对齐误差中位数 < 80ms
- [ ] 故意注入非法操作（删主轨、越界片段），全部在 `validate` 被拦

**可运行成果**：一个能自己剪第一版的剪辑器，人只做判断不做搬砖。

---

### 阶段 4：自主剪辑（约 5 个月）

**目标**：从「一片」到「一套流程」：脚本 → 分镜 → 粗剪 → 精剪 → 包装 → 审片，全链路自动，带质量门。

| 交付 | 内容 |
| --- | --- |
| 脚本层 | 分镜脚本中间表示（shots 带 source_range、意图、时长预算） |
| 粗剪 | 选段 + 排序 + 节奏（音频能量 + 语义重点） |
| 精剪 | 边界精修（词级对齐驱动）、跳剪、J/L cut、变速匹配 |
| 包装 | 字幕（逐字/整句/花字）、贴纸、转场、片头片尾模板 |
| 音频自动链 | 降噪 → 分离 → 响度归一（-14 LUFS）→ 压缩/EQ → 淡入淡出 |
| 审片 Critic | 六个维度（内容节奏/画幅构图/字幕文字/音频/时间线资源/交付结构），输出问题 + 证据 + 最小返修 |
| 返修闭环 | Critic 的问题回灌 Editor，最多 3 轮，收敛即停 |
| 自然语言改片 | 「第 3 段剪短点」「换成横版」「字幕再大一号」→ 落到命令 |

**依赖**：阶段 3 的 Agent 与工具层；阶段 2 的多轨与转场
**验收**
- [ ] 一条 26 分钟素材 → 30 秒竖版成片，全链路无人干预 < 8 分钟
- [ ] 成片通过 Critic 六维检查，问题数 ≤ 2 且都带证据定位
- [ ] 自然语言改片指令 20 条，正确落地 ≥ 18 条
- [ ] 同一素材跑三次，成片结构相似度（切点重合率）> 70%
- [ ] AI 决策记录完整率 100%（每个片段都能追到 run 与 rationale）

**可运行成果**：一键出片的工作站，人只审片与微调。

---

### 阶段 5：专业特效与音频（约 5 个月）

**目标**：从「短视频级」到「广播级」：节点合成、OFX 生态、调色、VST3、三维声起点。

| 交付 | 内容 |
| --- | --- |
| 节点图 | 8 类节点 + WGSL 求值 + 缓存句柄 + 节点级缓存 |
| OFX 宿主 | 1.4/1.5，`eContextFilter` + `eContextTransition`，扫描与参数 UI 自动生成 |
| 调色 | 节点式调色（LGG/曲线/HSL/色轮）、LUT、`.cube` 导入、片段级与序列级 |
| 音频宿主 | JUCE + VST3 进程外托管 + 插件扫描与崩溃隔离 |
| 变速不变调 | Rubber Band 进程外 + 音高锁定 |
| 字幕与文字 | 富文本、逐字动画、模板包（参数槽位） |
| 三维声起点 | 5.1 / 7.1 混音与导出（Atmos 走桥接，不做自研编码） |

**依赖**：阶段 2 的渲染管线；阶段 4 的包装能力
**验收**
- [ ] 20 个节点级联合成，4K 单帧渲染 < 120ms（GPU）
- [ ] 接 3 个真实 OFX 插件（去噪/抠像/光流），参数 UI 自动生成且可关键帧
- [ ] 调色节点链 6 级，导出与预览像素差 < 1/255
- [ ] VST3 插件崩溃不影响宿主（进程外托管验证：故意崩溃 5 个插件，应用无感）
- [ ] 500% 变速下音高不变（频谱基频偏移 < 2%）
- [ ] 响度导出 -14 LUFS ±0.5，真峰 -1 dBTP

**可运行成果**：能做广告片与短剧后期的工作站。

---

### 阶段 6：MCP 与外部 Agent 接入（约 3 个月）

**目标**：把工作站变成工具。Codex / Claude / 任何 MCP 客户端能创建工程、导素材、分析、粗剪、精剪、改时间轴、加字幕特效、处理音频、预览、导出、查进度。

| 交付 | 内容 |
| --- | --- |
| MCP Server | stdio + Streamable HTTP（spec 2026-07-28），OAuth 式鉴权 |
| 22 个工具 | 见 第五部分 L12 工具清单，全部带 JSON Schema 入参 |
| 长任务 | `_meta.progressToken` + `notifications/progress`（单调递增）+ 断线可查 |
| 交互 | elicitation 用于「选哪个素材」「要不要覆盖」这类决策 |
| 权限 | 外部 Agent 默认只读 + 剪辑白名单；写权限要显式开启并留痕 |
| 文档 | 每个工具一页说明 + 3 个可复制的工作流示例（Codex 脚本） |

**依赖**：阶段 3-5 的命令总线与工具层
**验收**
- [ ] Codex 用 MCP 完成「建工程 → 导 3 个素材 → 分析 → 粗剪 → 加字幕 → 导出」全流程，无需人工点界面
- [ ] 外部 Agent 与内部 Agent 走同一套事务与留痕（可对比 `event_log`）
- [ ] 长任务中断后重连，用原 progressToken 查到状态并续跑
- [ ] 工具名与入参 schema 通过 MCP 规范的字符与长度约束（CI 校验）
- [ ] 未授权写操作被拒绝且返回可读错误（含修复方式）

**可运行成果**：一个可被任何 Agent 编排的视频工作站。

---

### 阶段 7：完整工作站（约 6 个月）

**目标**：把前面六阶段合成一个能卖的产品：多工程、协作、模板市场、3D 起点、稳定性与性能收口。

| 交付 | 内容 |
| --- | --- |
| 多工程与快照 | 工程库管理、快照与恢复、归档打包（`.avsproj`） |
| 协作 | 单机多客户端 + 服务端语义合并（属性级三方合并）；冲突队列 |
| 模板与市场 | 模板包规范（参数 schema + 预览帧 + 槽位）、导入导出、版本兼容 |
| 3D 起点 | 3D 图层 + 摄像机 + 灯光（不做体积与粒子） |
| 交换 | OTIO / FCPXML / EDL / AAF / MLT / 剪映明文草稿 / Lottie |
| 性能收口 | 大工程（500 片段 / 20 轨）打开 < 3 秒，滚动 60fps |
| 稳定性 | 五进程看门狗、崩溃自动恢复、长任务断点续跑、7×24 渲染农场验证 |
| 交付工程 | 安装包、增量更新、签名、符号服务器、诊断包导出 |

**依赖**：全部前序
**验收**
- [ ] 500 片段 / 20 轨 / 3 层嵌套工程，打开 < 3 秒，时间轴滚动 60fps
- [ ] 两人同时改同一序列，合并后无数据丢失且不变量全过
- [ ] 模板从市场下载 → 改参数 → 导出，全流程 < 2 分钟
- [ ] 连续渲染 8 小时无内存增长（RSS 波动 < 5%）
- [ ] 六种交换格式往返：AVS → X → AVS，主轨切点与时长误差 < 1 帧

**可运行成果**：可交付客户的专业工作站。

---

### 时间与人力（一条排法）

| 阶段 | 月数 | 人力（人月） | 关键岗位 |
| --- | --- | --- | --- |
| 1 | 3 | 9 | C++ 桌面 ×2、媒体 ×1 |
| 2 | 4 | 16 | +渲染 ×1、色彩 ×1、UI ×1 |
| 3 | 4 | 16 | +Agent ×1、算法 ×1 |
| 4 | 5 | 20 | +剪辑算法 ×1、音频 ×1 |
| 5 | 5 | 20 | +图形 ×1、音频 ×1 |
| 6 | 3 | 9 | +后端 ×1 |
| 7 | 6 | 24 | +测试 ×1、运维 ×1 |
| 合计 | 30 | 114 | 峰值团队 8-10 人 |

阶段 2 与 3 可以并行（模型层与 Agent 层接口在阶段 1 就定死）；阶段 4 必须等 3 的 DSL 稳定；阶段 5 与 6 可并行。

---

### 每个阶段的「不许跳过」

| 阶段 | 不许跳过的东西 | 跳了会怎样 |
| --- | --- | --- |
| 1 | 命令总线与撤销 | 后面所有 AI 改动都没有事务边界，返工重写 |
| 1 | 规范化与往返测试 | 工程格式从此不可 diff，AI 改动的 diff 失去意义 |
| 2 | 分段并行渲染 | 4K 长片导出从 1 分钟变 20 分钟，产品直接不成立 |
| 2 | 音频主时钟 | 预览音画不同步，全片节奏判断全废 |
| 3 | 三段式（plan/validate/apply） | 模型一次写错就毁工程，用户不敢用 |
| 3 | 步骤账本 | 长任务一断就得从头跑，成本翻十倍 |
| 4 | 四级证据的审片 | Critic 会拿「草稿结构」当「成片呈现」，结论不可信 |
| 5 | 插件进程隔离 | 一个第三方插件崩溃带走整个会话 |
| 6 | 外部与内部同一套事务 | 外部 Agent 绕过留痕，出了问题查不到 |
| 7 | 协作的不变量校验 | 合并出「主轨空洞」这类非法状态，模型层崩 |

---

### 里程碑（对外可讲的节点）

| 时间点 | 里程碑 | 一句话 |
| --- | --- | --- |
| M3 | 能剪能出片 | 单轨剪辑器可用 |
| M7 | 专业多轨 | 4K 多轨 + 并行导出 |
| M11 | Agent 改工程 | 说一句话就能改片 |
| M16 | 一键出片 | 26 分钟素材出 30 秒成片 |
| M21 | 广播级 | OFX + 调色 + VST3 |
| M24 | 可被编排 | MCP 接入，外部 Agent 可控 |
| M30 | 可卖 | 协作 + 模板市场 + 稳定性 |

---

## 附录 A　AVS 1.0 JSON Schema 全文

> 机器可读版本见工程目录 `E_avs_project.schema.json`；下面内联同一份内容，便于单文件交付。

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aivideostudio.local/schema/avs_project.schema.json",
  "title": "AVS Project",
  "description": "AI Video Studio 工程文件（AVS 1.0）唯一真相格式。时间字段一律 int64 微秒，帧率一律有理数。",
  "type": "object",
  "additionalProperties": true,
  "required": ["schema_version", "min_reader", "id", "name", "sequences"],
  "properties": {
    "schema_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "min_reader": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "id": { "$ref": "#/$defs/id" },
    "name": { "type": "string", "minLength": 1, "maxLength": 200 },
    "created_us": { "type": "integer", "minimum": 0 },
    "updated_us": { "type": "integer", "minimum": 0 },
    "generator": {
      "type": "object",
      "properties": {
        "app": { "type": "string" },
        "version": { "type": "string" },
        "model_runs": { "type": "integer", "minimum": 0 }
      }
    },
    "settings": { "$ref": "#/$defs/settings" },
    "media": { "type": "array", "items": { "$ref": "#/$defs/media" } },
    "sequences": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/sequence" } },
    "effects_lib": { "type": "array", "items": { "$ref": "#/$defs/effect_def" } },
    "ai": { "$ref": "#/$defs/ai" },
    "history": { "$ref": "#/$defs/history" },
    "_ext": { "type": "object" }
  },
  "$defs": {
    "id": {
      "type": "string",
      "minLength": 3,
      "maxLength": 64,
      "description": "对象唯一标识。生产环境用带前缀的 UUIDv7（sq_/tr_/cl_/fx_/kf_/md_/tk_/tx_）；样例与测试允许短标识（如 sq_main），只要同工程内唯一。"
    },
    "us": { "type": "integer" },
    "rational": {
      "type": "object",
      "required": ["num", "den"],
      "properties": {
        "num": { "type": "integer", "minimum": 1 },
        "den": { "type": "integer", "minimum": 1 },
        "drop_frame": { "type": "boolean", "default": false }
      },
      "additionalProperties": false
    },
    "color4": {
      "type": "array", "minItems": 4, "maxItems": 4,
      "items": { "type": "number", "minimum": 0, "maximum": 1 }
    },

    "settings": {
      "type": "object",
      "properties": {
        "default_sequence_id": { "$ref": "#/$defs/id" },
        "ui": { "type": "object" },
        "ai": {
          "type": "object",
          "properties": {
            "model_route": { "type": "string" },
            "auto_apply_threshold": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.7 },
            "max_batch_clips": { "type": "integer", "minimum": 1, "default": 3 }
          }
        },
        "render": {
          "type": "object",
          "properties": { "default_preset_id": { "type": "string" } }
        },
        "paths": { "type": "object", "additionalProperties": { "type": "string" } }
      }
    },

    "media": {
      "type": "object",
      "required": ["id", "kind", "uri"],
      "properties": {
        "id": { "$ref": "#/$defs/id" },
        "kind": { "enum": ["video", "audio", "image", "sequence", "generator"] },
        "uri": { "type": "string" },
        "rel_uri": { "type": "string" },
        "sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
        "probe": {
          "type": "object",
          "properties": {
            "width": { "type": "integer", "minimum": 1 },
            "height": { "type": "integer", "minimum": 1 },
            "fps": { "$ref": "#/$defs/rational" },
            "dur_us": { "$ref": "#/$defs/us" },
            "video_codec": { "type": "string" },
            "pix_fmt": { "type": "string" },
            "color": {
              "type": "object",
              "properties": {
                "primaries": { "type": "string" },
                "transfer": { "type": "string" },
                "matrix": { "type": "string" },
                "range": { "enum": ["tv", "pc"] }
              }
            },
            "audio": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "codec": { "type": "string" },
                  "channels": { "type": "integer", "minimum": 1 },
                  "sample_rate": { "type": "integer", "minimum": 8000 }
                }
              }
            }
          }
        },
        "proxy": {
          "type": "object",
          "properties": {
            "path": { "type": "string" },
            "scale": { "type": "number", "exclusiveMinimum": 0, "maximum": 1 },
            "codec": { "type": "string" }
          }
        },
        "derived": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["kind", "blob"],
            "properties": {
              "kind": { "enum": ["waveform", "thumbnail", "transcript", "embedding", "proxy_index", "scene_cuts"] },
              "blob": { "type": "string" },
              "at_us": { "$ref": "#/$defs/us" },
              "lang": { "type": "string" },
              "diarized": { "type": "boolean" },
              "model": { "type": "string" }
            }
          }
        }
      }
    },

    "sequence": {
      "type": "object",
      "required": ["id", "name", "canvas", "fps", "tracks"],
      "properties": {
        "id": { "$ref": "#/$defs/id" },
        "name": { "type": "string" },
        "canvas": {
          "type": "object",
          "required": ["width", "height"],
          "properties": {
            "width": { "type": "integer", "minimum": 1 },
            "height": { "type": "integer", "minimum": 1 },
            "ratio": { "type": "string" },
            "background": { "$ref": "#/$defs/color4" }
          }
        },
        "fps": { "$ref": "#/$defs/rational" },
        "sample_rate": { "type": "integer", "minimum": 8000, "default": 48000 },
        "channels": { "type": "integer", "minimum": 1, "default": 2 },
        "color": {
          "type": "object",
          "properties": {
            "working": { "type": "string" },
            "display": { "type": "string" },
            "view": { "type": "string" },
            "ocio_config": { "type": "string" }
          }
        },
        "audio": {
          "type": "object",
          "properties": {
            "loudness_target_lufs": { "type": "number" },
            "true_peak_db": { "type": "number", "maximum": 0 },
            "normalize": { "type": "boolean", "default": false }
          }
        },
        "dur_us": { "$ref": "#/$defs/us" },
        "tracks": { "type": "array", "items": { "$ref": "#/$defs/track" } },
        "markers": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "at_us"],
            "properties": {
              "id": { "$ref": "#/$defs/id" },
              "at_us": { "$ref": "#/$defs/us" },
              "name": { "type": "string" },
              "color": { "type": "string" }
            }
          }
        },
        "nested_in": { "$ref": "#/$defs/id" }
      }
    },

    "track": {
      "type": "object",
      "required": ["id", "kind", "role", "clips"],
      "properties": {
        "id": { "$ref": "#/$defs/id" },
        "kind": { "enum": ["video", "audio", "text", "sticker", "effect", "mixed"] },
        "role": { "enum": ["main", "multi"] },
        "index": { "type": "integer", "minimum": 0, "default": 0 },
        "name": { "type": "string" },
        "locked": { "type": "boolean", "default": false },
        "muted": { "type": "boolean", "default": false },
        "hidden": { "type": "boolean", "default": false },
        "blend_default": { "type": "string", "default": "normal" },
        "clips": { "type": "array", "items": { "$ref": "#/$defs/clip" } }
      }
    },

    "clip": {
      "type": "object",
      "required": ["id", "seq_dur_us"],
      "properties": {
        "id": { "$ref": "#/$defs/id" },
        "media_id": { "$ref": "#/$defs/id" },
        "seq_start_us": { "$ref": "#/$defs/us" },
        "seq_dur_us": { "type": "integer", "minimum": 0 },
        "src_in_us": { "$ref": "#/$defs/us" },
        "src_dur_us": { "type": "integer", "minimum": 0 },
        "speed": { "type": "number", "exclusiveMinimum": 0, "default": 1.0 },
        "speed_curve": {
          "oneOf": [
            { "type": "null" },
            {
              "type": "object",
              "required": ["points"],
              "properties": {
                "points": {
                  "type": "array", "minItems": 2,
                  "items": {
                    "type": "object",
                    "required": ["t_us", "speed"],
                    "properties": {
                      "t_us": { "$ref": "#/$defs/us" },
                      "speed": { "type": "number", "exclusiveMinimum": 0 }
                    }
                  }
                },
                "interp": { "enum": ["linear", "smooth"], "default": "linear" }
              }
            }
          ]
        },
        "anchor": {
          "oneOf": [
            { "type": "null" },
            {
              "type": "object",
              "required": ["start_to"],
              "properties": {
                "start_to": { "type": "string" },
                "offset_us": { "$ref": "#/$defs/us" }
              }
            }
          ]
        },
        "enabled": { "type": "boolean", "default": true },
        "locked": { "type": "boolean", "default": false },
        "transform": { "$ref": "#/$defs/transform" },
        "crop": { "$ref": "#/$defs/crop" },
        "audio": { "$ref": "#/$defs/audio" },
        "effects": { "type": "array", "items": { "$ref": "#/$defs/effect_inst" } },
        "keyframes": { "type": "array", "items": { "$ref": "#/$defs/keyframe" } },
        "transition_in": { "$ref": "#/$defs/transition" },
        "transition_out": { "$ref": "#/$defs/transition" },
        "text": { "$ref": "#/$defs/text" },
        "ai": {
          "type": "object",
          "properties": {
            "run_id": { "$ref": "#/$defs/id" },
            "decision_id": { "$ref": "#/$defs/id" }
          }
        }
      }
    },

    "transform": {
      "type": "object",
      "properties": {
        "layout": { "enum": ["fit", "fill", "stretch", "none"], "default": "fit" },
        "x": { "type": "number", "minimum": -100000, "maximum": 100000, "default": 0 },
        "y": { "type": "number", "minimum": -100000, "maximum": 100000, "default": 0 },
        "scale": {
          "type": "array", "minItems": 2, "maxItems": 2,
          "items": { "type": "number", "exclusiveMinimum": 0 },
          "default": [1.0, 1.0]
        },
        "rotation_deg": { "type": "number", "default": 0 },
        "anchor": {
          "type": "array", "minItems": 2, "maxItems": 2,
          "items": { "type": "number" },
          "default": [0.5, 0.5]
        },
        "opacity": { "type": "number", "minimum": 0, "maximum": 1, "default": 1 },
        "flip": {
          "type": "object",
          "properties": {
            "h": { "type": "boolean", "default": false },
            "v": { "type": "boolean", "default": false }
          }
        }
      }
    },

    "crop": {
      "type": "object",
      "properties": {
        "mode": { "enum": ["inset", "corners"], "default": "inset" },
        "left": { "type": "number", "minimum": 0, "maximum": 1, "default": 0 },
        "right": { "type": "number", "minimum": 0, "maximum": 1, "default": 0 },
        "top": { "type": "number", "minimum": 0, "maximum": 1, "default": 0 },
        "bottom": { "type": "number", "minimum": 0, "maximum": 1, "default": 0 },
        "corners": {
          "type": ["array", "null"], "minItems": 8, "maxItems": 8,
          "items": { "type": "number" }
        },
        "lock_aspect": { "type": "boolean", "default": false }
      }
    },

    "audio": {
      "type": "object",
      "properties": {
        "gain_db": { "type": "number", "minimum": -96, "maximum": 24, "default": 0 },
        "pan": { "type": "number", "minimum": -1, "maximum": 1, "default": 0 },
        "fade_in_us": { "$ref": "#/$defs/us" },
        "fade_out_us": { "$ref": "#/$defs/us" },
        "mute": { "type": "boolean", "default": false },
        "speed_pitch_lock": { "type": "boolean", "default": true },
        "denoise": {
          "oneOf": [
            { "type": "null" },
            {
              "type": "object",
              "required": ["enabled"],
              "properties": {
                "enabled": { "type": "boolean" },
                "model": { "type": "string" },
                "amount": { "type": "number", "minimum": 0, "maximum": 1 }
              }
            }
          ]
        },
        "voice_separation": {
          "oneOf": [
            { "type": "null" },
            {
              "type": "object",
              "required": ["enabled"],
              "properties": {
                "enabled": { "type": "boolean" },
                "stem": { "enum": ["vocal", "music", "other"] }
              }
            }
          ]
        },
        "eq": {
          "type": "object",
          "properties": {
            "bands": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["freq", "gain_db"],
                "properties": {
                  "freq": { "type": "number", "minimum": 20, "maximum": 20000 },
                  "gain_db": { "type": "number", "minimum": -24, "maximum": 24 },
                  "q": { "type": "number", "minimum": 0.1, "maximum": 18 }
                }
              }
            }
          }
        },
        "compressor": {
          "type": "object",
          "properties": {
            "threshold_db": { "type": "number", "minimum": -60, "maximum": 0 },
            "ratio": { "type": "number", "minimum": 1, "maximum": 20 },
            "attack_ms": { "type": "number", "minimum": 0 },
            "release_ms": { "type": "number", "minimum": 1 }
          }
        },
        "chain": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id"],
            "properties": {
              "id": { "type": "string" },
              "plugin": { "type": "string" },
              "params": { "type": "object" },
              "bypass": { "type": "boolean", "default": false }
            }
          }
        }
      }
    },

    "effect_def": {
      "type": "object",
      "required": ["type", "impl"],
      "properties": {
        "type": { "type": "string" },
        "impl": {
          "type": "object",
          "required": ["kind"],
          "properties": {
            "kind": { "enum": ["node", "ofx", "dctl", "template"] },
            "node": { "type": "string" },
            "gpu": { "enum": ["wgsl", "cuda", "cpu"] },
            "bundle": { "type": "string" },
            "plugin_id": { "type": "string" },
            "package_id": { "type": "string" }
          }
        },
        "params_schema": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "type": { "enum": ["float", "int", "bool", "enum", "color", "vec2", "curve", "string"] },
              "min": { "type": "number" },
              "max": { "type": "number" },
              "default": {},
              "values": { "type": "array" },
              "ui": { "type": "string" },
              "unit": { "type": "string" }
            }
          }
        },
        "channels": { "type": "array", "items": { "enum": ["video", "audio"] } }
      }
    },

    "effect_inst": {
      "type": "object",
      "required": ["id", "type", "order"],
      "properties": {
        "id": { "$ref": "#/$defs/id" },
        "type": { "type": "string" },
        "order": { "type": "integer", "minimum": 0 },
        "enabled": { "type": "boolean", "default": true },
        "params": { "type": "object" },
        "keyframes": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["prop", "t_us", "v"],
            "properties": {
              "prop": { "type": "string", "pattern": "^params\\.[A-Za-z0-9_.]+$" },
              "t_us": { "$ref": "#/$defs/us" },
              "v": {},
              "interp": { "enum": ["linear", "hold", "bezier", "ease_in", "ease_out"], "default": "bezier" }
            }
          }
        }
      }
    },

    "keyframe": {
      "type": "object",
      "required": ["prop", "t_us", "v"],
      "properties": {
        "id": { "$ref": "#/$defs/id" },
        "prop": {
          "type": "string",
          "pattern": "^(transform\\.(x|y|scale|rotation_deg|opacity)|audio\\.(gain_db|pan))$"
        },
        "t_us": { "$ref": "#/$defs/us" },
        "v": {},
        "interp": { "enum": ["linear", "hold", "bezier", "ease_in", "ease_out"], "default": "bezier" },
        "ease": {
          "type": "object",
          "properties": {
            "in": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "number" } },
            "out": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "number" } }
          }
        }
      }
    },

    "transition": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "required": ["id", "type", "dur_us"],
          "properties": {
            "id": { "$ref": "#/$defs/id" },
            "type": { "type": "string" },
            "dur_us": { "type": "integer", "minimum": 0 },
            "params": { "type": "object" },
            "align": { "enum": ["center", "start", "end"], "default": "center" }
          }
        }
      ]
    },

    "text": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "required": ["kind", "content"],
          "properties": {
            "kind": { "enum": ["text", "subtitle", "sticker", "lyric"] },
            "content": { "type": "string" },
            "rich": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["range"],
                "properties": {
                  "range": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "integer", "minimum": 0 } },
                  "bold": { "type": "boolean" },
                  "italic": { "type": "boolean" },
                  "underline": { "type": "boolean" },
                  "size": { "type": "number", "exclusiveMinimum": 0 },
                  "fill": { "$ref": "#/$defs/color4" },
                  "stroke": {
                    "type": "object",
                    "properties": {
                      "color": { "$ref": "#/$defs/color4" },
                      "width": { "type": "number", "minimum": 0 }
                    }
                  }
                }
              }
            },
            "box": {
              "type": "object",
              "properties": {
                "w": { "type": "number", "minimum": 0, "maximum": 1 },
                "h": { "type": ["number", "null"] },
                "align": { "enum": ["left", "center", "right"] },
                "valign": { "enum": ["top", "middle", "bottom"] },
                "max_lines": { "type": "integer", "minimum": 1 }
              }
            },
            "font": {
              "type": "object",
              "properties": {
                "family": { "type": "string" },
                "path": { "type": ["string", "null"] },
                "fallback": { "type": "array", "items": { "type": "string" } }
              }
            },
            "spacing": {
              "type": "object",
              "properties": {
                "letter": { "type": "number" },
                "line": { "type": "number" }
              }
            },
            "animation": {
              "type": "object",
              "properties": {
                "in": {
                  "oneOf": [
                    { "type": "null" },
                    {
                      "type": "object",
                      "properties": {
                        "preset": { "type": "string" },
                        "dur_us": { "$ref": "#/$defs/us" }
                      }
                    }
                  ]
                },
                "out": {
                  "oneOf": [
                    { "type": "null" },
                    {
                      "type": "object",
                      "properties": {
                        "preset": { "type": "string" },
                        "dur_us": { "$ref": "#/$defs/us" }
                      }
                    }
                  ]
                }
              }
            }
          }
        }
      ]
    },

    "ai": {
      "type": "object",
      "properties": {
        "runs": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "agent", "goal", "status"],
            "properties": {
              "id": { "$ref": "#/$defs/id" },
              "agent": { "enum": ["director", "editor", "critic", "external"] },
              "model": {
                "type": "object",
                "properties": {
                  "route": { "type": "string" },
                  "provider": { "type": "string" },
                  "tokens_in": { "type": "integer", "minimum": 0 },
                  "tokens_out": { "type": "integer", "minimum": 0 }
                }
              },
              "goal": { "type": "string" },
              "contract": { "type": "object" },
              "steps": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["seq", "tool"],
                  "properties": {
                    "seq": { "type": "integer", "minimum": 1 },
                    "tool": { "type": "string" },
                    "input_ref": { "type": "string" },
                    "output_ref": { "type": "string" },
                    "ms": { "type": "integer", "minimum": 0 }
                  }
                }
              },
              "decisions": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["id", "action", "rationale"],
                  "properties": {
                    "id": { "$ref": "#/$defs/id" },
                    "action": { "enum": ["cut", "trim", "reorder", "add_effect", "add_text", "add_audio", "adjust", "recolor", "other"] },
                    "target_ref": { "type": "string" },
                    "rationale": { "type": "string" },
                    "evidence": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "required": ["kind", "ref"],
                        "properties": {
                          "kind": { "enum": ["transcript", "shot", "frame", "waveform", "user_request", "script", "structure", "render"] },
                          "ref": { "type": "string" },
                          "range_us": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "number" } }
                        }
                      }
                    },
                    "before_ref": { "type": "string" },
                    "after_ref": { "type": "string" },
                    "accepted": { "type": ["boolean", "null"] },
                    "applied_tx": { "type": "string" }
                  }
                }
              },
              "status": { "enum": ["planned", "previewed", "applied", "rejected", "failed"] }
            }
          }
        }
      }
    },

    "history": {
      "type": "object",
      "properties": {
        "cursor": { "type": "integer", "minimum": 0 },
        "events": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["seq", "actor", "cmd"],
            "properties": {
              "seq": { "type": "integer", "minimum": 0 },
              "ts_us": { "$ref": "#/$defs/us" },
              "actor": { "enum": ["user", "agent", "system"] },
              "cmd": { "type": "string" },
              "target": { "type": "string" },
              "args": { "type": "object" },
              "tx": { "type": "string" },
              "run": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```


---

## 附录 B　最小工程样例（已通过 schema 校验）

> 校验命令：`python _tools/validate_sample.py`，结果 PASS。

```json
{
  "schema_version": "1.0.0",
  "min_reader": "1.0.0",
  "id": "prj_01HZX0000000000000000000A",
  "name": "demo",
  "created_us": 1795000000000000,
  "updated_us": 1795000000000000,
  "generator": {
    "app": "AI Video Studio",
    "version": "0.1.0"
  },
  "settings": {
    "default_sequence_id": "sq_main",
    "ai": {
      "max_batch_clips": 3
    }
  },
  "media": [
    {
      "id": "md_01",
      "kind": "video",
      "uri": "file:///D:/a.mp4",
      "probe": {
        "width": 1920,
        "height": 1080,
        "fps": {
          "num": 30,
          "den": 1,
          "drop_frame": false
        },
        "dur_us": 6000000
      }
    }
  ],
  "sequences": [
    {
      "id": "sq_main",
      "name": "主序列",
      "canvas": {
        "width": 1080,
        "height": 1920,
        "ratio": "9:16",
        "background": [
          0,
          0,
          0,
          1
        ]
      },
      "fps": {
        "num": 30,
        "den": 1,
        "drop_frame": false
      },
      "sample_rate": 48000,
      "channels": 2,
      "dur_us": 6000000,
      "tracks": [
        {
          "id": "tr_v1",
          "kind": "video",
          "role": "main",
          "index": 0,
          "clips": [
            {
              "id": "cl_01",
              "media_id": "md_01",
              "seq_start_us": 0,
              "seq_dur_us": 6000000,
              "src_in_us": 0,
              "src_dur_us": 6000000,
              "speed": 1.0,
              "transform": {
                "layout": "fill",
                "x": 0,
                "y": 0,
                "scale": [
                  1.0,
                  1.0
                ],
                "rotation_deg": 0,
                "opacity": 1.0
              },
              "effects": [],
              "keyframes": []
            }
          ]
        }
      ]
    }
  ],
  "effects_lib": [],
  "ai": {
    "runs": []
  },
  "history": {
    "cursor": 0,
    "events": []
  }
}
```
