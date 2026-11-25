# 接口文档

所有接口都返回 JSON，编码是 UTF-8。请求体（只有新建笔记需要）也是 JSON。下面的例子用 curl，假设服务跑在本机的默认端口上。

## 通用约定

- 时间都是 UTC，格式是 ISO 8601，比如 `2026-10-20T08:30:00+00:00`。
- 笔记的 id 是自增整数，删除以后不会复用。
- 列表和搜索结果都按 id 倒序，也就是新的在前。
- 出错时返回的 JSON 只有一个字段 `error`，内容是给人看的说明。状态码的含义见文末的"错误码"一节。

## 健康检查

```
GET /health
```

用来确认服务活着，也会返回当前版本号。负载均衡和容器编排的存活探针可以直接用它。

请求：

```bash
curl http://localhost:8080/health
```

返回：

```json
{
  "status": "ok",
  "version": "0.3.1"
}
```

## 列出笔记

```
GET /notes?page=1
```

分页列出笔记，按 id 倒序。`page` 从 1 开始，不传就是第 1 页。每页的条数是固定的，由配置决定，不能通过参数修改。翻到没有数据的页，返回空列表，不报错。

请求：

```bash
curl "http://localhost:8080/notes?page=2"
```

返回：

```json
{
  "page": 2,
  "notes": [
    {
      "id": 21,
      "title": "周末计划",
      "body": "周末计划\n周六上午去爬山，下午整理照片。",
      "created_at": "2026-10-18T02:15:42+00:00"
    },
    {
      "id": 20,
      "title": "读书笔记：人月神话",
      "body": "读书笔记：人月神话\n向进度落后的项目增加人手，只会让它更落后。",
      "created_at": "2026-10-17T13:02:10+00:00"
    }
  ]
}
```

`page` 不是整数时返回 400。

## 新建笔记

```
POST /notes
```

请求体是一个 JSON 对象，只有一个字段 `body`，就是笔记正文。标题不能自己指定，服务会用正文的第一行生成，太长会截断。正文的首尾空白会被去掉。

请求：

```bash
curl -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"body": "买菜清单\n西红柿、鸡蛋、葱"}'
```

返回（状态码 201）：

```json
{
  "id": 22,
  "title": "买菜清单",
  "body": "买菜清单\n西红柿、鸡蛋、葱",
  "created_at": "2026-10-20T08:30:00+00:00"
}
```

请求体不是合法的 JSON、不是 JSON 对象、没有 `body` 字段或者 `body` 是空字符串，都返回 400。正文太长和请求体太大的情况见文末的"错误码"。

## 查看一条笔记

```
GET /notes/<id>
```

请求：

```bash
curl http://localhost:8080/notes/22
```

返回：

```json
{
  "id": 22,
  "title": "买菜清单",
  "body": "买菜清单\n西红柿、鸡蛋、葱",
  "created_at": "2026-10-20T08:30:00+00:00"
}
```

笔记不存在时返回 404：

```json
{
  "error": "笔记不存在"
}
```

## 删除笔记

```
DELETE /notes/<id>
```

请求：

```bash
curl -X DELETE http://localhost:8080/notes/22
```

返回：

```json
{
  "deleted": 22
}
```

删除不存在的笔记返回 404。0.3.1 之前这里会错误地返回 200，见 `CHANGELOG.md`。

## 搜索笔记

```
GET /search?q=关键词
```

在标题和正文里找包含关键词的笔记，是子串匹配，不分词。关键词要做 URL 编码，curl 可以用 `--data-urlencode` 帮你编码。

请求：

```bash
curl -G http://localhost:8080/search --data-urlencode "q=鸡蛋"
```

返回：

```json
{
  "q": "鸡蛋",
  "notes": [
    {
      "id": 22,
      "title": "买菜清单",
      "body": "买菜清单\n西红柿、鸡蛋、葱",
      "created_at": "2026-10-20T08:30:00+00:00"
    }
  ]
}
```

没有传 `q`，或者 `q` 只有空白时，返回 400：

```json
{
  "error": "缺少查询参数 q"
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 整数 | 笔记 id，自增，删除后不复用 |
| `title` | 字符串 | 由正文第一行生成，不能自己指定 |
| `body` | 字符串 | 正文，首尾空白已去掉 |
| `created_at` | 字符串 | 创建时间，UTC，ISO 8601 |
| `page` | 整数 | 列表接口返回当前页码 |
| `q` | 字符串 | 搜索接口原样返回查询的关键词 |
| `deleted` | 整数 | 删除接口返回被删除的笔记 id |
| `error` | 字符串 | 出错时的说明 |

## 用代码调用

### Python

只用标准库：

```python
import json
from urllib.request import Request, urlopen

BASE = "http://localhost:8080"


def create_note(body: str) -> dict:
    data = json.dumps({"body": body}).encode("utf-8")
    req = Request(f"{BASE}/notes", data=data, method="POST",
                  headers={"Content-Type": "application/json"})
    with urlopen(req) as resp:
        return json.load(resp)


def list_notes(page: int = 1) -> list[dict]:
    with urlopen(f"{BASE}/notes?page={page}") as resp:
        return json.load(resp)["notes"]


note = create_note("买菜清单\n西红柿、鸡蛋、葱")
print(note["id"], note["title"])
print(len(list_notes()))
```

出错时 `urlopen` 会抛出 `HTTPError`，可以从 `e.code` 拿到状态码，从 `e.read()` 拿到 `{"error": ...}`。

### JavaScript

浏览器和 Node.js 18 以上都可以直接用 `fetch`：

```javascript
const BASE = "http://localhost:8080";

async function createNote(body) {
  const resp = await fetch(`${BASE}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ body }),
  });
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(`${resp.status}: ${data.error}`);
  }
  return data;
}

async function searchNotes(keyword) {
  const url = `${BASE}/search?q=${encodeURIComponent(keyword)}`;
  const resp = await fetch(url);
  return (await resp.json()).notes;
}
```

从浏览器里直接调用时要注意跨域：tinynotes 没有设置 CORS 响应头，前端页面和服务不在同一个域名下会被浏览器拦住。可以在前面加一层反向代理，让页面和接口同源。

## 错误码

| 状态码 | 什么时候出现 | 怎么处理 |
|---|---|---|
| 400 | 请求体不是合法的 JSON 对象；缺少 `body`；搜索没传 `q`；`page` 不是整数 | 按提示修改请求 |
| 404 | 接口不存在；笔记不存在 | 检查路径和 id |
| 413 | 请求体超过 64 KB（`config.MAX_BODY_BYTES`） | 缩短内容，或者拆成多条笔记 |
| 422 | 笔记正文超过 2000 个字符（`config.MAX_NOTE_LENGTH`） | 缩短正文，或者拆成多条笔记 |
| 500 | 服务器内部错误 | 看服务端日志，响应里不会带内部细节 |
