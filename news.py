import json
from collections import deque
from datetime import datetime

import requests

from lark import send_lark_msg
from models import Message

msg_queue: deque = deque(maxlen=100)  # dedup queue, keeps last 100 ids


def request_news(first: bool = False):
    try:
        resp = requests.get(
            'https://api.theblockbeats.news/v1/open-api/open-flash'
            '?page=1&size=10&type=all&lang=cn'
        )
        msg = Message.from_json(json.loads(resp.text))
        for e in (msg.data.data or []):
            if e.id not in msg_queue:
                msg_queue.append(e.id)
                if not first:
                    _send_lark_news(e)
    except Exception as e:
        print(f'{datetime.now().isoformat()}\nerror: {e}\n')


def _send_lark_news(e):
    notice = f'{_escape_newlines(e.title)}\\n'
    notice += f'{_format_news_content(e.content)}\\n'
    notice += f'{e.url}'
    send_lark_msg(notice)


def _format_news_content(src: str) -> str:
    if src is None:
        return ''
    return (
        src.replace('\n', '\\n')
           .replace('<p>', '')
           .replace('</p>', '')
           .replace('<br>', '\\n')
           .replace('<br/>', '\\n')
    )


def _escape_newlines(src: str) -> str:
    if src is None:
        return ''
    return src.replace('\n', '\\n')
