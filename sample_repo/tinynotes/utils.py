"""一些小工具函数。"""
from . import config


def truncate(text: str, limit: int) -> str:
    """把文本截到最多 limit 个字符。

    被截断时，末尾加一个省略号"…"，省略号也算在 limit 里。
    """
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def make_title(body: str) -> str:
    """用正文的第一行做标题，最多 config.TITLE_LENGTH 个字符。正文为空时标题是"无标题"。"""
    lines = body.strip().splitlines()
    if not lines:
        return "无标题"
    return truncate(lines[0].strip(), config.TITLE_LENGTH)
