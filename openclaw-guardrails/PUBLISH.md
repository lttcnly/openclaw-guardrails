# ClawHub 发布指南

本指南教你如何将 OpenClaw Guardrails 发布到 ClawHub 技能市场。

---

## 方法一：手动上传（推荐，当前最可靠）

### 步骤 1: 登录 ClawHub

1. 打开浏览器访问：https://clawhub.ai/upload
2. 点击 "Sign in with GitHub"
3. 使用你的 GitHub 账号登录

### 步骤 2: 准备发布文件

确保你的技能文件夹包含以下必要文件：

```
openclaw-guardrails/
├── SKILL.md              # 必需 - ClawHub 技能描述
├── README.md             # 必需 - 使用说明
├── LICENSE               # 必需 - 开源许可证
├── scripts/              # 必需 - 脚本目录
│   ├── run_daily.py
│   ├── risk_score.py
│   └── ... (其他脚本)
└── reports/              # 可选 - 运行时生成（.gitignore）
```

### 步骤 3: 上传技能

1. 在 https://clawhub.ai/upload 页面点击 "Choose Folder" 或拖拽文件夹
2. 选择 `~/.openclaw/skills/openclaw-guardrails` 文件夹
3. 填写发布信息：

| 字段 | 填写内容 |
|------|----------|
| **Slug** | `openclaw-guardrails` |
| **Name** | `OpenClaw Guardrails` |
| **Version** | `1.0.0` |
| **Tags** | `latest,security,monitoring,openclaw,guardrails` |
| **Changelog** | `Initial release: Silent security monitoring for OpenClaw with risk scoring, auto-fix, threat intel, compliance checks.` |

4. 点击 "Publish" 按钮

### 步骤 4: 验证发布

1. 访问 https://clawhub.ai/skills/openclaw-guardrails
2. 检查技能信息是否正确
3. 测试安装命令：
   ```bash
   clawhub install openclaw-guardrails
   ```

---

## 方法二：CLI 发布（当前有 bug，不推荐）

> ⚠️ **注意**: ClawHub CLI v0.7.0 存在 bug (`acceptLicenseTerms: invalid value`)，暂时无法使用。

### 如果 CLI 已修复：

```bash
# 1. 登录 ClawHub
clawhub login

# 2. 验证登录
clawhub whoami

# 3. 发布技能
cd ~/.openclaw/skills/openclaw-guardrails
clawhub publish . \
  --slug openclaw-guardrails \
  --name "OpenClaw Guardrails" \
  --version "1.0.0" \
  --changelog "Silent security monitoring with risk scoring, auto-fix, threat intel, compliance checks" \
  --tags "latest,security,monitoring,openclaw"
```

---

## SKILL.md 说明

`SKILL.md` 是 ClawHub 识别技能的关键文件，必须包含：

```markdown
---
name: openclaw-guardrails
description: Silent security monitoring for OpenClaw deployments. Daily scans, risk scoring (0-100), auto-fix, threat intel, compliance checks.
metadata:
  {
    "clawdbot":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["openclaw", "python3"] },
        "os": ["linux", "darwin", "win32"],
      },
  }
---

# OpenClaw Guardrails

详细说明...
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 技能 slug | `openclaw-guardrails` |
| `description` | 简短描述（<200 字符） | `Silent security monitoring...` |
| `metadata.clawdbot.emoji` | 图标 emoji | `🛡️` |
| `metadata.clawdbot.requires.bins` | 依赖的二进制文件 | `["openclaw", "python3"]` |
| `metadata.clawdbot.os` | 支持的操作系统 | `["linux", "darwin", "win32"]` |

---

## 版本更新

### 更新现有技能

1. 修改 `SKILL.md` 中的版本号
2. 更新 changelog
3. 重新上传到 ClawHub

### 语义化版本规范

```
主版本号。次版本号。修订号
  ↑      ↑      ↑
  |      |      └─ 向后兼容的问题修正
  |      └─ 向后兼容的功能新增
  └─ 不兼容的 API 修改

示例：
1.0.0  # 初始发布
1.0.1  # Bug 修复
1.1.0  # 新功能
2.0.0  # 不兼容变更
```

---

## 常见问题

### Q: 上传失败 "No files found"
**A**: 确保文件夹包含 `SKILL.md` 文件，且没有 `.clawhubignore` 排除所有文件。

### Q: 上传失败 "acceptLicenseTerms: invalid value"
**A**: ClawHub CLI bug，请使用手动上传方式。

### Q: 如何删除已发布的技能？
**A**: 联系 ClawHub 管理员或在技能页面点击 "Delete"（如果开放）。

### Q: 如何查看技能的下载量/安装量？
**A**: 登录 ClawHub 后访问技能管理页面查看统计数据。

---

## 发布前检查清单

- [ ] `SKILL.md` 包含正确的元数据
- [ ] `README.md` 包含完整使用说明
- [ ] `LICENSE` 文件存在
- [ ] 所有脚本都能正常运行
- [ ] 已在本地测试过安装流程
- [ ] 版本号符合语义化规范
- [ ] Changelog 描述了本次变更

---

## 发布后

1. **更新 GitHub Release**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **通知用户**
   - GitHub Issues
   - Discord/社区
   - 更新文档

3. **监控反馈**
   - 查看 ClawHub 评论
   - 处理 GitHub Issues
   - 收集改进建议

---

**🎉 发布完成！感谢你的贡献！**
