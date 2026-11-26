"""第 1 天练习 2 的参考答案：连续聊 10 轮，看输入 token 怎么涨。

自动发 10 个问题，每轮打印输入 token、比上一轮多了多少，最后算一共花了多少输入 token。
运行：uv run day01/solutions/token_growth.py
对照：uv run day01/solutions/token_growth.py --no-history  （不带历史，输入 token 基本不涨）
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["BASE_URL"], api_key=os.environ["API_KEY"])
MODEL = os.environ["MODEL"]
KEEP_HISTORY = "--no-history" not in sys.argv

QUESTIONS = [
    "我叫小王，是一名程序员。",
    "推荐一门适合入门的编程语言。",
    "为什么推荐它？",
    "学它大概要多久？",
    "有什么好的入门书？",
    "我每天只有一小时，怎么安排？",
    "学完能做什么项目？",
    "做项目时卡住了怎么办？",
    "再推荐一个进阶方向。",
    "我叫什么？做什么工作？",
]

system = {"role": "system", "content": "你是一个简洁的助手，回答尽量不超过三句话。"}
history = []
total_input = 0
last_input = None

print(f"{'轮':>2}  {'消息数':>4}  {'输入 token':>9}  {'比上轮多':>7}  问题")
for i, question in enumerate(QUESTIONS, 1):
    user = {"role": "user", "content": question}
    messages = [system, *history, user] if KEEP_HISTORY else [system, user]
    resp = client.chat.completions.create(model=MODEL, messages=messages)
    answer = resp.choices[0].message.content
    # 和 chat.py 一样，只把回答 content 放回历史；思考内容不放回去
    history += [user, {"role": "assistant", "content": answer}]

    prompt = resp.usage.prompt_tokens
    delta = "" if last_input is None else f"{prompt - last_input:+d}"
    print(f"{i:>2}  {len(messages):>6}  {prompt:>10}  {delta:>9}  {question}")
    total_input += prompt
    last_input = prompt

print(f"\n10 轮一共发了 {total_input} 个输入 token；最后一轮的回答：{answer}")
