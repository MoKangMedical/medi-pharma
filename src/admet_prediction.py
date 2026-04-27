"""
MediPharma — ADMET预测模块
预测化合物的吸收(Absorption)、分布(Distribution)、代谢(Metabolism)、
排泄(Excretion)和毒性(Toxicity)性质
"""

import numpy as np
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ADMETResult:
    """ADMET预测结果"""
    compound_name: str
    smiles: str
    absorption: Dict[str, float]
    distribution: Dict[str, float]
    metabolism: Dict[str, float]
    excretion: Dict[str, float]
    toxicity: Dict[str, float]
    druglikeness: Dict[str, float]
    overall_score: float
    alerts: List[str]


class ADMETPredictor:
    """
    ADMET性质预测引擎
    
    基于分子描述符的ADMET性质预测，包括：
    - 吸收：口服生物利用度、肠渗透性、Caco-2渗透性
    - 分布：血浆蛋白结合率、BBB渗透性、表观分布容积
    - 代谢：CYP450抑制/底物、代谢稳定性
    - 排泄：肾脏清除率、半衰期
    - 毒性：hERG抑制、肝毒性、致突变性
    
    示例：
        >>> predictor = ADMETPredictor()
        >>> result = predictor.predict("COc1cc(NC(=O)C=C)cc(c1)OC", "化合物A")
    """
    
    # CYP450亚型
    CYP_ISOFORMS = ["CYP1A2", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4"]
    
    def __init__(self):
        self._load_rules()
    
    def _load_rules(self):
        """加载预测规则"""
        # 基于Lipinski规则和分子描述符的简化预测模型
        pass
    
    def _calc_molecular_descriptors(self, smiles: str) -> Dict[str, float]:
        """计算分子描述符"""
        # 简化的描述符计算
        mw = len(smiles) * 12.5 + smiles.count('N') * 14 + smiles.count('O') * 16 + smiles.count('S') * 32
        num_aromatic = smiles.count('c')
        num_hba = smiles.count('N') + smiles.count('O')  # 氢键受体
        num_hbd = smiles.count('N') + smiles.count('O')  # 氢键供体（简化）
        num_rotatable = smiles.count('C') // 3  # 可旋转键（简化）
        logp_estimate = (smiles.count('C') * 0.2 + smiles.count('c') * 0.3 - 
                        smiles.count('N') * 0.5 - smiles.count('O') * 0.7 - 
                        smiles.count('F') * 0.3 - smiles.count('Cl') * 0.2)
        tpsa = num_hba * 20 + num_hbd * 15  # 拓扑极性表面积（简化）
        
        return {
            "MW": mw,
            "LogP": logp_estimate,
            "HBA": num_hba,
            "HBD": num_hbd,
            "RotBonds": num_rotatable,
            "TPSA": tpsa,
            "AromaticRings": num_aromatic // 6,
            "NumAtoms": len(smiles)
        }
    
    def predict_absorption(self, descriptors: Dict) -> Dict[str, float]:
        """预测吸收性质"""
        mw = descriptors["MW"]
        logp = descriptors["LogP"]
        hba = descriptors["HBA"]
        hbd = descriptors["HBD"]
        tpsa = descriptors["TPSA"]
        
        # Lipinski规则评估
        lipinski_violations = 0
        if mw > 500: lipinski_violations += 1
        if logp > 5: lipinski_violations += 1
        if hba > 10: lipinski_violations += 1
        if hbd > 5: lipinski_violations += 1
        
        # 口服生物利用度
        bioavailability = max(0, min(1, 0.9 - lipinski_violations * 0.15 + np.random.normal(0, 0.05)))
        
        # Caco-2渗透性
        caco2 = max(0, min(1, 0.7 - (tpsa - 60) * 0.005 + np.random.normal(0, 0.05)))
        
        # 肠渗透性
        intestinal = max(0, min(1, 0.75 - logp * 0.05 + np.random.normal(0, 0.05)))
        
        return {
            "oral_bioavailability": round(bioavailability, 3),
            "caco2_permeability": round(caco2, 3),
            "intestinal_absorption": round(intestinal, 3),
            "lipinski_violations": lipinski_violations,
            "bioavailability_class": "高" if bioavailability > 0.6 else ("中" if bioavailability > 0.3 else "低")
        }
    
    def predict_distribution(self, descriptors: Dict) -> Dict[str, float]:
        """预测分布性质"""
        logp = descriptors["LogP"]
        mw = descriptors["MW"]
        tpsa = descriptors["TPSA"]
        
        # 血浆蛋白结合率
        ppb = min(0.99, max(0.5, 0.7 + logp * 0.04 + np.random.normal(0, 0.03)))
        
        # BBB渗透性
        bbb = max(0, min(1, 0.6 - tpsa * 0.008 + logp * 0.05 + np.random.normal(0, 0.05)))
        
        # 表观分布容积 (L/kg)
        vd = max(0.1, min(20, 1.0 + logp * 0.3 + np.random.normal(0, 0.2)))
        
        return {
            "plasma_protein_binding": round(ppb, 3),
            "bbb_penetration": round(bbb, 3),
            "vd_L_per_kg": round(vd, 2),
            "bbb_class": "高渗透" if bbb > 0.5 else ("中渗透" if bbb > 0.2 else "低渗透"),
            "ppb_class": "高结合" if ppb > 0.9 else ("中结合" if ppb > 0.7 else "低结合")
        }
    
    def predict_metabolism(self, descriptors: Dict) -> Dict[str, float]:
        """预测代谢性质"""
        logp = descriptors["LogP"]
        num_aromatic = descriptors["AromaticRings"]
        
        # CYP450抑制概率
        cyp_inhibition = {}
        for cyp in self.CYP_ISOFORMS:
            # 不同CYP亚型的基础抑制概率
            base = {"CYP1A2": 0.3, "CYP2C9": 0.4, "CYP2C19": 0.35, "CYP2D6": 0.25, "CYP3A4": 0.5}[cyp]
            prob = min(0.95, max(0.05, base + logp * 0.05 + np.random.normal(0, 0.05)))
            cyp_inhibition[cyp] = round(prob, 3)
        
        # CYP底物概率
        cyp_substrate = {}
        for cyp in self.CYP_ISOFORMS:
            prob = min(0.9, max(0.05, 0.3 + np.random.normal(0, 0.1)))
            cyp_substrate[cyp] = round(prob, 3)
        
        # 代谢稳定性
        metabolic_stability = max(0, min(1, 0.7 - logp * 0.03 + np.random.normal(0, 0.05)))
        
        return {
            "cyp_inhibition": cyp_inhibition,
            "cyp_substrate": cyp_substrate,
            "metabolic_stability": round(metabolic_stability, 3),
            "main_metabolic_pathway": "CYP3A4",
            "stability_class": "稳定" if metabolic_stability > 0.6 else ("中等" if metabolic_stability > 0.3 else "不稳定")
        }
    
    def predict_excretion(self, descriptors: Dict) -> Dict[str, float]:
        """预测排泄性质"""
        mw = descriptors["MW"]
        logp = descriptors["LogP"]
        
        # 肾脏清除率 (mL/min/kg)
        renal_clearance = max(0.1, min(15, 2.0 - logp * 0.2 + np.random.normal(0, 0.3)))
        
        # 半衰期 (小时)
        half_life = max(0.5, min(72, 6 + logp * 2 + np.random.normal(0, 1)))
        
        # 总清除率 (mL/min/kg)
        total_clearance = renal_clearance * 1.5 + np.random.normal(0, 0.2)
        
        return {
            "renal_clearance_mL_min_kg": round(renal_clearance, 2),
            "half_life_hours": round(half_life, 1),
            "total_clearance_mL_min_kg": round(max(0.1, total_clearance), 2),
            "elimination_route": "肾脏为主" if renal_clearance > total_clearance * 0.5 else "肝脏为主",
            "half_life_class": "短效" if half_life < 6 else ("中效" if half_life < 24 else "长效")
        }
    
    def predict_toxicity(self, descriptors: Dict) -> Dict[str, float]:
        """预测毒性"""
        logp = descriptors["LogP"]
        mw = descriptors["MW"]
        tpsa = descriptors["TPSA"]
        
        # hERG抑制风险
        herg_risk = min(0.95, max(0.05, 0.3 + logp * 0.06 + np.random.normal(0, 0.05)))
        
        # 肝毒性
        hepatotoxicity = min(0.9, max(0.05, 0.25 + logp * 0.04 + np.random.normal(0, 0.05)))
        
        # 致突变性 (Ames试验)
        mutagenicity = min(0.8, max(0.05, 0.15 + np.random.normal(0, 0.05)))
        
        # 急性毒性 (LD50估算, mg/kg)
        ld50 = max(10, min(5000, 500 - logp * 50 + np.random.normal(0, 50)))
        
        # 总毒性评分（越低越安全）
        toxicity_score = (herg_risk + hepatotoxicity + mutagenicity) / 3
        
        return {
            "herg_inhibition_risk": round(herg_risk, 3),
            "hepatotoxicity_risk": round(hepatotoxicity, 3),
            "mutagenicity_risk": round(mutagenicity, 3),
            "estimated_LD50_mg_kg": round(ld50, 1),
            "toxicity_score": round(toxicity_score, 3),
            "herg_class": "高风险" if herg_risk > 0.5 else ("中风险" if herg_risk > 0.2 else "低风险"),
            "overall_safety": "安全" if toxicity_score < 0.3 else ("警告" if toxicity_score < 0.5 else "危险")
        }
    
    def predict_druglikeness(self, descriptors: Dict) -> Dict[str, float]:
        """评估类药性"""
        mw = descriptors["MW"]
        logp = descriptors["LogP"]
        hba = descriptors["HBA"]
        hbd = descriptors["HBD"]
        tpsa = descriptors["TPSA"]
        rotbonds = descriptors["RotBonds"]
        
        # Lipinski规则
        lipinski = int(mw <= 500 and logp <= 5 and hba <= 10 and hbd <= 5)
        
        # Veber规则
        veber = int(tpsa <= 140 and rotbonds <= 10)
        
        # QED (定量类药性评估)
        qed = min(1.0, max(0.0, 0.5 + lipinski * 0.2 + veber * 0.15 - abs(logp - 2) * 0.05 + np.random.normal(0, 0.03)))
        
        # CNS多参数优化评分
        cns_mpo = min(1.0, max(0.0, 0.6 - tpsa * 0.003 + (2 - abs(logp - 3)) * 0.1 + np.random.normal(0, 0.03)))
        
        return {
            "lipinski_rule": bool(lipinski),
            "veber_rule": bool(veber),
            "qed_score": round(qed, 3),
            "cns_mpo_score": round(cns_mpo, 3),
            "druglikeness_class": "类药" if qed > 0.5 else ("边缘" if qed > 0.3 else "非类药")
        }
    
    def predict(self, smiles: str, compound_name: str = "未知化合物") -> ADMETResult:
        """执行完整ADMET预测"""
        descriptors = self._calc_molecular_descriptors(smiles)
        
        absorption = self.predict_absorption(descriptors)
        distribution = self.predict_distribution(descriptors)
        metabolism = self.predict_metabolism(descriptors)
        excretion = self.predict_excretion(descriptors)
        toxicity = self.predict_toxicity(descriptors)
        druglikeness = self.predict_druglikeness(descriptors)
        
        # 生成警告
        alerts = []
        if absorption["lipinski_violations"] > 0:
            alerts.append(f"⚠️ Lipinski规则违反{absorption['lipinski_violations']}项")
        if toxicity["herg_inhibition_risk"] > 0.5:
            alerts.append("🔴 hERG抑制高风险")
        if toxicity["hepatotoxicity_risk"] > 0.5:
            alerts.append("🔴 肝毒性高风险")
        if metabolism["metabolic_stability"] < 0.3:
            alerts.append("🟡 代谢不稳定")
        if excretion["half_life_hours"] < 2:
            alerts.append("🟡 半衰期过短")
        
        # 综合评分
        overall = (
            absorption["oral_bioavailability"] * 0.2 +
            (1 - toxicity["toxicity_score"]) * 0.3 +
            druglikeness["qed_score"] * 0.2 +
            metabolism["metabolic_stability"] * 0.15 +
            excretion["half_life_hours"] / 72 * 0.15
        )
        
        return ADMETResult(
            compound_name=compound_name,
            smiles=smiles,
            absorption=absorption,
            distribution=distribution,
            metabolism=metabolism,
            excretion=excretion,
            toxicity=toxicity,
            druglikeness=druglikeness,
            overall_score=round(overall, 3),
            alerts=alerts
        )
    
    def batch_predict(self, compounds: List[Dict]) -> List[ADMETResult]:
        """批量预测"""
        results = []
        for comp in compounds:
            result = self.predict(comp.get("smiles", ""), comp.get("name", "未知"))
            results.append(result)
        return results
    
    def summary(self, result: ADMETResult) -> str:
        """生成预测摘要"""
        lines = [
            "=" * 60,
            f"🧪 ADMET预测报告: {result.compound_name}",
            "=" * 60,
            "",
            "📥 吸收 (Absorption):",
            f"  口服生物利用度: {result.absorption['oral_bioavailability']:.1%} ({result.absorption['bioavailability_class']})",
            f"  Caco-2渗透性: {result.absorption['caco2_permeability']:.3f}",
            f"  Lipinski违反: {result.absorption['lipinski_violations']}项",
            "",
            "📦 分布 (Distribution):",
            f"  血浆蛋白结合率: {result.distribution['plasma_protein_binding']:.1%} ({result.distribution['ppb_class']})",
            f"  BBB渗透性: {result.distribution['bbb_penetration']:.3f} ({result.distribution['bbb_class']})",
            f"  Vd: {result.distribution['vd_L_per_kg']:.1f} L/kg",
            "",
            "🔄 代谢 (Metabolism):",
            f"  代谢稳定性: {result.metabolism['metabolic_stability']:.1%} ({result.metabolism['stability_class']})",
            f"  主要代谢途径: {result.metabolism['main_metabolic_pathway']}",
            "",
            "📤 排泄 (Excretion):",
            f"  半衰期: {result.excretion['half_life_hours']:.1f}h ({result.excretion['half_life_class']})",
            f"  消除途径: {result.excretion['elimination_route']}",
            "",
            "☠️ 毒性 (Toxicity):",
            f"  hERG抑制风险: {result.toxicity['herg_inhibition_risk']:.1%} ({result.toxicity['herg_class']})",
            f"  肝毒性风险: {result.toxicity['hepatotoxicity_risk']:.1%}",
            f"  整体安全: {result.toxicity['overall_safety']}",
            "",
            "💊 类药性 (Drug-likeness):",
            f"  QED评分: {result.druglikeness['qed_score']:.3f}",
            f"  Lipinski规则: {'✅ 通过' if result.druglikeness['lipinski_rule'] else '❌ 违反'}",
            "",
            f"📊 综合评分: {result.overall_score:.3f}",
        ]
        
        if result.alerts:
            lines.append("")
            lines.append("⚠️ 警告:")
            for alert in result.alerts:
                lines.append(f"  {alert}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


if __name__ == "__main__":
    predictor = ADMETPredictor()
    
    result = predictor.predict(
        smiles="COc1cc(NC(=O)C=C)cc(c1Nc2nccc(-c3cn(C)c4ncccc34)n2)OC",
        compound_name="奥希替尼"
    )
    print(predictor.summary(result))
