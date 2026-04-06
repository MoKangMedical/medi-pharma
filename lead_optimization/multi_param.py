"""
先导优化多参数模块
定义优化目标和约束条件
"""

from dataclasses import dataclass


@dataclass
class OptimizationObjective:
    """优化目标"""
    name: str
    weight: float
    direction: str        # maximize / minimize
    threshold: float      # 筛选阈值
    description: str


# 默认优化目标集
DEFAULT_OBJECTIVES = [
    OptimizationObjective(
        name="activity",
        weight=0.35,
        direction="maximize",
        threshold=6.0,
        description="预测活性 pIC50"
    ),
    OptimizationObjective(
        name="selectivity",
        weight=0.15,
        direction="maximize",
        threshold=0.7,
        description="靶点选择性"
    ),
    OptimizationObjective(
        name="solubility",
        weight=0.10,
        direction="maximize",
        threshold=0.5,
        description="水溶性"
    ),
    OptimizationObjective(
        name="permeability",
        weight=0.10,
        direction="maximize",
        threshold=0.5,
        description="细胞渗透性"
    ),
    OptimizationObjective(
        name="metabolic_stability",
        weight=0.10,
        direction="maximize",
        threshold=0.5,
        description="代谢稳定性"
    ),
    OptimizationObjective(
        name="herg_safety",
        weight=0.10,
        direction="minimize",
        threshold=0.5,
        description="hERG抑制风险"
    ),
    OptimizationObjective(
        name="synthesis_score",
        weight=0.10,
        direction="minimize",
        threshold=5.0,
        description="合成可及性评分"
    ),
]

# 罕见病专用目标（更侧重安全性）
RARE_DISEASE_OBJECTIVES = [
    OptimizationObjective("activity", 0.30, "maximize", 5.5, "预测活性"),
    OptimizationObjective("safety", 0.25, "maximize", 0.7, "综合安全性"),
    OptimizationObjective("bbb_penetration", 0.10, "maximize", 0.5, "CNS渗透（如需要）"),
    OptimizationObjective("oral_bioavailability", 0.15, "maximize", 0.3, "口服生物利用度"),
    OptimizationObjective("selectivity", 0.10, "maximize", 0.6, "靶点选择性"),
    OptimizationObjective("synthesis", 0.10, "minimize", 5.0, "合成可及性"),
]
