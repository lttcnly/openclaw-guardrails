# OpenClaw Guardrails 🛡️

**企业级 OpenClaw 安全防护系统** - 静默监控、自动修复、合规检查

[![GitHub stars](https://img.shields.io/github/stars/lttcnly/openclaw-guardrails)](https://github.com/lttcnly/openclaw-guardrails/stargazers)
[![License](https://img.shields.io/github/license/lttcnly/openclaw-guardrails)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue)](https://github.com/lttcnly/openclaw-guardrails)

---

## 🌟 核心优势

| 优势 | 说明 |
|------|------|
| 🤫 **静默监控** | 平时不打扰，只在发现高危风险时推送告警 |
| 🤖 **自动修复** | 对低风险问题自动修复（如配置漂移、依赖升级） |
| 📊 **风险评分** | 0-100 分直观展示安全状态（红黄绿灯） |
| 🔍 **威胁情报** | 集成 OSV + NVD + GitHub 三大漏洞库 |
| 📋 **合规检查** | 等保 2.0 / CIS Benchmarks 自动检查 |
| 🚀 **性能优化** | 增量扫描，只扫描变化的文件 |
| 🧹 **自动清理** | 自动清理过期报告，避免磁盘爆炸 |
| 🌐 **跨平台** | macOS / Linux / Windows 一键安装 |

---

## 🚀 快速开始

### 一键安装（推荐）

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/lttcnly/openclaw-guardrails/main/install.ps1 | Invoke-Expression
```

**手动安装:**
```bash
# 1. Clone 到 OpenClaw skills 目录
git clone https://github.com/lttcnly/openclaw-guardrails.git ~/.openclaw/skills/openclaw-guardrails

# 2. 运行一次验证
cd ~/.openclaw/skills/openclaw-guardrails
python3 scripts/run_daily.py

# 3. 创建每日定时任务（可选）
openclaw cron add --name guardrails:daily \
  --cron "17 3 * * *" \
  --session isolated \
  --light-context \
  --no-deliver \
  --message "Daily guardrails: exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py"
```

---

## 📋 功能清单

### 每日自动执行
| 功能 | 脚本 | 说明 |
|------|------|------|
| 🔍 风险评分 | `risk_score.py` | 0-100 分，含修复建议 |
| 📡 威胁情报 | `threat_intel.py` | OSV + NVD + GitHub 三数据源 |
| 📊 配置漂移 | `config_drift.py` | 检测不安全配置变更 |
| 🔧 自动修复 | `auto_fix.py` | 自动修复低风险问题 |
| 🎨 HTML 看板 | `html_dashboard.py` | 交互式仪表盘 |
| 🧹 报告清理 | `cleanup_reports.py` | 自动删除过期报告 |
| 🔄 增量扫描 | `incremental_scan.py` | 只扫描变化的文件 |

### 每周执行（周日）
| 功能 | 脚本 | 说明 |
|------|------|------|
| 🎯 技能审计 | `skills_audit.py` | 检测技能更新和新风险 |
| 📋 合规检查 | `compliance_check.py` | 等保 2.0 / CIS 检查 |

### 每月执行（1 号）
| 功能 | 脚本 | 说明 |
|------|------|------|
| 📈 趋势分析 | `trend_analysis.py` | 月度风险趋势报告 |

### 按需执行
| 功能 | 脚本 | 说明 |
|------|------|------|
| 🚫 安装前扫描 | `preinstall_scan.py` | 拦截高危技能安装 |

---

## 📊 风险评分说明

| 分数 | 等级 | 颜色 | 说明 |
|------|------|------|------|
| 80-100 | LOW | 🟢 | 安全状态良好 |
| 60-79 | MEDIUM | 🟡 | 存在中等风险 |
| 40-59 | HIGH | 🟠 | 存在高风险 |
| 0-39 | CRITICAL | 🔴 | 严重风险，需立即处理 |

**扣分规则:**
- 每个 critical 发现：-20 分（最多 -60）
- 每个 warn 发现：-5 分（最多 -20）
- 每个 HIGH 技能标记：-10 分（最多 -20）
- 每个高危漏洞：-10 分（最多 -20）

---

## 🛠️ 使用指南

### 查看风险评分
```bash
cat ~/.openclaw/skills/openclaw-guardrails/reports/summary-*.md
```

### 打开 HTML 看板
```bash
# macOS
open ~/.openclaw/skills/openclaw-guardrails/reports/dashboard-*.html

# Linux
xdg-open ~/.openclaw/skills/openclaw-guardrails/reports/dashboard-*.html

# Windows
start $env:USERPROFILE\.openclaw\skills\openclaw-guardrails\reports\dashboard-*.html
```

### 手动运行扫描
```bash
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py
```

### 安装前扫描技能
```bash
# 扫描要安装的技能文件夹
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/preinstall_scan.py /path/to/skill-folder

# 退出码：
# 0 = 安全，可以安装
# 1 = 警告，建议审查
# 2 = 高危，禁止安装
```

### 自动修复（模拟模式）
```bash
# 默认只模拟，不实际执行
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/auto_fix.py

# 实际执行修复（会修改系统配置）
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/auto_fix.py --execute
```

### 查看合规报告
```bash
cat ~/.openclaw/skills/openclaw-guardrails/reports/compliance-*.md
```

---

## 📁 报告文件说明

所有报告保存在 `~/.openclaw/skills/openclaw-guardrails/reports/`

| 文件 | 说明 | 保留期 |
|------|------|--------|
| `summary-*.md` | 风险评分摘要 | 7 天 |
| `risk-score-*.json` | 风险评分详情 | 7 天 |
| `threat-intel-*.json` | 威胁情报报告 | 7 天 |
| `config-drift-*.json` | 配置漂移报告 | 7 天 |
| `auto-fix-*.json` | 自动修复报告 | 7 天 |
| `compliance-*.md` | 合规检查报告 | 30 天 |
| `skills-audit-*.md` | 技能审计报告 | 30 天 |
| `trend-*.json` | 月度趋势数据 | 12 个月 |
| `dashboard-*.html` | HTML 看板 | 仅最新 1 个 |

---

## 🔧 配置说明

### 自定义风险基线

编辑 `~/.openclaw/skills/openclaw-guardrails/scripts/risk_score.py` 中的 `SECURE_BASELINE`:

```python
SECURE_BASELINE = {
    "groupPolicy": "allowlist",  # 期望的安全值
    "sandbox.mode": "all",
    "tools.fs.workspaceOnly": True,
    "gateway.bind": "loopback",
}
```

### 自定义告警渠道

编辑 `~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py` 中的告警逻辑，支持：
- OpenClaw 主会话（默认）
- 飞书 webhook
- 钉钉 webhook
- 邮件（SMTP）
- 短信（阿里云 SMS）

---

## 🛡️ 安全边界

### 自动执行（无需确认）
- ✅ 依赖升级（`npm update`, `pip install --upgrade`）
- ✅ 恢复已知安全配置

### 需要确认
- ⚠️ 卸载技能
- ⚠️ 修改核心配置（gateway bind 等）
- ⚠️ 系统级软件升级

### 禁止自动
- ❌ 下载执行外部脚本
- ❌ 修改防火墙/网络配置
- ❌ 安装未经验证的补丁

---

## 📈 性能影响

| 指标 | 数值 |
|------|------|
| 每日扫描时间 | 30-60 秒 |
| 增量扫描时间 | 5-10 秒 |
| 内存占用 | < 50MB |
| 磁盘占用 | ~100MB（含报告） |
| CPU 占用 | < 5%（扫描时） |

---

## 🐛 故障排查

### 报告不生成
```bash
# 检查 Python 版本
python3 --version  # 需要 3.10+

# 手动运行一次
python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py
```

### 告警不推送
```bash
# 检查 cron 任务
openclaw cron list | grep guardrails

# 查看 cron 执行历史
openclaw cron runs --id <job-id>
```

### 风险评分异常
```bash
# 查看详细扣分项
cat ~/.openclaw/skills/openclaw-guardrails/reports/risk-score-*.json | jq .breakdown
```

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [OpenClaw](https://openclaw.ai) - 强大的 AI 代理框架
- [OSV.dev](https://osv.dev) - Google 维护的开源漏洞库
- [NVD](https://nvd.nist.gov) - 美国国家漏洞数据库
- [GitHub Advisories](https://github.com/advisories) - GitHub 安全公告

---

## 📞 联系方式

- GitHub Issues: https://github.com/lttcnly/openclaw-guardrails/issues
- Email: lttcnly@gmail.com

---

**🛡️ 让 OpenClaw 更安全，从 Guardrails 开始！**
