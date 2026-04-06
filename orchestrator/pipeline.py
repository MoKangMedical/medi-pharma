"""
全流程编排器
靶点发现→虚拟筛选→分子生成→先导优化→ADMET评估的完整Pipeline
"""

import logging
import json
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Pipeline配置"""
    disease: str
    target: str = ""
    target_chembl_id: str = ""
    max_papers: int = 30
    max_compounds: int = 500
    n_generate: int = 100
    n_optimize: int = 30
    top_n: int = 10
    use_docking: bool = False
    auto_mode: bool = True  # 全自动模式


@dataclass
class PipelineResult:
    """Pipeline执行结果"""
    disease: str
    target: str
    stages_completed: list[str]
    target_report: Optional[dict] = None
    screening_report: Optional[dict] = None
    generation_report: Optional[dict] = None
    optimization_report: Optional[dict] = None
    admet_reports: list[dict] = field(default_factory=list)
    final_candidates: list[dict] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = ""


class PipelineOrchestrator:
    """
    全流程编排器
    一键执行从靶点到候选药物的完整流程
    """

    def __init__(
        self,
        llm_client: Optional[OpenAI] = None,
        llm_model: str = "mimo-v2-pro"
    ):
        self.llm = llm_client
        self.model = llm_model

    def run_full_pipeline(self, config: PipelineConfig) -> PipelineResult:
        """执行完整pipeline"""
        start_time = datetime.now()
        stages = []

        logger.info(f"""
╔══════════════════════════════════════════════╗
║  MediPharma 全流程Pipeline                   ║
║  疾病: {config.disease:<37s} ║
║  靶点: {(config.target or '待发现'):<37s} ║
║  模式: {'全自动' if config.auto_mode else '交互式':<36s} ║
╚══════════════════════════════════════════════╝
        """)

        result = PipelineResult(
            disease=config.disease,
            target=config.target,
            stages_completed=[],
            timestamp=start_time.isoformat()
        )

        # ========== Stage 1: 靶点发现 ==========
        if not config.target:
            logger.info("📍 Stage 1: 靶点发现")
            try:
                from ..target_discovery.engine import TargetDiscoveryEngine
                td = TargetDiscoveryEngine(llm_client=self.llm, llm_model=self.model)
                report = td.discover_targets(
                    disease=config.disease,
                    max_papers=config.max_papers,
                    top_n=config.top_n
                )
                result.target_report = asdict(report)
                stages.append("target_discovery")

                # 自动选择Top靶点
                if config.auto_mode and report.top_targets:
                    config.target = report.top_targets[0]["gene_symbol"]
                    result.target = config.target
                    logger.info(f"✅ 自动选择靶点: {config.target}")
            except Exception as e:
                logger.error(f"❌ 靶点发现失败: {e}")
        else:
            stages.append("target_discovery (pre-specified)")

        # ========== Stage 2: 虚拟筛选 ==========
        logger.info(f"📍 Stage 2: 虚拟筛选 (靶点: {config.target})")
        try:
            from ..virtual_screening.engine import VirtualScreeningEngine
            vs = VirtualScreeningEngine()
            screening = vs.screen(
                target_chembl_id=config.target_chembl_id or config.target,
                max_compounds=config.max_compounds,
                top_n=config.top_n,
                use_docking=config.use_docking
            )
            result.screening_report = asdict(screening)
            stages.append("virtual_screening")
        except Exception as e:
            logger.error(f"❌ 虚拟筛选失败: {e}")

        # ========== Stage 3: 分子生成 ==========
        logger.info("📍 Stage 3: 分子生成")
        try:
            from ..molecular_generation.engine import MolecularGenerationEngine
            mg = MolecularGenerationEngine()
            generation = mg.generate_candidates(
                target_name=config.target,
                n_generate=config.n_generate,
                top_n=config.top_n
            )
            result.generation_report = asdict(generation)
            stages.append("molecular_generation")
        except Exception as e:
            logger.error(f"❌ 分子生成失败: {e}")

        # ========== Stage 4: ADMET评估 ==========
        logger.info("📍 Stage 4: ADMET评估")
        try:
            from ..admet_prediction.engine import ADMETEngine
            admet = ADMETEngine()

            # 评估生成的top分子
            if result.generation_report and result.generation_report.get("top_candidates"):
                smiles_list = [c["smiles"] for c in result.generation_report["top_candidates"][:10]]
                admet_results = admet.batch_predict(smiles_list)
                result.admet_reports = admet_results
                stages.append("admet_prediction")
        except Exception as e:
            logger.error(f"❌ ADMET评估失败: {e}")

        # ========== Stage 5: 先导优化 ==========
        logger.info("📍 Stage 5: 先导优化")
        try:
            from ..lead_optimization.engine import LeadOptimizationEngine
            lo = LeadOptimizationEngine()

            # 优化ADMET通过的分子
            pass_smiles = [
                r["smiles"] for r in result.admet_reports
                if r.get("pass_filter", False) and r.get("recommendation") == "pass"
            ] or [
                c["smiles"] for c in (result.generation_report or {}).get("top_candidates", [])[:3]
            ]

            if pass_smiles:
                opt_result = lo.optimize(
                    starting_smiles=pass_smiles[0],
                    max_generations=10,
                    population_size=20
                )
                result.optimization_report = opt_result
                stages.append("lead_optimization")

                # 最终候选
                result.final_candidates = opt_result.get("top_candidates", [])[:config.top_n]
        except Exception as e:
            logger.error(f"❌ 先导优化失败: {e}")

        # 完成
        elapsed = (datetime.now() - start_time).total_seconds()
        result.stages_completed = stages
        result.execution_time = round(elapsed, 1)

        logger.info(f"""
╔══════════════════════════════════════════════╗
║  Pipeline 完成                               ║
║  耗时: {elapsed:.1f}s{' ' * (36 - len(f'{elapsed:.1f}s'))}║
║  完成阶段: {len(stages)}{' ' * (33 - len(str(len(stages))))}║
║  最终候选: {len(result.final_candidates)}{' ' * (33 - len(str(len(result.final_candidates))))}║
╚══════════════════════════════════════════════╝
        """)

        return result
