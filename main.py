#!/usr/bin/env python3
"""
MediPharma v2.0 — AI驱动药物发现平台
伪装成服务公司的软件公司

Usage:
    # 启动Web服务
    python main.py serve [--port 8095] [--host 0.0.0.0]

    # CLI：靶点发现
    python main.py target --disease "重症肌无力"

    # CLI：虚拟筛选
    python main.py screen --target CHEMBL2364162

    # CLI：分子生成
    python main.py generate --target CHRM1 --n 50

    # CLI：ADMET预测
    python main.py admet --smiles "CCO"

    # CLI：全流程Pipeline
    python main.py pipeline --disease "重症肌无力" --auto

    # 查看生态资源
    python main.py ecosystem
"""

import sys
import json
import logging
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("medipharma")


def cmd_serve(args):
    """启动FastAPI服务"""
    try:
        import uvicorn
        logger.info(f"🚀 启动MediPharma API服务: {args.host}:{args.port}")
        uvicorn.run(
            "backend.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except ImportError:
        logger.error("请安装uvicorn: pip install uvicorn")
        sys.exit(1)


def cmd_target(args):
    """靶点发现CLI"""
    from target_discovery.engine import TargetDiscoveryEngine
    engine = TargetDiscoveryEngine()
    report = engine.discover_targets(
        disease=args.disease,
        max_papers=args.max_papers,
        top_n=args.top_n
    )
    print(f"\n{'='*60}")
    print(f"🎯 靶点发现报告: {args.disease}")
    print(f"{'='*60}")
    print(f"候选靶点总数: {report.total_candidates}")
    print(f"\nTop靶点:")
    for t in report.top_targets[:args.top_n]:
        print(f"  #{t['rank']} {t['gene_symbol']}: 综合分={t['total_score']:.3f} ({t['recommendation']})")
    print(f"\n摘要: {report.summary}")


def cmd_screen(args):
    """虚拟筛选CLI"""
    from virtual_screening.engine import VirtualScreeningEngine
    engine = VirtualScreeningEngine()
    result = engine.screen(
        target_chembl_id=args.target,
        max_compounds=args.max_compounds,
        top_n=args.top_n
    )
    print(f"\n{'='*60}")
    print(f"🔬 虚拟筛选报告: {args.target}")
    print(f"{'='*60}")
    print(f"筛选化合物: {result.total_screened}")
    print(f"发现Hit: {result.hits_found}")
    print(f"\nTop候选:")
    for i, c in enumerate(result.top_candidates[:args.top_n]):
        smiles = c.get("smiles", "")[:40]
        pKd = c.get("predicted_pkd", 0)
        print(f"  #{i+1} pKd={pKd:.2f} | {smiles}...")


def cmd_generate(args):
    """分子生成CLI"""
    from molecular_generation.engine import MolecularGenerationEngine
    engine = MolecularGenerationEngine()
    report = engine.generate_candidates(
        target_name=args.target,
        n_generate=args.n,
        top_n=args.top_n
    )
    print(f"\n{'='*60}")
    print(f"🧬 分子生成报告: {args.target or 'De Novo'}")
    print(f"{'='*60}")
    print(f"生成总数: {report.total_generated}")
    print(f"有效分子: {report.valid_molecules}")
    print(f"\nTop候选:")
    for i, c in enumerate(report.top_candidates[:args.top_n]):
        smiles = c.get("smiles", "")[:45]
        qed = c.get("qed", 0)
        sa = c.get("sa_score", 0)
        print(f"  #{i+1} QED={qed:.3f} SA={sa:.1f} | {smiles}")


def cmd_admet(args):
    """ADMET预测CLI"""
    from admet_prediction.engine import ADMETEngine
    engine = ADMETEngine()

    smiles_list = [s.strip() for s in args.smiles.split(",")]
    for smiles in smiles_list:
        report = engine.predict(smiles)
        print(f"\n{'='*60}")
        print(f"💊 ADMET报告: {smiles[:50]}")
        print(f"{'='*60}")
        print(f"推荐: {report.recommendation} | 通过: {report.pass_filter}")
        print(f"综合评分: {report.overall}")
        print(f"吸收: {report.absorption}")
        print(f"毒性: {report.toxicity}")
        print(f"合成: {report.synthesis}")


def cmd_pipeline(args):
    """全流程Pipeline CLI"""
    from orchestrator.pipeline import PipelineOrchestrator, PipelineConfig
    orchestrator = PipelineOrchestrator()
    config = PipelineConfig(
        disease=args.disease,
        target=args.target,
        auto_mode=args.auto
    )
    result = orchestrator.run_full_pipeline(config)
    print(f"\n{'='*60}")
    print(f"💊 MediPharma 全流程Pipeline")
    print(f"{'='*60}")
    print(f"疾病: {result.disease}")
    print(f"靶点: {result.target}")
    print(f"完成阶段: {' → '.join(result.stages_completed)}")
    print(f"最终候选: {len(result.final_candidates)}")
    print(f"耗时: {result.execution_time:.1f}s")


def cmd_ecosystem(args):
    """查看开源生态资源"""
    eco_path = Path(__file__).parent / "docs" / "open-source-ecosystem.md"
    if eco_path.exists():
        print(eco_path.read_text())
    else:
        print("生态清单文件未找到")


def main():
    parser = argparse.ArgumentParser(
        prog="medipharma",
        description="MediPharma v2.0 — AI驱动药物发现平台"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # serve
    p_serve = subparsers.add_parser("serve", help="启动Web服务")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8095)
    p_serve.add_argument("--reload", action="store_true")

    # target
    p_target = subparsers.add_parser("target", help="靶点发现")
    p_target.add_argument("--disease", required=True, help="目标疾病")
    p_target.add_argument("--max-papers", type=int, default=30)
    p_target.add_argument("--top-n", type=int, default=10)

    # screen
    p_screen = subparsers.add_parser("screen", help="虚拟筛选")
    p_screen.add_argument("--target", required=True, help="ChEMBL靶点ID")
    p_screen.add_argument("--max-compounds", type=int, default=500)
    p_screen.add_argument("--top-n", type=int, default=20)

    # generate
    p_gen = subparsers.add_parser("generate", help="分子生成")
    p_gen.add_argument("--target", default="", help="靶点名称")
    p_gen.add_argument("-n", type=int, default=100, help="生成数量")
    p_gen.add_argument("--top-n", type=int, default=20)

    # admet
    p_admet = subparsers.add_parser("admet", help="ADMET预测")
    p_admet.add_argument("--smiles", required=True, help="SMILES (逗号分隔)")

    # pipeline
    p_pipe = subparsers.add_parser("pipeline", help="全流程Pipeline")
    p_pipe.add_argument("--disease", required=True, help="目标疾病")
    p_pipe.add_argument("--target", default="", help="靶点 (空=自动发现)")
    p_pipe.add_argument("--auto", action="store_true", default=True)

    # ecosystem
    subparsers.add_parser("ecosystem", help="查看开源生态资源")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "serve": cmd_serve,
        "target": cmd_target,
        "screen": cmd_screen,
        "generate": cmd_generate,
        "admet": cmd_admet,
        "pipeline": cmd_pipeline,
        "ecosystem": cmd_ecosystem,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
