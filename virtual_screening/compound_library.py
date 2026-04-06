"""
化合物库管理模块
整合ChEMBL、PubChem等公开化合物数据源
"""

import logging
from typing import Optional
from dataclasses import dataclass, asdict

import httpx

logger = logging.getLogger(__name__)

CHEMBL_API = "https://www.ebi.ac.uk/chembl/api/data"
PUBCHEM_API = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


@dataclass
class Compound:
    """化合物数据"""
    smiles: str
    chembl_id: str = ""
    pubchem_cid: str = ""
    name: str = ""
    mw: float = 0.0          # 分子量
    logp: float = 0.0        # 脂溶性
    hbd: int = 0             # 氢键供体
    hba: int = 0             # 氢键受体
    tpsa: float = 0.0        # 拓扑极性表面积
    ro5_violations: int = 0  # Lipinski规则违反数
    activity: float = 0.0    # 生物活性 (pIC50等)


class CompoundLibrary:
    """
    化合物库管理器
    从公共数据源获取和管理化合物库
    """

    def __init__(self):
        self.client = httpx.Client(timeout=60.0)

    def fetch_target_compounds(
        self,
        target_chembl_id: str,
        min_activity: float = 6.0,  # pIC50 >= 6
        limit: int = 1000
    ) -> list[Compound]:
        """
        获取某靶点的已知活性化合物
        从ChEMBL获取activity数据
        """
        compounds = []
        offset = 0
        batch_size = min(limit, 500)

        while len(compounds) < limit:
            try:
                resp = self.client.get(
                    f"{CHEMBL_API}/activity.json",
                    params={
                        "target_chembl_id": target_chembl_id,
                        "standard_type": "IC50",
                        "standard_relation": "<",
                        "limit": batch_size,
                        "offset": offset,
                    }
                )
                data = resp.json()
                activities = data.get("activities", [])

                if not activities:
                    break

                for act in activities:
                    value = act.get("standard_value")
                    if value and float(value) > 0:
                        pActivity = 9 - __import__('math').log10(float(value) * 1e-9)
                        if pActivity >= min_activity:
                            compounds.append(Compound(
                                smiles=act.get("canonical_smiles", ""),
                                chembl_id=act.get("molecule_chembl_id", ""),
                                name=act.get("molecule_pref_name", ""),
                                activity=round(pActivity, 2)
                            ))

                offset += batch_size
            except Exception as e:
                logger.error(f"ChEMBL化合物获取失败: {e}")
                break

        # 过滤无SMILES的
        compounds = [c for c in compounds if c.smiles]
        logger.info(f"获取 {len(compounds)} 个活性化合物 (靶点: {target_chembl_id})")
        return compounds[:limit]

    def search_similar_compounds(
        self,
        smiles: str,
        similarity_threshold: float = 0.7,
        limit: int = 100
    ) -> list[Compound]:
        """
        基于SMILES相似性搜索化合物
        使用PubChem Fingerprint/Tanimoto相似性
        """
        try:
            # PubChem相似性搜索
            resp = self.client.get(
                f"{PUBCHEM_API}/compound/fastsimilarity_2d/smiles/{smiles}/JSON",
                params={
                    "Threshold": int(similarity_threshold * 100),
                    "MaxRecords": limit
                }
            )
            data = resp.json()
            id_list = data.get("IdentifierList", {}).get("CID", [])

            if not id_list:
                return []

            # 获取详情
            return self._fetch_pubchem_details(id_list[:limit])

        except Exception as e:
            logger.warning(f"相似性搜索失败: {e}")
            return []

    def _fetch_pubchem_details(self, cids: list[int]) -> list[Compound]:
        """获取PubChem化合物详情"""
        compounds = []
        # 批量获取（每批50个）
        for i in range(0, len(cids), 50):
            batch = cids[i:i + 50]
            cid_str = ",".join(str(c) for c in batch)
            try:
                resp = self.client.get(
                    f"{PUBCHEM_API}/compound/cid/{cid_str}/property/"
                    "IsomericSMILES,MolecularWeight,XLogP,HBondDonorCount,"
                    "HBondAcceptorCount,TPSA,IUPACName/JSON"
                )
                data = resp.json()
                for prop in data.get("PropertyTable", {}).get("Properties", []):
                    compounds.append(Compound(
                        smiles=prop.get("IsomericSMILES", ""),
                        pubchem_cid=str(prop.get("CID", "")),
                        name=prop.get("IUPACName", ""),
                        mw=prop.get("MolecularWeight", 0),
                        logp=prop.get("XLogP", 0),
                        hbd=prop.get("HBondDonorCount", 0),
                        hba=prop.get("HBondAcceptorCount", 0),
                        tpsa=prop.get("TPSA", 0),
                    ))
            except Exception as e:
                logger.warning(f"PubChem详情获取失败 (batch {i}): {e}")

        return compounds

    def apply_lipinski_filter(self, compounds: list[Compound]) -> list[Compound]:
        """Lipinski五规则过滤"""
        filtered = []
        for c in compounds:
            violations = 0
            if c.mw > 500: violations += 1
            if c.logp > 5: violations += 1
            if c.hbd > 5: violations += 1
            if c.hba > 10: violations += 1
            c.ro5_violations = violations
            if violations <= 1:  # 允许1个违反
                filtered.append(c)
        return filtered

    def deduplicate(self, compounds: list[Compound]) -> list[Compound]:
        """基于SMILES去重"""
        seen = set()
        unique = []
        for c in compounds:
            if c.smiles not in seen:
                seen.add(c.smiles)
                unique.append(c)
        return unique
