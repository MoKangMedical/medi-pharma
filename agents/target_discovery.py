"""
MediPharma — 靶点发现模块
基于多组学数据和知识图谱的靶点发现
参考Insilico PandaOmics
"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class EvidenceLevel(Enum):
    """证据等级"""
    GENETIC = "genetic"           # 遗传学证据
    EXPRESSION = "expression"     # 表达差异
    PATHWAY = "pathway"          # 通路富集
    LITERATURE = "literature"     # 文献支持
    CLINICAL = "clinical"        # 临床证据


@dataclass
class Gene:
    """基因/靶点"""
    gene_id: str
    symbol: str
    name: str
    chromosome: str
    diseases: List[str] = field(default_factory=list)
    druggability: float = 0.0
    evidence_level: EvidenceLevel = EvidenceLevel.LITERATURE
    associations: List[Dict] = field(default_factory=list)


@dataclass
class Pathway:
    """生物通路"""
    pathway_id: str
    name: str
    genes: List[str]
    diseases: List[str]
    enrichment_score: float = 0.0


@dataclass
class TargetCandidate:
    """候选靶点"""
    target_id: str
    gene: Gene
    score: float
    evidence: List[Dict]
    druggability: float
    novelty: float
    validation_status: str  # validated / predicted / novel


class TargetDiscovery:
    """
    靶点发现引擎
    参考Insilico PandaOmics：
    1. 多组学数据分析
    2. 知识图谱挖掘
    3. 文献自动提取
    4. 靶点评分排序
    """

    # 罕见病相关基因库
    DISEASE_GENES = {
        "重症肌无力": [
            Gene("G001", "CHRNA1", "乙酰胆碱受体α1亚基", "2q24.1",
                 ["重症肌无力"], 0.85, EvidenceLevel.GENETIC),
            Gene("G002", "CHRNE", "乙酰胆碱受体ε亚基", "17p13.1",
                 ["重症肌无力"], 0.80, EvidenceLevel.GENETIC),
            Gene("G003", "CHRND", "乙酰胆碱受体δ亚基", "2q33.1",
                 ["重症肌无力"], 0.75, EvidenceLevel.GENETIC),
        ],
        "脊髓性肌萎缩症": [
            Gene("G004", "SMN1", "运动神经元存活基因1", "5q13.2",
                 ["脊髓性肌萎缩症"], 0.95, EvidenceLevel.GENETIC),
            Gene("G005", "SMN2", "运动神经元存活基因2", "5q13.2",
                 ["脊髓性肌萎缩症"], 0.90, EvidenceLevel.GENETIC),
        ],
        "戈谢病": [
            Gene("G006", "GBA1", "β-葡萄糖脑苷脂酶", "1q22",
                 ["戈谢病", "帕金森病"], 0.90, EvidenceLevel.GENETIC),
        ],
        "法布雷病": [
            Gene("G007", "GLA", "α-半乳糖苷酶A", "Xq22.1",
                 ["法布雷病"], 0.90, EvidenceLevel.GENETIC),
        ],
        "DMD": [
            Gene("G008", "DMD", "抗肌萎缩蛋白", "Xp21.2",
                 ["Duchenne肌营养不良"], 0.95, EvidenceLevel.GENETIC),
        ],
    }

    # 生物通路库
    PATHWAYS = {
        "PW001": Pathway("PW001", "胆碱能突触传递", 
                         ["CHRNA1", "CHRNE", "ACHE", "CHAT"],
                         ["重症肌无力"], 0.85),
        "PW002": Pathway("PW002", "神经肌肉接头信号",
                         ["CHRNA1", "CHRNE", "DOK7", "MUSK"],
                         ["重症肌无力", "SMA"], 0.80),
        "PW003": Pathway("PW003", "溶酶体代谢",
                         ["GBA1", "LAMP1", "CTSD"],
                         ["戈谢病"], 0.75),
    }

    def __init__(self):
        self.candidates: List[TargetCandidate] = []

    def analyze_disease(self, disease: str) -> List[TargetCandidate]:
        """分析疾病的潜在靶点"""
        candidates = []
        
        # 从基因库获取
        genes = self.DISEASE_GENES.get(disease, [])
        
        for gene in genes:
            # 计算靶点评分
            score = self._calculate_target_score(gene, disease)
            
            candidate = TargetCandidate(
                target_id=f"T_{gene.gene_id}",
                gene=gene,
                score=score,
                evidence=self._collect_evidence(gene, disease),
                druggability=gene.druggability,
                novelty=0.5,
                validation_status="validated" if gene.evidence_level == EvidenceLevel.GENETIC else "predicted"
            )
            candidates.append(candidate)
        
        # 按评分排序
        candidates.sort(key=lambda x: x.score, reverse=True)
        self.candidates.extend(candidates)
        
        return candidates

    def _calculate_target_score(self, gene: Gene, disease: str) -> float:
        """计算靶点评分"""
        score = 0.0
        
        # 遗传学证据加权
        if gene.evidence_level == EvidenceLevel.GENETIC:
            score += 0.4
        elif gene.evidence_level == EvidenceLevel.EXPRESSION:
            score += 0.3
        elif gene.evidence_level == EvidenceLevel.PATHWAY:
            score += 0.2
        
        # 可药性加权
        score += gene.druggability * 0.3
        
        # 疾病关联加权
        if disease in gene.diseases:
            score += 0.2
        
        return min(score, 1.0)

    def _collect_evidence(self, gene: Gene, disease: str) -> List[Dict]:
        """收集靶点证据"""
        evidence = []
        
        evidence.append({
            "type": "genetic",
            "description": f"{gene.symbol}与{disease}的遗传关联",
            "source": "OMIM",
            "confidence": 0.9
        })
        
        evidence.append({
            "type": "druggability",
            "description": f"{gene.symbol}的可药性评分: {gene.druggability}",
            "source": "ChEMBL",
            "confidence": gene.druggability
        })
        
        return evidence

    def find_pathway_targets(self, pathway_id: str) -> List[Gene]:
        """从通路中发现靶点"""
        pathway = self.PATHWAYS.get(pathway_id)
        if not pathway:
            return []
        
        targets = []
        for symbol in pathway.genes:
            # 从所有疾病中查找基因
            for disease, genes in self.DISEASE_GENES.items():
                for gene in genes:
                    if gene.symbol == symbol:
                        targets.append(gene)
        
        return targets

    def rank_targets(self, disease: str) -> List[Dict]:
        """靶点排序"""
        candidates = self.analyze_disease(disease)
        
        return [
            {
                "rank": i + 1,
                "target_id": c.target_id,
                "gene": c.gene.symbol,
                "name": c.gene.name,
                "score": round(c.score, 3),
                "druggability": round(c.druggability, 3),
                "validation": c.validation_status,
                "evidence_count": len(c.evidence),
            }
            for i, c in enumerate(candidates)
        ]

    def export_targets(self, disease: str) -> Dict:
        """导出靶点数据"""
        ranked = self.rank_targets(disease)
        
        return {
            "disease": disease,
            "total_targets": len(ranked),
            "targets": ranked,
            "summary": {
                "validated": sum(1 for t in ranked if t["validation"] == "validated"),
                "predicted": sum(1 for t in ranked if t["validation"] == "predicted"),
                "avg_score": round(sum(t["score"] for t in ranked) / len(ranked), 3) if ranked else 0,
            }
        }


# ========== 测试 ==========
if __name__ == "__main__":
    discovery = TargetDiscovery()
    
    print("=" * 60)
    print("🎯 MediPharma 靶点发现测试")
    print("=" * 60)
    
    # 分析重症肌无力
    targets = discovery.rank_targets("重症肌无力")
    
    print(f"\n📊 重症肌无力靶点排名:")
    for t in targets:
        print(f"   #{t['rank']} {t['gene']} ({t['name']})")
        print(f"      评分: {t['score']} | 可药性: {t['druggability']} | 状态: {t['validation']}")
    
    # 导出数据
    export = discovery.export_targets("重症肌无力")
    print(f"\n📋 靶点汇总:")
    print(f"   总靶点: {export['total_targets']}")
    print(f"   已验证: {export['summary']['validated']}")
    print(f"   预测: {export['summary']['predicted']}")
