# E 统一工程文件格式 AVS（AI Video Studio Project）

版本：AVS 1.0（本文件定的第一版）
配套：`E_avs_project.schema.json`（JSON Schema 2020-12，可直接喂 `ajv` / `python-jsonschema` 校验）

---

## 1. 七条设计原则（每条都对应三家里的一个坑）

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

## 2. 三层落地形态

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

## 3. 全局规则

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

## 4. 顶层结构

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

### 4.1 settings

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

### 4.2 media

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

### 4.3 sequence（序列 = AE 的 comp = 剪映的复合片段）

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

#### 4.3.1 track

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

主轨约束（抄剪映的规则）：`role:"main"` 的轨道**全工程只能有一条**，且它的 `clips` 必须**首尾相接无空洞**。

**这条约束属于 validator，不属于 schema。** JSON Schema 表达不了「跨片段的连续性」「同轨不重叠」「ID 全局唯一」「引用可解析」这四类约束。分工写死：

| 校验层 | 管什么 | 实现 |
| --- | --- | --- |
| schema（`E_avs_project.schema.json`） | 单对象形状：类型、必需字段、枚举、范围、单字段正负 | `ajv` / `jsonschema` |
| validator（编译器内建） | 跨对象不变量：主轨唯一且连续、同轨不重叠、ID 唯一、引用可解析、变速曲线积分一致、转场时长上限 | C++ `IProjectValidator`，Python 侧有等价实现供 CI 用 |
| 语义校验 | 素材时长够不够、嵌套有没有环、字体存不存在 | 导入/编译期 |

用 11 条反例跑过一轮（`_audit/schema_negtest.py`），schema 拦得住 4 条（负时长、浮点微秒、fps 分母为 0、画布为 0），拦不住 7 条（主轨留洞、两条主轨、重复 ID、字段名拼错、悬空素材、双侧转场）。**所以「schema 校验通过」只等于形状对，不等于工程能编。** 这条区别写进 CI：任何合并都必须同时过 schema 与 validator，缺一不算数。

#### 4.3.2 clip

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

### 4.4 effects_lib（效果定义）与 clip.effects（实例）

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

### 4.5 ai.runs（AI 一次运行）

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

### 4.6 history（事件溯源）

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

## 5. 关键机制

### 5.1 时间模型

```
时间线坐标 = int64 微秒，从序列起点 0 开始
帧号换算 = floor(us × fps.num / (fps.den × 1_000_000))，只在需要帧精度时算
drop-frame：只在 fps.den 为 1001 时有效，时间码显示层处理，工程内存储始终是无损微秒
```

为什么不用帧号做主键：变速、音频、字幕都需要亚帧精度；帧号会让 23.976 与 24fps 混剪的舍入误差越滚越大。微秒 + 有理数帧率的组合能无损表示所有常见帧率。

### 5.2 主轨连续与副轨自由

- 主轨：`role:"main"`，片段首尾相接，`seq_start_us` 由前序推导，schema 校验时校验「无空洞、无重叠、首段从 0 开始」。
- 副轨：任意位置、任意时长，允许重叠（同轨道内重叠由渲染层按 `index` 处理，或在同轨道内禁止——第一版选**禁止同轨重叠**，需要叠加就分轨，跟剪映一致）。
- 相对对齐：副轨片段可声明相对锚点，编译时展开成绝对时间：

```jsonc
"anchor": {"start_to": "cl_v1.right", "offset_us": -200000}
// 或 "start_to": "main.left" / "main.right"
```

`anchor` 与 `seq_start_us` 互斥。这样「音乐卡点」「字幕跟人声」不用算绝对时间，主轨一改自动跟随。

### 5.3 关键帧

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

### 5.4 变速

```jsonc
"speed": 1.0,
"speed_curve": {
  "points": [{"t_us": 0, "speed": 1.0}, {"t_us": 2000000, "speed": 2.0}, {"t_us": 6150000, "speed": 0.5}],
  "interp": "linear"
}
```

`seq_dur_us` 与 `src_dur_us` 的关系：匀速时 `src_dur_us = seq_dur_us × speed`；有 `speed_curve` 时以曲线积分为准，`src_dur_us` 必须由编译器算出来写入，**不许两边都手填**（这条是剪映 `time.duration` 与 `speed` 并存时的坑）。

### 5.5 transform（归一化坐标）

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

### 5.6 crop

```jsonc
"crop": {
  "mode": "inset",                       // inset（四边内缩比例）| corners（四角自定义，做透视裁切）
  "left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0,   // mode=inset，0~1 比例
  "corners": null,                        // mode=corners 时给 8 个数
  "lock_aspect": false
}
```

### 5.7 audio

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

### 5.8 transition

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

### 5.9 text / subtitle / sticker

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

### 5.10 代理与缓存

代理不进工程文件，进 `media.derived` 与独立缓存目录；工程里只存 `proxy.path` 相对引用 + 生成参数。缓存目录采用「根 + 内容哈希」布局，删除缓存不影响工程可读。

### 5.11 版本迁移

```jsonc
{"schema_version": "1.0.0", "min_reader": "1.0.0"}
```

规则：
- 读入时若 `schema_version` 高于自己的支持上限 → 拒绝打开并提示升级（不做静默降级）。
- 若 `min_reader` 高于自己 → 同上。
- 迁移函数链：`migrate_1_0_0_to_1_1_0(doc)` 纯函数，输入输出都是规范化 JSON，可单测。
- 每次迁移都在 `history.events` 里写一条 `system:migrate` 事件，留痕。

---

## 6. 规范化与 diff

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

## 7. 并发与协作（第一版的最小实现）

| 机制 | 做法 |
| --- | --- |
| 乐观锁 | 每次提交带 `base_revision`，服务端比对后自增 `revision` |
| 单写者 | 同一序列同一时刻只有一个写者（UI 或某个 Agent run），用租约表管 |
| 冲突 | 属性级最后写入胜，但对象级删除优先（删了的对象不再被改活） |
| 合并 | 语义 diff 的最小补丁按属性路径三方合并；冲突项进待人工确认队列 |

第一版只做「单机多客户端 + 服务端合并」，不做 CRDT。理由：视频工程的强顺序语义（轨道顺序、主轨连续）用 CRDT 表达会引入大量不变量修复逻辑，收益低。

---

## 8. XML 视图（给 Agent 的形态）与映射表

### 8.1 视图规则

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

### 8.2 字段映射表（JSON ↔ XML）

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

### 8.3 改动程序（AVS Selection DSL）

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

### 8.4 预演与落地

```
plan()   → 产生候选 XML，回给模型看，不落地
validate()→ 跑 schema 与不变量（主轨连续、无重叠、引用完整、时间范围有效）
apply()  → 开事务，编译 XML → JSON → 命令批次，一条命令一个 event，最后 commit
```
`plan → 人看一眼 → apply` 这条链路是产品级 AI 剪辑的必要形态：模型一次就对是奢望，**让它在候选区里改到对，再一次落地**。

---

## 9. 互转表

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

## 10. 完整样例（一个 18 行的最小工程）

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

## 11. 校验清单（写进 CI 的不变量）

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