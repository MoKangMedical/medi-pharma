"""
MediPharma — 知识图谱引擎
基于知识图谱的靶点发现和药物重定位
参考BenevolentAI知识图谱平台
"""
import json
from typing import List, Dict, Set
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """节点类型"""
    GENE = "gene"
    DISEASE = "disease"
    DRUG = "drug"
    PROTEIN = "protein"
    PATHWAY = "pathway"
    PHENOTYPE = "phenotype"


class RelationType(Enum):
    """关系类型"""
    ASSOCIATED_WITH = "associated_with"
    TARGETS = "targets"
    TREATS = "treats"
    CAUSES = "causes"
    PARTICIPATES_IN = "participates_in"
    SIMILAR_TO = "similar_to"


@dataclass
class KGNode:
    """知识图谱节点"""
    node_id: str
    node_type: NodeType
    name: str
    properties: Dict = field(default_factory=dict)


@dataclass
class KGEdge:
    """知识图谱边"""
    source_id: str
    target_id: str
    relation: RelationType
    confidence: float = 1.0
    source: str = ""


class KnowledgeEngine:
    """
    知识图谱引擎
    参考BenevolentAI：
    1. 多源数据融合
    2. 知识推理
    3. 靶点发现
    4. 药物重定位
    """

    def __init__(self):
        self.nodes: Dict[str, KGNode] = {}
        self.edges: List[KGEdge] = []
        self._build_graph()

    def _build_graph(self):
        """构建知识图谱"""
        # 基因节点
        genes = [
            KGNode("G001", NodeType.GENE, "CHRNA1", {"chr": "2q24.1"}),
            KGNode("G002", NodeType.GENE, "CHRNE", {"chr": "17p13.1"}),
            KGNode("G003", NodeType.GENE, "SMN1", {"chr": "5q13.2"}),
            KGNode("G004", NodeType.GENE, "GBA1", {"chr": "1q22"}),
            KGNode("G005", NodeType.GENE, "GLA", {"chr": "Xq22.1"}),
            KGNode("G006", NodeType.GENE, "DMD", {"chr": "Xp21.2"}),
            KGNode("G007", NodeType.GENE, "ACHE", {"chr": "7q22.1"}),
            KGNode("G008", NodeType.GENE, "C5", {"chr": "9q33.2"}),
        ]
        
        # 疾病节点
        diseases = [
            KGNode("D001", NodeType.DISEASE, "重症肌无力", {"prevalence": "20/100000"}),
            KGNode("D002", NodeType.DISEASE, "脊髓性肌萎缩症", {"prevalence": "1/10000"}),
            KGNode("D003", NodeType.DISEASE, "戈谢病", {"prevalence": "1/40000"}),
            KGNode("D004", NodeType.DISEASE, "法布雷病", {"prevalence": "1/40000"}),
            KGNode("D005", NodeType.DISEASE, "Duchenne肌营养不良", {"prevalence": "1/3500"}),
        ]
        
        # 药物节点
        drugs = [
            KGNode("DR001", NodeType.DRUG, "溴吡斯的明", {"type": "胆碱酯酶抑制剂"}),
            KGNode("DR002", NodeType.DRUG, "依库珠单抗", {"type": "单克隆抗体"}),
            KGNode("DR003", NodeType.DRUG, "伊米苷酶", {"type": "酶替代疗法"}),
            KGNode("DR004", NodeType.DRUG, "Spinraza", {"type": "反义寡核苷酸"}),
            KGNode("DR005", NodeType.DRUG, "Zolgensma", {"type": "基因疗法"}),
        ]
        
        # 添加节点
        for nodes in [genes, diseases, drugs]:
            for node in nodes:
                self.nodes[node.node_id] = node
        
        # 添加边
        edges = [
            # 基因-疾病关联
            KGEdge("G001", "D001", RelationType.ASSOCIATED_WITH, 0.95, "OMIM"),
            KGEdge("G002", "D001", RelationType.ASSOCIATED_WITH, 0.90, "OMIM"),
            KGEdge("G003", "D002", RelationType.ASSOCIATED_WITH, 0.95, "OMIM"),
            KGEdge("G004", "D003", RelationType.CAUSES, 0.90, "OMIM"),
            KGEdge("G005", "D004", RelationType.CAUSES, 0.90, "OMIM"),
            KGEdge("G006", "D005", RelationType.CAUSES, 0.95, "OMIM"),
            
            # 药物-疾病关联
            KGEdge("DR001", "D001", RelationType.TREATS, 0.85, "DrugBank"),
            KGEdge("DR002", "D001", RelationType.TREATS, 0.80, "ClinicalTrials"),
            KGEdge("DR003", "D003", RelationType.TREATS, 0.90, "DrugBank"),
            KGEdge("DR004", "D002", RelationType.TREATS, 0.85, "FDA"),
            KGEdge("DR005", "D002", RelationType.TREATS, 0.90, "FDA"),
            
            # 药物-靶点关联
            KGEdge("DR001", "G007", RelationType.TARGETS, 0.95, "ChEMBL"),
            KGEdge("DR002", "G008", RelationType.TARGETS, 0.90, "ChEMBL"),
        ]
        
        self.edges.extend(edges)

    def query_related(self, node_id: str, 
                     relation: RelationType = None) -> Dict:
        """查询关联节点"""
        related = {"genes": [], "diseases": [], "drugs": []}
        
        for edge in self.edges:
            if edge.source_id == node_id and (relation is None or edge.relation == relation):
                target = self.nodes.get(edge.target_id)
                if target:
                    key = f"{target.node_type.value}s"
                    related[key].append({
                        "id": target.node_id,
                        "name": target.name,
                        "relation": edge.relation.value,
                        "confidence": edge.confidence,
                    })
            elif edge.target_id == node_id and (relation is None or edge.relation == relation):
                source = self.nodes.get(edge.source_id)
                if source:
                    key = f"{source.node_type.value}s"
                    related[key].append({
                        "id": source.node_id,
                        "name": source.name,
                        "relation": edge.relation.value,
                        "confidence": edge.confidence,
                    })
        
        return related

    def find_drug_repurposing(self, disease: str) -> List[Dict]:
        """药物重定位发现"""
        candidates = []
        
        # 找到疾病节点
        disease_node = None
        for node in self.nodes.values():
            if node.node_type == NodeType.DISEASE and node.name == disease:
                disease_node = node
                break
        
        if not disease_node:
            return candidates
        
        # 找到治疗该疾病的药物
        approved_drugs = set()
        for edge in self.edges:
            if edge.target_id == disease_node.node_id and edge.relation == RelationType.TREATS:
                approved_drugs.add(edge.source_id)
        
        # 找到这些药物的靶点
        target_drugs = {}
        for edge in self.edges:
            if edge.source_id in approved_drugs and edge.relation == RelationType.TARGETS:
                target_id = edge.target_id
                if target_id not in target_drugs:
                    target_drugs[target_id] = []
                target_drugs[target_id].append(edge.source_id)
        
        # 查找靶向相同靶点的其他药物
        for target_id, drug_ids in target_drugs.items():
            for edge in self.edges:
                if (edge.target_id == target_id and 
                    edge.relation == RelationType.TARGETS and
                    edge.source_id not in approved_drugs):
                    
                    drug = self.nodes.get(edge.source_id)
                    target = self.nodes.get(target_id)
                    
                    if drug and target:
                        candidates.append({
                            "drug_id": drug.node_id,
                            "drug_name": drug.name,
                            "target": target.name,
                            "reason": f"共同靶点 {target.name}",
                            "confidence": edge.confidence,
                        })
        
        return candidates

    def discover_targets(self, disease: str) -> List[Dict]:
        """靶点发现"""
        targets = []
        
        # 找到疾病节点
        disease_node = None
        for node in self.nodes.values():
            if node.node_type == NodeType.DISEASE and node.name == disease:
                disease_node = node
                break
        
        if not disease_node:
            return targets
        
        # 找到关联基因
        for edge in self.edges:
            if (edge.target_id == disease_node.node_id and 
                edge.relation in [RelationType.ASSOCIATED_WITH, RelationType.CAUSES]):
                
                gene = self.nodes.get(edge.source_id)
                if gene and gene.node_type == NodeType.GENE:
                    # 检查是否可药
                    druggable = any(
                        e.target_id == gene.node_id and e.relation == RelationType.TARGETS
                        for e in self.edges
                    )
                    
                    targets.append({
                        "gene_id": gene.node_id,
                        "gene_name": gene.name,
                        "evidence": edge.relation.value,
                        "confidence": edge.confidence,
                        "druggable": druggable,
                        "properties": gene.properties,
                    })
        
        # 按置信度排序
        targets.sort(key=lambda x: x["confidence"], reverse=True)
        
        return targets

    def get_graph_stats(self) -> Dict:
        """获取图谱统计"""
        node_types = {}
        for node in self.nodes.values():
            node_types[node.node_type.value] = node_types.get(node.node_type.value, 0) + 1
        
        relation_types = {}
        for edge in self.edges:
            relation_types[edge.relation.value] = relation_types.get(edge.relation.value, 0) + 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "relation_types": relation_types,
        }


# ========== 测试 ==========
if __name__ == "__main__":
    engine = KnowledgeEngine()
    
    print("=" * 60)
    print("📚 MediPharma 知识图谱引擎测试")
    print("=" * 60)
    
    # 图谱统计
    stats = engine.get_graph_stats()
    print(f"\n📊 图谱统计:")
    print(f"   节点: {stats['total_nodes']}")
    print(f"   边: {stats['total_edges']}")
    print(f"   节点类型: {stats['node_types']}")
    
    # 靶点发现
    targets = engine.discover_targets("重症肌无力")
    print(f"\n🎯 重症肌无力靶点:")
    for t in targets:
        print(f"   {t['gene_name']}: {t['evidence']} ({t['confidence']})")
    
    # 药物重定位
    candidates = engine.find_drug_repurposing("重症肌无力")
    print(f"\n💊 药物重定位候选:")
    for c in candidates:
        print(f"   {c['drug_name']} → {c['target']} ({c['reason']})")
    
    # 查询关联
    related = engine.query_related("G001")
    print(f"\n🔍 CHRNA1关联:")
    print(f"   疾病: {[d['name'] for d in related['diseases']]}")
