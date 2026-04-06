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

## 🧠 技术哲学：Harness理论

> **在AI领域，Harness（环境设计）比模型本身更重要。**
> 优秀的Harness设计（工具链+信息格式+上下文管理+失败恢复+结果验证）能使性能提升64%。

MediPharma的本质是**药物发现Harness**——不是堆更多分子生成模型，而是设计好从靶点到候选药物的全流程架构：

- **Pipeline架构**：靶点→筛选→生成→优化→ADMET的有序编排
- **多维度评分框架**：亲和力+选择性+合成可及性+ADMET+知识产权
- **失败分子回溯**：自动识别失败原因→调整生成策略→重新优化
- **实验数据闭环**：实验结果→模型更新→策略调整

**护城河来源**：药物发现全流程的Harness设计，而非分子生成模型本身。
模型可以被替换（REINVENT/Diffusion/MolGPT），但Harness是私有的。

---

## 🚀 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动API
python main.py serve --port 8095

# 测试
python main.py run-pipeline "DRD2" --max-iterations 2
```

---

## ⚡ 核心功能

### 1. 靶点发现引擎
- **PubMed文献挖掘**：基于疾病/基因/通路的智能搜索
- **知识图谱构建**：基因-疾病-通路-药物关系网络
- **多维评分系统**：新颖性 × 可成药性 × 竞争格局 × 商业价值

### 2. 虚拟筛选平台
- **化合物库生成**：基于已知活性分子的类药化合物库
- **分子对接**：DiffDock集成 + Vina对接 + 亲和力评分
- **筛选管道**：批量筛选 + 自动排序 + Top-N推荐

### 3. 分子生成引擎
- **SMILES生成**：基于规则的分子生成
- **遗传算法优化**：多代进化优化分子性质
- **约束条件**：分子量、LogP、HBD/HBA等类药规则

### 4. ADMET预测
- **毒性预测**：hERG毒性、肝毒性、致癌性
- **PK预测**：口服生物利用度、半衰期、血脑屏障
- **合成可及性**：SA Score + 合成路线复杂度

### 5. 先导优化
- **多参数优化**：活性+选择性+ADMET+可合成性
- **分子编辑**：生物等排体替换 + 侧链修饰
- **SAR分析**：构效关系图谱

### 6. 知识引擎
- **RAG检索**：文献/专利/临床试验数据的智能检索
- **竞品分析**：同类靶点药物的竞争格局
- **知识问答**：基于文献的药物发现问答

### 7. Agent编排
- **药物发现Pipeline**：靶点→筛选→生成→优化→ADMET自动化
- **DMTA循环**：设计→制造→测试→分析自动化循环
- **决策支持**：Go/No-Go决策 + 失败原因分析
- **报告生成**：项目报告 + 实验方案 + 分析报告

---

## 📊 API端点（15+个）

### 核心端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 系统健康检查 |
| `/api/targets/discover` | POST | 靶点发现 |
| `/api/targets/score` | POST | 靶点评分 |
| `/api/screening/generate-library` | POST | 化合物库生成 |
| `/api/screening/dock` | POST | 分子对接 |
| `/api/screening/batch` | POST | 批量筛选 |
| `/api/generation/generate` | POST | 分子生成 |
| `/api/generation/optimize` | POST | 分子优化 |
| `/api/admet/predict` | POST | ADMET预测 |
| `/api/admet/batch` | POST | 批量ADMET |
| `/api/optimization/lead-optimize` | POST | 先导优化 |
| `/api/knowledge/query` | POST | 知识查询 |
| `/api/pipeline/run` | POST | 运行Pipeline |
| `/api/agents/dmta-cycle` | POST | DMTA循环 |
| `/api/agents/decision` | POST | 决策支持 |
| `/api/agents/report` | POST | 报告生成 |

### 使用示例

```python
import requests

# 1. 发现靶点
targets = requests.post("http://localhost:8095/api/targets/discover", json={
    "disease": "重症肌无力",
    "target_type": "protein",
    "max_results": 10
}).json()

# 2. 生成分子
molecules = requests.post("http://localhost:8095/api/generation/generate", json={
    "target_id": "ACHE",
    "num_molecules": 50,
    "method": "genetic"
}).json()

# 3. 预测ADMET
admet = requests.post("http://localhost:8095/api/admet/predict", json={
    "smiles": ["c1ccccc1", "CCO"]
}).json()

# 4. 运行完整Pipeline
report = requests.post("http://localhost:8095/api/pipeline/run", json={
    "target_id": "DRD2",
    "max_iterations": 5
}).json()
```

---

## 🏗️ 架构设计

```
medi-pharma/
├── discovery/          # 靶点发现
│   ├── target_discover.py
│   ├── knowledge_graph.py
│   └── target_scorer.py
├── screening/          # 虚拟筛选
│   ├── compound_library.py
│   ├── molecular_docking.py
│   └── screening_pipeline.py
├── generation/         # 分子生成
│   ├── molecular_generator.py
│   └── genetic_optimizer.py
├── admet/              # ADMET预测
│   ├── toxicity.py
│   ├── pk_prediction.py
│   └── synthesizability.py
├── optimization/       # 先导优化
│   ├── lead_optimizer.py
│   ├── molecular_editor.py
│   └── sar_analyzer.py
├── knowledge/          # 知识引擎
│   ├── rag_engine.py
│   ├── patent_analyzer.py
│   └── clinical_trials.py
├── agents/             # Agent编排
│   ├── pipeline.py
│   ├── dmta_loop.py
│   ├── decision_maker.py
│   └── report_generator.py
├── api/                # REST API
├── main.py             # CLI入口
└── requirements.txt
```

---

## 📈 性能基准

| 组件 | 指标 | 性能 |
|------|------|------|
| 靶点发现 | PubMed搜索速度 | ~5秒/10篇 |
| 分子生成 | 生成速度 | ~100分子/秒 |
| ADMET预测 | 单分子预测 | ~0.5秒 |
| 分子对接 | DiffDock对接 | ~30秒/分子 |
| Pipeline | 单靶点全流程 | ~30分钟 |

---

## 🔗 项目矩阵

| 项目 | 定位 | 状态 |
|------|------|------|
| MediChat-RD | 罕见病AI诊断 | ⭐ 技术壁垒 |
| MediSlim | 消费医疗 | ⭐ 现金流 |
| MediPharma | AI制药工具链 | ⭐ 药物发现 |
| DrugMind | 药物研发协作 | ⭐ 团队数字化 |

- **MediChat-RD**: https://github.com/MoKangMedical/medichat-rd （罕见病AI诊断技术品牌）
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
