import base64
import mimetypes
import os
import sys

import anthropic


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

# 能看图的模型（如果报错说模型不存在，就换成 deepseek-v4-flash 再试）
MODEL = "deepseek-flash"

PROMPT = """你是一个代码提取助手。下面的图片里是一段代码。
请把图片里的代码原样提取出来，保留缩进、符号、注释。
如果有看不清的地方，就在那个位置写 <此处模糊>，绝对不要自己编造。"""


def main():
    if len(sys.argv) < 2:
        print("用法：python test_api.py 图片路径")
        print("例如：python test_api.py test.png")
        return

    path = sys.argv[1]
    mime, _ = mimetypes.guess_type(path)
    if mime not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        print(f"不支持的图片格式：{mime}，请用 jpg/png/gif/webp")
        return

    with open(path, "rb") as f:
        image_data = f.read()
    image_b64 = base64.b64encode(image_data).decode("utf-8")

    print("正在调用 DeepSeek 看图模型，请稍等……")
    client = anthropic.Anthropic()  # 自动从 .env 读取 key 和地址

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
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

    print("===== 模型返回 =====")
    # 模型可能先返回"思考块"，再返回"文字块"，我们只取文字块
    text_parts = [b.text for b in message.content if getattr(b, "type", "") == "text"]
    reply = "\n".join(text_parts)
    if reply:
        print(reply)
    else:
        print("（没有找到文字结果，原始返回如下）")
        print(message.content)


if __name__ == "__main__":
    main()
