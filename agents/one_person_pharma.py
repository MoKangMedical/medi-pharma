"""
MediPharma — 一人药企全流程Agent
参考哈佛/斯坦福模式：1人+AI=完整药物发现管线
"""
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class PipelineStage(Enum):
    """管线阶段"""
    TARGET_IDENTIFICATION = "target_identification"
    TARGET_VALIDATION = "target_validation"
    HIT_IDENTIFICATION = "hit_identification"
    HIT_TO_LEAD = "hit_to_lead"
    LEAD_OPTIMIZATION = "lead_optimization"
    PRECLINICAL = "preclinical"
    CANDIDATE_SELECTION = "candidate_selection"


@dataclass
class DrugCandidate:
    """药物候选"""
    candidate_id: str
    name: str
    target: str
    disease: str
    stage: PipelineStage
    smiles: str
    properties: Dict[str, float] = field(default_factory=dict)
    timeline_months: int = 0
    cost_estimate: float = 0.0


@dataclass
class PipelineProject:
    """管线项目"""
    project_id: str
    name: str
    disease: str
    target_gene: str
    current_stage: PipelineStage
    candidates: List[DrugCandidate] = field(default_factory=list)
    start_date: str = ""
    estimated_completion: str = ""
    total_cost: float = 0.0
    timeline_months: int = 0


class OnePersonPharmaAgent:
    """
    一人药企AI Agent
    全流程自动化药物发现
    参考哈佛/斯坦福模式
    """

    # 阶段时间线（月）
    STAGE_TIMELINE = {
        PipelineStage.TARGET_IDENTIFICATION: 2,
        PipelineStage.TARGET_VALIDATION: 3,
        PipelineStage.HIT_IDENTIFICATION: 2,
        PipelineStage.HIT_TO_LEAD: 3,
        PipelineStage.LEAD_OPTIMIZATION: 6,
        PipelineStage.PRECLINICAL: 6,
        PipelineStage.CANDIDATE_SELECTION: 2,
    }

    # 阶段成本（万人民币）
    STAGE_COST = {
        PipelineStage.TARGET_IDENTIFICATION: 20,
        PipelineStage.TARGET_VALIDATION: 30,
        PipelineStage.HIT_IDENTIFICATION: 25,
        PipelineStage.HIT_TO_LEAD: 40,
        PipelineStage.LEAD_OPTIMIZATION: 80,
        PipelineStage.PRECLINICAL: 150,
        PipelineStage.CANDIDATE_SELECTION: 30,
    }

    def __init__(self):
        self.projects: List[PipelineProject] = []
        self.agent_logs: List[Dict] = []

    def start_project(self, name: str, disease: str, 
                      target_gene: str) -> PipelineProject:
        """启动新项目"""
        project = PipelineProject(
            project_id=f"PRJ_{len(self.projects)+1:03d}",
            name=name,
            disease=disease,
            target_gene=target_gene,
            current_stage=PipelineStage.TARGET_IDENTIFICATION,
            start_date=time.strftime("%Y-%m-%d"),
        )
        
        self.projects.append(project)
        self._log(f"启动项目: {name} ({disease})")
        
        return project

    def advance_stage(self, project_id: str) -> Dict:
        """推进项目到下一阶段"""
        project = self._find_project(project_id)
        if not project:
            return {"error": "Project not found"}
        
        current = project.current_stage
        stages = list(PipelineStage)
        current_idx = stages.index(current)
        
        if current_idx >= len(stages) - 1:
            return {"error": "Project already at final stage"}
        
        next_stage = stages[current_idx + 1]
        project.current_stage = next_stage
        
        # 累加时间和成本
        timeline = self.STAGE_TIMELINE.get(next_stage, 0)
        cost = self.STAGE_COST.get(next_stage, 0)
        project.timeline_months += timeline
        project.total_cost += cost
        
        self._log(f"项目 {project.name} 推进到: {next_stage.value}")
        
        return {
            "project_id": project.project_id,
            "previous_stage": current.value,
            "new_stage": next_stage.value,
            "timeline_added": timeline,
            "cost_added": cost,
            "total_timeline": project.timeline_months,
            "total_cost": project.total_cost,
        }

    def generate_candidate(self, project_id: str, 
                          name: str, smiles: str) -> DrugCandidate:
        """生成候选药物"""
        project = self._find_project(project_id)
        if not project:
            return None
        
        candidate = DrugCandidate(
            candidate_id=f"CMP_{project_id}_{len(project.candidates)+1:02d}",
            name=name,
            target=project.target_gene,
            disease=project.disease,
            stage=project.current_stage,
            smiles=smiles,
            properties={
                "potency_ic50": 50.0,  # nM
                "selectivity": 100.0,  # fold
                "solubility": 50.0,    # μg/mL
                "logp": 2.5,
                "mw": 450.0,
            },
            timeline_months=project.timeline_months,
            cost_estimate=project.total_cost,
        )
        
        project.candidates.append(candidate)
        self._log(f"生成候选药物: {name}")
        
        return candidate

    def get_pipeline_report(self, project_id: str = None) -> Dict:
        """获取管线报告"""
        if project_id:
            project = self._find_project(project_id)
            if not project:
                return {"error": "Project not found"}
            projects = [project]
        else:
            projects = self.projects
        
        report = {
            "total_projects": len(projects),
            "projects": [],
        }
        
        for p in projects:
            # 计算进度
            stages = list(PipelineStage)
            progress = (stages.index(p.current_stage) + 1) / len(stages) * 100
            
            report["projects"].append({
                "id": p.project_id,
                "name": p.name,
                "disease": p.disease,
                "target": p.target_gene,
                "current_stage": p.current_stage.value,
                "progress": f"{progress:.0f}%",
                "timeline_months": p.timeline_months,
                "total_cost": p.total_cost,
                "candidates": len(p.candidates),
            })
        
        return report

    def compare_with_traditional(self, project_id: str) -> Dict:
        """对比AI vs 传统流程"""
        project = self._find_project(project_id)
        if not project:
            return {"error": "Project not found"}
        
        # 传统流程时间和成本
        traditional_timeline = 120  # 10年
        traditional_cost = 50000   # 5亿
        
        ai_timeline = project.timeline_months or 24
        ai_cost = project.total_cost or 375
        
        return {
            "traditional": {
                "timeline_years": 10,
                "timeline_months": traditional_timeline,
                "cost_million": traditional_cost / 100,
                "description": "传统药物发现流程"
            },
            "ai_powered": {
                "timeline_years": round(ai_timeline / 12, 1),
                "timeline_months": ai_timeline,
                "cost_million": ai_cost / 100,
                "description": "AI驱动药物发现（MediPharma）"
            },
            "improvement": {
                "timeline_reduction": f"{((traditional_timeline - ai_timeline) / traditional_timeline * 100):.0f}%",
                "cost_reduction": f"{((traditional_cost - ai_cost) / traditional_cost * 100):.0f}%",
            }
        }

    def _find_project(self, project_id: str) -> Optional[PipelineProject]:
        """查找项目"""
        for p in self.projects:
            if p.project_id == project_id:
                return p
        return None

    def _log(self, message: str):
        """记录日志"""
        self.agent_logs.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        })


# ========== 测试 ==========
if __name__ == "__main__":
    agent = OnePersonPharmaAgent()
    
    print("=" * 60)
    print("🧬 MediPharma 一人药企Agent测试")
    print("=" * 60)
    
    # 启动项目
    project = agent.start_project(
        name="MG-AChR激动剂",
        disease="重症肌无力",
        target_gene="CHRNA1"
    )
    
    print(f"\n📋 新项目: {project.name}")
    print(f"   疾病: {project.disease}")
    print(f"   靶点: {project.target_gene}")
    
    # 推进到各阶段
    stages_to_advance = 5
    for i in range(stages_to_advance):
        result = agent.advance_stage(project.project_id)
        print(f"\n📈 推进: {result['previous_stage']} → {result['new_stage']}")
    
    # 生成候选药物
    candidate = agent.generate_candidate(
        project.project_id,
        name="MG-001",
        smiles="CC(=O)OC1=CC=CC=C1C(=O)O"
    )
    
    print(f"\n💊 候选药物: {candidate.name}")
    
    # 对比报告
    comparison = agent.compare_with_traditional(project.project_id)
    print(f"\n📊 AI vs 传统流程对比:")
    print(f"   传统: {comparison['traditional']['timeline_years']}年, {comparison['traditional']['cost_million']}亿")
    print(f"   AI:   {comparison['ai_powered']['timeline_years']}年, {comparison['ai_powered']['cost_million']}亿")
    print(f"   时间缩短: {comparison['improvement']['timeline_reduction']}")
    print(f"   成本降低: {comparison['improvement']['cost_reduction']}")
    
    # 管线报告
    report = agent.get_pipeline_report()
    print(f"\n📋 管线总览:")
    for p in report['projects']:
        print(f"   {p['name']}: {p['progress']} ({p['current_stage']})")
