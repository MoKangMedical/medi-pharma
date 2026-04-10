"""
FastAPI路由
MediPharma REST API接口
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    TargetDiscoveryRequest, TargetDiscoveryResponse,
    ScreeningRequest, ScreeningResponse,
    GenerationRequest, GenerationResponse,
    ADMETRequest, ADMETBatchRequest, ADMETResponse,
    OptimizationRequest, OptimizationResponse,
    PipelineRequest, PipelineResponse,
    KnowledgeRequest, KnowledgeResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)

# 创建FastAPI app
app = FastAPI(
    title="MediPharma API",
    description="AI驱动药物发现平台 — 伪装成服务公司的软件公司",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 健康检查 =====
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        modules=[
            "target_discovery",
            "virtual_screening",
            "molecular_generation",
            "admet_prediction",
            "lead_optimization",
            "knowledge_engine",
            "orchestrator",
        ],
        timestamp=datetime.now().isoformat()
    )


# ===== 靶点发现 =====
@app.post("/api/v1/targets/discover", response_model=TargetDiscoveryResponse)
async def discover_targets(req: TargetDiscoveryRequest):
    """靶点发现：疾病 → 候选靶点排名"""
    try:
        from target_discovery.engine import TargetDiscoveryEngine
        engine = TargetDiscoveryEngine()
        report = engine.discover_targets(
            disease=req.disease,
            max_papers=req.max_papers,
            top_n=req.top_n,
            disease_burden=req.disease_burden,
            unmet_need=req.unmet_need
        )
        return TargetDiscoveryResponse(
            disease=report.disease,
            total_candidates=report.total_candidates,
            top_targets=report.top_targets,
            summary=report.summary
        )
    except Exception as e:
        logger.error(f"靶点发现失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 虚拟筛选 =====
@app.post("/api/v1/screening/run", response_model=ScreeningResponse)
async def run_screening(req: ScreeningRequest):
    """虚拟筛选：靶点 → Top候选化合物"""
    try:
        from virtual_screening.engine import VirtualScreeningEngine
        engine = VirtualScreeningEngine()
        result = engine.screen(
            target_chembl_id=req.target_chembl_id,
            protein_pdb=req.protein_pdb,
            max_compounds=req.max_compounds,
            top_n=req.top_n,
            use_docking=req.use_docking
        )
        return ScreeningResponse(
            target=result.target,
            total_screened=result.total_screened,
            hits_found=result.hits_found,
            top_candidates=result.top_candidates,
            summary=result.summary
        )
    except Exception as e:
        logger.error(f"虚拟筛选失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 分子生成 =====
@app.post("/api/v1/generate", response_model=GenerationResponse)
async def generate_molecules(req: GenerationRequest):
    """分子生成：从头设计候选分子"""
    try:
        from molecular_generation.engine import MolecularGenerationEngine
        engine = MolecularGenerationEngine()
        report = engine.generate_candidates(
            target_name=req.target_name,
            scaffold=req.scaffold,
            n_generate=req.n_generate,
            top_n=req.top_n,
            target_properties={"mw": req.target_mw, "logp": req.target_logp}
        )
        return GenerationResponse(
            target=report.target,
            total_generated=report.total_generated,
            valid_molecules=report.valid_molecules,
            top_candidates=report.top_candidates,
            summary=report.summary
        )
    except Exception as e:
        logger.error(f"分子生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== ADMET预测 =====
@app.post("/api/v1/admet/predict", response_model=ADMETResponse)
async def predict_admet(req: ADMETRequest):
    """ADMET预测：单分子全ADMET评估"""
    try:
        from admet_prediction.engine import ADMETEngine
        engine = ADMETEngine()
        report = engine.predict(req.smiles)
        return ADMETResponse(
            smiles=report.smiles,
            absorption=report.absorption,
            distribution=report.distribution,
            metabolism=report.metabolism,
            excretion=report.excretion,
            toxicity=report.toxicity,
            synthesis=report.synthesis,
            overall=report.overall,
            pass_filter=report.pass_filter,
            recommendation=report.recommendation
        )
    except Exception as e:
        logger.error(f"ADMET预测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/admet/batch")
async def batch_predict_admet(req: ADMETBatchRequest):
    """ADMET批量预测"""
    try:
        from admet_prediction.engine import ADMETEngine
        engine = ADMETEngine()
        results = engine.batch_predict(req.smiles_list)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 先导优化 =====
@app.post("/api/v1/optimize", response_model=OptimizationResponse)
async def optimize_lead(req: OptimizationRequest):
    """先导优化：分子多参数优化"""
    try:
        from lead_optimization.engine import LeadOptimizationEngine
        engine = LeadOptimizationEngine()
        result = engine.optimize(
            starting_smiles=req.smiles,
            objective_weights=req.objective_weights,
            max_generations=req.max_generations,
            population_size=req.population_size
        )
        return OptimizationResponse(
            starting_smiles=result["starting_smiles"],
            candidates_found=result["candidates_found"],
            top_candidates=result["top_candidates"],
            optimization_trajectory=result["optimization_trajectory"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 全流程Pipeline =====
@app.post("/api/v1/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(req: PipelineRequest):
    """一键全流程：靶点→筛选→生成→优化→ADMET"""
    try:
        from orchestrator.pipeline import PipelineOrchestrator, PipelineConfig
        orchestrator = PipelineOrchestrator()
        config = PipelineConfig(
            disease=req.disease,
            target=req.target,
            target_chembl_id=req.target_chembl_id,
            max_papers=req.max_papers,
            max_compounds=req.max_compounds,
            n_generate=req.n_generate,
            top_n=req.top_n,
            auto_mode=req.auto_mode
        )
        result = orchestrator.run_full_pipeline(config)
        return PipelineResponse(
            disease=result.disease,
            target=result.target,
            stages_completed=result.stages_completed,
            final_candidates=result.final_candidates,
            execution_time=result.execution_time,
        )
    except Exception as e:
        logger.error(f"Pipeline执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 知识引擎 =====
@app.post("/api/v1/knowledge/report", response_model=KnowledgeResponse)
async def knowledge_report(req: KnowledgeRequest):
    """知识分析：靶点-疾病综合报告"""
    try:
        from knowledge_engine.engine import KnowledgeEngine
        engine = KnowledgeEngine()
        report = engine.generate_knowledge_report(
            target=req.target,
            disease=req.disease,
            include_patents=req.include_patents,
            include_clinical=req.include_clinical
        )
        return KnowledgeResponse(
            target=report.target,
            disease=report.disease,
            literature_summary=report.literature_summary,
            patent_landscape=report.patent_landscape,
            clinical_trials=report.clinical_trials,
            competitive_analysis=report.competitive_analysis,
            key_insights=report.key_insights
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== 开放生态资源 =====
@app.get("/api/v1/ecosystem")
async def get_ecosystem():
    """获取AI药物发现开源生态资源清单"""
    try:
        from pathlib import Path
        import json
        eco_path = Path(__file__).parent.parent / "docs" / "open-source-ecosystem.md"
        if eco_path.exists():
            content = eco_path.read_text()
            return {"content": content, "format": "markdown"}
        return {"content": "生态清单未找到", "format": "text"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
