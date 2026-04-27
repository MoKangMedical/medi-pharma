"""
知识图谱可视化模块
基于Streamlit的交互式知识图谱展示
"""

import logging
from typing import Optional
import json

logger = logging.getLogger(__name__)


def generate_knowledge_graph_html(nodes: list, edges: list, 
                                  width: int = 800, height: int = 600) -> str:
    """
    生成知识图谱的HTML代码
    
    Args:
        nodes: 节点列表 [{"id": "1", "label": "EGFR", "type": "target", "size": 30}]
        edges: 边列表 [{"from": "1", "to": "2", "label": "inhibits", "color": "#ff0000"}]
        width: 宽度
        height: 高度
        
    Returns:
        HTML代码字符串
    """
    # 节点颜色映射
    node_colors = {
        "target": "#667eea",
        "disease": "#e94560",
        "drug": "#00b894",
        "pathway": "#fdcb6e",
        "protein": "#a29bfe",
        "gene": "#fab1a0",
    }
    
    # 生成节点数据
    nodes_js = []
    for node in nodes:
        node_type = node.get("type", "default")
        color = node_colors.get(node_type, "#95a5a6")
        nodes_js.append({
            "id": node["id"],
            "label": node["label"],
            "size": node.get("size", 20),
            "color": color,
            "title": node.get("description", node["label"])
        })
    
    # 生成边数据
    edges_js = []
    for edge in edges:
        edges_js.append({
            "from": edge["from"],
            "to": edge["to"],
            "label": edge.get("label", ""),
            "color": edge.get("color", "#95a5a6"),
            "arrows": "to"
        })
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            #graph-container {{
                width: {width}px;
                height: {height}px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }}
        </style>
    </head>
    <body>
        <div id="graph-container"></div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({json.dumps(nodes_js)});
            var edges = new vis.DataSet({json.dumps(edges_js)});
            var container = document.getElementById('graph-container');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    font: {{ size: 14, color: '#333' }},
                    borderWidth: 2,
                    shadow: true
                }},
                edges: {{
                    font: {{ size: 12, color: '#666', strokeWidth: 0 }},
                    smooth: {{ type: 'continuous' }},
                    shadow: true
                }},
                physics: {{
                    stabilization: {{ iterations: 100 }},
                    barnesHut: {{ gravitationalConstant: -2000, springConstant: 0.001 }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    
    return html


def create_target_disease_graph(target_name: str, diseases: list) -> str:
    """
    创建靶点-疾病知识图谱
    
    Args:
        target_name: 靶点名称
        diseases: 疾病列表
        
    Returns:
        HTML代码字符串
    """
    nodes = [{"id": "target", "label": target_name, "type": "target", "size": 40}]
    edges = []
    
    for i, disease in enumerate(diseases):
        disease_id = f"disease_{i}"
        nodes.append({
            "id": disease_id,
            "label": disease,
            "type": "disease",
            "size": 25
        })
        edges.append({
            "from": "target",
            "to": disease_id,
            "label": "associated_with",
            "color": "#e94560"
        })
    
    return generate_knowledge_graph_html(nodes, edges)


def create_drug_target_graph(drug_name: str, targets: list) -> str:
    """
    创建药物-靶点知识图谱
    
    Args:
        drug_name: 药物名称
        targets: 靶点列表
        
    Returns:
        HTML代码字符串
    """
    nodes = [{"id": "drug", "label": drug_name, "type": "drug", "size": 40}]
    edges = []
    
    for i, target in enumerate(targets):
        target_id = f"target_{i}"
        nodes.append({
            "id": target_id,
            "label": target,
            "type": "target",
            "size": 25
        })
        edges.append({
            "from": "drug",
            "to": target_id,
            "label": "binds_to",
            "color": "#667eea"
        })
    
    return generate_knowledge_graph_html(nodes, edges)


def create_pathway_graph(pathway_name: str, genes: list) -> str:
    """
    创建通路-基因知识图谱
    
    Args:
        pathway_name: 通路名称
        genes: 基因列表
        
    Returns:
        HTML代码字符串
    """
    nodes = [{"id": "pathway", "label": pathway_name, "type": "pathway", "size": 40}]
    edges = []
    
    for i, gene in enumerate(genes):
        gene_id = f"gene_{i}"
        nodes.append({
            "id": gene_id,
            "label": gene,
            "type": "gene",
            "size": 20
        })
        edges.append({
            "from": "pathway",
            "to": gene_id,
            "label": "contains",
            "color": "#fdcb6e"
        })
    
    return generate_knowledge_graph_html(nodes, edges)


def get_sample_knowledge_graph() -> str:
    """获取示例知识图谱"""
    nodes = [
        {"id": "egfr", "label": "EGFR", "type": "target", "size": 40},
        {"id": "nsclc", "label": "非小细胞肺癌", "type": "disease", "size": 35},
        {"id": "gef", "label": "Gefitinib", "type": "drug", "size": 30},
        {"id": "erk", "label": "ERK", "type": "protein", "size": 25},
        {"id": "ras", "label": "RAS", "type": "gene", "size": 25},
        {"id": "pi3k", "label": "PI3K", "type": "protein", "size": 25},
        {"id": "akt", "label": "AKT", "type": "protein", "size": 25},
        {"id": "mapk", "label": "MAPK通路", "type": "pathway", "size": 30},
        {"id": "pi3k_path", "label": "PI3K通路", "type": "pathway", "size": 30},
    ]
    
    edges = [
        {"from": "gef", "to": "egfr", "label": "抑制", "color": "#e94560"},
        {"from": "egfr", "to": "nsclc", "label": "关联", "color": "#667eea"},
        {"from": "egfr", "to": "erk", "label": "激活", "color": "#00b894"},
        {"from": "egfr", "to": "ras", "label": "激活", "color": "#00b894"},
        {"from": "ras", "to": "mapk", "label": "参与", "color": "#fdcb6e"},
        {"from": "erk", "to": "mapk", "label": "参与", "color": "#fdcb6e"},
        {"from": "egfr", "to": "pi3k", "label": "激活", "color": "#00b894"},
        {"from": "pi3k", "to": "akt", "label": "激活", "color": "#00b894"},
        {"from": "pi3k", "to": "pi3k_path", "label": "参与", "color": "#fdcb6e"},
        {"from": "akt", "to": "pi3k_path", "label": "参与", "color": "#fdcb6e"},
    ]
    
    return generate_knowledge_graph_html(nodes, edges)
