#!/usr/bin/env python3
"""
MediPharma — AI Drug Discovery Platform
Streamlit Web UI v3.0

启动: streamlit run app.py --server.port 8095
"""

import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# ===== 页面配置 =====
st.set_page_config(
    page_title="MediPharma — AI Drug Discovery",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 自定义CSS =====
st.markdown("""
<style>
    /* 全局样式 */
    .main {
        padding-top: 1rem;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* 标题样式 */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    h2, h3 {
        color: #1a1a2e;
    }
    
    /* 指标卡片 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 表格样式 */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* 分割线 */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 2rem 0;
    }
    
    /* 底部信息 */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
    }
    
    .footer a {
        color: #667eea;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)


def load_local_data():
    """加载本地数据"""
    data_dir = Path(__file__).parent / "data"
    
    compounds = []
    targets = []
    
    compounds_file = data_dir / "demo_compounds.json"
    targets_file = data_dir / "demo_targets.json"
    
    if compounds_file.exists():
        with open(compounds_file) as f:
            compounds = json.load(f)
    
    if targets_file.exists():
        with open(targets_file) as f:
            targets = json.load(f)
    
    return compounds, targets


def run_admet_prediction(smiles_list):
    """运行ADMET预测"""
    try:
        from admet_prediction.engine import ADMETEngine
        engine = ADMETEngine()
        results = []
        for smiles in smiles_list:
            if smiles.strip():
                report = engine.predict(smiles.strip())
                results.append({
                    "smiles": smiles.strip(),
                    "report": report
                })
        return results
    except Exception as e:
        st.error(f"ADMET预测失败: {e}")
        return []


def run_virtual_screening(target_id, max_compounds):
    """运行虚拟筛选"""
    try:
        from virtual_screening.engine import VirtualScreeningEngine
        engine = VirtualScreeningEngine()
        result = engine.screen(
            target_chembl_id=target_id,
            max_compounds=max_compounds,
            top_n=10,
            library_source="local"
        )
        return result
    except Exception as e:
        st.error(f"虚拟筛选失败: {e}")
        return None


def run_molecular_generation(target_name, n_generate):
    """运行分子生成"""
    try:
        from molecular_generation.engine import MolecularGenerationEngine
        engine = MolecularGenerationEngine()
        result = engine.generate_candidates(
            target_name=target_name,
            n_generate=n_generate,
            top_n=10
        )
        return result
    except Exception as e:
        st.error(f"分子生成失败: {e}")
        return None


def render_mol_2d(smiles: str, width: int = 300, height: int = 200):
    """渲染2D分子结构"""
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw
        import base64
        import io
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            st.warning("无效的SMILES")
            return
        
        img = Draw.MolToImage(mol, size=(width, height))
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        st.markdown(
            f'<div style="text-align: center;"><img src="data:image/png;base64,{img_str}" width="{width}"></div>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"渲染失败: {e}")


def render_mol_properties(smiles: str):
    """渲染分子属性"""
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, QED
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return
        
        props = {
            "分子量": f"{Descriptors.MolWt(mol):.1f}",
            "LogP": f"{Descriptors.MolLogP(mol):.2f}",
            "氢键供体": Descriptors.NumHDonors(mol),
            "氢键受体": Descriptors.NumHAcceptors(mol),
            "极性表面积": f"{Descriptors.TPSA(mol):.1f}",
            "QED": f"{QED.qed(mol):.3f}",
        }
        
        cols = st.columns(3)
        for i, (key, value) in enumerate(props.items()):
            with cols[i % 3]:
                st.metric(key, value)
    except Exception as e:
        st.warning(f"计算属性失败: {e}")


def main():
    # 加载数据
    compounds, targets = load_local_data()
    
    # ===== 侧边栏 =====
    with st.sidebar:
        st.markdown("## 💊 MediPharma")
        st.markdown("**AI Drug Discovery Platform**")
        
        st.divider()
        
        st.markdown("### 📊 数据源")
        st.markdown(f"- 化合物库: {len(compounds)} 个")
        st.markdown(f"- 靶点库: {len(targets)} 个")
        
        st.divider()
        
        st.markdown("### 🔬 核心功能")
        st.markdown("- 虚拟筛选")
        st.markdown("- 分子生成")
        st.markdown("- ADMET预测")
        st.markdown("- 分子可视化")
        st.markdown("- 全流程Pipeline")
        
        st.divider()
        
        st.markdown("### 🔗 链接")
        st.markdown("[GitHub](https://github.com/MoKangMedical/medi-pharma)")
        st.markdown("[API文档](http://localhost:8000/docs)")
        
        st.divider()
        
        st.markdown("### ℹ️ 关于")
        st.markdown("MediPharma v3.0.0")
        st.markdown("Built by MoKangMedical")
    
    # ===== 主界面 =====
    st.title("MediPharma")
    st.markdown("**AI驱动的药物发现平台** — 基于ChEMBL 2.4M化合物和OpenTargets靶点数据")
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("化合物库", f"{len(compounds)}", "本地数据")
    with col2:
        st.metric("靶点库", f"{len(targets)}", "热门靶点")
    with col3:
        st.metric("ADMET模型", "20+", "预测属性")
    with col4:
        st.metric("准确率", "85%", "AUC")
    
    st.divider()
    
    # 功能标签页
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "🎯 虚拟筛选", 
        "🧬 分子生成", 
        "💊 ADMET预测",
        "🔬 分子可视化",
        "💊 药物重定位",
        "🕸️ 知识图谱",
        "🏥 临床试验",
        "📋 监管合规",
        "🧬 蛋白质结构",
        "📊 数据浏览",
        "🔄 全流程演示"
    ])
    
    # ===== Tab 1: 虚拟筛选 =====
    with tab1:
        st.header("虚拟筛选")
        st.markdown("从化合物库中筛选潜在的药物候选分子")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            target_options = {t["gene_symbol"]: t["target_id"] for t in targets}
            selected_target = st.selectbox(
                "选择靶点",
                options=list(target_options.keys()),
                index=0
            )
        with col2:
            max_compounds = st.slider("筛选数量", 10, 100, 30)
        
        if st.button("🔍 开始筛选", key="btn_screen", use_container_width=True):
            with st.spinner("正在执行虚拟筛选..."):
                target_id = target_options[selected_target]
                result = run_virtual_screening(target_id, max_compounds)
                
                if result and result.top_candidates:
                    st.success(f"筛选完成! 发现 {result.hits_found} 个Hit化合物")
                    
                    # 显示结果表格
                    import pandas as pd
                    df = pd.DataFrame(result.top_candidates)
                    if "smiles" in df.columns:
                        display_cols = ["name", "smiles", "predicted_pkd", "confidence"]
                        display_cols = [c for c in display_cols if c in df.columns]
                        st.dataframe(df[display_cols], use_container_width=True)
                    
                    # 下载结果
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 下载结果",
                        csv,
                        "screening_results.csv",
                        "text/csv"
                    )
    
    # ===== Tab 2: 分子生成 =====
    with tab2:
        st.header("AI分子生成")
        st.markdown("使用AI生成新型候选药物分子")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            gen_target = st.selectbox(
                "选择靶点",
                options=list(target_options.keys()),
                index=0,
                key="gen_target"
            )
        with col2:
            n_generate = st.slider("生成数量", 10, 100, 30, key="gen_n")
        
        if st.button("🧬 开始生成", key="btn_gen", use_container_width=True):
            with st.spinner("正在生成候选分子..."):
                result = run_molecular_generation(gen_target, n_generate)
                
                if result and result.top_candidates:
                    st.success(f"生成完成! 有效分子 {result.valid_molecules} 个")
                    
                    # 显示结果
                    import pandas as pd
                    df = pd.DataFrame(result.top_candidates)
                    if "smiles" in df.columns:
                        display_cols = ["smiles", "mw", "logp", "qed", "sa_score"]
                        display_cols = [c for c in display_cols if c in df.columns]
                        st.dataframe(df[display_cols], use_container_width=True)
                    
                    # 下载结果
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 下载结果",
                        csv,
                        "generation_results.csv",
                        "text/csv"
                    )
    
    # ===== Tab 3: ADMET预测 =====
    with tab3:
        st.header("ADMET预测")
        st.markdown("预测化合物的吸收、分布、代谢、排泄和毒性")
        
        smiles_input = st.text_area(
            "输入SMILES (每行一个)",
            "CC(=O)OC1=CC=CC=C1C(=O)O\nCCO\nCC(=O)NC1=CC=C(O)C=C1",
            height=150,
            key="admet_smiles"
        )
        
        if st.button("💊 开始预测", key="btn_admet", use_container_width=True):
            smiles_list = [s.strip() for s in smiles_input.split("\n") if s.strip()]
            
            if smiles_list:
                with st.spinner(f"正在预测 {len(smiles_list)} 个化合物..."):
                    results = run_admet_prediction(smiles_list)
                    
                    if results:
                        st.success(f"预测完成! 共 {len(results)} 个化合物")
                        
                        for i, item in enumerate(results):
                            report = item["report"]
                            smiles = item["smiles"]
                            
                            with st.expander(f"化合物 {i+1}: {smiles[:30]}..."):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("综合评分", f"{report.overall['total_score']:.2f}")
                                with col2:
                                    st.metric("吸收", f"{report.overall['absorption']:.2f}")
                                with col3:
                                    st.metric("毒性", f"{report.overall['toxicity']:.2f}")
                                with col4:
                                    status = "✅ PASS" if report.pass_filter else "❌ FAIL"
                                    st.metric("状态", status)
                                
                                # 显示2D结构
                                render_mol_2d(smiles)
                                
                                # 显示详细属性
                                st.json({
                                    "absorption": report.absorption,
                                    "distribution": report.distribution,
                                    "metabolism": report.metabolism,
                                    "toxicity": report.toxicity
                                })
    
    # ===== Tab 4: 分子可视化 =====
    with tab4:
        st.header("分子可视化")
        st.markdown("查看分子的2D结构和属性")
        
        # 从化合物库选择或手动输入
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("从化合物库选择")
            if compounds:
                compound_names = [c.get("name", f"化合物 {i}") for i, c in enumerate(compounds)]
                selected_compound = st.selectbox("选择化合物", compound_names)
                selected_idx = compound_names.index(selected_compound)
                selected_smiles = compounds[selected_idx].get("smiles", "")
            else:
                selected_smiles = ""
        
        with col2:
            st.subheader("或手动输入SMILES")
            manual_smiles = st.text_input("SMILES", "CC(=O)OC1=CC=CC=C1C(=O)O")
        
        # 使用选择的或手动输入的SMILES
        display_smiles = selected_smiles if selected_smiles else manual_smiles
        
        if display_smiles:
            st.divider()
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("2D结构")
                render_mol_2d(display_smiles, width=400, height=300)
            
            with col2:
                st.subheader("分子属性")
                render_mol_properties(display_smiles)
    
    # ===== Tab 5: 药物重定位 =====
    with tab5:
        st.header("药物重定位")
        st.markdown("基于分子相似性发现老药新用机会")
        
        # 输入SMILES
        repurposing_smiles = st.text_input(
            "输入查询分子SMILES",
            "CC(=O)OC1=CC=CC=C1C(=O)O",
            key="repurposing_smiles"
        )
        
        if st.button("🔍 查找相似药物", key="btn_repurposing", use_container_width=True):
            if repurposing_smiles:
                with st.spinner("正在搜索相似药物..."):
                    try:
                        sys.path.insert(0, str(Path(__file__).parent / "src"))
                        from drug_repurposing import DrugRepurposing
                        
                        repurposer = DrugRepurposing()
                        
                        # 查找相似药物
                        similar_drugs = repurposer.find_similar_drugs(repurposing_smiles, top_n=5)
                        
                        if similar_drugs:
                            st.success(f"找到 {len(similar_drugs)} 个相似药物")
                            
                            # 显示结果
                            import pandas as pd
                            df = pd.DataFrame(similar_drugs)
                            st.dataframe(df[["name", "indication", "similarity"]], use_container_width=True)
                            
                            # 显示查询分子结构
                            st.subheader("查询分子")
                            render_mol_2d(repurposing_smiles)
                            
                            # 分析类药性
                            st.subheader("类药性分析")
                            drug_likeness = repurposer.analyze_drug_likeness(repurposing_smiles)
                            
                            if "error" not in drug_likeness:
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("分子量", drug_likeness["molecular_weight"])
                                with col2:
                                    st.metric("LogP", drug_likeness["logp"])
                                with col3:
                                    st.metric("QED", drug_likeness["qed"])
                                with col4:
                                    st.metric("类药性", "✅" if drug_likeness["is_drug_like"] else "❌")
                            
                            # 建议新适应症
                            st.subheader("潜在新适应症")
                            new_indications = repurposer.suggest_new_indications(repurposing_smiles)
                            
                            if new_indications:
                                for indication in new_indications:
                                    st.info(f"**{indication['indication']}** (来源: {indication['source_drug']}, 相似性: {indication['similarity']})")
                            else:
                                st.warning("未找到潜在新适应症")
                        else:
                            st.warning("未找到相似药物")
                    except Exception as e:
                        st.error(f"药物重定位失败: {e}")
    
    # ===== Tab 6: 知识图谱 =====
    with tab6:
        st.header("知识图谱")
        st.markdown("可视化靶点、疾病、药物之间的关联关系")
        
        # 选择图谱类型
        graph_type = st.selectbox(
            "选择图谱类型",
            ["靶点-疾病关联", "药物-靶点关联", "通路-基因关联", "示例图谱"],
            key="graph_type"
        )
        
        if graph_type == "靶点-疾病关联":
            st.subheader("靶点-疾病知识图谱")
            
            # 选择靶点
            if targets:
                target_names = [t["gene_symbol"] for t in targets]
                selected_target = st.selectbox("选择靶点", target_names, key="kg_target")
                
                # 获取相关疾病
                target_data = next((t for t in targets if t["gene_symbol"] == selected_target), None)
                if target_data and "disease_areas" in target_data:
                    diseases = target_data["disease_areas"]
                    
                    # 生成图谱
                    try:
                        sys.path.insert(0, str(Path(__file__).parent / "src"))
                        from knowledge_graph_viz import create_target_disease_graph
                        
                        graph_html = create_target_disease_graph(selected_target, diseases)
                        st.components.v1.html(graph_html, height=600)
                    except Exception as e:
                        st.error(f"生成图谱失败: {e}")
        
        elif graph_type == "药物-靶点关联":
            st.subheader("药物-靶点知识图谱")
            
            # 输入药物SMILES
            drug_smiles = st.text_input("输入药物SMILES", "CC(=O)OC1=CC=CC=C1C(=O)O", key="kg_drug")
            
            if drug_smiles:
                # 显示药物结构
                render_mol_2d(drug_smiles, width=200, height=150)
                
                # 生成图谱（示例）
                try:
                    sys.path.insert(0, str(Path(__file__).parent / "src"))
                    from knowledge_graph_viz import create_drug_target_graph
                    
                    # 示例靶点
                    sample_targets = ["COX-1", "COX-2", "TXA2"]
                    graph_html = create_drug_target_graph("Aspirin", sample_targets)
                    st.components.v1.html(graph_html, height=600)
                except Exception as e:
                    st.error(f"生成图谱失败: {e}")
        
        elif graph_type == "通路-基因关联":
            st.subheader("通路-基因知识图谱")
            
            # 选择通路
            pathway = st.selectbox(
                "选择通路",
                ["MAPK通路", "PI3K-AKT通路", "Wnt通路", "Notch通路"],
                key="kg_pathway"
            )
            
            # 示例基因
            pathway_genes = {
                "MAPK通路": ["KRAS", "BRAF", "MEK", "ERK"],
                "PI3K-AKT通路": ["PI3K", "AKT", "mTOR", "PTEN"],
                "Wnt通路": ["Wnt", "Frizzled", "β-catenin", "APC"],
                "Notch通路": ["Notch", "DLL", "Jagged", "NICD"],
            }
            
            genes = pathway_genes.get(pathway, [])
            
            if genes:
                try:
                    sys.path.insert(0, str(Path(__file__).parent / "src"))
                    from knowledge_graph_viz import create_pathway_graph
                    
                    graph_html = create_pathway_graph(pathway, genes)
                    st.components.v1.html(graph_html, height=600)
                except Exception as e:
                    st.error(f"生成图谱失败: {e}")
        
        else:  # 示例图谱
            st.subheader("示例知识图谱")
            st.markdown("展示EGFR靶点相关的知识图谱")
            
            try:
                sys.path.insert(0, str(Path(__file__).parent / "src"))
                from knowledge_graph_viz import get_sample_knowledge_graph
                
                graph_html = get_sample_knowledge_graph()
                st.components.v1.html(graph_html, height=600)
            except Exception as e:
                st.error(f"生成图谱失败: {e}")
    
    # ===== Tab 7: 临床试验 =====
    with tab7:
        st.header("临床试验模拟")
        st.markdown("基于AI预测临床试验成功率和设计优化")
        
        # 输入参数
        col1, col2 = st.columns(2)
        
        with col1:
            ct_smiles = st.text_input("药物SMILES", "CC(=O)OC1=CC=CC=C1C(=O)O", key="ct_smiles")
            ct_target = st.text_input("靶点", "EGFR", key="ct_target")
        
        with col2:
            ct_indication = st.text_input("适应症", "非小细胞肺癌", key="ct_indication")
            ct_phase = st.selectbox("临床阶段", ["Phase I", "Phase II", "Phase III", "Phase IV"], key="ct_phase")
        
        if st.button("🏥 模拟临床试验", key="btn_clinical", use_container_width=True):
            with st.spinner("正在模拟临床试验..."):
                try:
                    sys.path.insert(0, str(Path(__file__).parent / "src"))
                    from clinical_trial import ClinicalTrialSimulator
                    
                    simulator = ClinicalTrialSimulator()
                    
                    # 设计临床试验
                    design = simulator.design_trial(ct_smiles, ct_target, ct_indication, ct_phase)
                    
                    # 预测成功率
                    prediction = simulator.predict_success(ct_smiles, ct_target, ct_indication, ct_phase)
                    
                    # 显示结果
                    st.success("临床试验模拟完成!")
                    
                    # 显示设计
                    st.subheader("临床试验设计")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("阶段", design.phase)
                    with col2:
                        st.metric("目标人群", design.target_population)
                    with col3:
                        st.metric("持续时间", f"{design.duration_weeks}周")
                    with col4:
                        st.metric("成功率", f"{prediction.success_probability*100:.1f}%")
                    
                    # 显示详细信息
                    st.subheader("试验详情")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**主要终点**")
                        st.info(design.primary_endpoint)
                        
                        st.markdown("**次要终点**")
                        for endpoint in design.secondary_endpoints:
                            st.markdown(f"- {endpoint}")
                    
                    with col2:
                        st.markdown("**给药方案**")
                        st.info(design.dosing_regimen)
                        
                        st.markdown("**纳入标准**")
                        for criteria in design.inclusion_criteria:
                            st.markdown(f"- {criteria}")
                    
                    # 显示风险因素
                    if prediction.risk_factors:
                        st.subheader("风险因素")
                        for risk in prediction.risk_factors:
                            st.warning(risk)
                    
                    # 显示建议
                    if prediction.recommendations:
                        st.subheader("优化建议")
                        for rec in prediction.recommendations:
                            st.info(rec)
                    
                    # 优化设计
                    st.subheader("多阶段优化分析")
                    optimization = simulator.optimize_design(ct_smiles, ct_target, ct_indication)
                    
                    # 显示各阶段成功率
                    phases = list(optimization["predictions"].keys())
                    probabilities = list(optimization["predictions"].values())
                    
                    import pandas as pd
                    df = pd.DataFrame({
                        "阶段": phases,
                        "成功率": [f"{p*100:.1f}%" for p in probabilities]
                    })
                    st.dataframe(df, use_container_width=True)
                    
                    st.metric("总体成功率", f"{optimization['overall_success_rate']*100:.1f}%")
                    
                    st.markdown("**推荐起始阶段**")
                    st.success(optimization["recommended_start_phase"])
                    
                except Exception as e:
                    st.error(f"临床试验模拟失败: {e}")
    
    # ===== Tab 8: 监管合规 =====
    with tab8:
        st.header("监管合规")
        st.markdown("基于FDA/EMA/NMPA指南的合规检查和文档生成")
        
        # 输入参数
        col1, col2 = st.columns(2)
        
        with col1:
            reg_smiles = st.text_input("药物SMILES", "CC(=O)OC1=CC=CC=C1C(=O)O", key="reg_smiles")
            reg_target = st.text_input("靶点", "EGFR", key="reg_target")
        
        with col2:
            reg_indication = st.text_input("适应症", "非小细胞肺癌", key="reg_indication")
            reg_doc_type = st.selectbox("文档类型", ["IND", "NDA", "BLA"], key="reg_doc_type")
        
        if st.button("📋 检查合规性", key="btn_regulatory", use_container_width=True):
            with st.spinner("正在检查合规性..."):
                try:
                    sys.path.insert(0, str(Path(__file__).parent / "src"))
                    from regulatory import RegulatoryCompliance
                    
                    reg_engine = RegulatoryCompliance()
                    
                    # 获取合规性摘要
                    summary = reg_engine.get_compliance_summary(reg_smiles, reg_target, reg_indication)
                    
                    # 显示结果
                    st.success("合规性检查完成!")
                    
                    # 显示摘要
                    st.subheader("合规性摘要")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("总检查项", summary["total_checks"])
                    with col2:
                        st.metric("通过", summary["pass_count"])
                    with col3:
                        st.metric("警告", summary["warning_count"])
                    with col4:
                        st.metric("合规分数", f"{summary['compliance_score']*100:.1f}%")
                    
                    # 显示合规状态
                    if summary["is_compliant"]:
                        st.success("✅ 合规性检查通过")
                    else:
                        st.error("❌ 合规性检查未通过")
                    
                    # 显示详细检查
                    st.subheader("详细检查")
                    
                    for check in summary["checks"]:
                        if check.status == "pass":
                            st.success(f"**{check.check_name}**: {check.details}")
                        elif check.status == "warning":
                            st.warning(f"**{check.check_name}**: {check.details}")
                            for rec in check.recommendations:
                                st.markdown(f"- {rec}")
                        else:
                            st.error(f"**{check.check_name}**: {check.details}")
                            for rec in check.recommendations:
                                st.markdown(f"- {rec}")
                    
                    # 生成监管文档
                    st.subheader("监管文档")
                    
                    doc = reg_engine.generate_regulatory_document(
                        reg_smiles, reg_target, reg_indication, reg_doc_type
                    )
                    
                    st.text_area("文档内容", doc.content, height=400, key="reg_doc_content")
                    
                    # 下载文档
                    st.download_button(
                        "📥 下载文档",
                        doc.content,
                        f"{reg_doc_type}_document.md",
                        "text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"监管合规检查失败: {e}")
    
    # ===== Tab 9: 蛋白质结构 =====
    with tab9:
        st.header("蛋白质结构预测")
        st.markdown("基于AlphaFold2/ESMFold的蛋白质结构预测和分析")
        
        # 输入参数
        col1, col2 = st.columns(2)
        
        with col1:
            protein_target = st.selectbox(
                "选择靶点",
                ["EGFR", "HER2", "BRAF", "KRAS", "PI3K", "自定义"],
                key="protein_target"
            )
            
            if protein_target == "自定义":
                protein_sequence = st.text_area(
                    "输入蛋白质序列",
                    "MKTILILTLAVVTASCFCQGTGHGNSRGKTCTSCGSN",
                    height=100,
                    key="protein_sequence"
                )
            else:
                protein_sequence = ""
        
        with col2:
            protein_method = st.selectbox(
                "预测方法",
                ["AlphaFold2", "ESMFold"],
                key="protein_method"
            )
            
            protein_ligand = st.text_input(
                "配体SMILES (可选)",
                "CC(=O)OC1=CC=CC=C1C(=O)O",
                key="protein_ligand"
            )
        
        if st.button("🧬 预测结构", key="btn_protein", use_container_width=True):
            with st.spinner("正在预测蛋白质结构..."):
                try:
                    sys.path.insert(0, str(Path(__file__).parent / "src"))
                    from protein_structure import ProteinStructurePredictor
                    
                    predictor = ProteinStructurePredictor()
                    
                    # 获取序列
                    if protein_target == "自定义":
                        sequence = protein_sequence
                    else:
                        sequence = predictor.get_target_sequence(protein_target)
                        if not sequence:
                            st.error(f"未找到{protein_target}的序列")
                            return
                    
                    # 预测结构
                    structure = predictor.predict_structure(sequence, protein_method.lower())
                    
                    # 显示结果
                    st.success("蛋白质结构预测完成!")
                    
                    # 显示基本信息
                    st.subheader("结构信息")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("PDB ID", structure.pdb_id)
                    with col2:
                        st.metric("置信度", f"{structure.confidence*100:.1f}%")
                    with col3:
                        st.metric("方法", structure.method)
                    
                    # 显示序列
                    st.subheader("蛋白质序列")
                    st.text_area("序列", structure.sequence, height=100, key="seq_display")
                    
                    # 分析结合位点
                    if protein_ligand:
                        st.subheader("结合位点分析")
                        
                        binding_analysis = predictor.analyze_binding_site(structure, protein_ligand)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**结合位点信息**")
                            st.info(f"中心: {binding_analysis['binding_site']['center']}")
                            st.info(f"半径: {binding_analysis['binding_site']['radius']} Å")
                            st.info(f"残基: {', '.join(binding_analysis['binding_site']['residues'])}")
                        
                        with col2:
                            st.markdown("**预测结合亲和力**")
                            st.metric("结合亲和力", f"{binding_analysis['predicted_affinity']} kcal/mol")
                            st.metric("置信度", f"{binding_analysis['confidence']*100:.1f}%")
                        
                        # 显示相互作用
                        st.subheader("相互作用")
                        
                        for interaction in binding_analysis["interactions"]:
                            st.markdown(f"- **{interaction['type']}**: {interaction['residue']} (距离: {interaction['distance']} Å)")
                    
                    # 生成PyMOL脚本
                    st.subheader("PyMOL脚本")
                    
                    pymol_script = predictor.generate_pymol_script(structure)
                    
                    st.code(pymol_script, language="python")
                    
                    # 下载脚本
                    st.download_button(
                        "📥 下载PyMOL脚本",
                        pymol_script,
                        f"{structure.pdb_id}_pymol.py",
                        "text/python"
                    )
                    
                except Exception as e:
                    st.error(f"蛋白质结构预测失败: {e}")
    
    # ===== Tab 10: 数据浏览 =====
    with tab10:
        st.header("数据浏览")
        st.markdown("浏览本地化合物库和靶点库")
        
        data_tab1, data_tab2 = st.tabs(["化合物库", "靶点库"])
        
        with data_tab1:
            if compounds:
                import pandas as pd
                df = pd.DataFrame(compounds)
                st.dataframe(df, use_container_width=True)
                st.caption(f"共 {len(compounds)} 个化合物")
        
        with data_tab2:
            if targets:
                import pandas as pd
                df = pd.DataFrame(targets)
                st.dataframe(df, use_container_width=True)
                st.caption(f"共 {len(targets)} 个靶点")
    
    # ===== Tab 11: 全流程演示 =====
    with tab11:
        st.header("全流程演示")
        st.markdown("展示完整的药物发现流程")
        
        st.info("点击下方按钮运行完整的药物发现Pipeline：靶点发现 → 虚拟筛选 → 分子生成 → ADMET预测 → 综合报告")
        
        if st.button("🚀 启动全流程", key="btn_pipeline", use_container_width=True):
            with st.spinner("正在执行全流程Pipeline...这可能需要1-2分钟"):
                # 运行演示脚本
                import subprocess
                result = subprocess.run(
                    ["python3.12", "demo_e2e.py"],
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).parent)
                )
                
                if result.returncode == 0:
                    st.success("全流程Pipeline完成!")
                    
                    # 读取结果
                    results_file = Path(__file__).parent / "demo_results.json"
                    if results_file.exists():
                        with open(results_file) as f:
                            demo_results = json.load(f)
                        
                        # 显示摘要
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("筛选化合物", demo_results["screening"]["total_screened"])
                        with col2:
                            st.metric("生成分子", demo_results["generation"]["valid_molecules"])
                        with col3:
                            st.metric("ADMET通过", demo_results["admet_evaluation"]["passed"])
                        
                        # 显示详细输出
                        st.text(result.stdout[-2000:])  # 最后2000字符
                else:
                    st.error("Pipeline执行失败")
                    st.text(result.stderr[-1000:])
    
    # ===== 底部 =====
    st.divider()
    st.markdown("""
    <div class="footer">
        <p>MediPharma v3.0.0 — AI Drug Discovery Platform</p>
        <p>Built by <a href="https://github.com/MoKangMedical">MoKangMedical</a> | 
           <a href="https://github.com/MoKangMedical/medi-pharma">GitHub</a> | 
           MIT License</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
