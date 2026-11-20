# F 最终技术选型报告

规则：每个模块只给四种判定之一——**用现成 / 借代码（fork 或摘模块）/ 调 SDK / 自研**，另加一个缓做标记。不出现「视情况」这种话。协议一律写全称，GPL 系一律进程外隔离。

判定依据三条：① 这层是否决定产品差异（决定的必须自研） ② 开源协议的传染性 ③ 三年后还维护得动的成本。

---

## 1. 一页速览

| # | 模块 | 判定 | 选择 | 协议 | 上它的阶段 |
| --- | --- | --- | --- | --- | --- |
| 1 | 桌面壳 | 用现成 | Qt 6.8（Widgets + Quick 混编） | LGPL-3.0（动态链接） | 1 |
| 2 | 时间轴控件 | 自研 | QWidget + QOpenGLWidget 自绘 | — | 2 |
| 3 | 媒体解码 | 用现成 | FFmpeg libav* 直连（libavcodec/libavformat/libswscale/libswresample） | LGPL-2.1（禁用 `--enable-gpl`） | 1 |
| 4 | 编码与封装 | 用现成 | FFmpeg + NVENC/QSV/AMF | 同上 + 各家 SDK | 2 |
| 5 | 时间轴数据模型 | **自研** | C++20，纯值语义，可单测 | — | 1 |
| 6 | 工程存储 | 用现成 | SQLite 3（WAL） | Public Domain | 1 |
| 7 | 工程格式 | **自研** | AVS（E 文档） | 自有 | 1 |
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

## 2. 逐模块判定与理由

### 2.1 桌面壳：Qt 6.8（用现成）

**定 Qt 而非 Electron/Tauri。** 三条硬理由：
1. 时间轴要在 60fps 下重绘十万级图元，Qt 的 QWidget 自绘 + QOpenGLWidget 有明确的可控路径；Chromium 那层合成多一次上下文切换。
2. 要接 GPU 纹理、要低延迟预览、要硬件解码零拷贝，原生窗口系统接口是底线。
3. 三家专业软件全走 Qt（剪映 Qt6、达芬奇 Qt5），插件与工控生态成熟。

协议处理：动态链接 LGPL-3.0，不改 Qt 源码，不静态链接，提供 Qt 源码获取方式。**避开 GPL-only 模块**（Qt Quick 3D、Quick Timeline、HTTP Server、gRPC、MQTT、Virtual Keyboard、Wayland Compositor、Graphs 等 14 项），这些只用自研或替代。

### 2.2 时间轴控件：自研

控件是产品的脸，也是性能瓶颈所在。现成方案（Qt 的 QGraphicsView、QML ListView）在「十万 item + 亚像素缩放 + 多轨对齐吸附」这个量级都会掉出 60fps。自绘 + 分层缓存（背景栅格 / 片段块 / 关键帧点 / 播放头 / 覆盖层）是唯一可控的做法。

### 2.3 解码：FFmpeg libav* 直连（用现成）

**不走 ffmpeg.exe 命令行。** 命令行每帧一次管道拷贝、参数靠字符串拼，精确 seek 与逐帧控制都要绕。直连 libavcodec 能拿到：
- 精确帧定位（`av_seek_frame` + 双向解码到目标帧）；
- 硬解零拷贝（D3D11VA 纹理直接给渲染器）；
- 每源独立 `AVCodecContext`，多线程安全边界清晰；
- 色彩元数据（primaries/transfer/matrix/range）直读直用。

协议纪律：**编译期不加 `--enable-gpl`**，保持 LGPL-2.1；不链 x264（GPL），H.264 编码走硬件（NVENC/QSV/AMF）或 OpenH264。要 x265 时走命令行子进程（GPL 隔离）。

### 2.4 编码与封装：FFmpeg + 三家硬件编码（用现成）

NVENC / QSV(libmfx 或 oneVPL) / AMF 三条通路覆盖 N/A/I 三厂。选实现策略：优先硬件 → 退软件 x264（进程外）→ 退 OpenH264。封装（MP4/MOV/MKV/MXF）用 libavformat 的 muxer，`-c copy` 分段拼接靠它。

### 2.5 时间轴数据模型：自研（核心）

这是差异化的第一层，没有备选。要求写死：
- 纯 C++20，无第三方依赖，可独立单测（模型层不链 Qt）；
- 值语义 + 不可变快照（改一次产生新版本，UI 侧比较句柄）；
- 命令总线（D 文档 L4），命令可校验、可反转、可序列化进 event_log；
- 所有时间 int64 微秒，帧率有理数。

为什么不用 MLT 或 OTIO 做内核：MLT 的模型是「producer/playlist/tractor」三件套，服务的是播放管线，表达不了「主轨连续 + 副轨相对对齐 + 嵌套序列 + AI 决策留痕」；OTIO 是交换格式，没有编辑语义（没有命令、没有撤销、没有不变量）。两者都做**外部适配器**，不做内核。

### 2.6 工程存储：SQLite（用现成）+ 内容寻址 blob

SQLite 的确定性优势：单文件、WAL 并发读、事务、崩溃安全、全平台一致、随应用分发（Public Domain）。工程库用 SQLite，大块数据用 sha256 命名的分桶文件。不用 LevelDB/RocksDB（无 SQL、工具链弱），不用自有二进制（调试成本高）。

### 2.7 工程格式：自研 AVS（E 文档）

明文 JSON 主存 + XML 视图 + ZIP 包发布。三条硬要求：规范化后字节稳定、`json→xml→json` 往返一致、事件日志可重放。这层是产品护城河（可 diff、可审、可回放），不做妥协。

### 2.8 合成与节点图：自研

自研范围：8 类节点（source/transform/color/blur/keyer/merge/text/time/output）、GPU 执行、关键帧求值、缓存句柄。不做 Fusion 那种全功能节点图（成本不可控），靠 OFX 补效果数量。

为什么不直接嵌 Natron（GPL）或 Fusion（闭源）：协议与体积都不成立；Natron 的节点引擎与其 UI 强耦合，摘出来比自己写贵。

### 2.9 特效宿主：OpenFX（调 SDK）

OFX 1.4/1.5 是最划算的生态入口：写一次宿主，能直接吃 Resolve/Natron/Nuke 生态的插件。1.5 新增 Metal/CUDA/OpenCL 渲染与 `OfxDrawSuite`，向后兼容无 deprecation。

宿主要做的四件事：扫描目录 → 解析 bundle 的 `Info.plist`/XML → 建 `OfxHost` 回调表（进度、时间、内存、多线程、属性）→ 走 `describe/render`。第一版只支持 `eContextFilter` 与 `eContextTransition` 两种上下文。

### 2.10 色彩管理：OpenColorIO 2.6 + ACES 2.0（用现成）

理由：ACES 2.0 的官方 config 就是 OCIO 格式，行业一致；GPU 侧走 `GpuShaderCreator` 产着色文本注入自家管线，跟达芬奇、AE 的做法一致。自研色彩管理在今天没有收益，只有坑。

### 2.11 音频宿主：JUCE（借代码，协议先定死）

JUCE 能一次给齐：音频设备、VST3/AU 加载、DSP 模块、时间拉伸接口。协议两条路：
- **AGPL-3.0 轨**：开源整个应用（不现实）。
- **商业轨**：按营收分档付费（Starter 免费档有营收上限，Indie / Pro 是按用户月费制）。

第一版走商业轨的 Indie 档，并在预算里写死。备选：PortAudio（MIT 式）+ 自研 VST3 宿主（用 Steinberg 的 VST3 SDK，GPL-3.0 或 Steinberg 双协议），成本高 3 倍，作退路。

### 2.12 变速不变调：Rubber Band（首选）/ SoundTouch（兜底）

Rubber Band 质量好、支持实时与非实时两套模式，GPL-2.0 → **进程外**：放 `audiofx.exe`，通过共享内存传 PCM，主程序不受传染。轻量档用 SoundTouch（LGPL-2.1，可直接链）。

### 2.13 降噪：DeepFilterNet3 + RNNoise

端侧实时降噪两档：DeepFilterNet3（MIT/Apache-2.0 双协议，质量高，CPU 可跑）做默认；RNNoise（BSD-3，模型 120KB 级）做低端机与实时通话档。剪映用的就是 RNNoise v2 这类轻量模型，路径验证过。

### 2.14 人声分离：Demucs v4（用现成）

MIT 协议，htdemucs 四轨分离质量在开源里第一梯队。推理放 AI 进程（GPU），结果以 PCM 存 blob。商用替代：MVSEP 类服务（走 API）——第一版不做，端侧够用。

### 2.15 ASR：faster-whisper（GPU）+ whisper.cpp（CPU）

- GPU 路径：faster-whisper large-v3 + batching，3 小时素材在 12 分钟内可转完（D 文档性能预算）。
- CPU 兜底：whisper.cpp（量化模型），保证没有独显的机器也能用。
- 中文场景补 FunASR/Paraformer（MIT）作为可选后端：它对中文标点与口语更友好。

### 2.16 词级对齐与说话人：WhisperX + pyannote

WhisperX 给词级时间戳（forced alignment），pyannote.audio 给说话人分段（diarization）。两者都 MIT，组合是社区标准做法。落地形态：一次推理出 `transcript + words[] + speakers[]`，写进 `media.derived`。

### 2.17 镜头切分：PySceneDetect（用现成）

内容感知检测（HSV 差异 + 自适应阈值）就够用，再加一路自研的音频能量突变检测做交叉验证（画面没切但声音断了，也算一个语义切点）。输出 `shots[]` 带 `source_range`。

### 2.18 分割与抠像：SAM 2 + 人像抠像模型

- 通用可提示分割：SAM 2（Apache-2.0）——点/框提示给 mask，做「选中这个人」「去掉这个物体」。
- 人像视频抠像：**BiRefNet（MIT）为主路**。RVM（Robust Video Matting）实测是 **GPL-3.0**，与闭源宿主冲突，只能走进程外或干脆不用——这条是 C 文档逐仓库核协议时抓出来的修正。
- 绿幕：自研色度键（成本极低，比模型快一个量级，且可控）。

### 2.19 检测与跟踪：RT-DETR / YOLOX + ByteTrack（借代码，避开 AGPL）

**这条是协议红线**：Ultralytics 的 YOLOv8/v11 是 AGPL-3.0，商用闭源要么买商业授权要么整个应用开源。选 Apache-2.0 的 RT-DETR 或 YOLOX + MIT 的 ByteTrack，功能差距在追平。

### 2.20 视频理解：远端 VLM 为主 + 端侧打底

3 小时素材塞不进任何模型的上下文。策略：镜头切分 + 抽关键帧 → 每镜一帧喂 VLM 打标（人物/场景/动作/情绪/可用性），得到结构化标签；叙事级判断交给强模型读「标签化摘要」。端侧跑轻量 CLIP 类做检索向量（剪映也是这条路：`chinese-clip-vit-base-patch16`）。

### 2.21 Agent 框架：自研

不套 LangChain/AutoGen 这类通用编排：我们要的是「受限工具集 + 强事务 + 强留痕」，通用框架的自由度反而是负担。自研范围：RunContext、工具注册表（带 scope）、步骤账本、失败分类与重试策略、配额与预算控制。

### 2.22 模型网关：MAGPIE（用现成）

`yetone/magpie` 是 MIT 的本地网关（Go + Wails），监听本地 `3425` 端口，`/v1` 前缀，能双向翻译 OpenAI Chat / OpenAI Responses / Anthropic Messages / Gemini 四套协议（流式与工具调用一起翻），路由组做组内多供应商顺位切换，账号级额度耗尽自动换同厂下一账号。

我们只加三样东西（不动它的协议层）：上下文预算器、任务路由表、计量账本。

### 2.23 MCP 服务端：协议自研 + 官方 SDK 只用于工具脚本侧

- spec 2026-07-28，传输只有 stdio 与 Streamable HTTP，原语 Tools/Resources/Prompts + 客户端 Sampling/Elicitation/Roots，鉴权走 OAuth 式流程（含动态注册与 step-up authorization）。
- **官方 Python SDK（v2.3.0）与 TypeScript SDK（v2.4.0）都验证为 MIT 且可用**；C++ 侧没有可依赖的官方 SDK（该仓库路径三轮回退仍 404/连接中断，记为未核实）。结论：`mcp.exe` 的 JSON-RPC 层自研（协议很薄：帧头 + JSON + 会话表），Python 侧脚本工具直接用官方 SDK。
- 长任务用 `_meta.progressToken` + `notifications/progress`（progress 必须单调递增，total 可为浮点）。
- 工具名限 `A-Za-z0-9_-.`，1–128 字符——我们的命名 `analyze.transcribe` 符合这套规范。

### 2.24 插件面板：WebView2（用现成）

Windows 自带，不需要分发 Chromium（省 200MB）。面板协议照达芬奇 Workflow Integration 的三件套：manifest（id/name/version/entry）+ preload（受限 API）+ 原生桥（C++ 暴露 QWebChannel 或自定义消息）。

### 2.25 打包与更新：WiX + 自研增量

MSI 用 WiX（MS-RL），更新做增量（按文件块差分，参考 courgette 思路，剪映自己也带 `courgette64.exe`）。第一版只做全量更新 + 校验，增量放阶段 5。

### 2.26 崩溃上报：Crashpad（借代码）

fork 一份 Crashpad（Apache-2.0），五个进程都挂 handler，符号走自建符号服务器。

### 2.27 测试与 CI：GoogleTest + pytest + Actions 自托管

模型层与命令层用 GoogleTest（BSD-3）；AI 侧用 pytest（MIT）；CI 必须跑三条门禁：schema 校验、`json→xml→json` 往返、事件重放一致性（E 文档第 11 节）。

### 2.28 对外交换：OpenTimelineIO（用现成）

OTIO Apache-2.0，C++ 核 + Python 适配器。我们做双向：AVS → OTIO（对外），OTIO → AVS（导入别人的时间轴）。达芬奇自己把 OTIO 当一等导出格式，这是行业通用货币。

### 2.29 MLT：缓做

只在「导入 Shotcut/Kdenlive 工程」这个需求真的来了再接。MLT 的 XML 是它 API 结构的直映射，解析成本不低，收益单一。

### 2.30 Blender 无头渲染：缓做

Blender 是 GPL-3.0，只能进程外。价值在于 3D 图层与体积特效，属于阶段 7 的加分项，不做地基。

---

## 3. 三条协议红线（写进代码评审清单）

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

## 4. 三年成本权衡（为什么这么定）

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

## 5. 一句话总结

**能借生态的全借（FFmpeg / OCIO / OFX / OTIO / MAGPIE / MCP / SAM2 / Whisper 系），决定产品差异的三层全自研（时间轴模型 / 工程格式 / Agent 与事务）**。其余按协议红线做进程隔离，一分别省错地方。