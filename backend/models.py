"""
FastAPI数据模型
所有API请求/响应的Pydantic模型
"""

from typing import Optional
from pydantic import BaseModel, Field


# ===== 靶点发现 =====
class TargetDiscoveryRequest(BaseModel):
    disease: str = Field(..., description="目标疾病名称")
    max_papers: int = Field(50, description="最大检索文献数")
    top_n: int = Field(10, description="返回Top N靶点")
    disease_burden: float = Field(0.8, description="疾病负担评分 (0-1)")
    unmet_need: float = Field(0.8, description="未满足需求评分 (0-1)")


class TargetScore(BaseModel):
    gene_symbol: str
    total_score: float
    evidence_score: float
    druggability_score: float
    novelty_score: float
    recommendation: str
    rank: int


class TargetDiscoveryResponse(BaseModel):
    disease: str
    total_candidates: int
    top_targets: list[TargetScore]
    summary: str


# ===== 虚拟筛选 =====
class ScreeningRequest(BaseModel):
    target_chembl_id: str = Field(..., description="ChEMBL靶点ID")
    protein_pdb: Optional[str] = Field(None, description="蛋白质PDB文件路径")
    max_compounds: int = Field(500, description="最大筛选化合物数")
    top_n: int = Field(20, description="返回Top N")
    use_docking: bool = Field(False, description="是否使用分子对接")


class ScreeningResponse(BaseModel):
    target: str
    total_screened: int
    hits_found: int
    top_candidates: list[dict]
    summary: str


# ===== 分子生成 =====
class GenerationRequest(BaseModel):
    target_name: str = Field("", description="靶点名称")
    scaffold: Optional[str] = Field(None, description="起始骨架SMILES")
    n_generate: int = Field(200, description="生成数量")
    top_n: int = Field(20, description="返回Top N")
    target_mw: float = Field(400, description="目标分子量")
    target_logp: float = Field(2.5, description="目标LogP")


class GenerationResponse(BaseModel):
    target: str
    total_generated: int
    valid_molecules: int
    top_candidates: list[dict]
    summary: str


# ===== ADMET预测 =====
class ADMETRequest(BaseModel):
    smiles: str = Field(..., description="分子SMILES")


class ADMETBatchRequest(BaseModel):
    smiles_list: list[str] = Field(..., description="分子SMILES列表")


class ADMETResponse(BaseModel):
    smiles: str
    absorption: dict
    distribution: dict
    metabolism: dict
    excretion: dict
    toxicity: dict
    synthesis: dict
    overall: dict
    pass_filter: bool
    recommendation: str


# ===== 先导优化 =====
class OptimizationRequest(BaseModel):
    smiles: str = Field(..., description="起始分子SMILES")
    objective_weights: Optional[dict] = Field(None, description="目标权重")
    max_generations: int = Field(20, description="最大优化代数")
    population_size: int = Field(30, description="种群大小")


class OptimizationResponse(BaseModel):
    starting_smiles: str
    candidates_found: int
    top_candidates: list[dict]
    optimization_trajectory: list[dict]


# ===== Pipeline =====
class PipelineRequest(BaseModel):
    disease: str = Field(..., description="目标疾病")
    target: str = Field("", description="靶点（空=自动发现）")
    target_chembl_id: str = Field("", description="ChEMBL ID")
    max_papers: int = Field(30)
    max_compounds: int = Field(500)
    n_generate: int = Field(100)
    top_n: int = Field(10)
    auto_mode: bool = Field(True, description="全自动模式")


class PipelineResponse(BaseModel):
    disease: str
    target: str
    stages_completed: list[str]
    final_candidates: list[dict]
    execution_time: float
    report: str = ""


# ===== 知识引擎 =====
class KnowledgeRequest(BaseModel):
    target: str = Field(..., description="靶点名称")
    disease: str = Field(..., description="疾病名称")
    include_patents: bool = Field(True)
    include_clinical: bool = Field(True)


class KnowledgeResponse(BaseModel):
    target: str
    disease: str
    literature_summary: str
    patent_landscape: dict
    clinical_trials: list[dict]
    competitive_analysis: str
    key_insights: list[str]


# ===== 通用 =====
class HealthResponse(BaseModel):
    status: str
    version: str
    modules: list[str]
    timestamp: str
