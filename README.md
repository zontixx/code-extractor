# 图片提取代码

把代码截图 / 照片里的代码，一键提取成可直接复制的文本，并对被遮挡、缺失的部分**单独**给出补全（不会覆盖原始代码）。

## 功能

- 原样提取图片中的代码（保留缩进、符号、注释）
- 对遮挡 / 模糊 / 缺失的代码单独给出补全，明确标注「AI 推测」
- 一键复制
- 深色代码展示，清晰区分「原始代码」与「补全代码」

## 技术栈

- Python + Flask
- DeepSeek 视觉模型（`deepseek-flash`）

## 本地运行

1. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv venv
   # Windows PowerShell 激活：
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. 在项目根目录创建 `.env` 文件，填入你的 DeepSeek 密钥：
   ```
   ANTHROPIC_AUTH_TOKEN=你的DeepSeek密钥
   ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
   ```

3. 运行：
   - Windows 双击 `启动.bat`（会自动打开浏览器）
   - 或命令行 `python app.py`，然后访问 http://127.0.0.1:5000

## 支持的图片格式

jpg / png / gif / webp（iPhone 的 heic 格式请先转成 jpg）
