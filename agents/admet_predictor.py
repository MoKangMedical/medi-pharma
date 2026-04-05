"""
MediPharma — ADMET预测模块
吸收性质、分布、代谢、排泄、毒性预测
参考Insilico Chemistry42 ADMET
"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class ADMETProperty(Enum):
    """ADMET性质"""
    ABSORPTION = "absorption"       # 吸收
    DISTRIBUTION = "distribution"   # 分布
    METABOLISM = "metabolism"       # 代谢
    EXCRETION = "excretion"         # 排泄
    TOXICITY = "toxicity"           # 毒性


@dataclass
class ADMETPrediction:
    """ADMET预测结果"""
    compound_id: str
    smiles: str
    
    # 吸收
    oral_bioavailability: float    # 口服生物利用度 (%)
    caco2_permeability: float      # Caco-2渗透性
    pgp_substrate: bool            # P-gp底物
    bbb_penetration: float         # 血脑屏障穿透
    
    # 分布
    plasma_protein_binding: float  # 血浆蛋白结合率 (%)
    vd: float                      # 分布容积 (L/kg)
    
    # 代谢
    cyp_inhibition: Dict[str, float]  # CYP抑制
    cyp_substrate: Dict[str, bool]    # CYP底物
    half_life: float                  # 半衰期 (h)
    
    # 排泄
    renal_clearance: float         # 肾清除率
    biliary_excretion: float       # 胆汁排泄
    
    # 毒性
    herg_ic50: float               # hERG抑制 (μM)
    hepatotoxicity: float          # 肝毒性风险
    mutagenicity: float            # 致突变性
    ld50: float                    # LD50 (mg/kg)
    
    # 综合评分
    admet_score: float             # 综合ADMET评分
    risk_level: str                # 风险等级


class ADMETPredictor:
    """
    ADMET预测引擎
    参考Insilico Chemistry42 ADMET模块
    50+性质预测
    """

    # CYP酶亚型
    CYP_ISOFORMS = ["CYP1A2", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4"]

    # 预测阈值
    THRESHOLDS = {
        "oral_bioavailability": 30.0,     # >30%为好
        "caco2_permeability": -5.0,       # >-5为好
        "bbb_penetration": 0.3,           # >0.3为能穿透
        "plasma_protein_binding": 90.0,   # <90%为好
        "half_life": 2.0,                 # >2h为好
        "herg_ic50": 10.0,                # >10μM为安全
        "hepatotoxicity": 0.3,            # <0.3为安全
        "mutagenicity": 0.3,              # <0.3为安全
    }

    def __init__(self):
        self.predictions: List[ADMETPrediction] = []

    def predict(self, compound_id: str, smiles: str) -> ADMETPrediction:
        """预测ADMET性质"""
        # 模拟ADMET预测
        prediction = ADMETPrediction(
            compound_id=compound_id,
            smiles=smiles,
            
            # 吸收
            oral_bioavailability=65.0,
            caco2_permeability=-4.5,
            pgp_substrate=False,
            bbb_penetration=0.45,
            
            # 分布
            plasma_protein_binding=85.0,
            vd=1.2,
            
            # 代谢
            cyp_inhibition={
                "CYP1A2": 15.0,
                "CYP2C9": 20.0,
                "CYP2C19": 25.0,
                "CYP2D6": 30.0,
                "CYP3A4": 18.0,
            },
            cyp_substrate={
                "CYP1A2": False,
                "CYP2C9": True,
                "CYP2C19": False,
                "CYP2D6": False,
                "CYP3A4": True,
            },
            half_life=8.5,
            
            # 排泄
            renal_clearance=0.8,
            biliary_excretion=0.3,
            
            # 毒性
            herg_ic50=25.0,
            hepatotoxicity=0.15,
            mutagenicity=0.08,
            ld50=2500.0,
            
            # 综合
            admet_score=0.0,
            risk_level=""
        )
        
        # 计算综合评分
        prediction.admet_score = self._calculate_score(prediction)
        prediction.risk_level = self._assess_risk(prediction)
        
        self.predictions.append(prediction)
        return prediction

    def _calculate_score(self, pred: ADMETPrediction) -> float:
        """计算综合ADMET评分"""
        score = 0.0
        
        # 吸收评分
        if pred.oral_bioavailability > self.THRESHOLDS["oral_bioavailability"]:
            score += 0.15
        if pred.caco2_permeability > self.THRESHOLDS["caco2_permeability"]:
            score += 0.10
        
        # 分布评分
        if pred.plasma_protein_binding < self.THRESHOLDS["plasma_protein_binding"]:
            score += 0.10
        
        # 代谢评分
        if pred.half_life > self.THRESHOLDS["half_life"]:
            score += 0.15
        
        # 毒性评分
        if pred.herg_ic50 > self.THRESHOLDS["herg_ic50"]:
            score += 0.20
        if pred.hepatotoxicity < self.THRESHOLDS["hepatotoxicity"]:
            score += 0.15
        if pred.mutagenicity < self.THRESHOLDS["mutagenicity"]:
            score += 0.15
        
        return round(score, 3)

    def _assess_risk(self, pred: ADMETPrediction) -> str:
        """评估风险等级"""
        if pred.admet_score >= 0.8:
            return "低风险"
        elif pred.admet_score >= 0.6:
            return "中等风险"
        else:
            return "高风险"

    def filter_by_admet(self, compounds: List[Dict], 
                        min_score: float = 0.6) -> List[Dict]:
        """按ADMET过滤化合物"""
        filtered = []
        
        for comp in compounds:
            pred = self.predict(comp.get("id", ""), comp.get("smiles", ""))
            if pred.admet_score >= min_score:
                filtered.append({
                    **comp,
                    "admet_score": pred.admet_score,
                    "risk_level": pred.risk_level,
                })
        
        return filtered

    def get_admet_report(self, prediction: ADMETPrediction) -> Dict:
        """生成ADMET报告"""
        return {
            "compound_id": prediction.compound_id,
            "summary": {
                "admet_score": prediction.admet_score,
                "risk_level": prediction.risk_level,
            },
            "absorption": {
                "oral_bioavailability": f"{prediction.oral_bioavailability}%",
                "caco2_permeability": prediction.caco2_permeability,
                "pgp_substrate": "是" if prediction.pgp_substrate else "否",
                "bbb_penetration": prediction.bbb_penetration,
            },
            "distribution": {
                "plasma_protein_binding": f"{prediction.plasma_protein_binding}%",
                "vd": f"{prediction.vd} L/kg",
            },
            "metabolism": {
                "cyp_inhibition": prediction.cyp_inhibition,
                "half_life": f"{prediction.half_life}h",
            },
            "toxicity": {
                "herg_ic50": f"{prediction.herg_ic50} μM",
                "hepatotoxicity": prediction.hepatotoxicity,
                "mutagenicity": prediction.mutagenicity,
                "ld50": f"{prediction.ld50} mg/kg",
            },
            "assessment": self._generate_assessment(prediction),
        }

    def _generate_assessment(self, pred: ADMETPrediction) -> List[str]:
        """生成评估意见"""
        assessments = []
        
        if pred.oral_bioavailability > 50:
            assessments.append("✅ 口服生物利用度良好")
        else:
            assessments.append("⚠️ 口服生物利用度需优化")
        
        if pred.herg_ic50 > 10:
            assessments.append("✅ hERG抑制风险低")
        else:
            assessments.append("❌ hERG抑制风险高，需注意心脏毒性")
        
        if pred.half_life > 4:
            assessments.append("✅ 半衰期适中")
        else:
            assessments.append("⚠️ 半衰期较短，可能需要频繁给药")
        
        return assessments


# ========== 测试 ==========
if __name__ == "__main__":
    predictor = ADMETPredictor()
    
    print("=" * 60)
    print("🧪 MediPharma ADMET预测测试")
    print("=" * 60)
    
    # 预测ADMET
    prediction = predictor.predict(
        "CMP001",
        "CC(=O)OC1=CC=CC=C1C(=O)O"
    )
    
    # 生成报告
    report = predictor.get_admet_report(prediction)
    
    print(f"\n📊 ADMET报告:")
    print(f"   化合物: {report['compound_id']}")
    print(f"   综合评分: {report['summary']['admet_score']}")
    print(f"   风险等级: {report['summary']['risk_level']}")
    
    print(f"\n💊 吸收:")
    for k, v in report['absorption'].items():
        print(f"   {k}: {v}")
    
    print(f"\n🧬 代谢:")
    print(f"   半衰期: {report['metabolism']['half_life']}")
    
    print(f"\n⚠️ 毒性:")
    print(f"   hERG IC50: {report['toxicity']['herg_ic50']}")
    
    print(f"\n📋 评估:")
    for a in report['assessment']:
        print(f"   {a}")
