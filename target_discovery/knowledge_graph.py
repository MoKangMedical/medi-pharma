"""
知识图谱查询模块
整合DRKG、ChEMBL、UniProt等数据源进行靶点关联分析
"""

import logging
from typing import Optional
from dataclasses import dataclass, asdict

import httpx

logger = logging.getLogger(__name__)

# 外部API端点
CHEMBL_API = "https://www.ebi.ac.uk/chembl/api/data"
UNIPROT_API = "https://rest.uniprot.org"
OPENTARGETS_API = "https://api.platform.opentargets.org/api/v4/graphql"


@dataclass
class TargetInfo:
    """靶点综合信息"""
    gene_symbol: str
    uniprot_id: str
    protein_name: str
    target_type: str  # SINGLE_PROTEIN, PROTEIN_FAMILY, etc.
    organism: str
    known_drugs: int  # 已知药物数
    diseases: list[str]
    pathway: list[str]
    druggability_score: float  # 0-1
    novelty_score: float  # 0-1 (越新越高)


class KnowledgeGraphQuery:
    """知识图谱查询器：多数据源靶点关联"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def query_uniprot(self, gene_symbol: str) -> dict:
        """查询UniProt获取蛋白信息"""
        try:
            resp = self.client.get(
                f"{UNIPROT_API}/uniprotkb/search",
                params={
                    "query": f"gene:{gene_symbol} AND organism_id:9606 AND reviewed:true",
                    "format": "json",
                    "size": 1
                }
            )
            data = resp.json()
            results = data.get("results", [])
            if results:
                entry = results[0]
                return {
                    "uniprot_id": entry.get("primaryAccession", ""),
                    "protein_name": entry.get("proteinDescription", {})
                        .get("recommendedName", {})
                        .get("fullName", {})
                        .get("value", ""),
                    "organism": "Homo sapiens",
                    "function": entry.get("comments", [{}])[0].get("texts", [{}])[0].get("value", "") if entry.get("comments") else ""
                }
        except Exception as e:
            logger.warning(f"UniProt查询失败 ({gene_symbol}): {e}")
        return {}

    def query_chembl_target(self, gene_symbol: str) -> dict:
        """查询ChEMBL获取靶点药物信息"""
        try:
            # 搜索靶点
            resp = self.client.get(
                f"{CHEMBL_API}/target/search.json",
                params={"q": gene_symbol, "limit": 5}
            )
            data = resp.json()
            targets = data.get("targets", [])

            if targets:
                target = targets[0]
                target_chembl_id = target.get("target_chembl_id", "")

                # 获取该靶点的活性化合物数
                act_resp = self.client.get(
                    f"{CHEMBL_API}/activity.json",
                    params={"target_chembl_id": target_chembl_id, "limit": 1}
                )
                act_data = act_resp.json()
                total_activities = act_data.get("page_meta", {}).get("total_count", 0)

                return {
                    "chembl_id": target_chembl_id,
                    "target_type": target.get("target_type", ""),
                    "organism": target.get("organism", ""),
                    "total_activities": total_activities,
                    "pref_name": target.get("pref_name", "")
                }
        except Exception as e:
            logger.warning(f"ChEMBL查询失败 ({gene_symbol}): {e}")
        return {}

    def query_opentargets(self, gene_symbol: str) -> dict:
        """查询OpenTargets获取靶点-疾病关联"""
        query = """
        query TargetAssociations($ensemblId: String!) {
            target(ensemblId: $ensemblId) {
                id
                approvedSymbol
                approvedName
                associatedDiseases(page: {size: 10, index: 0}) {
                    rows {
                        disease {
                            id
                            name
                        }
                        score
                    }
                }
                knownDrugs {
                    uniqueDrugs
                }
            }
        }
        """
        try:
            # 先通过基因符号获取Ensembl ID
            # 简化处理：直接用符号查询
            resp = self.client.post(
                OPENTARGETS_API,
                json={
                    "query": """
                    query SearchTarget($queryString: String!) {
                        search(queryString: $queryString, entityNames: ["target"], page: {size: 1}) {
                            hits {
                                id
                                name
                            }
                        }
                    }
                    """,
                    "variables": {"queryString": gene_symbol}
                }
            )
            search_data = resp.json()
            hits = search_data.get("data", {}).get("search", {}).get("hits", [])

            if hits:
                ensembl_id = hits[0]["id"]

                # 获取详细关联
                resp2 = self.client.post(
                    OPENTARGETS_API,
                    json={"query": query, "variables": {"ensemblId": ensembl_id}}
                )
                target_data = resp2.json().get("data", {}).get("target", {})

                diseases = []
                for row in target_data.get("associatedDiseases", {}).get("rows", []):
                    diseases.append({
                        "name": row["disease"]["name"],
                        "score": row["score"]
                    })

                return {
                    "ensembl_id": ensembl_id,
                    "diseases": diseases,
                    "known_drugs": target_data.get("knownDrugs", {}).get("uniqueDrugs", 0)
                }
        except Exception as e:
            logger.warning(f"OpenTargets查询失败 ({gene_symbol}): {e}")
        return {}

    def get_target_profile(self, gene_symbol: str) -> TargetInfo:
        """获取靶点综合画像"""
        uniprot = self.query_uniprot(gene_symbol)
        chembl = self.query_chembl_target(gene_symbol)
        opentargets = self.query_opentargets(gene_symbol)

        # 计算可药性评分
        druggability = self._calc_druggability(uniprot, chembl, opentargets)

        # 计算新颖性评分（药物越少越新）
        known_drugs = opentargets.get("known_drugs", 0) or chembl.get("total_activities", 0)
        novelty = max(0, 1 - min(known_drugs / 1000, 1.0))

        diseases = [d["name"] for d in opentargets.get("diseases", [])[:5]]

        return TargetInfo(
            gene_symbol=gene_symbol,
            uniprot_id=uniprot.get("uniprot_id", ""),
            protein_name=uniprot.get("protein_name", "") or chembl.get("pref_name", ""),
            target_type=chembl.get("target_type", "SINGLE_PROTEIN"),
            organism="Homo sapiens",
            known_drugs=known_drugs,
            diseases=diseases,
            pathway=[],
            druggability_score=druggability,
            novelty_score=round(novelty, 3)
        )

    def _calc_druggability(self, uniprot: dict, chembl: dict, opentargets: dict) -> float:
        """计算可药性评分"""
        score = 0.5  # 基础分

        # 有已知药物 → 更可药
        if chembl.get("total_activities", 0) > 0:
            score += 0.2

        # 有蛋白功能注释 → 更好
        if uniprot.get("function"):
            score += 0.1

        # 有疾病关联 → 更有价值
        if opentargets.get("diseases"):
            score += 0.1

        # 是单蛋白靶点 → 最可药
        if chembl.get("target_type") == "SINGLE_PROTEIN":
            score += 0.1

        return min(round(score, 3), 1.0)

    def batch_target_profile(self, gene_symbols: list[str]) -> list[dict]:
        """批量获取靶点画像"""
        results = []
        for gene in gene_symbols:
            try:
                profile = self.get_target_profile(gene)
                results.append(asdict(profile))
                import time; time.sleep(0.3)  # 限速
            except Exception as e:
                logger.warning(f"靶点画像失败 ({gene}): {e}")
                results.append({"gene_symbol": gene, "error": str(e)})
        return results
