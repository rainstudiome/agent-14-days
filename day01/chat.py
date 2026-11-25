"""第 1 天：命令行里的多轮对话。

每一轮都把整段对话发给模型，并打印这次发了几条消息、用了多少 token。
运行：uv run day01/chat.py
实验：uv run day01/chat.py --no-history  （每轮只发当前这一句，看模型还记不记得前面）
输入 exit 或直接回车退出。
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["BASE_URL"], api_key=os.environ["API_KEY"])
MODEL = os.environ["MODEL"]
KEEP_HISTORY = "--no-history" not in sys.argv

system = {"role": "system", "content": "你是一个简洁的助手，回答尽量不超过三句话。"}
history = []  # 之前每一轮的提问和回答

while True:
    try:
        question = input("\n你：").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if question in ("", "exit", "quit"):
        break

    user = {"role": "user", "content": question}
    # 模型自己不记得任何东西：它知道的，只有这次发过去的 messages
    messages = [system, *history, user] if KEEP_HISTORY else [system, user]
    resp = client.chat.completions.create(model=MODEL, messages=messages)
    answer = resp.choices[0].message.content

    history += [user, {"role": "assistant", "content": answer}]
    print(f"模型：{answer}")
    u = resp.usage
    print(f"  [这次发了 {len(messages)} 条消息；输入 {u.prompt_tokens} token，输出 {u.completion_tokens} token]")
