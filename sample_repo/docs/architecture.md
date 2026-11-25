# 架构

tinynotes 分三层，每层一个文件：

| 层 | 文件 | 做什么 |
|---|---|---|
| 接口层 | `tinynotes/server.py` | 解析 HTTP 请求、检查参数、返回 JSON |
| 存储层 | `tinynotes/storage.py` | 用 SQLite 存取笔记 |
| 工具函数 | `tinynotes/utils.py` | 截断文本、生成标题 |

配置集中在 `tinynotes/config.py`。

## 一次请求的流程

以新建笔记为例：

1. `server.Handler.do_POST` 收到请求，交给 `_route_post`。
2. `_read_json_body` 读请求体并解析 JSON；`_validate_note` 检查正文。
3. `utils.make_title` 用正文第一行生成标题。
4. `storage.add_note` 写入数据库，返回新笔记的 id。
5. 接口层把新笔记转成 JSON 返回，状态码 201。

## 数据表

只有一张表 `notes`：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 主键，自增 |
| title | TEXT | 标题，由正文第一行生成 |
| body | TEXT | 正文 |
| created_at | TEXT | 创建时间，本地时间，ISO 8601 格式 |

## 并发

服务用 `ThreadingHTTPServer`，每个请求一个线程，所有线程共用一个 SQLite 连接（`check_same_thread=False`）。笔记服务写入量很小，这样够用；写入量大的话要换成连接池或者别的数据库。
