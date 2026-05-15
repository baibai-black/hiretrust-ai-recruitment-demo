"""Deterministic mock AI for a candidate-facing recruitment demo.

The logic is intentionally transparent and toy-scale. It is not suitable for
real hiring, compensation, or placement decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SENSITIVE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "性别": ("性别", "男", "女", "女生", "男生"),
    "年龄": ("年龄", "岁", "出生", "生日"),
    "婚育": ("婚育", "已婚", "未婚", "生育", "怀孕"),
    "民族": ("民族",),
    "户籍": ("户籍", "户口", "籍贯"),
    "外貌": ("外貌", "照片", "形象照", "证件照", "颜值"),
    "家庭背景": ("父母", "家庭背景", "家庭条件"),
    "地域刻板印象": ("地域", "老家", "省份刻板印象"),
    "与岗位能力无关的学校标签": ("学校标签", "学历歧视", "院校歧视"),
}

TECH_SIGNALS: dict[str, tuple[str, ...]] = {
    "数据分析": ("python", "sql", "数据", "指标", "建模", "可视化", "ab测试", "a/b"),
    "算法工程": ("算法", "机器学习", "深度学习", "模型", "推荐", "nlp", "cv"),
    "产品技术": ("产品", "需求", "原型", "用户", "实验", "增长", "数据"),
}

FUNCTION_SIGNALS: dict[str, tuple[str, ...]] = {
    "人力资源": ("招聘", "面试", "沟通", "组织", "员工", "培训", "hr"),
    "市场运营": ("运营", "内容", "活动", "品牌", "社群", "用户", "增长"),
    "销售管培": ("销售", "客户", "商务", "谈判", "渠道", "方案"),
}

DEFAULT_ROLES = ["AI产品经理", "数据分析师", "业务运营管培生"]


@dataclass(frozen=True)
class RoleResult:
    role: str
    reference_match: int | None
    evidence_sufficiency: str
    rationale: str
    process_status: str


SAMPLE_PAYLOAD: dict[str, Any] = {
    "candidate_name": "张同学",
    "role_type": "技术岗",
    "target_roles": "AI产品经理，数据分析师，算法产品实习生",
    "resume": "参与校园数据分析项目，使用 Python 和 SQL 做用户分层，也做过产品需求文档。",
    "assessment": "AI测评显示逻辑表达清晰，能解释项目指标，但对商业落地仍需人工面谈确认。",
    "concerns": "担心 AI 把我推到不适合的岗位，也担心参考匹配度影响最终 offer。",
    "resource_mode": "试岗资源不足",
}


def analyze_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a transparent, deterministic recommendation package."""

    candidate_name = str(payload.get("candidate_name") or "候选人").strip()
    role_type = str(payload.get("role_type") or "技术岗").strip()
    target_roles = _parse_roles(payload.get("target_roles"))
    resume = _clean_material(payload.get("resume"))
    assessment = _clean_material(payload.get("assessment"))
    concerns = _clean_material(payload.get("concerns"))
    resource_mode = str(payload.get("resource_mode") or "")

    full_text = " ".join([resume, assessment, concerns]).lower()
    excluded = _find_sensitive_factors(full_text)
    signals = _recognized_signals(full_text, role_type)
    recommendations = _recommend_roles(target_roles, signals, role_type)

    insufficient_evidence = any("证据不足" in item.evidence_sufficiency for item in recommendations)
    concern_review = bool(concerns.strip())
    unrelated_review = len(target_roles) > 1 and _looks_unrelated(target_roles)
    human_review_required = bool(excluded or insufficient_evidence or concern_review or unrelated_review)

    review_reasons: list[str] = []
    if excluded:
        review_reasons.append("输入中出现敏感信息，系统已排除并要求人工确认未参与判断。")
    if insufficient_evidence:
        review_reasons.append("材料证据不足，必须人工确认。")
    if concern_review:
        review_reasons.append("候选人表达了对AI结论的担忧，需要HR及时沟通。")
    if unrelated_review:
        review_reasons.append("三个目标岗位关联度较弱，需要HR协助候选人重新排序。")
    if not review_reasons:
        review_reasons.append("进入常规人工面谈确认，AI不做最终决策。")

    trial_plan = _trial_plan(resource_mode)
    ai_assist_level = _assist_level(role_type)

    return {
        "candidate_name": candidate_name,
        "role_type": role_type,
        "ai_assist_level": ai_assist_level,
        "ai_summary": _summary(candidate_name, role_type, signals, recommendations),
        "recommended_roles": [item.__dict__ for item in recommendations],
        "parallel_processes": _parallel_processes(target_roles, recommendations),
        "recognized_signals": signals,
        "excluded_factors": excluded,
        "excluded_factor_notice": "系统仅基于候选人主动提交的经历、技能、项目、岗位偏好和补充说明生成辅助建议；敏感因素只用于排除和复核提示，不进入参考匹配度。",
        "match_notice": "页面中的数字是参考匹配度，表示当前材料与岗位要求的匹配程度；不代表能力高低，不代表最终录用结果，也不作为Offer、定岗或定薪的唯一依据。",
        "salary_reference_notice": "本系统不生成最终薪资结论，仅提示可能影响薪资沟通的经历维度，例如岗位匹配度、项目经验、实习深度、岗位稀缺性等。最终薪资由HR与业务负责人结合面谈、岗位预算和公司制度确认。",
        "evidence_sufficiency_notice": "证据充分度只表示当前材料是否足以支持岗位建议，不代表能力高低、人格评价、潜力上限或最终录用资格。",
        "capability_explanations": _capability_explanations(full_text, role_type),
        "evidence_strength": _evidence_strength(resume, assessment, concerns),
        "human_review_required": human_review_required,
        "review_reasons": review_reasons,
        "candidate_explanation": _candidate_explanation(recommendations, human_review_required),
        "appeal_options": [
            "AI错误理解岗位意愿：补充被误读的经历或测评上下文。",
            "经历未体现：上传项目说明、作品集或导师/实习证明。",
            "岗位意愿不符：重新排序三个目标岗位并说明原因。",
        ],
        "comfort_message": "AI测评只是初步沟通和记录工具，不等于最终结论；后续仍由HR与业务负责人共同面谈确认。",
        "responsibility_boundary": "关键招聘决策由HR与业务负责人共同担责，AI只提供记录、建议、证据摘要和复盘材料。",
        "evidence_log": _evidence_log(resume, assessment, signals),
        "trial_plan": trial_plan,
        "employer_brand_promises": [
            "透明：候选人可看到AI依据、限制和申诉入口。",
            "公平：敏感因素不参与参考匹配度，证据不足或存在争议时必须人工复核。",
            "负责：争议面评由HR和业务共同复盘，不把责任推给AI。",
            "迭代：候选人反馈、HR复核结果和业务满意度进入系统优化。",
        ],
    }


def _parse_roles(raw_roles: Any) -> list[str]:
    if isinstance(raw_roles, list):
        roles = [str(role).strip() for role in raw_roles]
    else:
        normalized = str(raw_roles or "").replace("，", ",").replace("、", ",").replace("\n", ",")
        roles = [role.strip() for role in normalized.split(",")]
    roles = [role for role in roles if role and not _is_no_content_text(role)]
    return (roles or DEFAULT_ROLES)[:3]


def _clean_material(raw_text: Any) -> str:
    text = str(raw_text or "").strip()
    return "" if _is_no_content_text(text) else text


def _is_no_content_text(text: str) -> bool:
    normalized = text.strip().lower().replace("。", "").replace(".", "")
    no_content_values = {
        "",
        "无",
        "暂无",
        "没有",
        "无内容",
        "无相关经历",
        "没有相关经历",
        "无测评",
        "暂无测评",
        "无担忧",
        "没有担忧",
        "none",
        "no",
        "n/a",
        "na",
        "/",
        "-",
    }
    return normalized in no_content_values


def _find_sensitive_factors(text: str) -> list[str]:
    found: list[str] = []
    for label, keywords in SENSITIVE_KEYWORDS.items():
        if any(keyword.lower() in text for keyword in keywords):
            found.append(label)
    return found


def _recognized_signals(text: str, role_type: str) -> list[str]:
    signal_map = TECH_SIGNALS if "技术" in role_type else FUNCTION_SIGNALS
    signals: list[str] = []
    for label, keywords in signal_map.items():
        hits = [keyword for keyword in keywords if keyword.lower() in text]
        if hits:
            signals.append(f"{label}：识别到 {', '.join(hits[:3])}")
    if "沟通" in text or "表达" in text:
        signals.append("沟通表达：测评中出现沟通或表达能力证据")
    if not signals:
        signals.append("证据不足：当前材料需要人工补充确认")
    return signals


def _recommend_roles(target_roles: list[str], signals: list[str], role_type: str) -> list[RoleResult]:
    evidence_count = sum(1 for signal in signals if not signal.startswith("证据不足"))
    # Demo weights: technical-role materials are usually more structured, while
    # functional roles need more interview context. Later target roles are shown
    # as lower-priority options, not as lower candidate ability.
    base = 72 if "技术" in role_type else 64
    roles: list[RoleResult] = []
    for index, role in enumerate(target_roles[:3]):
        reference_match = None if evidence_count == 0 else max(45, min(92, base + evidence_count * 5 - index * 4))
        evidence_sufficiency = _evidence_sufficiency_label(reference_match)
        rationale = "与已识别材料证据较匹配" if "证据不足" not in evidence_sufficiency else "材料证据不足，必须人工确认"
        if "职能" in role_type:
            rationale += "；职能岗需重点看沟通、情境判断和面谈表现"
        status = "并行评估中" if index < 2 else "候选人可选择保留或降优先级"
        roles.append(RoleResult(role, reference_match, evidence_sufficiency, rationale, status))
    return roles


def _evidence_sufficiency_label(reference_match: int | None) -> str:
    if reference_match is None:
        return "证据不足，无法生成参考匹配度，必须人工确认"
    if reference_match >= 82:
        return "证据充分度：较充分"
    if reference_match >= 65:
        return "证据充分度：中等，需人工确认"
    return "证据不足，必须人工确认"


def _capability_explanations(text: str, role_type: str) -> list[dict[str, str]]:
    explanations = [
        {
            "能力标签": "数据分析能力",
            "解释": "根据数据、Python、SQL、指标或可视化经历判断材料与数据类岗位要求的关系。",
            "材料状态": "已出现相关证据" if any(token in text for token in ["python", "sql", "数据", "指标"]) else "待补充材料",
        },
        {
            "能力标签": "产品理解能力",
            "解释": "根据需求、用户、原型、增长或业务落地描述判断材料与产品类岗位要求的关系。",
            "材料状态": "已出现相关证据" if any(token in text for token in ["产品", "需求", "用户", "增长"]) else "待补充材料",
        },
        {
            "能力标签": "沟通表达能力",
            "解释": "根据测评记录、自我陈述和面谈材料整理沟通表达证据，仍需人工确认。",
            "材料状态": "已出现相关证据" if any(token in text for token in ["沟通", "表达", "解释"]) else "待面谈确认",
        },
        {
            "能力标签": "HR/组织协作能力",
            "解释": "根据招聘、组织、培训、协作等材料判断与职能岗位要求的关系。",
            "材料状态": "已出现相关证据" if "职能" in role_type or any(token in text for token in ["招聘", "组织", "培训", "协作"]) else "非当前主证据",
        },
    ]
    return explanations


def _evidence_strength(resume: str, assessment: str, concerns: str) -> list[dict[str, str]]:
    return [
        {
            "证据层级": "强证据",
            "说明": "项目经历、实习经历、试岗记录。",
            "当前状态": "已提供" if resume.strip() else "待补充",
        },
        {
            "证据层级": "中等证据",
            "说明": "测评描述、自我陈述。",
            "当前状态": "已提供" if assessment.strip() else "待补充",
        },
        {
            "证据层级": "待确认",
            "说明": "岗位意愿、商业落地能力、团队协作表现。",
            "当前状态": "需人工沟通" if concerns.strip() else "常规面谈确认",
        },
    ]


def _looks_unrelated(roles: list[str]) -> bool:
    joined = " ".join(roles)
    clusters = [
        ("数据", "算法", "AI", "产品"),
        ("HR", "人力", "招聘", "组织"),
        ("市场", "运营", "品牌", "内容"),
        ("销售", "商务", "客户"),
    ]
    matches = sum(any(token in joined for token in cluster) for cluster in clusters)
    return matches > 2


def _assist_level(role_type: str) -> dict[str, str]:
    if "技术" in role_type:
        return {
            "level": "较高",
            "policy": "AI可更多参与技能证据整理、项目关键词匹配和岗位范围推荐，但最终仍需人工确认。",
        }
    return {
        "level": "审慎",
        "policy": "职能岗涉及沟通、协作和情境判断，AI只做记录摘要，HR面谈权重更高。",
    }


def _summary(
    candidate_name: str,
    role_type: str,
    signals: list[str],
    recommendations: list[RoleResult],
) -> str:
    top_role = recommendations[0].role if recommendations else "待确认岗位"
    evidence_count = sum(1 for signal in signals if not signal.startswith("证据不足"))
    evidence_text = f"已识别{evidence_count}类有效材料证据" if evidence_count else "当前材料不足，暂不生成数字化参考匹配度"
    return (
        f"{candidate_name}当前进入{role_type}透明评估流程。"
        f"AI仅基于候选人材料和测评记录生成初步建议，优先推荐范围为{top_role}等相关岗位。"
        f"{evidence_text}，所有关键结论需HR与业务负责人共同复核。"
    )


def _candidate_explanation(recommendations: list[RoleResult], needs_review: bool) -> str:
    roles = "、".join(item.role for item in recommendations)
    review_text = "由于存在担忧、争议或材料证据不足，系统已标记人工复核。" if needs_review else "系统仍会进入常规人工确认。"
    return f"你不会被AI直接定岗或定薪。当前展示的是{roles}的推荐范围，{review_text}"


def _parallel_processes(target_roles: list[str], recommendations: list[RoleResult]) -> list[dict[str, str]]:
    processes: list[dict[str, str]] = []
    match_by_role = {item.role: item.reference_match for item in recommendations}
    for role in target_roles[:3]:
        reference_match = match_by_role.get(role)
        processes.append(
            {
                "role": role,
                "status": "候选人选择进入",
                "hr_visibility": "HR后台可见该流程状态，避免重复沟通和岗位冲突。",
                "reference_match": str(reference_match) if reference_match is not None else "待补充材料",
            }
        )
    return processes


def _trial_plan(resource_mode: str) -> dict[str, str]:
    if "不足" in resource_mode or "有限" in resource_mode:
        return {
            "mode": "短问答作业 + 一对一沟通",
            "reason": "试岗资源不足时，用标准化短问答降低成本，再通过一对一沟通补足人工判断。",
        }
    return {
        "mode": "轻量试岗 + HR/业务复盘",
        "reason": "资源允许时使用短周期任务观察真实协作表现，AI只记录证据和阶段性反馈。",
    }


def _evidence_log(resume: str, assessment: str, signals: list[str]) -> list[str]:
    snippets: list[str] = []
    if resume.strip():
        snippets.append(f"简历材料：{resume.strip()[:60]}")
    if assessment.strip():
        snippets.append(f"测评记录：{assessment.strip()[:60]}")
    snippets.extend(signals[:3])
    return snippets or ["暂无充分证据，需候选人补充材料并进入人工沟通。"]
