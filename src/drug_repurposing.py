"""
药物重定位模块
基于分子相似性的老药新用发现
"""

import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RepurposingResult:
    """药物重定位结果"""
    original_drug: str
    original_smiles: str
    original_indication: str
    similar_drugs: list
    potential_new_indications: list
    similarity_scores: list


class DrugRepurposing:
    """
    药物重定位引擎
    基于分子相似性发现老药新用机会
    """
    
    # FDA批准药物数据库（简化版）
    FDA_APPROVED_DRUGS = [
        {"name": "Aspirin", "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O", "indication": "疼痛、炎症、发热"},
        {"name": "Metformin", "smiles": "CN(C)C(=N)NC(=N)N", "indication": "2型糖尿病"},
        {"name": "Atorvastatin", "smiles": "CC(C)C1=C(C(=O)NC2=CC=CC=C2)C(=C(N1CCC(CC(CC(=O)O)O)O)C1=CC=C(C=C1)F)C1=CC=CC=C1", "indication": "高胆固醇血症"},
        {"name": "Omeprazole", "smiles": "COC1=CC2=NC(=CC(=O)N2C=C1)CS(=O)C1=NC2=CC=CC=C2N1C", "indication": "胃食管反流病"},
        {"name": "Losartan", "smiles": "CCCC1=NC(=C(N1CC1=CC=C(C=C1)C1=CC=CC=C1C1=NNN=N1)CO)Cl", "indication": "高血压"},
        {"name": "Amlodipine", "smiles": "CCOC(=O)C1=C(NC(=C(C1C1=CC=CC=C1Cl)C(=O)OC)C)COCCN", "indication": "高血压、心绞痛"},
        {"name": "Ciprofloxacin", "smiles": "C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CCNCC4)F)C(=O)O", "indication": "细菌感染"},
        {"name": "Ibuprofen", "smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "indication": "疼痛、炎症"},
        {"name": "Paracetamol", "smiles": "CC(=O)NC1=CC=C(O)C=C1", "indication": "疼痛、发热"},
        {"name": "Salicylic acid", "smiles": "OC(=O)C1=CC=CC=C1O", "indication": "皮肤病"},
    ]
    
    def __init__(self):
        pass
    
    def find_similar_drugs(self, smiles: str, top_n: int = 5) -> list:
        """
        查找相似药物
        
        Args:
            smiles: 查询分子SMILES
            top_n: 返回数量
            
        Returns:
            相似药物列表
        """
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem, DataStructs
            
            query_mol = Chem.MolFromSmiles(smiles)
            if query_mol is None:
                return []
            
            # 计算查询分子的指纹
            query_fp = AllChem.GetMorganFingerprintAsBitVect(query_mol, 2, nBits=2048)
            
            # 计算与所有药物的相似性
            similarities = []
            for drug in self.FDA_APPROVED_DRUGS:
                drug_mol = Chem.MolFromSmiles(drug["smiles"])
                if drug_mol is None:
                    continue
                
                drug_fp = AllChem.GetMorganFingerprintAsBitVect(drug_mol, 2, nBits=2048)
                similarity = DataStructs.TanimotoSimilarity(query_fp, drug_fp)
                
                similarities.append({
                    "name": drug["name"],
                    "smiles": drug["smiles"],
                    "indication": drug["indication"],
                    "similarity": round(similarity, 3)
                })
            
            # 按相似性排序
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similarities[:top_n]
            
        except Exception as e:
            logger.error(f"相似性搜索失败: {e}")
            return []
    
    def suggest_new_indications(self, smiles: str) -> list:
        """
        建议新的适应症
        
        Args:
            smiles: 查询分子SMILES
            
        Returns:
            潜在新适应症列表
        """
        similar_drugs = self.find_similar_drugs(smiles, top_n=3)
        
        # 收集相似药物的适应症
        indications = []
        for drug in similar_drugs:
            if drug["similarity"] > 0.3:  # 相似性阈值
                indications.append({
                    "indication": drug["indication"],
                    "source_drug": drug["name"],
                    "similarity": drug["similarity"]
                })
        
        return indications
    
    def analyze_drug_likeness(self, smiles: str) -> dict:
        """
        分析类药性
        
        Args:
            smiles: SMILES字符串
            
        Returns:
            类药性分析结果
        """
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, QED
            
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "无效的SMILES"}
            
            # 计算属性
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            qed = QED.qed(mol)
            
            # Lipinski五规则检查
            lipinski_violations = 0
            if mw > 500: lipinski_violations += 1
            if logp > 5: lipinski_violations += 1
            if hbd > 5: lipinski_violations += 1
            if hba > 10: lipinski_violations += 1
            
            # 类药性评分
            drug_likeness_score = qed * 0.4 + (1 - lipinski_violations / 4) * 0.3 + min(tpsa / 140, 1) * 0.3
            
            return {
                "molecular_weight": round(mw, 1),
                "logp": round(logp, 2),
                "hbd": hbd,
                "hba": hba,
                "tpsa": round(tpsa, 1),
                "qed": round(qed, 3),
                "lipinski_violations": lipinski_violations,
                "drug_likeness_score": round(drug_likeness_score, 3),
                "is_drug_like": lipinski_violations <= 1 and qed > 0.3
            }
            
        except Exception as e:
            return {"error": str(e)}


def get_repurposing_module():
    """获取药物重定位模块实例"""
    return DrugRepurposing()
