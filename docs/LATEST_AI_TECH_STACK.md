# MediPharma 2026 最新AI制药技术栈

> 更新日期：2026-04-06
> 技术哲学：Harness理论 — 环境设计比模型更重要，模型可以被替换，Harness是私有的

---

## 一、技术全景图

```
┌─────────────────────────────────────────────────────┐
│              MediPharma 技术栈 (2026)                │
├─────────────────────────────────────────────────────┤
│ Layer 7: 业务价值 — 候选化合物交付                    │
├─────────────────────────────────────────────────────┤
│ Layer 6: Harness — Pipeline编排/评分框架/失败回溯    │
├─────────────────────────────────────────────────────┤
│ Layer 5: Agent — DMTA循环/决策支持/报告生成          │
├─────────────────────────────────────────────────────┤
│ Layer 4: 工具集成 — MCP协议/API/外部数据源            │
├─────────────────────────────────────────────────────┤
│ Layer 3: 上下文管理 — 知识图谱/RAG/状态管理           │
├─────────────────────────────────────────────────────┤
│ Layer 2: 推理优化 — Prompt工程/评分函数设计            │
├─────────────────────────────────────────────────────┤
│ Layer 1: 模型层 — REINVENT4/DiffDock/AlphaFold3     │
└─────────────────────────────────────────────────────┘
```

---

## 二、2026核心技术栈

### 2.1 分子生成：从筛选到创造

| 技术 | 类型 | GitHub | 状态 | 核心能力 |
|------|------|--------|------|---------|
| **REINVENT 4** | RNN/Transformer + RL | [MolecularAI/REINVENT4](https://github.com/MolecularAI/REINVENT4) | ✅ v4.7 (2025.11) | 多目标优化(QED+SA+对接亲和力)，支持de novo/骨架跃迁/R基替换 |
| **MolOrgGPT** | Decoder-only Transformer (1.47B) | - | ✅ 2026.1 | GPT-2架构+SELFIES+PPO-RL，QED 0.68，低毒性，新颖骨架 |
| **PocketFlow** | 自回归流匹配模型 | [Saoge123/PocketFlow](https://github.com/Saoge123/PocketFlow) | ✅ 2024 | 基于口袋条件的分子生成，100%化学有效性，湿实验验证 |
| **DiffDock** | 扩散模型（盲对接） | [gcorso/DiffDock](https://github.com/gcorso/DiffDock) | ✅ 持续更新 | SE(3)等变扩散过程，预测配体位置/旋转/扭转，超越AutoDock Vina |
| **Apo2Mol** | 层次图扩散模型 | [arXiv](https://arxiv.org/abs/2511.14559) | ✅ 2025 | 从apo口袋生成配体+口袋构象适应，亲和力和灵活性SOTA |

**技术演进路线**：
```
传统HTS筛选 (90%失败率)
    ↓
虚拟筛选 + 分子对接 (AutoDock Vina)
    ↓
基于配体的生成 (VAE/GAN/REINVENT)
    ↓
基于口袋的条件生成 (DiffDock/PocketFlow) ← 当前前沿
    ↓
多模态扩散生成 (Apo2Mol/DiffPhore/PIDiff) ← 2026热点
```

### 2.2 蛋白质结构预测：AlphaFold3生态

| 技术 | 开发者 | 状态 | 核心能力 |
|------|--------|------|---------|
| **AlphaFold 3** | Google DeepMind + Isomorphic Labs | ✅ 2024.5 | 多模态（蛋白+核酸+配体+离子），扩散架构，预测结合位点和亲和力 |
| **IsoDDE** | Isomorphic Labs | ✅ 2026.2 | 基于AF3的药物设计引擎，2x准确率提升，去新分子生成+临床候选物 |
| **OpenFold3** | OpenFold Consortium + NVIDIA | ✅ 2025-2026 | AF3开源替代，支持微调和商业应用 |
| **Ligo AlphaFold3** | Ligo Biosciences | ✅ GitHub | 社区实现，更广泛可用 |

**应用链路**：
```
AF3预测靶点结构 → DiffDock对接 → PocketFlow生成 → REINVENT优化 → ADMET验证
```

### 2.3 强化学习优化：REINVENT生态

**REINVENT 4 核心能力**：
- **预训练Prior**：在大规模化学数据上预训练的RNN/Transformer
- **迁移学习**：在自定义数据集上微调Prior
- **RL优化**：REINFORCE策略梯度，采样SMILES→评分→更新策略
- **多目标评分**：QED + 合成可及性 + 对接亲和力 + 自定义评分函数
- **支持任务**：de novo生成/骨架跃迁/R基替换/连接子设计

**2025-2026改进**：
- REINFORCE改进：更好的奖励塑造、基线、爬山法、经验回放 → SOTA on MolOpt基准
- MolOrgGPT（2026.1）：1.47B参数GPT-2+SELFIES+PPO-RL → QED 0.68，低毒性，新颖骨架
- Active Learning闭环：生成→测试→反馈→模型更新 → 药物-材料性质前沿

### 2.4 扩散模型：分子生成新范式

**扩散模型 vs 传统生成**：

| 维度 | VAE/GAN | RL (REINVENT) | 扩散模型 |
|------|---------|---------------|---------|
| 生成方式 | 随机采样 | 策略优化 | 去噪过程 |
| 3D感知 | ❌ | ❌ | ✅ |
| 口袋条件 | ❌ | 有限 | ✅ 原生支持 |
| 有效性 | ~90% | ~85% | ~100% |
| 多样性 | 中 | 中 | 高 |

**核心扩散工具**：
- DiffDock：盲分子对接，SE(3)等变扩散
- PocketFlow：口袋条件生成，自回归流匹配
- Apo2Mol：层次图扩散，口袋+配体联合生成
- DiffPhore/PIDiff：药效团条件扩散

---

## 三、MediPharma技术实现路线

### Phase 1（当前）：基础Harness
- ✅ 靶点发现（PubMed挖掘+知识图谱+多维评分）
- ✅ 虚拟筛选（DiffDock对接+亲和力评分）
- ✅ 分子生成（SMILES生成+遗传算法优化）
- ✅ ADMET预测（RDKit+规则库）
- ✅ 先导优化（多参数平衡+分子编辑）
- ✅ 知识引擎（RAG+专利+临床试验）
- ✅ Agent编排（Pipeline+DMTA+决策+报告）

### Phase 2（Q2 2026）：扩散模型集成
- 🔲 DiffDock集成（替代AutoDock Vina）
- 🔲 PocketFlow/扩散模型生成（替代遗传算法）
- 🔲 REINVENT 4集成（RL优化+迁移学习）
- 🔲 AlphaFold 3结构预测集成

### Phase 3（Q3-Q4 2026）：端到端自动化
- 🔲 多模态生成（蛋白结构+口袋+配体联合生成）
- 🔲 Active Learning闭环（生成→测试→反馈→模型更新）
- 🔲 Agentic AI（自主决策+自适应Pipeline）
- 🔲 湿实验闭环验证（自动化实验室集成）

---

## 四、开源工具生态

### 4.1 核心依赖
| 工具 | 用途 | 许可证 |
|------|------|--------|
| RDKit | 化学信息学 | BSD |
| REINVENT 4 | 分子生成+RL优化 | Apache 2.0 |
| DiffDock | 分子对接 | MIT |
| PocketFlow | 口袋条件生成 | MIT |
| AlphaFold Server | 蛋白质结构预测 | 学术/非商用 |
| OpenFold3 | 蛋白质结构预测（开源） | Apache 2.0 |
| PyTorch Geometric | GNN | MIT |
| PubChemPy | 数据访问 | MIT |

### 4.2 数据源
| 数据源 | 内容 | 访问方式 |
|--------|------|---------|
| PubChem | 化合物库（1.1亿+） | API/FTP |
| ChEMBL | 生物活性数据 | API |
| PDB | 蛋白质结构 | API |
| AlphaFold DB | 预测结构（2亿+） | API |
| PubMed | 文献 | Entrez API |
| ClinicalTrials.gov | 临床试验 | API |
| DrugBank | 药物数据 | API |
| Open Targets | 靶点-疾病关联 | GraphQL |

---

## 五、竞争优势分析

### vs 竞品
| 维度 | 传统AI制药公司 | MediPharma |
|------|---------------|-----------|
| 技术路线 | 自研模型（高投入） | 开源Harness（低成本） |
| 模型依赖 | 绑定特定模型 | Harness可替换任何模型 |
| 成本结构 | 大团队+高算力 | 一人公司+云端推理 |
| 迭代速度 | 季度级 | 天级 |
| 护城河 | 模型（易被超越） | Harness（私有设计） |

### 核心壁垒
1. **Harness设计专利**：Pipeline架构+评分框架+失败回溯 = 私有IP
2. **数据闭环**：生成→测试→反馈→优化 = 越用越好
3. **全开源工具链**：零许可费+可定制+社区支持
4. **一人公司模式**：90%自动化+极低边际成本

---

*MediPharma v2.0 | 2026年4月*
*Harness理论驱动的AI药物发现平台*
