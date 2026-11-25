# 部署

## 直接运行

```bash
TINYNOTES_PORT=9000 TINYNOTES_DB=/var/lib/tinynotes/notes.db python -m tinynotes
```

需要 Python 3.9 以上，没有第三方依赖。

## 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TINYNOTES_PORT` | `8080` | 监听端口 |
| `TINYNOTES_DB` | `notes.db` | SQLite 数据库文件路径 |

## Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV TINYNOTES_PORT=8080 TINYNOTES_DB=/data/notes.db
EXPOSE 8080
CMD ["python", "-m", "tinynotes"]
```

```bash
docker build -t tinynotes .
docker run -d -p 8080:8080 -v tinynotes-data:/data tinynotes
```

数据库放在 `/data` 卷里，删掉容器数据也还在。改端口时，`TINYNOTES_PORT`、`EXPOSE` 和 `-p` 三处要一起改。

## 备份

SQLite 就是一个文件。两种备份办法：

1. 服务停着的时候，直接复制 `notes.db`。
2. 服务运行中，用 sqlite3 的在线备份：`sqlite3 /data/notes.db ".backup /data/notes-backup.db"`。不要在服务运行时直接复制文件，可能复制到写了一半的数据。
