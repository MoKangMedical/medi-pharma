"""
RAG文献检索模块
基于PubMed的增强检索生成
"""

import logging
from typing import Optional

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class RAGSearchEngine:
    """RAG增强文献搜索引擎"""

    def __init__(
        self,
        llm_client: Optional[OpenAI] = None,
        llm_model: str = "mimo-v2-pro",
        email: str = "medipharma@example.com"
    ):
        self.llm = llm_client
        self.model = llm_model
        self.email = email
        self.client = httpx.Client(timeout=30.0)

    def search_and_summarize(
        self,
        query: str,
        max_results: int = 20
    ) -> str:
        """搜索文献并生成摘要"""
        # 搜索PubMed
        articles = self._pubmed_search(query, max_results)

        if not articles:
            return f"未找到与'{query}'相关的文献。"

        if self.llm:
            return self._llm_summarize(query, articles)
        else:
            return self._simple_summarize(articles)

    def _pubmed_search(self, query: str, max_results: int) -> list[dict]:
        """PubMed搜索"""
        try:
            # 搜索
            resp = self.client.get(
                f"{EUTILS_BASE}/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "sort": "relevance",
                    "email": self.email
                }
            )
            ids = resp.json().get("esearchresult", {}).get("idlist", [])

            if not ids:
                return []

            # 获取摘要
            resp2 = self.client.get(
                f"{EUTILS_BASE}/efetch.fcgi",
                params={
                    "db": "pubmed",
                    "id": ",".join(ids[:max_results]),
                    "retmode": "xml",
                    "rettype": "abstract",
                    "email": self.email
                }
            )

            return self._parse_articles(resp2.text, ids)

        except Exception as e:
            logger.error(f"PubMed搜索失败: {e}")
            return []

    def _parse_articles(self, xml_text: str, pmids: list[str]) -> list[dict]:
        """解析PubMed XML"""
        articles = []
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_text)

            for article in root.findall(".//PubmedArticle"):
                pmid_el = article.find(".//PMID")
                title_el = article.find(".//ArticleTitle")
                abstract_el = article.find(".//AbstractText")
                year_el = article.find(".//PubDate/Year")

                articles.append({
                    "pmid": pmid_el.text if pmid_el is not None else "",
                    "title": "".join(title_el.itertext()) if title_el is not None else "",
                    "abstract": "".join(abstract_el.itertext())[:1500] if abstract_el is not None else "",
                    "year": int(year_el.text) if year_el is not None else 2024,
                })
        except Exception as e:
            logger.warning(f"XML解析失败: {e}")

        return articles

    def _llm_summarize(self, query: str, articles: list[dict]) -> str:
        """使用LLM生成文献综述"""
        context = "\n\n".join([
            f"[{a['pmid']}] ({a['year']}) {a['title']}\n{a['abstract']}"
            for a in articles if a.get("abstract")
        ][:15])

        try:
            resp = self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是生物医学文献综述专家。根据以下PubMed文献摘要，撰写一份结构化的文献综述，包括：研究背景、关键发现、技术趋势、研究空白。控制在500字以内。"
                    },
                    {
                        "role": "user",
                        "content": f"检索主题: {query}\n\n文献摘要:\n{context}"
                    }
                ],
                temperature=0.3
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"LLM综述生成失败: {e}")
            return self._simple_summarize(articles)

    def _simple_summarize(self, articles: list[dict]) -> str:
        """简单摘要（无LLM）"""
        years = [a.get("year", 2024) for a in articles]
        return (f"共检索到{len(articles)}篇相关文献 "
                f"({min(years)}-{max(years)})。"
                f"Top文献包括：" +
                "；".join([a["title"][:50] for a in articles[:3]]))
