# 部署说明

## 1. 本地运行

从当前仓库根目录运行：

```bash
conda create -n hiretrust-ai python=3.10 -y
conda activate hiretrust-ai
pip install -r requirements.txt
streamlit run recruit_ai_demo/app.py
```

如果只使用 `recruit_ai_demo/` 目录作为独立仓库：

```bash
conda create -n hiretrust-ai python=3.10 -y
conda activate hiretrust-ai
pip install -r requirements.txt
streamlit run app.py
```

## 2. 上传 GitHub

上传源码和文档，不上传缓存、虚拟环境、压缩包、`.env` 或任何真实候选人信息。

建议保留：

- `recruit_ai_demo/app.py`
- `recruit_ai_demo/recruit_ai_mock.py`
- `recruit_ai_demo/workflow_state.py`
- `recruit_ai_demo/DESIGN.md`
- `recruit_ai_demo/README.md`
- `recruit_ai_demo/requirements.txt`
- `requirements.txt`
- `tests/test_recruit_ai_demo.py`

## 3. Streamlit Cloud 部署

如果上传当前仓库结构：

- App URL source：GitHub 仓库
- Branch：你的提交分支
- Main file path：`recruit_ai_demo/app.py`

如果只把 `recruit_ai_demo/` 作为仓库根目录：

- Main file path：`app.py`

## 4. 常见问题排查

- `ModuleNotFoundError`：检查 `requirements.txt` 是否已上传，确认 `Main file path` 与目录结构一致。
- Streamlit Cloud 找不到 `app.py`：当前仓库结构应填写 `recruit_ai_demo/app.py`，独立 Demo 仓库才填写 `app.py`。
- 页面打开但状态丢失：这是 `session_state` 的临时会话状态，刷新后会重置。
- 本地能跑但云端不能跑：检查是否使用了绝对路径、本地 conda 路径、未上传文件或真实密钥。
