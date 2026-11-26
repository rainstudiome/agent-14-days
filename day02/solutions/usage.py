"""第 2 天练习 2 的参考答案：打印两次请求的 usage，看第二次多花了多少 token。

流程和 tool_call.py 一样，只是不打印消息全文，改成打印每次请求的 token 用量。
运行：uv run day02/solutions/usage.py
      uv run day02/solutions/usage.py "docs/api.md 里有哪些接口？"
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["BASE_URL"], api_key=os.environ["API_KEY"])
MODEL = os.environ["MODEL"]
ROOT = Path(__file__).resolve().parent.parent.parent / "sample_repo"


def read_file(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取示例项目里的一个文本文件，返回全文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "相对于项目根目录的路径，比如 README.md"},
                },
                "required": ["path"],
            },
        },
    }
]


def show_usage(title: str, u) -> None:
    details = getattr(u, "completion_tokens_details", None)
    reasoning = getattr(details, "reasoning_tokens", None) or 0
    print(f"{title}：输入 {u.prompt_tokens}，输出 {u.completion_tokens}（其中思考 {reasoning}），合计 {u.total_tokens}")


question = " ".join(sys.argv[1:]) or "这个项目怎么运行？"
messages = [
    {"role": "system", "content": "你是代码仓库助手。需要看文件时就调用工具，不要猜。"},
    {"role": "user", "content": question},
]

resp1 = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
msg = resp1.choices[0].message
show_usage("第一次请求", resp1.usage)
if not msg.tool_calls:
    print("模型没有调用工具，直接回答了，没有第二次请求。")
    raise SystemExit

messages.append(
    {
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": [
            {"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
            for c in msg.tool_calls
        ],
    }
)
tool_chars = 0
for call in msg.tool_calls:
    try:
        result = read_file(**json.loads(call.function.arguments))
    except Exception as e:
        result = f"出错：{e}"
    tool_chars += len(result)
    print(f"  执行 {call.function.name}({call.function.arguments})，结果 {len(result)} 个字符")
    messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

resp2 = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
show_usage("第二次请求", resp2.usage)

extra = resp2.usage.prompt_tokens - resp1.usage.prompt_tokens
print(f"\n第二次的输入比第一次多了 {extra} 个 token：第一次的工具请求，加上 {tool_chars} 个字符的工具结果。")
total = resp1.usage.total_tokens + resp2.usage.total_tokens
print(f"这一个问题，两次请求合计 {total} 个 token。")
