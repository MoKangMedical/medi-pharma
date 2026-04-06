# MediPharma 全球开源资源清单

> 基于2026年4月全网扫描，覆盖AI药物发现全流程

## 一、靶点发现模块

### 蛋白质结构预测
| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [AlphaFold](https://github.com/google-deepmind/alphafold) | 13k+ | DeepMind蛋白质结构预测，药物靶点基础 | Apache-2.0 |
| [OpenFold](https://github.com/aqlaboratory/openfold) | 2.2k+ | AlphaFold的PyTorch复现 | Apache-2.0 |
| [ESMFold](https://github.com/facebookresearch/esm) | 3k+ | Meta蛋白质语言模型+结构预测 | MIT |
| [ColabFold](https://github.com/sokrypton/ColabFold) | 2.5k+ | AlphaFold2快速版本 | MIT |

### 知识图谱 & 靶点挖掘
| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [DRKG](https://github.com/gnn4dr/DRKG) | 600+ | 药物重定位知识图谱，基因/化合物/疾病关联 | Apache-2.0 |
| [BioMedGPS](https://github.com/open-prophetdb/biomedgps) | 400+ | GNN知识图谱+药物重定位系统 | Apache-2.0 |
| [TypeDB Bio](https://github.com/typedb-osi/typedb-bio) | 200+ | 生物医学知识图谱数据库 | Apache-2.0 |
| [RepurAgent](https://github.com/pharmbio/repuragent) | 新 | 多Agent药物重定位系统 | MIT |
| [iKraph](https://github.com/myinsilicom/iKraph) | 100+ | 大规模生物医学知识图谱 | MIT |

## 二、虚拟筛选模块

### 分子对接
| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [DiffDock](https://github.com/gcorso/DiffDock) | 1.5k+ | 扩散模型分子对接，top-1成功率38% | MIT |
| [AutoDock Vina](https://github.com/ccsb-scripps/AutoDock-Vina) | 800+ | 经典分子对接工具 | Apache-2.0 |
| [OpenVS](https://github.com/gfzhou/OpenVS) | 70+ | AI加速虚拟筛选平台 | MIT |
| [DrugPipe](https://github.com/HySonLab/DrugPipe) | 19 | 生成式AI虚拟筛选管线 | MIT |
| [NVIDIA BioNeMo](https://github.com/NVIDIA-BioNeMo-blueprints/generative-virtual-screening) | 80 | NVIDIA全流程生成式虚拟筛选 | Apache-2.0 |

### 化合物库
| 数据源 | 化合物数 | 说明 |
|--------|----------|------|
| ChEMBL | 230万+ | 生物活性化合物数据库 |
| ZINC | 10亿+ | 可购买化合物虚拟筛选库 |
| PubChem | 1.15亿+ | 化学信息数据库 |
| Enamine REAL | 360亿+ | 最大可合成化合物库 |

## 三、分子生成模块

| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [torch-molecule](https://github.com/liugangcode/torch-molecule) | 318 | sklearn风格分子AI套件，生成+预测 | MIT |
| [PCMol](https://github.com/CDDLeiden/PCMol) | 75 | AlphaFold条件的从头分子生成 | MIT |
| [DrugGEN](https://github.com/HUBioDataLab/DrugGEN) | 50+ | 靶点特异性从头分子生成 | MIT |
| [MolGPT](https://github.com/ardigen/molgpt) | 100+ | GPT分子生成 | MIT |
| [JTVAE](https://github.com/wengong-jin/iclr17-jtvae) | 500+ | 树结构变分自编码器分子生成 | MIT |

## 四、ADMET预测模块

| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [ADMET-AI](https://github.com/swansonk14/admet_ai) | 287 | Chemprop ADMET预测，Web+CLI+API | MIT |
| [OpenADMET](https://github.com/OpenADMET) | 46+ | 开源ADMET联盟模型 | MIT |
| [Admetica](https://github.com/datagrok-ai/admetica) | 29 | Docker化ADMET REST API | MIT |
| [ADMET-X](https://github.com/RohithReddyGK/ADMET-X) | 3 | Web ADMET平台，可直接部署 | MIT |
| [deephERG](https://github.com/ChengF-Lab/deephERG) | 50+ | hERG心脏毒性预测 | MIT |

## 五、通用AI药物发现工具包

| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [DeepChem](https://github.com/deepchem/deepchem) | 6.7k+ | 最成熟的AI药物发现工具包 | MIT |
| [Chemprop](https://github.com/chemprop/chemprop) | 2.5k+ | 分子属性预测GNN | MIT |
| [RDKit](https://github.com/rdkit/rdkit) | 2.5k+ | 化学信息学基础库 | BSD |
| [Uni-Mol](https://github.com/dptech-corp/Uni-Mol) | 700+ | 统一分子表示学习 | Apache-2.0 |
| [ChemBERTa](https://github.com/seyonec/ChemBERTa) | 500+ | 分子语言模型 | MIT |
| [TorchDrug](https://github.com/DeepGraphLearning/TorchDrug) | 2k+ | PyTorch药物发现库 | MIT |

## 六、Agent & 自动化工作流

| 项目 | Stars | 说明 | 许可证 |
|------|-------|------|--------|
| [agentic-drug-discovery](https://github.com/UAB-SPARC/agentic-drug-discovery) | 新 | 多Agent并行药物发现 | MIT |
| [DrugAgent](https://github.com/FermiQ/drugagent) | 新 | 多Agent DTI预测 | MIT |
| [TxAgent](https://github.com/mims-harvard/TxAgent) | 新 | 治疗学推理Agent | MIT |
| [DEDA](https://github.com/drug-discovery-ai/deda-drug-evaluation-and-discovery-agent) | 新 | 药物评估发现Agent | MIT |
| [AgentD](https://github.com/hoon-ock/AgentD) | 新 | 模块化药物发现Agent | MIT |

## 七、综合清单 (Awesome Lists)

| 项目 | 说明 |
|------|------|
| [awesome-drug-discovery](https://github.com/yboulaamane/awesome-drug-discovery) | 最全药物发现工具清单 |
| [awesome-AIDD](https://github.com/daiyun02211/awesome-AIDD) | AI药物发现专项清单 |
| [awesome-small-molecule-ml](https://github.com/benb111/awesome-small-molecule-ml) | 小分子ML论文/数据集 |
| [awesome-drug-discovery-knowledge-graphs](https://github.com/astrazeneca/awesome-drug-discovery-knowledge-graphs) | AstraZeneca知识图谱清单 |
| [Awesome-AI-Agents-for-Healthcare](https://github.com/AgenticHealthAI/Awesome-AI-Agents-for-Healthcare) | 医疗AI Agent清单 |

---
*最后更新: 2026-04-06 | MediPharma v2.0 资源库*
