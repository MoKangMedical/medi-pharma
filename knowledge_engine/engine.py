"""
知识引擎主模块
整合文献、专利、临床数据，构建药物研发知识图谱
"""

import logging
from dataclasses import dataclass, asdict
from typing import Optional

from openai import OpenAI

from .rag_search import RAGSearchEngine
from .patent_analyzer import PatentAnalyzer
from .clinical_data import ClinicalDataQuery

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeReport:
    """知识分析报告"""
    target: str
    disease: str
    literature_summary: str
    patent_landscape: dict
    clinical_trials: list[dict]
    competitive_analysis: str
    key_insights: list[str]


class KnowledgeEngine:
    """
    知识引擎
    为药物发现提供全面的知识支持
    """

    def __init__(
        self,
        llm_client: Optional[OpenAI] = None,
        llm_model: str = "mimo-v2-pro"
    ):
        self.rag = RAGSearchEngine(llm_client=llm_client, llm_model=llm_model)
        self.patent = PatentAnalyzer()
        self.clinical = ClinicalDataQuery()
        self.llm = llm_client
        self.model = llm_model

    def generate_knowledge_report(
        self,
        target: str,
        disease: str,
        max_literature: int = 20,
        include_patents: bool = True,
        include_clinical: bool = True
    ) -> KnowledgeReport:
        """
        生成靶点-疾病综合知识报告
        """
        logger.info(f"=== 生成知识报告: {target} x {disease} ===")

        # 文献综述
        literature = self.rag.search_and_summarize(
            query=f"{target} {disease} drug discovery",
            max_results=max_literature
        )

        # 专利分析
        patent_data = {}
        if include_patents:
            patent_data = self.patent.analyze_landscape(target, disease)

        # 临床试验
        trials = []
        if include_clinical:
            trials = self.clinical.search_trials(disease, target)

        # 竞品分析
        competitive = self._competitive_analysis(target, disease, trials)

        # 关键洞察
        insights = self._extract_insights(target, disease, literature, patent_data, trials)

        return KnowledgeReport(
            target=target,
            disease=disease,
            literature_summary=literature,
            patent_landscape=patent_data,
            clinical_trials=trials,
            competitive_analysis=competitive,
            key_insights=insights
        )

    def _competitive_analysis(
        self, target: str, disease: str, trials: list[dict]
    ) -> str:
        """竞品管线分析"""
        if not trials:
            return f"未找到针对{target}/{disease}的活跃临床试验。可能存在开发机会。"

        phases = {}
        for t in trials:
            phase = t.get("phase", "Unknown")
            phases[phase] = phases.get(phase, 0) + 1

        if self.llm:
            try:
                trials_text = "\n".join([
                    f"- {t.get('name', 'N/A')}: Phase {t.get('phase', '?')} - {t.get('status', '?')}"
                    for t in trials[:10]
                ])
                resp = self.llm.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是药物研发竞争情报专家。根据以下临床试验数据，分析竞争格局和差异化机会。"
                        },
                        {
                            "role": "user",
                            "content": f"靶点: {target}\n疾病: {disease}\n临床试验:\n{trials_text}"
                        }
                    ],
                    temperature=0.3
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning(f"竞品分析生成失败: {e}")

        # fallback
        summary = f"靶点{target}在{disease}领域的管线概况：\n"
        for phase, count in phases.items():
            summary += f"- {phase}: {count}个试验\n"
        return summary

    def _extract_insights(
        self,
        target: str,
        disease: str,
        literature: str,
        patents: dict,
        trials: list[dict]
    ) -> list[str]:
        """提取关键洞察"""
        insights = []

        # 基于数据的自动洞察
        if not trials:
            insights.append(f"{target}在{disease}领域无活跃临床试验，可能存在First-in-class机会")
        elif len(trials) < 3:
            insights.append(f"{target}在{disease}领域临床试验较少，竞争压力小")

        if patents:
            patent_count = patents.get("total_patents", 0)
            if patent_count > 100:
                insights.append(f"专利密集({patent_count}个)，需注意freedom-to-operate")
            elif patent_count < 20:
                insights.append(f"专利密度低({patent_count}个)，IP空间充足")

        # LLM补充洞察
        if self.llm and (literature or patents):
            try:
                resp = self.llm.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是药物研发战略顾问。根据以下信息，提取3-5个关键洞察，每个洞察一句话。"
                        },
                        {
                            "role": "user",
                            "content": f"靶点: {target}\n疾病: {disease}\n文献摘要: {literature[:500]}\n专利: {patents}"
                        }
                    ],
                    temperature=0.3
                )
                llm_insights = resp.choices[0].message.content
                # 按行分割
                for line in llm_insights.strip().split("\n"):
                    line = line.strip().lstrip("- 1234567890.")
                    if line:
                        insights.append(line)
            except Exception as e:
                logger.warning(f"LLM洞察提取失败: {e}")

        return insights[:8]
