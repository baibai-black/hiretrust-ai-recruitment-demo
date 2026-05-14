from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from recruit_ai_demo.recruit_ai_mock import analyze_candidate
from recruit_ai_demo.workflow_state import build_audit_log, build_effect_metrics, create_appeal, record_hr_review


def test_technical_role_limits_to_three_processes_and_keeps_human_decision() -> None:
    result = analyze_candidate(
        {
            "candidate_name": "李同学",
            "role_type": "技术岗",
            "target_roles": "AI产品经理, 数据分析师, 算法产品实习生, 运营",
            "resume": "Python SQL 数据分析 项目 产品需求",
            "assessment": "表达清晰",
            "concerns": "",
            "resource_mode": "试岗资源充足",
        }
    )

    assert result["ai_assist_level"]["level"] == "较高"
    assert len(result["recommended_roles"]) == 3
    assert len(result["parallel_processes"]) == 3
    assert "reference_match" in result["recommended_roles"][0]
    assert "evidence_sufficiency" in result["recommended_roles"][0]
    assert "参考匹配度" in result["match_notice"]
    assert "不代表最终录用结果" in result["match_notice"]
    assert "不作为Offer、定岗或定薪的唯一依据" in result["match_notice"]


def test_functional_role_requires_more_hr_intervention() -> None:
    result = analyze_candidate(
        {
            "role_type": "职能岗",
            "target_roles": "人力资源, 市场运营",
            "resume": "组织过社群活动，负责沟通、招聘协助和培训记录",
            "assessment": "候选人表达稳定",
            "concerns": "",
        }
    )

    assert result["ai_assist_level"]["level"] == "审慎"
    assert "HR面谈权重更高" in result["ai_assist_level"]["policy"]


def test_sensitive_information_is_excluded_from_scoring() -> None:
    result = analyze_candidate(
        {
            "role_type": "技术岗",
            "target_roles": "数据分析师",
            "resume": "女生，23岁，Python SQL 数据项目，附照片",
            "assessment": "",
            "concerns": "",
        }
    )

    assert "性别" in result["excluded_factors"]
    assert "年龄" in result["excluded_factors"]
    assert "外貌" in result["excluded_factors"]
    assert result["human_review_required"] is True
    assert "不进入参考匹配度" in result["excluded_factor_notice"]


def test_candidate_concern_triggers_human_review() -> None:
    result = analyze_candidate(
        {
            "role_type": "技术岗",
            "target_roles": "数据分析师",
            "resume": "Python SQL 数据项目",
            "assessment": "",
            "concerns": "担心AI误判我的岗位意愿",
        }
    )

    assert result["human_review_required"] is True
    assert any("候选人表达了对AI结论的担忧" in reason for reason in result["review_reasons"])
    assert "不会被AI直接定岗或定薪" in result["candidate_explanation"]


def test_trial_resource_shortage_uses_short_answer_and_one_to_one() -> None:
    result = analyze_candidate(
        {
            "role_type": "职能岗",
            "target_roles": "市场运营",
            "resume": "品牌 活动 沟通",
            "assessment": "",
            "resource_mode": "试岗资源不足",
        }
    )

    assert result["trial_plan"]["mode"] == "短问答作业 + 一对一沟通"


def test_design_doc_is_under_1000_chinese_assignment_chars() -> None:
    text = Path("recruit_ai_demo/DESIGN.md").read_text(encoding="utf-8")
    non_space_chars = "".join(text.split())

    assert len(non_space_chars) <= 1000
    assert "候选人透明度与申诉看板" in text
    assert "AI只给出岗位范围、参考匹配度和复盘证据" in text


def test_appeal_has_id_and_can_be_saved_to_audit_log() -> None:
    appeal = create_appeal(
        "AI 错误理解岗位意愿",
        "我更希望进入AI产品经理流程。",
        "2026-05-14 10:00:00",
        existing_count=1,
    )
    result = analyze_candidate({"target_roles": "AI产品经理", "resume": "Python 产品 数据"})

    audit_log = build_audit_log(
        {"candidate_name": "王同学"},
        result,
        [appeal],
        None,
        report_viewed=True,
    )

    assert appeal["status"] == "待 HR 复核"
    assert appeal["appeal_id"] == "APPEAL-002"
    assert any(row["事件"].startswith("APPEAL-002") and "AI产品经理" in row["留痕说明"] for row in audit_log)
    assert any(row["当前状态"] == "待人工复核" for row in audit_log)


def test_hr_review_action_can_be_recorded() -> None:
    review = record_hr_review(
        "转业务负责人复核",
        "请业务负责人确认岗位意愿与项目深度。",
        covered_appeal_count=2,
        reviewed_at="2026-05-14 10:30:00",
    )

    assert review["action"] == "转业务负责人复核"
    assert review["status"] == "已复核"
    assert review["covered_appeal_count"] == 2
    assert "业务负责人" in review["review_note"]


def test_multiple_appeals_all_appear_in_audit_timeline() -> None:
    appeals = [
        create_appeal("AI 忽略项目经历", "补充第一个项目。", "2026-05-14 10:00:00", existing_count=0),
        create_appeal("希望转人工沟通", "希望与HR一对一沟通。", "2026-05-14 10:05:00", existing_count=1),
    ]
    result = analyze_candidate({"target_roles": "AI产品经理", "resume": "Python 产品 数据"})

    audit_log = build_audit_log({"candidate_name": "王同学"}, result, appeals, None, report_viewed=True)
    event_text = "\n".join(row["事件"] + row["留痕说明"] for row in audit_log)

    assert "APPEAL-001" in event_text
    assert "APPEAL-002" in event_text
    assert "补充第一个项目" in event_text
    assert "一对一沟通" in event_text


def test_effect_metrics_reflect_current_session_state() -> None:
    appeals = [
        create_appeal("AI 忽略项目经历", "补充项目。", existing_count=0),
        {**create_appeal("希望转人工沟通", "希望人工沟通。", existing_count=1), "status": "已复核"},
    ]
    metrics = build_effect_metrics(appeals, None, report_viewed=True)
    metric_map = {item["指标"]: item["状态"] for item in metrics}

    assert metric_map["AI 自动决策次数"] == "0"
    assert metric_map["当前候选人申诉数"] == "2"
    assert metric_map["待复核申诉数"] == "1"
    assert metric_map["HR 复核状态"] == "待复核"
    assert metric_map["敏感因素排除机制"] == "已启用"
    assert metric_map["薪资自动决策"] == "未启用"


def test_high_risk_phrases_do_not_appear_in_page_or_docs() -> None:
    checked_files = [
        Path("recruit_ai_demo/app.py"),
        Path("recruit_ai_demo/recruit_ai_mock.py"),
        Path("recruit_ai_demo/DESIGN.md"),
        Path("recruit_ai_demo/README.md"),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    risky_phrases = [
        "AI " + "自动淘汰",
        "AI" + "自动淘汰",
        "AI " + "自动定薪",
        "AI" + "自动定薪",
        "AI " + "决定录用",
        "AI" + "决定录用",
        "录用" + "概率",
        "能力" + "排名",
        "置" + "信度",
        "confi" + "dence",
    ]
    for phrase in risky_phrases:
        assert phrase not in combined


def test_streamlit_runtime_config_reduces_reconnect_loops() -> None:
    config_paths = [
        Path(".streamlit/config.toml"),
        Path("recruit_ai_demo/.streamlit/config.toml"),
    ]

    for path in config_paths:
        content = path.read_text(encoding="utf-8")
        assert 'fileWatcherType = "none"' in content
        assert "runOnSave = false" in content
        assert "enableWebsocketCompression = false" in content

    app_text = Path("recruit_ai_demo/app.py").read_text(encoding="utf-8")
    assert "fonts.googleapis.com" not in app_text
