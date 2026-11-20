# AI Video Studio 技术底座研究

对三款成熟视频软件（剪映专业版 11.7 / DaVinci Resolve 21.2 / After Effects 27.0）做静态结构与自动化接口逆向，产出一套可直接落地的技术底座设计：架构、工程文件格式、选型、路线图。

**一句话结论**：决定产品差异的三层全自研（时间轴模型 / 工程格式 / Agent 与事务），其余全借生态（FFmpeg / OCIO / OpenFX / OTIO / MAGPIE / MCP / Whisper 系 / SAM2），GPL 系一律进程外隔离。

---

## 从哪读起

| 目标 | 文件 |
| --- | --- |
| 一次读完全部 | [`AI_Video_Studio_技术底座总报告.md`](AI_Video_Studio_技术底座总报告.md)（约 21 万字符，8 部分 + 2 附录） |
| 只看路线与结论 | [`docs/00_研究路线与技术地图.md`](docs/00_研究路线与技术地图.md) |
| 三家软件怎么做的 | [`docs/A_三大软件逆向研究报告.md`](docs/A_三大软件逆向研究报告.md) |
| 功能逐项对照 | [`docs/B_三大软件功能对照表.md`](docs/B_三大软件功能对照表.md)（116 行主表） |
| 开源项目与协议分级 | [`docs/C_GitHub开源项目技术清单.md`](docs/C_GitHub开源项目技术清单.md)（83 个项目） |
| 系统怎么搭 | [`docs/D_AI_Video_Studio总体技术架构.md`](docs/D_AI_Video_Studio总体技术架构.md) |
| 工程格式 | [`docs/E_统一工程文件格式.md`](docs/E_统一工程文件格式.md) + [`schema/E_avs_project.schema.json`](schema/E_avs_project.schema.json) |
| 每层用什么 | [`docs/F_技术选型报告.md`](docs/F_技术选型报告.md) |
| 什么时候做什么 | [`docs/G_开发路线图.md`](docs/G_开发路线图.md) |

---

## 核心发现（每条都在正文里有证据档）

### 剪映 11.7.0.14652

- **不是 Electron**：Qt6 6.2.2 + CEF 121 + 字节 Lynx 三层前端，C++ 剪辑内核 `videoeditor.dll`（70MB），渲染栈 `VECreator.dll`（275MB）/ `cccreator.dll`（151MB），引导壳仅 0.42MB。
- **草稿格式字段级**：`draft_content.json` 28 个顶层键、46 类 materials、时间全微秒、变换归一化（`clip.transform.y = -0.76`）、`extra_material_refs` 做效果总线。
- **Lyra XMLDraft 协议**（`xmldraft/v1`、`v2`）：给大模型的不是 JSON patch，而是带选择器的改动小程序 —— 11 个 mutation + `target_xml` / `current_xml` / `apply()` 三态事务 + 「影响 ≤3 片段一次提交，>3 个拆两批」。
- **原生命令表 17 个域 200+ 条**，模型只拿到其中 26 条安全子集；`batchStart/batchEnd` 让「一批改动 = 一个 undo 步」。
- **端侧 AI 货架**：46 个模型包约 240MB（抠像 52MB、音频 65MB、检索 55MB…），四个推理后端（ORT-CUDA / OpenVINO-NPU / 高通 QNN / 字节自研 ByteNN）；声音克隆与 TTS 走云。
- **6.0 起草稿上锁**（AES-CTR 家族推断），但外部写明文剪映照读；官方 `.jypack` 关联通道 + `jianying-agent-cli` 五个子命令。

### DaVinci Resolve 21.2

- `.drp` = **ZIP**：`project.xml` + `MediaPool/Master/MpFolder.xml` + `SeqContainer/<uuid>.xml` + `Gallery.xml`，明文结构 + 二进制内容 + UUID 引用。
- 脚本面 **22 个类 / 530 个方法**（`TimelineItem` 独占 110 个），Lua 5.1 + 内嵌 Python 3.14，端口 1144。
- 四条扩展腿：Fuse（Lua 节点）/ DCTL（C 风格像素着色器）/ OpenFX 1.4 / Electron 面板。
- 端侧推理栈完整内嵌：`llama.dll` + `mtmd.dll` + ORT + OpenVINO + `torch_cpu`（231MB）+ cuDNN 9；AI 能力包化（Extras）且脚本可装。

### After Effects 27.0

- `.aep` 是 RIFX（`Egg!`）大端容器，chunk 结构到字段级（`cdta` / `ldta` / `idta` / `tdbs`），时间基仍是 `uint16 × time_scale`。
- 三层脚本皮（ExtendScript / CEP / UXP）+ 一个命令行（`aerender`）+ 两条 SDK（PF_Effect / AEGP）。
- 三个硬边界：脚本读不到像素、`renderQueue.render()` 阻塞、`executeCommand` 与语言包绑死。
- 量产组合：模板 `.aep` + `py-aep` 改参数 + `aerender` 多进程。

---

## 交付物结构

```
AI_Video_Studio_技术底座总报告.md      整合版单文件（8 部分 + 附录 A schema + 附录 B 样例）
docs/                                 8 份独立交付物（00 / A–G）
schema/E_avs_project.schema.json      AVS 1.0 工程格式 schema（JSON Schema 2020-12，19 个 $defs）
samples/min_project.json              最小工程样例（已过 schema 校验）
tools/                                校验与装配脚本
  ├─ check_banned.py                  用词扫描
  ├─ validate_sample.py               样例 → schema 校验
  └─ merge_report.py                  8 份文档 → 整合版
research/                             各软件原始调研笔记（每条结论带 URL 与证据标签）
```

## 自己验一遍

```bash
python tools/validate_sample.py   # 期望：PASS：样例通过 AVS 1.0 schema 校验
python tools/merge_report.py      # 重新装配整合版
python tools/check_banned.py .    # 用词扫描
```

AVS 格式的三条 CI 门禁（见 `docs/E_统一工程文件格式.md` 第 11 节）：
schema 校验通过、`json → xml → json` 规范化后字节相等、事件日志重放出的工程状态与保存态一致。

---

## 证据分级

正文每一条结论后面标来源：

| 标记 | 含义 |
| --- | --- |
| `[实测]` | 本机隔离环境跑命令 / 读文件拿到的原始事实 |
| `[随包文档]` | 软件自带官方开发者文档、`.pyi`、样例代码 |
| `[开源代码]` | 公开仓库可逐行对照 |
| `[第三方]` | 逆向研究帖、专利、技术演讲 |
| `[推断]` | 有链条的可证伪推理，带判据 |
| `[未证实]` | 只有传闻，照实留白 |

## 照实留白的项

`ResolveMCP`（21.1 自带 8 工具）、CEP 在 AE 的 EOL 日期、UXP 在 AE 的起版版本、剪映加密算法本体、达芬奇库表名、`onnxruntime` / `cpp-sdk` 的 star 与协议、AE 磁盘缓存目录布局、表达式求值规格 —— 全部标 `[未证实]`，没拿传闻当事实。

## 环境与边界

研究在隔离副本上进行：剪映 11.7 与 Resolve 21.2 从官方安装包展开到工程目录，数据目录重定向，不写宿主注册表、不建全局快捷方式、不动本机原装软件。AE 未安装，结论全部来自公开一手文档与开源解析器（`boltframe/aftereffects-aep-parser`、`forticheprod/py-aep`）。

## 协议

文档内容版权归项目所有者；未指定开源协议前默认保留所有权利。引用第三方项目时已在正文标注其协议（GPL 系标注为「只能进程外隔离」）。

## 链接

- OpenTimelineIO · OpenFX · OpenColorIO · FFmpeg · MAGPIE（`yetone/magpie`，MIT）· MCP spec 2026-07-28
- 剪映草稿解析参考：`GuanYixuan/pyJianYingDraft`（0.3.1，Apache-2.0）
- AE 工程解析参考：`boltframe/aftereffects-aep-parser`（Go，132★）、`forticheprod/py-aep`（Python，87★）