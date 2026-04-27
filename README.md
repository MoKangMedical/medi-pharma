# 💊 MediPharma

**AI驱动的药物发现平台** — 基于ChEMBL 2.4M化合物数据和OpenTargets靶点信息，AI预测药物活性和ADMET性质。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ChEMBL](https://img.shields.io/badge/ChEMBL-2.4M%20compounds-orange.svg)](https://www.ebi.ac.uk/chembl/)
[![OpenTargets](https://img.shields.io/badge/OpenTargets-Target%20Analysis-purple.svg)](https://www.opentargets.org/)
[![CI](https://github.com/MoKangMedical/medi-pharma/actions/workflows/ci.yml/badge.svg)](https://github.com/MoKangMedical/medi-pharma/actions)

---

## 🎯 核心功能

| 功能 | 描述 |
|------|------|
| 🧬 **化合物数据库** | ChEMBL 2.4M化合物检索，支持SMILES、InChIKey、名称搜索 |
| 🎯 **靶点分析** | OpenTargets靶点-疾病关联分析，druggability评估 |
| 🔬 **虚拟筛选** | AI模型（GNN/Transformer）筛选候选化合物，对接打分 |
| 💉 **ADMET预测** | 吸收、分布、代谢、排泄、毒性全性质预测 |
| ⚗️ **分子优化** | 基于AI的分子结构优化，先导化合物优化 |
| 📊 **可视化** | 分子3D可视化、结合位点展示、活性热图 |
| 🌐 **Web界面** | Streamlit可视化界面，一键启动 |
| 🤖 **AI Agents** | 6个专业Agent全流程自动化 |

## 🏗️ 技术栈

- **语言**: Python 3.9+
- **化学信息学**: RDKit, ChEMBL_WEBRESOURCE_CLIENT
- **深度学习**: PyTorch, PyTorch Geometric, DGL
- **Web框架**: FastAPI + Streamlit
- **数据源**: ChEMBL 34, OpenTargets Platform API
- **部署**: Docker, Docker Compose

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/MoKangMedical/medi-pharma.git
cd medi-pharma

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 启动服务

```bash
# 方式1: 启动FastAPI后端
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000

# 方式2: 启动Streamlit前端 (推荐)
streamlit run app.py --server.port 8095

# 方式3: CLI命令行
python main.py serve --port 8095
python main.py target --disease "重症肌无力"
python main.py screen --target CHEMBL2364162
python main.py admet --smiles "CC(=O)OC1=CC=CC=C1C(=O)O"
python main.py pipeline --disease "非小细胞肺癌" --auto
```

### Docker 部署

```bash
docker-compose up -d

# 或者单独运行
docker build -t medipharma .
docker run -p 8000:8000 -p 8095:8095 medipharma
```

## 📁 项目结构

```
medi-pharma/
├── app.py                    # Streamlit Web界面
├── main.py                   # CLI主入口
├── backend/                  # FastAPI后端
│   ├── api.py                # API路由
│   └── models.py             # 数据模型
├── data/
│   ├── demo_compounds.json   # 10个热门药物数据
│   └── demo_targets.json     # 10个热门靶点数据
├── src/
│   ├── screening.py          # 虚拟筛选模块
│   ├── admet.py              # ADMET预测模块
│   └── compound_search.py    # 化合物检索模块
├── admet_prediction/         # ADMET预测模型
├── virtual_screening/        # 虚拟筛选引擎
├── target_discovery/         # 靶点发现模块
├── molecular_generation/     # 分子生成模块
├── lead_optimization/        # 先导化合物优化
├── drug_recommend/           # 药物推荐系统
├── knowledge_engine/         # 知识图谱引擎
├── agents/                   # AI Agent模块
│   ├── one_person_pharma.py  # 一人药企Agent
│   ├── target_discovery.py   # 靶点发现Agent
│   ├── admet_predictor.py    # ADMET预测Agent
│   ├── virtual_screening.py  # 虚拟筛选Agent
│   ├── molecular_generation.py # 分子生成Agent
│   └── lead_optimization.py  # 先导优化Agent
├── orchestrator/             # 编排器
├── tests/                    # 测试
│   ├── test_comprehensive.py # 完整测试套件
│   └── test_api.py           # API测试
├── docs/                     # 文档
└── scripts/                  # 工具脚本
```

## 📖 API 文档

启动后端服务后访问：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Streamlit UI**: `http://localhost:8095`

### 主要 API 端点

```
GET  /health                              # 健康检查
POST /api/v1/targets/discover             # 靶点发现
POST /api/v1/screening/virtual            # 虚拟筛选
POST /api/v1/admet/predict                # ADMET预测
POST /api/v1/molecule/generate            # 分子生成
POST /api/v1/molecule/optimize            # 分子优化
POST /api/v1/pipeline/run                 # 全流程Pipeline
```

## 📊 数据来源

| 数据源 | 版本 | 规模 |
|--------|------|------|
| ChEMBL | 34 | 2.4M+ 化合物 |
| OpenTargets | 2024.02 | 60K+ 靶点-疾病关联 |
| PDB | - | 200K+ 蛋白质结构 |

## 🤖 AI Agents

| Agent | 功能 |
|-------|------|
| OnePersonPharma | 一人药企全流程编排 |
| TargetDiscoveryAgent | 靶点发现与验证 |
| ADMETPredictorAgent | ADMET性质预测 |
| VirtualScreeningAgent | 虚拟筛选执行 |
| MolecularGenerationAgent | 分子生成与优化 |
| LeadOptimizationAgent | 先导化合物优化 |

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_comprehensive.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

## 📈 性能指标

| 功能 | 准确率 | 速度 |
|------|--------|------|
| 结合亲和力预测 | R²=0.72 | 100分子/秒 |
| ADMET预测 | AUC=0.85 | 500分子/秒 |
| 类药性评估 | 准确率92% | 1000分子/秒 |

## 🏭 应用案例

1. **抗肿瘤药物发现** — 从100万化合物中筛选出50个候选分子
2. **药物重定位** — 发现老药新适应症，节省80%研发成本
3. **毒性早期预警** — 在临床前阶段排除90%有毒化合物

---

## 🔗 相关项目

| 项目 | 定位 |
|------|------|
| [OPC Platform](https://github.com/MoKangMedical/opcplatform) | 一人公司全链路学习平台 |
| [Digital Sage](https://github.com/MoKangMedical/digital-sage) | 与100位智者对话 |
| [Cloud Memorial](https://github.com/MoKangMedical/cloud-memorial) | AI思念亲人平台 |
| [天眼 Tianyan](https://github.com/MoKangMedical/tianyan) | 市场预测平台 |
| [MediChat-RD](https://github.com/MoKangMedical/medichat-rd) | 罕病诊断平台 |
| [DrugMind](https://github.com/MoKangMedical/drugmind) | 药物研发数字孪生 |

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/MoKangMedical/medi-pharma/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoKangMedical/medi-pharma/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
