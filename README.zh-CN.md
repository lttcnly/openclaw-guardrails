# 🛡️ OpenClaw Guardrails

[![OpenClaw](https://img.shields.io/badge/生态-OpenClaw-blueviolet)](https://github.com/google/gemini-cli)
[![License](https://img.shields.io/badge/协议-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/版本-1.1.0-blue)](SKILL.md)

**OpenClaw 的“免疫系统”。**  
OpenClaw Guardrails 为你的 AI 代理部署提供无感、企业级的安全监控、风险评分及自愈能力。

---

## 🚀 极速上手 (AI 原生指令)

如果你正在使用 **OpenClaw**，无需手动克隆或配置。直接对你的 Agent 说：

> **“帮我的项目安装好 GitHub 开源项目 `lttcnly/openclaw-guardrails`，并按要求进行配置。”**

或者直接在终端运行一键安装指令：
```bash
# 一键安装并建立安全基线
openclaw skill install https://github.com/lttcnly/openclaw-guardrails --auto-setup
```

---

## ✨ 为什么选择 Guardrails?

在 AI 驱动的时代，Agent 拥有极高的执行权限。Guardrails 确保它们在安全边界内运行，且不增加任何日常干扰。

*   **⚡ 高性能并行引擎**: 并行执行官方审计、供应链扫描与漏洞分析，速度飞快。
*   **🧠 动态风险评分**: 实时 0-100 分量化安全态势，根据内置 `guardrails.yaml` 策略精细化计算。
*   **🩹 配置自愈 (Self-Healing)**: 自动检测并修复不安全的配置（如不当的权限放开），自带时间戳备份。
*   **🔍 零信任供应链**: 静态分析第三方 Skill 依赖，识别恶意代码、后门及敏感信息泄露。
*   **📋 合规性对标**: 预置 **等保 2.0 (MLPS)** 及 CIS 基准检查项。

---

## 📊 功能一览

| 维度 | 功能 | 价值 |
| :--- | :--- | :--- |
| **身份安全** | 凭据泄露监控 | 防止 API Key、Token 在日志或对话中意外暴露。 |
| **系统安全** | 配置漂移监控 | 当 Skill 或用户修改了关键系统设置时立即感知。 |
| **供应链** | 哈希锁定与校验 | 确保你的 Skills 代码未被非法篡改。 |
| **网络审计** | 端口与代理检查 | 发现非法的外部连接或未经授权的内网穿透。 |
| **决策分析** | 趋势可视化大屏 | 自动生成包含 10 天风险趋势的交互式 HTML 报告。 |

---

## 🛠️ 进阶使用

### 开启每日“免疫扫描”
一次配置，终身守护。Guardrails 将在后台静默运行，仅在发现 **CRITICAL (致命)** 风险时才会通过 OpenClaw 主会话推送通知。

```bash
openclaw cron add --name guardrails:daily \
  --cron "17 3 * * *" \
  --session isolated \
  --message "exec python3 ~/.openclaw/skills/openclaw-guardrails/scripts/run_daily.py"
```

### 查看交互式看板
```bash
# 在浏览器中打开生成的安全报告
open .openclaw/skills/openclaw-guardrails/reports/dashboard.html
```

---

## 🤝 参与贡献

我们欢迎安全研究员和 OpenClaw 爱好者！欢迎通过以下方式贡献：
1.  在 `guardrails.yaml` 中提交新的**安全策略**。
2.  优化**风险评分**权重算法。
3.  针对常见漏洞添加**自动修复 (Auto-fix)** 脚本。

---

**🛡️ 让你的 AI 代理无坚不摧。Trust, but verify.**
