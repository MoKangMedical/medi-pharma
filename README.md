# 💊 MediPharma — AI驱动药物发现平台

> **中国版Insilico Medicine × 罕见病专注**
> 全流程AI制药：靶点发现→虚拟筛选→先导优化→临床前
> 参考Insilico Medicine（30个月进入临床）和Variational AI（Enki模式）

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🎯 一句话

**AI驱动的药物发现全流程平台，从靶点到候选药物。** 专注罕见病创新药研发。

---

## 🏗️ 平台架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MediPharma v1.0                          │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  靶点发现     │  虚拟筛选     │  先导优化     │  临床前评估    │
│  Target ID   │  Virtual     │  Lead        │  Preclinical  │
│              │  Screening   │  Optimization │  Assessment   │
├──────────────┴──────────────┴──────────────┴────────────────┤
│              AI Engine (MIMO API + OpenAI)                  │
├─────────────────────────────────────────────────────────────┤
│  数据层: ChEMBL · PDB · UniProt · PubMed · ClinicalTrials  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 核心模块

| 模块 | 功能 | 技术 | 状态 |
|------|------|------|------|
| 🎯 靶点发现 | 多组学分析、知识图谱、文献挖掘 | GNN + NLP | ✅ |
| 🔬 虚拟筛选 | 10亿级化合物库、AI对接、活性预测 | DL + GNN | ✅ |
| 💡 先导优化 | 多参数优化、生成式设计、ADMET预测 | RL + Diffusion | ✅ |
| 🧪 临床前评估 | 毒性预测、PK模拟、合成可行性 | ML + Physics | ✅ |
| 📊 知识引擎 | 文献挖掘、专利分析、临床数据 | RAG + LLM | ✅ |
| 🤖 Agent系统 | 自动化DMTA循环、智能决策 | Agentic AI | ✅ |

---

## 📦 技术栈

- **后端**: FastAPI + Python 3.10+
- **AI引擎**: MIMO API (零成本) + OpenAI
- **数据库**: SQLite + PostgreSQL
- **分子模拟**: RDKit + OpenMM
- **深度学习**: PyTorch + PyG
- **前端**: React + Vite

---

## 🎯 目标疾病

| 疾病 | 患者数 | 未满足需求 | AI价值 | 优先级 |
|------|--------|-----------|--------|--------|
| 重症肌无力(MG) | 20万+ | 诊断延迟2-5年 | ⭐⭐⭐⭐⭐ | 🥇 |
| 脊髓性肌萎缩症(SMA) | 3万+ | 基因疗法昂贵 | ⭐⭐⭐⭐⭐ | 🥈 |
| 戈谢病(GD) | 2万+ | 酶替代疗法局限 | ⭐⭐⭐⭐ | 🥉 |
| 法布雷病 | 1万+ | 早期诊断困难 | ⭐⭐⭐⭐ | |
| DMD | 5万+ | 无治愈方法 | ⭐⭐⭐⭐ | |

---

## 💰 商业模式

| 收入来源 | 客户 | Y2目标 |
|----------|------|--------|
| 药物发现服务 | Biotech/Pharma | 500万 |
| 候选药物授权 | 大型药企 | 1,000万 |
| 数据服务 | 研究机构 | 200万 |
| 平台订阅 | CRO | 300万 |
| **合计** | | **2,000万** |

---

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/MoKangMedical/medi-pharma.git
cd medi-pharma

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

---

## 📁 项目结构

```
medi-pharma/
├── main.py                    # 主入口
├── agents/                    # AI代理
│   ├── target_discovery.py   # 靶点发现
│   ├── virtual_screening.py  # 虚拟筛选
│   ├── lead_optimization.py  # 先导优化
│   ├── admet_predictor.py    # ADMET预测
│   ├── knowledge_engine.py   # 知识引擎
│   └── orchestrator.py       # Agent编排
├── backend/                   # API服务
│   ├── api.py               # REST API
│   └── models.py            # 数据模型
├── data/                      # 数据
│   ├── compounds/            # 化合物库
│   ├── targets/              # 靶点数据
│   └── literature/           # 文献
├── docs/                      # 文档
└── requirements.txt          # 依赖
```

---

## 🔗 相关项目

- **MediChat-RD**: https://github.com/MoKangMedical/medichat-rd
- **MediSlim**: https://github.com/MoKangMedical/medi-slim

---

*MediPharma v1.0 | 2026年4月*
*AI驱动的药物发现平台*
