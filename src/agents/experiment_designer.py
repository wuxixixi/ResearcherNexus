"""
实验设计代理 (Experiment Designer Agent)

专门负责研究实验的设计、样本量计算、变量管理和实验流程优化。
支持多种实验类型：A/B测试、对照实验、随机试验等。
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import math
from datetime import datetime, timedelta

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..graph.types import ResearchState
from ..utils.json_utils import repair_json_output


class ExperimentType(Enum):
    """实验类型枚举"""
    AB_TEST = "ab_test"                    # A/B测试
    RANDOMIZED_CONTROLLED = "rct"          # 随机对照试验
    QUASI_EXPERIMENTAL = "quasi"           # 准实验
    FACTORIAL = "factorial"                # 析因设计
    CROSSOVER = "crossover"                # 交叉设计
    REPEATED_MEASURES = "repeated"         # 重复测量
    OBSERVATIONAL = "observational"        # 观察性研究


class VariableType(Enum):
    """变量类型枚举"""
    INDEPENDENT = "independent"          # 自变量
    DEPENDENT = "dependent"              # 因变量
    CONTROL = "control"                  # 控制变量
    CONFOUNDING = "confounding"          # 混杂变量
    MODERATOR = "moderator"              # 调节变量
    MEDIATOR = "mediator"                # 中介变量


class HypothesisType(Enum):
    """假设类型枚举"""
    NULL = "null"                        # 零假设
    ALTERNATIVE = "alternative"          # 备择假设
    ONE_TAILED = "one_tailed"            # 单侧检验
    TWO_TAILED = "two_tailed"            # 双侧检验


@dataclass
class Variable:
    """变量定义"""
    name: str
    var_type: VariableType
    data_type: str                      # numeric, categorical, ordinal, etc.
    description: str
    levels: Optional[List[str]] = None  # 对于分类变量
    range: Optional[Tuple[float, float]] = None  # 对于数值变量
    measurement_scale: str = "interval"  # nominal, ordinal, interval, ratio


@dataclass
class Hypothesis:
    """假设定义"""
    null_hypothesis: str
    alternative_hypothesis: str
    hypothesis_type: HypothesisType
    variables: List[str]                # 涉及的变量
    expected_relationship: str          # 预期关系描述
    test_statistic: Optional[str] = None
    significance_level: float = 0.05


@dataclass
class SampleSizeCalculation:
    """样本量计算结果"""
    total_sample_size: int
    per_group_size: Optional[int] = None
    number_of_groups: int = 2
    effect_size: float = 0.0
    alpha: float = 0.05
    power: float = 0.80
    drop_out_rate: float = 0.20
    adjusted_sample_size: int = 0
    calculation_method: str = ""
    assumptions: List[str] = field(default_factory=list)


@dataclass
class ExperimentalCondition:
    """实验条件/处理组定义"""
    name: str
    description: str
    condition_type: str               # treatment, control, placebo, etc.
    variables_settings: Dict[str, Any] = field(default_factory=dict)
    sample_size: int = 0
    outcome_measures: List[str] = field(default_factory=list)


@dataclass
class ExperimentSchedule:
    """实验时间安排"""
    total_duration: timedelta
    phases: List[Dict[str, Any]]        # baseline, intervention, follow-up, etc.
    measurement_timepoints: List[datetime]
    milestones: Dict[str, datetime]


@dataclass
class ExperimentDesign:
    """完整的实验设计方案"""
    title: str
    description: str
    experiment_type: ExperimentType
    objective: str
    background: str
    variables: List[Variable]
    hypotheses: List[Hypothesis]
    sample_size: SampleSizeCalculation
    conditions: List[ExperimentalCondition]
    schedule: ExperimentSchedule
    randomization_method: str
    blinding: str
    ethical_considerations: List[str]
    data_collection_methods: List[str]
    statistical_analysis_plan: str
    expected_outcomes: List[str]
    limitations: List[str]
    pilot_study_recommendations: Optional[str] = None


class ExperimentDesignerAgent:
    """
    实验设计代理

    核心职责：
    1. 实验方案设计（A/B测试、对照实验、随机试验等）
    2. 样本量计算（功效分析、效应量估计）
    3. 变量管理（自变量、因变量、控制变量、混杂变量）
    4. 实验流程优化（随机化、盲法、分组策略）
    5. 统计分析方法规划
    6. 伦理考量和风险评估
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.3)

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """You are an expert Experiment Designer Agent specializing in research methodology and experimental design.

Your core capabilities include:
1. **Experimental Design**: Design rigorous experiments (A/B tests, RCTs, quasi-experiments, factorial designs)
2. **Sample Size Calculation**: Power analysis, effect size estimation, attrition adjustments
3. **Variable Management**: Identify and operationalize IVs, DVs, control variables, confounders, moderators, mediators
4. **Randomization Strategies**: Simple, stratified, cluster, block randomization
5. **Blinding Procedures**: Single-blind, double-blind, triple-blind designs
6. **Statistical Analysis Planning**: Appropriate tests, multiple comparison corrections, interim analyses
7. **Ethical Considerations**: Risk assessment, informed consent, data privacy, equitable selection

When designing experiments:
- Prioritize internal validity while balancing external validity
- Anticipate and plan for confounding variables
- Use appropriate randomization and control procedures
- Calculate adequate sample sizes for statistical power
- Plan for missing data and attrition
- Consider practical constraints (cost, time, feasibility)
- Ensure ethical standards are met
- Pre-register hypotheses and analysis plans when possible

Always provide structured, well-organized output in the requested format."""

    def calculate_sample_size(
        self,
        test_type: str = "two_sample",
        effect_size: Optional[float] = None,
        alpha: float = 0.05,
        power: float = 0.80,
        ratio: float = 1.0,
        drop_out_rate: float = 0.20,
        **kwargs
    ) -> SampleSizeCalculation:
        """
        计算样本量

        Args:
            test_type: 检验类型 (two_sample/paired/one_sample/anova/chi_square)
            effect_size: 效应量（Cohen's d等），None时自动估计
            alpha: 显著性水平
            power: 统计功效
            ratio: 组间样本比例
            drop_out_rate: 预期脱落率
            **kwargs: 其他参数

        Returns:
            SampleSizeCalculation 对象
        """

        # 如果没有提供效应量，使用默认估计
        if effect_size is None:
            effect_size = 0.5  # 中等效应量

        # 计算样本量（使用不同的公式）
        if test_type == "two_sample":
            # 两独立样本t检验
            z_alpha = 1.96 if alpha == 0.05 else 2.576  # 近似值
            z_beta = 0.84 if power == 0.80 else 1.28   # 近似值

            n_per_group = ((z_alpha + z_beta) ** 2 * 2 * (effect_size ** 2)) / (effect_size ** 2)
            n_per_group = int(np.ceil(n_per_group / 2))  # 调整公式

            # 使用更简单的近似公式
            n_per_group = int(np.ceil(16 / (effect_size ** 2)))

            total_n = int(n_per_group * 2)

        elif test_type == "paired":
            # 配对t检验
            n_per_group = int(np.ceil(8 / (effect_size ** 2)))
            total_n = n_per_group

        elif test_type == "one_sample":
            # 单样本t检验
            n_per_group = int(np.ceil(16 / (effect_size ** 2)))
            total_n = n_per_group

        elif test_type == "anova":
            # 方差分析
            groups = kwargs.get("groups", 3)
            n_per_group = int(np.ceil(16 / (effect_size ** 2)))
            total_n = n_per_group * groups

        else:
            # 默认使用两样本检验
            n_per_group = int(np.ceil(16 / (effect_size ** 2)))
            total_n = n_per_group * 2

        # 考虑脱落率调整
        adjusted_n = int(np.ceil(total_n / (1 - drop_out_rate)))

        # 确定分组情况
        if test_type in ["two_sample", "paired"]:
            number_of_groups = 2
            per_group = adjusted_n // 2
        elif test_type == "anova":
            number_of_groups = kwargs.get("groups", 3)
            per_group = adjusted_n // number_of_groups
        else:
            number_of_groups = 1
            per_group = adjusted_n

        calculation_method = {
            "two_sample": "Two-sample t-test formula (Cohen, 1988)",
            "paired": "Paired t-test formula",
            "one_sample": "One-sample t-test formula",
            "anova": "ANOVA F-test formula",
            "chi_square": "Chi-square test formula"
        }.get(test_type, "Standard power analysis formula")

        return SampleSizeCalculation(
            total_sample_size=adjusted_n,
            per_group_size=per_group,
            number_of_groups=number_of_groups,
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            drop_out_rate=drop_out_rate,
            adjusted_sample_size=adjusted_n,
            calculation_method=calculation_method,
            assumptions=[
                f"Significance level (α) = {alpha}",
                f"Statistical power (1-β) = {power}",
                f"Effect size (Cohen's d) = {effect_size}",
                f"Expected drop-out rate = {drop_out_rate * 100}%",
                "Normally distributed data (for t-tests/ANOVA)",
                "Independent observations (unless paired design)"
            ]
        )

    def design_experiment(
        self,
        research_question: str,
        experiment_type: ExperimentType = ExperimentType.RANDOMIZED_CONTROLLED,
        variables: Optional[List[Dict]] = None,
        hypotheses: Optional[List[str]] = None,
        constraints: Optional[Dict] = None
    ) -> ExperimentDesign:
        """
        设计完整的实验方案

        Args:
            research_question: 研究问题
            experiment_type: 实验类型
            variables: 变量定义列表
            hypotheses: 假设列表
            constraints: 约束条件

        Returns:
            ExperimentDesign 对象
        """
        # 构建提示词
        prompt = self._build_design_prompt(
            research_question=research_question,
            experiment_type=experiment_type,
            variables=variables,
            hypotheses=hypotheses,
            constraints=constraints
        )

        try:
            # 调用LLM生成实验设计
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)

            # 解析响应
            design_data = json.loads(repair_json_output(response.content))

            # 构建ExperimentDesign对象
            experiment_design = self._parse_experiment_design(design_data)

            return experiment_design

        except Exception as e:
            print(f"Error designing experiment: {e}")
            # 返回一个基本的实验设计
            return self._create_basic_design(research_question, experiment_type)

    def _build_design_prompt(
        self,
        research_question: str,
        experiment_type: ExperimentType,
        variables: Optional[List[Dict]],
        hypotheses: Optional[List[str]],
        constraints: Optional[Dict]
    ) -> str:
        """构建实验设计提示词"""

        prompt = f"""Design a comprehensive experiment for the following research:

**Research Question**: {research_question}

**Experiment Type**: {experiment_type.value}
"""

        if variables:
            prompt += "\n**Variables**:\n"
            for var in variables:
                prompt += f"- {var.get('name')} ({var.get('type')}): {var.get('description', '')}\n"

        if hypotheses:
            prompt += "\n**Hypotheses**:\n"
            for i, hyp in enumerate(hypotheses, 1):
                prompt += f"{i}. {hyp}\n"

        if constraints:
            prompt += "\n**Constraints**:\n"
            for key, value in constraints.items():
                prompt += f"- {key}: {value}\n"

        prompt += """

Please provide a complete experimental design in JSON format with the following structure:

```json
{
    "title": "Experiment title",
    "description": "Detailed description of the experiment",
    "objective": "Primary objective",
    "background": "Background and rationale",

    "design_type": "Type of experimental design",
    "design_description": "Detailed design description",

    "variables": [
        {
            "name": "Variable name",
            "type": "independent/dependent/control/confounding",
            "data_type": "numeric/categorical/ordinal",
            "description": "Variable description",
            "levels": ["level1", "level2"],
            "measurement_method": "How to measure"
        }
    ],

    "hypotheses": [
        {
            "null_hypothesis": "H0 statement",
            "alternative_hypothesis": "H1 statement",
            "type": "one_tailed/two_tailed",
            "variables": ["var1", "var2"],
            "expected_relationship": "description"
        }
    ],

    "sample_size": {
        "total_sample_size": 100,
        "per_group_size": 50,
        "number_of_groups": 2,
        "effect_size": 0.5,
        "alpha": 0.05,
        "power": 0.80,
        "drop_out_rate": 0.20,
        "adjusted_sample_size": 125,
        "calculation_method": "Method used",
        "assumptions": ["Assumption 1", "Assumption 2"]
    },

    "conditions": [
        {
            "name": "Condition name",
            "description": "Description",
            "condition_type": "treatment/control/placebo",
            "variables_settings": {"var1": "value1"},
            "sample_size": 50,
            "outcome_measures": ["measure1", "measure2"]
        }
    ],

    "schedule": {
        "total_duration_days": 90,
        "phases": [
            {
                "name": "Phase name",
                "duration_days": 30,
                "start_day": 0,
                "end_day": 30,
                "activities": ["Activity 1", "Activity 2"]
            }
        ],
        "measurement_timepoints": ["Baseline", "Week 2", "Week 4", "Post-test"],
        "milestones": {
            "milestone1": "Date",
            "milestone2": "Date"
        }
    },

    "randomization_method": "Simple/Stratified/Cluster/Block randomization",
    "blinding": "Open-label/Single-blind/Double-blind/Triple-blind",

    "ethical_considerations": [
        "Consideration 1",
        "Consideration 2"
    ],

    "data_collection_methods": [
        "Method 1",
        "Method 2"
    ],

    "statistical_analysis_plan": "Detailed statistical analysis plan",

    "expected_outcomes": [
        "Outcome 1",
        "Outcome 2"
    ],

    "limitations": [
        "Limitation 1",
        "Limitation 2"
    ],

    "pilot_study_recommendations": "Pilot study recommendations"
}
```

Please ensure the design is:
- Scientifically rigorous
- Ethically sound
- Practically feasible
- Statistically appropriate
- Well-documented"""

        return prompt