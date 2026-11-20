# R2 — After Effects 内部结构、工程格式与自动化体系 · 事实清单

抓取时间：2026-11-20。本机未装 AE，全部结论来自公开资料的实抓正文。

## 0. 抓取通道与可读性（先说清楚证据链）

- `web_search` 工具本轮不可用：返回 `DeepSeek API error (HTTP 402): Insufficient Balance`，检索端点 `https://api.deepseek.com/v1/tools/search` 拒付。所以没有一条结论来自搜索引擎摘要。
- 可用通道：`web_fetch`（docsforadobe.dev、helpx.adobe.com 可达）、`Invoke-WebRequest`（`raw.githubusercontent.com`、`api.github.com`、`registry.npmjs.org`、`pypi.org/pypi/*/json` 可达）。
- 不可达：`github.com` 页面（连接被中断）、`web.archive.org`、`r.jina.ai`、`duckduckgo`、`experienceleague.adobe.com`、`www.aenhancers.com`、`developer.adobe.com`（SPA 空壳，返回 200 但正文为空）。
- Adobe 官方 `helpx.adobe.com` 页面正文读不到全文：页面 HTML 前 ~30k 字符全是全站导航树，取回内容在导航里就被截断。所以 aerender 官方页只确认了 URL 与存在性，参数表改用实抓的 `aerender -help` 输出（见 3.4）。
- 凡是 GitHub 仓库，一律用 `api.github.com/repos/.../readme` 或 `raw.githubusercontent.com` 读原文，避开 github.com 的不可达。

---

## 1. `.aep` 二进制工程格式

### 1.1 容器与字节序

`.aep` 是 RIFF 的变体 **RIFX**：头 4 字节 ASCII 为 `RIFX`，紧跟 `uint32` 文件长度，再跟 4 字节格式标识 `Egg!`，之后是 chunk 序列；整数一律**大端**。可直接 `Get-Content -Encoding Byte` 看前 12 字节自证。 [第三方研究] https://github.com/boltframe/aftereffects-aep-parser （README 原文："encoded using the Resource Interchange File Format (RIFF) in a Big-Endian byte-ordering (also known as RIFX)… will contain the following ASCII characters: `RIFX....`"）

同一份事实在 lottie-docs 的 AEP 章节里给了完整字段表，并明确："It should always be `RIFX` format (big endian). The format identifier for AEP is `Egg!`." [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md

### 1.2 chunk 结构

每个 chunk = 4 字节 ASCII 标识 + `uint32` 数据长度 + 数据；长度奇数时补 1 字节 padding（boltframe 的 Kaitai 定义里 `padding: if: (block_size % 2) != 0`）。`LIST` 类 chunk 的数据体是 4 字节子类型标识 + 嵌套 chunk 序列。 [开源代码] https://github.com/boltframe/aftereffects-aep-parser

### 1.3 关键 chunk（已抓到字段级定义）

| chunk | 含义 | 关键字段 |
|---|---|---|
| `LIST Egg!` | 文件根，紧随 RIFX 头 | 全项目 chunk 树 |
| `head` | 文件头 | 前 6 字节疑似 AE 版本指纹；另有 `uint16` File Revision，"每次保存 +2"（原文："Increases by 2 every time you save"） |
| `LIST Fold` | 根文件夹 | 内含 `LIST Item` 序列 |
| `LIST Sfdr` | 子文件夹 | 内含 `LIST Item` 序列 |
| `LIST Item` | 一个工程项 | `idta` + `Utf8`(名字) + `cmta`(注释，可选) + 类型专属 chunk |
| `idta` | 项数据 | 项 ID + 项类型：`1`=文件夹、`4`=合成、`7`=素材 |
| `cdta` | 合成数据 | X/Y Resolution(u16)、Time Scale(u16)、Playhead、In/Out Time、Comp duration、Color(24bit RGB)、Flags、Width(u16)、Height(u16)、Pixel Ratio(W/H u32)、Framerate(u16)、Shutter Angle、Shutter Phase、Samples Limit、Samples per frame |
| `ldta` | 图层数据 | Layer ID(u32)、Quality(u16, 0线框/1草图/2最佳)、Start Time(s16)、In/Out Time、Attributes(3字节 Flags)、Source ID(u32)、Label Color、Layer Name(32字节 string0)、Matte Mode、Layer Type(u8)、Parent ID(u32)、Matte Layer ID(u32, 仅 AE≥23) |
| `LIST Layr` | 一个图层 | `ldta` + `Utf8` + `cmta` + `LIST tdgp` |
| `LIST tdgp` | 属性组 | `tdsb`(flags) + `tdsn>Utf8`(名) + 属性序列 + `tdmn`=`ADBE Group End` 收尾 |
| `LIST tdbs` | 属性定义 | `tdb4`(类型/维数/是否动画) + `cdat`(静态值) 或 `LIST list`(关键帧) + `Utf8`(表达式代码) |
| `lhd3` / `ldat` | 关键帧容器 / 关键帧数据 | `ldat` 元素大小 = `ldat 长度 / lhd3 计数` |
| `opti` | 素材信息 | 素材类型在 `opti` 前 4 字节 |
| `sspc` | 素材尺寸 | 宽/高等 |
| `fiac` | 当前活动项 | 标志 chunk |
| `LIST tdsn`/`fnam`/`pdnm` | 名字类容器 | 内部含子 chunk（不是普通 LIST） |
| `LIST btdk` | 特殊块 | 数据格式不同，按 RIFF LIST 解会错 |

来源：[第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md （`cdta` §1151、`ldta` §1202、`head` §1622、`LIST Layr`/`LIST tdgp` §1952–1995、`lhd3`/`ldat` §1368–1420）

### 1.4 时间与关键帧的编码

- 时间值是 `uint16`，按 `cdta` 里的 `time_scale` 缩放：`time_frames = time_value / cdta.time_scale`；若在图层内还要加 `ldta.start_time` 偏移。 [第三方研究] 同上 §71
- 关键帧公共头：1 字节保留 + Time(2) + 2 字节保留 + Ease Mode(1) + Label Color(1) + Attributes(1)。Ease Mode：`1`=Linear、`2`=Ease、`3`=Hold。多维属性的关键帧体是 `float64[n]` 的 Value / In Speed / In Influence / Out Speed / Out Influence 五段。Attributes 里含 Continuous Bezier(0,3)、Auto Bezier(0,4)、Roving across time(0,5)。 [第三方研究] 同上 §1421–1490
- 颜色按 ARGB float 存，范围 [0,255]。 [第三方研究] 同上 §286

结论：**.aep 完全能解析出合成、图层、关键帧、父子关系、遮罩层 ID、表达式文本**——静态解析路径成立，不需要启动 AE。

### 1.5 RIFX 之后还有东西

RIFX 数据结束之后，文件尾部还挂着一段 XMP（XML）元数据，记录 AE 版本、创建/修改时间。 [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §2379

### 1.6 开源解析器仓库与能力边界

| 仓库 | 语言/栈 | 能干什么 | 边界 |
|---|---|---|---|
| `boltframe/aftereffects-aep-parser`（132★） | Go | 静态打开 `.aep`，暴露 project / item / layer / property 结构；仓库自带 `data/*.aep` 样本与 Kaitai 定义 | 只读为主；表达式不求值；不渲染 | [开源代码] https://github.com/boltframe/aftereffects-aep-parser |
| `forticheprod/py-aep`（87★） | Python3（`struct`） | **读 + 写**：读 `.aep`、`py_aep.new()` 从零建空工程、另存 `.aep`、改大部分属性（含 ExtendScript 摸不到的渐变、渲染设置、3D 渲染器选项、输出模块设置）、加删关键帧（含遮罩路径、源文本、标记、方向、渐变）、建合成/文件夹/图层（solid/null/shape/text/camera/light/参数化网格）、导入素材与序列、代理、基本图形、色彩管理（工作/显示空间、素材解释、输出模块）、渲染队列管理 | README 明列不支持：**表达式求值**、**图像采样与渲染**、图层/属性/关键帧的选中态、运行期信息（系统信息、UI 状态）。原 `aep-parser` 包已改名到 `py-aep` | [开源代码] https://github.com/forticheprod/py-aep ；包元数据 [第三方研究] https://pypi.org/project/py-aep/ |
| `actumn/aepx.js`（42★） | Node | 解析 `.aepx`（XML 工程）→ 可读 JSON | README 首行标 Deprecated，叫你去用 boltframe | [开源代码] https://github.com/actumn/aepx.js |
| `Jam3/ae-to-json` | JSX + Node | 在 **AE 内部**跑 JSX 把工程导成 JSON；配 `after-effects` npm 包从 Node 远程跑 | 依赖活的 AE 实例（走 ExtendScript 引擎），不是静态解析；上游自标 experimental | [开源代码] https://github.com/Jam3/ae-to-json |
| `virtualritz/dot-aep`（4★） | Rust | 只读解析 | star 少，字段覆盖未知 | [第三方研究] https://github.com/virtualritz/dot-aep |
| `yueli-fx/aep-reader` | Rust | 只读，MIT OR Apache-2.0 双证 | 同上 | [第三方研究] https://github.com/yueli-fx/aep-reader |
| `daveowenatl/AepSharp` | C# | boltframe 解析器的 C# 移植 | 同上 | [第三方研究] https://github.com/daveowenatl/AepSharp |
| `airbnb/lottie-web` | JS 运行时 | 消费 AE 导出的 **JSON**（不是 .aep），浏览器/移动端渲染 | 不吃 `.aep`，只吃 Bodymovin 导出的 lottie JSON | [开源代码] https://github.com/airbnb/lottie-web |

`lottie / Bodymovin` 的定位：Bodymovin 是装在 AE 里的扩展（发布渠道 aescripts + Adobe Exchange，CC 2014 起支持，装法是把 `bodymovin.zxp` 丢进 CEP 扩展目录），把 AE 动画导成 JSON；lottie-web 等运行时再把它放出来播。 [开源代码] https://github.com/airbnb/lottie-web （README "Plugin installation" 段）

一条实战口径：Bodymovin 转换时会**改写表达式**，表达式没转成功动画就会跑歪。 [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §405

---

## 2. `.aep` 与 `.aepx`（XML 工程）的关系

- AE 能把工程另存为 **XML 工程**，扩展名 `.aepx`。lottie-docs 原文："Aftereffects allows you to save the project as XML. This is basically as the RIFX but with a different container format and binary data encoded as hex." [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §2388
- 元素对照：根元素 `AfterEffectsProject` 对应 RIFX 根；`<string>` 取代 `Utf8` chunk；凡是 RIFX 里是 `LIST` 的，XML 里就是有子元素的节点；带 `bdata` 属性的元素把二进制数据 hex 编码在属性里，按 RIFX 规则解即可；`tdsn`/`fnam`/`pdnm` 在 XML 里是容器元素（与 RIFX 不同之处）。 [第三方研究] 同上 §2397–2428
- XMP 在 RIFX 里是文件尾裸挂；在 `.aepx` 里是 `ProjectXMPMetadata` 元素。 [第三方研究] 同上
- 可操作性：`.aepx` 是纯文本 XML，拿 Python `lxml` / Node `fast-xml-parser` 直接读，不需要任何第三方解析器；`actumn/aepx.js` 就是把 `.aepx` 变 JSON 的现成货（已标 Deprecated）。 [开源代码] https://github.com/actumn/aepx.js
- 工程实践：`.aepx` 适合做**模板注入**（文本级改参数再让 AE 打开），`.aep` 适合做**静态审计**（字段级、无损）。`.aepx` 体量大、AE 打开慢，量产流程仍以 `.aep` 为主。 [推断]

---

## 3. 自动化体系全景

### 3.1 ExtendScript（JSX）

语言层：ExtendScript 是 ECMA-262 第 3 版实现 + E4X（ECMA-357，直接吃 XML），带 `$` 调试对象、`File`/`Folder` 文件系统对象、`Socket`、ScriptUI。脚本扩展名必须是 `.jsx`（UTF-8），可编译成二进制 `.jsxbin`。 [官方文档] https://ae-scripting.docsforadobe.dev/introduction/overview/

出厂限制与开关：默认**禁止**脚本写文件、禁止联网；要开就在 编辑 > 首选项 > 常规 里勾 `Allow Scripts To Write Files And Access Network`。这条是量产管线的第一个坑——不勾，写日志、写渲染结果、开 socket 全被拦。 [官方文档] 同上 "Activating full scripting features"

对象模型骨架：`app`（Application）→ `app.project`（Project）→ `project.items`（ItemCollection）/ `project.renderQueue`（RenderQueue）→ Item 派生 CompItem / FolderItem / FootageItem → `compItem.layers`（LayerCollection）→ Layer 派生 AVLayer / CameraLayer / LightLayer / ShapeLayer / TextLayer / ThreeDModelLayer / ParametricMeshLayer → `layer.property(...)` 拿 PropertyGroup / Property → Property 上的关键帧方法。 [官方文档] https://ae-scripting.docsforadobe.dev/introduction/objectmodel/ ；类层级 https://ae-scripting.docsforadobe.dev/introduction/classhierarchy/

已抓到的具体能力（全部逐条对过文档）：
- 建合成：`ItemCollection.addComp(name, width, height, pixelAspect, frameRate, duration)` [官方文档] https://ae-scripting.docsforadobe.dev/item/itemcollection/
- 建图层：`LayerCollection.add()` / `addSolid()` / `addText()` / `addBoxText()` / `addVerticalText()` / `addVerticalBoxText()` / `addCamera()` / `addLight()` / `addNull()` / `addShape()` / `addParametricMesh()` / `byName()` / `precompose()` [官方文档] https://ae-scripting.docsforadobe.dev/layer/layercollection/
- 改关键帧：`Property.addKey()`、`setValueAtKey()`、`removeKey()`、`keyTime()`、`keyValue()`、`nearestKeyIndex()`、`setInterpolationTypeAtKey()`、`setTemporalEaseAtKey()`、`setSpatialTangentsAtKey()`、`setTemporalContinuousAtKey()`、`setTemporalAutoBezierAtKey()`、`setSpatialContinuousAtKey()`、`setRovingAtKey()`、`setLabelAtKey()`、`setSelectedAtKey()`、`keyInTemporalEase()` / `keyOutTemporalEase()` 等读取器；还有 `numKeys`、`selectedKeys`、`isTimeVarying`、`canVaryOverTime` [官方文档] https://ae-scripting.docsforadobe.dev/property/property/
- 表达式：`property.expression`（字符串读写）、`expressionEnabled`、`expressionError`、`canSetExpression`；工程级 `app.project.expressionEngine` [官方文档] https://ae-scripting.docsforadobe.dev/property/property/ 、 https://ae-scripting.docsforadobe.dev/general/project/
- 3D / 摄像机 / 灯光：`AVLayer.threeDLayer`、`CompItem.activeCamera`、`LayerCollection.addCamera()`、`addLight()`、`AVLayer.calculateTransformFromPoints()`、`compPointToSource()` [官方文档] https://ae-scripting.docsforadobe.dev/layer/avlayer/ 、 https://ae-scripting.docsforadobe.dev/item/compitem/
- 父子级：`Layer.parent`（读写）、`Layer.setParentWithJump()` [官方文档] https://ae-scripting.docsforadobe.dev/layer/layer/
- 轨道遮罩：`AVLayer.trackMatteLayer`、`trackMatteType`、`hasTrackMatte`、`isTrackMatte`、`setTrackMatte()`、`removeTrackMatte()` [官方文档] https://ae-scripting.docsforadobe.dev/layer/avlayer/
- 混合模式：`AVLayer.blendingMode` [官方文档] 同上
- 时间重映射：`AVLayer.timeRemapEnabled`（+ `canSetTimeRemapEnabled`） [官方文档] 同上
- 预合成嵌套：`LayerCollection.precompose()`；合成图层用 `AVLayer.source` 指到 CompItem [官方文档] https://ae-scripting.docsforadobe.dev/layer/layercollection/ 、 https://ae-scripting.docsforadobe.dev/layer/avlayer/
- 代理：`AVItem.proxySource`、`useProxy`、`setProxy(file)`、`setProxyWithSequence(file, forceAlphabetical)`、`setProxyWithSolid(...)`、`setProxyWithPlaceholder(name, w, h, fps, duration)`、`setProxyToNone()` [官方文档] https://ae-scripting.docsforadobe.dev/item/avitem/
- 渲染队列：`project.renderQueue.items.add(comp)`、`item.applyTemplate(模板名)`、`item.outputModule(1).applyTemplate(名)`、`outputModule(1).file = File`、`renderQueue.render()`（**阻塞到渲染完**）、`pauseRendering()`、`stopRendering()`、`showWindow()`、`queueInAME(bool)`（需 AME 11.0+）、`canQueueInAME`、`queueNotify` [官方文档] https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/ 、 https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/ 、 https://ae-scripting.docsforadobe.dev/renderqueue/outputmodule/ 、 https://ae-scripting.docsforadobe.dev/renderqueue/rqitemcollection/
- 应用级开关：`app.beginSuppressDialogs()` / `endSuppressDialogs(bool)`（压掉弹窗，无头跑必备）、`app.beginUndoGroup()` / `endUndoGroup()`、`app.executeCommand(id)`（走菜单命令 ID，API 没暴露的功能靠它，例：`app.executeCommand(4162)` = Convert To Bezier Path）、`app.findMenuCommandId("命令文本")`、`app.purge()`、`app.scheduleTask()`、`app.watchFolder()` / `endWatchFolder()` / `pauseWatchFolder()`、`app.setMultiFrameRenderingConfig()`、`app.availableGPUAccelTypes`（CUDA / Metal / OPENCL / SOFTWARE）、`app.disableRendering`、`app.memoryInUse`、`app.onError` 回调、`app.exitAfterLaunchAndEval`、`app.exitCode` [官方文档] https://ae-scripting.docsforadobe.dev/general/application/

**脚本摸不到的东西**（边界，逐条有据）：
- 读像素：CompItem 的完整属性/方法表里没有取像素的接口（属性只有 activeCamera/bgColor/counters/…/workAreaStart，方法只有 duplicate/exportAsMotionGraphicsTemplate/get-setMotionGraphicsControllerName/layer/openInEssentialGraphics/openInViewer）。要像素只能先渲染成 PNG/EXR 再读文件。 [官方文档] https://ae-scripting.docsforadobe.dev/item/compitem/
- `app.executeCommand` 是补洞口子，但菜单 ID 与语言包绑定，跨语言版本会错位——文档自己写着 `findMenuCommandId` 跨语言包靠不住。 [官方文档] https://ae-scripting.docsforadobe.dev/general/application/
- 渲染进度只能靠回调（`app.onError`、`RenderQueueItem.onStatusChanged`），`renderQueue.render()` 调用期间脚本线程被占住，要并发就得拆进程（见 3.4）。 [官方文档] https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/

### 3.2 CEP（Common Extensibility Platform）

- CEP 用 HTML/CSS/JS 写面板，装进 ZXP 包分发；旧 Flash/ActionScript 扩展模型已从 CC2014 起移除。 [官方文档] https://github.com/Adobe-CEP/CEP-Resources （README 首段）
- AE 与 CEP 版本对应（官方表）：AE 16 (CEP 9) → 17 (CEP 9) → 17.1.4 (CEP 10) → 18.4 (CEP 11) → **AE 25.0 (CEP 12)**。Host ID `AEFT`。 [官方文档] https://github.com/Adobe-CEP/CEP-Resources/blob/master/CEP_12.x/Documentation/CEP%2012%20HTML%20Extension%20Cookbook.md
- 清单文件：`manifest.xml`，根元素 `ExtensionManifest`，子元素 `Extensions` / `ExtensionList` / `DispatchList`，schema 5.0 起用。 [官方文档] 同上
- 与 ExtendScript 的桥：面板 JS 里 `new CSInterface().evalScript(script, callback)` → `window.__adobe_cep__.evalScript`；另有 `getHostEnvironment()`、`getSystemPath()`、`getExtensionID()`、`openURLInDefaultBrowser()`。**CEP 面板本身不改工程，所有 AE 操作都要翻译成 JSX 字符串丢给 evalScript。** [开源代码] https://raw.githubusercontent.com/Adobe-CEP/CEP-Resources/master/CEP_12.x/CSInterface.js
- Node 集成：CEP 12 内置 Node.js 17.7.1 + Node-WebKit 0.62.1（CEP 11=15.9.0，CEP 10=12.3.1，CEP 9=8.6.0）；要 Node API 得在 CEF 命令行加 `--enable-nodejs`，之后全局多一个 `cep_node` 符号。老 Node 模块跨 CEP 大版本会加载失败，得按目标版本重编。 [官方文档] https://github.com/Adobe-CEP/CEP-Resources/blob/master/CEP_12.x/Documentation/CEP%2012%20HTML%20Extension%20Cookbook.md
- 面板尺寸限制：改面板 HTML 尺寸在 Premiere Pro / Prelude / After Effects / Audition 里不生效（模态/非模态窗口可以）。 [官方文档] 同上
- 弃用时间线：CEP 12 官方 cookbook 里**没有**任何 CEP EOL 日期或停更声明——翻了全文，只有 Chromium/CSS 变更的 deprecation 提示。CEP 在 AE 25.0 仍是现行扩展体系。UXP 的替代进程存在（见 3.3），但"CEP 何时在 AE 停用"这条**没抓到官方日期**，标 [未证实]。

### 3.3 UXP

- Adobe 官方已经放了 After Effects 的 UXP API 文档仓：`AdobeDocs/uxp-after-effects`，描述 "UXP After Effects Documentation"，正文标 "**throughout the beta**"（说明处于 beta 阶段）。 [官方文档] https://github.com/AdobeDocs/uxp-after-effects
- 接入方式：`const app = require("aftereffects");`，然后直接调 `app.beginUndoGroup(...)` / `app.endUndoGroup(...)`——主机模块名就是 `aftereffects`。 [官方文档] https://github.com/AdobeDocs/uxp-after-effects/blob/main/src/pages/after-effects-api/index.md
- API 覆盖面（官方索引逐条列了 44 个 API 页）：Application、Project、ItemCollection、CompItem、AVItem/AVLayer、Layer、LayerCollection、CameraLayer、LightLayer、ShapeLayer、TextLayer、ThreeDModelLayer、ParametricMeshLayer、Property、PropertyGroup、MaskPropertyGroup、Shape、KeyframeEase、MarkerValue、TextDocument、CharacterRange、ParagraphRange、Font/Fonts、ImportOptions、FileSource/FootageSource/PlaceholderSource/SolidSource、FolderItem、GuideOptions、View/Viewer/ViewOptions、Preferences、Settings、**RenderQueue / RenderQueueItem / RQItemCollection / OMCollection / OutputModule**、DeferredCall。也就是说 UXP 版把 ExtendScript 那套对象模型基本抄了一遍，渲染队列也在里面。 [官方文档] 同上
- 与 CEP 的差别（结构层面，均为文档直读）：CEP = Chromium + Node + HTML 面板 + `evalScript` 转发 JSX；UXP = 共享 UXP 平台 API（`fs`/`os`/`uxp` 存储、HTML/CSS、Spectrum UI）+ 主机模块 `require("aftereffects")` 直调对象模型，不再需要 JSX 字符串桥。 [官方文档] 同上 + https://github.com/Adobe-CEP/CEP-Resources
- UXP 在 AE 的能力缺口：官方文档只写了 "After Effects-specific setup and development guidance will be added here by the After Effects team."（Get Started 页是空壳），并且索引里没有 ExtendScript 的 `app.executeCommand` / `app.scheduleTask` / `app.watchFolder` / `System`/`Socket` 这些条目——**菜单命令 ID 通道、Watch Folder、Socket 在 UXP AE 文档里都没出现**。起版版本号（AE 哪个版本开始支持 UXP）在可达资料里没有明确写死，标 [未证实]。 [官方文档] https://github.com/AdobeDocs/uxp-after-effects/blob/main/src/pages/get-started/index.md

### 3.4 aerender 命令行（完整参数表）

参数逐条来自实抓的 `aerender -help` 全文（AE 2019 / CC 2019 的 Windows 版输出，官方 helpx 页是它的官方出处）。 [开源代码] https://github.com/devtud/aerender （README 内嵌 `-help` 原始输出）；官方页 [官方文档] https://helpx.adobe.com/after-effects/desktop/render-and-export/automate-rendering/automated-rendering-network-rendering.html

```
-h / -help                         打印用法
-reuse                             复用已运行的 AE 实例；不给就每次新起一个实例
-project <project_path>            要打开的工程（路径或 URI）；不给就用当前已开工程
-teamproject <project_name>        打开团队工程
-comp <comp_name>                  只渲这个合成；若已在队列里且可渲，只渲第一个可渲实例；
                                   不在队列里就加进队列再渲
-rqindex <index_in_render_queue>   按队列序号渲单条
-RStemplate <render_settings_template>   套渲染设置模板（模板不存在=报错）
-OMtemplate <output_module_template>     套输出模块模板（同上）
-output <output_path>              输出目标（路径或 URI）
-log <logfile_path>                日志文件；默认 stdout
-s <start_frame>                   起始帧
-e <end_frame>                     结束帧（含）
-i <increment>                     帧步进；1=逐帧，>1 会重复渲染并拖慢但更快
-mem_usage <image_cache_percent> <max_mem_percent>   图像缓存占比、AE 可用内存占比
-v <verbose_flag>                  ERRORS 或 ERRORS_AND_PROGRESS（默认后者）
-close <close_flag>                DO_NOT_SAVE_CHANGES（默认）/ SAVE_CHANGES / DO_NOT_CLOSE
-sound <sound_flag>                ON / OFF（默认 OFF）
-version                           只打印 aerender 版本，不渲染
-continueOnMissingFootage          素材缺失不停机，缺的地方用彩条占位并写日志
```

单实例/并发行为（`-help` 原文口径）：
- 默认 **aerender 每次新起一个 AE 实例**，即使已有 AE 在跑。
- 给了 `-reuse` 才会把渲染请求丢给已在跑的实例；此时渲染完不会退出 AE，而且退出时会写回偏好设置。不带 `-reuse` 时，新起的实例渲完就退出，也**不写**偏好设置。
- 一旦用 `-comp`，`-RStemplate`/`-OMtemplate`/`-output`/`-s`/`-e`/`-i` 才生效；**不给 `-comp` 时渲整个队列，此时只有 `-project`/`-log`/`-v`/`-mem_usage`/`-close` 起作用，其余全被忽略**。
- 多实例并发：`-help` 里没有并发调度开关，多个 aerender 进程 = 多个 AE 实例，靠外部脚本/队列器（Deadline、自写 worker）并发。 [推断]

官方给的三种典型命令（原文照抄）：
```
aerender -project c:\projects\proj1.aep -comp "Comp 1" -output c:\output\proj1\proj1.avi
aerender -project c:\projects\proj1.aep
aerender -project c:\projects\proj1.aep -comp "Comp 1" -s 1 -e 10 -RStemplate "Multi-Machine Settings" -OMtemplate "Multi-Machine Sequence" -output c:\output\proj1\frames[####].psd
```

### 3.5 After Effects SDK（C++ 插件）

三种插件形态：
- **效果插件（PF_Effect）**：入口收 `PF_Cmd_*` 选择器；`PF_InData` 是宿主喂进来的上下文（`inter` 交互回调套件、`utils` 图形/数学回调、`effect_ref` 插件标识、`quality` = `PF_Quality_HI`/`PF_Quality_LO`、`version`、`serial_num`、`appl_id`（AE 里是 `FXTC`，Premiere 里是 `PrMr`）、`num_params`…），`PF_OutData` 回填。 [官方文档] https://ae-plugins.docsforadobe.dev/effect-basics/PF_InData/
- **AEGP（After Effects General Plug-in）**：直接操工程内容、挂菜单、监听消息，走一堆 `AEGP_*Suite`。最新 `AEGP_ColorSettingsSuite5`（2023-05 起）带 OCIO 调用；`AEGP_StreamSuite` 已到 v7；`AEGP_LayerSuite9` 加了 3 个 Track Matte 方法；26.5 SDK 加了 `AEGP_GuideSuite1/2`、`AEGP_ItemViewSuite2`、`AEGP_CompSuite13`（能建参数化网格层）。 [官方文档] https://ae-plugins.docsforadobe.dev/aegps/aegp-suites/ 、 https://ae-plugins.docsforadobe.dev/history/
- **AEIO**：管文件导入导出；另有 Artisans（3D 渲染器）与 Mercury Transmit（广播输出，API 在 Premiere SDK 里）。 [官方文档] https://ae-plugins.docsforadobe.dev/

GPU 入口：GPU SDK 从 **AE 16.0** 起（配 `SDK_Invert_ProcAmp` 样例）。Windows 侧要 Boost + CUDA SDK + DirectX Shader Compiler，环境变量 `CUDA_SDK_BASE_PATH` / `Boost_BASE_PATH` / `DXC_SDK_BASE_PATH`；DirectX 渲染要置位 `PF_OutFlag2_SUPPORTS_DIRECTX_RENDERING` 并同步改 PiPL，否则回落 CPU；CUDA 版本跟 AE 版本走（AE 27.0.0 = x64 CUDA 12.8 / ARM64 CUDA 13.4；AE 25.4 = CUDA 12.8），官方推荐只用 CUDA Driver API。 [官方文档] https://ae-plugins.docsforadobe.dev/intro/gpu-build-instructions/
Metal / OPENCL / CUDA / SOFTWARE 这四种出现在**渲染加速类型**枚举里（`app.availableGPUAccelTypes`、`app.project.gpuAccelType`），属于项目级渲染设置，不是效果插件的着色器入口。 [官方文档] https://ae-scripting.docsforadobe.dev/general/application/ ；插件侧 Metal/OptiX 专属入口在可达文档里没有独立章节 → [未证实]

插件包结构：Windows 插件装到 `HKLM\SOFTWARE\Adobe\After Effects\[version]\PluginInstallPath` 指向的目录，公共插件目录看 `...\CommonPluginInstallPath`；macOS 应用专属目录 `/Applications/Adobe After Effects [version]/Plug-ins/`，公共目录 `/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/`（版本号对所有 CC 锁 `7.0`）。 [官方文档] https://ae-plugins.docsforadobe.dev/intro/where-installers-should-put-plug-ins/
`.aex` 是 Windows 侧效果插件的二进制容器（带 PiPL 资源），macOS 侧是 `.plugin` bundle（`Curves.plugin/Contents/MacOS/Curves`）。 [官方文档] https://ae-plugins.docsforadobe.dev/effect-details/multi-frame-rendering-in-ae/ （文中给的 macOS 二进制路径示例）

---

## 4. 表达式引擎

- 表达式和脚本是**两套东西**，同一个 JS 语法底子：表达式只描述"这个属性等于什么"，脚本是"让应用做事"；表达式读不到脚本里的变量与函数。 [官方文档] https://ae-scripting.docsforadobe.dev/introduction/overview/
- 引擎可在两种之间切：`app.project.expressionEngine` 取值 `extendscript` 或 `javascript-1.0`（AE 16.0 / 2019 起可读可写），对应工程设置里的 Expressions Engine 下拉。这就是"老 ExtendScript 引擎"与"新 JavaScript 引擎"的开关。 [官方文档] https://ae-scripting.docsforadobe.dev/general/project/
- 表达式文本落在哪：`.aep` 里就是属性 `LIST tdbs` 内的一个 `Utf8` chunk —— 也就是说表达式是**当字符串存进工程文件**的，静态解析能把它完整抠出来。 [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §286–312
- 脚本侧对表达式的操作面：`property.expression`（读写）、`expressionEnabled`、`expressionError`（读报错）、`canSetExpression`，外带 `project.autoFixExpressions(oldText, newText)` 批量改。 [官方文档] https://ae-scripting.docsforadobe.dev/property/property/ 、 https://ae-scripting.docsforadobe.dev/general/project/
- `time` / `value` / `wiggle` 这类是表达式语言内建对象与函数（逐帧求值、以属性原值 `value` 为基准、`time` 是当前合成时间），经典用法与范例在 Dan Ebberts 的 Expressions Lab 里成套：https://motionscript.com/expressions-lab-ae65/table-of-contents.html [第三方研究]
- 表达式求值的**运行期**行为（每帧重算、依赖图层顺序、跨预合成取值）在读到的文档里没有正式规格页；能确定的是：不做表达式求值的纯解析器（py-aep/boltframe）明确把"表达式求值"列为不支持项。 [开源代码] https://github.com/forticheprod/py-aep

---

## 5. 渲染引擎与缓存体系

- **多帧渲染（MFR）**：AE 2022 及以后支持一帧多线程并发渲。插件要吃到这个加速，必须在全局 flags 置 `PF_OutFlag2_SUPPORTS_THREADED_RENDERING`，并且代码线程安全；不置位的插件会被串行化（同一时刻只允许一个线程进插件），UI 上给它挂警告图标。 [官方文档] https://ae-plugins.docsforadobe.dev/effect-details/multi-frame-rendering-in-ae/
- MFR 下选择器并发规则：UI 选择器仍在主线程，但 `PF_Cmd_SEQUENCE_SETUP/RESETUP/SETDOWN`、`SMART_PRE_RENDER`、`RENDER`、`SMART_RENDER` 会多线程并发；`PF_Cmd_GLOBAL_SETUP/GLOBAL_SETDOWN` 只在主线程。 [官方文档] 同上
- `sequence_data` 在渲染期变 `const`，统一走 `PF_EffectSequenceDataSuite` 读；非要在渲染期写就得加 `PF_OutFlag2_MUTABLE_RENDER_SEQUENCE_DATA_SLOWER`，代价是每个渲染线程各持一份副本、性能掉档。 [官方文档] 同上
- **Compute Cache**：线程安全缓存，替代/补充 sequence_data，跨线程共享已算结果，内存与其他缓存统一平衡，还支持 A/B 参数双态并存；实现是 `AEGP_ComputeCacheSuite1` + `AEGP_ComputeCacheCallbacks`（`AEGP_ClassRegister`/`AEGP_ClassUnRegister` 等），2022 起默认开。 [官方文档] https://ae-plugins.docsforadobe.dev/effect-details/compute-cache-api/
- 脚本层能摸到的 MFR 开关：`app.setMultiFrameRenderingConfig()`，AE 22.0 (2021-10) 加入，同期加了渲染队列通知 `RenderQueue.queueNotify` / `RenderQueueItem.queueItemNotify`。 [官方文档] https://ae-scripting.docsforadobe.dev/introduction/changelog/
- **代理（proxy）**：脚本可全套配代理（`setProxy` / `setProxyWithSequence` / `setProxyWithSolid` / `setProxyWithPlaceholder` / `setProxyToNone` / `useProxy`），其中"用纯色当代理"只有脚本能干，UI 做不到。 [官方文档] https://ae-scripting.docsforadobe.dev/item/avitem/
- **内存清理**：`app.purge()`、`app.setMemoryUsageLimits()`、`app.memoryInUse` 可读可调；aerender 侧对应 `-mem_usage <image_cache_percent> <max_mem_percent>`。 [官方文档] https://ae-scripting.docsforadobe.dev/general/application/ ； https://github.com/devtud/aerender
- **磁盘缓存**：AE 的磁盘缓存/媒体缓存目录在可达的官方正文里没抓到字段级说明（helpx 正文被导航截断）。脚本层的可见面是 `app.purge()` 的清理选项与首选项对象 `app.preferences`。磁盘缓存的目录布局与索引格式标 [未证实]。 [官方文档] https://ae-scripting.docsforadobe.dev/other/preferences/
- **色彩管理 / OCIO / ACES**：AE 的 OCIO 集成通过 `AEGP_ColorSettingsSuite5` 暴露（2023-05 SDK 起）——`AEGP_IsOCIOColorManagementUsed`（工程是否走 OCIO 引擎）、`AEGP_GetOCIOConfigurationFile` / `...FilePath`（读 OCIO 配置）、`AEGPD_GetOCIOWorkingColorSpace`（工作空间）、`AEGPD_GetOCIODisplayColorSpace`（Display + View 变换）。 [官方文档] https://ae-plugins.docsforadobe.dev/aegps/aegp-suites/
- 脚本层的色彩面：`project.workingSpace`、`workingGamma`、`linearizeWorkingSpace`、`linearBlending`、`bitsPerChannel`、`listColorProfiles()`、`compensateForSceneReferredProfiles`。 [官方文档] https://ae-scripting.docsforadobe.dev/general/project/
- 素材侧的 ICC 配置在 `.aep` 里落在 `LIST CLRS` 的 `Utf8`（JSON，内含 base64 的 ICC profile）。 [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §187
- 32bpc 浮点通道与 SmartFX：效果插件通过 SmartFX 扩展拿 FP 图像；像素类型 `PF_Pixel8/16/Float(PF_Pixel32)`，色彩转换走 `PF_ColorCallbacksSuite`（RGBtoHLS/HLStoRGB/RGBtoYIQ/YIQtoRGB/Luminance/Hue/Lightness/Saturation）。 [官方文档] https://ae-plugins.docsforadobe.dev/effect-details/color-space-conversion/ 、 https://ae-plugins.docsforadobe.dev/smartfx/smartfx/

---

## 6. 合成 / 图层 / 时间轴数据模型

- **合成**：`cdta` 存分辨率（含 X/Y Resolution 这两个是**渲染降采样除数**，X Resolution=5 + 宽 500 → 输出 100px）、Time Scale、Playhead、In/Out、时长、背景色、Width/Height、像素比（W/H 各 1 = 方形像素）、Framerate、快门角度/相位、Samples 上限与每帧采样数；Flags 里含 Shy、Motion Blur、Frame Blending、Preserve Framerate、Preserve Resolution。 [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §1151
- **图层类型**（`ldta.Layer Type`）：`0`=AVLayer（素材/纯色/预合成等，靠 `Source ID` 非零判定）、`1`=灯光（`ADBE Light Options Group`）、`2`=摄像机（`ADBE Camera Options Group`）、`3`=文本（`ADBE Text Properties`）、`4`=形状（`ADBE Root Vectors Group`）。 [第三方研究] 同上 §208–260
- **预合成嵌套**：合成项就是一个 `LIST Item` 里带 `cdta` + 若干 `LIST Layr`；预合成层是 type 0 图层，`Source ID` 指向那个合成项的 `idta` ID。脚本侧对应 `LayerCollection.precompose(indices, moveAllAttributes)` 与 `AVLayer.source`。 [第三方研究] 同上 §141 ； [官方文档] https://ae-scripting.docsforadobe.dev/layer/layercollection/
- **父子级（parenting）**：`ldta.Parent ID`（u32）存父层 ID；脚本侧 `Layer.parent` 读写、`Layer.setParentWithJump()` 跳变不改位置。 [第三方研究] 同上 §1202 ； [官方文档] https://ae-scripting.docsforadobe.dev/layer/layer/
- **轨道遮罩（track matte）**：AE 23 起 `ldta` 多出 `Matte Layer ID`（u32）与 `Matte Mode`（u8）；脚本侧 `trackMatteType` / `trackMatteLayer` / `setTrackMatte()` / `removeTrackMatte()`；AEGP 侧 `AEGP_LayerSuite9`（2022-10）加了 3 个 Track Matte 方法。 [第三方研究] 同上 ； [官方文档] https://ae-scripting.docsforadobe.dev/layer/avlayer/ 、 https://ae-plugins.docsforadobe.dev/history/
- **混合模式 / 时间重映射 / 调整层 / 空对象 / 引导层**：脚本侧 `blendingMode`、`timeRemapEnabled`、`adjustmentLayer`、`nullLayer`、`guideLayer`；`.aep` 侧对应 `ldta.Attributes` 里的 Adjustment(1,1)、Null(1,7)、Guide(0,1)、Visible(2,0)、3D(1,2)、Solo(1,3)。 [官方文档] https://ae-scripting.docsforadobe.dev/layer/avlayer/ 、 https://ae-scripting.docsforadobe.dev/layer/layer/ ； [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §1202
- **3D 图层 / 摄像机 / 灯光**：`AVLayer.threeDLayer` 切 2D/3D；`CompItem.activeCamera` 取当前活动摄像机；`LayerCollection.addCamera(name, centerPoint)`、`addLight(name, centerPoint)`；`.aep` 里摄像机/灯光的参数挂在 `ADBE Camera Options Group` / `ADBE Light Options Group` 的属性组下。 [官方文档] https://ae-scripting.docsforadobe.dev/layer/avlayer/ 、 https://ae-scripting.docsforadobe.dev/item/compitem/ ； [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §235–246
- **形状图层**：`LayerCollection.addShape()` 建；内容在 `ADBE Root Vectors Group` 属性组；`.aep` 里路径数据在 `shph`/`shap` chunk 族，形状层是 `LIST shap`。 [官方文档] https://ae-scripting.docsforadobe.dev/layer/layercollection/ ； [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §2014
- **参数化网格层（新增）**：`LayerCollection.addParametricMesh()`；SDK 26.5 起 `AEGP_CompSuite13` 有 `AEGP_CreateParametricMeshLayerInComp`，`AEGP_GetLayerObjectType` 可返回 `AEGP_ObjectType_3D_PARAMETRIC_MESH`。 [官方文档] https://ae-plugins.docsforadobe.dev/history/ ； https://ae-scripting.docsforadobe.dev/layer/layercollection/
- **属性与关键帧的容器规律**：属性类 chunk 一律 `td` 前缀（`tdgp` 组、`tdsb` 组 flags、`tdsn` 组名、`tdmn` 匹配名、`tdbs` 属性定义、`tdb4` 属性细节），值类是 `XXst` 父 + `XXky` 值。属性由 `tdmn`（match name，跨版本稳定）+ `tdbs`（含 `tdb4`/`cdat`/`list`/表达式 `Utf8`）组成。 [第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md §387–410、§1967

---

## 7. 落地：外部程序驱动 AE 的全部路径

四条路径，按"要不要 GUI、要不要授权、扛不扛并发"选：

### 路径 A：JSX + `afterfx.exe -r`（最轻，官方唯一命令行入口）

官方原文给的两种命令行投喂方式： [官方文档] https://ae-scripting.docsforadobe.dev/introduction/overview/

```
afterfx -r c:\script_path\example_script.jsx
afterfx.exe -r c:\myDocuments\Scripts\yourAEScriptHere.jsx
afterfx.exe -r "c:\myDocuments\Scripts\Script Name with Spaces.jsx"
afterfx.exe -s "alert("You just sent an alert to After Effects")"
```

要点：`-r` 把脚本丢给**已存在的实例**执行，不会新开一个 AE（原文："This command does not open a new instance of the After Effects application; it runs the script in the existing instance."）；`-s` 是直接跑一段脚本字符串。要拿控制台回显，Windows 上得用 `AfterFX.com`（它是命令行程序）。 [官方文档] https://ae-scripting.docsforadobe.dev/introduction/overview/ 、 https://ae-plugins.docsforadobe.dev/intro/other-integration-possibilities/

要让它跑完就退，脚本里自己置 `app.exitAfterLaunchAndEval = true`（只对 Windows 命令行生效），退出码用 `app.exitCode`（默认 0，出错自己设正值）。 [官方文档] https://ae-scripting.docsforadobe.dev/general/application/

仓库内可直接用的全流程 JSX（建工程 → 建合成 → 建层 → 打关键帧 → 进队列 → 套模板 → 设输出 → 渲染 → 退出）：

```jsx
// drive_ae.jsx —— afterfx.exe -r "C:\path\drive_ae.jsx"
app.beginSuppressDialogs();          // 无头跑，先压弹窗
app.exitAfterLaunchAndEval = true;   // Windows 命令行：跑完就退
var outDir = new Folder("C:/render_out"); if (!outDir.exists) outDir.create();

app.newProject();
var comp = app.project.items.addComp("R2_MAIN", 1920, 1080, 1, 30, 5);
var bg   = comp.layers.addSolid([0.05,0.05,0.06], "BG", 1920, 1080, 1, 5);
var txt  = comp.layers.addText("AI VIDEO STUDIO");
var tp   = txt.property("ADBE Transform Group").property("ADBE Position");
tp.setValueAtTime(0, [960, 900]);
tp.setValueAtTime(4, [960, 300]);
var cam  = comp.layers.addCamera("CAM", [960, 540]);
var lgt  = comp.layers.addLight("KEY", [960, 540]);

var rq   = app.project.renderQueue.items.add(comp);
rq.applyTemplate("Best Settings");
var om   = rq.outputModule(1);
om.applyTemplate("Lossless");                                   // 或 "PNG Sequence"
om.file  = new File("C:/render_out/R2_MAIN_[####].png");
app.project.renderQueue.render();    // 阻塞到渲完
app.exitCode = 0;
app.quit();
```

（`addComp` / `addSolid` / `addText` / `addCamera` / `addLight` / `RenderQueue.items.add` / `applyTemplate` / `OutputModule.file` / `render()` 全部经上文文档逐条核对过。）

### 路径 B：aerender（无 GUI、可并发、官方唯一批量渲染入口）

```
"C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\aerender.exe" ^
  -project "C:\proj\main.aep" -comp "R2_MAIN" ^
  -RStemplate "Best Settings" -OMtemplate "PNG Sequence" ^
  -output "C:\render_out\R2_MAIN_[####].png" ^
  -s 0 -e 120 -v ERRORS_AND_PROGRESS ^
  -log "C:\render_out\aerender.log" ^
  -continueOnMissingFootage -close DO_NOT_SAVE_CHANGES
```
`-reuse` 会把活丢给已开的 AE；不给就新起实例，渲完自退。

### 路径 C：CEP / UXP 面板（GUI 内嵌，对外部程序不友好）

CEP 面板里所有 AE 操作都要拼成 JSX 字符串走 `CSInterface.evalScript`，本质仍是路径 A，只是宿主换成面板；UXP 换成 `require("aftereffects")` 直调，但 AE 版 UXP 仍在 beta。 [开源代码] https://raw.githubusercontent.com/Adobe-CEP/CEP-Resources/master/CEP_12.x/CSInterface.js ； [官方文档] https://github.com/AdobeDocs/uxp-aftereffects… → https://github.com/AdobeDocs/uxp-after-effects

### 路径 D：静态改工程文件（不走 AE 进程）

用 `py-aep` 直接开 `.aep` 改参数、加关键帧、加输出模块、另存，再交给路径 B 渲染。这条路省掉一次 AE 启动（几秒到几十秒）和一次授权占用，是模板量产的最优解；短板是表达式不求值、渲不了图。 [开源代码] https://github.com/forticheprod/py-aep

### 推荐组合（本项目口径）

**模板 `.aep` 常驻 + `py-aep` 改参数落新 `.aep` + `aerender` 多进程渲染 + `-log` 收日志 + 失败重投**。渲染队列靠 `-RStemplate`/`-OMtemplate` 锁死，脚本层只负责改内容，不碰渲染设置——把变量面压到最小。 [推断]

---

## 8. 没抓到证据的空白（照实标）

| 待查项 | 状态 |
|---|---|
| CEP 在 AE 的正式 EOL 日期 | [未证实] — CEP 12 cookbook 全文无 EOL 声明 |
| UXP 在 AE 的起版版本号与 GA 时间 | [未证实] — 官方 UXP AE 文档正文标 beta，未写版本 |
| 插件侧 Metal / OptiX 专属 API 章节 | [未证实] — GPU 章节只覆盖 DirectX + CUDA |
| AE 磁盘缓存目录布局与索引格式 | [未证实] — 官方正文页被导航截断，脚本层只暴露 `app.purge()` |
| 表达式每帧求值的正式规格 | [未证实] — 只有"表达式≠脚本"与引擎切换两条官方口径 |
| `.aep` 里 `LIST btdk` 的语义 | [未证实] — lottie-docs 只标注"格式不同，别按 RIFF LIST 解" |

---

## 9. 25 条核心事实

1. `.aep` 是 RIFF 的 RIFX 变体：头 4 字节 `RIFX`、`uint32` 长度、格式标识 `Egg!`，整数大端。[第三方研究] https://github.com/boltframe/aftereffects-aep-parser
2. chunk = 4 字节 ASCII 标识 + `uint32` 长度 + 数据，奇数长度补 1 字节 padding。[开源代码] 同上
3. `LIST` chunk 数据体是 4 字节子类型 + 嵌套 chunk；`LIST Fold`/`Sfdr`/`Item`/`Layr`/`tdgp` 都是这种嵌套。[第三方研究] https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md
4. `idta` 定项类型：1=文件夹、4=合成、7=素材。[第三方研究] 同上
5. `cdta` 存合成全参数：分辨率、Time Scale、In/Out、时长、W/H、像素比、帧率、快门角、采样数、背景色、Shy/运动模糊/帧混合 flags。[第三方研究] 同上 §1151
6. `ldta` 存图层全参数：Layer ID、质量、Start Time、In/Out、Source ID、层名（32 字节 string0）、Matte Mode、Layer Type、Parent ID，AE≥23 还有 Matte Layer ID。[第三方研究] 同上 §1202
7. 图层类型码：0=AVLayer、1=灯光、2=摄像机、3=文本、4=形状。[第三方研究] 同上 §208
8. 时间值 `uint16` 按 `cdta.time_scale` 缩放；层内还要加 `ldta.start_time`。[第三方研究] 同上 §71
9. 关键帧公共头含 Time、Ease Mode（1=Linear/2=Ease/3=Hold）、Label、Flags；多维关键帧体是 float64[n] 的 Value/In-Speed/In-Influence/Out-Speed/Out-Influence。[第三方研究] 同上 §1421
10. `head` 里的 File Revision 每次保存 +2，前 6 字节带 AE 版本指纹。[第三方研究] 同上 §1622
11. RIFX 数据之后挂一段 XMP（XML），记 AE 版本与创建/修改时间。[第三方研究] 同上 §2379
12. AE 能把工程另存为 XML 工程 `.aepx`：结构同 RIFX、`<string>` 取代 `Utf8`、`bdata` 属性里是 hex 编码的二进制。[第三方研究] 同上 §2388
13. `boltframe/aftereffects-aep-parser`（Go，132★）静态解析 `.aep`，仓库自带 Kaitai 定义与样本 `.aep`。[开源代码] https://github.com/boltframe/aftereffects-aep-parser
14. `forticheprod/py-aep`（Python，87★）能读写 `.aep`：建工程、建层、加删关键帧、改 ExtendScript 摸不到的渐变/渲染设置/输出模块设置；不支持表达式求值与图像渲染。[开源代码] https://github.com/forticheprod/py-aep
15. `Jam3/ae-to-json` 走的是"活 AE 里的 JSX 导 JSON"，不是静态解析；`actumn/aepx.js` 解 `.aepx` 且已标 Deprecated。[开源代码] https://github.com/Jam3/ae-to-json 、 https://github.com/actumn/aepx.js
16. Bodymovin 是 AE 内的 CEP 扩展，把动画导成 JSON，lottie-web 负责播放；Bodymovin 转换时会改写表达式。[开源代码] https://github.com/airbnb/lottie-web
17. ExtendScript = ECMA-262 3rd + E4X，脚本必须 `.jsx`（UTF-8），可编 `.jsxbin`；默认禁写文件禁联网，要开首选项开关。[官方文档] https://ae-scripting.docsforadobe.dev/introduction/overview/
18. `afterfx.exe -r <jsx>` 把脚本丢给已运行实例执行，不新开实例；`-s` 直接跑字符串；Windows 拿回显要用 `AfterFX.com`。[官方文档] 同上
19. 脚本跑完自退靠 `app.exitAfterLaunchAndEval = true`，退出码靠 `app.exitCode`。[官方文档] https://ae-scripting.docsforadobe.dev/general/application/
20. 脚本能建合成（`items.addComp`）、建各类层（`addSolid/addText/addShape/addCamera/addLight/addNull/addParametricMesh/precompose`）、增删改关键帧、设父子级、切 3D、设轨道遮罩与混合模式、加队列并触发 `renderQueue.render()`（阻塞到渲完）。[官方文档] https://ae-scripting.docsforadobe.dev/item/itemcollection/ 、 https://ae-scripting.docsforadobe.dev/layer/layercollection/ 、 https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/
21. 脚本读不到像素：CompItem 的属性/方法表里没有取像素接口，要像素先渲染成 PNG/EXR 再读文件。[官方文档] https://ae-scripting.docsforadobe.dev/item/compitem/
22. aerender 关键参数：`-project -comp -rqindex -RStemplate -OMtemplate -output -log -s -e -i -mem_usage -v -close -sound -reuse -teamproject -continueOnMissingFootage -version`；不给 `-comp` 渲整队列时，`-RStemplate/-OMtemplate/-output/-s/-e/-i` 全被忽略。[开源代码] https://github.com/devtud/aerender
23. aerender 默认每次新起 AE 实例、渲完自退且不写偏好；加 `-reuse` 才复用已开实例、渲完不退、退出时写偏好。[开源代码] 同上
24. MFR 自 AE 2022 起：插件需置 `PF_OutFlag2_SUPPORTS_THREADED_RENDERING` 且线程安全，否则被串行化；渲染期 `sequence_data` 变 const，写要靠 `PF_OutFlag2_MUTABLE_RENDER_SEQUENCE_DATA_SLOWER` 或 Compute Cache；脚本侧开关是 `app.setMultiFrameRenderingConfig()`（AE 22.0 起）。[官方文档] https://ae-plugins.docsforadobe.dev/effect-details/multi-frame-rendering-in-ae/ 、 https://ae-scripting.docsforadobe.dev/introduction/changelog/
25. OCIO 走 `AEGP_ColorSettingsSuite5`（2023-05 SDK 起）：`AEGP_IsOCIOColorManagementUsed`、`AEGP_GetOCIOConfigurationFile/Path`、`AEGPD_GetOCIOWorkingColorSpace`、`AEGPD_GetOCIODisplayColorSpace`；插件 GPU 从 SDK 16.0 起，DirectX 要 `PF_OutFlag2_SUPPORTS_DIRECTX_RENDERING`，CUDA 版本随 AE（AE 27.0.0 = x64 CUDA 12.8 / ARM64 CUDA 13.4）。[官方文档] https://ae-plugins.docsforadobe.dev/aegps/aegp-suites/ 、 https://ae-plugins.docsforadobe.dev/intro/gpu-build-instructions/

补充两条（自动化体系版本账）：
- AE 与 CEP 对应：AE 16/17→CEP 9、17.1.4→CEP 10、18.4→CEP 11、AE 25.0→CEP 12；CEP 12 内置 Node 17.7.1 + Node-WebKit 0.62.1，Node API 要 `--enable-nodejs`。[官方文档] https://github.com/Adobe-CEP/CEP-Resources
- AE 的 UXP 官方 API 文档已发布（`require("aftereffects")`，44 个 API 页，含 RenderQueue/OutputModule），正文标 beta；起版版本号与 CEP 的 EOL 日期在可达资料里都没有。[官方文档] https://github.com/AdobeDocs/uxp-after-effects