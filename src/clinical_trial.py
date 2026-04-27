"""
临床试验模拟模块
基于AI的临床试验设计和预测
"""

import logging
from typing import Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class ClinicalTrialDesign:
    """临床试验设计"""
    phase: str
    target_population: int
    primary_endpoint: str
    secondary_endpoints: list
    duration_weeks: int
    dosing_regimen: str
    inclusion_criteria: list
    exclusion_criteria: list


@dataclass
class ClinicalTrialPrediction:
    """临床试验预测"""
    success_probability: float
    expected_enrollment: int
    expected_duration_weeks: int
    risk_factors: list
    recommendations: list


class ClinicalTrialSimulator:
    """
    临床试验模拟器
    基于AI预测临床试验成功率和设计优化
    """
    
    # 历史成功率数据（基于公开数据）
    SUCCESS_RATES = {
        "Phase I": 0.63,
        "Phase II": 0.30,
        "Phase III": 0.58,
        "Phase IV": 0.85,
    }
    
    # 治疗领域成功率
    THERAPEUTIC_AREA_RATES = {
        "肿瘤": 0.05,
        "心血管": 0.10,
        "神经": 0.08,
        "免疫": 0.12,
        "感染": 0.15,
        "代谢": 0.13,
        "罕见病": 0.25,
    }
    
    def __init__(self):
        pass
    
    def design_trial(self, 
                     drug_smiles: str,
                     target: str,
                     indication: str,
                     phase: str = "Phase II") -> ClinicalTrialDesign:
        """
        设计临床试验
        
        Args:
            drug_smiles: 药物SMILES
            target: 靶点
            indication: 适应症
            phase: 临床阶段
            
        Returns:
            临床试验设计
        """
        # 基于阶段确定参数
        if phase == "Phase I":
            return ClinicalTrialDesign(
                phase="Phase I",
                target_population=30,
                primary_endpoint="安全性、耐受性、药代动力学",
                secondary_endpoints=["药效动力学", "生物标志物"],
                duration_weeks=12,
                dosing_regimen="递增剂量",
                inclusion_criteria=["健康志愿者", "年龄18-65岁"],
                exclusion_criteria=["严重基础疾病", "妊娠期"]
            )
        elif phase == "Phase II":
            return ClinicalTrialDesign(
                phase="Phase II",
                target_population=100,
                primary_endpoint="疗效、安全性",
                secondary_endpoints=["生物标志物", "生活质量"],
                duration_weeks=24,
                dosing_regimen="固定剂量",
                inclusion_criteria=[f"{indication}患者", "年龄18-75岁"],
                exclusion_criteria=["严重肝肾功能不全", "妊娠期"]
            )
        elif phase == "Phase III":
            return ClinicalTrialDesign(
                phase="Phase III",
                target_population=500,
                primary_endpoint="疗效、安全性",
                secondary_endpoints=["长期安全性", "成本效益"],
                duration_weeks=52,
                dosing_regimen="固定剂量",
                inclusion_criteria=[f"{indication}患者", "年龄18-80岁"],
                exclusion_criteria=["严重基础疾病", "妊娠期"]
            )
        else:  # Phase IV
            return ClinicalTrialDesign(
                phase="Phase IV",
                target_population=1000,
                primary_endpoint="长期安全性",
                secondary_endpoints=["真实世界疗效", "药物经济学"],
                duration_weeks=104,
                dosing_regimen="常规剂量",
                inclusion_criteria=[f"{indication}患者"],
                exclusion_criteria=[]
            )
    
    def predict_success(self,
                        drug_smiles: str,
                        target: str,
                        indication: str,
                        phase: str,
                        admet_score: float = 0.8) -> ClinicalTrialPrediction:
        """
        预测临床试验成功率
        
        Args:
            drug_smiles: 药物SMILES
            target: 靶点
            indication: 适应症
            phase: 临床阶段
            admet_score: ADMET评分
            
        Returns:
            临床试验预测
        """
        # 基础成功率
        base_rate = self.SUCCESS_RATES.get(phase, 0.5)
        
        # 治疗领域调整
        area_rate = 0.1
        for area, rate in self.THERAPEUTIC_AREA_RATES.items():
            if area in indication:
                area_rate = rate
                break
        
        # ADMET评分调整
        admet_factor = admet_score * 0.3
        
        # 计算最终成功率
        success_probability = (base_rate * 0.4 + area_rate * 0.3 + admet_factor * 0.3)
        success_probability = min(max(success_probability, 0.01), 0.99)
        
        # 风险因素
        risk_factors = []
        if admet_score < 0.6:
            risk_factors.append("ADMET评分较低")
        if phase == "Phase III":
            risk_factors.append("Phase III成功率相对较低")
        if "肿瘤" in indication:
            risk_factors.append("肿瘤领域成功率较低")
        
        # 建议
        recommendations = []
        if admet_score < 0.7:
            recommendations.append("建议优化ADMET性质")
        if phase == "Phase II":
            recommendations.append("建议进行充分的Phase I研究")
        recommendations.append("建议进行生物标志物研究")
        
        return ClinicalTrialPrediction(
            success_probability=round(success_probability, 3),
            expected_enrollment=self.design_trial(drug_smiles, target, indication, phase).target_population,
            expected_duration_weeks=self.design_trial(drug_smiles, target, indication, phase).duration_weeks,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def optimize_design(self,
                        drug_smiles: str,
                        target: str,
                        indication: str) -> dict:
        """
        优化临床试验设计
        
        Args:
            drug_smiles: 药物SMILES
            target: 靶点
            indication: 适应症
            
        Returns:
            优化建议
        """
        # 预测各阶段成功率
        predictions = {}
        for phase in ["Phase I", "Phase II", "Phase III", "Phase IV"]:
            pred = self.predict_success(drug_smiles, target, indication, phase)
            predictions[phase] = pred.success_probability
        
        # 找到最佳起始阶段
        best_phase = max(predictions, key=predictions.get)
        
        return {
            "predictions": predictions,
            "recommended_start_phase": best_phase,
            "overall_success_rate": round(
                predictions["Phase I"] * predictions["Phase II"] * predictions["Phase III"], 3
            ),
            "recommendations": [
                f"建议从{best_phase}开始",
                "建议进行充分的临床前研究",
                "建议进行生物标志物研究",
                "建议进行患者分层"
            ]
        }


def get_clinical_trial_module():
    """获取临床试验模拟模块实例"""
    return ClinicalTrialSimulator()
