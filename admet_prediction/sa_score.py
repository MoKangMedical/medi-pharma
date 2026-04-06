"""
合成可及性评分模块
评估分子的合成难度
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SAScorer:
    """合成可及性评分器 (1-10, 越低越容易合成)"""

    # 常见容易合成的子结构
    EASY_FRAGMENTS = [
        "c1ccccc1", "C(=O)O", "C(=O)N", "CC", "CO", "CN",
        "c1ccncc1", "C1CCNCC1", "c1ccc(cc1)N", "c1ccc(cc1)O"
    ]

    # 难合成子结构
    HARD_FRAGMENTS = [
        "P(=O)(O)O", "B(O)O", "[Si]", "C#C", "C=C=C",
        "[nH]1cccc1c2cccc[nH+]2",  # 复杂杂环
    ]

    def score(self, smiles: str) -> dict:
        """
        计算合成可及性评分

        Returns:
            dict: {
                sa_score: float (1-10),
                accessibility: str (easy/moderate/hard),
                n_steps: int (预估合成步骤),
                factors: list[str] (影响因素)
            }
        """
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors

            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {
                    "sa_score": 10.0,
                    "accessibility": "invalid",
                    "n_steps": 99,
                    "factors": ["无效SMILES"]
                }

            score = 1.0
            factors = []

            # 重原子数
            n_heavy = mol.GetNumHeavyAtoms()
            if n_heavy > 30:
                score += 1.5
                factors.append(f"重原子数多({n_heavy})")
            elif n_heavy > 20:
                score += 0.8

            # 环数
            n_rings = Descriptors.RingCount(mol)
            if n_rings > 4:
                score += 1.5
                factors.append(f"环数多({n_rings})")
            elif n_rings > 2:
                score += 0.5

            # 手性中心
            n_stereo = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True))
            if n_stereo > 2:
                score += 1.0
                factors.append(f"手性中心多({n_stereo})")

            # 可旋转键
            n_rot = Descriptors.NumRotatableBonds(mol)
            if n_rot > 8:
                score += 0.8
                factors.append(f"可旋转键多({n_rot})")

            # 杂原子
            n_hetero = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() not in [1, 6])
            if n_hetero > 6:
                score += 0.5

            # 特殊元素
            special_elements = {"P", "S", "B", "Si", "Se", "Metal"}
            for atom in mol.GetAtoms():
                symbol = atom.GetSymbol()
                if symbol in special_elements:
                    score += 0.3
                    factors.append(f"含特殊元素({symbol})")

            # 大环
            ring_info = mol.GetRingInfo()
            for ring in ring_info.AtomRings():
                if len(ring) > 8:
                    score += 0.5
                    factors.append("含大环")
                    break

            # 螺环
            if ring_info.NumRings() > 2:
                # 检查螺环
                bridgeheads = Chem.GetSSSR(mol)

            score = min(max(score, 1.0), 10.0)

            # 估算合成步骤
            n_steps = max(3, int(score * 1.5))

            # 可及性等级
            if score <= 3.5:
                accessibility = "easy"
            elif score <= 6.0:
                accessibility = "moderate"
            else:
                accessibility = "hard"

            return {
                "sa_score": round(score, 2),
                "accessibility": accessibility,
                "n_steps": n_steps,
                "factors": factors if factors else ["标准药物分子结构"]
            }

        except ImportError:
            # RDKit未安装
            return {
                "sa_score": 4.0,
                "accessibility": "moderate",
                "n_steps": 6,
                "factors": ["RDKit未安装，使用默认评分"]
            }
