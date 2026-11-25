"""tinynotes 的配置。带环境变量的项，都可以在启动时覆盖。"""
import os

# 服务监听的端口
PORT = int(os.environ.get("TINYNOTES_PORT", "8080"))

# SQLite 数据库文件的位置
DB_PATH = os.environ.get("TINYNOTES_DB", "notes.db")

# 一条笔记正文最多多少个字符
MAX_NOTE_LENGTH = 2000

# 列表接口每页返回多少条
PAGE_SIZE = 20

# 请求体最多多少字节
MAX_BODY_BYTES = 64 * 1024

# 标题最多多少个字符，见 utils.make_title
TITLE_LENGTH = 30
