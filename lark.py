import json
import requests

DEBUG = False

LARK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/950542f4-6cf2-47d1-ad5b-9305f1045ae9'
LARK_DEBUG_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/fcf7033e-e493-4cb2-834b-20aafe62135a'


def send_lark_msg(msg: str):
    params = {
        'msg_type': 'text',
        'content': json.dumps({'text': msg}),
    }
    _send(params)


def send_lark_card_msg(card):
    print(f'#fwd# send_lark_card_msg, card= {card}')
    params = {
        'msg_type': 'interactive',
        'card': card,
    }
    _send(params)


def _send(params: dict):
    print(f'--> [Lark] {params}')
    url = LARK_DEBUG_URL if DEBUG else LARK_URL
    try:
        res = requests.post(
            url,
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            data=json.dumps(params, ensure_ascii=False).encode('utf-8'),
        )
        print(f'<--  [Lark] {res.text}')
    except Exception as e:
        print(e)
