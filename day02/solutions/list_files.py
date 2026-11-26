"""第 2 天练习 1 的参考答案：加一个 list_files 工具。

在 tool_call.py 的基础上多给模型一个工具，让它先看目录，再决定读哪个文件。
和 tool_call.py 一样只处理一轮，所以最后会打印"模型还想再调工具"和它挑中的文件。
运行：uv run day02/solutions/list_files.py
      uv run day02/solutions/list_files.py "测试是怎么写的？"
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


def list_files(path: str = ".") -> str:
    """列出一个目录里的文件和子目录，子目录名后面加 /，方便模型区分。"""
    entries = sorted((ROOT / path).iterdir(), key=lambda p: (p.is_file(), p.name))
    return "\n".join(p.name + ("/" if p.is_dir() else "") for p in entries) or "（空目录）"


# 工具名 → 真正干活的函数。模型说要调哪个，就按名字找到对应的函数
FUNCTIONS = {"read_file": read_file, "list_files": list_files}

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
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "列出示例项目里一个目录下的文件和子目录（只列一层），子目录名以 / 结尾。"
                "不知道该读哪个文件时，先用它看看有什么。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "相对于项目根目录的目录路径，不填就是根目录，比如 . 或 tinynotes",
                    },
                },
                "required": [],
            },
        },
    },
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

resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
msg = resp.choices[0].message
if not msg.tool_calls:
    print("\n模型没有调用工具，直接回答了：", msg.content)
    raise SystemExit

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

for call in msg.tool_calls:
    try:
        if call.function.name not in FUNCTIONS:
            raise ValueError(f"没有叫 {call.function.name} 的工具，可用的有：{', '.join(FUNCTIONS)}")
        args = json.loads(call.function.arguments or "{}")  # list_files 可以不带参数，arguments 可能是空字符串
        result = FUNCTIONS[call.function.name](**args)
    except Exception as e:
        result = f"出错：{e}"
    tool_message = {"role": "tool", "tool_call_id": call.id, "content": result}
    messages.append(tool_message)
    show(f"③ 程序执行 {call.function.name}({call.function.arguments})，把结果交还给模型：", tool_message)

resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
final = resp.choices[0].message
if final.tool_calls:
    print("\n④ 模型看完目录，还想再调工具：")
    for c in final.tool_calls:
        print(f"   {c.function.name}({c.function.arguments})")
    print("   这个脚本只处理一轮。要让它一直调下去，就得写成循环，这是第 3 天的内容。")
else:
    show("④ 模型的最终回答：", {"role": "assistant", "content": final.content})
