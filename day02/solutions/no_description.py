"""第 2 天练习 3 的参考答案：把 description 删掉，只留名字，看模型还会不会用工具。

默认：工具名还是 read_file、参数名还是 path，但工具和参数的 description 都删掉了。
加 --vague：连名字也换成看不出意思的 tool_1 和 x，模型只剩一个空壳可看。
运行：uv run day02/solutions/no_description.py
      uv run day02/solutions/no_description.py --vague
      uv run day02/solutions/no_description.py --vague "一条笔记最多能写多少字？"
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

VAGUE = "--vague" in sys.argv
NAME, PARAM = ("tool_1", "x") if VAGUE else ("read_file", "path")


def read_file(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


# 只有名字和参数类型，没有任何 description
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": NAME,
            "parameters": {
                "type": "object",
                "properties": {PARAM: {"type": "string"}},
                "required": [PARAM],
            },
        },
    }
]

args_text = [a for a in sys.argv[1:] if a != "--vague"]
question = " ".join(args_text) or "这个项目怎么运行？"
messages = [
    {"role": "system", "content": "你是代码仓库助手。需要看文件时就调用工具，不要猜。"},
    {"role": "user", "content": question},
]
print(f"工具名：{NAME}，参数名：{PARAM}，没有 description")
print(f"问题：{question}")

resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
msg = resp.choices[0].message
if not msg.tool_calls:
    print("\n模型没有调用工具，直接回答了：", msg.content)
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
for call in msg.tool_calls:
    print(f"\n模型调用了 {call.function.name}({call.function.arguments})")
    try:
        result = read_file(json.loads(call.function.arguments)[PARAM])
    except Exception as e:
        result = f"出错：{e}"
    print(f"  结果：{result[:80]!r}{' ……' if len(result) > 80 else ''}")
    messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
final = resp.choices[0].message
if final.tool_calls:
    print("\n模型还想再调工具：", [f"{c.function.name}({c.function.arguments})" for c in final.tool_calls])
else:
    print("\n模型的最终回答：", final.content)
