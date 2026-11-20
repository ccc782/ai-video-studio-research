# B 三大软件功能对照表

> 基线日期：2026-11-20
> 对象：剪映专业版 11.7.0.14652（本机隔离版实测）、DaVinci Resolve 21.2 build 6（本机隔离版实测）、After Effects 27.0（本机未装，走公开资料与随包文档线）
> 证据口径沿用 `00_研究路线与技术地图.md` 六档：`[实测]` / `[随包文档]` / `[开源代码]` / `[第三方]` / `[推断]` / `[未证实]`

> 规模：十组主表合计 **126 行**（① 13 / ② 13 / ③ 13 / ④ 13 / ⑤ 13 / ⑥ 10 / ⑦ 12 / ⑧ 11 / ⑨ 13 / ⑩ 15），每行 9 列。

## 读法

- 每行一个具体功能，9 列固定：功能 ｜ 剪映 11.7 ｜ 达芬奇 21.2 ｜ AE 27.0 ｜ 实现方式判定 ｜ 公开程度 ｜ 我们复用度 ｜ 开发难度 ｜ 技术来源。
- 「实现方式判定」写落点：CPU 算法 / GPU shader / AI 模型推理 / 云端 API / 参数化模板 / 脚本层实现，括注证据档。
- 「公开程度」四档：公开文档化 / 随包文档 / 需逆向 / 闭源黑盒。
- 「我们复用度」五档：直接抄设计 / 可借鉴 / 换成开源实现 / 自研 / 不做。
- 「开发难度」★ 到 ★★★★★，锚点：★★ ≈ 3 人月，★★★★★ ≈ 30 人月以上。
- 三家单元格里写机制，不写「有/无」两级判定；确实没有该项的实现时写它拿什么顶替。

---

## ① 工程与文件格式

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

## ② 时间轴与轨道

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

## ③ 剪辑操作

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

## ④ 画面变换与合成

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

## ⑤ 特效与插件

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

## ⑥ 字幕与文字

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

## ⑦ 音频

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

## ⑧ 调色与色彩管理

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

## ⑨ 渲染与导出

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

## ⑩ 自动化与 Agent

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

## 三家各自不可替代的三件事

### 剪映

1. **Lyra XMLDraft 协议：把工程当文档改，不当数据库改。** Selection Expression 先选节点，Mutation 八类（attr / removeAttr / appendXml / replaceWithXml / remove / empty / reorderChildrenById 等）再局部改 XML 片段，AI 只提交「选点 + 片段」，宿主负责重排时间轴。抄不来的点：这套协议和它的 200+ 原生命令表、undoRedo 域是三向绑定的，命令语义写在 `app-server.mjs` 里，光看 XML 学不到「改完怎么让内核重算」。
2. **微秒时间基 + 46 类扁平材质表。** 全工程一个 JSON，材质平铺，AI 一次读全、一次改准；微秒让帧率无关的剪辑（29.97 / 25 / 60 混剪）不用换算。抄不来的点：扁平表意味着所有跨对象引用靠 id 字符串，这是海量草稿喂出来的工程决策，改结构等于重写渲染与导出的对齐逻辑。
3. **端侧模型货架。** `models/` 46 个包约 240MB，配 onnxruntime(CUDA)、OpenVINO、高通 QNN(Hexagon NPU)、自研 ByteNN 四路后端，断网也能跑智能抠像、字幕识别、踩点。抄不来的点：四路后端的选择逻辑与模型量化版本是硬件厂联调出来的，换机型就换模型包。

### 达芬奇

1. **三层色彩管线：RCM + 节点级 CST + 随包 OCIO 2.5。** 工程级、片段级、节点级三层色彩变换可叠加，配 `SetLUT()` / `SetCDL()` 的 1-based 节点索引，脚本能精确点到某个节点的某个 LUT。抄不来的点：OCIO 2.5 + ACES 2.0 的配置集和它的 GPU 求值是逐像素对齐过的，配错了就是整条片子偏色。
2. **Fairlight FlexBus 与沉浸声链。** 子混 / 总线 / VCA / Link Group 四层路由，VST3 + AU + Fairlight FX 三套插件层，Atmos 走 RMU + re-render 预设，Bounce Mix to Track 一次过出多份交付。抄不来的点：48 轨以上的实时混音调度与 Dolby 授权件是两回事，前者是工程活，后者是商务活。
3. **工程即明文（`.drp` = zip + XML）+ 530 方法脚本 API。** 外部程序能整工程读写、能无头跑，`project.xml` 里连 `DbPrjVer` 与 `TimelineHandleVec` 都摆在明面上。抄不来的点：这套 XML 结构跟 Fusion 的 `CompositionBA` 压缩块、版本堆 `pLmVerTable` 咬合，缺一块就读不出工程。

### AE

1. **表达式引擎：每个属性都是可编程的。** JS 子集 + 时间/空间插值的双插值模型 + 逐属性重算，能做到「一个滑杆驱动 300 个图层的参数」。抄不来的点：表达式沙箱、增量重算、循环依赖检测三件事绑在一起，重写等于自研一个小 JS 运行时。
2. **效果栈 + 图层 + 预合成的自由度。** 任意深度嵌套、任意混合模式组合、蒙版与轨道遮罩交叉，没有「轨道类型」的限制。抄不来的点：自由度换来的是一次渲染要遍历的图很大，能扛住这个规模的缓存与调度才是本体。
3. **MOGRT + aerender 的工业化出货链。** 模板暴露控件、脚本灌值、`aerender` 批渲染，一条命令出几百条带参数的成片，配 `-s` / `-e` 帧段切分。抄不来的点：MOGRT 的控件 schema 与工程内部参数表的对应关系闭源，第三方只能靠脚本 `setValue` 反推。

---

## 三家都做得烂的三件事

### 1. 工程文件是给自家程序用的，不是给程序用的 API

- **现象**：剪映改完 draft 要重载工程才生效，`draft_patch` 还得走三段式；达芬奇 `.drp` 里 `FieldsBlob` 是私有 TLV，`CompositionBA` 是压缩 blob，外部程序只能整块搬运，局部改拿不到入口；AE 的 RIFX 干脆没有公开规范，第三方解析器全靠猜。三家的共同毛病是：**没有一个带 schema 的增量写入口**。
- **我们的做法**：AVS = SQLite 单库 + JSON/XML 双视图导出（抄达芬奇 `.drp` 的「明文可读 + 分片」形态），所有写入走 Command 总线，每条命令带 schema 版本与 pre/post 快照，AI 与 UI 走同一套写入路径；再配事件溯源，任意 revision 可回放。

### 2. AI 能力锁在云端或会员档里，且编排不了

- **现象**：剪映的智能成片、花字、音色走云，端侧只放抠像与识别；达芬奇的 `llama.dll` + `mtmd.dll` 只喂自己 UI，脚本层拿不到模型调用；AE 27.0 干脆没有 AI。三家里没有一家把模型暴露成可编排的工具。
- **我们的做法**：模型货架本地化（llama.cpp + ONNX Runtime + Vulkan Compute 三后端），统一 provider 抽象，模型调用与编辑命令一起注册进 MCP 工具表，外部 Agent 与内部 Editor Agent 用同一份工具描述。

### 3. 时间基与单位三家互不兼容，交换格式必然丢字段

- **现象**：剪映微秒、达芬奇帧、AE 秒；走 OTIO 或 FCPXML 一过，关键帧曲线类型、特效参数、蒙版形状这三类信息基本丢干净。达芬奇官方文档写「OTIO 比 AAF 与 XML 兼容性更好」，实测下来丢字段一样丢。
- **我们的做法**：内部统一 64 位 tick（1/1e6 秒，对齐剪映的微秒）+ 每个属性带 unit 元数据；导入导出走「逐字段映射 + 丢失清单」，转换完直接给用户一张「哪些字段没搬过去」的表，不做静默丢弃。

### 补两条（同一批坑里挖出来的）

4. **撤销与脚本层打架。** 达芬奇脚本没有 undo 分组，AE 脚本执行期间多数操作不入栈，剪映只有 UI 撤销。我们的做法：所有 API 默认在事务里，可 group、可 dry-run、可回滚到任意 revision，脚本跑一半失败能整组回退。
5. **预览管线和渲染管线是两条。** 三家都存在「显示的和导出的不一致」，尤其在色彩、字体、混合模式上。我们的做法：FrameServer 单一渲染路径，预览就是渲染的低分辨率分支，两边共用同一份节点求值结果。

---

## 复用优先级矩阵

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

## 附：`[未证实]` 行索引

本文标 `[未证实]` 的位置，共 5 处，对应主表行：

- ① 工程加密与混淆：剪映 draft 加密算法本身未拿到，只有社区的探测结论。
- ④ 表达式与程序化：剪映 Selection Expression 的完整语法未拿到，随包 skill 只覆盖常用子集。
- ⑤ 插件 ABI：剪映作为 OFX 宿主的实际加载路径未抓到运行时证据。
- ⑦ 变声与音色：剪映本地模型与云 API 的分界线未定。
- ⑩ 端侧模型：达芬奇 `llama.dll` 的调用方进程与调用链未抓到。