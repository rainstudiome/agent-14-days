"""第 1 天：发出第一个请求，确认环境配好了。

运行：uv run day01/hello.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 读取仓库根目录的 .env
client = OpenAI(base_url=os.environ["BASE_URL"], api_key=os.environ["API_KEY"])

resp = client.chat.completions.create(
    model=os.environ["MODEL"],
    messages=[{"role": "user", "content": "用一句话介绍你自己。"}],
)
print(resp.choices[0].message.content)
print(resp.usage)  # 这次请求用了多少 token：输入、输出、合计
