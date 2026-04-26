# 💊 MediPharma — AI驱动的药物发现平台

> 基于ChEMBL 2.4M化合物数据和OpenTargets靶点信息，AI预测药物活性和ADMET性质

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ChEMBL](https://img.shields.io/badge/ChEMBL-2.4M%20compounds-orange.svg)](https://www.ebi.ac.uk/chembl/)
[![OpenTargets](https://img.shields.io/badge/OpenTargets-Target%20Analysis-purple.svg)](https://www.opentargets.org/)

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

## 🏗️ 技术栈

- **语言**: Python 3.9+
- **化学信息学**: RDKit, ChEMBL_WEBRESOURCE_CLIENT
- **深度学习**: PyTorch, PyTorch Geometric, DGL
- **Web框架**: Streamlit, FastAPI
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
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
# 启动 Streamlit 前端
streamlit run main.py

# 或启动 FastAPI 后端
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
docker-compose up -d
```

## 📁 项目结构

```
medi-pharma/
├── main.py                  # Streamlit 主入口
├── backend/                 # FastAPI 后端
├── data/
│   ├── sample-compounds.json   # 50个热门药物分子数据
│   └── targets.json            # 20个热门靶点数据
├── src/
│   ├── screening.py         # 虚拟筛选模块
│   ├── admet.py             # ADMET预测模块
│   └── compound_search.py   # 化合物检索模块
├── admet_prediction/        # ADMET预测模型
├── virtual_screening/       # 虚拟筛选引擎
├── target_discovery/        # 靶点发现模块
├── molecular_generation/    # 分子生成模块
├── lead_optimization/       # 先导化合物优化
├── drug_recommend/          # 药物推荐系统
├── knowledge_engine/        # 知识图谱引擎
├── agents/                  # AI Agent 模块
├── orchestrator/            # 编排器
├── integrations/            # 外部API集成
├── examples/                # 使用案例
├── tests/                   # 测试
├── docs/                    # 文档
└── scripts/                 # 工具脚本
```

## 📖 API 文档

启动后端服务后访问：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 主要 API 端点

```
GET  /api/v1/compounds/search?q={query}     # 化合物搜索
GET  /api/v1/compounds/{chembl_id}           # 化合物详情
POST /api/v1/screening/virtual               # 虚拟筛选
POST /api/v1/admet/predict                   # ADMET预测
GET  /api/v1/targets/{target_id}             # 靶点信息
GET  /api/v1/targets/{target_id}/diseases    # 靶点-疾病关联
POST /api/v1/molecule/optimize               # 分子优化
```

### 示例请求

```bash
# 搜索化合物
curl "http://localhost:8000/api/v1/compounds/search?q=aspirin"

# ADMET预测
curl -X POST "http://localhost:8000/api/v1/admet/predict" \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}'

# 虚拟筛选
curl -X POST "http://localhost:8000/api/v1/screening/virtual" \
  -H "Content-Type: application/json" \
  -d '{"target": "EGFR", "num_results": 10}'
```

## 📊 数据来源

| 数据源 | 版本 | 规模 |
|--------|------|------|
| ChEMBL | 34 | 2.4M+ 化合物 |
| OpenTargets | 2024.02 | 60K+ 靶点-疾病关联 |
| PDB | - | 200K+ 蛋白质结构 |

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/MoKangMedical/medi-pharma/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoKangMedical/medi-pharma/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
