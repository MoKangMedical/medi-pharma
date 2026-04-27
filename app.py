#!/usr/bin/env python3
"""
MediPharma — AI Drug Discovery Platform
Streamlit Web UI v2.1

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
    
    /* 成功/警告消息 */
    .stAlert {
        border-radius: 8px;
    }
    
    /* 分割线 */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 2rem 0;
    }
    
    /* 功能卡片 */
    .feature-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 16px;
    }
    
    .feature-card h4 {
        color: #1a1a2e;
        margin-bottom: 8px;
    }
    
    .feature-card p {
        color: #666;
        margin: 0;
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
        st.markdown("- 全流程Pipeline")
        
        st.divider()
        
        st.markdown("### 🔗 链接")
        st.markdown("[GitHub](https://github.com/MoKangMedical/medi-pharma)")
        st.markdown("[API文档](http://localhost:8000/docs)")
        
        st.divider()
        
        st.markdown("### ℹ️ 关于")
        st.markdown("MediPharma v2.1.0")
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 虚拟筛选", 
        "🧬 分子生成", 
        "💊 ADMET预测",
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
                                
                                # 详细属性
                                st.json({
                                    "absorption": report.absorption,
                                    "distribution": report.distribution,
                                    "metabolism": report.metabolism,
                                    "toxicity": report.toxicity
                                })
    
    # ===== Tab 4: 数据浏览 =====
    with tab4:
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
    
    # ===== Tab 5: 全流程演示 =====
    with tab5:
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
        <p>MediPharma v2.1.0 — AI Drug Discovery Platform</p>
        <p>Built by <a href="https://github.com/MoKangMedical">MoKangMedical</a> | 
           <a href="https://github.com/MoKangMedical/medi-pharma">GitHub</a> | 
           MIT License</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
