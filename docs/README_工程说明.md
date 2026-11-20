# AI Video Studio 工程参考

建库时间：2026-11-20
位置：`C:\AI Video Studio工程参考`

本目录所有软件与本机已装软件隔离：数据目录重定向到本工程目录，不写系统注册表、不建全局快捷方式、不碰本机程序。本机原剪映 11.6.0.14552 保持原样。

---

## 1. 剪映专业版 11.7.0.14652 — 已隔离安装完成 ✅

- 官方安装包：`JianyingPro_11.7.0.14652_Windows_x64.exe`（932,125,528 字节）
  - SHA256：`B2597B52BCE9142ECFEF4E08DB39DB74EF5AA2C782D1F67B730D109CAD41CAF1`
- 隔离版目录：`剪映专业版_11.7.0.14652_隔离版\JYPacket\11.7.0.14652\`
- 主程序：`...\JYPacket\11.7.0.14652\JianyingPro.exe`
- 启动：双击 `剪映专业版_11.7.0.14652_隔离版\启动剪映_隔离版.bat`
- 隔离原理：从官方安装包内嵌 7z 流直接解包（绕过安装器写注册表/快捷方式），5615 个文件、3.2GB。启动器把 LOCALAPPDATA / APPDATA / USERPROFILE / TEMP 全部重定向到隔离目录内，草稿和配置不写进本机 `C:\Users\<user>\AppData\Local\JianyingPro`。

## 2. DaVinci Resolve 21.2 — 已隔离安装完成 ✅

- 官方版本：DaVinci Resolve 21.2 Update（build 6，2026-11-04 发布）
- 官方 ZIP：`DaVinci_Resolve_21.2_Windows.zip`（3,761,931,072 字节）
  - SHA256：`805FC04B526B74DB54F21EF1CB58F21314BAA5E0DCA517CDF989B076481AD364`
  - 官方签名 CDN 直链存于 `resolve_url.txt`
- 隔离版目录：`DaVinci_Resolve_21.2_隔离版\Resolve_21.2_程序\Blackmagic Design\DaVinci Resolve\`
- 主程序：`...\DaVinci Resolve\Resolve.exe`
- 启动：双击 `DaVinci_Resolve_21.2_隔离版\启动Resolve_隔离版.bat`
- 隔离原理：ZIP 内是 7-Zip SFX 安装器，解出 `ResolveInstaller.msi` 后用 `msiexec /a`（管理安装模式）展开到工程目录，不执行真实安装、不写系统注册表和 ProgramData。启动器重定向数据目录。

## 3. After Effects 27.0（2026 年 11 月版）— 官方账号步骤待完成

- 官方版本：After Effects 27.0，Adobe 2026-11 发行说明确认：https://helpx.adobe.com/tw/after-effects/release-note/release-notes-effects-cc.html
- Adobe 不提供 After Effects 免登录独立离线 exe，官方渠道是 Creative Cloud 桌面应用登录账号下载。本机网络访问 adobe.com 返回 403，这一步只能在浏览器里登录 Adobe 账号完成。
- 已准备：`AfterEffects_27.0_安装引导.bat` — 打开官方下载页，登录后把安装路径指向 `C:\AI Video Studio工程参考\AfterEffects_27.0` 即实现隔离。
- 官方 CC 直连帮助页：https://helpx.adobe.com/download-install/apps/download-install-apps/creative-cloud-apps/download-creative-cloud-desktop-app-using-direct-links.html
- 需要您操作的部分：Adobe 账号登录（只有您有）+ 安装路径选工程目录。剩下的隔离配置脚本已备好。
