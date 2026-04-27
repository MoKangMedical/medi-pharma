#!/usr/bin/env python3
"""
MediPharma — Streamlit Web UI
AI驱动药物发现平台

启动: streamlit run app.py --server.port 8095
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# ===== 配置 =====
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="MediPharma — AI Drug Discovery",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 自定义CSS =====
st.markdown("""
<style>
    .main { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a73e8;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1a73e8;
    }
</style>
""", unsafe_allow_html=True)


def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """调用后端API"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=30)
        else:
            resp = requests.post(url, json=data, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "API服务未启动，请先运行: uvicorn backend.api:app --port 8000"}
    except Exception as e:
        return {"error": str(e)}


def main():
    # ===== 侧边栏 =====
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/pill.png", width=64)
        st.title("MediPharma")
        st.caption("AI Drug Discovery Platform")
        
        st.divider()
        st.markdown("### 数据源")
        st.markdown("- ChEMBL 2.4M+ 化合物")
        st.markdown("- OpenTargets 60K+ 靶点")
        st.markdown("- UniProt 蛋白质注释")
        
        st.divider()
        st.markdown("### 技术栈")
        st.markdown("- Python 3.9+")
        st.markdown("- RDKit / PyTorch")
        st.markdown("- FastAPI / Streamlit")
        
        st.divider()
        st.markdown("### 链接")
        st.markdown("[GitHub](https://github.com/MoKangMedical/medi-pharma)")
        st.markdown("[API文档](http://localhost:8000/docs)")
        st.markdown("[MoKangMedical](https://github.com/MoKangMedical)")

    # ===== 主界面 =====
    st.title("💊 MediPharma — AI药物发现平台")
    st.markdown("**基于ChEMBL 2.4M化合物和OpenTargets靶点数据的全流程AI药物发现**")
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("化合物库", "2.4M+", "ChEMBL")
    with col2:
        st.metric("靶点", "60K+", "OpenTargets")
    with col3:
        st.metric("ADMET模型", "20+", "预测属性")
    with col4:
        st.metric("准确率", "85%", "AUC")
    
    st.divider()
    
    # 功能标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 靶点发现", "🔬 虚拟筛选", "🧬 分子生成", 
        "💊 ADMET预测", "⚗️ 先导优化", "🔄 全流程Pipeline"
    ])
    
    # ===== Tab 1: 靶点发现 =====
    with tab1:
        st.header("靶点发现")
        st.markdown("基于文献挖掘和知识图谱，发现疾病相关靶点")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            disease = st.text_input("目标疾病", "重症肌无力", key="target_disease")
        with col2:
            max_papers = st.number_input("最大文献数", 10, 100, 30, key="target_papers")
        
        if st.button("🔍 开始靶点发现", key="btn_target"):
            with st.spinner("正在分析文献和靶点数据..."):
                result = call_api("/targets/discover", "POST", {
                    "disease": disease,
                    "max_papers": max_papers,
                    "top_n": 10
                })
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(f"发现 {result.get('total_candidates', 0)} 个候选靶点")
                    
                    if "top_targets" in result:
                        df = pd.DataFrame(result["top_targets"])
                        st.dataframe(df, use_container_width=True)
    
    # ===== Tab 2: 虚拟筛选 =====
    with tab2:
        st.header("虚拟筛选")
        st.markdown("AI模型筛选候选化合物，预测结合亲和力")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            target_id = st.text_input("靶点ChEMBL ID", "CHEMBL2364162", key="screen_target")
        with col2:
            max_compounds = st.number_input("筛选化合物数", 100, 10000, 1000, key="screen_compounds")
        
        if st.button("🔬 开始虚拟筛选", key="btn_screen"):
            with st.spinner("正在筛选化合物库..."):
                result = call_api("/screening/virtual", "POST", {
                    "target_chembl_id": target_id,
                    "max_compounds": max_compounds,
                    "top_n": 20
                })
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(f"筛选完成: {result.get('hits_found', 0)} 个Hit化合物")
                    
                    if "top_candidates" in result:
                        df = pd.DataFrame(result["top_candidates"])
                        st.dataframe(df, use_container_width=True)
    
    # ===== Tab 3: 分子生成 =====
    with tab3:
        st.header("分子生成")
        st.markdown("基于AI生成新型候选分子")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            gen_target = st.text_input("靶点名称", "EGFR", key="gen_target")
        with col2:
            gen_n = st.number_input("生成数量", 10, 500, 100, key="gen_n")
        with col3:
            gen_top = st.number_input("展示Top", 5, 50, 20, key="gen_top")
        
        if st.button("🧬 开始分子生成", key="btn_gen"):
            with st.spinner("正在生成候选分子..."):
                result = call_api("/molecule/generate", "POST", {
                    "target_name": gen_target,
                    "n_generate": gen_n,
                    "top_n": gen_top
                })
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(f"生成完成: {result.get('valid_molecules', 0)} 个有效分子")
                    
                    if "top_candidates" in result:
                        df = pd.DataFrame(result["top_candidates"])
                        st.dataframe(df, use_container_width=True)
    
    # ===== Tab 4: ADMET预测 =====
    with tab4:
        st.header("ADMET预测")
        st.markdown("预测化合物的吸收、分布、代谢、排泄和毒性")
        
        smiles_input = st.text_area(
            "输入SMILES (每行一个或逗号分隔)",
            "CC(=O)OC1=CC=CC=C1C(=O)O\nCCO\nCC(=O)NC1=CC=C(O)C=C1",
            key="admet_smiles"
        )
        
        if st.button("💊 开始ADMET预测", key="btn_admet"):
            smiles_list = [s.strip() for s in smiles_input.replace(",", "\n").split("\n") if s.strip()]
            
            with st.spinner(f"正在预测 {len(smiles_list)} 个化合物的ADMET..."):
                result = call_api("/admet/predict", "POST", {
                    "smiles_list": smiles_list
                })
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("ADMET预测完成")
                    
                    if "predictions" in result:
                        for pred in result["predictions"]:
                            with st.expander(f"SMILES: {pred.get('smiles', '')[:30]}..."):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("综合评分", pred.get("overall", "N/A"))
                                with col2:
                                    st.metric("吸收", pred.get("absorption", "N/A"))
                                with col3:
                                    st.metric("毒性", pred.get("toxicity", "N/A"))
                                
                                st.json(pred)
    
    # ===== Tab 5: 先导优化 =====
    with tab5:
        st.header("先导化合物优化")
        st.markdown("基于AI的分子结构优化，改善ADMET性质")
        
        opt_smiles = st.text_input("输入先导化合物SMILES", "CC(=O)OC1=CC=CC=C1C(=O)O", key="opt_smiles")
        
        if st.button("⚗️ 开始优化", key="btn_opt"):
            with st.spinner("正在优化分子结构..."):
                result = call_api("/molecule/optimize", "POST", {
                    "smiles": opt_smiles,
                    "n_generate": 10
                })
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(f"优化完成: 生成 {result.get('total_generated', 0)} 个衍生物")
                    
                    if "optimized_molecules" in result:
                        df = pd.DataFrame(result["optimized_molecules"])
                        st.dataframe(df, use_container_width=True)
    
    # ===== Tab 6: 全流程Pipeline =====
    with tab6:
        st.header("全流程Pipeline")
        st.markdown("从疾病到候选药物的自动化全流程")
        
        col1, col2 = st.columns(2)
        with col1:
            pipe_disease = st.text_input("目标疾病", "非小细胞肺癌", key="pipe_disease")
        with col2:
            pipe_target = st.text_input("靶点 (可选，留空自动发现)", "", key="pipe_target")
        
        if st.button("🔄 启动全流程", key="btn_pipe"):
            with st.spinner("正在执行全流程Pipeline...这可能需要几分钟"):
                result = call_api("/pipeline/run", "POST", {
                    "disease": pipe_disease,
                    "target": pipe_target if pipe_target else None,
                    "auto_mode": True
                })
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("全流程Pipeline完成!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("完成阶段", len(result.get("stages_completed", [])))
                    with col2:
                        st.metric("最终候选", len(result.get("final_candidates", [])))
                    with col3:
                        st.metric("耗时", f"{result.get('execution_time', 0):.1f}s")
                    
                    st.markdown("### 流程阶段")
                    st.json(result.get("stages_completed", []))
                    
                    if result.get("final_candidates"):
                        st.markdown("### 最终候选药物")
                        df = pd.DataFrame(result["final_candidates"])
                        st.dataframe(df, use_container_width=True)
    
    # ===== 底部信息 =====
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>MediPharma v2.0 — AI Drug Discovery Platform</p>
        <p>Built by MoKangMedical | 
           <a href='https://github.com/MoKangMedical/medi-pharma'>GitHub</a> | 
           <a href='https://mokangmedical.github.io/medi-pharma/'>Documentation</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
