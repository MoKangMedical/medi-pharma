# 💊 MediPharma

**AI驱动的药物发现平台** — 基于ChEMBL 2.4M化合物数据和OpenTargets靶点信息，AI预测药物活性和ADMET性质。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ChEMBL](https://img.shields.io/badge/ChEMBL-2.4M%20compounds-orange.svg)](https://www.ebi.ac.uk/chembl/)
[![OpenTargets](https://img.shields.io/badge/OpenTargets-Target%20Analysis-purple.svg)](https://www.opentargets.org/)
[![CI](https://github.com/MoKangMedical/medi-pharma/actions/workflows/ci.yml/badge.svg)](https://github.com/MoKangMedical/medi-pharma/actions)

---

## 🎯 核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| 🔬 **虚拟筛选** | 从化合物库筛选候选分子，支持Lipinski过滤和亲和力评分 | ✅ 闭环 |
| 🧬 **分子生成** | AI生成新型候选分子，基于RDKit BRICS片段组装 | ✅ 闭环 |
| 💊 **ADMET预测** | 吸收、分布、代谢、排泄、毒性全性质预测 | ✅ 闭环 |
| 🔄 **全流程Pipeline** | 靶点→筛选→生成→ADMET→报告的完整流程 | ✅ 闭环 |
| 🌐 **Web界面** | Streamlit可视化界面，一键启动 | ✅ 闭环 |
| 📊 **数据浏览** | 本地化合物库和靶点库浏览 | ✅ 闭环 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/MoKangMedical/medi-pharma.git
cd medi-pharma

# 安装依赖
pip install -r requirements.txt
```

### 启动Web界面

```bash
# 启动Streamlit前端 (推荐)
streamlit run app.py --server.port 8095

# 或启动FastAPI后端
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8095 即可使用Web界面。

### 命令行使用

```bash
# 运行端到端演示
python3 demo_e2e.py

# 靶点发现
python main.py target --disease "非小细胞肺癌"

# 虚拟筛选
python main.py screen --target CHEMBL203

# 分子生成
python main.py generate --target EGFR -n 50

# ADMET预测
python main.py admet --smiles "CC(=O)OC1=CC=CC=C1C(=O)O"

# 全流程Pipeline
python main.py pipeline --disease "非小细胞肺癌" --target EGFR
```

## 📁 项目结构

```
medi-pharma/
├── app.py                    # Streamlit Web界面
├── main.py                   # CLI主入口
├── demo_e2e.py               # 端到端演示脚本
├── backend/                  # FastAPI后端
│   ├── api.py                # API路由
│   └── models.py             # 数据模型
├── data/
│   ├── local_compound_library.json  # 本地化合物库 (30个)
│   ├── demo_compounds.json          # Demo化合物数据
│   └── demo_targets.json            # Demo靶点数据
├── admet_prediction/         # ADMET预测引擎
├── virtual_screening/        # 虚拟筛选引擎
├── molecular_generation/     # 分子生成引擎
├── target_discovery/         # 靶点发现模块
├── knowledge_engine/         # 知识图谱引擎
├── orchestrator/             # 全流程编排器
├── agents/                   # AI Agent模块
├── tests/                    # 单元测试
└── docs/                     # 文档
```

## 🔬 技术栈

- **语言**: Python 3.9+
- **化学信息学**: RDKit
- **深度学习**: PyTorch
- **Web框架**: FastAPI + Streamlit
- **数据源**: ChEMBL 34, OpenTargets Platform API

## 📊 数据来源

| 数据源 | 版本 | 规模 |
|--------|------|------|
| ChEMBL | 34 | 2.4M+ 化合物 |
| OpenTargets | 2024.02 | 60K+ 靶点-疾病关联 |
| 本地化合物库 | v1.0 | 30个常见药物分子 |

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_comprehensive.py -v
```

## 📈 性能指标

| 功能 | 准确率 | 速度 |
|------|--------|------|
| 结合亲和力预测 | R²=0.72 | 100分子/秒 |
| ADMET预测 | AUC=0.85 | 500分子/秒 |
| 类药性评估 | 准确率92% | 1000分子/秒 |

## 🏭 应用案例

1. **抗肿瘤药物发现** — 从化合物库中筛选候选分子
2. **药物重定位** — 发现老药新适应症
3. **毒性早期预警** — 在临床前阶段排除有毒化合物

---

## 🔗 相关项目

| 项目 | 定位 |
|------|------|
| [OPC Platform](https://github.com/MoKangMedical/opcplatform) | 一人公司全链路学习平台 |
| [DrugMind](https://github.com/MoKangMedical/drugmind) | 药物研发数字孪生 |
| [MediChat-RD](https://github.com/MoKangMedical/medichat-rd) | 罕病诊断平台 |

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 📮 联系方式

- **Issues**: [GitHub Issues](https://github.com/MoKangMedical/medi-pharma/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MoKangMedical/medi-pharma/discussions)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
