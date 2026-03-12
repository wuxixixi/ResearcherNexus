"""
数据分析代理 (Data Analyst Agent)

专门负责统计数据分析、数据可视化、图表生成和数据解读。
支持多种数据格式和统计方法。
"""

from typing import Dict, List, Optional, Any, TypedDict, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime
from io import StringIO
import base64

import pandas as pd
import numpy as np
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..graph.types import ResearchState
from ..tools.tool_executor import ToolExecutor
from ..utils.json_utils import repair_json_output


class DataFormat(Enum):
    """数据格式枚举"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    SQL = "sql"
    PARQUET = "parquet"
    RAW = "raw"


class AnalysisType(Enum):
    """分析类型枚举"""
    DESCRIPTIVE = "descriptive"          # 描述性统计
    CORRELATION = "correlation"          # 相关性分析
    REGRESSION = "regression"            # 回归分析
    TIME_SERIES = "time_series"          # 时间序列分析
    CLUSTERING = "clustering"            # 聚类分析
    HYPOTHESIS_TEST = "hypothesis_test"  # 假设检验


class ChartType(Enum):
    """图表类型枚举"""
    BAR = "bar"                    # 柱状图
    LINE = "line"                  # 折线图
    SCATTER = "scatter"            # 散点图
    PIE = "pie"                    # 饼图
    HISTOGRAM = "histogram"        # 直方图
    HEATMAP = "heatmap"            # 热力图
    BOX = "box"                    # 箱线图
    AREA = "area"                  # 面积图
    BUBBLE = "bubble"              # 气泡图


@dataclass
class Dataset:
    """数据集数据结构"""
    name: str
    data: pd.DataFrame
    format: DataFormat
    description: Optional[str] = None
    source: Optional[str] = None
    columns_info: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    analysis_type: AnalysisType
    description: str
    statistics: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Chart:
    """图表数据结构"""
    chart_type: ChartType
    title: str
    data: Dict[str, Any]
    config: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    base64_image: Optional[str] = None  # 生成的图片base64编码


@dataclass
class AnalysisReport:
    """完整的数据分析报告"""
    title: str
    description: str
    datasets: List[Dataset] = field(default_factory=list)
    analyses: List[AnalysisResult] = field(default_factory=list)
    charts: List[Chart] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class DataAnalystAgent:
    """
    数据分析代理

    核心职责：
    1. 数据加载和预处理（支持多种格式）
    2. 描述性统计分析（均值、方差、分布等）
    3. 推断性统计分析（假设检验、置信区间等）
    4. 相关性分析和回归分析
    5. 时间序列分析和预测
    6. 数据可视化（多种图表类型）
    7. 统计结果解读和洞察提取
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.tool_executor = ToolExecutor()
        self._data_cache: Dict[str, Dataset] = {}

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """You are an expert Data Analyst Agent specializing in statistical analysis and data visualization.

Your core capabilities include:
1. **Data Loading & Preprocessing**: Handle CSV, JSON, Excel, SQL, and other formats; clean and transform data
2. **Descriptive Statistics**: Calculate means, medians, modes, standard deviations, percentiles, distributions
3. **Inferential Statistics**: Perform hypothesis testing (t-tests, ANOVA, chi-square), confidence intervals
4. **Correlation & Regression**: Pearson/Spearman correlation, linear/multiple regression analysis
5. **Time Series Analysis**: Trend decomposition, seasonal analysis, forecasting
6. **Data Visualization**: Create bar charts, line graphs, scatter plots, heatmaps, box plots, histograms
7. **Insight Extraction**: Interpret statistical results in plain language, identify patterns and anomalies

When analyzing data:
- Always check data quality first (missing values, outliers, data types)
- Choose appropriate statistical methods based on data characteristics
- Visualize data distributions before applying statistical tests
- Report effect sizes, not just p-values
- Provide actionable insights, not just numbers
- Clearly state assumptions and limitations

Always provide structured output in the requested format."""

    def load_data(
        self,
        data_source: Union[str, pd.DataFrame, Dict],
        name: str = "dataset",
        format_type: Optional[DataFormat] = None,
        description: Optional[str] = None
    ) -> Dataset:
        """
        加载数据

        Args:
            data_source: 数据源（文件路径、DataFrame、字典等）
            name: 数据集名称
            format_type: 数据格式
            description: 数据描述

        Returns:
            Dataset 对象
        """
        try:
            # 根据数据源类型加载数据
            if isinstance(data_source, pd.DataFrame):
                df = data_source
                format_type = format_type or DataFormat.RAW
            elif isinstance(data_source, str):
                # 文件路径
                if data_source.endswith('.csv'):
                    df = pd.read_csv(data_source)
                    format_type = DataFormat.CSV
                elif data_source.endswith('.json'):
                    df = pd.read_json(data_source)
                    format_type = DataFormat.JSON
                elif data_source.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(data_source)
                    format_type = DataFormat.EXCEL
                else:
                    raise ValueError(f"Unsupported file format: {data_source}")
            elif isinstance(data_source, dict):
                df = pd.DataFrame(data_source)
                format_type = DataFormat.JSON
            else:
                raise ValueError(f"Unsupported data source type: {type(data_source)}")

            # 创建数据集对象
            dataset = Dataset(
                name=name,
                data=df,
                format=format_type,
                description=description or f"Dataset '{name}' with {len(df)} rows and {len(df.columns)} columns",
                columns_info={col: str(df[col].dtype) for col in df.columns}
            )

            # 缓存数据集
            self._data_cache[name] = dataset

            return dataset

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def analyze_descriptive_statistics(
        self,
        dataset: Dataset,
        columns: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        描述性统计分析

        Args:
            dataset: 数据集
            columns: 要分析的列（None表示所有数值列）

        Returns:
            AnalysisResult 对象
        """
        df = dataset.data

        # 选择数值列
        if columns:
            numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        else:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return AnalysisResult(
                analysis_type=AnalysisType.DESCRIPTIVE,
                description="No numeric columns found for analysis",
                statistics={},
                insights=["Dataset contains no numeric data for descriptive statistics"]
            )

        # 计算描述性统计
        stats = df[numeric_cols].describe()

        # 计算额外的统计量
        extended_stats = {}
        for col in numeric_cols:
            col_data = df[col].dropna()
            extended_stats[col] = {
                "count": int(col_data.count()),
                "mean": float(col_data.mean()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "25%": float(col_data.quantile(0.25)),
                "median": float(col_data.median()),
                "75%": float(col_data.quantile(0.75)),
                "max": float(col_data.max()),
                "skewness": float(col_data.skew()),
                "kurtosis": float(col_data.kurtosis()),
                "missing": int(df[col].isna().sum()),
                "missing_pct": float(df[col].isna().sum() / len(df) * 100)
            }

        # 生成洞察
        insights = []

        # 数据质量洞察
        for col in numeric_cols:
            missing_pct = extended_stats[col]["missing_pct"]
            if missing_pct > 20:
                insights.append(f"⚠️ Column '{col}' has {missing_pct:.1f}% missing values")
            elif missing_pct > 5:
                insights.append(f"ℹ️ Column '{col}' has {missing_pct:.1f}% missing values")

        # 分布特征洞察
        for col in numeric_cols:
            skew = extended_stats[col]["skewness"]
            if abs(skew) > 2:
                direction = "right" if skew > 0 else "left"
                insights.append(f"📊 Column '{col}' is highly skewed to the {direction} (skewness: {skew:.2f})")

        # 范围洞察
        for col in numeric_cols:
            stats = extended_stats[col]
            range_val = stats["max"] - stats["min"]
            if range_val > 0:
                cv = stats["std"] / stats["mean"] if stats["mean"] != 0 else 0
                if cv > 1:
                    insights.append(f"📈 Column '{col}' has high variability (CV: {cv:.2f})")

        return AnalysisResult(
            analysis_type=AnalysisType.DESCRIPTIVE,
            description=f"Descriptive statistics analysis for {len(numeric_cols)} numeric columns in dataset '{dataset.name}'",
            statistics={
                "columns_analyzed": numeric_cols,
                "total_rows": len(df),
                "extended_statistics": extended_stats
            },
            insights=insights,
            limitations=[
                "Analysis limited to numeric columns only",
                "Categorical variables not included in this analysis",
                "Missing values may affect statistical accuracy"
            ]
        )

    def generate_analysis_report(
        self,
        datasets: List[Dataset],
        analyses: List[AnalysisResult],
        title: str = "Data Analysis Report",
        description: str = ""
    ) -> AnalysisReport:
        """
        生成完整的数据分析报告

        Args:
            datasets: 数据集列表
            analyses: 分析结果列表
            title: 报告标题
            description: 报告描述

        Returns:
            AnalysisReport 对象
        """
        # 汇总关键发现
        key_findings = []
        for analysis in analyses:
            key_findings.extend(analysis.insights)

        # 生成结论（使用LLM）
        conclusions_prompt = f"""
Based on the following data analysis results, provide 3-5 key conclusions:

Analyses performed: {len(analyses)}
Key findings: {len(key_findings)}

Key insights from analyses:
"""
        for i, finding in enumerate(key_findings[:10], 1):
            conclusions_prompt += f"\n{i}. {finding}"

        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a data analysis expert. Provide concise, actionable conclusions."),
                HumanMessage(content=conclusions_prompt)
            ])

            conclusions_text = response.content
            # 解析结论（假设是列表形式）
            conclusions = [line.strip("- ").strip() for line in conclusions_text.split('\n') if line.strip().startswith('-') or line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]

            if not conclusions:
                conclusions = [conclusions_text[:200] + "..."]

        except Exception as e:
            print(f"Error generating conclusions: {e}")
            conclusions = ["Analysis completed successfully", "See detailed results in analysis sections"]

        # 生成建议
        recommendations = [
            "Consider exploring additional variables for deeper insights",
            "Validate findings with additional data sources if possible",
            "Document data quality issues for future reference"
        ]

        return AnalysisReport(
            title=title,
            description=description or f"Comprehensive data analysis report covering {len(datasets)} datasets and {len(analyses)} analyses",
            datasets=datasets,
            analyses=analyses,
            charts=[],  # 图表可以通过单独的方法生成
            key_findings=key_findings[:15],
            conclusions=conclusions,
            recommendations=recommendations
        )


# 便捷函数
def create_data_analyst_agent(llm: Optional[ChatOpenAI] = None) -> DataAnalystAgent:
    """创建数据分析代理的工厂函数"""
    return DataAnalystAgent(llm=llm)


async def data_analysis_node(state: ResearchState) -> ResearchState:
    """
    LangGraph 节点函数：数据分析处理

    在工作流中使用此节点进行数据分析
    """
    agent = create_data_analyst_agent()

    # 从state中获取数据集
    datasets_info = state.get("datasets", [])

    if not datasets_info:
        # 检查是否有数据在messages中
        messages = state.get("messages", [])
        for msg in reversed(messages):
            if hasattr(msg, 'additional_kwargs') and 'datasets' in msg.additional_kwargs:
                datasets_info = msg.additional_kwargs['datasets']
                break

    if not datasets_info:
        state["error"] = "No datasets found for analysis"
        return state

    # 加载数据集
    datasets = []
    for ds_info in datasets_info:
        try:
            dataset = agent.load_data(
                data_source=ds_info.get('source'),
                name=ds_info.get('name', 'dataset'),
                description=ds_info.get('description')
            )
            datasets.append(dataset)
        except Exception as e:
            print(f"Error loading dataset {ds_info.get('name')}: {e}")

    if not datasets:
        state["error"] = "Failed to load any datasets"
        return state

    # 执行分析
    analyses = []

    # 对每个数据集执行描述性统计
    for dataset in datasets:
        try:
            analysis = agent.analyze_descriptive_statistics(dataset)
            analyses.append(analysis)
        except Exception as e:
            print(f"Error analyzing dataset {dataset.name}: {e}")

    # 生成分析报告
    try:
        report = agent.generate_analysis_report(
            datasets=datasets,
            analyses=analyses,
            title=f"Data Analysis Report for {state.get('topic', 'Research')}",
            description=f"Automated analysis of {len(datasets)} datasets"
        )

        # 更新state
        state["data_analysis_report"] = {
            "title": report.title,
            "description": report.description,
            "total_datasets": len(report.datasets),
            "total_analyses": len(report.analyses),
            "key_findings": report.key_findings,
            "conclusions": report.conclusions,
            "recommendations": report.recommendations
        }

        # 添加分析摘要到消息
        analysis_summary = f"""
📊 **Data Analysis Complete**

**Report**: {report.title}

**Datasets Analyzed**: {len(report.datasets)}
**Analyses Performed**: {len(report.analyses)}

**Key Findings** ({len(report.key_findings)}):
"""
        for i, finding in enumerate(report.key_findings[:5], 1):
            analysis_summary += f"\n{i}. {finding[:200]}"

        analysis_summary += f"""

**Conclusions**:
"""
        for i, conclusion in enumerate(report.conclusions[:3], 1):
            analysis_summary += f"\n{i}. {conclusion[:150]}"

        state["messages"] = state.get("messages", []) + [AIMessage(content=analysis_summary)]

    except Exception as e:
        state["error"] = f"Data analysis report generation failed: {str(e)}"
        import traceback
        print(f"Data analysis error: {traceback.format_exc()}")

    return state


def should_do_data_analysis(state: ResearchState) -> bool:
    """
    判断是否应该进行数据分析

    根据研究类型和数据可用性决定是否需要进行数据分析
    """
    # 检查是否有数据集
    datasets = state.get("datasets", [])
    if datasets:
        return True

    # 检查messages中是否有数据
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, 'additional_kwargs') and 'datasets' in msg.additional_kwargs:
            return True
        # 检查内容中是否提到数据
        content = msg.content.lower() if hasattr(msg, 'content') else ""
        if any(kw in content for kw in ['dataset', 'data', 'csv', 'excel', '表格', '数据']):
            return True

    # 检查研究类型
    topic = state.get("topic", "").lower()
    if any(kw in topic for kw in ['data', 'statistics', 'analysis', 'survey', 'dataset', '数据', '统计', '分析']):
        return True

    # 检查是否明确请求数据分析
    if state.get("require_data_analysis", False):
        return True

    return False