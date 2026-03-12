"""
文献综述代理 (Literature Reviewer Agent)

专门负责学术文献的检索、筛选、分析和综述撰写。
支持多种学术数据库的查询和综合分析。
"""

from typing import Dict, List, Optional, Any, TypedDict, Annotated
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from ..graph.types import ResearchState
from ..tools.search import tavily_search, duckduckgo_search, arxiv_search
from ..tools.web_scraper import jina_fetch, readability_fetch
from ..citations.collector import CitationCollector
from ..utils.json_utils import repair_json_output


class LiteratureType(Enum):
    """文献类型枚举"""
    RESEARCH_ARTICLE = "research_article"      # 研究论文
    REVIEW_ARTICLE = "review_article"          # 综述论文
    CONFERENCE_PAPER = "conference_paper"      # 会议论文
    PREPRINT = "preprint"                       # 预印本
    BOOK_CHAPTER = "book_chapter"              # 书籍章节
    THESIS = "thesis"                          # 学位论文
    REPORT = "report"                          # 技术报告


@dataclass
class LiteratureRecord:
    """文献记录数据结构"""
    title: str
    authors: List[str]
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    lit_type: LiteratureType = LiteratureType.RESEARCH_ARTICLE
    citation_count: Optional[int] = None
    relevance_score: float = 0.0
    full_text: Optional[str] = None


@dataclass
class LiteratureReview:
    """文献综述数据结构"""
    topic: str
    summary: str
    key_findings: List[str]
    research_gaps: List[str]
    future_directions: List[str]
    literature_records: List[LiteratureRecord] = field(default_factory=list)
    citations: List[Dict] = field(default_factory=list)


class LiteratureReviewerAgent:
    """
    文献综述代理

    核心职责：
    1. 学术文献检索（ArXiv、Google Scholar、PubMed 等）
    2. 文献筛选与相关性评估
    3. 文献元数据提取和结构化
    4. 自动撰写文献综述
    5. 研究空白识别和未来方向建议
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.citation_collector = CitationCollector()
        self.literature_cache: Dict[str, List[LiteratureRecord]] = {}

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """You are an expert Literature Reviewer Agent specializing in academic research analysis.

Your core capabilities include:
1. **Literature Search & Retrieval**: Query academic databases (ArXiv, Google Scholar, PubMed) to find relevant papers
2. **Relevance Assessment**: Evaluate paper relevance based on title, abstract, keywords, and citations
3. **Metadata Extraction**: Extract structured information (authors, year, venue, DOI, citation count)
4. **Literature Synthesis**: Identify common themes, methodologies, and findings across papers
5. **Gap Analysis**: Identify research gaps and suggest future research directions

When processing literature:
- Prioritize high-quality sources (peer-reviewed journals, top conferences)
- Consider citation count and publication venue prestige
- Extract key methodologies and findings systematically
- Identify contradictions or gaps in existing research
- Suggest how new research could address identified gaps

Always provide structured, well-organized output in the requested format."""

    def search_literature(
        self,
        query: str,
        search_type: str = "general",
        max_results: int = 20,
        year_range: Optional[tuple] = None
    ) -> List[LiteratureRecord]:
        """
        搜索学术文献

        Args:
            query: 搜索查询
            search_type: 搜索类型 (general/arxiv/pubmed)
            max_results: 最大结果数
            year_range: 年份范围 (start_year, end_year)

        Returns:
            文献记录列表
        """
        records = []

        # ArXiv 搜索
        if search_type in ["general", "arxiv"]:
            try:
                arxiv_results = arxiv_search(query, max_results=max_results//2)
                for result in arxiv_results:
                    record = self._parse_arxiv_result(result)
                    if record:
                        records.append(record)
            except Exception as e:
                print(f"ArXiv search error: {e}")

        # 通用搜索 (Tavily/DuckDuckGo)
        if search_type in ["general"]:
            try:
                search_results = tavily_search(query, max_results=max_results//2)
                for result in search_results:
                    record = self._parse_search_result(result)
                    if record and not self._is_duplicate(record, records):
                        records.append(record)
            except Exception as e:
                print(f"General search error: {e}")

        # 年份过滤
        if year_range:
            records = [
                r for r in records
                if r.year and year_range[0] <= r.year <= year_range[1]
            ]

        # 相关性排序
        records.sort(key=lambda x: x.relevance_score, reverse=True)

        # 缓存结果
        cache_key = f"{query}_{search_type}"
        self.literature_cache[cache_key] = records

        return records[:max_results]

    def _parse_arxiv_result(self, result: Dict) -> Optional[LiteratureRecord]:
        """解析ArXiv搜索结果"""
        try:
            return LiteratureRecord(
                title=result.get("title", ""),
                authors=result.get("authors", []),
                year=result.get("published", "").split("-")[0] if result.get("published") else None,
                abstract=result.get("summary", ""),
                doi=result.get("doi"),
                url=result.get("link", ""),
                keywords=result.get("categories", []),
                lit_type=LiteratureType.PREPRINT if "arxiv" in result.get("link", "") else LiteratureType.RESEARCH_ARTICLE,
                relevance_score=0.8  # ArXiv结果通常相关性较高
            )
        except Exception as e:
            print(f"Error parsing arxiv result: {e}")
            return None

    def _parse_search_result(self, result: Dict) -> Optional[LiteratureRecord]:
        """解析通用搜索结果"""
        try:
            return LiteratureRecord(
                title=result.get("title", ""),
                authors=[],  # 需要后续提取
                abstract=result.get("content", ""),
                url=result.get("url", ""),
                relevance_score=result.get("score", 0.5)
            )
        except Exception as e:
            print(f"Error parsing search result: {e}")
            return None

    def _is_duplicate(self, record: LiteratureRecord, existing_records: List[LiteratureRecord]) -> bool:
        """检查是否为重复文献"""
        for existing in existing_records:
            # 通过标题相似度判断
            if record.title and existing.title:
                if self._title_similarity(record.title, existing.title) > 0.8:
                    return True
            # 通过DOI判断
            if record.doi and existing.doi and record.doi == existing.doi:
                return True
        return False

    def _title_similarity(self, title1: str, title2: str) -> float:
        """计算标题相似度（简化版）"""
        # 转为小写并分词
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard相似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def analyze_literature(
        self,
        records: List[LiteratureRecord],
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        分析文献集合

        Args:
            records: 文献记录列表
            analysis_type: 分析类型 (comprehensive/trends/gaps/methods)

        Returns:
            分析结果字典
        """
        if not records:
            return {"error": "No literature records to analyze"}

        # 构建分析提示
        prompt = self._build_analysis_prompt(records, analysis_type)

        try:
            # 调用LLM进行分析
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)

            # 解析JSON响应
            content = repair_json_output(response.content)
            analysis = json.loads(content)

            return analysis

        except Exception as e:
            print(f"Error analyzing literature: {e}")
            return {
                "error": str(e),
                "summary": f"Failed to analyze {len(records)} literature records",
                "key_findings": [],
                "research_gaps": []
            }

    def _build_analysis_prompt(
        self,
        records: List[LiteratureRecord],
        analysis_type: str
    ) -> str:
        """构建分析提示词"""

        # 构建文献信息文本
        lit_texts = []
        for i, record in enumerate(records[:30], 1):  # 限制数量避免token超限
            authors_str = ", ".join(record.authors[:3]) if record.authors else "Unknown"
            if len(record.authors) > 3:
                authors_str += " et al."

            lit_text = f"""
[{i}] {record.title}
    Authors: {authors_str}
    Year: {record.year or "Unknown"}
    Venue: {record.venue or "Unknown"}
    Abstract: {record.abstract[:300] if record.abstract else "N/A"}...
"""
            lit_texts.append(lit_text)

        literature_context = "\n".join(lit_texts)

        # 根据分析类型构建提示
        analysis_focus = {
            "comprehensive": "comprehensive analysis covering all aspects",
            "trends": "research trends and evolution over time",
            "gaps": "research gaps and unexplored areas",
            "methods": "methodologies and research approaches"
        }.get(analysis_type, "comprehensive analysis")

        prompt = f"""Analyze the following collection of {len(records)} research papers and provide a {analysis_focus}.

## Literature Collection:

{literature_context}

## Analysis Requirements:

Please provide your analysis in the following JSON format:

{{
    "summary": "A comprehensive 300-500 word summary of the main themes, findings, and contributions across all papers",

    "key_findings": [
        "Key finding 1 with supporting evidence from specific papers",
        "Key finding 2 with supporting evidence from specific papers",
        "... (5-8 key findings)"
    ],

    "research_gaps": [
        "Identified gap 1: description and why it's important",
        "Identified gap 2: description and why it's important",
        "... (3-5 research gaps)"
    ],

    "future_directions": [
        "Suggested future research direction 1",
        "Suggested future research direction 2",
        "... (3-5 future directions)"
    ],

    "methodology_analysis": {{
        "common_methods": ["List of commonly used methodologies"],
        "emerging_methods": ["List of new or emerging approaches"],
        "methodological_criticisms": ["Identified limitations or criticisms of current methods"]
    }},

    "statistical_overview": {{
        "total_papers_analyzed": {len(records)},
        "year_range": "e.g., 2019-2024",
        "top_venues": ["List of most common publication venues"],
        "author_collaboration_patterns": "Description of collaboration trends"
    }}
}}

Ensure your analysis is:
- Evidence-based, citing specific papers from the collection
- Critical and objective, identifying both strengths and limitations
- Forward-looking, identifying meaningful research opportunities
- Well-structured and comprehensive"""

        return prompt

    def generate_literature_review(
        self,
        topic: str,
        max_papers: int = 50,
        year_range: Optional[tuple] = None
    ) -> LiteratureReview:
        """
        生成完整的文献综述

        Args:
            topic: 研究主题
            max_papers: 最大文献数量
            year_range: 年份范围

        Returns:
            LiteratureReview 对象
        """
        # 1. 搜索文献
        print(f"Searching literature for topic: {topic}")
        search_query = f"{topic} research paper academic"
        records = self.search_literature(
            query=search_query,
            max_results=max_papers,
            year_range=year_range
        )

        if not records:
            return LiteratureReview(
                topic=topic,
                summary=f"No literature found for topic: {topic}",
                key_findings=[],
                research_gaps=[],
                future_directions=[],
                literature_records=[]
            )

        print(f"Found {len(records)} relevant papers")

        # 2. 分析文献
        print("Analyzing literature collection...")
        analysis = self.analyze_literature(records, analysis_type="comprehensive")

        # 3. 构建文献综述对象
        review = LiteratureReview(
            topic=topic,
            summary=analysis.get("summary", ""),
            key_findings=analysis.get("key_findings", []),
            research_gaps=analysis.get("research_gaps", []),
            future_directions=analysis.get("future_directions", []),
            literature_records=records,
            citations=self._extract_citations(records)
        )

        print(f"Literature review generated successfully!")
        print(f"  - Total papers: {len(records)}")
        print(f"  - Key findings: {len(review.key_findings)}")
        print(f"  - Research gaps identified: {len(review.research_gaps)}")

        return review

    def _extract_citations(self, records: List[LiteratureRecord]) -> List[Dict]:
        """从文献记录中提取引用信息"""
        citations = []
        for i, record in enumerate(records, 1):
            citation = {
                "id": i,
                "title": record.title,
                "authors": record.authors,
                "year": record.year,
                "venue": record.venue,
                "doi": record.doi,
                "url": record.url,
                "type": record.lit_type.value
            }
            citations.append(citation)
        return citations


# 便捷函数
def create_literature_reviewer_agent(llm: Optional[ChatOpenAI] = None) -> LiteratureReviewerAgent:
    """创建文献综述代理的工厂函数"""
    return LiteratureReviewerAgent(llm=llm)


async def literature_review_node(state: ResearchState) -> ResearchState:
    """
    LangGraph 节点函数：文献综述处理

    在工作流中使用此节点进行文献综述生成
    """
    agent = create_literature_reviewer_agent()

    # 从state中获取研究主题
    topic = state.get("topic", "")
    if not topic:
        # 尝试从messages中提取主题
        messages = state.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                topic = msg.content
                break

    if not topic:
        state["error"] = "No research topic found for literature review"
        return state

    # 生成文献综述
    try:
        review = agent.generate_literature_review(
            topic=topic,
            max_papers=30,
            year_range=(2020, 2024)
        )

        # 更新state
        state["literature_review"] = {
            "topic": review.topic,
            "summary": review.summary,
            "key_findings": review.key_findings,
            "research_gaps": review.research_gaps,
            "future_directions": review.future_directions,
            "total_papers": len(review.literature_records),
            "citations": review.citations
        }

        # 添加文献综述到消息
        review_summary = f"""
📚 **Literature Review Complete**

**Topic**: {review.topic}

**Summary**: {review.summary[:500]}...

**Key Findings** ({len(review.key_findings)}):
"""
        for i, finding in enumerate(review.key_findings[:5], 1):
            review_summary += f"\n{i}. {finding[:200]}"

        review_summary += f"""

**Research Gaps Identified** ({len(review.research_gaps)}):
"""
        for i, gap in enumerate(review.research_gaps[:3], 1):
            review_summary += f"\n{i}. {gap[:150]}"

        state["messages"] = state.get("messages", []) + [AIMessage(content=review_summary)]

    except Exception as e:
        state["error"] = f"Literature review generation failed: {str(e)}"
        import traceback
        print(f"Literature review error: {traceback.format_exc()}")

    return state


def should_do_literature_review(state: ResearchState) -> bool:
    """
    判断是否应该进行文献综述

    根据研究类型和主题决定是否需要进行文献综述
    """
    topic = state.get("topic", "").lower()
    research_type = state.get("research_type", "general")

    # 学术类研究应该做文献综述
    academic_keywords = [
        "research", "study", "paper", "literature", "review",
        "学术", "研究", "论文", "文献", "综述",
        "survey", "meta-analysis", "systematic"
    ]

    if any(kw in topic for kw in academic_keywords):
        return True

    if research_type in ["academic", "literature_review", "thesis"]:
        return True

    # 检查state中是否明确请求文献综述
    if state.get("require_literature_review", False):
        return True

    return False