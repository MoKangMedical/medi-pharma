"""
MediPharma — Streamlit 界面
AI驱动的一体化药物发现平台交互界面
"""

import streamlit as st
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="MediPharma", page_icon="🧬", layout="wide")

st.title("🧬 MediPharma — AI药物发现平台")
st.markdown("集成分子对接、ADMET预测、先导化合物优化的一体化药物研发平台")

# 侧边栏
page = st.sidebar.selectbox(
    "功能模块",
    ["🏠 首页", "🔬 分子对接", "🧪 ADMET预测", "⚗️ 先导化合物优化", "📊 批量筛选", "📋 数据浏览"]
)


if page == "🏠 首页":
    st.header("欢迎使用 MediPharma")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🔬 分子对接**\n配体-受体对接模拟，虚拟筛选和结合亲和力预测")
    with col2:
        st.info("**🧪 ADMET预测**\n吸收、分布、代谢、排泄和毒性全方位预测")
    with col3:
        st.info("**⚗️ 先导化合物优化**\n多参数优化评分、结构修饰建议和优化路线图")
    
    st.markdown("---")
    
    # 统计数据
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    compounds_path = os.path.join(data_dir, "sample-compounds.json")
    targets_path = os.path.join(data_dir, "targets.json")
    
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(compounds_path):
            with open(compounds_path) as f:
                compounds = json.load(f)
            st.metric("化合物库", f"{len(compounds)} 个")
    with col2:
        if os.path.exists(targets_path):
            with open(targets_path) as f:
                targets = json.load(f)
            st.metric("靶点库", f"{len(targets)} 个")
    
    st.markdown("""
    ### 平台特点
    - 🔬 **分子对接** — 基于评分函数的虚拟筛选，支持多靶点批量对接
    - 🧪 **ADMET预测** — 5大类20+性质预测，覆盖药物研发全流程
    - ⚗️ **先导优化** — MPO评分、生物电子等排体、结构修饰建议
    - 📊 **批量处理** — 支持化合物库批量筛选和分析
    """)


elif page == "🔬 分子对接":
    st.header("🔬 分子对接")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("化合物信息")
        compound_name = st.text_input("化合物名称", "奥希替尼")
        smiles = st.text_input("SMILES", "COc1cc(NC(=O)C=C)cc(c1Nc2nccc(-c3cn(C)c4ncccc34)n2)OC")
    
    with col2:
        st.subheader("靶点选择")
        target = st.selectbox(
            "选择靶点",
            ["EGFR", "HER2", "ALK", "BTK", "PARP1", "VEGFR2", "CDK4", "JAK1"]
        )
        
        # 显示靶点信息
        try:
            from molecular_docking import MolecularDocking
            docking = MolecularDocking()
            target_info = docking.get_target_info(target)
            if target_info:
                st.caption(f"结合位点: {target_info['name']}")
                st.caption(f"体积: {target_info['volume']} ų")
        except:
            pass
    
    if st.button("🔬 执行对接", type="primary"):
        try:
            from molecular_docking import MolecularDocking
            docking = MolecularDocking()
            result = docking.dock(smiles, target, compound_name)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("结合亲和力", f"{result.binding_affinity} kcal/mol")
            col2.metric("IC50估算", f"{result.ic50_estimate} nM")
            col3.metric("姿态评分", f"{result.pose_score}/10")
            col4.metric("置信度", f"{result.confidence:.0%}")
            
            st.subheader("关键相互作用")
            for interaction in result.key_interactions:
                st.markdown(f"- {interaction}")
            
        except Exception as e:
            st.error(f"对接出错: {e}")


elif page == "🧪 ADMET预测":
    st.header("🧪 ADMET预测")
    
    col1, col2 = st.columns(2)
    
    with col1:
        compound_name = st.text_input("化合物名称", "奥希替尼", key="admet_name")
        smiles = st.text_input("SMILES", "COc1cc(NC(=O)C=C)cc(c1Nc2nccc(-c3cn(C)c4ncccc34)n2)OC", key="admet_smiles")
    
    if st.button("🧪 执行ADMET预测", type="primary"):
        try:
            from admet_prediction import ADMETPredictor
            predictor = ADMETPredictor()
            result = predictor.predict(smiles, compound_name)
            
            # 综合评分
            st.metric("综合评分", f"{result.overall_score:.3f}")
            
            # 警告
            if result.alerts:
                for alert in result.alerts:
                    st.warning(alert)
            
            # 详细结果
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 吸收", "📦 分布", "🔄 代谢", "📤 排泄", "☠️ 毒性"])
            
            with tab1:
                st.json(result.absorption)
            with tab2:
                st.json(result.distribution)
            with tab3:
                st.json(result.metabolism)
            with tab4:
                st.json(result.excretion)
            with tab5:
                st.json(result.toxicity)
            
            # 类药性
            st.subheader("💊 类药性评估")
            col1, col2 = st.columns(2)
            col1.metric("QED评分", f"{result.druglikeness['qed_score']:.3f}")
            col2.metric("Lipinski规则", "✅ 通过" if result.druglikeness['lipinski_rule'] else "❌ 违反")
            
        except Exception as e:
            st.error(f"预测出错: {e}")


elif page == "⚗️ 先导化合物优化":
    st.header("⚗️ 先导化合物优化")
    
    col1, col2 = st.columns(2)
    
    with col1:
        compound_name = st.text_input("化合物名称", "先导化合物A", key="opt_name")
        smiles = st.text_input("SMILES", "c1ccc2c(c1)nc(n2)N3CCNCC3", key="opt_smiles")
        optimization_goal = st.selectbox("优化目标", ["admet", "potency", "selectivity", "solubility"])
    
    if st.button("⚗️ 执行优化分析", type="primary"):
        try:
            from lead_optimization import LeadOptimizer
            optimizer = LeadOptimizer()
            result = optimizer.optimize(smiles, compound_name, optimization_goal)
            
            col1, col2 = st.columns(2)
            col1.metric("MPO评分", f"{result.mpo_score:.3f}/1.000")
            col2.metric("优化建议数", f"{len(result.suggestions)}条")
            
            st.subheader("📊 属性概况")
            st.json(result.property_profile)
            
            st.subheader("💡 优化建议")
            for i, sug in enumerate(result.suggestions[:5], 1):
                with st.expander(f"{i}. [{sug.type}] {sug.description[:50]}..."):
                    st.markdown(f"**描述**: {sug.description}")
                    st.markdown(f"**预期效果**: {sug.expected_effect}")
                    st.markdown(f"**依据**: {sug.rationale}")
                    st.markdown(f"**优先级**: {'⭐' * (4 - sug.priority)}")
            
            st.subheader("🗺️ 优化路线图")
            for step in result.optimization_route:
                st.markdown(f"- {step}")
            
        except Exception as e:
            st.error(f"优化分析出错: {e}")


elif page == "📊 批量筛选":
    st.header("📊 批量虚拟筛选")
    
    st.markdown("从化合物库中选择靶点进行批量虚拟筛选")
    
    # 加载化合物库
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    compounds_path = os.path.join(data_dir, "sample-compounds.json")
    
    if os.path.exists(compounds_path):
        with open(compounds_path) as f:
            compounds = json.load(f)
        
        st.info(f"化合物库: {len(compounds)} 个化合物")
        
        target = st.selectbox("选择靶点", ["EGFR", "HER2", "ALK", "BTK", "PARP1", "VEGFR2", "CDK4", "JAK1"], key="batch_target")
        top_n = st.slider("显示前N个结果", 5, 50, 10)
        
        if st.button("🚀 开始批量筛选", type="primary"):
            with st.spinner("正在筛选..."):
                try:
                    from molecular_docking import MolecularDocking
                    docking = MolecularDocking()
                    
                    results = docking.virtual_screen(compounds, target, top_n=top_n)
                    
                    import pandas as pd
                    data = []
                    for r in results:
                        data.append({
                            "化合物": r.compound_name,
                            "结合亲和力 (kcal/mol)": r.binding_affinity,
                            "IC50 (nM)": r.ic50_estimate,
                            "姿态评分": r.pose_score,
                            "置信度": f"{r.confidence:.0%}"
                        })
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    st.success(f"筛选完成！共筛选 {len(compounds)} 个化合物")
                    
                except Exception as e:
                    st.error(f"筛选出错: {e}")
    else:
        st.warning("未找到化合物库文件")


elif page == "📋 数据浏览":
    st.header("📋 数据浏览")
    
    tab1, tab2 = st.tabs(["化合物库", "靶点库"])
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    with tab1:
        compounds_path = os.path.join(data_dir, "sample-compounds.json")
        if os.path.exists(compounds_path):
            with open(compounds_path) as f:
                compounds = json.load(f)
            
            import pandas as pd
            df = pd.DataFrame(compounds)
            st.dataframe(df, use_container_width=True)
            st.caption(f"共 {len(compounds)} 个化合物")
        else:
            st.warning("未找到化合物库文件")
    
    with tab2:
        targets_path = os.path.join(data_dir, "targets.json")
        if os.path.exists(targets_path):
            with open(targets_path) as f:
                targets = json.load(f)
            
            import pandas as pd
            df = pd.DataFrame(targets)
            st.dataframe(df, use_container_width=True)
            st.caption(f"共 {len(targets)} 个靶点")
        else:
            st.warning("未找到靶点库文件")


st.sidebar.markdown("---")
st.sidebar.markdown("### 关于")
st.sidebar.markdown("MediPharma v1.0\n\nAI驱动的一体化药物发现平台")
