from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from recruit_ai_demo.recruit_ai_mock import SAMPLE_PAYLOAD, analyze_candidate
    from recruit_ai_demo.workflow_state import (
        APPEAL_TYPES,
        HR_ACTIONS,
        build_audit_log,
        build_effect_metrics,
        create_appeal,
        mark_appeals_reviewed,
        record_hr_review,
    )
except ModuleNotFoundError:
    from recruit_ai_mock import SAMPLE_PAYLOAD, analyze_candidate
    from workflow_state import (
        APPEAL_TYPES,
        HR_ACTIONS,
        build_audit_log,
        build_effect_metrics,
        create_appeal,
        mark_appeals_reviewed,
        record_hr_review,
    )


st.set_page_config(
    page_title="候选人AI透明度与申诉看板",
    page_icon="🧭",
    layout="wide",
)


CSS = """
<style>
.stApp {
    background:
      radial-gradient(circle at 12% 10%, rgba(247, 180, 93, .28), transparent 28%),
      radial-gradient(circle at 90% 4%, rgba(50, 117, 127, .22), transparent 24%),
      linear-gradient(135deg, #fff8ed 0%, #edf4ef 48%, #f7efe1 100%);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
      "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
}
section.main > div.block-container {
    padding-top: 4.6rem !important;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 2.4rem !important;
}
h1, h2, h3 {
    font-family: "Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", serif;
}
.hero {
    border: 1px solid rgba(35, 56, 52, .16);
    border-radius: 28px;
    padding: 28px 30px;
    background: rgba(255, 252, 244, .82);
    box-shadow: 0 22px 70px rgba(39, 55, 50, .10);
}
.soft-card {
    border-radius: 22px;
    padding: 18px 20px;
    background: rgba(255, 255, 255, .72);
    border: 1px solid rgba(36, 56, 50, .12);
}
.redline {
    border-left: 5px solid #b04430;
    padding: 12px 16px;
    background: rgba(176, 68, 48, .08);
    border-radius: 14px;
}
</style>
"""


def init_state() -> None:
    if "payload" not in st.session_state:
        st.session_state.payload = SAMPLE_PAYLOAD.copy()
    if "result" not in st.session_state:
        st.session_state.result = analyze_candidate(st.session_state.payload)
    if "appeals" not in st.session_state:
        st.session_state.appeals = []
    if "hr_review" not in st.session_state:
        st.session_state.hr_review = None
    if "report_viewed" not in st.session_state:
        st.session_state.report_viewed = False


def run_analysis(payload: dict[str, str]) -> None:
    st.session_state.payload = payload
    st.session_state.result = analyze_candidate(payload)
    st.session_state.appeals = []
    st.session_state.hr_review = None
    st.session_state.report_viewed = False


def render_header() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
          <h1>候选人 AI 透明度与申诉看板</h1>
          <p>
            这个 Demo 回应“AI 提升招聘效率”与“学生担心黑箱、不公和错配”的冲突：
            AI 负责记录、解释和推荐范围，关键决策由 HR 与业务负责人共同确认。
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_panel() -> str:
    with st.sidebar:
        view = st.radio(
            "选择演示视角",
            ["候选人视角", "HR/业务负责人视角", "审计与效果评估视角"],
            index=0,
        )
        st.divider()
        st.header("演示输入")
        if st.button("载入推荐示例", use_container_width=True):
            run_analysis(SAMPLE_PAYLOAD.copy())

        with st.form("candidate_form"):
            candidate_name = st.text_input("候选人姓名", value=st.session_state.payload["candidate_name"])
            role_type = st.selectbox(
                "岗位类型",
                ["技术岗", "职能岗"],
                index=0 if st.session_state.payload["role_type"] == "技术岗" else 1,
            )
            target_roles = st.text_input("最多三个目标岗位", value=st.session_state.payload["target_roles"])
            resume = st.text_area("简历/项目经历", value=st.session_state.payload["resume"], height=120)
            assessment = st.text_area("AI测评/试岗记录", value=st.session_state.payload["assessment"], height=120)
            concerns = st.text_area("候选人担忧或申诉", value=st.session_state.payload["concerns"], height=90)
            resource_mode = st.selectbox(
                "试岗资源情况",
                ["试岗资源不足", "试岗资源充足"],
                index=0 if "不足" in st.session_state.payload["resource_mode"] else 1,
            )
            submitted = st.form_submit_button("生成透明评估", use_container_width=True)

        if submitted:
            run_analysis(
                {
                    "candidate_name": candidate_name,
                    "role_type": role_type,
                    "target_roles": target_roles,
                    "resume": resume,
                    "assessment": assessment,
                    "concerns": concerns,
                    "resource_mode": resource_mode,
                }
            )
        return view


def render_information_policy() -> None:
    st.subheader("系统使用 / 不使用的信息")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 系统会使用的信息")
        for item in [
            "候选人主动提交的简历/项目经历",
            "候选人填写的目标岗位",
            "AI 测评或试岗记录",
            "候选人补充说明",
            "与岗位胜任力有关的技能和经历证据",
        ]:
            st.markdown(f"- {item}")
    with col2:
        st.markdown("#### 系统不会使用的信息")
        for item in [
            "性别",
            "年龄",
            "外貌",
            "家庭背景",
            "地域刻板印象",
            "与岗位能力无关的学校标签",
            "其他与岗位胜任力无关的个人信息",
        ]:
            st.markdown(f"- {item}")


def render_candidate_dashboard(result: dict) -> None:
    st.session_state.report_viewed = True
    st.subheader("AI测评摘要")
    st.info(result["ai_summary"])

    col1, col2, col3 = st.columns(3)
    col1.metric("AI辅助等级", result["ai_assist_level"]["level"])
    col2.metric("推荐岗位数", len(result["recommended_roles"]))
    col3.metric("人工复核", "需要" if result["human_review_required"] else "常规确认")
    st.caption(result["ai_assist_level"]["policy"])

    st.subheader("推荐岗位范围")
    for role in result["recommended_roles"]:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 1, 3])
            c1.markdown(f"### {role['role']}")
            c2.metric("参考匹配度", role["reference_match"])
            c3.write(f"{role['evidence_sufficiency']}。{role['rationale']}")
            st.caption(role["process_status"])

    st.caption("参考匹配度表示当前材料与岗位要求的匹配程度，不代表能力高低，也不代表最终录用结果。")
    st.caption(result["evidence_sufficiency_notice"])

    st.subheader("AI分析逻辑说明")
    st.markdown(
        "<div class='redline'>AI 解释的是材料证据与岗位要求之间的关系，"
        "不评价候选人的人格、潜力上限或最终录用资格。</div>",
        unsafe_allow_html=True,
    )
    st.write("识别到的能力或证据：")
    for signal in result["recognized_signals"]:
        st.markdown(f"- {signal}")

    st.write("能力标签解释：")
    st.dataframe(result["capability_explanations"], use_container_width=True, hide_index=True)

    st.write("证据强弱说明：")
    st.dataframe(result["evidence_strength"], use_container_width=True, hide_index=True)

    st.write("AI记录的关键证据：")
    for evidence in result["evidence_log"]:
        st.markdown(f"- {evidence}")


def render_appeal(result: dict) -> None:
    st.subheader("不参与分析因素")
    excluded = result["excluded_factors"] or ["当前输入未识别到敏感因素"]
    st.warning("、".join(excluded))
    st.caption(result["excluded_factor_notice"])

    st.subheader("参考匹配度说明")
    st.markdown(f"<div class='redline'>{result['match_notice']}</div>", unsafe_allow_html=True)

    st.subheader("薪资沟通参考维度")
    st.info(result["salary_reference_notice"])

    st.subheader("申诉与补充说明")
    st.write(result["candidate_explanation"])
    for option in result["appeal_options"]:
        st.markdown(f"- {option}")

    with st.form("appeal_form"):
        appeal_type = st.selectbox("申诉类型", APPEAL_TYPES)
        appeal_text = st.text_area(
            "候选人补充说明",
            value="我希望优先考虑AI产品经理岗位，数据分析经历主要是为了支持产品决策。",
            height=100,
        )
        submitted = st.form_submit_button("提交申诉或补充说明")

    if submitted:
        appeal = create_appeal(appeal_type, appeal_text, existing_count=len(st.session_state.appeals))
        st.session_state.appeals.append(appeal)
        st.success("已保存申诉并进入 HR 人工复核队列。")

    if st.session_state.appeals:
        st.write("已提交记录：")
        st.dataframe(st.session_state.appeals, use_container_width=True, hide_index=True)
    else:
        st.caption("当前尚未提交申诉或补充说明。")


def render_brand(result: dict) -> None:
    st.subheader("雇主品牌承诺")
    for promise in result["employer_brand_promises"]:
        st.markdown(f"- {promise}")

    st.subheader("敏感因素排除说明")
    st.write("系统不会使用以下因素作为判断依据：")
    for item in ["性别", "年龄", "外貌", "家庭背景", "地域刻板印象", "与岗位能力无关的学校标签", "其他与岗位胜任力无关的个人信息"]:
        st.markdown(f"- {item}")
    st.caption("系统仅基于候选人主动提交的经历、技能、项目、岗位偏好和补充说明生成辅助建议。")

    st.subheader("及时沟通文案")
    st.success(result["comfort_message"])

    st.subheader("责任边界")
    st.markdown(f"<div class='redline'>{result['responsibility_boundary']}</div>", unsafe_allow_html=True)

    st.subheader("为什么方案A优先")
    st.write(
        "方案A直接解决学生对AI黑箱的恐惧：候选人能看到推荐范围、依据、排除因素和申诉入口。"
        "方案B保留为后台证据能力，帮助HR解释和复盘，但不把系统做成只服务HR效率的内部工具。"
    )


def render_review(result: dict) -> None:
    st.subheader("AI 建议摘要")
    st.info(result["ai_summary"])

    st.subheader("人工复核责任提示")
    st.markdown(
        "<div class='redline'>AI 仅提供辅助建议和证据整理，不自动决定 Offer、定岗或定薪。"
        "最终决策必须由 HR 与业务负责人共同确认。</div>",
        unsafe_allow_html=True,
    )

    st.subheader("HR/业务复盘证据")
    for reason in result["review_reasons"]:
        st.markdown(f"- {reason}")

    st.subheader("候选人申诉或补充说明")
    pending_count = sum(1 for appeal in st.session_state.appeals if appeal.get("status") == "待 HR 复核")
    st.metric("待复核申诉数量", pending_count)
    if st.session_state.appeals:
        st.dataframe(st.session_state.appeals, use_container_width=True, hide_index=True)
    else:
        st.info("暂无候选人补充说明")

    st.subheader("三个岗位并行流程")
    st.dataframe(result["parallel_processes"], use_container_width=True, hide_index=True)

    st.subheader("HR 人工终审动作")
    if pending_count:
        st.warning("本次复核将覆盖当前所有待复核申诉。")
    else:
        st.info("本次复核为常规人工确认。")

    with st.form("hr_review_form"):
        action = st.selectbox("最终处理动作", HR_ACTIONS)
        review_note = st.text_area(
            "HR 人工复核意见",
            value="建议进入人工面谈，重点确认岗位意愿、项目真实性和业务场景理解。",
            height=100,
        )
        confirmed = st.form_submit_button("确认人工复核结果")

    if confirmed:
        st.session_state.hr_review = record_hr_review(action, review_note, covered_appeal_count=pending_count)
        st.session_state.appeals = mark_appeals_reviewed(st.session_state.appeals)
        st.success("HR 人工复核结果已保存。")

    if st.session_state.hr_review:
        st.write("已保存复核结果：")
        st.json(st.session_state.hr_review)
    else:
        st.caption("当前状态：待 HR 复核")

    st.subheader("试岗或替代方案")
    st.write(f"**{result['trial_plan']['mode']}**")
    st.caption(result["trial_plan"]["reason"])

    st.subheader("AI使用红线")
    redlines = [
        "AI可以量化任务表现，但不能长期替代HR专业判断。",
        "参考匹配度不能作为唯一筛选标准。",
        "证据不足或存在争议时必须人工复核。",
        "关键决策由HR与业务负责人共同承担，AI只提供记录和建议。",
    ]
    for item in redlines:
        st.markdown(f"- {item}")


def render_audit_log(result: dict) -> None:
    st.subheader("审计日志事件时间线")
    st.write("该模块用于课堂展示系统可解释、可申诉、可复盘、可追责。")
    audit_log = build_audit_log(
        st.session_state.payload,
        result,
        st.session_state.appeals,
        st.session_state.hr_review,
        st.session_state.report_viewed,
    )
    st.dataframe(audit_log, use_container_width=True, hide_index=True)

    st.subheader("效果评估指标")
    metrics = build_effect_metrics(st.session_state.appeals, st.session_state.hr_review, st.session_state.report_viewed)
    cols = st.columns(4)
    for index, metric in enumerate(metrics):
        cols[index % 4].metric(metric["指标"], metric["状态"])

    st.subheader("申诉处理状态")
    if st.session_state.appeals:
        st.dataframe(st.session_state.appeals, use_container_width=True, hide_index=True)
    else:
        st.info("暂无候选人补充说明")

    st.subheader("HR 复核覆盖情况")
    if st.session_state.hr_review:
        st.json(st.session_state.hr_review)
    else:
        st.warning("待人工复核")


def render_candidate_view(result: dict) -> None:
    render_information_policy()
    st.divider()
    render_candidate_dashboard(result)
    st.divider()
    render_appeal(result)
    st.divider()
    render_brand(result)


def render_hr_business_view(result: dict) -> None:
    render_review(result)


def render_audit_evaluation_view(result: dict) -> None:
    render_audit_log(result)


def main() -> None:
    init_state()
    render_header()
    view = render_input_panel()

    result = st.session_state.result
    if view == "候选人视角":
        render_candidate_view(result)
    elif view == "HR/业务负责人视角":
        render_hr_business_view(result)
    else:
        render_audit_evaluation_view(result)

    st.divider()
    st.caption("学习和作业演示用途：本Demo不能直接用于真实招聘、录用、定岗、定薪或薪资谈判。")


if __name__ == "__main__":
    main()
