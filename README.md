# HireTrust AI：候选人透明度与申诉看板

HireTrust AI 是一个基于 Streamlit 的 AI 辅助招聘透明化 Demo，面向校园招聘中候选人担心 AI 黑箱、岗位错配、压薪和过度自动化决策的问题。

系统通过候选人透明看板、岗位参考匹配度解释、申诉补充机制、HR/业务人工复核和审计留痕，展示 AI 如何在不越权的前提下辅助招聘。

## 核心功能

- 候选人透明看板：展示岗位推荐范围、参考匹配度、材料证据和解释说明。
- 参考匹配度与证据充分度解释：说明数字只代表当前材料与岗位要求的匹配程度。
- 系统使用信息 / 不使用信息说明：明确敏感因素和无关个人信息不会参与判断。
- 候选人申诉与补充说明：候选人可提交申诉类型、补充说明和时间记录。
- HR/业务负责人终审：HR 可记录终审动作、人工意见和覆盖申诉数量。
- 审计日志与责任边界：用事件时间线展示完整流程，便于复盘。
- 效果评估面板：展示申诉数、待复核数、人工复核覆盖、解释报告查看状态等指标。
- AI 自动决策次数为 0：系统不做最终 Offer、定岗、定薪或淘汰决定。

## 技术栈

- Python
- Streamlit
- 本地 Mock AI 规则引擎
- pytest

当前 Demo 使用本地 Mock AI 模拟岗位匹配和解释生成，目的是保证课堂演示稳定、避免收集真实隐私；真实落地时可以替换为 LLM、RAG、企业 ATS 系统或招聘规则引擎。

## 本地运行方式

```bash
conda create -n hiretrust-ai python=3.10 -y
conda activate hiretrust-ai
pip install -r requirements.txt
streamlit run recruit_ai_demo/app.py
```

## Streamlit Community Cloud 部署方式

1. 登录 Streamlit Community Cloud。
2. 点击 `New app`。
3. 连接 GitHub 仓库。
4. 选择部署分支。
5. `Main file path` 填写：`recruit_ai_demo/app.py`。
6. 点击 `Deploy`。
7. 部署完成后获得在线 Demo 链接，可用于作业提交或课堂展示。

## 作业提交建议

建议提交：

- Streamlit 在线 Demo 链接。
- GitHub 仓库链接。
- `recruit_ai_demo/DESIGN.md` 设计文档。
- 如有需要，可附本地运行截图或录屏作为备用。

## Vibe coding 记录

- V1：生成基础 Streamlit Demo。
- V2：调整为候选人透明度与申诉看板。
- V3：增加申诉机制、敏感因素排除和雇主品牌承诺。
- V4：增加 HR 人工复核、审计日志和责任边界。
- V5：补充测试、README、requirements.txt，并检查高风险文案。
- V6：将证据判断表述改为证据充分度，升级审计日志为事件时间线，增加效果评估面板和角色视角。
- V7：整理 GitHub 与 Streamlit Cloud 部署版本。

## 风险边界说明

本 Demo 不进行真实招聘决策。  
本 Demo 不自动淘汰候选人。  
本 Demo 不自动决定 Offer。  
本 Demo 不自动定岗。  
本 Demo 不自动定薪。  
所有关键决策均需 HR 与业务负责人共同确认。
