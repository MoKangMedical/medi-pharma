#!/usr/bin/env python3
"""
MediPharma 端到端闭环演示
展示完整的药物发现流程：靶点→筛选→生成→ADMET→报告
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from admet_prediction.engine import ADMETEngine
from virtual_screening.engine import VirtualScreeningEngine
from molecular_generation.engine import MolecularGenerationEngine


def run_demo():
    """运行完整的药物发现演示"""
    
    print("=" * 70)
    print("  MediPharma — AI药物发现平台 端到端演示")
    print("  " + "=" * 66)
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # ===== Phase 1: 靶点信息 =====
    print("\n[Phase 1] 靶点信息")
    print("-" * 50)
    target = {
        "name": "EGFR",
        "chembl_id": "CHEMBL203",
        "disease": "非小细胞肺癌",
        "description": "表皮生长因子受体，肺癌重要治疗靶点"
    }
    print(f"  靶点: {target['name']} ({target['chembl_id']})")
    print(f"  疾病: {target['disease']}")
    print(f"  描述: {target['description']}")
    
    # ===== Phase 2: 虚拟筛选 =====
    print("\n[Phase 2] 虚拟筛选")
    print("-" * 50)
    screening_engine = VirtualScreeningEngine()
    screening_result = screening_engine.screen(
        target_chembl_id=target["chembl_id"],
        max_compounds=50,
        top_n=5,
        library_source="local"
    )
    
    print(f"  筛选化合物: {screening_result.total_screened}")
    print(f"  发现Hit: {screening_result.hits_found}")
    print(f"  方法: {screening_result.method}")
    
    if screening_result.top_candidates:
        print("\n  Top 5 候选化合物:")
        for i, mol in enumerate(screening_result.top_candidates[:5]):
            name = mol.get("name", "未知")
            pkd = mol.get("predicted_pkd", 0)
            smiles = mol.get("smiles", "")[:30]
            print(f"    #{i+1} {name:20s} | pKd={pkd:.2f} | {smiles}...")
    
    # ===== Phase 3: 分子生成 =====
    print("\n[Phase 3] AI分子生成")
    print("-" * 50)
    generation_engine = MolecularGenerationEngine()
    generation_result = generation_engine.generate_candidates(
        target_name=target["name"],
        n_generate=30,
        top_n=5
    )
    
    print(f"  生成总数: {generation_result.total_generated}")
    print(f"  有效分子: {generation_result.valid_molecules}")
    print(f"  方法: {generation_result.method}")
    
    if generation_result.top_candidates:
        print("\n  Top 5 生成分子:")
        for i, mol in enumerate(generation_result.top_candidates[:5]):
            qed = mol.get("qed", 0)
            mw = mol.get("mw", 0)
            smiles = mol.get("smiles", "")[:30]
            print(f"    #{i+1} QED={qed:.3f} MW={mw:.1f} | {smiles}...")
    
    # ===== Phase 4: ADMET预测 =====
    print("\n[Phase 4] ADMET预测")
    print("-" * 50)
    admet_engine = ADMETEngine()
    
    # 选择Top分子进行ADMET预测
    molecules_to_evaluate = []
    
    # 从筛选结果中取Top 3
    for mol in screening_result.top_candidates[:3]:
        molecules_to_evaluate.append({
            "source": "筛选",
            "name": mol.get("name", ""),
            "smiles": mol.get("smiles", "")
        })
    
    # 从生成结果中取Top 3
    for mol in generation_result.top_candidates[:3]:
        molecules_to_evaluate.append({
            "source": "生成",
            "name": "AI生成分子",
            "smiles": mol.get("smiles", "")
        })
    
    admet_results = []
    for mol in molecules_to_evaluate:
        smiles = mol["smiles"]
        if not smiles:
            continue
            
        report = admet_engine.predict(smiles)
        admet_results.append({
            **mol,
            "admet": report
        })
        
        status = "PASS" if report.pass_filter else "FAIL"
        print(f"  [{status}] {mol['name']:20s} | 综合={report.overall['total_score']:.2f} | {smiles[:25]}...")
    
    # ===== Phase 5: 综合报告 =====
    print("\n[Phase 5] 综合报告")
    print("-" * 50)
    
    # 筛选出通过ADMET的分子
    passed = [r for r in admet_results if r["admet"].pass_filter]
    failed = [r for r in admet_results if not r["admet"].pass_filter]
    
    print(f"  评估分子数: {len(admet_results)}")
    print(f"  ADMET通过: {len(passed)}")
    print(f"  ADMET未通过: {len(failed)}")
    
    if passed:
        print("\n  推荐候选药物:")
        for i, mol in enumerate(passed[:5]):
            admet = mol["admet"]
            print(f"    #{i+1} {mol['name']}")
            print(f"        SMILES: {mol['smiles'][:50]}...")
            print(f"        综合评分: {admet.overall['total_score']:.2f}")
            print(f"        吸收: {admet.overall['absorption']:.2f}")
            print(f"        毒性: {admet.overall['toxicity']:.2f}")
            print(f"        推荐: {admet.recommendation}")
    
    # ===== 保存结果 =====
    output = {
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "screening": {
            "total_screened": screening_result.total_screened,
            "hits_found": screening_result.hits_found,
            "top_candidates": screening_result.top_candidates[:5]
        },
        "generation": {
            "total_generated": generation_result.total_generated,
            "valid_molecules": generation_result.valid_molecules,
            "top_candidates": generation_result.top_candidates[:5]
        },
        "admet_evaluation": {
            "total_evaluated": len(admet_results),
            "passed": len(passed),
            "failed": len(failed)
        }
    }
    
    output_path = Path(__file__).parent / "demo_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n  结果已保存: {output_path}")
    
    print("\n" + "=" * 70)
    print("  演示完成!")
    print("=" * 70)
    
    return output


if __name__ == "__main__":
    run_demo()
