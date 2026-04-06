"""
临床试验数据查询模块
整合ClinicalTrials.gov数据
"""

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

CLINICALTRIALS_API = "https://clinicaltrials.gov/api/v2"


class ClinicalDataQuery:
    """临床试验数据查询器"""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)

    def search_trials(
        self,
        disease: str,
        target: str = "",
        status: str = "RECRUITING,ACTIVE_NOT_RECRUITING",
        max_results: int = 20
    ) -> list[dict]:
        """
        搜索临床试验

        Args:
            disease: 疾病名称
            target: 靶点名称（可选）
            status: 试验状态过滤
            max_results: 最大返回数
        """
        try:
            query = disease
            if target:
                query += f" {target}"

            resp = self.client.get(
                f"{CLINICALTRIALS_API}/studies",
                params={
                    "query.cond": disease,
                    "query.term": target if target else "",
                    "filter.overallStatus": status,
                    "pageSize": max_results,
                    "format": "json"
                }
            )
            data = resp.json()
            studies = data.get("studies", [])

            results = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                ident = protocol.get("identificationModule", {})
                status_mod = protocol.get("statusModule", {})
                design = protocol.get("designModule", {})
                desc = protocol.get("descriptionModule", {})

                # 提取phase
                phases = design.get("phases", [])
                phase = ", ".join(phases) if phases else "N/A"

                # 提取干预措施
                interventions = []
                arms = design.get("armsInterventionsModule", {})
                for intv in arms.get("interventions", []):
                    interventions.append({
                        "name": intv.get("name", ""),
                        "type": intv.get("type", ""),
                    })

                results.append({
                    "nct_id": ident.get("nctId", ""),
                    "name": ident.get("briefTitle", ""),
                    "phase": phase,
                    "status": status_mod.get("overallStatus", ""),
                    "start_date": status_mod.get("startDateStruct", {}).get("date", ""),
                    "interventions": interventions[:3],
                    "description": desc.get("briefSummary", "")[:200],
                })

            logger.info(f"临床试验搜索: {disease}/{target} → {len(results)}个结果")
            return results

        except Exception as e:
            logger.error(f"临床试验搜索失败: {e}")
            return []

    def get_trial_details(self, nct_id: str) -> dict:
        """获取单个试验详情"""
        try:
            resp = self.client.get(
                f"{CLINICALTRIALS_API}/studies/{nct_id}",
                params={"format": "json"}
            )
            return resp.json()
        except Exception as e:
            logger.error(f"获取试验详情失败: {e}")
            return {}

    def analyze_competitive_landscape(
        self,
        disease: str,
        target: str = ""
    ) -> dict:
        """分析临床开发竞争格局"""
        trials = self.search_trials(disease, target, max_results=50)

        # 按phase统计
        phase_counts = {}
        for t in trials:
            phase = t.get("phase", "N/A")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        # 按干预措施统计
        intervention_counts = {}
        for t in trials:
            for intv in t.get("interventions", []):
                name = intv.get("name", "Unknown")
                intervention_counts[name] = intervention_counts.get(name, 0) + 1

        # Top干预措施
        top_interventions = sorted(
            intervention_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "total_trials": len(trials),
            "phase_distribution": phase_counts,
            "top_interventions": [{"name": k, "trials": v} for k, v in top_interventions],
            "active_competitors": len(set(
                i["name"] for t in trials for i in t.get("interventions", [])
            )),
        }
