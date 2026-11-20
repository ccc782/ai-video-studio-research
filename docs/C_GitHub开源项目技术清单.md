# C GitHub 开源项目技术清单

> 工程目录：`C:\AI Video Studio工程参考`
> 采集时间：2026-11-20（时区 +08:00）
> 基线：`00_研究路线与技术地图.md` 的 12 层技术地图 · `F_技术选型报告.md` 的四种判定 · `G_开发路线图.md` 的七阶段
> 覆盖项目：83 个，分 10 组（其中 2 个因仓库路径拿不到，star 与版本标「未核实」，另有 5 个缺 Release 语义只标 star 与提交时间）

---

## 0. 数据口径（先看这段，后面所有数字都按这套读）

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

## 1. 媒体解码编码

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

## 2. 时间轴与工程交换

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
| MLT | 能 | C API（`mlt/framework/mlt.h`）+ C++ 包装 `src/mlt++/` | `src/framework/`（`mlt_producer.c`、`mlt_playlist.c`、`mlt_tractor.c`、`mlt_transition.c`、`mlt_filter.c`）、`src/modules/avformat/`、`src/modules/qt/` | 动态库（LGPL 纪律） | `producer/playlist/tractor` 三件套绑死播放管线，与我们的命令总线语义冲突；拿它当内核，每加一个 AI 能力都要跟它的模型打架（F 文档已判缓做） |
| pyJianYingDraft | 只做参考 | 无 | `draft_content.json` 字段构造器（28 个顶层字段、46 类 materials、时间单位微秒）、`_src_script_file` 对应的 `ScriptFile`、`Track`、`TextSegment`、关键帧、蒙版、色度抠图参数、转场表 | 不集成，抄语义 | Python 侧、不渲染、靠剪映客户端出片；格式随剪映版本漂移（README 自标「10.8 ✅」） |
| pyCapCut | 只做参考 | 无 | 同源分支，CapCut 草稿字段 | 不集成 | 无协议文件可读，代码只当字段字典 |
| pyaaf | 只做参考 | 无 | `aaf2/` 对象模型（Mob / Slot / Component / TimelineMobSlot / OperationGroup） | 不集成 | 2017 年后停更；读能用，写复杂 AAF 会缺结构 |

**本轮结论**：这一组只上 OTIO。

- **OpenTimelineIO**（阶段 2 起做适配器骨架，阶段 7 全量）：FCPXML / AAF / EDL 三个适配器是白送的，`AVS ↔ OTIO` 双向映射写一次就同时解决「导出给别人」与「导入别人的时间轴」，G 文档阶段 7 的六格式往返验收直接靠它。

剪映草稿这一路只抄字段语义、不抄一行代码——那份 `draft_content.json` 的字段设计研究价值远高于代码价值。

---

## 3. 合成 / 特效 / 插件标准

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
- **imgui-node-editor**（阶段 5）：节点画布、连线、框选、缩放这些交互是纯体力活，借它省两周；求值仍走自研 WGSL，G 文档阶段 5「20 节点级联 4K 单帧 < 120ms」的账算在自己手里。

tinyexpr 留作表达式引擎的词法层，包一层变量表就能用，成本一个下午，不占位置。

---

## 4. 色彩管理

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

达芬奇的色彩管线和它是同一套 config，跟行业对齐这件事不用讨论；`GpuShaderCreator` 吐着色文本注入自家管线，正好落 G 文档阶段 2 的「像素差 < 1/255」验收。colour-science 只当常量表来源，aces-dev 只提供 CTL 原件用来烘 LUT。

---

## 5. 音频

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
| JUCE | 能 | 无（本身是 C++ 框架） | `modules/juce_audio_devices/`（WASAPI / ASIO）、`modules/juce_audio_processors/`（VST3/AU 宿主）、`modules/juce_audio_formats/`、`modules/juce_dsp/`、`modules/juce_gui_basics/` | 静态库进 `audiofx.exe` | AGPL-3.0 会把整个应用拽成 AGPL；商业轨按营收/人头收费；拿它就得在「开源全应用」与「买授权」之间选一个（F 文档已定买 Indie 轨，或退到自研宿主） |
| RNNoise | 能 | C API（`include/rnnoise.h`） | `src/denoise.c`、`src/rnn_data.c`、`models/rnnoise_v2.0.model` | 静态库 | 48kHz 单声道写死，其他采样率要重采样；模型 2024 年后没再更新 |
| Rubber Band | 能 | C API（`rubberband/rubberband-c.h`） | `src/RubberBandStretcher.cpp`（实时/离线两套 API）、`src/StretcherProcess.cpp` | 只能进程外（`audiofx.exe`） | GPL-2.0；实时模式音质低于离线模式；变速质量与延迟要按用途分档 |
| libsndfile | 能 | C API（`sndfile.h`） | `src/sndfile.c`、`src/wav.c`、`src/rf64.c`、`src/broadcast.c`（BWF 元数据） | 动态库（LGPL 纪律） | 只读写文件不做处理；WAV/BWF 之外容器覆盖一般 |
| miniaudio | 能 | C API（单头 `miniaudio.h`） | `miniaudio.h`（设备、混音、重采样、`ma_decoder`、`ma_engine`） | 单头直接编进工程 | 20 万行单文件，首次编译慢；ASIO 要额外编 `ma_backend_asio`；工程里放两份会重定义 |
| DeepFilterNet | 能（C ABI） | 无 | `libDF/src/`（Rust 推理核）、`libDF` 的 C ABI 导出层、`DeepFilterNet/`（torch 训练侧） | 进程外 `ai.exe` 或 Rust→C 静态库 | 2023 年 8 月后停更；Rust 工具链进构建链；模型按 48kHz 训的 |
| Demucs | 不嵌（Python） | 无 | `demucs/htdemucs.py`、`demucs/apply.py`、`demucs/separate.py` | 进程外（`ai.exe`）或导 ONNX | torch 依赖重；分离一首 3 分钟要 GPU 秒级，CPU 分钟级 |
| libebur128 | 能 | C API | `ebur128.c`（单文件：EBU R128 / ITU-R BS.1770 响度 + true peak） | 单文件编进工程 | 要吃 48k 双声道，喂之前得自己重采样；只有测量，没有归一化动作 |
| VST3 SDK | 能 | 无 | `public.sdk/source/vst/hosting/`（`moduleloader.cpp`、`hostclasses.cpp`、`connectionproxy.cpp`）、`pluginterfaces/vst/` | 静态库进 `audiofx.exe` | SDK 是 MIT，但分发 VST3 插件要 Steinberg 的 VST3 授权协议；Windows 上是 COM 生命周期，插件崩在宿主进程里就是整进程带走（所以进程外托管） |

**本轮结论**：这一组定两个，JUCE 那条改判。

- **miniaudio + VST3 SDK 的 hosting 层**（阶段 5）：设备枚举、WASAPI 共享/独占、混音与重采样一个单头解决；VST3 的 `moduleloader.cpp` 与 `hostclasses.cpp` 是现成的插件加载与宿主实现，fork 进 `audiofx.exe` 就绕开了 JUCE 的 AGPL 传染——G 文档阶段 5 的「故意崩溃 5 个插件，应用无感」这条验收也用它实现。
- **RNNoise 0.2 + libebur128**（阶段 4）：降噪与响度归一（-14 LUFS ±0.5、真峰 -1 dBTP）是阶段 4 音频自动链的两端，这两个都是单文件级成本。

JUCE 只在商业授权预算落定的前提下才进，否则 AGPL-3.0 会让整个 `studio.exe` 变成开源义务。

---

## 6. 字幕与语音

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

## 7. 视频理解与 AI

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
| Ultralytics | 不嵌 | 无 | `ultralytics/engine/`、`ultralytics/models/yolo/` | 只能进程外，或整条换掉 | AGPL-3.0，闭源产品里进不了链接侧（F 文档已划红线，换 RT-DETR / YOLOX） |
| ByteTrack | 不嵌 | 无 | `yolox/tracker/byte_tracker.py`、`matching.py` | 进程外 | 2021 年后的跟踪范式没跟进；作为 Kalman + 匈牙利匹配的参考实现仍然最省读 |
| BiRefNet | 不嵌 | 无 | `models/`（双参考分支网络）、推理脚本 | 进程外 | 单帧分割，视频上要自己加时序平滑 |
| Robust Video Matting | 不嵌 | 无 | `model/model.py`、`inference.py` | 进程外 | **协议是 GPL-3.0**，F 文档里按 Apache/MIT 记的那条要改（见第 11 节）；2021 年后停更 |
| Real-ESRGAN | 不嵌 | 无 | `realesrgan/archs/`、`inference_realesrgan.py` | 进程外 | 2022 年后停更；只超分单帧，不吃视频容器与音频 |
| diffusers | 不嵌 | 无 | `src/diffusers/pipelines/`、`schedulers/`、`models/` | 服务化进程外 | 生成式管线吃显存；只适合当外部服务 |
| ComfyUI | 不嵌 | 无 | `comfy/`（`nodes.py`、`samplers.py`）、`custom_nodes/` | 进程外 HTTP | GPL-3.0；节点生态自管版本，升级会炸工作流 |
| InsightFace | 不嵌 | 无 | `python-package/insightface/model_zoo/`（ArcFace、RetinaFace）、`app/face_analysis.py` | 进程外 | 根目录无协议文件可读，权重商用条款要单看；无 release 语义 |

**本轮结论**：这一组定两个，另外记一笔协议修正。

- **llama.cpp b12557**（阶段 4）：VLM 打标走 `tools/mtmd`，端侧就能把「人物 / 场景 / 动作 / 情绪 / 可用性」变成结构化标签，不必等云；阶段 4 的叙事级判断再交强模型读标签化摘要。
- **PySceneDetect v0.7.3**（阶段 3）：镜头切分是 Agent 的最小分析单元，`ContentDetector` 的输出直接变 `shots[]` 带 `source_range`，F 文档定的这条路没有更省事的替代。

协议修正记一笔：**RVM（RobustVideoMatting）是 GPL-3.0**，人像抠像这条只能走 BiRefNet（MIT）或自研色度键，F 文档 2.18 节里「RVM 或 BiRefNet 一类，Apache-2.0/MIT 系」的说法要按 BiRefNet 收口。

---

## 8. 桌面壳与 UI

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
| Qt Base | 能 | Python（PySide6，另有 PyQt） | `src/widgets/`、`src/quick/`、`src/gui/painting/`、`src/opengl/`、`src/plugins/platforms/windows/` | 动态库（LGPL-3.0 纪律：动态链 + 允许替换 Qt 库） | 静态链接要商业授权；Qt Quick 3D、Quick Timeline、HTTP Server、Virtual Keyboard、Graphs 等 14 项是 GPL-only，闭源产品里放不进去（F 文档 2.1 节已列） |
| CEF | 能 | C++ / C API | `include/cef_client.h`、`include/cef_browser.h`、`libcef/browser/`、`wrapper/cef_helpers.h` | 动态库 + 独立子进程 | 分发体积 ~150MB；browser / render / GPU 多进程吃内存；CEF 版本与 Chromium 版本锁死，升级是项目级动作 |
| Qt Advanced Docking System | 能 | 无 | `src/DockManager.cpp`、`src/DockWidget.cpp`、`src/FloatingDockContainer.cpp`、`src/DockAreaWidget.cpp` | 静态库（LGPL-2.1 动态纪律适用于命名的库） | 只管停靠布局与浮动，不做多窗口渲染同步；品牌定制要改源码 |
| Dear ImGui | 能 | 无 | `imgui.cpp`、`imgui_draw.cpp`、`imgui_widgets.cpp`、`backends/imgui_impl_dx11.cpp` | 静态库 | 立即模式，长列表与大表格要自己做虚拟化；中文 IME 要接 `ImmContext` |
| SDL3 | 能 | C API | `src/video/windows/`、`src/audio/wasapi/`、`src/events/` | 动态库 `SDL3.dll` | 只管窗口 / 输入 / 音频，不管控件 |
| GLFW | 能 | C API | `src/win32_window.c`、`src/wgl_context.c`、`src/monitor.c` | 静态库 | 同上；Win32 深接口（DPI、任务栏、JumpList）不在它的范围 |
| webview | 能 | C / C++ | `core/include/webview/webview.h`、`core/src/platform/windows/` | 静态库 + WebView2 | 依赖 WebView2 Runtime（Win10 1803+ 要装）；没有 CDP/DevTools 那种深度；2024 年后节奏放慢 |
| SQLite | 能 | C API | `src/sqlite3.c`（amalgamation）、`src/wal.c`、`src/btree.c` | 单文件编进 `projectd.exe` | 单写者模型，WAL 下并发读可以、并发写要排队；大 blob 进库会让 WAL 暴涨（F 文档已定 sha256 分桶存 blob） |
| Crashpad | 能 | C / C++ | `client/`（`crashpad_client_win.cc`）、`handler/`、`util/`、`minidump/` | 静态库，五个进程各挂一份 handler | 符号服务器要自建；minidump 不含显存与纹理，GPU 侧崩溃复现率有限 |

**本轮结论**：这一组定两个。

- **Qt 6.8 LTS 线**（阶段 1；仓库当前最新是 v6.11.3，产品锁 LTS 轨道）：LGPL-3.0 动态链接，避开 14 项 GPL-only 模块；时间轴要在 60fps 下重绘十万级图元，QWidget 自绘 + QOpenGLWidget 是可控路径，这一条 F 文档已经算过账。
- **Qt Advanced Docking System 5.1.1**（阶段 1）：媒体箱 / 监视器 / 属性 / 音频表的停靠与浮动是纯体力活，LGPL-2.1 能直接链。

CEF 留到阶段 5：插件面板第一版用 WebView2（系统组件，省 150MB），只有当「要跑剪映那种整页 Web 面板」的需求成立时才把 CEF 按独立进程引入。SQLite 与 Crashpad 属宿主基础件，跟着阶段 1 一次性接完。

---

## 9. Agent 与 MCP

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
| MAGPIE | 不嵌（独立服务） | 无 | `/v1` 路由、路由组（组内供应商顺位切换）、四套协议双向翻译、账号级额度切换 | 进程外，本地 `3425` 端口 | 只做翻译与路由，不管上下文预算与计量（F 文档 2.22 节：我们只加预算器、路由表、计量账本三样） |

**本轮结论**：这一组一条主路 + 一个参考。

- **自研 C++ MCP Server（stdio + Streamable HTTP，spec 2026-07-28）+ nlohmann/json 3.12.0**（阶段 6）：22 个工具要跟命令总线、事务边界、事件账本绑死，套 Python/TS SDK 只是多一层进程与一次序列化；报文层用 `json.hpp` 单头，分帧与 capability 协商照 `python-sdk` 的 `shared/session.py` 行为对齐。
- **MAGPIE**（阶段 3 起，其实写在 F 文档 2.22 节）：模型网关直接用现成的，我们只叠预算器、路由表、计量账本。

这里要改 F 文档一句话：2.23 节写的「官方 Python/TS SDK + 自研工具层」在 C++ 侧没有可用的官方实现（`modelcontextprotocol/cpp-sdk` 这条路本次没拿到），落地形态改为**全自研 + 对齐 spec 与 python-sdk 行为**。

---

## 10. 参考型应用（能抄架构的成品）

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

- **Natron 的 OFX 宿主实现**（服务阶段 5）：`Engine/OfxEffectInstance.cpp` 把参数求值、渲染上下文、多线程回调全走了一遍，是市面上唯一能逐行读的完整 OFX 宿主；G 文档阶段 5「接 3 个真实 OFX 插件、参数 UI 自动生成且可关键帧」这条验收，读完它少踩两周坑。
- **OBS 的 D3D11 图形层 + Kdenlive 的 timeline2 命令模型**（服务阶段 1-2）：前者给出纹理共享、GPU 同步、D3D11 设备丢失恢复的工程做法；后者给出「clip/track 模型 + 命令 undo」与 AI 改动留痕的接口形状。

Natron 的节点引擎与 UI 强耦合、Blender 的 depsgraph 过重，这两条 F 文档已经判过：摘出来比自己写贵。

---

## 11. 按协议分级的可用性

分四档。第一档是能直接闭源商用链接的；第二档是 LGPL，链接可以但要守纪律；第三档只能进程外隔离；第四档是参考实现，代码一行都不复制。

### 11.1 可直接闭源商用链接（MIT / Apache-2.0 / BSD-2 / BSD-3 / ISC / Zlib / Public Domain）

| 协议 | 项目 |
| --- | --- |
| MIT | BtbN/FFmpeg-Builds（脚本）、imgui-node-editor、tinyexpr（Zlib）、Dear ImGui、webview、nlohmann/json、libass（ISC）、VST3 SDK（SDK 本体）、oneVPL、RNNoise、libebur128、Demucs、whisper.cpp、openai/whisper、faster-whisper、pyannote.audio、FunASR、sherpa-onnx（Apache-2.0 见下）、ByteTrack、BiRefNet、llama.cpp、DirectML、Ollama、MAGPIE、Qt Advanced Docking System（LGPL 见 11.2）、Piper、pyaaf、Aegisub（BSD-3） |
| Apache-2.0 | OpenTimelineIO、OpenImageIO、OpenVINO、SAM 2、diffusers、ONNX 规范、FastMCP、Crashpad、pyJianYingDraft、MCP 规范 / Servers / C# SDK（迁移中）、aces-dev、sherpa-onnx、DeepFilterNet（双轨） |
| BSD-2-Clause | libavif、OpenH264 |
| BSD-3-Clause | libjxl、libwebp、OpenFX、OpenEXR、Skia、OpenColorIO、colour-science、WhisperX、PySceneDetect、Real-ESRGAN、CEF、Aegisub |
| ISC / Zlib / Public Domain | libass（ISC）、tinyexpr（Zlib）、SDL3（Zlib）、GLFW（Zlib）、miniaudio（Unlicense 或 MIT-0）、SQLite（Public Domain） |

一句话结论：这一档里 FFmpeg 之外的媒体与 AI 地基全是干净的，可以直接生成安装包。

### 11.2 LGPL 动态链接档（可以链，但要守三条纪律）

| 项目 | 协议 | 纪律 |
| --- | --- | --- |
| FFmpeg | LGPL-2.1-or-later | 动态链 `av*.dll`；编译期不加 `--enable-gpl`；提供协议文本与源码获取方式 |
| Qt Base | LGPL-3.0 | 动态链；不改 Qt 源码；允许用户替换 Qt 库；14 项 GPL-only 模块不碰 |
| libplacebo | LGPL-2.1 | 动态链；版本升级要重测着色器路径 |
| libsndfile | LGPL-2.1 | 动态链 |
| MLT Framework | LGPL-2.1 | 动态链（本文判缓做，只在导入 Shotcut/Kdenlive 工程时接） |
| Qt Advanced Docking System | LGPL-2.1 | 动态链或独立 DLL |

一句话结论：这一档要的是「链接方式」，不是「能否落地」，动态链 + 不改源码 + 提供替换途径三条做到，闭源分发成立。

### 11.3 只能进程外隔离（GPL-2.0 / GPL-3.0 / AGPL-3.0）

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
| Ultralytics | **AGPL-3.0** | 整条不用，换 RT-DETR / YOLOX（F 文档红线） |
| JUCE | **AGPL-3.0 / 商业双轨** | 只在买商业授权后链接；否则整应用开源 |

一句话结论：这一档的每一个都必须跨进程边界，且跨的方式要写进代码评审清单——`audiofx.exe`（Rubber Band）、`blender.exe`（3D 加分项）、外部 HTTP（ComfyUI）。

### 11.4 参考实现，代码不可复制

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

## 12. Top 12 必上项目

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

## 13. 未核实字段清单

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

另有一项判定性修正，不进上表但同样要落进 F 文档：**`PeterL1n/RobustVideoMatting` 的开源协议是 GPL-3.0**（本次核实），F 文档 2.18 节把它与 BiRefNet 一起写成「Apache-2.0/MIT 系」的说法要改成 BiRefNet 单走。