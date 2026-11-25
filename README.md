# 从 0 到 1，14 天入门 Agent 开发

用 14 天，从零写出一个代码助手：它能读代码、找答案、修 bug，动手改文件之前会先问你。

- **前 8 天不用任何框架**：从一个最普通的 HTTP 请求开始，一天加一样东西，包括工具、循环、权限、上下文、评测和检索。
- **第 9 天学 LangGraph**：用框架重写一遍，看它替你做了什么。
- **第 10–12 天学 DeepAgents**：用官方脚手架生成项目，把前面手写的东西换成框架内置的，做成一个能接手长任务的"深度 Agent"。
- **最后 2 天走向实用**：给它做一个网页界面；换上本地部署的开源模型，把步骤固定的部分写成工作流。
- **另有两篇番外**：给 Agent 加上追踪；多 Agent 什么时候值得拆，怎么用 A2A 协议连起来。

每天一篇文章，加一份能跑的代码。文章首发在公众号 rainstudiome（见[关注更新](#关注更新)），代码在这个仓库。

## 适合谁

- **零基础也能跟。** 每一步都写了要敲的命令、应该看到的结果，以及没看到时怎么办。会一点编程更好，看得懂 Python 最好。
- 用过 ChatGPT、Cursor 或 Claude Code，好奇 Agent 是怎么工作的。
- 想系统地学一遍 Agent 开发，把它用到自己项目里的程序员。

需要准备：一台电脑（Windows、macOS、Linux 都行），一个模型 API 的账号（第 1 天教你注册）。跑完整个系列，模型 API 的花费很少；也可以用本机的 Ollama，不花钱（第 14 天细讲）。第 13 天的网页要装 Node.js。

## 学完能做到

1. 不靠框架，讲清楚 Agent 每一步在做什么：消息、工具调用、循环、上下文。
2. 自己写出带工具、权限审批、上下文管理、评测和检索的 Agent。
3. 用 LangGraph 和 DeepAgents 搭 Agent，知道它们替你做了什么、没替你做什么。
4. 用一套评测集，拿数字说明一次改动是变好了还是变坏了。
5. 给 Agent 做一个网页界面：回答边生成边显示，改文件之前在浏览器里审批。
6. 把 Agent 换成本地部署的开源模型；知道什么时候该改用工作流，以及怎么让模型按固定格式输出。

## 我们要做的东西

一个"代码仓库助手"，对着练习项目 `sample_repo` 干活。`sample_repo` 是一个很小的笔记服务，叫 tinynotes。它有接口、有测试、有文档，还故意留了一个 bug、埋了两处文档和代码对不上的地方。

| 到第几天 | 它能做什么 |
|---|---|
| 第 3 天 | 自己翻文件，回答"这个项目怎么运行" |
| 第 5 天 | 找到失败的测试，改代码，再跑测试确认；改之前先给你看改了哪几行 |
| 第 6 天 | 接手要读十几个文件的长任务，不跑偏、不撑爆上下文 |
| 第 7 天 | 30 道评测题（20 道回归题、10 道能力题），一条命令跑出通过率 |
| 第 8 天 | 用你自己的话提问也找得到答案：关键词、向量检索和重排序 |
| 第 11 天 | 派几个子 Agent 分头核对文档，写一份报告 |
| 第 12 天 | 会列计划、记得住你的习惯；审批可以先放着，过一会儿再批 |
| 第 13 天 | 有了网页界面：回答一个字一个字地出来，在浏览器里看 diff、点批准 |
| 第 14 天 | 换上在自己电脑上跑的开源模型；固定的流程改成工作流，只调用一次模型 |

想换成你自己的项目：在命令前面加 `REPO=/你的项目路径`。

## 大纲

### 第一部分：手写（第 1–8 天，不用任何框架）

| 天 | 题目 | 搞懂什么 |
|---|---|---|
| 1 | Agent 是什么：先跟模型说上话 | Agent = 模型 + 工具 + 循环；装好环境、拿到 API key；消息和 token；模型自己没有记忆 |
| 2 | 工具调用：模型不会执行，它只会"请求" | 一次工具调用前后完整的消息序列；工具说明的 JSON Schema；`tool_call_id` |
| 3 | 不到 100 行，手写一个 Agent | 循环和停止条件；工具出错时交还给模型；故意把它弄坏三次 |
| 4 | 工具设计：Agent 好不好用，一半看工具 | 工具设计的五条原则；分段读、搜索、能照着改的报错；用 MCP 把工具接进 Claude Code |
| 5 | 权限：Agent 动手之前，先问你 | 只读、改文件、执行命令三档权限；diff 预览；命令白名单；拒绝也是信息；反思和完成判定；提示词注入和"致命三要素" |
| 6 | 长任务：计划、压缩和子 Agent | 待办清单；清理旧的工具结果；压缩历史；缓存为什么怕改前面的内容；子 Agent 隔离上下文 |
| 7 | 评测：用数字回答"变好还是变坏" | 回归题和能力题；程序判分和模型判分；错误分析，包括"判错了"；两次结果怎么比；pass^k；评测饱和了怎么办 |
| 8 | 检索与记忆：找得到，记得住 | 切块、BM25、中文切词；检索评测（Hit@k、MRR）；向量存进 Qdrant；混合检索和重排序；长期记忆文件；写记忆为什么要审批 |

### 第二部分：框架（第 9–12 天）

| 天 | 题目 | 搞懂什么 |
|---|---|---|
| 9 | LangGraph：人在回路，看框架替你做了什么 | 状态、节点、边；`interrupt` 和 `Command`；批准、修改、拒绝三种决定；checkpointer；`create_agent` 加审批中间件 |
| 10 | DeepAgents 上手：用官方脚手架搭第一个深度 Agent | 深度 Agent 的四个要素；`langgraph new` 生成项目；`create_deep_agent`；内置工具；接国产模型；`langgraph dev` 和 Studio |
| 11 | DeepAgents 进阶：文件系统、子 Agent 和技能 | 四种存储后端和按路径组合；大结果写进文件；自定义子 Agent；多 Agent 的两种组织方式和 A2A；技能（`SKILL.md`）；自动压缩怎么配 |
| 12 | DeepAgents 实战：人在回路、Postgres 和上线 | 按路径和按工具审批；四种决定；对话状态和长期记忆存进 Postgres；用第 7 天的评测比较手写版和 DeepAgents 版；上线清单 |

### 第三部分：走向实用（第 13–14 天）

| 天 | 题目 | 搞懂什么 |
|---|---|---|
| 13 | 网页界面：流式输出，在浏览器里审批 | 流式输出和 SSE；思考模型的流式；Agent 在服务端、网页只管显示；`@langchain/react` 的 `useStream`；审批卡片；刷新页面为什么不丢 |
| 14 | 私有化：换上开源模型，能写死的就写死 | Ollama 和 vLLM；上下文窗口的坑；换模型前先测工具调用；用 LangGraph 写工作流；结构化输出的三种做法和校验；工作流的五种形状；Agent 和工作流比一比；14 天回顾 |

### 番外（不算在 14 天里，学完可以接着看）

| 篇 | 题目 | 搞懂什么 |
|---|---|---|
| 番外一 | 看得见：给 Agent 加上追踪 | trace、span 和属性；手写一个追踪器，不改代码包一层；用追踪找出时间和 token 花在哪；OpenTelemetry 和大模型的属性规范；发到 Jaeger、Langfuse；DeepAgents 不改代码接上 |
| 番外二 | 多 Agent：什么时候值得拆，A2A 怎么连 | 什么时候该拆；管理者模式和交接，手写一个交接；A2A 的名片、任务和消息；LangGraph 服务自带的 A2A 接口；远程审批；手写的 Agent 通过 A2A 请 DeepAgents 版帮忙 |

## 为什么这样安排

- **先手写，后框架。** 框架把循环、状态、审批都藏起来了。先手写一遍，学框架时你能对上它的每一个概念：这个中间件就是第 5 天的 `permissions.check`，那个 `task` 工具就是第 6 天的子 Agent。
- **一个项目做到底。** 每天的代码都能单独运行，和前一天比只多一样东西，用 diff 一比就知道那天加了什么。
- **每天都故意弄坏一次。** 删掉一行、拿掉一个限制，看它怎么坏。坏的样子，就是生产环境里会遇到的问题。
- **评测放在中间。** 第 7 天以后的每一次改动，包括换成 DeepAgents，都用同一套题打分，不凭感觉说"好像更好了"。
- **从易到难。** 前 8 天只要 Python 和一个模型 API；第 9 天加 LangGraph；第 10–12 天用官方脚手架；数据库到第 12 天才用，而且是可选的；第 13 天加一点前端；第 14 天的本地模型也是可选的。
- **最后落到实用。** 有界面，别人才用得上；模型私有化、能写死的写死，是把 Agent 用到实际项目里最常遇到的两件事。

## 准备

详细步骤见第 1 天的文章。简单说：

1. **装 uv。** uv 是现在 Python 项目最常用的管理工具，能帮你装好 Python 和所有依赖。
2. **下载代码**，在仓库根目录运行 `uv sync`。
3. **配置模型。** 把 `.env.example` 复制成 `.env`，填好 `BASE_URL`、`API_KEY`、`MODEL` 三项。
4. **检查。** `uv run day01/hello.py` 能打印出模型的回答，就可以开始了。

习惯用 pip 也可以：建一个虚拟环境，`pip install -r requirements.txt`，然后把文中的 `uv run` 换成 `python`。

第 10–12 天在 `deep-agent/` 目录，是用 LangGraph 官方脚手架生成的独立项目，有自己的依赖，第 10 天的文章里会一步步教你。

第 13 天的网页在 `day13/web/`，要装 Node.js（20.19 以上），第 13 天的文章里会一步步教你。

## 每天怎么运行

| 天 | 命令（在仓库根目录） |
|---|---|
| 1 | `uv run day01/hello.py`、`uv run day01/chat.py` |
| 2 | `uv run day02/tool_call.py` |
| 3 | `uv run day03/agent.py "这个项目有哪些接口？"` |
| 4 | `uv run day04/agent.py "笔记太长时，接口返回什么状态码？"` |
| 5 | `uv run day05/agent.py "tests 里有个测试过不了，找到原因修好，再跑测试确认"`、`uv run day05/goal.py "tests 里有个测试过不了，找到原因修好"` |
| 6 | `uv run day06/agent.py "把 docs 目录下每个文档的要点各用一句话总结"` |
| 7 | `uv run day07/evals/run_evals.py` |
| 8 | `uv run day08/agent.py "部署的时候数据存在哪？怎么备份？"`、`uv run day08/eval_retrieval.py` |
| 9 | `uv run day09/graph_agent.py "tests 里有个测试过不了，修好它"` |
| 10–12 | `cd deep-agent`，然后 `uv run python -m deep_agent.cli day10 "问题"`（第 10 天细讲） |
| 13 | `uv run day13/stream.py`；网页：先在 `deep-agent` 里运行 `uv run langgraph dev`，再在 `day13/web` 里运行 `npm install`、`npm run dev` |
| 14 | `uv run day14/probe_tools.py`、`uv run day14/workflow.py`、`uv run day14/bench.py`、`uv run day14/patterns.py route "问题"` |
| 番外一 | `uv run extra01/run.py "问题"`，然后 `uv run extra01/view_trace.py` |
| 番外二 | `uv run extra02/handoff.py "问题"`；先在 `deep-agent` 里运行 `uv run langgraph dev`，再 `uv run extra02/a2a_client.py "问题"`、`uv run extra02/manager.py "任务"` |

从第 5 天起，Agent 会真的修改 `sample_repo` 里的文件，改之前会先问你。想恢复原样：`git checkout sample_repo`。

想看某一天比前一天多了什么，用 diff 比一比，比如第 5 天的工具比第 4 天多了什么：

```bash
git diff --no-index day04/tools.py day05/tools.py
```

## 目录

```
.
├── README.md            课程介绍和大纲（就是这份）
├── pyproject.toml       第 1–9 天、第 13–14 天和番外的 Python 依赖（uv 用）
├── requirements.txt     同样的依赖（pip 用）
├── .env.example         模型和数据库的配置模板
├── docker-compose.yml   第 9、12 天可选的 Postgres
├── sample_repo/         练习项目：一个很小的笔记服务
├── day01/ … day09/      每天一个目录：README.md 是当天的文章，images/ 是配图，其余是代码
├── day10/ … day12/      DeepAgents 那 3 天的文章
├── deep-agent/          DeepAgents 那 3 天的代码：用官方脚手架生成的项目；第 13 天的网页也连它
├── day13/               网页界面：stream.py，和 web/ 里的 React 项目
├── day14/               私有化和工作流
├── extra01/             番外一：追踪
├── extra02/             番外二：多 Agent 和 A2A
├── scripts/             生成文章配图的脚本
└── tests/               第 1–9 天、第 14 天和番外代码的测试
```

## 代码规范

- **依赖管理用 uv。** 依赖写在 `pyproject.toml` 里，版本锁在 `uv.lock` 里，谁装都是同一套版本。
- **代码风格用 Ruff 检查和格式化。** `uv run ruff check .`、`uv run ruff format .`。
- **测试不花钱。** `uv run pytest` 会把每天的关键代码都跑一遍。测试里用的是一个假的模型服务（`tests/fake_llm.py`），按脚本回复，不联网、不用 API key。
- **DeepAgents 的项目用官方脚手架生成。** `langgraph new --template deep-agent-python`，项目结构、`langgraph.json`、Makefile、测试都沿用官方模板的写法。
- **网页用 Vite + React + TypeScript。** 连 Agent 用官方的 `@langchain/react`；`npm run build` 会先做类型检查。
- **配图用代码生成。** `uv run scripts/diagrams.py` 画出 SVG，再用本机的 Chrome 导出 PNG，都放在每天的 `images/` 里。想改图，改脚本再运行一遍。

## 一起看的资料

这个系列参考了下面这些资料。它们各有侧重，学完这 14 天，可以按需要接着看：

| 资料 | 是什么 | 和这个系列的关系 |
|---|---|---|
| [Hello-Agents](https://github.com/datawhalechina/hello-agents)（Datawhale） | 中文，16 章，从理论到多个综合案例，还有自研框架 | 更全面、更系统；想补理论和经典范式就看它 |
| [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | 从一个循环一路加到权限、计划、子 Agent、压缩、记忆、MCP，每课一个机制 | 思路最接近，用的是 Claude 的接口；想往"做一个 Claude Code"深挖就看它 |
| [How to Build an Agent](https://ampcode.com/notes/how-to-build-an-agent)（Thorsten Ball） | 用 Go 写一个会读文件、改文件的 Agent | 第 3 天的出发点 |
| Anthropic 工程博客的几篇：[Building effective agents](https://www.anthropic.com/research/building-effective-agents)、[Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)、[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 什么时候用工作流、什么时候用 Agent；怎么设计工具；怎么管理上下文 | 第 1、4、6 天的主要参考 |
| [AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)（微软） | 十几课，讲设计模式、多 Agent、可信、上线 | 示例基于微软自家的框架和 Azure |
| [Agents Course](https://huggingface.co/learn/agents-course)（Hugging Face） | 从基础到 smolagents、LangGraph、LlamaIndex 三个框架 | 想横向比较几个框架就看它 |
| [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)（OpenAI） | 选模型、单 Agent 和多 Agent 怎么组织、护栏 | 第 5、11 天和番外二的参考；和 Anthropic 那几篇对照着读 |
| [Deep Agents 文档](https://docs.langchain.com/oss/python/deepagents/overview)（LangChain） | DeepAgents 的官方文档 | 第 10–12 天的主要参考；框架更新快，以官方文档为准 |

## 版本

代码在这些版本上测过：Python 3.12、openai 3.57、langchain 1.5、langgraph 1.2、deepagents 0.7.41、langgraph-cli 0.4、langgraph-api 0.18（自带 A2A 1.0 接口）、mcp 2.3、qdrant-client 1.20、opentelemetry-sdk 1.45、Postgres 18；网页是 Node.js 24、React 19、Vite 7、@langchain/react 1.3。模型用 DeepSeek 的 `deepseek-flash` 跑过一遍（2026 年 11 月）。完整的版本锁在 `uv.lock`、`deep-agent/uv.lock` 和 `day13/web/package-lock.json` 里。LangGraph、DeepAgents 和 `@langchain/react` 更新很快，遇到接口对不上，先对照这里的版本。

## 关注更新

这个系列的文章首发在公众号，之后写的 Agent 开发内容也会发在下面这几个地方：

| 平台 | 账号 | 发什么 |
|---|---|---|
| 微信公众号 | rainstudiome | 文章首发 |
| 知乎 | rainstudiome | 文章同步，回答 Agent 开发的问题 |
| B 站 | rainstudiome | 视频 |

文章有错、代码跑不通，欢迎在 GitHub 上提 Issue。

## 许可

- 代码（包括 `sample_repo`、`deep-agent`、`day13/web`，以及每天和番外的 `.py` 文件）：[MIT](LICENSE)。
- 文章和配图（每天和番外的 `README.md`，以及 `images/`）：[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)。转载、改编请注明出处，并以同样的方式共享，不能用于商业用途。
