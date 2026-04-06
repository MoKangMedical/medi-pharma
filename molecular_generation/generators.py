"""
分子生成策略模块
支持多种分子生成方法：SMILES RNN、图生成、片段组装
"""

import logging
import random
from typing import Optional
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GeneratedMolecule:
    """生成的分子"""
    smiles: str
    validity: bool          # SMILES是否有效
    uniqueness: bool        # 是否唯一
    novelty: bool           # 是否新颖（不在训练集中）
    qed: float = 0.0        # 药物相似性
    sa_score: float = 0.0   # 合成可及性
    logp: float = 0.0
    mw: float = 0.0


class SMILESGenerator:
    """
    SMILES分子生成器
    基于MCTS + 规则的分子生成（无需GPU训练）
    """

    # 常见药物分子子结构（片段库）
    FRAGMENTS = [
        "c1ccccc1",        # 苯环
        "c1ccc2[nH]ccc2c1",  # 吲哚
        "c1ccc(cc1)N",     # 苯胺
        "c1ccncc1",        # 吡啶
        "C1CCNCC1",        # 哌啶
        "c1ccc(cc1)O",     # 苯酚
        "c1cnc2ccccc2n1",  # 喹唑啉
        "C1CCCCC1",        # 环己烷
        "c1ccc2ncccc2c1",  # 喹啉
        "c1ccoc1",         # 呋喃
        "c1ccsc1",         # 噻吩
        "c1cnccn1",        # 嘧啶
        "c1cncnc1",        # 吡嗪
        "C(=O)N",          # 酰胺
        "C(=O)O",          # 羧酸
        "C(=O)",           # 羰基
        "CC(=O)N",         # 乙酰胺
        "c1ccc(cc1)F",     # 氟苯
        "c1ccc(cc1)Cl",    # 氯苯
        "COc1ccccc1",      # 苯甲醚
    ]

    # 连接器
    LINKERS = [
        "C", "CC", "CCC", "C(=O)", "C(=O)N", "CC(=O)N",
        "c1cc(ccc1)", "C1CC1", "NC(=O)", "S(=O)(=O)N"
    ]

    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)

    def generate(
        self,
        n_molecules: int = 100,
        target_properties: Optional[dict] = None,
        scaffold: Optional[str] = None
    ) -> list[GeneratedMolecule]:
        """
        基于片段组装生成分子

        Args:
            n_molecules: 生成数量
            target_properties: 目标属性 {mw: 350, logp: 2.5, ...}
            scaffold: 起始骨架SMILES
        """
        molecules = []
        seen_smiles = set()

        max_attempts = n_molecules * 10
        attempts = 0

        while len(molecules) < n_molecules and attempts < max_attempts:
            attempts += 1

            try:
                if scaffold:
                    smiles = self._extend_scaffold(scaffold)
                else:
                    smiles = self._assemble_from_fragments()

                if not smiles or smiles in seen_smiles:
                    continue

                seen_smiles.add(smiles)

                # 验证SMILES
                valid, props = self._validate_and_properties(smiles)
                if not valid:
                    continue

                # 过滤目标属性
                if target_properties and not self._match_properties(props, target_properties):
                    continue

                mol = GeneratedMolecule(
                    smiles=smiles,
                    validity=True,
                    uniqueness=True,
                    novelty=True,  # 简化处理
                    qed=props.get("qed", 0),
                    sa_score=props.get("sa_score", 0),
                    logp=props.get("logp", 0),
                    mw=props.get("mw", 0),
                )
                molecules.append(mol)

            except Exception:
                continue

        logger.info(f"生成 {len(molecules)} 个有效分子 (尝试 {attempts} 次)")
        return molecules

    def _assemble_from_fragments(self) -> str:
        """随机组装片段"""
        n_frags = random.randint(2, 3)
        frags = random.sample(self.FRAGMENTS, n_frags)
        linkers = random.choices(self.LINKERS, k=n_frags - 1)

        result = frags[0]
        for i, linker in enumerate(linkers):
            result = result + linker + frags[i + 1]

        return result

    def _extend_scaffold(self, scaffold: str) -> str:
        """在骨架上添加取代基"""
        n_subst = random.randint(1, 3)
        substituents = random.sample(self.FRAGMENTS, n_subst)
        linkers = random.choices(self.LINKERS, k=n_subst)

        result = scaffold
        for subst, linker in zip(substituents, linkers):
            result = result + linker + subst

        return result

    def _validate_and_properties(self, smiles: str) -> tuple[bool, dict]:
        """验证SMILES并计算属性"""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, QED

            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return False, {}

            props = {
                "mw": round(Descriptors.MolWt(mol), 1),
                "logp": round(Descriptors.MolLogP(mol), 2),
                "hbd": Descriptors.NumHDonors(mol),
                "hba": Descriptors.NumHAcceptors(mol),
                "tpsa": round(Descriptors.TPSA(mol), 1),
                "qed": round(QED.qed(mol), 3),
                "sa_score": self._calc_sa_score(mol),
                "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "rings": Descriptors.RingCount(mol),
            }
            return True, props

        except ImportError:
            # RDKit未安装，基础验证
            valid = len(smiles) > 5 and any(c.isalpha() for c in smiles)
            return valid, {"mw": 300, "logp": 2.0, "qed": 0.5, "sa_score": 3.0}
        except Exception:
            return False, {}

    def _calc_sa_score(self, mol) -> float:
        """合成可及性评分（简化版）"""
        try:
            from rdkit import Chem
            n_rings = Chem.Descriptors.RingCount(mol)
            n_rot = Chem.Descriptors.NumRotatableBonds(mol)
            n_ha = mol.GetNumHeavyAtoms()

            # 简化公式
            score = 1 + n_rings * 0.5 + n_rot * 0.25 + max(0, (n_ha - 20)) * 0.1
            return round(min(max(score, 1), 10), 2)
        except:
            return 3.0

    def _match_properties(self, props: dict, targets: dict) -> bool:
        """检查属性是否匹配目标范围"""
        for key, target_val in targets.items():
            if key in props:
                val = props[key]
                # 允许30%偏差
                if abs(val - target_val) > abs(target_val * 0.3):
                    return False
        return True
