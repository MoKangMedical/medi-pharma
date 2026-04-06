"""
药代动力学预测模块
吸收(Caco2, HIA)、分布(BBB, PPBR)、代谢(CYP)、排泄(Clearance)
"""

import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)


class PKPredictor:
    """药代动力学预测器"""

    def predict_caco2(self, smiles: str) -> float:
        """
        Caco-2细胞渗透性预测
        log(cm/s), > -5.15 为良好渗透
        """
        props = self._quick_props(smiles)
        base = -5.0

        # LogP适中 → 渗透好
        logp = props.get("logp", 2)
        if 1 <= logp <= 4:
            base += 0.3
        elif logp > 5:
            base -= 0.3

        # TPSA低 → 渗透好
        tpsa = props.get("psa", 80)
        if tpsa < 80:
            base += 0.3
        elif tpsa > 140:
            base -= 0.3

        # HBD少 → 渗透好
        if props.get("hbd", 2) <= 1:
            base += 0.2

        return round(base, 3)

    def predict_hia(self, smiles: str) -> float:
        """
        人体肠道吸收预测 (0-1)
        > 0.3 为可接受
        """
        props = self._quick_props(smiles)
        base = 0.5

        if props.get("mw", 350) < 400:
            base += 0.15
        if 1 <= props.get("logp", 2) <= 4:
            base += 0.15
        if props.get("psa", 80) < 100:
            base += 0.1
        if props.get("hbd", 2) <= 3:
            base += 0.1

        return round(min(max(base, 0.1), 0.99), 3)

    def predict_bioavailability(self, smiles: str) -> float:
        """口服生物利用度预测 (0-1)"""
        hia = self.predict_hia(smiles)
        props = self._quick_props(smiles)
        base = hia * 0.7

        # 大分子生物利用度低
        if props.get("mw", 350) > 500:
            base -= 0.15

        return round(min(max(base, 0.05), 0.95), 3)

    def predict_bbb(self, smiles: str) -> float:
        """
        血脑屏障渗透性预测 (0-1)
        > 0.5 为良好BBB渗透
        """
        props = self._quick_props(smiles)
        base = 0.4

        # 小分子 + 脂溶性好 + 低极性
        if props.get("mw", 350) < 400:
            base += 0.15
        if props.get("psa", 80) < 70:
            base += 0.2
        if props.get("logp", 2) > 2:
            base += 0.1
        if props.get("hbd", 2) <= 1:
            base += 0.15

        return round(min(max(base, 0.05), 0.99), 3)

    def predict_ppbr(self, smiles: str) -> float:
        """
        血浆蛋白结合率预测 (0-1)
        < 0.95 为理想（太高可能导致药物相互作用）
        """
        props = self._quick_props(smiles)
        base = 0.75

        if props.get("logp", 2) > 3:
            base += 0.1
        if props.get("mw", 350) > 400:
            base += 0.05

        return round(min(max(base, 0.3), 0.99), 3)

    def predict_vd(self, smiles: str) -> float:
        """
        分布容积预测 (L/kg)
        0.7-2.0为理想范围
        """
        props = self._quick_props(smiles)
        logp = props.get("logp", 2)

        # Vd与LogP正相关
        vd = 0.5 + logp * 0.2
        return round(max(vd, 0.1), 2)

    def predict_pgp(self, smiles: str) -> float:
        """P-gp底物预测 (0-1)"""
        props = self._quick_props(smiles)
        base = 0.3

        if props.get("mw", 350) > 400:
            base += 0.15
        if props.get("hbd", 2) > 3:
            base += 0.1
        if props.get("psa", 80) > 100:
            base += 0.1

        return round(min(max(base, 0.1), 0.9), 3)

    def predict_clearance(self, smiles: str) -> float:
        """
        清除率预测 (mL/min/kg)
        中等清除率为理想
        """
        props = self._quick_props(smiles)
        base = 5.0

        # 高LogP → 高肝清除
        if props.get("logp", 2) > 4:
            base += 5.0
        if props.get("mw", 350) < 300:
            base += 3.0  # 小分子清除快

        return round(base, 2)

    def predict_half_life(self, smiles: str) -> float:
        """
        半衰期预测 (hours)
        4-24h为理想范围
        """
        clearance = self.predict_clearance(smiles)
        vd = self.predict_vd(smiles)

        # t1/2 = 0.693 * Vd / CL
        cl_lh = clearance * 60 / 1000  # 转换
        if cl_lh > 0:
            half_life = 0.693 * vd / cl_lh
        else:
            half_life = 12.0

        return round(max(half_life, 0.5), 2)

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
                }
        except:
            pass
        return {"mw": 350, "logp": 2.5, "psa": 80, "hbd": 2, "hba": 4}
