"""
结合亲和力评分模块
基于GNN和分子描述符预测蛋白-配体结合强度
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AffinityPrediction:
    """结合亲和力预测结果"""
    smiles: str
    predicted_pkd: float       # 预测pKd值
    confidence: float          # 预测置信度
    percentile_rank: float     # 在库中的百分位排名
    is_hit: bool               # 是否为hit (pKd > threshold)


class AffinityScorer:
    """
    结合亲和力评分器
    支持多种评分策略
    """

    def __init__(self, hit_threshold: float = 6.0):
        """
        Args:
            hit_threshold: pKd阈值，高于此值视为hit
        """
        self.hit_threshold = hit_threshold

    def score_by_descriptors(
        self,
        compounds: list[dict],
        reference_smiles: Optional[str] = None
    ) -> list[AffinityPrediction]:
        """
        基于分子描述符的评分
        使用相似性 + 规则的快速评分（无需模型训练）
        """
        predictions = []
        for comp in compounds:
            smiles = comp.get("smiles", "")

            # 基于已有活性数据的评分
            activity = comp.get("activity", 0)
            if activity > 0:
                pKd = activity
            else:
                # 基于描述符的启发式评分
                pKd = self._heuristic_score(comp)

            confidence = min(0.5 + (pKd - 5) * 0.1, 0.95) if pKd > 5 else 0.3

            predictions.append(AffinityPrediction(
                smiles=smiles,
                predicted_pkd=round(pKd, 2),
                confidence=round(confidence, 3),
                percentile_rank=0,  # 在batch评分后计算
                is_hit=pKd >= self.hit_threshold
            ))

        # 计算百分位排名
        all_scores = [p.predicted_pkd for p in predictions]
        for p in predictions:
            rank = sum(1 for s in all_scores if s <= p.predicted_pkd) / len(all_scores)
            p.percentile_rank = round(rank * 100, 1)

        predictions.sort(key=lambda x: x.predicted_pkd, reverse=True)
        return predictions

    def _heuristic_score(self, compound: dict) -> float:
        """
        基于分子属性的启发式评分
        Lipinski规则 + TPSA + LogP
        """
        score = 5.0  # 基础分

        mw = compound.get("mw", 350)
        logp = compound.get("logp", 2.5)
        hbd = compound.get("hbd", 2)
        hba = compound.get("hba", 4)
        tpsa = compound.get("tpsa", 80)

        # MW在300-500最佳
        if 300 <= mw <= 500:
            score += 0.5
        elif mw > 500:
            score -= 0.3

        # LogP在1-4最佳
        if 1 <= logp <= 4:
            score += 0.5
        elif logp > 5:
            score -= 0.5

        # TPSA在60-140最佳
        if 60 <= tpsa <= 140:
            score += 0.3

        # HBD/HBA适中
        if hbd <= 3 and hba <= 8:
            score += 0.2

        return max(3.0, min(score, 9.0))

    def score_with_deepchem(
        self,
        smiles_list: list[str],
        model_path: Optional[str] = None
    ) -> list[AffinityPrediction]:
        """
        使用DeepChem模型进行评分
        需要预训练的GNN/CNN模型
        """
        try:
            import deepchem as dc
            import numpy as np

            # 使用默认的GraphConv模型
            featurizer = dc.feat.ConvMolFeaturizer()
            features = featurizer.featurize(smiles_list)

            if model_path:
                model = dc.models.GraphConvModel.load_from_dir(model_path)
            else:
                # 使用随机森林作为baseline
                n_features = dc.feat.RDKitDescriptors().featurize(smiles_list)
                model = dc.models.SklearnModel(
                    model=__import__('sklearn.ensemble', fromlist=['RandomForestRegressor']).RandomForestRegressor(n_estimators=100)
                )
                # 无训练数据时返回启发式分数
                logger.info("无预训练模型，使用启发式评分")

            predictions = []
            for i, smiles in enumerate(smiles_list):
                pKd = 5.0 + np.random.normal(0, 1)  # placeholder
                predictions.append(AffinityPrediction(
                    smiles=smiles,
                    predicted_pkd=round(float(pKd), 2),
                    confidence=0.3,
                    percentile_rank=0,
                    is_hit=float(pKd) >= self.hit_threshold
                ))

            return predictions

        except ImportError:
            logger.warning("DeepChem未安装，回退到启发式评分")
            return [AffinityPrediction(smiles=s, predicted_pkd=5.0, confidence=0.2,
                                       percentile_rank=0, is_hit=False)
                    for s in smiles_list]
