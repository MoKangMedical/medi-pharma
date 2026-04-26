"""
MediPharma — 先导化合物优化模块
提供多参数优化（MPO）、分子编辑建议和优化策略
"""

import numpy as np
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    type: str  # "structural_modification", "bioisostere", "scaffold_hop"
    description: str
    expected_effect: Dict[str, str]
    priority: int  # 1=高, 2=中, 3=低
    rationale: str


@dataclass
class OptimizationResult:
    """优化结果"""
    compound_name: str
    original_smiles: str
    mpo_score: float
    property_profile: Dict[str, float]
    suggestions: List[OptimizationSuggestion]
    optimization_route: List[str]
    predicted_improvement: Dict[str, float]


class LeadOptimizer:
    """
    先导化合物优化引擎
    
    支持：
    - 多参数优化评分（MPO）
    - 结构修饰建议
    - 生物电子等排体替换
    - 骨架跳跃
    - ADMET性质优化策略
    
    示例：
        >>> optimizer = LeadOptimizer()
        >>> result = optimizer.optimize("c1ccc2c(c1)nc(n2)N3CCNCC3", "先导化合物A")
    """
    
    # 常见生物电子等排体替换
    BIOISOSTERES = {
        "COOH": ["tetrazole", "SO2NH2", "PO3H2", "acylsulfonamide"],
        "OH": ["NH2", "SH", "CH2OH", "CF3"],
        "NH2": ["OH", "NHSO2CH3", "NHCN"],
        "Cl": ["CF3", "OCF3", "OCH3", "CN"],
        "CH3": ["CF3", "OCH3", "NH2"],
        "phenyl": ["thiophene", "pyridine", "pyrimidine", "cyclohexyl"],
        "ester": ["amide", "oxadiazole", "triazole"],
        "amide": ["sulfonamide", "reverse amide", "oxazole"]
    }
    
    # 常见优化策略
    OPTIMIZATION_STRATEGIES = {
        "potency": [
            "增加与靶点的关键氢键相互作用",
            "优化疏水口袋填充",
            "引入刚性约束减少构象熵损失",
            "利用卤键增强结合",
            "优化π-π堆积相互作用"
        ],
        "selectivity": [
            "利用靶点特异性残基差异",
            "调整分子体积避免非靶点结合",
            "引入选择性口袋的互补基团",
            "优化构象限制提高选择性"
        ],
        "admet": [
            "降低分子量改善口服吸收",
            "减少氢键供体提高渗透性",
            "降低LogP减少hERG风险",
            "引入代谢阻断基团提高稳定性",
            "优化溶解度提高生物利用度"
        ],
        "solubility": [
            "引入极性基团增加溶解度",
            "减少芳香环数量",
            "引入可电离基团",
            "考虑前药策略"
        ]
    }
    
    def __init__(self):
        pass
    
    def _calc_descriptors(self, smiles: str) -> Dict[str, float]:
        """计算分子描述符"""
        mw = len(smiles) * 12.5 + smiles.count('N') * 14 + smiles.count('O') * 16
        logp = (smiles.count('C') * 0.2 + smiles.count('c') * 0.3 - 
                smiles.count('N') * 0.5 - smiles.count('O') * 0.7)
        hba = smiles.count('N') + smiles.count('O')
        hbd = smiles.count('N') + smiles.count('O')
        tpsa = hba * 20 + hbd * 15
        rotbonds = smiles.count('C') // 3
        aromatic = smiles.count('c') // 6
        
        return {
            "MW": mw, "LogP": logp, "HBA": hba, "HBD": hbd,
            "TPSA": tpsa, "RotBonds": rotbonds, "AromaticRings": aromatic
        }
    
    def calculate_mpo(self, smiles: str, weights: Optional[Dict[str, float]] = None) -> float:
        """
        计算多参数优化评分（MPO）
        
        基于Wager et al. (2010) CNS MPO评分体系的改进版
        """
        desc = self._calc_descriptors(smiles)
        
        if weights is None:
            weights = {
                "MW": 0.20, "LogP": 0.20, "TPSA": 0.15,
                "HBD": 0.15, "HBA": 0.10, "RotBonds": 0.10,
                "AromaticRings": 0.10
            }
        
        # 各项评分（0-1范围）
        scores = {}
        
        # MW: 200-400最优
        mw = desc["MW"]
        scores["MW"] = max(0, min(1, 1 - abs(mw - 350) / 200))
        
        # LogP: 1-3最优
        logp = desc["LogP"]
        scores["LogP"] = max(0, min(1, 1 - abs(logp - 2) / 4))
        
        # TPSA: 60-100最优
        tpsa = desc["TPSA"]
        scores["TPSA"] = max(0, min(1, 1 - abs(tpsa - 80) / 60))
        
        # HBD: 0-2最优
        scores["HBD"] = max(0, min(1, 1 - max(0, desc["HBD"] - 2) / 3))
        
        # HBA: 2-5最优
        hba = desc["HBA"]
        scores["HBA"] = max(0, min(1, 1 - abs(hba - 3.5) / 5))
        
        # RotBonds: 0-5最优
        scores["RotBonds"] = max(0, min(1, 1 - max(0, desc["RotBonds"] - 5) / 5))
        
        # AromaticRings: 1-2最优
        ar = desc["AromaticRings"]
        scores["AromaticRings"] = max(0, min(1, 1 - abs(ar - 1.5) / 2))
        
        mpo = sum(scores[k] * weights[k] for k in weights)
        return round(mpo, 3)
    
    def analyze_properties(self, smiles: str) -> Dict[str, Dict]:
        """分析属性概况"""
        desc = self._calc_descriptors(smiles)
        
        analysis = {}
        
        # 分子量
        mw = desc["MW"]
        if mw > 500:
            analysis["MW"] = {"value": mw, "status": "🔴 超标", "suggestion": "考虑去除不必要的基团"}
        elif mw > 450:
            analysis["MW"] = {"value": mw, "status": "🟡 偏高", "suggestion": "接近Lipinski上限"}
        else:
            analysis["MW"] = {"value": mw, "status": "✅ 正常", "suggestion": ""}
        
        # LogP
        logp = desc["LogP"]
        if logp > 5:
            analysis["LogP"] = {"value": logp, "status": "🔴 超标", "suggestion": "引入极性基团降低脂溶性"}
        elif logp > 4:
            analysis["LogP"] = {"value": logp, "status": "🟡 偏高", "suggestion": "考虑增加极性"}
        elif logp < 0:
            analysis["LogP"] = {"value": logp, "status": "🟡 偏低", "suggestion": "渗透性可能不足"}
        else:
            analysis["LogP"] = {"value": logp, "status": "✅ 正常", "suggestion": ""}
        
        # TPSA
        tpsa = desc["TPSA"]
        if tpsa > 140:
            analysis["TPSA"] = {"value": tpsa, "status": "🔴 超标", "suggestion": "口服吸收可能受限"}
        elif tpsa > 100:
            analysis["TPSA"] = {"value": tpsa, "status": "🟡 偏高", "suggestion": "渗透性可能受影响"}
        else:
            analysis["TPSA"] = {"value": tpsa, "status": "✅ 正常", "suggestion": ""}
        
        return analysis
    
    def generate_suggestions(self, smiles: str, optimization_goal: str = "admet") -> List[OptimizationSuggestion]:
        """生成优化建议"""
        desc = self._calc_descriptors(smiles)
        suggestions = []
        
        # 基于属性的建议
        if desc["MW"] > 500:
            suggestions.append(OptimizationSuggestion(
                type="structural_modification",
                description="分子量过高，建议去除不必要的取代基或简化结构",
                expected_effect={"MW": "降低50-100", "吸收": "改善"},
                priority=1,
                rationale="Lipinski规则要求MW≤500"
            ))
        
        if desc["LogP"] > 5:
            suggestions.append(OptimizationSuggestion(
                type="structural_modification",
                description="LogP过高，建议引入极性基团（如-OH, -NH2）或用杂环替换苯环",
                expected_effect={"LogP": "降低1-2", "hERG风险": "降低"},
                priority=1,
                rationale="高LogP与hERG抑制和肝毒性相关"
            ))
        
        if desc["TPSA"] > 140:
            suggestions.append(OptimizationSuggestion(
                type="structural_modification",
                description="TPSA过高，建议减少极性基团数量或用非极性基团替代",
                expected_effect={"TPSA": "降低20-40", "渗透性": "改善"},
                priority=1,
                rationale="高TPSA影响口服吸收和BBB渗透"
            ))
        
        if desc["HBD"] > 5:
            suggestions.append(OptimizationSuggestion(
                type="bioisostere",
                description="氢键供体过多，建议用生物电子等排体替换部分-NH/-OH",
                expected_effect={"HBD": "减少1-2", "渗透性": "改善"},
                priority=2,
                rationale="HBD>5影响膜渗透性"
            ))
        
        # 基于优化目标的建议
        if optimization_goal in self.OPTIMIZATION_STRATEGIES:
            strategies = self.OPTIMIZATION_STRATEGIES[optimization_goal]
            for i, strategy in enumerate(strategies[:3]):
                suggestions.append(OptimizationSuggestion(
                    type="strategy",
                    description=strategy,
                    expected_effect={optimization_goal: "预期改善"},
                    priority=2,
                    rationale=f"基于{optimization_goal}优化策略"
                ))
        
        # 生物电子等排体建议
        for group, replacements in self.BIOISOSTERES.items():
            if group.lower() in smiles.lower():
                suggestions.append(OptimizationSuggestion(
                    type="bioisostere",
                    description=f"检测到{group}基团，可考虑替换为: {', '.join(replacements[:3])}",
                    expected_effect={"选择性": "可能改善", "代谢稳定性": "可能改善"},
                    priority=3,
                    rationale=f"{group}的生物电子等排体替换"
                ))
        
        # 按优先级排序
        suggestions.sort(key=lambda x: x.priority)
        
        return suggestions
    
    def optimize(
        self,
        smiles: str,
        compound_name: str = "未知化合物",
        optimization_goal: str = "admet"
    ) -> OptimizationResult:
        """执行先导化合物优化分析"""
        mpo = self.calculate_mpo(smiles)
        properties = self.analyze_properties(smiles)
        suggestions = self.generate_suggestions(smiles, optimization_goal)
        
        # 构建优化路线图
        route = [
            "1. 评估当前属性概况",
            "2. 识别关键问题属性",
            "3. 应用结构修饰/生物电子等排体替换",
            "4. 重新评估ADMET性质",
            "5. 迭代优化至达到标准"
        ]
        
        # 预测改进幅度
        predicted_improvement = {
            "MW": -50 if properties.get("MW", {}).get("status", "").startswith("🔴") else 0,
            "LogP": -1.0 if properties.get("LogP", {}).get("status", "").startswith("🔴") else 0,
            "TPSA": -20 if properties.get("TPSA", {}).get("status", "").startswith("🔴") else 0,
            "MPO_improvement": 0.1 if mpo < 0.6 else 0.05
        }
        
        return OptimizationResult(
            compound_name=compound_name,
            original_smiles=smiles,
            mpo_score=mpo,
            property_profile={k: v.get("value", 0) for k, v in properties.items()},
            suggestions=suggestions,
            optimization_route=route,
            predicted_improvement=predicted_improvement
        )
    
    def compare_compounds(self, compounds: List[Dict]) -> List[Dict]:
        """比较多化合物的优化潜力"""
        results = []
        for comp in compounds:
            smiles = comp.get("smiles", "")
            name = comp.get("name", "未知")
            mpo = self.calculate_mpo(smiles)
            desc = self._calc_descriptors(smiles)
            
            results.append({
                "name": name,
                "smiles": smiles,
                "mpo_score": mpo,
                "MW": desc["MW"],
                "LogP": desc["LogP"],
                "TPSA": desc["TPSA"],
                "optimization_potential": round(1 - mpo, 3)
            })
        
        results.sort(key=lambda x: x["mpo_score"], reverse=True)
        return results
    
    def summary(self, result: OptimizationResult) -> str:
        """生成优化报告摘要"""
        lines = [
            "=" * 60,
            f"⚗️ 先导化合物优化报告: {result.compound_name}",
            "=" * 60,
            f"MPO评分: {result.mpo_score:.3f}/1.000",
            "",
            "📊 属性概况:",
        ]
        
        for prop, info in result.property_profile.items():
            lines.append(f"  {prop}: {info}")
        
        lines.append("")
        lines.append("💡 优化建议:")
        for i, sug in enumerate(result.suggestions[:5], 1):
            lines.append(f"  {i}. [{sug.type}] {sug.description}")
            lines.append(f"     预期效果: {sug.expected_effect}")
        
        lines.append("")
        lines.append("🗺️ 优化路线图:")
        for step in result.optimization_route:
            lines.append(f"  {step}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


if __name__ == "__main__":
    optimizer = LeadOptimizer()
    
    result = optimizer.optimize(
        smiles="COc1cc(NC(=O)C=C)cc(c1Nc2nccc(-c3cn(C)c4ncccc34)n2)OC",
        compound_name="奥希替尼",
        optimization_goal="admet"
    )
    print(optimizer.summary(result))
