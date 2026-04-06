"""
靶点评分模块
综合文献证据、可药性、新颖性等维度对候选靶点排序
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TargetScore:
    """靶点综合评分"""
    gene_symbol: str
    evidence_score: float      # 文献证据强度 (0-1)
    druggability_score: float  # 可药性 (0-1)
    novelty_score: float       # 新颖性 (0-1)
    safety_score: float        # 安全性预估 (0-1)
    commercial_score: float    # 商业价值 (0-1)
    total_score: float         # 综合分 (0-1)
    rank: int
    recommendation: str        # strong / moderate / weak / reject


class TargetScorer:
    """靶点多维评分系统"""

    # 评分权重（可配置）
    DEFAULT_WEIGHTS = {
        "evidence": 0.25,
        "druggability": 0.25,
        "novelty": 0.20,
        "safety": 0.15,
        "commercial": 0.15
    }

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def score_target(
        self,
        gene_symbol: str,
        evidence_strength: str = "moderate",
        total_papers: int = 0,
        known_drugs: int = 0,
        has_3d_structure: bool = False,
        is_essential_gene: bool = False,
        disease_burden: float = 0.5,  # 疾病负担 0-1
        unmet_need: float = 0.5,      # 未满足需求 0-1
    ) -> TargetScore:
        """单靶点评分"""

        # 文献证据分
        evidence_map = {"strong": 0.9, "moderate": 0.5, "weak": 0.2}
        evidence_score = evidence_map.get(evidence_strength, 0.3)
        if total_papers > 50:
            evidence_score = min(evidence_score + 0.1, 1.0)

        # 可药性分
        druggability = 0.5
        if has_3d_structure:
            druggability += 0.2
        if known_drugs > 0:
            druggability += 0.2
        if known_drugs > 10:
            druggability += 0.1
        druggability = min(druggability, 1.0)

        # 新颖性分（药物越少越新）
        novelty = max(0.1, 1.0 - min(known_drugs / 100, 0.9))

        # 安全性预估
        safety = 0.7  # 默认中等
        if is_essential_gene:
            safety -= 0.2  # 必需基因风险更高
        if known_drugs > 5:
            safety += 0.2  # 有已知药物说明可管理
        safety = max(0.1, min(safety, 1.0))

        # 商业价值
        commercial = (disease_burden * 0.5 + unmet_need * 0.5)

        # 综合评分
        total = (
            evidence_score * self.weights["evidence"] +
            druggability * self.weights["druggability"] +
            novelty * self.weights["novelty"] +
            safety * self.weights["safety"] +
            commercial * self.weights["commercial"]
        )

        # 推荐等级
        if total > 0.7:
            rec = "strong"
        elif total > 0.5:
            rec = "moderate"
        elif total > 0.3:
            rec = "weak"
        else:
            rec = "reject"

        return TargetScore(
            gene_symbol=gene_symbol,
            evidence_score=round(evidence_score, 3),
            druggability_score=round(druggability, 3),
            novelty_score=round(novelty, 3),
            safety_score=round(safety, 3),
            commercial_score=round(commercial, 3),
            total_score=round(total, 3),
            rank=0,  # 在批量评分后填充
            recommendation=rec
        )

    def rank_targets(self, targets_data: list[dict]) -> list[TargetScore]:
        """批量评分并排序"""
        scores = []
        for t in targets_data:
            score = self.score_target(
                gene_symbol=t.get("gene_symbol", ""),
                evidence_strength=t.get("evidence_strength", "moderate"),
                total_papers=t.get("total_papers", 0),
                known_drugs=t.get("known_drugs", 0),
                has_3d_structure=t.get("has_3d_structure", False),
                is_essential_gene=t.get("is_essential_gene", False),
                disease_burden=t.get("disease_burden", 0.5),
                unmet_need=t.get("unmet_need", 0.5),
            )
            scores.append(score)

        # 按总分排序
        scores.sort(key=lambda x: x.total_score, reverse=True)
        for i, s in enumerate(scores):
            s.rank = i + 1

        return scores
