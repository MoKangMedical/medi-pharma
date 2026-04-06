# 💊 MediPharma v2.0 — AI驱动药物发现平台

> **伪装成服务公司的软件公司** — 我们交付候选化合物结果，不是卖AI工具
> 全流程AI制药：靶点发现→虚拟筛选→分子生成→先导优化→ADMET评估
> 参考Insilico Medicine（30个月进入临床）和Variational AI（Enki模式）

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)](#)

---

## 🎯 一句话

**AI驱动的药物发现全流程平台，从靶点到候选药物。** 专注罕见病创新药研发。

---

## 💰 商业定位（红杉论点）

> 下一代万亿美元公司是"伪装成服务公司的软件公司"。关键转变：从"卖工具"到"卖结果"。

- **MediPharma不是卖AI平台**，是卖"候选化合物"（从靶点到先导分子的结果）
- **大模型进步** → 药物发现更快更便宜 → 利润空间更大
- **OPC一人公司模式**：90%运营由AI Agent完成，边际成本趋零
- **切入点**：已外包的CRO任务（药物发现早期），逐步渗透判断型工作

---

## 🏗️ 平台架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    MediPharma v2.0                              │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│ 🎯 靶点  │ 🔬 虚拟  │ 🧬 分子  │ 💡 先导  │ 💊 ADMET          │
│ 发现     │ 筛选     │ 生成     │ 优化     │ 预测              │
├──────────┴──────────┴──────────┴──────────┴────────────────────┤
│ 📊 知识引擎 (RAG文献 + 专利分析 + 临床试验)                     │
├─────────────────────────────────────────────────────────────────┤
│ 🤖 Agent编排器 (全流程Pipeline + DMTA循环 + 智能决策)            │
├─────────────────────────────────────────────────────────────────┤
│              AI Engine (MIMO API - 零成本推理)                   │
├─────────────────────────────────────────────────────────────────┤
│  数据层: ChEMBL · PubChem · PDB · UniProt · PubMed · CT.gov    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 核心模块（7+1）

| 模块 | 功能 | 关键技术 | 开源参考 |
|------|------|----------|----------|
| 🎯 靶点发现 | PubMed挖掘+知识图谱+多维评分 | GNN + NLP + LLM | DRKG, BioMedGPS, OpenTargets |
| 🔬 虚拟筛选 | 10亿级化合物库+对接+亲和力预测 | DiffDock + DeepChem | DiffDock, OpenVS, NVIDIA BioNeMo |
| 🧬 分子生成 | 从头设计+靶点条件生成+遗传算法 | SMILES RNN + MCTS | torch-molecule, PCMol, DrugGEN |
| 💡 先导优化 | 多参数优化+分子编辑+骨架跃迁 | 遗传算法 + ADMET平衡 | DeepChem, Chemprop |
| 💊 ADMET预测 | 毒性/PK/合成可及性综合评估 | Chemprop + 启发式 | ADMET-AI, Admetica, OpenADMET |
| 📊 知识引擎 | RAG文献+专利+临床试验+竞品分析 | PubMed + ClinicalTrials.gov | RepurAgent, TypeDB Bio |
| 🤖 Agent编排 | 全流程Pipeline+DMTA循环+决策 | Agentic AI | agentic-drug-discovery, DrugAgent |
| 🌐 REST API | 7大模块统一接口 | FastAPI + Swagger | - |

---

## 📦 开源生态集成

MediPharma整合了全球最优秀的AI药物发现开源工具（[完整清单](docs/open-source-ecosystem.md)）：

### 靶点发现
- **AlphaFold** (13k⭐) — 蛋白质结构预测
- **DRKG** — 药物重定位知识图谱
- **OpenTargets** — 靶点-疾病关联

### 虚拟筛选
- **DiffDock** (1.5k⭐) — 扩散模型分子对接，top-1成功率38%
- **DeepChem** (6.7k⭐) — 最成熟的AI药物发现工具包
- **NVIDIA BioNeMo** — GPU加速生成式虚拟筛选

### 分子生成
- **torch-molecule** (318⭐) — sklearn风格分子AI套件
- **PCMol** — AlphaFold条件从头分子生成
- **Chemprop** (2.5k⭐) — 分子属性预测GNN

### ADMET
- **ADMET-AI** (287⭐) — Chemprop ADMET预测
- **OpenADMET** — 开源ADMET联盟
- **Admetica** — Docker化ADMET API

### Agent & 自动化
- **agentic-drug-discovery** — 多Agent并行药物发现
- **DrugAgent** — 多Agent DTI预测
- **RepurAgent** — 多Agent药物重定位

---

## 🎯 目标疾病

| 疾病 | 患者数 | 未满足需求 | AI价值 | 优先级 |
|------|--------|-----------|--------|--------|
| 重症肌无力(MG) | 20万+ | 诊断延迟2-5年 | ⭐⭐⭐⭐⭐ | 🥇 |
| 脊髓性肌萎缩症(SMA) | 3万+ | 基因疗法昂贵 | ⭐⭐⭐⭐⭐ | 🥈 |
| 戈谢病(GD) | 2万+ | 酶替代疗法局限 | ⭐⭐⭐⭐ | 🥉 |

---

## 🚀 快速开始

```bash
# 克隆
git clone https://github.com/MoKangMedical/medi-pharma.git
cd medi-pharma

# 安装
pip install -r requirements.txt

# 启动Web服务
python main.py serve --port 8095

# CLI靶点发现
python main.py target --disease "重症肌无力"

# CLI虚拟筛选
python main.py screen --target CHEMBL2364162

# CLI分子生成
python main.py generate --target CHRM1 -n 50

# CLI ADMET预测
python main.py admet --smiles "CC(=O)Oc1ccccc1C(=O)O"

# CLI全流程Pipeline
python main.py pipeline --disease "重症肌无力" --auto
```

---

## 📁 项目结构

```
medi-pharma/
├── main.py                       # 入口：FastAPI + CLI
├── requirements.txt              # 依赖
├── target_discovery/             # 🎯 靶点发现
│   ├── engine.py                 # 主引擎
│   ├── pubmed_miner.py           # PubMed文献挖掘
│   ├── knowledge_graph.py        # 多源知识图谱
│   └── scorer.py                 # 多维靶点评分
├── virtual_screening/            # 🔬 虚拟筛选
│   ├── engine.py                 # 主引擎
│   ├── compound_library.py       # 化合物库管理
│   ├── docking.py                # DiffDock/Vina对接
│   └── scorer.py                 # 亲和力评分
├── molecular_generation/         # 🧬 分子生成
│   ├── engine.py                 # 主引擎
│   ├── generators.py             # SMILES生成策略
│   └── optimizer.py              # 遗传算法优化
├── admet_prediction/             # 💊 ADMET预测
│   ├── engine.py                 # 主引擎
│   ├── toxicity.py               # 毒性预测
│   ├── pk_predictor.py           # PK预测
│   └── sa_score.py               # 合成可及性
├── lead_optimization/            # 💡 先导优化
│   ├── engine.py                 # 主引擎
│   ├── multi_param.py            # 多参数优化目标
│   └── edits.py                  # 分子编辑操作库
├── knowledge_engine/             # 📊 知识引擎
│   ├── engine.py                 # 主模块
│   ├── rag_search.py             # RAG文献检索
│   ├── patent_analyzer.py        # 专利分析
│   └── clinical_data.py          # ClinicalTrials.gov
├── orchestrator/                 # 🤖 Agent编排
│   ├── pipeline.py               # 全流程Pipeline
│   ├── dmta.py                   # DMTA循环管理
│   ├── decision.py               # Go/No-Go决策
│   └── reporter.py               # 报告生成
├── backend/                      # 🌐 REST API
│   ├── api.py                    # FastAPI路由 (15+端点)
│   └── models.py                 # Pydantic数据模型
└── docs/
    └── open-source-ecosystem.md  # 全球开源资源清单
```

---

## 🔗 相关项目

- **MediChat-RD**: https://github.com/MoKangMedical/medichat-rd （罕见病AI诊断）
- **MediSlim**: https://github.com/MoKangMedical/medi-slim （消费医疗现金流）

---

## 💰 商业模式

| 收入来源 | 客户 | Y2目标 |
|----------|------|--------|
| 候选化合物交付 | Biotech/Pharma | 1,000万 |
| 药物发现服务 | 制药企业 | 500万 |
| 数据服务 | 研究机构 | 200万 |
| 平台订阅 | CRO | 300万 |
| **合计** | | **2,000万** |

---

*MediPharma v2.0 | 2026年4月*
*AI驱动的药物发现平台 — 伪装成服务公司的软件公司*
