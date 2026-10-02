import base64
import mimetypes
import os
import threading
import webbrowser

import anthropic
from flask import Flask, render_template, request

app = Flask(__name__)


def load_env():
    """读取项目根目录下的 .env 文件，把配置读进环境变量"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env()

client = anthropic.Anthropic()  # 自动从 .env 读取 key 和地址

MODEL = "deepseek-flash"  # 能看图的模型

ALLOWED_MIME = {"image/jpeg", "image/png", "image/gif", "image/webp"}

PROMPT = """你是一个代码提取助手。下面的图片里是一段代码（可能是手机拍摄或电脑截图，部分内容可能被遮挡、模糊或拍不全）。

请严格按下面三个部分输出，每个部分用一行固定的分隔符开头，不要输出任何多余的内容：

=====原始代码=====
把图片中能清楚看到的代码原样提取出来，保留缩进、符号、注释。如果某处看不清，就在那个位置写 <此处模糊>，绝对不要自己编造。

=====补全说明=====
用一两句话说明哪些地方被遮挡、模糊或缺失，以及你补全的依据是什么。

=====补全代码=====
给出补全后的完整代码。在每一处补全或修改的位置，用注释标注 # 补全: 简要说明。如果原始代码已经完整，这一节只写「无需补全」四个字。

记住：补全只是推测，可能与原作者意图不符。"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("code_image")
        if file is None or file.filename == "":
            return render_template("index.html", error="请先选择一张图片")

        filename = file.filename.lower()
        mime, _ = mimetypes.guess_type(filename)
        if mime not in ALLOWED_MIME:
            return render_template(
                "index.html",
                error="不支持的格式，请上传 jpg/png/gif/webp 的图片。"
                "（iPhone 的 heic 格式请先转成 jpg）",
            )

        image_b64 = base64.b64encode(file.read()).decode("utf-8")

        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime,
                                    "data": image_b64,
                                },
                            },
                        ],
                    }
                ],
            )
            reply = get_text(message)
        except Exception as e:
            return render_template("index.html", error=f"调用失败：{e}")

        extracted, note, completed = split_reply(reply)

        return render_template(
            "result.html",
            filename=filename,
            extracted=extracted,
            note=note,
            completed=completed,
        )

    return render_template("index.html", error=None)


def get_text(message):
    """从模型返回里取出所有文字块（跳过思考块）"""
    parts = [b.text for b in message.content if getattr(b, "type", "") == "text"]
    return "\n".join(parts)


def split_reply(text):
    """把模型的回复按三个分隔符拆开"""
    extracted, note, completed = "", "", ""
    current = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("=====原始代码====="):
            current = "extracted"
            continue
        if s.startswith("=====补全说明====="):
            current = "note"
            continue
        if s.startswith("=====补全代码====="):
            current = "completed"
            continue
        if current == "extracted":
            extracted += line + "\n"
        elif current == "note":
            note += line + "\n"
        elif current == "completed":
            completed += line + "\n"
    return extracted.strip(), note.strip(), completed.strip()


if __name__ == "__main__":
    # 启动后等 1 秒，让服务器先跑起来，再自动用默认浏览器打开网页
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True, use_reloader=False)
