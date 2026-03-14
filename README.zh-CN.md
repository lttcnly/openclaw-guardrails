# 🛡️ OpenClaw Guardrails

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</p>

[![OpenClaw](https://img.shields.io/badge/生态-OpenClaw-blueviolet)](https://github.com/google/gemini-cli)
[![License](https://img.shields.io/badge/协议-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/版本-1.1.0-blue)](SKILL.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-欢迎-brightgreen.svg)](https://github.com/lttcnly/openclaw-guardrails/pulls)

**AI 代理的终极“免疫系统”。**  
OpenClaw Guardrails 是一套专为 OpenClaw 量身打造的企业级安全编排套件。它将传统静默的审计转化为主动的防御盾牌，确保你的 AI 部署安全、合规且透明。

---

## 🚀 一键智能安装 (AI 原生指令)

如果你正在运行 **OpenClaw**，只需一句话即可完成全套防御体系的部署。请对你的 Agent 说：

> **“帮我安装 GitHub 项目 `lttcnly/openclaw-guardrails`。安装完成后，请初始化安全基线，配置每日自动扫描任务，并展示第一次的安全审计报告。”**

*这条指令将触发 Agent 自动完成：克隆仓库、运行 `install.py` 初始化、配置 Cron 定时任务并执行首次全量审计。*

---

## 💎 为什么每个 OpenClaw 用户都需要 Guardrails？

1.  **Trust, But Verify (信任但验证)**：AI 代理拥有强大的工具权限（如 Shell、文件访问）。Guardrails 确保没有任何 Skill 或提示词注入能悄无声息地提权。
2.  **零成本合规**：满足 **等保 2.0 (MLPS)** 或 **CIS** 安全标准通常非常痛苦。Guardrails 将 90% 的检查项自动化。
3.  **零噪音监控**：不同于传统的冗长日志，Guardrails 采用**智能告警去重**。只有当安全状态真正发生改变或出现风险时，它才会通过主会话提醒你。
4.  **全局资产可见性**：你知道你安装的几十个 Skill 到底引入了哪些第三方依赖吗？Guardrails 的 **SBOM 引擎**能精准告诉你。

---

## 🔥 核心能力深度解析

### 🛡️ 第一层：主动防御与自愈 (Active Defense)
*   **自动化修复 (`auto_fix.py`)**：检测不安全的 `groupPolicy="open"` 配置或未授权的 Shell 暴露，并自动恢复到安全状态，同时保留带时间戳的备份。
*   **完整性保护 (`hash_pin.py/verify.py`)**：为所有 Skill 生成加密签名的哈希基线。一旦 Skill 代码被篡改（如遭受供应链攻击），将立即触发锁定报警。

### 🔍 第二层：深度检测引擎 (Deep Inspection)
*   **系统加固审计 (`audit.py`)**：扫描操作系统层面的异常监听端口、防火墙错误配置，以及 Agent 使用的非标代理通道。
*   **零信任 Skill 扫描 (`skills_scan.py`)**：对每个安装的 Skill 进行静态分析，识别潜在的凭据泄露、硬编码密钥及可疑的 API 调用模式。
*   **依赖漏洞扫描 (`vuln_scan.py`)**：自动对比所有 Skill 的 `package.json` 和 `requirements.txt` 与全球漏洞库 (NVD/CVE)，发现过时的不安全依赖。

### 📋 第三层：企业合规与治理 (Governance)
*   **SBOM (软件物料清单) (`sbom.py`)**：为 AI 环境生成完整的组件清单。面对类似 "Log4j" 的零日漏洞，能瞬间定位受影响的 Skill。
*   **配置漂移监控 (`config_drift.py`)**：实时追踪 `openclaw.json` 的每一次变动。清晰记录“谁”在“何时”修改了“什么”。
*   **等保 2.0 合规检查 (`compliance_check.py`)**：针对国内网络安全等级保护标准量身定制，让你的 AI 部署随时“准备好审计”。

### 📊 第四层：情报与可视化 (Intelligence)
*   **动态风险评分 (`risk_score.py`)**：基于加权算法的 0-100 分系统，将复杂的安全指标转化为直观的单一数字。
*   **交互式看板 (`html_dashboard.py`)**：生成精美的响应式 HTML 报告，包含 **10 天风险趋势图**，助你掌控安全态势的长期演变。
*   **威胁情报集成 (`threat_intel.py`)**：将本地发现与全球威胁情报库关联，识别新兴的攻击模式。

---

## 🛠️ 技术亮点与性能设计
*   **并行执行引擎**：利用 Python 多进程技术，所有扫描任务并行运行，几秒钟内即可完成全量审计。
*   **增量扫描技术**：智能识别自上次扫描以来的变动，仅扫描受影响部分，极大降低 CPU 和 IO 消耗。
*   **敏感信息脱敏**：所有报告在保存至 `reports/` 目录前，都会自动对敏感信息（如 Token、个人隐私）进行脱敏处理。
*   **自动化生命周期**：`cleanup_reports.py` 自动清理历史冗余报告，确保磁盘空间不被占用。

---

## 📖 路线图 (Roadmap)
- [x] 并行扫描引擎 (v1.1)
- [x] 风险评分与 HTML 看板
- [x] 自动化修复 (Auto-fix)
- [ ] **多端同步**：在多个 OpenClaw 节点间同步安全基线。
- [ ] **基于 ML 的异常检测**：利用本地模型识别异常的提示词模式。
- [ ] **多渠道告警**：集成 Slack/Discord/Telegram 实时风险推送。

---

## 🤝 社区与支持

加入我们，共同打造最安全的 AI 运行环境。
- **提交 Bug**：如果你发现了绕过机制，请提交 Issue。
- **功能建议**：有特定的合规检查需求？请告诉我们。
- **安全研究**：我们非常看重来自社区的专业反馈。

**🛡️ 为你的 AI 代理穿上防弹衣。Guardrails 是你的第一道，也是最后一道防线。**
