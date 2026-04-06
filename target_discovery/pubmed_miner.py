"""
PubMed文献挖掘模块
通过NCBI E-utilities API挖掘靶点相关文献，提取基因-疾病关联
"""

import json
import time
import logging
from typing import Optional
from dataclasses import dataclass, asdict

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

# NCBI E-utilities base URL
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


@dataclass
class LiteratureHit:
    """文献挖掘结果"""
    pmid: str
    title: str
    abstract: str
    genes_mentioned: list[str]
    relevance_score: float  # 0-1
    year: int


@dataclass
class TargetEvidence:
    """靶点证据汇总"""
    gene_symbol: str
    total_papers: int
    avg_relevance: float
    key_papers: list[LiteratureHit]
    disease_associations: list[str]
    evidence_strength: str  # strong / moderate / weak


class PubMedMiner:
    """PubMed文献挖掘器：疾病→基因→靶点"""

    def __init__(self, email: str = "medipharma@example.com", api_key: Optional[str] = None):
        self.email = email
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)

    def search_disease_genes(
        self,
        disease: str,
        max_results: int = 100,
        min_year: int = 2015
    ) -> list[dict]:
        """
        搜索疾病相关基因文献
        返回PMID列表和摘要
        """
        # Step 1: 搜索PubMed
        query = f'({disease}[Title/Abstract]) AND (gene[Title/Abstract] OR target[Title/Abstract]) AND {min_year}:2026[PDAT]'
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
            "email": self.email
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            resp = self.client.get(f"{EUTILS_BASE}/esearch.fcgi", params=params)
            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            total = data.get("esearchresult", {}).get("count", "0")
            logger.info(f"PubMed搜索 '{disease}': 找到 {total} 篇，取前 {len(id_list)} 篇")
        except Exception as e:
            logger.error(f"PubMed搜索失败: {e}")
            return []

        if not id_list:
            return []

        # Step 2: 获取摘要详情
        return self._fetch_details(id_list)

    def _fetch_details(self, pmids: list[str]) -> list[dict]:
        """获取文献详情"""
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract",
            "email": self.email
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            resp = self.client.get(f"{EUTILS_BASE}/efetch.fcgi", params=params)
            # 简化处理：返回原始XML供后续解析
            return self._parse_xml_articles(resp.text, pmids)
        except Exception as e:
            logger.error(f"获取文献详情失败: {e}")
            return []

    def _parse_xml_articles(self, xml_text: str, pmids: list[str]) -> list[dict]:
        """解析PubMed XML，提取标题和摘要"""
        articles = []
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_text)

            for article in root.findall(".//PubmedArticle"):
                pmid_el = article.find(".//PMID")
                title_el = article.find(".//ArticleTitle")
                abstract_el = article.find(".//AbstractText")

                pmid = pmid_el.text if pmid_el is not None else ""
                title = "".join(title_el.itertext()) if title_el is not None else ""
                abstract = "".join(abstract_el.itertext()) if abstract_el is not None else ""

                # 提取年份
                year = 2024
                year_el = article.find(".//PubDate/Year")
                if year_el is not None:
                    year = int(year_el.text)

                articles.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract[:2000],  # 截断
                    "year": year
                })
        except Exception as e:
            logger.warning(f"XML解析失败: {e}")
            # fallback: 返回基本结构
            for pmid in pmids:
                articles.append({"pmid": pmid, "title": "", "abstract": "", "year": 2024})

        return articles

    def extract_genes_from_abstracts(
        self,
        articles: list[dict],
        llm_client: Optional[OpenAI] = None,
        model: str = "mimo-v2-pro"
    ) -> list[TargetEvidence]:
        """
        从文献摘要中提取关键基因/靶点
        使用LLM进行基因实体识别
        """
        if not articles:
            return []

        if llm_client is None:
            # 基于关键词的简单提取（无LLM时的fallback）
            return self._keyword_gene_extraction(articles)

        # 批量处理：每10篇一组
        all_genes: dict[str, list[dict]] = {}
        batch_size = 10

        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            batch_text = "\n\n".join([
                f"[PMID:{a['pmid']}] {a['title']}\n{a['abstract']}"
                for a in batch if a['abstract']
            ])

            if not batch_text.strip():
                continue

            try:
                response = llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是生物医学文献分析专家。从以下文献摘要中提取所有提到的基因/蛋白质靶点符号（如EGFR, TNF, VEGFA等），以及相关的疾病名称。以JSON格式返回：[{gene: 'SYMBOL', diseases: ['disease1'], relevance: 0-1}]"
                        },
                        {"role": "user", "content": batch_text}
                    ],
                    temperature=0.1
                )

                result_text = response.choices[0].message.content
                # 尝试解析JSON
                genes_data = self._parse_llm_json(result_text)

                for g in genes_data:
                    gene = g.get("gene", "").upper()
                    if gene:
                        if gene not in all_genes:
                            all_genes[gene] = []
                        all_genes[gene].append({
                            "diseases": g.get("diseases", []),
                            "relevance": g.get("relevance", 0.5)
                        })

            except Exception as e:
                logger.warning(f"LLM基因提取失败 (batch {i}): {e}")
                continue

            time.sleep(0.5)  # 限速

        # 汇总为TargetEvidence
        results = []
        for gene, evidence_list in all_genes.items():
            avg_rel = sum(e["relevance"] for e in evidence_list) / len(evidence_list)
            diseases = list(set(d for e in evidence_list for d in e["diseases"]))

            strength = "strong" if avg_rel > 0.7 and len(evidence_list) > 3 else \
                       "moderate" if avg_rel > 0.4 else "weak"

            results.append(TargetEvidence(
                gene_symbol=gene,
                total_papers=len(evidence_list),
                avg_relevance=round(avg_rel, 3),
                key_papers=[],  # 可后续关联
                disease_associations=diseases,
                evidence_strength=strength
            ))

        # 按相关性排序
        results.sort(key=lambda x: x.avg_relevance * x.total_papers, reverse=True)
        return results

    def _keyword_gene_extraction(self, articles: list[dict]) -> list[TargetEvidence]:
        """无LLM时的关键词基因提取（基于常见基因符号列表）"""
        import re
        # 常见基因符号模式：大写字母+数字
        gene_pattern = re.compile(r'\b([A-Z][A-Z0-9]{1,10})\b')
        # 过滤常见非基因大写词
        stopwords = {"DNA", "RNA", "PCR", "MRI", "CT", "FDA", "USA", "COVID", "SARS",
                     "HIV", "WHO", "THE", "AND", "FOR", "WITH", "FROM", "THIS", "THAT"}

        gene_counts: dict[str, int] = {}
        for article in articles:
            text = f"{article['title']} {article['abstract']}"
            genes = gene_pattern.findall(text)
            for g in genes:
                if g not in stopwords and len(g) > 2:
                    gene_counts[g] = gene_counts.get(g, 0) + 1

        results = []
        for gene, count in sorted(gene_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
            results.append(TargetEvidence(
                gene_symbol=gene,
                total_papers=count,
                avg_relevance=min(count / max(len(articles), 1), 1.0),
                key_papers=[],
                disease_associations=[],
                evidence_strength="moderate" if count > 5 else "weak"
            ))
        return results

    def _parse_llm_json(self, text: str) -> list[dict]:
        """从LLM响应中解析JSON"""
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(text)
        except json.JSONDecodeError:
            return []

    def full_mining_pipeline(
        self,
        disease: str,
        max_papers: int = 50,
        llm_client: Optional[OpenAI] = None
    ) -> list[dict]:
        """
        完整文献挖掘流水线
        疾病名 → PubMed搜索 → 基因提取 → 靶点证据
        """
        logger.info(f"开始文献挖掘: {disease}")
        articles = self.search_disease_genes(disease, max_results=max_papers)
        evidence_list = self.extract_genes_from_abstracts(articles, llm_client)

        return [asdict(e) for e in evidence_list]
