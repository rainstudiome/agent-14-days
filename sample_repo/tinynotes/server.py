"""HTTP 接口。用标准库的 http.server，不依赖任何 Web 框架。

路由：
    GET    /health          健康检查
    GET    /notes?page=1    分页列出笔记
    POST   /notes           新建笔记，请求体是 JSON：{"body": "正文"}
    GET    /notes/<id>      查看一条笔记
    DELETE /notes/<id>      删除一条笔记
    GET    /search?q=关键词  搜索笔记

请求体的检查放在文件末尾的 _read_json_body 和 _validate_note 里。
"""
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import __version__, config, storage
from .utils import make_title

NOTE_PATH = re.compile(r"^/notes/(\d+)$")


class ApiError(Exception):
    """接口错误：带上 HTTP 状态码和给调用方看的说明。"""

    def __init__(self, status: HTTPStatus, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class Handler(BaseHTTPRequestHandler):
    """每个请求一个实例。数据库连接在 main() 里创建，挂在 server 上共享。"""

    server_version = f"tinynotes/{__version__}"

    # ---------- 路由 ----------

    def do_GET(self) -> None:
        self._dispatch(self._route_get)

    def do_POST(self) -> None:
        self._dispatch(self._route_post)

    def do_DELETE(self) -> None:
        self._dispatch(self._route_delete)

    def _route_get(self) -> tuple[HTTPStatus, object]:
        url = urlparse(self.path)
        if url.path == "/health":
            return HTTPStatus.OK, {"status": "ok", "version": __version__}
        if url.path == "/notes":
            page = _int_param(parse_qs(url.query), "page", default=1)
            return HTTPStatus.OK, {"page": page, "notes": storage.list_notes(self.db, page)}
        if url.path == "/search":
            keyword = parse_qs(url.query).get("q", [""])[0].strip()
            if not keyword:
                raise ApiError(HTTPStatus.BAD_REQUEST, "缺少查询参数 q")
            return HTTPStatus.OK, {"q": keyword, "notes": storage.search_notes(self.db, keyword)}
        match = NOTE_PATH.match(url.path)
        if match:
            note = storage.get_note(self.db, int(match.group(1)))
            if note is None:
                raise ApiError(HTTPStatus.NOT_FOUND, "笔记不存在")
            return HTTPStatus.OK, note
        raise ApiError(HTTPStatus.NOT_FOUND, "没有这个接口")

    def _route_post(self) -> tuple[HTTPStatus, object]:
        if urlparse(self.path).path != "/notes":
            raise ApiError(HTTPStatus.NOT_FOUND, "没有这个接口")
        data = _read_json_body(self)
        body = _validate_note(data)
        note_id = storage.add_note(self.db, make_title(body), body)
        return HTTPStatus.CREATED, storage.get_note(self.db, note_id)

    def _route_delete(self) -> tuple[HTTPStatus, object]:
        match = NOTE_PATH.match(urlparse(self.path).path)
        if not match:
            raise ApiError(HTTPStatus.NOT_FOUND, "没有这个接口")
        if not storage.delete_note(self.db, int(match.group(1))):
            raise ApiError(HTTPStatus.NOT_FOUND, "笔记不存在")
        return HTTPStatus.OK, {"deleted": int(match.group(1))}

    # ---------- 公共部分 ----------

    @property
    def db(self):
        return self.server.db  # type: ignore[attr-defined]

    def _dispatch(self, route) -> None:
        try:
            status, payload = route()
        except ApiError as e:
            status, payload = e.status, {"error": e.message}
        except Exception:  # 预料之外的错误：不把内部细节返回给调用方
            self.log_exception()
            status, payload = HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "服务器内部错误"}
        self._send_json(status, payload)

    def _send_json(self, status: HTTPStatus, payload: object) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_exception(self) -> None:
        import traceback

        traceback.print_exc()


def _int_param(query: dict, name: str, default: int) -> int:
    try:
        return int(query.get(name, [default])[0])
    except ValueError:
        raise ApiError(HTTPStatus.BAD_REQUEST, f"参数 {name} 必须是整数") from None


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", config.PORT), Handler)
    server.db = storage.connect()  # type: ignore[attr-defined]
    print(f"tinynotes {__version__} 正在监听 {config.PORT} 端口")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


# ---------- 请求体检查 ----------


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    """读请求体并解析成 JSON 对象。

    请求体超过 config.MAX_BODY_BYTES 时返回 413（Payload Too Large），
    不是合法的 JSON 对象时返回 400。
    """
    length = int(handler.headers.get("Content-Length") or 0)
    if length > config.MAX_BODY_BYTES:
        raise ApiError(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "请求体太大")
    raw = handler.rfile.read(length)
    try:
        data = json.loads(raw or b"{}")
    except json.JSONDecodeError:
        raise ApiError(HTTPStatus.BAD_REQUEST, "请求体不是合法的 JSON") from None
    if not isinstance(data, dict):
        raise ApiError(HTTPStatus.BAD_REQUEST, "请求体必须是 JSON 对象")
    return data


def _validate_note(data: dict) -> str:
    """检查笔记正文，返回去掉首尾空白的正文。

    - 没有 body 字段或者正文为空：400（Bad Request）
    - 正文超过 config.MAX_NOTE_LENGTH 个字符：422（Unprocessable Entity）
    """
    body = data.get("body")
    if not isinstance(body, str) or not body.strip():
        raise ApiError(HTTPStatus.BAD_REQUEST, "缺少笔记正文 body")
    body = body.strip()
    if len(body) > config.MAX_NOTE_LENGTH:
        raise ApiError(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            f"笔记太长：最多 {config.MAX_NOTE_LENGTH} 个字符，现在是 {len(body)} 个",
        )
    return body
