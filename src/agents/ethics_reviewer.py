"""
伦理审查代理 (Ethics Reviewer Agent)

专门负责研究伦理审查、数据隐私合规检查、研究可重复性验证。
支持多种伦理框架和合规标准。
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import re
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..graph.types import ResearchState
from ..utils.json_utils import repair_json_output


class RiskLevel(Enum):
    """风险等级枚举"""
    MINIMAL = "minimal"           # 最小风险
    LOW = "low"                   # 低风险
    MODERATE = "moderate"         # 中等风险
    HIGH = "high"                 # 高风险
    UNACCEPTABLE = "unacceptable"  # 不可接受的风险


class EthicalPrinciple(Enum):
    """伦理原则枚举"""
    RESPECT_FOR_PERSONS = "respect_for_persons"    # 尊重人格
    BENEFICENCE = "beneficence"                     # 有益性
    NON_MALEFICENCE = "non_maleficence"             # 不伤害
    JUSTICE = "justice"                             # 公正
    AUTONOMY = "autonomy"                           # 自主性
    PRIVACY = "privacy"                             # 隐私
    INFORMED_CONSENT = "informed_consent"           # 知情同意


class DataPrivacyRegulation(Enum):
    """数据隐私法规枚举"""
    GDPR = "GDPR"                    # 欧盟通用数据保护条例
    CCPA = "CCPA"                    # 加州消费者隐私法
    HIPAA = "HIPAA"                  # 美国健康保险可携性责任法
    PIPEDA = "PIPEDA"                # 加拿大个人信息保护法案
    LGPD = "LGPD"                    # 巴西通用数据保护法
    PDPA = "PDPA"                    # 新加坡个人数据保护法
    APPI = "APPI"                    # 日本个人信息保护法
    PIPL = "PIPL"                    # 中国个人信息保护法


class ReproducibilityStandard(Enum):
    """可重复性标准枚举"""
    T1 = "T1"  # 可重复 - 相同数据相同结果
    T2 = "T2"  # 可复制 - 新数据相同方法
    T3 = "T3"  # 可扩展 - 扩展方法新数据
    T4 = "T4"  # 可泛化 - 不同背景验证


@dataclass
class EthicalRisk:
    """伦理风险定义"""
    risk_id: str
    description: str
    category: str
    principle: EthicalPrinciple
    severity: RiskLevel
    likelihood: RiskLevel
    impact: str
    affected_stakeholders: List[str]
    mitigation_measures: List[str]
    residual_risk: RiskLevel


@dataclass
class InformedConsentCheck:
    """知情同意检查"""
    element: str
    required: bool
    present: bool
    quality: str  # good/fair/poor
    description: str
    recommendations: List[str]


@dataclass
class PrivacyComplianceCheck:
    """隐私合规检查"""
    regulation: DataPrivacyRegulation
    requirement: str
    compliant: bool
    evidence: str
    gaps: List[str]
    remediation: List[str]
    risk_level: RiskLevel


@dataclass
class ReproducibilityCheck:
    """可重复性检查"""
    standard: ReproducibilityStandard
    aspect: str
    status: str  # pass/partial/fail
    evidence: str
    recommendations: List[str]
    tools_needed: List[str]


@dataclass
class EthicsReviewReport:
    """伦理审查报告"""
    review_id: str
    project_title: str
    principal_investigator: str
    review_date: datetime
    review_type: str
    overall_risk_level: RiskLevel
    approval_status: str
    approval_conditions: List[str]
    approval_expiry: Optional[datetime]

    # 详细评估
    ethical_risks: List[EthicalRisk]
    informed_consent: List[InformedConsentCheck]
    privacy_compliance: List[PrivacyComplianceCheck]
    reproducibility: List[ReproducibilityCheck]

    # 利益相关者分析
    affected_populations: List[str]
    vulnerable_groups: List[str]
    benefit_sharing_plan: str

    # 审查建议
    modifications_required: List[str]
    monitoring_requirements: List[str]
    reporting_requirements: List[str]

    # 参考文件
    guidelines_referenced: List[str]
    regulations_cited: List[str]
    precedent_cases: List[str]


class EthicsReviewerAgent:
    """
    伦理审查代理

    核心职责：
    1. 研究伦理风险评估
    2. 知情同意过程审查
    3. 数据隐私合规检查（GDPR、HIPAA等）
    4. 研究可重复性验证
    5. 利益相关者分析
    6. 伦理审查报告生成
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.2)

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """You are an expert Ethics Reviewer Agent specializing in research ethics, data privacy, and research integrity.

Your core capabilities include:
1. **Ethical Risk Assessment**: Identify and evaluate ethical risks based on principles (Respect for Persons, Beneficence, Justice, Autonomy)
2. **Informed Consent Review**: Evaluate consent processes for adequacy, comprehension, voluntariness, and documentation
3. **Data Privacy Compliance**: Assess compliance with regulations (GDPR, HIPAA, CCPA, PIPL, etc.)
4. **Research Reproducibility**: Verify adherence to reproducibility standards (T1-T4) and open science practices
5. **Stakeholder Analysis**: Identify affected populations, vulnerable groups, and benefit-sharing implications
6. **Ethics Review Reporting**: Generate comprehensive ethics review reports with approval recommendations

When conducting ethics reviews:
- Prioritize protection of participants and vulnerable populations
- Balance scientific value with ethical obligations
- Apply appropriate ethical frameworks and regulations
- Consider cultural, social, and contextual factors
- Ensure transparency and accountability
- Document rationale for all decisions
- Identify conditions for approval and monitoring requirements

Always provide structured, well-organized output in the requested format."""

    def conduct_ethics_review(
        self,
        project_description: str,
        review_type: str = "full_review",
        regulations: Optional[List[DataPrivacyRegulation]] = None,
        context: Optional[Dict] = None
    ) -> EthicsReviewReport:
        """
        执行完整的伦理审查

        Args:
            project_description: 项目描述
            review_type: 审查类型
            regulations: 适用的法规列表
            context: 额外上下文信息

        Returns:
            EthicsReviewReport 对象
        """
        # 生成审查ID
        review_id = f"ER-{datetime.now().strftime('%Y%m%d')}-{hash(project_description) % 10000:04d}"

        # 构建审查提示词
        prompt = self._build_ethics_review_prompt(
            project_description=project_description,
            review_type=review_type,
            regulations=regulations,
            context=context
        )

        try:
            # 调用LLM执行审查
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)

            # 解析审查结果
            review_data = json.loads(repair_json_output(response.content))

            # 构建审查报告
            report = self._parse_ethics_review_report(review_id, review_data)

            return report

        except Exception as e:
            print(f"Error conducting ethics review: {e}")
            # 返回一个基本的审查报告
            return self._create_basic_ethics_review(review_id, project_description)

    def _build_ethics_review_prompt(
        self,
        project_description: str,
        review_type: str,
        regulations: Optional[List[DataPrivacyRegulation]],
        context: Optional[Dict]
    ) -> str:
        """构建伦理审查提示词"""

        prompt = f"""Conduct a comprehensive ethics review for the following research project:

## Project Description:
{project_description}

## Review Type: {review_type}
"""

        if regulations:
            prompt += f"\n## Applicable Regulations:\n"
            for reg in regulations:
                prompt += f"- {reg.value}\n"

        if context:
            prompt += f"\n## Additional Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"

        prompt += """

Please provide your ethics review in the following JSON format:

```json
{
    "project_title": "Project title",
    "principal_investigator": "PI name if known, otherwise 'TBD'",

    "overall_risk_assessment": {
        "risk_level": "minimal/low/moderate/high/unacceptable",
        "justification": "Explanation of risk assessment",
        "key_risk_factors": ["Factor 1", "Factor 2"]
    },

    "approval_recommendation": {
        "status": "approved/approved_with_conditions/major_modifications_required/rejected",
        "conditions": ["Condition 1", "Condition 2"],
        "expiry_months": 12
    },

    "ethical_risks": [
        {
            "risk_id": "R001",
            "description": "Risk description",
            "category": "Physical/Psychological/Privacy/Social",
            "principle": "Respect for Persons/Beneficence/Justice/Autonomy",
            "severity": "minimal/low/moderate/high",
            "likelihood": "low/moderate/high",
            "impact": "Who is affected and how",
            "affected_stakeholders": ["Stakeholder 1", "Stakeholder 2"],
            "mitigation_measures": ["Measure 1", "Measure 2"],
            "residual_risk": "minimal/low/moderate/high"
        }
    ],

    "informed_consent": {
        "adequacy_overall": "adequate/partial/inadequate",
        "checks": [
            {
                "element": "Information disclosure",
                "required": true,
                "present": true,
                "quality": "good/fair/poor",
                "description": "Assessment",
                "recommendations": ["Rec 1"]
            }
        ],
        "voluntariness_assessment": "Assessment of voluntariness",
        "comprehension_assessment": "Assessment of comprehension",
        "special_populations": ["Minors", "Prisoners", "Pregnant women"]
    },

    "privacy_compliance": {
        "regulations_checked": ["GDPR", "HIPAA", "CCPA"],
        "checks": [
            {
                "regulation": "GDPR",
                "requirement": "Lawful basis for processing",
                "compliant": true,
                "evidence": "Consent obtained",
                "gaps": ["Gap 1"],
                "remediation": ["Action 1"],
                "risk_level": "low"
            }
        ],
        "overall_compliance_status": "fully_compliant/partially_compliant/non_compliant",
        "data_minimization_assessment": "Assessment",
        "purpose_limitation_assessment": "Assessment",
        "storage_limitation_assessment": "Assessment",
        "security_measures_assessment": "Assessment"
    },

    "reproducibility": {
        "standards_assessed": ["T1", "T2", "T3"],
        "checks": [
            {
                "standard": "T1",
                "aspect": "Data availability",
                "status": "pass/partial/fail",
                "evidence": "Evidence description",
                "recommendations": ["Rec 1"],
                "tools_needed": ["Tool 1"]
            }
        ],
        "open_science_practices": {
            "preregistration": true/false,
            "open_data": true/false,
            "open_code": true/false,
            "open_materials": true/false
        },
        "documentation_quality": "adequate/partial/inadequate"
    },

    "stakeholders": {
        "affected_populations": ["Population 1", "Population 2"],
        "vulnerable_groups": ["Children", "Elderly", "Disabled"],
        "benefit_sharing_plan": "Description of benefit sharing",
        "community_engagement": "Description of community engagement",
        "diversity_considerations": "Considerations for diversity and inclusion"
    },

    "modifications_required": [
        {
            "item": "What needs to be modified",
            "priority": "critical/major/minor",
            "rationale": "Why this modification is needed",
            "guidance": "How to make the modification"
        }
    ],

    "monitoring_requirements": [
        "Requirement 1",
        "Requirement 2"
    ],

    "reporting_requirements": [
        "Requirement 1",
        "Requirement 2"
    ],

    "guidelines_referenced": [
        "Declaration of Helsinki",
        "Belmont Report",
        "CIOMS Guidelines"
    ],

    "regulations_cited": [
        "45 CFR 46",
        "21 CFR 56",
        "ICH-GCP"
    ],

    "precedent_cases": [
        "Case 1",
        "Case 2"
    ]
}
```

Provide a thorough, evidence-based review that prioritizes participant protection while supporting scientifically valuable research."""

        return prompt

    def _parse_ethics_review_report(self, review_id: str, review_data: Dict) -> EthicsReviewReport:
        """解析伦理审查报告"""

        # 解析日期
        try:
            expiry = datetime.now() + timedelta(days=365)
            if review_data.get("approval_recommendation", {}).get("expiry_months"):
                months = review_data["approval_recommendation"]["expiry_months"]
                expiry = datetime.now() + timedelta(days=30*months)
        except:
            expiry = None

        return EthicsReviewReport(
            review_id=review_id,
            project_title=review_data.get("project_title", ""),
            principal_investigator=review_data.get("principal_investigator", ""),
            review_date=datetime.now(),
            review_type="full_review",
            overall_risk_level=RiskLevel(review_data.get("overall_risk_assessment", {}).get("risk_level", "moderate")),
            approval_status=review_data.get("approval_recommendation", {}).get("status", "pending"),
            approval_conditions=review_data.get("approval_recommendation", {}).get("conditions", []),
            approval_expiry=expiry,

            ethical_risks=self._parse_ethical_risks(review_data.get("ethical_risks", [])),
            informed_consent=self._parse_informed_consent(review_data.get("informed_consent", {})),
            privacy_compliance=self._parse_privacy_compliance(review_data.get("privacy_compliance", {})),
            reproducibility=self._parse_reproducibility(review_data.get("reproducibility", {})),

            affected_populations=review_data.get("stakeholders", {}).get("affected_populations", []),
            vulnerable_groups=review_data.get("stakeholders", {}).get("vulnerable_groups", []),
            benefit_sharing_plan=review_data.get("stakeholders", {}).get("benefit_sharing_plan", ""),

            modifications_required=[m.get("item", "") for m in review_data.get("modifications_required", [])],
            monitoring_requirements=review_data.get("monitoring_requirements", []),
            reporting_requirements=review_data.get("reporting_requirements", []),
            guidelines_referenced=review_data.get("guidelines_referenced", []),
            regulations_cited=review_data.get("regulations_cited", []),
            precedent_cases=review_data.get("precedent_cases", [])
        )

    def _parse_ethical_risks(self, risks_data: List[Dict]) -> List[EthicalRisk]:
        """解析伦理风险"""
        risks = []
        for risk in risks_data:
            risks.append(EthicalRisk(
                risk_id=risk.get("risk_id", ""),
                description=risk.get("description", ""),
                category=risk.get("category", ""),
                principle=EthicalPrinciple(risk.get("principle", "respect_for_persons")),
                severity=RiskLevel(risk.get("severity", "moderate")),
                likelihood=RiskLevel(risk.get("likelihood", "moderate")),
                impact=risk.get("impact", ""),
                affected_stakeholders=risk.get("affected_stakeholders", []),
                mitigation_measures=risk.get("mitigation_measures", []),
                residual_risk=RiskLevel(risk.get("residual_risk", "low"))
            ))
        return risks

    def _parse_informed_consent(self, consent_data: Dict) -> List[InformedConsentCheck]:
        """解析知情同意"""
        checks = []
        for check in consent_data.get("checks", []):
            checks.append(InformedConsentCheck(
                element=check.get("element", ""),
                required=check.get("required", True),
                present=check.get("present", False),
                quality=check.get("quality", "poor"),
                description=check.get("description", ""),
                recommendations=check.get("recommendations", [])
            ))
        return checks

    def _parse_privacy_compliance(self, privacy_data: Dict) -> List[PrivacyComplianceCheck]:
        """解析隐私合规"""
        checks = []
        for check in privacy_data.get("checks", []):
            checks.append(PrivacyComplianceCheck(
                regulation=DataPrivacyRegulation(check.get("regulation", "GDPR")),
                requirement=check.get("requirement", ""),
                compliant=check.get("compliant", False),
                evidence=check.get("evidence", ""),
                gaps=check.get("gaps", []),
                remediation=check.get("remediation", []),
                risk_level=RiskLevel(check.get("risk_level", "moderate"))
            ))
        return checks

    def _parse_reproducibility(self, repro_data: Dict) -> List[ReproducibilityCheck]:
        """解析可重复性"""
        checks = []
        for check in repro_data.get("checks", []):
            checks.append(ReproducibilityCheck(
                standard=ReproducibilityStandard(check.get("standard", "T1")),
                aspect=check.get("aspect", ""),
                status=check.get("status", "fail"),
                evidence=check.get("evidence", ""),
                recommendations=check.get("recommendations", []),
                tools_needed=check.get("tools_needed", [])
            ))
        return checks

    def _create_basic_ethics_review(self, review_id: str, project_description: str) -> EthicsReviewReport:
        """创建基本伦理审查报告（出错时备用）"""
        return EthicsReviewReport(
            review_id=review_id,
            project_title="Project pending detailed review",
            principal_investigator="TBD",
            review_date=datetime.now(),
            review_type="initial_review",
            overall_risk_level=RiskLevel.MODERATE,
            approval_status="pending",
            approval_conditions=["Complete detailed ethics review"],
            approval_expiry=None,
            ethical_risks=[],
            informed_consent=[],
            privacy_compliance=[],
            reproducibility=[],
            affected_populations=[],
            vulnerable_groups=[],
            benefit_sharing_plan="",
            modifications_required=["Complete full ethics assessment"],
            monitoring_requirements=[],
            reporting_requirements=[],
            guidelines_referenced=[],
            regulations_cited=[],
            precedent_cases=[]
        )


def create_ethics_reviewer_agent(llm: Optional[ChatOpenAI] = None) -> EthicsReviewerAgent:
    """创建伦理审查代理的工厂函数"""
    return EthicsReviewerAgent(llm=llm)


async def ethics_review_node(state: ResearchState) -> ResearchState:
    """
    LangGraph 节点函数：伦理审查处理

    在工作流中使用此节点进行伦理审查
    """
    agent = create_ethics_reviewer_agent()

    # 从state中获取研究信息
    topic = state.get("topic", "")
    messages = state.get("messages", [])

    # 构建项目描述
    project_description = f"Research Topic: {topic}\n\n"

    # 添加相关消息作为上下文
    for msg in messages[-5:]:  # 最近5条消息
        if hasattr(msg, 'content'):
            content = msg.content[:500] if len(msg.content) > 500 else msg.content
            project_description += f"\n{content}\n"

    try:
        # 执行伦理审查
        report = agent.conduct_ethics_review(
            project_description=project_description,
            review_type="initial_review",
            regulations=[DataPrivacyRegulation.GDPR, DataPrivacyRegulation.CCPA]
        )

        # 更新state
        state["ethics_review"] = {
            "review_id": report.review_id,
            "project_title": report.project_title,
            "review_date": report.review_date.isoformat(),
            "overall_risk_level": report.overall_risk_level.value,
            "approval_status": report.approval_status,
            "approval_conditions": report.approval_conditions,
            "ethical_risks_count": len(report.ethical_risks),
            "modifications_required": report.modifications_required
        }

        # 添加伦理审查摘要到消息
        ethics_summary = f"""
⚖️ **Ethics Review Complete**

**Review ID**: {report.review_id}
**Status**: {report.approval_status.upper()}
**Overall Risk Level**: {report.overall_risk_level.value.upper()}

**Ethical Risks Identified**: {len(report.ethical_risks)}

**Modifications Required** ({len(report.modifications_required)}):
"""
        for i, mod in enumerate(report.modifications_required[:5], 1):
            ethics_summary += f"\n{i}. {mod[:150]}"

        if report.approval_conditions:
            ethics_summary += f"\n\n**Approval Conditions**:\n"
            for i, cond in enumerate(report.approval_conditions[:3], 1):
                ethics_summary += f"\n{i}. {cond}"

        state["messages"] = state.get("messages", []) + [AIMessage(content=ethics_summary)]

    except Exception as e:
        state["error"] = f"Ethics review failed: {str(e)}"
        import traceback
        print(f"Ethics review error: {traceback.format_exc()}")

    return state


def should_do_ethics_review(state: ResearchState) -> bool:
    """
    判断是否应该进行伦理审查

    根据研究类型和潜在风险决定是否需要进行伦理审查
    """
    topic = state.get("topic", "").lower()
    research_type = state.get("research_type", "general")

    # 涉及人类参与者的研究
    human_subjects_keywords = [
        "human", "participant", "subject", "patient", "clinical", "trial",
        "survey", "interview", "questionnaire", "people", "user",
        "人类", "参与者", "受试者", "患者", "临床", "试验",
        "调查", "访谈", "问卷", "用户"
    ]

    if any(kw in topic for kw in human_subjects_keywords):
        return True

    # 涉及敏感数据的研究
    sensitive_data_keywords = [
        "personal data", "health data", "medical record", "genetic",
        "biometric", "location data", "financial", "privacy",
        "个人数据", "健康数据", "医疗记录", "基因", "生物识别"
    ]

    if any(kw in topic for kw in sensitive_data_keywords):
        return True

    # 涉及弱势群体的研究
    vulnerable_groups_keywords = [
        "children", "minor", "elderly", "pregnant", "prisoner",
        "disability", "cognitive impairment", "vulnerable",
        "儿童", "未成年人", "老年人", "孕妇", "囚犯", "残疾"
    ]

    if any(kw in topic for kw in vulnerable_groups_keywords):
        return True

    # 检查是否明确请求伦理审查
    if state.get("require_ethics_review", False):
        return True

    return False