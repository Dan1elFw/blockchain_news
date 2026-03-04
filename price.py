import copy
import json
from datetime import datetime
from urllib.parse import quote

import requests

from lark import send_lark_card_msg
from models import TickerPriceChange
from num_util import compact, format_percent

SYMBOLS = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT',
    'SOLUSDT',
    'XRPUSDT',
    'ADAUSDT',
    'AVAXUSDT',
    'DOGEUSDT',
    'SHIBUSDT',
    'TRXUSDT',
    'TRUMPUSDT',
]

_CARD_TEMPLATE = {
    'elements': [
        {
            'tag': 'column_set',
            'flex_mode': 'none',
            'background_style': 'grey',
            'columns': [
                {
                    'tag': 'column',
                    'width': 'weighted',
                    'weight': 1,
                    'vertical_align': 'top',
                    'elements': [{'tag': 'markdown', 'content': '**交易对**', 'text_align': 'center'}],
                },
                {
                    'tag': 'column',
                    'width': 'weighted',
                    'weight': 1,
                    'vertical_align': 'top',
                    'elements': [{'tag': 'markdown', 'content': '**最新价**', 'text_align': 'center'}],
                },
                {
                    'tag': 'column',
                    'width': 'weighted',
                    'weight': 1,
                    'vertical_align': 'top',
                    'elements': [{'tag': 'markdown', 'content': '**涨跌幅**', 'text_align': 'center'}],
                },
            ],
        }
    ]
}

_PRICE_ITEM_TEMPLATE = {
    'tag': 'column_set',
    'flex_mode': 'none',
    'background_style': 'default',
    'columns': [
        {
            'tag': 'column',
            'width': 'weighted',
            'weight': 1,
            'vertical_align': 'top',
            'elements': [{'tag': 'markdown', 'content': '', 'text_align': 'center'}],
        },
        {
            'tag': 'column',
            'width': 'weighted',
            'weight': 1,
            'vertical_align': 'top',
            'elements': [{'tag': 'markdown', 'content': '', 'text_align': 'center'}],
        },
        {
            'tag': 'column',
            'width': 'weighted',
            'weight': 1,
            'vertical_align': 'top',
            'elements': [{'tag': 'markdown', 'content': '', 'text_align': 'center'}],
        },
    ],
}


def request_price():
    symbols_param = quote(json.dumps(SYMBOLS))
    ticker_list = []
    try:
        resp = requests.get(
            f'https://data-api.binance.vision/api/v3/ticker/24hr?symbols={symbols_param}'
        )
        if resp.text:
            for e in json.loads(resp.text):
                ticker_list.append(TickerPriceChange.from_json(e))
    except Exception as e:
        print(f'{datetime.now().isoformat()}\nerror: {e}\n')

    card = copy.deepcopy(_CARD_TEMPLATE)
    price_elements = []
    for e in ticker_list:
        is_rise = (float(e.price_change or '0') >= 0)
        item = copy.deepcopy(_PRICE_ITEM_TEMPLATE)
        columns = item['columns']
        columns[0]['elements'][0]['content'] = e.symbol or '--'
        columns[1]['elements'][0]['content'] = compact(e.last_price) if e.last_price else '--'
        columns[2]['elements'][0]['content'] = _add_color(
            format_percent(e.price_change_percent) if e.price_change_percent else '--',
            is_rise,
        )
        price_elements.append(item)
    card['elements'].extend(price_elements)
    send_lark_card_msg(card)


def _add_color(content: str, is_rise: bool) -> str:
    color = 'green' if is_rise else 'red'
    return f"<font color='{color}'>{content}</font>"
