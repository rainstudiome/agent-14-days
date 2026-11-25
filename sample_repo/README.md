# tinynotes

一个很小的笔记服务：用 HTTP 接口增删查笔记，数据存在 SQLite 里。只用 Python 标准库，没有第三方依赖。

> 这是《从 0 到 1，14 天入门 Agent 开发》的练习项目。系列里的 Agent 会在它上面读代码、找答案、修 bug。

## 运行

```bash
python -m tinynotes
```

改端口、改数据库位置都用环境变量，见 `tinynotes/config.py`。

## 测试

```bash
python -m unittest discover -s tests
```

## 目录

- `tinynotes/config.py`：配置项
- `tinynotes/storage.py`：SQLite 读写
- `tinynotes/server.py`：HTTP 接口
- `tinynotes/utils.py`：小工具函数
- `docs/`：架构、接口、部署、常见问题
- `CHANGELOG.md`：版本记录
