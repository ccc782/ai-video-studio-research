# A 三大软件逆向研究报告

对象：剪映专业版 11.7.0.14652 / DaVinci Resolve 21.2 build 6 / After Effects 27.0
方法：隔离环境静态结构测绘 + 随包开发者文档全读 + 真实工程文件字段级 dump + 关键 CLI 实跑
证据标记：`[实测]` `[随包文档]` `[开源代码]` `[第三方]` `[推断]` `[未证实]`

---

# 第一章 剪映专业版 11.7.0.14652

## 1.1 它到底是什么：四层结构，没有 Electron

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

## 1.2 GPU 与后端：真正干活的是 VECreator 家族

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

## 1.3 端侧 AI 货架：这是最值得抄的部分

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

## 1.4 草稿格式：`draft_content.json` 字段级

`[实测]` 真实工程样本：`剪映草稿_样本A\draft_content.json`，644KB，3 条轨道（video 95 段 / text 312 段 / text 1 段）。同目录另有两个文件：`draft_info.json`（644KB，内容与 draft_content 一致，是兼容别名）、`draft_meta_info.json`（1.4KB，草稿登记信息）。

### 1.4.1 顶层 28 字段

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
设计启示：**它把「AI 异步任务」直接挂进工程文件**（`*_taskinfo` + `*_recognition_id`），工程打开时能恢复未完成任务的上下文。我们抄这条，但要改成任务表 + 事件溯源（见 E 文档）。

### 1.4.2 片段结构（video 段实测原始值）

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

### 1.4.3 materials 46 类（实测类目全表）

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

### 1.4.4 文字段与文字素材

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

### 1.4.5 draft_meta_info.json

`[实测]` 只做草稿登记与云同步状态，全部平铺 30 个键：`draft_id / draft_name / draft_fold_path / draft_root_path / draft_cover / draft_materials[type 0,1,2,3,6,7,8] / draft_cloud_* / draft_enterprise_info / draft_is_ai_shorts / draft_is_ai_packaging_used / draft_is_ai_translate / tm_duration / tm_draft_cloud_modified`。
设计启示：**内容（content）与索引（meta）分离**，列表页只读 meta 就能渲染草稿墙，不用加载 644KB 正文。这条必须抄。

### 1.4.6 补充实测：草稿从 6.0 起上锁了（这条改结论）

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

对我们的直接影响（写进 E 文档的格式策略）：
1. **「明文工程」是产品决策，不是技术细节**。剪映上锁是为了堵第三方工具与防抄袭，代价是自己的文件不可 diff、不可审查、出问题只能靠 `.bak`。我们的 AVS 格式一律明文 + 规范化排序，diff 与审查是一等能力。
2. **读他人工程的适配器要认加密**。做「导入剪映草稿」功能时，明文草稿直接解析；密文稿需要用户在剪映里导出或降版本，或者走它自己的 `-open-draft-pack` 通道（见 1.7.0），不做密钥提取。
3. `attachment_editing.json` + `agent_adoption_ledger.db` 证明它**已经在记录 AI 采纳率**。我们的 `ai_decision` 表（D 文档 L3）要对齐这个思路并做厚：记录证据、候选、采纳与否。

### 1.4.7 官方命令行入口（比 CLI 更靠底层）

`[实测]` 注册表项：

```
HKCR\JianyingPro.JYPack   → JianyingPro.exe -open-draft-pack="%1"     （扩展名 .jypack）
HKCR\JianyingPro.Media    → JianyingPro.exe -open-file="%1"
```

启动器二进制里带 `deeplink or open-draft-pack process end nRet=` 的处理串。也就是说**剪映有一个官方承认的「草稿包」通道**：把草稿打包成 `.jypack` 后用 shell 关联打开。这是比逆向 JSON 更稳的集成面——我们做「在剪映里打开我生成的草稿」时优先走这条。

## 1.5 Lyra XMLDraft：给 AI 用的工程语言（本轮最大发现）

`[实测]` 位置：`Resources\canvas_agent\skills\jianying.hub.studio_lyra_xml_timeline_builder_v2\`
协议版本：`xmldraft/v1`（current）、`xmldraft/v2`（opt_in）；schema 状态 `complete`，诊断数 `0`。

这套东西的本质：**给大模型一套受限的 XML 工程视图 + 一套受限的修改表达式**，让模型改工程而不是生成工程文件。它跟 `draft_content.json` 是两套表示，中间有编译器。

### 1.5.1 文档骨架

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

### 1.5.2 Selection Expression：模型改工程的语言（`[随包文档]` `references/selection.md`）

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

### 1.5.3 一次改几个片段决定调用形态

`[随包文档]` 原文规则的实质：**影响 ≤ 3 个片段，一次调用写完 mutation + `draft.apply()` 直接提交；影响 > 3 个片段或用了 `selectAll`，拆成两次调用**——第一次只提交 mutation（不 apply），宿主缓存成 target_xml；核对通过后再单独 `DraftEditing({selection_expression:"draft.apply();"})`。

抄这条的理由：大模型的输出有长度上限且会漂移。**把「改」和「提交」分成两个事务**，让失败可以带状态重试，而不必重放整批。这比「生成整份工程再覆盖」健壮一个量级。

## 1.6 原生编辑命令表：200+ 条，17 个域（`[实测]`）

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

1. **命令按「对象域.动作」组织，全部走一条总线**。这正是我们 D 文档里 Command Bus 的现成样本。
2. **它自己有一份「模型可用的安全子集」**（`IX1`）：只放 `draft.setCanvasSize`、`track.add`、`segment.split/delete/setTimeRange`、`video.add/setVolume/muteOn`、`audio.add/setVolume`、`text.add`、`undoRedo.*`、`invokeBatch` 等 26 条。全量命令表给内核与内部脚本，模型只拿到这一小片。**这是「AI 权限分级」的落地样本**。
3. `batchStart/batchEnd` + `undoRedo` 说明它把「一批改动 = 一个 undo 步」做成了显式原语。我们的命令总线要照抄这条：**一次 AI 提交 = 一个可整体撤销的事务**。

## 1.7 自动化与 Agent 内部架构（`[实测]`）

### 1.7.1 真能调的 CLI

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

### 1.7.2 内部分级：Director → Editing → Flair → DraftEditing

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

### 1.7.3 工程能力清单（从 skill 目录名反推）

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

## 1.8 音频与语音（`[实测]`）

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

## 1.9 剪映的五条可搬运结论

1. **工程双层表示**：磁盘 JSON（快、全量）+ 内存 XML 视图（给模型、给 diff、给事务）。两层之间用编译器连接，模型只见 XML。这条直接决定我们 E 文档的格式设计。
2. **命令表 + 白名单 + 批事务**：200 条命令按域组织，模型只拿到 26 条安全子集，一次 AI 提交等于一个 undo 步。
3. **端侧模型货架 + 云侧能力边界**：能端侧的全端侧，省带宽省钱且离线可用；要版权的走云。模型按能力分目录、按 100KB~30MB 分级部署。
4. **特效即参数化模板包**：`Resources\MixMode\MixMode.json` 明列 `nameId/effectId/resourceId/path` 四元组（实测例：`color_filter / 871339 / 6758325170760323597`），单包结构为 `config.json` + `content.json` + `anim.prefab` + `blend.material` + `xshader\blend.xshader`。**它没有「特效代码」这个概念，全是数据 + 着色器 + 预制体**。这条最省事：我们的包装效果也按「模板包 + 参数槽位」做，一个特效 = 一份清单 + 一批资源 + 一个参数 schema。
5. **AI 采纳率是产品指标**：`attachment_editing.json` + `agent_adoption_ledger.db` 说明它在统计「AI 给的方案人到底用没用」。我们的 `ai_decision` 表要把这个做成可查询的一等数据。

---

# 第二章 DaVinci Resolve 21.2

## 2.1 架构总览：一个 581MB 的 Qt 单体 + 一组可插拔子系统

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

## 2.2 脚本自动化：三层入口，一套对象模型

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

## 2.3 API 面清点：22 个类，530 个方法（`[实测]`）

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

## 2.4 工程存储：SQLite 库 + `.drp` 是 ZIP 包 XML（`[实测]`）

### 2.4.1 磁盘库

`[实测]` `sqldrivers\qsqlite.dll` + 自带 `sqlite3.exe` + `qsqlpsql.dll` + `libpq.dll`：
- 本地库走 SQLite；协作/多机走 PostgreSQL。
- 自带 `sqlite3.exe` 意味着**官方允许直接开工程库做只读分析**（分析工具就靠它）。
- `ProjectManager.GetDatabaseList()` / `SetCurrentDatabase()` 说明库是可切换的多库模型；`ArchiveProject()` / `RestoreProject()` 是整库快照级操作。

### 2.4.2 `.drp` 拆包结果

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
**它把 OTIO 当成一等导出格式**。这条直接影响我们的格式策略：AVS 必须能无损映射到 OTIO（见 E 文档 5 节）。

## 2.5 Fusion：节点引擎 + 三种扩展语言

`[实测]` `Plugins\*.plugin` 是 Fusion 的模块化二进制（`fuses.plugin` 156KB 是 Fuse 运行时，`openfx.plugin` 337KB 是 OFX 宿主，`krokodove.plugin` 1.9MB 与 `ograf.plugin` 1.19MB 是第三方节点包内联）：

### 2.5.1 Fuse：Lua 写的原生节点

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

### 2.5.2 DCTL：C 风格像素着色器（`[随包文档]` `Developer\DaVinciCTL\README.txt`）

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

### 2.5.3 OFX：宿主契约（`[随包文档]` `Developer\OpenFX\README.txt`）

- 随包 OFX 1.4 头 + C++ 包装 + 5 个样例（Gain / TemporalBlur / DissolveTransition / RandomFrameAccess / …）。
- 三种上下文：`eContextFilter`（单输入滤镜）、`eContextTransition`（双输入 + `Transition` 参数）、生成器。
- GPU 三后端各自的入口：`processImagesCUDA` / `processImagesOpenCL` / `processImagesMetal` / `multiThreadProcessImages`。
- 装到 `C:\Program Files\Common Files\OFX\Plugins`；Windows ARM64 宿主按 `Win-arm64x` → `Win-arm64ec` → `Win64` 顺序扫。
- `p_Desc.setSupportsCudaStream(true)` 表明宿主可传 CUDA stream；`setNoSpatialAwareness(true)` 表明该效果与邻域无关（可进 LUT 合批）。

**OFX 是最划算的生态接入点**：写一次，Resolve / Natron / Nuke / Vegas / Bash 都能吃。我们的特效系统做成 OFX 1.4 宿主，第一年就白拿几百个现成效果。

## 2.6 调色与色彩管理

`[实测]` `OpenColorIO_2_5.dll` + `Plugins\opencolorio.plugin` + `CanonLUTs\` + `Fusion\LUTs\` + `ROMM RGB.icc` / `USWebCoatedSWOP.icc`（`AfResources` 里带印刷级 ICC）。

`[随包文档]` 设置族的键直接反映色彩管线的分层：
- 项目级：`colorScience`（DaVinci YRGB / DaVinci YRGB Color Managed / ACEScc / ACEScct）、ACES 版本、IDT/ODT 选择。
- 片段级：`SetCDL`、`Graph.SetLUT(nodeIndex, path)`、`MediaPoolItem.GetClipProperty('Color Space')`。
- 节点级：`Graph` 15 个方法里一半是节点标签/颜色/缓存/使能，说明**调色节点是脚本可控的一等对象**。
- 缓存：`SetNodeCacheMode(cache_value)` 对应 `resolve.CACHE_*`，节点级缓存开关能脚本化。

`[推断]` 判据：既带 OCIO 2.5 又自带 ACES DCTL 实现，ACES 走的是「自己的 DCTL + 参考 ampa/aces-dev」，不是简单调用 OCIO 的 ACES config。这解释了为什么 DCTL 能做自定义 IDT/ODT。

## 2.7 Fairlight 音频

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

## 2.8 AI：端侧推理栈完整内嵌（`[实测]`）

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

## 2.9 Workflow Integration SDK：Electron 面板（`[实测]`）

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

## 2.10 渲染与交付

`[实测]`/`[随包文档]`：
- 渲染 job 模型：`AddRenderJob` → 设置 `SetRenderSettings({...})` → `StartRendering([jobId...])` → `GetRenderJobStatus(jobId)`；`IsRenderingInProgress` / `StopRendering`。
- 渲染前后挂钩脚本：Deliver 页 Advanced Settings 里能挂 start/end 脚本，脚本里能拿到 `job ID` / `status` / `render errors`（`[随包文档]` `8_slack_notification_by_render_job.py`）。
- 快速导出：`SetQuickExportEnabledForRenderPreset` / `RenderWithQuickExport` / `GetRenderWithQuickExportStatus`（同步/异步两套）。
- 编解码清单可查：`GetRenderFormats` / `GetRenderCodecs` / `GetAudioRenderFormats` / `GetAudioRenderCodecs`。
- 交付元数据：Dolby Vision 版本化导出（2.9 / 4.0 / 5.1）、HDR10 Profile A/B、ALE/CDL、DCP（`fraunhoferdcp` + `kdu`）。

## 2.11 达芬奇的四条可搬运结论

1. **工程 = 明文结构 + 二进制内容 + UUID 引用**。结构可读（能 diff、能脚本、能手改），内容防手改（合成/特效打包），引用用 UUID（能合并、能套模板）。
2. **脚本 API 的重心在片段层**：`TimelineItem` 110 个方法就是最好的接口设计参考；渲染走 job id；设置走字符串字典。
3. **扩展四条腿**：Lua（Fuse，节点）、C 着色器（DCTL，像素）、C++（OFX，跨宿主）、Electron（Workflow Integration，面板）。四条腿各管一段，互不挤占。
4. **AI 能力包化 + 脚本可管**：能力即包，包可脚本安装，缺包可探测，任务可查状态。

## 2.12 与官方 21 版手册交叉核对后的补正

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

最后一条值得单独盯着：`[第三方研究]` 有资料称 **Resolve Studio 21.1 起自带原生 `ResolveMCP`（stdio，8 个工具）**。若成立，意味着达芬奇已经把「被外部 Agent 编排」做成官方能力——这条我们这条路线（D 文档 L12）不是独家，得靠工具面深度（22 个工具、完整剪辑语义）拉开差距。该说法我没有在官方页面直接核实，标 `[未证实]`，列入待验证。

---

# 第三章 After Effects 27.0

> 本机未安装 AE（Adobe 不提供免登录离线包，官方渠道是 CC 桌面应用登录下载，见 `README_工程说明.md` 第 3 节）。本章全部结论来自公开一手资料：docsforadobe 官方脚本/SDK 文档、`AdobeDocs/uxp-after-effects`、Adobe-CEP 官方仓库、`aerender -help` 原文、lottie-docs 的 AEP 字节级字段表、两个可直接读源码的开源解析器。原始抓取记录见 `_research\R2_AE内部结构与自动化调研.md`（357 行，每条带 URL 与证据标签）。

## 3.1 三层结构：宿主 + 两条 SDK 腿 + 三层脚本皮

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

## 3.2 `.aep` 工程格式：RIFX 二进制，字段级可解析

### 3.2.1 容器

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

### 3.2.2 关键 chunk 表（可据此写解析器）

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

### 3.2.3 时间与关键帧的编码（抄这套要谨慎，它是历史包袱）

- 时间值是 `uint16`，按 `cdta.time_scale` 缩放：`frames = value / time_scale`；图层的 `ldta.start_time` 是额外偏移。`uint16` 上限 65535，这是 AE 当年 16 位时代的遗产——**我们现在用 int64 微秒，不背这个包袱**。
- 关键帧公共头：1 字节保留 + Time(2) + 2 字节保留 + Ease Mode(1: `1`Linear/`2`Ease/`3`Hold) + Label(1) + Attributes(1)。
- 多维属性关键帧体 = `float64[n]` 五段：Value / In Speed / In Influence / Out Speed / Out Influence。
- Attributes 里带 Continuous Bezier、Auto Bezier、Roving across time 三个位。
- 颜色按 ARGB float，范围 [0,255]。

### 3.2.4 `.aepx`：AE 自己的 XML 工程

`[第三方研究]` AE 能把工程另存为 XML 工程 `.aepx`，结构等同 RIFX：`<string>` 取代 `Utf8`，RIFX 的 `LIST` 变成有子元素的节点，二进制数据 hex 编码进 `bdata` 属性，XMP 变成 `ProjectXMPMetadata` 元素。

对我们的用处：**模板注入走 `.aepx`（文本级改参数），静态审计走 `.aep`（字段级）**。`[推断]`

### 3.2.5 开源解析器现状（能直接借的）

| 仓库 | 语言 | 能力 | 边界 |
| --- | --- | --- | --- |
| `boltframe/aftereffects-aep-parser` 132★ | Go | 静态只读解析 .aep，仓库自带 Kaitai 定义 + 样本 .aep | 表达式不求值、不渲染 |
| `forticheprod/py-aep` 87★ | Python3 | **读 + 写**：建空工程、建合成/文件夹/图层（solid/null/shape/text/camera/light/参数化网格）、加删关键帧（含遮罩路径/源文本/标记/渐变）、改渐变与渲染/输出模块设置、管理渲染队列、色彩管理 | 不求值表达式、不渲染像素、不碰选中态与运行期状态 |
| `actumn/aepx.js` 42★ | Node | .aepx → JSON | 已标 Deprecated |
| `Jam3/ae-to-json` | JSX+Node | 在活 AE 里跑 JSX 导 JSON | 依赖运行中的 AE |
| `virtualritz/dot-aep` / `yueli-fx/aep-reader` | Rust | 只读 | star 少，字段覆盖未知 |
| `daveowenatl/AepSharp` | C# | boltframe 的 C# 移植 | 同上 |

`py-aep` 的能力清单里有一句最值钱：**它能改 ExtendScript 摸不到的渐变、渲染设置、3D 渲染器选项、输出模块设置**。也就是说「静态改工程」这条路在参数面上比脚本更宽。

## 3.3 自动化体系：三层皮 + 一个命令行 + 两条 SDK

### 3.3.1 ExtendScript 的真实能力与边界（`[官方文档]` 逐条核对）

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

### 3.3.2 CEP 与 UXP 的真实状态

| 项 | CEP | UXP |
| --- | --- | --- |
| 形态 | HTML/CSS/JS 面板，ZXP 分发 | 共享 UXP 平台（`fs`/`os`/`uxp`）+ Spectrum UI + 主机模块 |
| 调 AE 的方式 | 一切操作拼成 JSX 字符串走 `CSInterface.evalScript()` | `const app = require("aftereffects")` 直调对象模型 |
| AE 版本对应 | AE 16/17→CEP 9、17.1.4→CEP 10、18.4→CEP 11、**AE 25.0→CEP 12** | 官方文档仓 `AdobeDocs/uxp-aftereffects`，正文标 `throughout the beta` |
| 内置运行时 | CEP 12 带 Node 17.7.1 + Node-WebKit 0.62.1，Node API 要 `--enable-nodejs`（全局多出 `cep_node`） | UXP 自带 |
| 停用日期 | CEP 12 cookbook 全文没有 EOL 声明 `[未证实]` | AE 起版版本号在可达资料里没写死 `[未证实]` |
| UXP 的能力缺口 | — | 官方索引 44 个 API 页里**没有** `executeCommand` / `scheduleTask` / `watchFolder` / `Socket` |

`[官方文档]` UXP 的能力其实不小：44 个 API 页覆盖 Application/Project/ItemCollection/CompItem/AVLayer/Layer/LayerCollection/CameraLayer/LightLayer/ShapeLayer/TextLayer/ThreeDModelLayer/ParametricMeshLayer/Property/PropertyGroup/MaskPropertyGroup/Shape/KeyframeEase/MarkerValue/TextDocument/CharacterRange/ParagraphRange/Font(s)/ImportOptions/各类 Source/FolderItem/GuideOptions/View(Viewer/Options)/Preferences/Settings/**RenderQueue + RenderQueueItem + RQItemCollection + OMCollection + OutputModule**/DeferredCall——等于把 ExtendScript 那套抄了一遍，连渲染队列都在。缺口在「菜单命令 ID 通道、Watch Folder、Socket」这三块。

### 3.3.3 aerender：官方唯一批量渲染入口（`[官方文档]` `-help` 原文）

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

### 3.3.4 驱动 AE 的四条路径（按「要不要 GUI / 扛不扛并发」选）

| 路径 | 命令/机制 | 优点 | 短板 |
| --- | --- | --- | --- |
| A `afterfx -r` | `afterfx.exe -r script.jsx`、`afterfx.exe -s "代码"` | 最轻，官方唯一命令行入口；`-r` 把脚本丢给**已存在实例**执行，不新开 | 要 GUI 授权；`renderQueue.render()` 阻塞；回显要用 `AfterFX.com` |
| B `aerender` | 见 3.3.3 | 无 GUI、可多进程、日志齐全 | 只渲图，不建工程 |
| C 面板 | CEP/UXP | 用户可交互 | 对外部程序不友好 |
| D 静态改工程 | `py-aep` 改 `.aep` → 交给 B | **省一次 AE 启动（几秒到几十秒）与一次授权占用** | 表达式不求值、渲不了图 |

`[推断]` 我们的模板量产组合定为：**模板 `.aep` 常驻 + `py-aep` 改参数落新 `.aep` + `aerender` 多进程渲染 + `-log` 收日志 + 失败重投**；渲染设置用 `-RStemplate`/`-OMtemplate` 锁死，改参数与渲染设置彻底分离，把变量面压到最小。

## 3.4 表达式引擎：跟脚本是两套东西

- 表达式只描述「这个属性等于什么」，脚本是「让应用做事」；**表达式读不到脚本里的变量与函数**。`[官方文档]`
- 引擎两档可切：`app.project.expressionEngine` 取 `extendscript` 或 `javascript-1.0`（AE 16.0/2019 起可读可写），对应工程设置里的 Expressions Engine 下拉。`[官方文档]`
- **表达式文本就存在工程里的属性上**（`.aep` 的 `LIST tdbs` 里那个 `Utf8` chunk）。静态解析能把表达式完整抠出来。`[第三方研究]`
- 脚本侧操作面：`property.expression`（读写）、`expressionEnabled`、`expressionError`、`canSetExpression`，外加 `project.autoFixExpressions(oldText, newText)` 批量改。
- 求值语义（每帧重算、依赖图层顺序、跨预合成取值）在读到的官方正文里没有规格页；能确定的是纯解析器（py-aep / boltframe）明确把「表达式求值」列为不支持项。`[未证实]` 留白。

对我们的意义：**表达式就是「属性级的脚本化」**。我们要给 AI 一个比表达式更安全的等价物：受控的小 DSL（见 E 文档的 `expr` 字段设计），只放确定性函数，禁网络禁文件。

## 3.5 渲染与缓存：MFR 是真本事

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

## 3.6 数据模型：合成 / 图层 / 属性三层，跟剪映完全不同

| 概念 | AE 的做法 | 剪映的做法 | 我们的选择 |
| --- | --- | --- | --- |
| 容器 | 工程 → 文件夹树 → 合成 → 图层 → 属性组 → 属性 → 关键帧 | 工程 → 轨道数组 → 片段 → 属性/关键帧 | 工程 → 序列 → 轨道 → 片段 → 属性 → 关键帧（借 AE 的深度 + 剪映的扁平） |
| 复用单元 | 合成（precomp），`Source ID` 指向合成项 | 复合片段（compound），`materials.drafts` | 序列即合成，可嵌套，UUID 引用 |
| 时间基 | `cdta.time_scale` + uint16 时间值 | 微秒 int64 | int64 微秒 + 帧率有理数 |
| 关键帧 | float64 五段（值/入速/入影响/出速/出影响）+ Ease Mode | 归一化值 + 曲线类型 | 三次贝塞尔 + 可选缓动预设 + 保持帧 |
| 遮罩 | track matte（层引用 + 模式） | track_matte / 蒙版素材 | 层引用 + 模式 + 蒙版路径对象 |
| 3D | 真 3D：摄像机、灯光、3D 层、参数化网格 | 无（只有 2D 变换） | 3D 层 + 摄像机 + 灯光（第二阶段做） |

`[官方文档]` 图层类型码（`ldta.Layer Type`）：`0` AVLayer、`1` 灯光、`2` 摄像机、`3` 文本、`4` 形状。父子级是 `Parent ID`（u32），轨道遮罩从 AE 23 起多一个 `Matte Layer ID`（u32）。

## 3.7 AE 的四条可搬运结论

1. **用「版本化 suite 结构体」做插件 ABI**（AEGP 的做法）比「稳定 C++ 类虚表」更抗演化：加方法只需出新版本 suite 号，旧插件不重编继续跑。
2. **模板 + 静态改工程 + 批渲染**是量产流水线的最优组合。AE 生态里 `py-aep` + `aerender` 这套组合已经验证了「不启动 GUI 也能出货」，我们做外挂式 AE 集成直接照搬。
3. **MFR 的代价要提前付**：无共享可变状态、显式缓存句柄、UI 与渲染线程严格分层。
4. **表达式的定位**：属性级确定性脚本。我们要给 AI 的版本必须砍掉文件系统与网络访问，只留纯函数。

---

# 第四章 三家横向比对与可搬运清单

## 4.1 七个关键分叉

| 维度 | 剪映 11.7 | 达芬奇 21.2 | AE 27.0 | 我们怎么定 |
| --- | --- | --- | --- | --- |
| UI 技术 | Qt6 Quick + Lynx + CEF | Qt5 Widgets 为主 + CEF 面板 | 自绘（闭源） | Qt6 Widgets 主窗 + Quick 面板 + WebView2 插件位 |
| 工程格式 | JSON（微秒） | SQLite 库 + `.drp`=ZIP(XML) | RIFX 二进制 + `.aepx` XML | SQLite 库 + AVS JSON/XML 双视图导出（E 文档） |
| 时间基 | int64 微秒 | 帧号 + 时间基线偏移 | uint16 + time_scale | int64 微秒 + 有理数帧率 |
| 扩展协议 | 内部命令表 + OFX bundle | Fuse(Lua) + DCTL(C) + OFX + Electron 面板 | PF_Effect + AEGP + CEP/UXP | OFX 1.4 宿主 + 自研 Lua 节点 + WebView 面板 |
| 脚本接口 | `jianying-agent-cli` + Lyra XMLDraft | 22 类 530 方法 + 1144 端口 | JSX + aerender + UXP | MCP 工具 + REST/JSON-RPC 内部总线（D 文档） |
| AI 落地 | 端侧 46 个模型包 + 云侧 SDK | 端侧 llama.cpp/ORT/OpenVINO + Extras 包 | 无端侧 AI（靠第三方脚本） | 端侧 ORT+llama.cpp，能力包化（F 文档） |
| 撤销粒度 | 命令 + `batchStart/batchEnd` | 内部（脚本层无撤销 API） | `beginUndoGroup/endUndoGroup` | 命令总线 + 事务 + 事件溯源（D 文档） |

## 4.2 可搬运清单（按「抄什么 / 从哪抄 / 抄到哪层」）

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

## 4.3 三家都做得难看的三个地方（我们的机会）

| 现象 | 三家各自的表现 | 我们怎么做 |
| --- | --- | --- |
| AI 改工程要么太粗要么不可控 | 剪映靠专用协议（好用但绑定自己）；达芬奇给脚本 API（自由但模型易写错）；AE 全靠第三方拼 JSX（脆） | 受限 DSL + 预演（`--preview` 回候选不落地）+ 修订号乐观锁 + 一次提交等于一个 undo 步 |
| 工程文件不可读/不可 diff | 剪映双重 JSON 字符串、达芬奇 `FieldsBlob`、AE RIFX | JSON 主存 + 规范化排序 + 语义 diff（按对象与属性，不按行） |
| 长任务黑盒 | 三家都只有「状态查询」，没有「可续跑的步骤账本」 | 任务表 + 步骤账本（每步输入/输出/证据）+ 断点续跑 |

## 4.4 三家的不可替代之处（抄不来的部分）

- **剪映**：短视频素材库 + 模板商城 + 端侧模型与产品化的贴合度。它把「一键成片」拆成了 18 个技能包 + 200 条命令，这套产品工程学比代码更值钱。
- **达芬奇**：Fusion 节点的完整度 + 色彩科学的行业信任 + 免费的 Studio 级调色。它的护城河是「专业调色师的工作流习惯」。
- **AE**：表达式 + 效果插件生态 + 与 PS/AI/PR 的工程互操作。它的护城河是二十年的插件积累与 MoGraph 用户惯性。