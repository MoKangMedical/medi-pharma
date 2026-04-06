"""
专利分析模块
分析药物研发相关专利 landscape
"""

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class PatentAnalyzer:
    """专利景观分析器"""

    # Google Patents Public Data API (BigQuery)
    # 简化版：基于关键词搜索

    def analyze_landscape(
        self,
        target: str,
        disease: str,
        years_back: int = 10
    ) -> dict:
        """
        分析专利景观

        Returns:
            dict: {
                total_patents: int,
                top_assignees: list,
                year_trend: dict,
                technology_areas: list,
                freedom_to_operate: str,
            }
        """
        # 使用Google Patents搜索
        patents = self._search_patents(target, disease, years_back)

        if not patents:
            return {
                "total_patents": 0,
                "top_assignees": [],
                "year_trend": {},
                "technology_areas": [],
                "freedom_to_operate": "数据不足，需进一步分析",
                "note": "建议使用专业专利数据库(如Espacenet, USPTO)进行详细FTO分析"
            }

        # 分析
        assignees = {}
        years = {}
        for p in patents:
            assignee = p.get("assignee", "Unknown")
            assignees[assignee] = assignees.get(assignee, 0) + 1
            year = p.get("year", "Unknown")
            years[year] = years.get(year, 0) + 1

        top_assignees = sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_patents": len(patents),
            "top_assignees": [{"name": a[0], "count": a[1]} for a in top_assignees],
            "year_trend": years,
            "technology_areas": self._extract_areas(patents),
            "freedom_to_operate": self._assess_fto(patents),
        }

    def _search_patents(
        self,
        target: str,
        disease: str,
        years_back: int
    ) -> list[dict]:
        """搜索专利（通过Google Patents简化搜索）"""
        try:
            client = httpx.Client(timeout=30.0)
            # 简化搜索 - 实际应用中应使用专业API
            query = f"{target} {disease} drug"
            resp = client.get(
                "https://patents.google.com/xhr/query",
                params={"q": query, "num": 20}
            )
            # Google Patents的API需要复杂的处理，这里简化
            logger.info(f"专利搜索: {query}")
            return []
        except Exception as e:
            logger.warning(f"专利搜索失败: {e}")
            return []

    def _extract_areas(self, patents: list[dict]) -> list[str]:
        """提取技术领域"""
        areas = set()
        for p in patents:
            for area in p.get("classifications", []):
                areas.add(area)
        return list(areas)[:10]

    def _assess_fto(self, patents: list[dict]) -> str:
        """评估自由运营空间"""
        if len(patents) < 10:
            return "专利密度较低，FTO空间较大。但仍需检查核心专利。"
        elif len(patents) < 50:
            return "中等专利密度。需重点检查方法专利和化合物专利。"
        else:
            return "高专利密度区域。建议聘请专利律师进行详细FTO分析，考虑差异化策略。"
