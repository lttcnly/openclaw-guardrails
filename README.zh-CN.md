# 🛡️ OpenClaw Guardrails

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Eco-OpenClaw-blueviolet?style=for-the-badge" alt="Eco-OpenClaw">
  <img src="https://img.shields.io/badge/Security-Enterprise_Grade-red?style=for-the-badge" alt="Enterprise">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Version-1.1.0-blue?style=for-the-badge" alt="Version">
</p>

---

**OpenClaw Guardrails** 是专为 AI 代理设计的**全栈安全防护与自愈框架**。它是 OpenClaw 生态中的“免疫系统”，通过实时语义拦截、配置硬性守护和供应链深度扫描，确保您的 AI 助手在安全边界内运行，避免金融资产流失、隐私泄露及毁灭性指令执行。

---

## 🚀 极速上手：AI 原生安装

如果您正在使用 **OpenClaw**，只需一句话即可完成全套企业级防御体系的自动化部署。请对您的 Agent 说：

> **“帮我安装 `lttcnly/openclaw-guardrails`。安装后初始化安全基线，配置每日 03:17 的自动审计任务，并展示首份风险评分报告。”**

---

## 🏗️ 系统架构：三位一体防御体系 (Vertical Flow)

本项目采用垂直分层架构，从入口到持久化层提供全方位保护：

```mermaid
graph TD
    subgraph L1 [第一层：主动防御 - Shield Mode]
        A[Agent 动作发起] --> B{语义意图分析}
        B -- 识别到风险 --> C[拦截并请求人工审批]
        B -- 确认安全 --> D[允许执行]
    end

    D --> E

    subgraph L2 [第二层：配置自愈 - Enforce Mode]
        E[系统配置监控] --> F{安全基线校验}
        F -- 发现非法篡改 --> G[强制回滚与快照备份]
        F -- 符合基线 --> H[保持运行]
    end

    H --> I

    subgraph L3 [第三层：深度审计 - Intelligence]
        I[SBOM 资产盘点] --> J[全球漏洞情报比对]
        J --> K[动态风险评分报告]
    end

    style L1 fill:#f9f,stroke:#333,stroke-width:2px
    style L2 fill:#bbf,stroke:#333,stroke-width:2px
    style L3 fill:#bfb,stroke:#333,stroke-width:2px
```

---

## 🔥 核心特性深度解析

### 💎 1. 金融级指令拦截 (Financial Shield)
唯一能深度理解 Agent 意图的安全框架：
-   **语义识别**：识别隐藏在普通指令中的 `transfer`, `pay`, `withdraw` 等操作。
-   **上下文感知**：区分合法的查询与非法的资产转移请求。
-   **熔断机制**：在风险触发时立即切断工具调用流，并要求管理员二次确认。

### 🩹 2. 安全基线硬性守护 (Baseline Enforcement)
防止“权限漂移”导致的安全黑洞：
-   **黄金镜像**：强制执行 `authMode: token`, `systemRunApproval: always` 等核心配置。
-   **即时回滚**：检测到配置被篡改后（如 `allowInsecure: true`），微秒级自动恢复。

### 🕵️ 3. 隐私与凭据扫描仪 (PII Sanitizer)
防止您的 API Key 成为“公开的秘密”：
-   **全量探测**：扫描 `.env`, `.log`, `.json` 中的秘钥、邮箱、IP 及 Token。
-   **自动脱敏**：生成审计报告时自动对敏感数据进行 `[REDACTED]` 处理。

---

## 📋 合规性支持 (Compliance)

Guardrails 旨在帮助企业快速满足主流安全标准：
-   ✅ **等保 2.0 (MLPS)**：身份鉴别、访问控制、安全审计、数据完整性。
-   ✅ **CIS Benchmarks**：操作系统与服务加固检查。
-   ✅ **GDPR**：自动隐私数据识别与脱敏。

---

## 💡 征集更好的方案与算法 (Join Us!)

**我们相信，安全是一个永无止境的博弈过程。**

我们热忱欢迎安全专家、算法工程师和社区开发者提供更好的方式来加固这个“免疫系统”。我们特别关注：
1.  **更精准的语义分析算法**：如何更有效地识别复杂的提示词注入或绕过攻击？
2.  **更高效的自愈机制**：对于大规模分布式节点，如何更优雅地同步安全策略？
3.  **零信任审计模型**：针对动态加载的第三方工具，是否有更深层的沙箱审计方案？

如果您有任何想法，欢迎提交 **Issue** 或发起 **Pull Request**！您的每一个算法优化都将让 AI 的世界更安全。

---

## 🛠️ 技术指标 (Benchmarks)

| 指标 | 表现 | 说明 |
| :--- | :--- | :--- |
| **全量审计耗时** | < 15s | 基于 Python 多进程并行扫描引擎。 |
| **配置自愈时延** | < 100ms | 检测到变动后的自动恢复速度。 |
| **扫描深度** | 递归 5 层 | 深度识别嵌套的 npm/pip 影子依赖。 |

---

## 🤝 路线图 (Roadmap)
- [x] v1.1 并行执行引擎与配置自愈
- [x] 金融级语义拦截与 PII 脱敏
- [ ] **多端同步**：支持多 OpenClaw 节点联邦安全审计。
- [ ] **Agent 行为画像**：基于机器学习识别异常操作序列。

---

**🛡️ 为您的 AI 代理穿上防弹衣。Guardrails 是您的第一道，也是最后一道防线。**
