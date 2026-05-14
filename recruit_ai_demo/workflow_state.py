"""Small state helpers for the Streamlit recruitment demo."""

from __future__ import annotations

from datetime import datetime
from typing import Any


APPEAL_TYPES = [
    "AI 忽略项目经历",
    "AI 错误理解岗位意愿",
    "AI 对技能判断偏低",
    "希望转人工沟通",
    "其他",
]

HR_ACTIONS = [
    "维持 AI 推荐，但进入人工面谈",
    "调整推荐岗位",
    "要求候选人补充材料",
    "转业务负责人复核",
    "暂不采纳 AI 建议",
]


def create_appeal(
    appeal_type: str,
    candidate_note: str,
    submitted_at: str | None = None,
    existing_count: int = 0,
) -> dict[str, Any]:
    """Create a candidate appeal record suitable for session_state storage."""

    clean_type = appeal_type if appeal_type in APPEAL_TYPES else "其他"
    return {
        "appeal_id": f"APPEAL-{existing_count + 1:03d}",
        "appeal_type": clean_type,
        "candidate_note": candidate_note.strip(),
        "submitted_at": submitted_at or _now_text(),
        "status": "待 HR 复核",
    }


def record_hr_review(
    action: str,
    review_note: str,
    covered_appeal_count: int = 0,
    reviewed_at: str | None = None,
) -> dict[str, str]:
    """Create an HR review record."""

    clean_action = action if action in HR_ACTIONS else "转业务负责人复核"
    return {
        "action": clean_action,
        "review_note": review_note.strip(),
        "covered_appeal_count": covered_appeal_count,
        "reviewed_at": reviewed_at or _now_text(),
        "status": "已复核",
    }


def mark_appeals_reviewed(appeals: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return appeal records marked as reviewed without mutating the input."""

    return [{**appeal, "status": "已复核"} for appeal in appeals]


def build_audit_log(
    payload: dict[str, Any],
    result: dict[str, Any],
    appeals: list[dict[str, str]],
    hr_review: dict[str, str] | None,
    report_viewed: bool,
) -> list[dict[str, str]]:
    """Build an event timeline for classroom demonstration."""

    candidate_name = str(payload.get("candidate_name") or result.get("candidate_name") or "候选人")
    role_count = len(result.get("recommended_roles", []))
    events = [
        {
            "时间": "当前会话",
            "事件": "候选人提交基本信息",
            "当前状态": "已提交" if payload else "未提交",
            "留痕说明": f"{candidate_name}已提交岗位偏好、经历和测评材料。",
        },
        {
            "时间": "当前会话",
            "事件": "AI生成岗位匹配建议",
            "当前状态": "已生成" if role_count else "待生成",
            "留痕说明": f"系统生成{role_count}个岗位范围建议，使用参考匹配度表达。",
        },
        {
            "时间": "当前会话",
            "事件": "候选人查看解释性报告",
            "当前状态": "已查看" if report_viewed else "待查看",
            "留痕说明": "候选人可查看证据来源、敏感因素排除和责任边界。",
        },
    ]
    if appeals:
        for appeal in appeals:
            events.append(
                {
                    "时间": appeal.get("submitted_at", "未记录"),
                    "事件": f"{appeal.get('appeal_id', 'APPEAL-未知')} 候选人申诉",
                    "当前状态": appeal.get("status", "待 HR 复核"),
                    "留痕说明": (
                        f"{appeal.get('appeal_type', '其他')}："
                        f"{_short_text(appeal.get('candidate_note', ''))}"
                    ),
                }
            )
    else:
        events.append(
            {
                "时间": "未提交",
                "事件": "候选人提交申诉或补充说明",
                "当前状态": "未提交",
                "留痕说明": "暂无候选人补充说明",
            }
        )

    if hr_review:
        events.append(
            {
                "时间": hr_review.get("reviewed_at", "未记录"),
                "事件": "HR/业务负责人完成人工复核",
                "当前状态": hr_review.get("status", "已复核"),
                "留痕说明": (
                    f"{hr_review.get('action', '未记录动作')}；"
                    f"覆盖申诉数：{hr_review.get('covered_appeal_count', '0')}；"
                    f"意见：{_short_text(hr_review.get('review_note', ''))}"
                ),
            }
        )
    else:
        events.append(
            {
                "时间": "待处理",
                "事件": "HR/业务负责人完成人工复核",
                "当前状态": "待人工复核",
                "留痕说明": "HR与业务负责人尚未确认",
            }
        )

    return events


def build_effect_metrics(
    appeals: list[dict[str, str]],
    hr_review: dict[str, str] | None,
    report_viewed: bool,
) -> list[dict[str, str]]:
    """Build effect metrics for the audit and classroom evaluation panel."""

    pending_count = sum(1 for appeal in appeals if appeal.get("status") == "待 HR 复核")
    reviewed = hr_review is not None
    covered = reviewed and pending_count == 0
    return [
        {"指标": "AI 自动决策次数", "状态": "0"},
        {"指标": "当前候选人申诉数", "状态": str(len(appeals))},
        {"指标": "待复核申诉数", "状态": str(pending_count)},
        {"指标": "HR 复核状态", "状态": "已复核" if reviewed else "待复核"},
        {"指标": "人工复核覆盖", "状态": "已覆盖" if covered else "待覆盖"},
        {"指标": "候选人解释报告查看状态", "状态": "已查看" if report_viewed else "待查看"},
        {"指标": "敏感因素排除机制", "状态": "已启用"},
        {"指标": "薪资自动决策", "状态": "未启用"},
    ]


def _short_text(text: str, limit: int = 42) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped or "未填写"
    return f"{stripped[:limit]}..."


def _now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
