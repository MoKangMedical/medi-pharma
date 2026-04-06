"""
毒性预测模块
hERG心脏毒性、Ames致突变性、LD50、DILI、CYP抑制
基于分子描述符的启发式预测
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ToxicityPredictor:
    """毒性预测器"""

    def predict_herg(self, smiles: str) -> float:
        """hERG通道抑制预测 (0-1, 越高越危险)"""
        risk = self._base_risk(smiles)
        # 高脂溶性 + 大分子量 → hERG风险高
        props = self._quick_props(smiles)
        if props.get("logp", 0) > 4:
            risk += 0.15
        if props.get("mw", 0) > 450:
            risk += 0.1
        if props.get("psa", 0) < 60:
            risk += 0.1
        return round(min(max(risk, 0.05), 0.95), 3)

    def predict_ames(self, smiles: str) -> float:
        """Ames致突变性预测 (0-1, 越高越危险)"""
        risk = self._base_risk(smiles)
        # 芳香胺/硝基化合物 → 高致突变
        alerts = ["N(=O)=O", "[NH2]c1", "Nc1ccc", "c1ccc(N)"]
        for alert in alerts:
            if alert in smiles:
                risk += 0.3
        return round(min(max(risk, 0.05), 0.95), 3)

    def predict_ld50(self, smiles: str) -> float:
        """LD50预测 (log mol/kg, 越高越安全)"""
        base = 2.8
        props = self._quick_props(smiles)
        # 小分子一般更安全
        if props.get("mw", 400) < 350:
            base += 0.3
        if props.get("logp", 3) < 3:
            base += 0.2
        # 含毒性子结构降低
        tox_patterns = ["C#N", "N(=O)=O", "c1ccc(cc1)[N+]", "P(=O)"]
        for p in tox_patterns:
            if p in smiles:
                base -= 0.5
        return round(max(base, 1.0), 3)

    def predict_dili(self, smiles: str) -> float:
        """药物性肝损伤预测 (0-1)"""
        risk = self._base_risk(smiles)
        props = self._quick_props(smiles)
        # 高剂量 + 高LogP → DILI风险高
        if props.get("logp", 0) > 3.5:
            risk += 0.1
        if props.get("mw", 0) > 500:
            risk += 0.1
        return round(min(max(risk, 0.05), 0.95), 3)

    def predict_cardiotoxicity(self, smiles: str) -> float:
        """心脏毒性综合预测"""
        herg = self.predict_herg(smiles)
        # 心脏毒性主要由hERG驱动
        return round(herg * 0.7 + self._base_risk(smiles) * 0.3, 3)

    def predict_cyp_inhibition(self, smiles: str, cyp: str) -> float:
        """
        CYP酶抑制预测 (0-1)
        越低越好（< 0.5表示不太可能抑制）
        """
        risk = self._base_risk(smiles)
        props = self._quick_props(smiles)

        # 不同CYP对不同结构敏感
        if cyp in ["3A4", "2C9"]:
            # 这两个CYP更容易被抑制
            if props.get("logp", 0) > 3:
                risk += 0.15
        if cyp == "2D6":
            # 2D6对碱性氮敏感
            if "N" in smiles and props.get("logp", 0) > 2:
                risk += 0.1

        return round(min(max(risk, 0.05), 0.95), 3)

    def _base_risk(self, smiles: str) -> float:
        """基础风险评分"""
        # 基于分子复杂度的基线
        complexity = len(set(smiles)) / 20  # 字符多样性
        return round(0.2 + complexity * 0.1, 3)

    def _quick_props(self, smiles: str) -> dict:
        """快速计算分子属性"""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                return {
                    "mw": Descriptors.MolWt(mol),
                    "logp": Descriptors.MolLogP(mol),
                    "psa": Descriptors.TPSA(mol),
                    "hbd": Descriptors.NumHDonors(mol),
                    "hba": Descriptors.NumHAcceptors(mol),
                    "rotatable": Descriptors.NumRotatableBonds(mol),
                }
        except:
            pass
        return {"mw": 350, "logp": 2.5, "psa": 80, "hbd": 2, "hba": 4, "rotatable": 4}
