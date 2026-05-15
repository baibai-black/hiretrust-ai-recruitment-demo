# 项目目录说明

这个仓库是 HireTrust AI 招聘透明度 Demo 的提交版本。评审或面试官如果只想快速了解项目，建议优先查看以下四个文件：

1. `recruit_ai_demo/DESIGN.md`：1000 字以内设计文档，是作业要求中的核心文字交付物。
2. `recruit_ai_demo/app.py`：Streamlit Demo 启动入口，是可运行产品原型。
3. `recruit_ai_demo/README.md`：项目介绍、运行方式、部署方式和提交说明。
4. `tests/test_recruit_ai_demo.py`：核心逻辑测试，证明申诉、HR 复核、审计留痕和风险文案检查可运行。

## 目录结构

```text
recruit_ai_demo/
  app.py
  recruit_ai_mock.py
  workflow_state.py
  DESIGN.md
  README.md
  DEPLOYMENT.md
  requirements.txt
  .streamlit/config.toml
tests/
  test_recruit_ai_demo.py
requirements.txt
.streamlit/config.toml
.gitignore
PACKAGE_CONTENTS.md
```

## 文件用途

`recruit_ai_demo/app.py` 是网页 Demo 的主程序。运行 `streamlit run recruit_ai_demo/app.py` 后，可以看到候选人视角、HR/业务负责人视角、审计与效果评估视角三个页面。

`recruit_ai_demo/recruit_ai_mock.py` 是本地 Mock AI 规则逻辑，用来模拟岗位参考匹配度、证据充分度、能力标签解释、敏感因素排除和薪资沟通参考维度。它不连接真实 API，也不处理真实简历。

`recruit_ai_demo/workflow_state.py` 保存产品闭环状态，包括候选人申诉、HR 人工复核记录、审计事件时间线和效果评估指标。

`recruit_ai_demo/DESIGN.md` 是最主要的设计文档，适合直接作为作业中的“1000 字以内设计文档”提交。

`recruit_ai_demo/README.md` 是 GitHub 首页式说明，适合让别人了解项目目标、核心功能、技术栈、本地运行、云端部署和风险边界。

`recruit_ai_demo/DEPLOYMENT.md` 是部署说明，主要用于 Streamlit Community Cloud 部署和常见问题排查。

`tests/test_recruit_ai_demo.py` 是当前 Demo 的核心测试文件，覆盖岗位推荐、参考匹配度、申诉保存、HR 复核、审计日志、效果评估和高风险表达检查。

`requirements.txt` 和 `recruit_ai_demo/requirements.txt` 都用于安装依赖。保留根目录版本是为了 GitHub 和 Streamlit Cloud 更容易识别。

`.streamlit/config.toml` 和 `recruit_ai_demo/.streamlit/config.toml` 是 Streamlit 页面配置。保留根目录版本是为了云端部署兼容，子目录版本是为了本地 Demo 目录完整。

`.gitignore` 用于避免上传缓存、虚拟环境、日志和敏感文件。

## 怎么提交

如果作业平台只允许提交少量内容，建议提交：

1. Streamlit 在线 Demo 链接。
2. GitHub 仓库链接。
3. `recruit_ai_demo/DESIGN.md`。
4. 如需备用材料，再提交 `delivery/recruit_ai_demo_package.zip`。

如果只看压缩包，优先打开 `recruit_ai_demo/DESIGN.md` 和 `recruit_ai_demo/README.md`，再按 README 中的命令启动 Demo。

## 注意

当前 Demo 不接真实招聘数据库，不接真实 API，不收集真实隐私，不做真实简历上传。系统只展示 AI 辅助建议、候选人申诉、HR/业务人工复核和审计留痕流程；所有关键决策都必须由 HR 与业务负责人共同确认。
