class Data2:
    def __init__(self, id=None, title=None, content=None, pic=None, link=None, url=None, create_time=None):
        self.id = id
        self.title = title
        self.content = content
        self.pic = pic
        self.link = link
        self.url = url
        self.create_time = create_time

    @classmethod
    def from_json(cls, json):
        return cls(
            id=json.get('id'),
            title=json.get('title'),
            content=json.get('content'),
            pic=json.get('pic'),
            link=json.get('link'),
            url=json.get('url'),
            create_time=json.get('create_time'),
        )


class Data:
    def __init__(self, page=None, data=None):
        self.page = page
        self.data = data  # list of Data2

    @classmethod
    def from_json(cls, json):
        data_list = None
        if json.get('data') is not None:
            data_list = [Data2.from_json(v) for v in json['data']]
        return cls(page=json.get('page'), data=data_list)


class Message:
    def __init__(self, status=None, message=None, data=None):
        self.status = status
        self.message = message
        self.data = data  # Data instance

    @classmethod
    def from_json(cls, json):
        data = Data.from_json(json['data']) if json.get('data') else None
        return cls(status=json.get('status'), message=json.get('message'), data=data)


class TickerPriceChange:
    def __init__(self, symbol=None, price_change=None, price_change_percent=None,
                 weighted_avg_price=None, prev_close_price=None, last_price=None,
                 last_qty=None, bid_price=None, bid_qty=None, ask_price=None,
                 ask_qty=None, open_price=None, high_price=None, low_price=None,
                 volume=None, quote_volume=None, open_time=None, close_time=None,
                 first_id=None, last_id=None, count=None):
        self.symbol = symbol
        self.price_change = price_change
        self.price_change_percent = price_change_percent
        self.weighted_avg_price = weighted_avg_price
        self.prev_close_price = prev_close_price
        self.last_price = last_price
        self.last_qty = last_qty
        self.bid_price = bid_price
        self.bid_qty = bid_qty
        self.ask_price = ask_price
        self.ask_qty = ask_qty
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.volume = volume
        self.quote_volume = quote_volume
        self.open_time = open_time
        self.close_time = close_time
        self.first_id = first_id
        self.last_id = last_id
        self.count = count

    @classmethod
    def from_json(cls, json):
        return cls(
            symbol=json.get('symbol'),
            price_change=json.get('priceChange'),
            price_change_percent=json.get('priceChangePercent'),
            weighted_avg_price=json.get('weightedAvgPrice'),
            prev_close_price=json.get('prevClosePrice'),
            last_price=json.get('lastPrice'),
            last_qty=json.get('lastQty'),
            bid_price=json.get('bidPrice'),
            bid_qty=json.get('bidQty'),
            ask_price=json.get('askPrice'),
            ask_qty=json.get('askQty'),
            open_price=json.get('openPrice'),
            high_price=json.get('highPrice'),
            low_price=json.get('lowPrice'),
            volume=json.get('volume'),
            quote_volume=json.get('quoteVolume'),
            open_time=json.get('openTime'),
            close_time=json.get('closeTime'),
            first_id=json.get('firstId'),
            last_id=json.get('lastId'),
            count=json.get('count'),
        )
