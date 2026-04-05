"""
MediPharma — 先导优化模块
多参数优化和生成式设计
参考Variational AI Enki模式
"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class OptimizationObjective(Enum):
    """优化目标"""
    POTENCY = "potency"           # 效力
    SELECTIVITY = "selectivity"   # 选择性
    ADMET = "admet"              # ADMET性质
    SOLUBILITY = "solubility"     # 溶解度
    SYNTHESIZABILITY = "synthesizability"  # 合成可行性


@dataclass
class Molecule:
    """分子"""
    molecule_id: str
    smiles: str
    name: str
    properties: Dict[str, float] = field(default_factory=dict)
    generation: int = 0
    parent_id: Optional[str] = None


@dataclass
class OptimizationRound:
    """优化轮次"""
    round_id: int
    input_molecules: List[Molecule]
    output_molecules: List[Molecule]
    objectives: List[OptimizationObjective]
    best_score: float
    improvement: float


@dataclass
class TargetProductProfile:
    """目标产品概要(TPP)"""
    potency_ic50: float  # nM
    selectivity: float   # fold
    solubility: float    # μg/mL
    half_life: float     # hours
    oral_bioavailability: float  # %
    toxicity_risk: str   # low / medium / high


class LeadOptimization:
    """
    先导优化引擎
    参考Variational AI Enki：
    1. 多参数优化（50+性质）
    2. 生成式分子设计
    3. 约束条件优化
    4. TPP驱动设计
    """

    # 优化目标权重
    DEFAULT_WEIGHTS = {
        OptimizationObjective.POTENCY: 0.35,
        OptimizationObjective.SELECTIVITY: 0.25,
        OptimizationObjective.ADMET: 0.20,
        OptimizationObjective.SOLUBILITY: 0.10,
        OptimizationObjective.SYNTHESIZABILITY: 0.10,
    }

    # TPP模板
    TPP_TEMPLATES = {
        "oncology": TargetProductProfile(
            potency_ic50=10.0,
            selectivity=100.0,
            solubility=50.0,
            half_life=12.0,
            oral_bioavailability=40.0,
            toxicity_risk="medium"
        ),
        "rare_disease": TargetProductProfile(
            potency_ic50=50.0,
            selectivity=50.0,
            solubility=100.0,
            half_life=24.0,
            oral_bioavailability=60.0,
            toxicity_risk="low"
        ),
        "cns": TargetProductProfile(
            potency_ic50=20.0,
            selectivity=200.0,
            solubility=20.0,
            half_life=8.0,
            oral_bioavailability=30.0,
            toxicity_risk="low"
        ),
    }

    def __init__(self):
        self.rounds: List[OptimizationRound] = []

    def create_initial_molecules(self, hits: List[Dict]) -> List[Molecule]:
        """从Hit创建初始分子集"""
        molecules = []
        
        for i, hit in enumerate(hits):
            mol = Molecule(
                molecule_id=f"LEAD_{i+1:03d}",
                smiles=hit.get("smiles", ""),
                name=hit.get("name", f"Lead-{i+1}"),
                properties={
                    "potency": hit.get("affinity", -7.0),
                    "selectivity": 50.0,
                    "solubility": 30.0,
                    "synthesizability": 0.7,
                },
                generation=0
            )
            molecules.append(mol)
        
        return molecules

    def optimize(self, molecules: List[Molecule], 
                 tpp: TargetProductProfile,
                 objectives: List[OptimizationObjective] = None,
                 max_rounds: int = 5) -> List[Molecule]:
        """执行多轮优化"""
        if objectives is None:
            objectives = list(self.DEFAULT_WEIGHTS.keys())
        
        current_molecules = molecules
        
        for round_num in range(max_rounds):
            # 生成新分子变体
            new_molecules = self._generate_variants(current_molecules, round_num)
            
            # 评分和排序
            scored = self._score_molecules(new_molecules, tpp, objectives)
            
            # 选择Top分子
            current_molecules = scored[:10]
            
            # 记录优化轮次
            best_score = max(m.properties.get("optimization_score", 0) 
                           for m in current_molecules)
            
            self.rounds.append(OptimizationRound(
                round_id=round_num + 1,
                input_molecules=molecules,
                output_molecules=current_molecules,
                objectives=objectives,
                best_score=best_score,
                improvement=0.05 if round_num > 0 else 0
            ))
        
        return current_molecules

    def _generate_variants(self, molecules: List[Molecule],
                          generation: int) -> List[Molecule]:
        """生成分子变体"""
        variants = []
        
        for mol in molecules:
            # 模拟生成3个变体
            for i in range(3):
                variant = Molecule(
                    molecule_id=f"{mol.molecule_id}_v{generation}_{i}",
                    smiles=mol.smiles,  # 实际应使用生成模型
                    name=f"{mol.name}-Variant-{i}",
                    properties={
                        "potency": mol.properties.get("potency", -7.0) - 0.5,
                        "selectivity": mol.properties.get("selectivity", 50) * 1.2,
                        "solubility": mol.properties.get("solubility", 30) * 1.1,
                        "synthesizability": max(0.5, mol.properties.get("synthesizability", 0.7) - 0.1),
                    },
                    generation=generation + 1,
                    parent_id=mol.molecule_id
                )
                variants.append(variant)
        
        return variants

    def _score_molecules(self, molecules: List[Molecule],
                        tpp: TargetProductProfile,
                        objectives: List[OptimizationObjective]) -> List[Molecule]:
        """评分分子"""
        for mol in molecules:
            score = 0.0
            
            # 效力评分
            potency = mol.properties.get("potency", -7.0)
            potency_score = min(1.0, abs(potency) / abs(tpp.potency_ic50))
            score += potency_score * self.DEFAULT_WEIGHTS.get(
                OptimizationObjective.POTENCY, 0)
            
            # 选择性评分
            selectivity = mol.properties.get("selectivity", 50)
            selectivity_score = min(1.0, selectivity / tpp.selectivity)
            score += selectivity_score * self.DEFAULT_WEIGHTS.get(
                OptimizationObjective.SELECTIVITY, 0)
            
            # 合成可行性
            synth = mol.properties.get("synthesizability", 0.7)
            score += synth * self.DEFAULT_WEIGHTS.get(
                OptimizationObjective.SYNTHESIZABILITY, 0)
            
            mol.properties["optimization_score"] = round(score, 3)
        
        # 按评分排序
        molecules.sort(key=lambda x: x.properties.get("optimization_score", 0),
                      reverse=True)
        
        return molecules

    def get_optimization_report(self) -> Dict:
        """生成优化报告"""
        if not self.rounds:
            return {"error": "No optimization rounds"}
        
        final_round = self.rounds[-1]
        best_mol = max(final_round.output_molecules,
                      key=lambda x: x.properties.get("optimization_score", 0))
        
        return {
            "total_rounds": len(self.rounds),
            "initial_molecules": len(self.rounds[0].input_molecules),
            "final_molecules": len(final_round.output_molecules),
            "best_molecule": {
                "id": best_mol.molecule_id,
                "name": best_mol.name,
                "smiles": best_mol.smiles,
                "score": best_mol.properties.get("optimization_score", 0),
                "potency": best_mol.properties.get("potency", 0),
                "selectivity": best_mol.properties.get("selectivity", 0),
            },
            "optimization_history": [
                {
                    "round": r.round_id,
                    "best_score": r.best_score,
                    "improvement": r.improvement,
                }
                for r in self.rounds
            ],
        }


# ========== 测试 ==========
if __name__ == "__main__":
    optimizer = LeadOptimization()
    
    print("=" * 60)
    print("💡 MediPharma 先导优化测试")
    print("=" * 60)
    
    # 创建初始分子
    hits = [
        {"name": "Hit-1", "smiles": "CCO", "affinity": -8.5},
        {"name": "Hit-2", "smiles": "CCN", "affinity": -7.8},
        {"name": "Hit-3", "smiles": "CCC", "affinity": -7.2},
    ]
    
    initial = optimizer.create_initial_molecules(hits)
    
    # 设置TPP
    tpp = optimizer.TPP_TEMPLATES["rare_disease"]
    
    # 执行优化
    optimized = optimizer.optimize(initial, tpp, max_rounds=3)
    
    # 生成报告
    report = optimizer.get_optimization_report()
    
    print(f"\n📊 优化报告:")
    print(f"   总轮次: {report['total_rounds']}")
    print(f"   初始分子: {report['initial_molecules']}")
    print(f"   最终分子: {report['final_molecules']}")
    
    print(f"\n🏆 最佳分子:")
    best = report['best_molecule']
    print(f"   名称: {best['name']}")
    print(f"   评分: {best['score']}")
    print(f"   效力: {best['potency']} kcal/mol")
    
    print(f"\n📈 优化历史:")
    for h in report['optimization_history']:
        print(f"   第{h['round']}轮: 评分={h['best_score']}")
