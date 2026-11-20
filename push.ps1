# 一键推送到 GitHub
# 用法（在 repo 目录里执行）：
#   .\push.ps1 -User 你的GitHub用户名 -Repo ai-video-studio-research -Token ghp_xxx
# 或者已装 gh 并登录：
#   .\push.ps1 -UseGh -Repo ai-video-studio-research
param(
    [string]$User,
    [string]$Repo = "ai-video-studio-research",
    [string]$Token,
    [switch]$UseGh,
    [switch]$Private
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".git")) {
    git init -b main | Out-Null
    git config user.name  "AI Video Studio"
    git config user.email "research@localhost"
}

git add -A
$staged = (git diff --cached --name-only | Measure-Object).Count
if ($staged -gt 0) {
    git commit -m "docs: AI Video Studio 技术底座研究（剪映/达芬奇/AE 逆向 + AVS 格式 + 架构与路线图）" | Out-Null
    Write-Host "已提交 $staged 个文件"
} else {
    Write-Host "无新改动，跳过提交"
}

if ($UseGh) {
    $exists = gh repo view "$User/$Repo" 2>$null
    if (-not $exists) {
        $vis = if ($Private) { "--private" } else { "--public" }
        gh repo create "$User/$Repo" $vis --source . --remote origin --push
        Write-Host "已创建并推送：https://github.com/$User/$Repo"
        exit 0
    }
    git remote remove origin 2>$null
    git remote add origin "https://github.com/$User/$Repo.git"
    git push -u origin main
    exit 0
}

if (-not $User -or -not $Token) {
    throw "需要 -User 与 -Token（GitHub Personal Access Token，勾选 repo 权限），或改用 -UseGh"
}

$remote = "https://$User`:$Token@github.com/$User/$Repo.git"
git remote remove origin 2>$null
git remote add origin $remote

# 仓库不存在时用 API 建（私有/公开按 -Private）
$headers = @{ Authorization = "Bearer $Token"; "User-Agent" = "ai-video-studio"; Accept = "application/vnd.github+json" }
try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$User/$Repo" -Headers $headers -Method Get | Out-Null
    Write-Host "仓库已存在，直接推送"
} catch {
    $body = @{ name = $Repo; private = [bool]$Private; description = "AI Video Studio 技术底座研究：剪映/达芬奇/AE 逆向、AVS 工程格式、架构与路线图" } | ConvertTo-Json
    Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json" | Out-Null
    Write-Host "已创建仓库 $User/$Repo"
}

git push -u origin main
git remote set-url origin "https://github.com/$User/$Repo.git"
Write-Host "推送完成：https://github.com/$User/$Repo"