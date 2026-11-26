"""第 2 天：一次完整的工具调用。

模型不会自己读文件。它只会说"我要调 read_file，参数是 README.md"，
真正去读文件的是我们的程序。这个脚本把来回的每一条消息都打印出来。
运行：uv run day02/tool_call.py
      uv run day02/tool_call.py "这个项目怎么跑测试？"
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
ROOT = Path(__file__).resolve().parent.parent / "sample_repo"  # 练习用的示例项目


def read_file(path: str) -> str:
    """真正干活的函数。模型永远碰不到它，只有我们的程序会调用它。"""
    return (ROOT / path).read_text(encoding="utf-8")


# 告诉模型有哪些工具：名字、说明、参数的 JSON Schema
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


def show(title: str, message: dict) -> None:
    text = json.dumps(message, ensure_ascii=False, indent=2)
    print(f"\n{title}\n{text[:1200]}{' ……（后面省略）' if len(text) > 1200 else ''}")


question = " ".join(sys.argv[1:]) or "这个项目怎么运行？"
messages = [
    {"role": "system", "content": "你是代码仓库助手。需要看文件时就调用工具，不要猜。"},
    {"role": "user", "content": question},
]
show("① 我们发出的问题：", messages[-1])

# 第一次请求：把工具清单一起发过去，由模型决定要不要用
resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
msg = resp.choices[0].message
if not msg.tool_calls:
    print("\n模型没有调用工具，直接回答了：", msg.content)
    raise SystemExit

# 模型的回复里没有答案，只有"我要调哪个工具、参数是什么"
assistant = {
    "role": "assistant",
    "content": msg.content or "",
    "tool_calls": [
        {"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
        for c in msg.tool_calls
    ],
}
messages.append(assistant)
show("② 模型的回复：", assistant)

# 由我们的程序执行工具，每个调用的结果都作为一条 tool 消息交还给模型
for call in msg.tool_calls:
    args = json.loads(call.function.arguments)  # arguments 是字符串，要自己解析
    try:
        result = read_file(**args)
    except Exception as e:
        result = f"出错：{e}"
    tool_message = {"role": "tool", "tool_call_id": call.id, "content": result}
    messages.append(tool_message)
    show(f"③ 程序执行 {call.function.name}({call.function.arguments})，把结果交还给模型：", tool_message)

# 第二次请求：模型看到工具结果，再回答
resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
final = resp.choices[0].message
if final.tool_calls:
    print("\n④ 模型还想再调工具：", [c.function.name for c in final.tool_calls])
    print("   这个脚本只处理一轮。要让它一直调下去，就得写成循环，这是第 3 天的内容。")
else:
    show("④ 模型的最终回答：", {"role": "assistant", "content": final.content})
