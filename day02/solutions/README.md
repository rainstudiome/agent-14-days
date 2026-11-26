# 第 2 天练习：参考答案

> 题目见 [第 2 天文章](../README.md#练习) 的最后。三个脚本都是在 `day02/tool_call.py` 上改的，可以对照着看改了哪几处。下面的输出是我用 `deepseek-flash` 跑出来的，模型每次的选择都不一样，以你自己跑出来的为准。

## 练习 1：加一个 `list_files` 工具

代码：[`list_files.py`](list_files.py)

```bash
uv run day02/solutions/list_files.py
```

和 `tool_call.py` 比，改了三处。

**第一处：写一个真正干活的函数。**

```python
def list_files(path: str = ".") -> str:
    """列出一个目录里的文件和子目录，子目录名后面加 /，方便模型区分。"""
    entries = sorted((ROOT / path).iterdir(), key=lambda p: (p.is_file(), p.name))
    return "\n".join(p.name + ("/" if p.is_dir() else "") for p in entries) or "（空目录）"
```

- `path` 默认是 `"."`，也就是项目根目录。模型不给参数时，就列根目录。
- 子目录名后面加 `/`。模型只看得到文字，不加的话它分不清 `docs` 是文件还是目录。
- 返回的是一个字符串，每行一个名字。工具的结果最终都要变成文字交给模型，返回列表、对象都得先转成字符串。

**第二处：在 `TOOLS` 里加一项说明。**

```python
{
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "列出示例项目里一个目录下的文件和子目录（只列一层），子目录名以 / 结尾。不知道该读哪个文件时，先用它看看有什么。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相对于项目根目录的目录路径，不填就是根目录，比如 . 或 tinynotes"},
            },
            "required": [],
        },
    },
},
```

description 的最后一句"不知道该读哪个文件时，先用它看看有什么"是在告诉模型**什么时候**用它。只写"列出目录"，模型也会用，但不一定想到要先用。`required` 是空列表，表示 `path` 可以不填。

**第三处：按名字找到对应的函数。**

原来只有一个工具，直接调 `read_file(**args)` 就行。现在有两个了，要看模型请求的是哪一个：

```python
FUNCTIONS = {"read_file": read_file, "list_files": list_files}
...
args = json.loads(call.function.arguments or "{}")
result = FUNCTIONS[call.function.name](**args)
```

- 用一个字典把"工具名"映射到"函数"，模型说要哪个，就按名字取出来调用。以后加第三个、第四个工具，只要往字典里加一项。
- `arguments or "{}"`：`list_files` 可以不带参数，有的模型这时给的 `arguments` 是空字符串，`json.loads("")` 会报错。
- 模型要是编了一个不存在的工具名，就报一句"没有叫 xxx 的工具，可用的有……"，被 `try` 接住，作为结果交还给模型，程序不会崩，模型也知道该换哪个。

**应该看到**：第一次请求，模型调用 `list_files`；拿到目录以后，第二次请求它会去读 `README.md` 或 `tinynotes/config.py`：

```
③ 程序执行 list_files({})，把结果交还给模型：
{
  "role": "tool",
  "tool_call_id": "call_00_……",
  "content": "docs/\ntests/\ntinynotes/\nCHANGELOG.md\nREADME.md\npyproject.toml"
}

④ 模型看完目录，还想再调工具：
   read_file({"path": "README.md"})
   read_file({"path": "pyproject.toml"})
```

我用 `deepseek-flash` 跑了两次，两次都是这样：先看目录，再从列表里挑了 README.md 和 pyproject.toml，一次要两个。

这正是题目想让你看到的：**读哪个文件，是模型看了目录以后自己决定的**，不是我们写死的。有的模型会在第一次就同时请求 `list_files` 和 `read_file("README.md")`，因为 README 几乎每个项目都有，它猜得到。

和 `tool_call.py` 一样，这个脚本只处理一轮，所以停在"还想再调工具"。明天写成循环，它就能一路查下去了。

## 练习 2：打印两次请求的 `usage`

代码：[`usage.py`](usage.py)

```bash
uv run day02/solutions/usage.py
```

改法很简单：两次请求分别存成 `resp1`、`resp2`，打印各自的 `usage`，再相减。我用 `deepseek-flash` 跑的一次结果：

```
第一次请求：输入 329，输出 82（其中思考 8），合计 411
  执行 read_file({"path": "README.md"})，结果 460 个字符
  执行 read_file({"path": "package.json"})，结果 109 个字符
第二次请求：输入 679，输出 117（其中思考 23），合计 796

第二次的输入比第一次多了 350 个 token：第一次的工具请求，加上 569 个字符的工具结果。
这一个问题，两次请求合计 1207 个 token。
```

顺便留意第二个工具调用：sample_repo 里根本没有 `package.json`，模型没看目录，凭经验猜了一个。读文件出错，`try` 把报错（109 个字符）当作结果交还给模型，程序没崩。可这条报错也算进了输入 token。这正好说明练习 1 的 `list_files` 有什么用：先看清楚有什么，再去读。

**答案：第二次多出来的输入 token，等于"第一次模型的工具请求 + 工具结果"。** 拆开看：

| 第二次请求里的内容 | 第一次有没有 |
|---|---|
| system、user 两条消息 | 有 |
| 工具清单 `TOOLS` | 有，**每次请求都要带**，也算输入 token |
| assistant 那条工具请求 | 没有，新加的，几十个 token |
| tool 消息，也就是 README 全文 | 没有，新加的，大头在这里 |

几个值得注意的地方：

1. **工具结果越长，第二次越贵。** sample_repo 的 README 很短，只多了几百个 token。换一个问题让它读长一点的文件：

   ```bash
   uv run day02/solutions/usage.py "docs/api.md 里有哪些接口？"
   ```

   我跑的那次，api.md 有 4404 个字符，第二次请求的输入从 332 涨到了 2223，多了 1891 个 token。真实项目里一个源文件几千行，读一次就是几万 token。第 4 天的"分段读"就是为这个准备的。
2. **工具清单本身也要钱。** 第一次请求只问了一句话，输入却有 329 个 token，而第 1 天的 `hello.py` 只有几十个。多出来的大头就是 `TOOLS` 那一段 JSON Schema。工具越多、说明越长，每次请求的底价越高。
3. **思考的 token 不会被带到第二次。** 我们只把 `content` 和 `tool_calls` 放回了 messages，第一次输出里思考的部分不会出现在第二次的输入里。（有的思考模型在调工具时要求把思考内容也带回去，那样第二次会更贵一点，第 3 天的代码会处理。）

## 练习 3：把 `description` 删掉，只留名字

代码：[`no_description.py`](no_description.py)

```bash
uv run day02/solutions/no_description.py           # 删掉 description，名字还是 read_file、path
uv run day02/solutions/no_description.py --vague   # 连名字也换成 tool_1、x
```

脚本把工具和参数的 description 全删了，只剩名字和类型：

```python
TOOLS = [{"type": "function", "function": {
    "name": "read_file",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
}}]
```

**答案：多半还会用，而且用得对。** 我用 `deepseek-flash` 跑了两次，两次都是：

```
工具名：read_file，参数名：path，没有 description
问题：这个项目怎么运行？

模型调用了 read_file({"path": "README.md"})
```

原因是 `read_file` 和 `path` 这两个名字本身就把意思说清楚了。模型见过大量代码，看到这两个名字，猜得出它是读文件的、参数是文件路径。再加上 system 里写了"需要看文件时就调用工具"。

**名字也是提示词。** 加 `--vague` 再跑一遍就看得出来：名字换成 `tool_1`、参数换成 `x`，模型没有任何线索，只能猜。我同一个问题跑了三次，三次各不一样：

```
模型调用了 tool_1({"x": "README.md"})     ← 猜对了，当成读文件
模型调用了 tool_1({"x": "ls -la"})        ← 当成执行命令
模型调用了 tool_1({"x": "."})             ← 当成列目录，结果"出错：Is a directory"
```

换成问"一条笔记最多能写多少字？"，它更是把 `tool_1` 当成了终端，先 `ls -la`，失败了又写了一长串 `grep -rn ... | head -50`，全部出错。

这就是"看运气"的工具：同一个模型、同一个问题，每次猜得都不一样。也说明了一件事，**模型看不到你的函数是怎么写的**，它对一个工具的全部了解，就是名字、参数和说明这几行字。有的模型在这种情况下干脆不调用工具，直接凭印象回答。

所以这道题的结论是：**名字、参数名、description，三样都是写给模型看的。** 名字起得好，可以少写一点说明；名字含糊，就得靠说明补。但即使名字很清楚，description 也不该省：

- 名字只说了"是什么"，说不了"什么时候用""路径相对于哪里""文件太大怎么办"。练习 1 里 `list_files` 的"不知道该读哪个文件时，先用它"，就只能写在说明里。
- 工具一多，名字相近的工具（比如 `read_file` 和 `read_files`、`search` 和 `grep`）靠名字分不清，模型会用错。

第 4 天专门讲怎么写工具说明。
