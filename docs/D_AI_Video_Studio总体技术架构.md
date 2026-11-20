# D AI Video Studio 总体技术架构

目标：一个以 Agent 为核心的专业视频工作站。人能用可视化时间轴精修，Agent 能自主剪完整条片子，外部 Agent（Codex / Claude / 任何支持 MCP 的客户端）能把它当工具使。

本文件定 12 层、5 个进程、6 类线程、4 条数据通路，以及每条关键接口的签名。落地顺序见 G 文档，选型理由见 F 文档，格式细节见 E 文档。

---

## 1. 五进程模型（先定边界，再谈代码）

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

## 2. 线程模型（6 类，每类的规则写死）

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

## 3. 12 层架构与每层接口卡

### L1 桌面壳与 UI

```
职责   主窗、时间轴控件、属性面板、媒体箱、WebView 插件面板
技术   Qt 6.8（Widgets 主窗 + Quick 面板混编）；WebView2 走 QtWebEngine 或原生 WebView2 控件
接口   IMainWindow / ITimelineView / IPropertyPanel / IPluginHost
关键点 时间轴控件用 QWidget + QOpenGLWidget 自绘，不用 QML 列表（QML 在十万级 item 场景会掉帧）
```

### L2 媒体抽象

```
职责   解码器注册、时间基换算、色彩管线、代理生成、帧缓存
技术   FFmpeg 8.x/9.x libav* 直连（不走命令行）
接口   IMediaSource::open(path) / IMediaDecoder::decode(frameIdx) / IColorPipeline::convert(src,dst)
       IProxyManager::ensure(mediaId, quality) / IFrameCache::get(key) / IFrameCache::put(key, frame)
硬指标 4K H.265 单路解码 > 100fps（多核 + 硬解）；seek 到任意帧 < 30ms（预解关键帧 + 双向解码）
```

### L3 工程存储

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

### L4 时间轴数据模型（自研核心）

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

### L5 预览与播放

```
职责   FrameServer、预览缓存、音频时钟、播放控制
技术   自研 FrameServer + GPU 纹理池 + LRU 帧缓存
接口   IFrameServer::request(seqId, frameIdx, quality, priority) -> GpuFrame
       IPlaybackClock（音频驱动）/ IPreviewCache::prefetch(range)
硬指标 1080p 代理 60fps 不掉帧；4K 原始素材 30fps；seek 后首帧 < 60ms
```

### L6 渲染与导出

```
职责   合成图求值、分段并行编码、硬件编码、封装、多机分片
技术   FFmpeg libavfilter 自建图 + 自研 GPU 合成 + NVENC/QSV/AMF
接口   IRenderJob::submit(spec) -> jobId / status(jobId) / cancel(jobId)
       IEncoderFactory（按 codec + 硬件能力选实现）
规则   分段并行：按 GOP 边界切片，多 worker 各渲一段，最后 `-c copy` 拼接
       导出与预览共用同一套合成图求值代码（唯一差别是质量档与是否回读）
```

分段并行是这套架构的性能命门：**导出 4K 长片的时间 ≈ 单片时长 / worker 数**，前提是切点落在关键帧且音频单独成轨拼接（见 G 文档阶段 2 验收标准）。

### L7 音频引擎

```
职责   多轨混音、增益/包络、降噪、变速、人声分离、响度归一
技术   JUCE 做宿主与 VST3 加载（进程外托管）；Rubber Band 做变速；DeepFilterNet/RNNoise 降噪；Demucs 分离
接口   IAudioGraph::build(seqId) -> IAudioNode 树 / IAudioGraph::render(range) -> AudioBuffer
       IVstHost::scan() / load(pluginPath) / setParam(id, value)
硬规则 实时线程零分配；所有模型推理在 AI 进程侧链完成，结果以 PCM 或参数回传
```

### L8 特效与节点系统

```
职责   节点图、效果求值、OpenFX 插件宿主、表达式 DSL
技术   自研轻节点图（DAG，非 Fusion 那种全功能）+ OpenFX 1.4/1.5 宿主 + WGSL 计算着色器
接口   INodeGraph::addNode(type) / connect(a,b,slot) / evaluate(node, frameCtx) -> GpuFrame
       IOfxHost::scan(pluginDir) / instantiate(pluginId) / render(instance, ctx)
       IExpr::compile(expr) -> Program（白名单函数，无 IO，无网络）
节点类型  source / transform / color / blur / keyer / merge / text / time / output（8 类起步）
边界   第一年只做 8 类 40 个节点；OpenFX 插件直接白拿几百个现成效果
```

### L9 视频理解

```
职责   转写、说话人、镜头切分、画面事实、语义检索、向量索引
技术   方案见 F 文档：ASR 用 faster-whisper/WhisperX；说话人 pyannote；镜头切分 PySceneDetect；
       分割 SAM2；检测/跟踪 YOLO(注意协议)或 RT-DETR + ByteTrack；VLM 走 MAGPIE 远端
接口   IAnalyzer::run(mediaId, tasks[]) -> AnalysisResult
       AnalysisResult{ transcript[], speakers[], shots[], frames[], embeddings[], objects[] }
       ISearch::index(projectId) / query(projectId, text|vector, k)
存储   结果写 media_derived + 向量表（sqlite-vec 或独立 FAISS 索引文件）
```

### L10 内部 Agent

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

### L11 模型网关

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

### L12 MCP 接口层

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

`timeline.apply` 的入参就是 E 文档定义的 XML 改动程序（受控 DSL），**不是自由 JSON patch**。理由：模型写错 XML 结构会被 schema 拦住，写错自由 path 会静默改坏工程。

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

## 4. 四条数据通路

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

## 5. 工程上下文管理（Agent 的内存怎么建）

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

## 6. 可观测性与失败恢复

| 项 | 做法 |
| --- | --- |
| 崩溃隔离 | 五个进程各自看门狗；media/render 挂了自动重启并从当前帧续解/续渲 |
| 断点续跑 | 每个 AI 任务有步骤账本（step 表 + 输入哈希 + 输出 blob），重跑只补缺失步骤 |
| 长任务可续 | MCP 侧 `progressToken` 全生命周期有效；客户端断了用 `tools/get` 查状态 |
| 审计 | 每条命令写 event_log；每条 AI 改动写 ai_decision；两者用 `tx_id` 关联 |
| 性能埋点 | 帧耗时、缓存命中率、解码等待、GPU 占用、模型延迟，按 runId 聚合 |

---

## 7. 性能预算（第一年必须打到的数）

| 场景 | 目标 | 判定方式 |
| --- | --- | --- |
| 1080p 30fps 代理 + 3 轨叠加 + 字幕 | 60fps 预览不掉帧 | 播放 60 秒无 dropped frame 计数增长 |
| 4K 原始素材单轨 | 30fps 预览 | 同上 |
| seek 任意位置 | 首帧 < 60ms | 100 次随机 seek 的 P95 |
| 导出 4K 60s / H.265 硬编 | < 90 秒（8 worker） | 实际跑 3 次取均值 |
| 3 小时素材全量转写 | < 12 分钟（GPU） | faster-whisper large-v3 + batching |
| 长视频规划（200 镜） | 单次 Agent 调用 < 40 秒 | 端到端计时 |

---

## 8. 这张架构图跟三家的对应关系

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