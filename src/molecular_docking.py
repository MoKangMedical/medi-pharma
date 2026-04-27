"""
MediPharma — 分子对接模块
提供基于配体-受体相互作用的虚拟筛选和打分功能
"""

import numpy as np
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class DockingResult:
    """对接结果"""
    compound_name: str
    target_name: str
    binding_affinity: float  # kcal/mol
    ic50_estimate: float  # nM
    key_interactions: List[str]
    pose_score: float
    confidence: float


@dataclass
class BindingSite:
    """结合位点"""
    name: str
    residues: List[str]
    volume: float  # Å³
    center: Tuple[float, float, float]
    properties: Dict[str, float] = field(default_factory=dict)


class MolecularDocking:
    """
    分子对接引擎
    
    基于评分函数的分子对接模拟，支持：
    - 配体-受体结合亲和力预测
    - 关键相互作用识别
    - IC50估算
    - 虚拟筛选
    
    示例：
        >>> docking = MolecularDocking()
        >>> result = docking.dock("COc1cc(NC(=O)C=C)cc(c1)OC", "EGFR")
        >>> print(result.binding_affinity)
    """
    
    # 常见靶点结合位点信息
    TARGET_SITES = {
        "EGFR": BindingSite(
            name="ATP结合口袋",
            residues=["Met793", "Leu788", "Thr790", "Glu762", "Leu844", "Phe856"],
            volume=450, center=(15.2, 22.8, 30.5),
            properties={"hydrophobicity": 0.65, "hbond_donors": 3, "hbond_acceptors": 4}
        ),
        "HER2": BindingSite(
            name="ATP结合口袋",
            residues=["Met801", "Leu796", "Thr803", "Glu770", "Leu852"],
            volume=480, center=(14.8, 21.5, 29.8),
            properties={"hydrophobicity": 0.60, "hbond_donors": 3, "hbond_acceptors": 5}
        ),
        "ALK": BindingSite(
            name="ATP结合口袋",
            residues=["Met1199", "Leu1196", "Gly1202", "Leu1256", "Phe1271"],
            volume=420, center=(16.1, 23.4, 31.2),
            properties={"hydrophobicity": 0.70, "hbond_donors": 2, "hbond_acceptors": 3}
        ),
        "BTK": BindingSite(
            name="ATP结合口袋",
            residues=["Met477", "Leu474", "Glu475", "Cys481", "Phe540"],
            volume=390, center=(12.5, 18.7, 25.3),
            properties={"hydrophobicity": 0.72, "hbond_donors": 2, "hbond_acceptors": 3}
        ),
        "PARP1": BindingSite(
            name="NAD+结合口袋",
            residues=["Gly863", "Ser904", "Tyr907", "His862", "Asp766"],
            volume=350, center=(10.2, 15.8, 22.4),
            properties={"hydrophobicity": 0.45, "hbond_donors": 5, "hbond_acceptors": 6}
        ),
        "VEGFR2": BindingSite(
            name="ATP结合口袋",
            residues=["Cys919", "Leu889", "Val916", "Glu885", "Phe918"],
            volume=440, center=(13.8, 20.1, 27.6),
            properties={"hydrophobicity": 0.68, "hbond_donors": 3, "hbond_acceptors": 4}
        ),
        "CDK4": BindingSite(
            name="ATP结合口袋",
            residues=["Val96", "Ile12", "Ala41", "Glu61", "Asp97"],
            volume=380, center=(11.5, 17.2, 24.8),
            properties={"hydrophobicity": 0.55, "hbond_donors": 3, "hbond_acceptors": 5}
        ),
        "JAK1": BindingSite(
            name="ATP结合口袋",
            residues=["Leu959", "Gly960", "Glu957", "Val981", "Asp1003"],
            volume=410, center=(14.2, 19.8, 26.5),
            properties={"hydrophobicity": 0.62, "hbond_donors": 3, "hbond_acceptors": 4}
        )
    }
    
    def __init__(self):
        self.results_cache = {}
    
    def _estimate_binding_affinity(self, smiles: str, target: str) -> float:
        """估算结合亲和力（kcal/mol）"""
        # 基于分子描述符的简化评分
        mol_weight = len(smiles) * 12.5  # 粗略估算
        num_rings = smiles.count('c') + smiles.count('C')
        num_hetero = smiles.count('N') + smiles.count('O') + smiles.count('S')
        num_halogen = smiles.count('F') + smiles.count('Cl') + smiles.count('Br')
        
        # 基础亲和力
        base_affinity = -6.0
        
        # 分子量贡献（最优范围300-500）
        if 300 <= mol_weight <= 500:
            mw_score = -1.5
        elif 200 <= mol_weight <= 600:
            mw_score = -0.8
        else:
            mw_score = 0.5
        
        # 芳香环贡献
        ring_score = min(num_rings * -0.3, -1.5)
        
        # 杂原子贡献（氢键）
        hetero_score = min(num_hetero * -0.2, -1.0)
        
        # 卤素贡献
        halogen_score = min(num_halogen * -0.3, -0.9)
        
        # 靶点特异性修正
        target_bonus = {
            "EGFR": -0.5, "HER2": -0.3, "ALK": -0.4, "BTK": -0.6,
            "PARP1": -0.4, "VEGFR2": -0.3, "CDK4": -0.2, "JAK1": -0.3
        }.get(target, 0)
        
        affinity = base_affinity + mw_score + ring_score + hetero_score + halogen_score + target_bonus
        
        # 添加一些随机性
        noise = np.random.normal(0, 0.3)
        return round(affinity + noise, 2)
    
    def _estimate_ic50(self, binding_affinity: float) -> float:
        """从结合亲和力估算IC50（nM）"""
        # ΔG = RT ln(Kd), Kd ≈ IC50
        RT = 0.593  # kcal/mol at 298K
        kd = np.exp(binding_affinity / RT) * 1e9  # 转换为nM
        return round(max(kd, 0.01), 2)
    
    def _identify_interactions(self, smiles: str, target: str) -> List[str]:
        """识别关键相互作用"""
        interactions = []
        
        # 基于SMILES特征识别
        if 'N' in smiles:
            interactions.append("氢键供体-受体相互作用")
        if 'O' in smiles:
            interactions.append("氢键受体相互作用")
        if 'c' in smiles:
            interactions.append("π-π堆积相互作用")
        if 'F' in smiles or 'Cl' in smiles:
            interactions.append("卤键相互作用")
        if 'C' in smiles and 'c' in smiles:
            interactions.append("疏水相互作用")
        
        # 靶点特异性
        site = self.TARGET_SITES.get(target)
        if site:
            if site.properties.get("hydrophobicity", 0) > 0.6:
                interactions.append("疏水口袋填充")
        
        return interactions[:5]
    
    def dock(self, smiles: str, target: str, compound_name: str = "未知化合物") -> DockingResult:
        """执行分子对接"""
        affinity = self._estimate_binding_affinity(smiles, target)
        ic50 = self._estimate_ic50(affinity)
        interactions = self._identify_interactions(smiles, target)
        
        # 姿态评分（结合亲和力的归一化形式）
        pose_score = round(max(0, min(10, -affinity * 1.2)), 2)
        
        # 置信度
        confidence = round(min(0.95, 0.6 + abs(affinity) * 0.05), 2)
        
        result = DockingResult(
            compound_name=compound_name,
            target_name=target,
            binding_affinity=affinity,
            ic50_estimate=ic50,
            key_interactions=interactions,
            pose_score=pose_score,
            confidence=confidence
        )
        
        return result
    
    def virtual_screen(
        self,
        compounds: List[Dict],
        target: str,
        top_n: int = 10
    ) -> List[DockingResult]:
        """虚拟筛选"""
        results = []
        
        for comp in compounds:
            smiles = comp.get("smiles", "")
            name = comp.get("name", "未知")
            result = self.dock(smiles, target, name)
            results.append(result)
        
        # 按结合亲和力排序（越低越好）
        results.sort(key=lambda x: x.binding_affinity)
        
        return results[:top_n]
    
    def batch_dock(
        self,
        compounds: List[Dict],
        targets: List[str]
    ) -> Dict[str, List[DockingResult]]:
        """批量对接（多化合物×多靶点）"""
        all_results = {}
        
        for target in targets:
            all_results[target] = self.virtual_screen(compounds, target)
        
        return all_results
    
    def get_target_info(self, target: str) -> Optional[Dict]:
        """获取靶点结合位点信息"""
        site = self.TARGET_SITES.get(target)
        if site:
            return {
                "name": site.name,
                "residues": site.residues,
                "volume": site.volume,
                "center": site.center,
                "properties": site.properties
            }
        return None
    
    def summary(self, result: DockingResult) -> str:
        """生成对接结果摘要"""
        lines = [
            "=" * 50,
            f"🔬 分子对接结果: {result.compound_name} × {result.target_name}",
            "=" * 50,
            f"结合亲和力: {result.binding_affinity} kcal/mol",
            f"IC50估算: {result.ic50_estimate} nM",
            f"姿态评分: {result.pose_score}/10",
            f"置信度: {result.confidence:.0%}",
            "-" * 50,
            "关键相互作用:",
        ]
        for interaction in result.key_interactions:
            lines.append(f"  • {interaction}")
        
        lines.append("=" * 50)
        return "\n".join(lines)


if __name__ == "__main__":
    docking = MolecularDocking()
    
    # 单个对接
    result = docking.dock(
        smiles="COc1cc(NC(=O)C=C)cc(c1Nc2nccc(-c3cn(C)c4ncccc34)n2)OC",
        target="EGFR",
        compound_name="奥希替尼"
    )
    print(docking.summary(result))
    
    # 虚拟筛选
    compounds = [
        {"name": "化合物A", "smiles": "c1ccc2c(c1)nc(n2)N3CCNCC3"},
        {"name": "化合物B", "smiles": "COc1cc2ncnc(c2cc1OC)Nc3ccc(c(c3)Cl)F"},
        {"name": "化合物C", "smiles": "CC(=O)Nc1ccc(cc1)S(=O)(=O)N"}
    ]
    
    print("\n=== 虚拟筛选结果 ===")
    results = docking.virtual_screen(compounds, "EGFR", top_n=3)
    for r in results:
        print(f"{r.compound_name}: ΔG={r.binding_affinity} kcal/mol, IC50={r.ic50_estimate} nM")
