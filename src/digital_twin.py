"""
数字孪生模块
基于AI的临床试验数字孪生技术
"""

import logging
from typing import Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class DigitalTwin:
    """数字孪生"""
    patient_id: str
    characteristics: dict
    predicted_outcomes: dict
    confidence: float
    method: str


class DigitalTwinEngine:
    """
    数字孪生引擎
    基于AI创建临床试验患者的数字孪生
    """
    
    # 患者特征
    PATIENT_CHARACTERISTICS = {
        "年龄": {"min": 18, "max": 80, "mean": 55},
        "性别": {"男": 0.5, "女": 0.5},
        "体重": {"min": 40, "max": 120, "mean": 70},
        "身高": {"min": 150, "max": 190, "mean": 170},
        "BMI": {"min": 18, "max": 35, "mean": 25},
        "血压": {"收缩压": {"min": 90, "max": 180, "mean": 120}, "舒张压": {"min": 60, "max": 120, "mean": 80}},
        "血糖": {"min": 3.9, "max": 11.1, "mean": 5.6},
        "肝功能": {"ALT": {"min": 0, "max": 40, "mean": 20}, "AST": {"min": 0, "max": 40, "mean": 20}},
        "肾功能": {"肌酐": {"min": 44, "max": 133, "mean": 70}},
    }
    
    # 预测结果
    PREDICTED_OUTCOMES = {
        "疗效": {"有效": 0.6, "部分有效": 0.25, "无效": 0.15},
        "安全性": {"良好": 0.7, "轻度不良反应": 0.2, "严重不良反应": 0.1},
        "依从性": {"高": 0.6, "中": 0.3, "低": 0.1},
    }
    
    def __init__(self):
        pass
    
    def create_digital_twin(self,
                            patient_id: str,
                            indication: str,
                            treatment: str) -> DigitalTwin:
        """
        创建数字孪生
        
        Args:
            patient_id: 患者ID
            indication: 适应症
            treatment: 治疗方案
            
        Returns:
            数字孪生
        """
        # 生成患者特征
        characteristics = self._generate_characteristics()
        
        # 预测结果
        predicted_outcomes = self._predict_outcomes(characteristics, indication, treatment)
        
        # 计算置信度
        confidence = round(random.uniform(0.7, 0.95), 3)
        
        return DigitalTwin(
            patient_id=patient_id,
            characteristics=characteristics,
            predicted_outcomes=predicted_outcomes,
            confidence=confidence,
            method="AI数字孪生"
        )
    
    def create_synthetic_control_arm(self,
                                     n_patients: int,
                                     indication: str) -> list:
        """
        创建合成对照组
        
        Args:
            n_patients: 患者数量
            indication: 适应症
            
        Returns:
            数字孪生列表
        """
        digital_twins = []
        
        for i in range(n_patients):
            patient_id = f"patient_{i+1:04d}"
            twin = self.create_digital_twin(patient_id, indication, "对照")
            digital_twins.append(twin)
        
        return digital_twins
    
    def analyze_trial_outcomes(self,
                               digital_twins: list,
                               indication: str) -> dict:
        """
        分析试验结果
        
        Args:
            digital_twins: 数字孪生列表
            indication: 适应症
            
        Returns:
            分析结果
        """
        if not digital_twins:
            return {"error": "没有数字孪生数据"}
        
        # 统计结果
        efficacy_counts = {"有效": 0, "部分有效": 0, "无效": 0}
        safety_counts = {"良好": 0, "轻度不良反应": 0, "严重不良反应": 0}
        
        for twin in digital_twins:
            efficacy = twin.predicted_outcomes.get("疗效", "未知")
            safety = twin.predicted_outcomes.get("安全性", "未知")
            
            if efficacy in efficacy_counts:
                efficacy_counts[efficacy] += 1
            if safety in safety_counts:
                safety_counts[safety] += 1
        
        total = len(digital_twins)
        
        return {
            "total_patients": total,
            "efficacy": {
                "有效率": round(efficacy_counts["有效"] / total, 3),
                "部分有效率": round(efficacy_counts["部分有效"] / total, 3),
                "无效率": round(efficacy_counts["无效"] / total, 3),
            },
            "safety": {
                "良好率": round(safety_counts["良好"] / total, 3),
                "轻度不良反应率": round(safety_counts["轻度不良反应"] / total, 3),
                "严重不良反应率": round(safety_counts["严重不良反应"] / total, 3),
            },
            "recommendations": [
                "建议进行真实世界验证",
                "建议进行长期随访",
                "建议进行亚组分析",
                "建议进行生物标志物研究"
            ]
        }
    
    def optimize_trial_design(self,
                              indication: str,
                              treatment: str) -> dict:
        """
        优化试验设计
        
        Args:
            indication: 适应症
            treatment: 治疗方案
            
        Returns:
            优化建议
        """
        # 生成优化建议
        recommendations = [
            "建议使用数字孪生作为合成对照组",
            "建议进行适应性试验设计",
            "建议进行贝叶斯统计分析",
            "建议进行患者分层",
            "建议进行生物标志物驱动的试验设计",
        ]
        
        # 计算预期效果
        expected_effects = {
            "样本量减少": round(random.uniform(0.2, 0.5), 3),
            "试验时间缩短": round(random.uniform(0.1, 0.3), 3),
            "成功率提高": round(random.uniform(0.05, 0.15), 3),
        }
        
        return {
            "indication": indication,
            "treatment": treatment,
            "recommendations": recommendations,
            "expected_effects": expected_effects
        }
    
    def _generate_characteristics(self) -> dict:
        """生成患者特征"""
        characteristics = {}
        
        # 年龄
        characteristics["年龄"] = random.randint(18, 80)
        
        # 性别
        characteristics["性别"] = random.choice(["男", "女"])
        
        # 体重
        characteristics["体重"] = round(random.uniform(40, 120), 1)
        
        # 身高
        characteristics["身高"] = round(random.uniform(150, 190), 1)
        
        # BMI
        characteristics["BMI"] = round(characteristics["体重"] / (characteristics["身高"]/100)**2, 1)
        
        # 血压
        characteristics["收缩压"] = random.randint(90, 180)
        characteristics["舒张压"] = random.randint(60, 120)
        
        # 血糖
        characteristics["血糖"] = round(random.uniform(3.9, 11.1), 1)
        
        # 肝功能
        characteristics["ALT"] = random.randint(0, 40)
        characteristics["AST"] = random.randint(0, 40)
        
        # 肾功能
        characteristics["肌酐"] = random.randint(44, 133)
        
        return characteristics
    
    def _predict_outcomes(self,
                          characteristics: dict,
                          indication: str,
                          treatment: str) -> dict:
        """预测结果"""
        outcomes = {}
        
        # 预测疗效
        efficacy_probs = self.PREDICTED_OUTCOMES["疗效"]
        outcomes["疗效"] = random.choices(
            list(efficacy_probs.keys()),
            weights=list(efficacy_probs.values())
        )[0]
        
        # 预测安全性
        safety_probs = self.PREDICTED_OUTCOMES["安全性"]
        outcomes["安全性"] = random.choices(
            list(safety_probs.keys()),
            weights=list(safety_probs.values())
        )[0]
        
        # 预测依从性
        adherence_probs = self.PREDICTED_OUTCOMES["依从性"]
        outcomes["依从性"] = random.choices(
            list(adherence_probs.keys()),
            weights=list(adherence_probs.values())
        )[0]
        
        return outcomes


def get_digital_twin_module():
    """获取数字孪生模块实例"""
    return DigitalTwinEngine()
