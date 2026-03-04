以下是dart 代码

void main() {
  requestNews(first: true);
  Timer.periodic(const Duration(minutes: 15), (timer) {
    print('News timer tick #${timer.tick}');
    requestNews();
  });

  requestPrice();
  Timer.periodic(const Duration(hours: 4), (timer) {
    var now = DateTime.now();
    print('Price timer ticker at hour: ${now.hour.toString()}');
    //if (now.hour >= 8 && now.hour <= 24) {
     // print('Price timer tick #${timer.tick}');
      requestPrice();
   // }
  });
}
import 'dart:async';
import 'dart:collection';
import 'dart:convert';

import 'package:block_beats_news_lark_push/util/lark.dart';
import 'package:http/http.dart' as http;

import 'model/block_beats_news.dart';

Queue<int> msgQueue = Queue(); //为了去重

void requestNews({bool first = false}) {
  http
      .get(Uri.parse(
          'https://api.theblockbeats.news/v1/open-api/open-flash?page=1&size=10&type=all&lang=cn'))
      .then((value) {
    Message msg = Message.fromJson(json.decode(value.body));
    for (var e in msg.data!.data!) {
      if (!msgQueue.contains(e.id)) {
        msgQueue.addLast(e.id!);
        if (!first) sendLarkNews(e);
      }
      if (msgQueue.length > 100) {
        msgQueue.removeFirst();
      }
    }
  }).onError((error, stackTrace) {
    print(
        '${DateTime.now().toIso8601String()}\nerror: $error\nstackTrace: $stackTrace\n');
  });
}

sendLarkNews(Data2 e) async {
  String notice = '${e.title?.replaceAll('\n', '\\n')}\\n';
  notice += '${formatNewsContent(e.content)}\\n';
  notice += '${e.url}';
  sendLarkMsg(notice);
}

String? formatNewsContent(String? src) => src
    ?.replaceAll('\n', '\\n')
    .replaceAll('<p>', '')
    .replaceAll('</p>', '')
    .replaceAll('<br>', '\\n')
    .replaceAll('<br/>', '\\n');


import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import 'model/ticker_price_change.dart';
import 'util/lark.dart';
import 'util/num_util.dart';

void requestPrice() {
  var list = [
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
  ];
  var symbols = '%5B%22${list.join('%22,%22')}%22%5D';

  var binanceMarket = http
      .get(Uri.parse(
          'https://data-api.binance.vision/api/v3/ticker/24hr?symbols=$symbols'))
      .onError((e, s) => errResp);
  binanceMarket.then((resp) {
    List<TickerPriceChange> list = [];
    //解析binanceMarket json
    if (resp.body.isNotEmpty) {
      for (var e in json.decode(resp.body)) {
        list.add(TickerPriceChange.fromJson(e));
      }
    }


    //发送lark卡片消息
    var cardJson = '''
    {
    "elements": [
      {
        "tag": "column_set",
        "flex_mode": "none",
        "background_style": "grey",
        "columns": [
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "vertical_align": "top",
            "elements": [
              {
                "tag": "markdown",
                "content": "**交易对**",
                "text_align": "center"
              }
            ]
          },
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "vertical_align": "top",
            "elements": [
              {
                "tag": "markdown",
                "content": "**最新价**",
                "text_align": "center"
              }
            ]
          },
          {
            "tag": "column",
            "width": "weighted",
            "weight": 1,
            "vertical_align": "top",
            "elements": [
              {
                "tag": "markdown",
                "content": "**涨跌幅**",
                "text_align": "center"
              }
            ]
          }
        ]
      }
      
    ]
  }
    ''';
    var card =
        json.decode(cardJson);
    var priceElements = list.map((e) {
      bool isRise = (double.tryParse(e.priceChange ?? '0') ?? 0) >= 0;

      var priceItemJson = '''
      {
    "tag": "column_set",
    "flex_mode": "none",
    "background_style": "default",
    "columns": [
      {
        "tag": "column",
        "width": "weighted",
        "weight": 1,
        "vertical_align": "top",
        "elements": [
          {
            "tag": "markdown",
            "content": "symbol1",
            "text_align": "center"
          }
        ]
      },
      {
        "tag": "column",
        "width": "weighted",
        "weight": 1,
        "vertical_align": "top",
        "elements": [
          {
            "tag": "markdown",
            "content": "lastPrice",
            "text_align": "center"
          }
        ]
      },
      {
        "tag": "column",
        "width": "weighted",
        "weight": 1,
        "vertical_align": "top",
        "elements": [
          {
            "tag": "markdown",
            "content": "change_rate",
            "text_align": "center"
          }
        ]
      }
    ]
  }
      ''';
      Map priceItem =
          json.decode(priceItemJson);
      List columns = priceItem['columns'];
      columns[0]['elements'][0]['content'] = e.symbol ?? '--';
      columns[1]['elements'][0]['content'] = e.lastPrice?.compact ?? '--';
      columns[2]['elements'][0]['content'] =
          addColor(e.priceChangePercent?.formatPercent ?? '--', isRise);
      return priceItem;
    }).toList();
    card['elements'].addAll(priceElements);
    sendLarkCardMsg(card);
  }).onError((error, stackTrace) {
    print(
        '${DateTime.now().toIso8601String()}\nerror: $error\nstackTrace: $stackTrace\n');
  });
}

http.Response get errResp => http.Response('', 9999);

String addColor(String content, bool isRise) {
  return isRise
      ? '<font color=\'green\'>$content</font>'
      : '<font color=\'red\'>$content</font>';
}



import 'dart:convert';

import 'package:http/http.dart' as http;

final debug = false;

void sendLarkMsg(String msg) async {
  Map<String, dynamic> params = {"msg_type": "text"};
  params["content"] = '{"text":"$msg"}';
  send(params);
}

void sendLarkCardMsg(dynamic card) {
  print('#fwd# sendLarkCardMsg， card= $card');
  Map<String, dynamic> params = {"msg_type": "interactive"};
  params["card"] = card;
  send(params);
}

void send(Map<String, dynamic> params) async {
  print('--> [Lark] $params');
  String url =
      'https://open.larksuite.com/open-apis/bot/v2/hook/950542f4-6cf2-47d1-ad5b-9305f1045ae9';
  String debugUrl =
      'https://open.larksuite.com/open-apis/bot/v2/hook/fcf7033e-e493-4cb2-834b-20aafe62135a'; //testGroup
  http
      .post(
    Uri.parse(debug ? debugUrl : url),
    headers: {'Content-Type': 'application/json; charset=UTF-8'},
    body: json.encode(params),
  )
      .then((res) {
    print('<--  [Lark] ${res.body}');
  }).catchError((e, s) {
    print('$e\n$s');
  });
}


extension NumStringExtension on String {
  String get compact => _removeUselessTailZero();

  String _removeUselessTailZero() {
    if (this.isEmpty || double.tryParse(this) == null) {
      return this;
    }
    if (this.contains('.')) {
      var list = this.split('.');
      var tail = list[1];
      var index = tail.length - 1;
      while (index >= 0) {
        if (tail[index] == '0') {
          index--;
        } else {
          break;
        }
      }
      if (index == -1) {
        return list[0];
      } else {
        return '${list[0]}.${tail.substring(0, index + 1)}';
      }
    } else {
      return this;
    }
  }

  String get formatPercent {
    var value = double.tryParse(this);
    if (value == null) {
      return '--';
    }
    //保留两位小数
    return '${value > 0 ? '+' : ''}${value.toStringAsFixed(2)}%';
  }
}


class Message {
  int? status;
  String? message;
  Data? data;

  Message({this.status, this.message, this.data});

  Message.fromJson(Map<String, dynamic> json) {
    status = json['status'];
    message = json['message'];
    data = json['data'] != null ? Data.fromJson(json['data']) : null;
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = <String, dynamic>{};
    data['status'] = status;
    data['message'] = message;
    if (this.data != null) {
      data['data'] = this.data!.toJson();
    }
    return data;
  }
}

class Data {
  int? page;
  List<Data2>? data;

  Data({this.page, this.data});

  Data.fromJson(Map<String, dynamic> json) {
    page = json['page'];
    if (json['data'] != null) {
      data = <Data2>[];
      json['data'].forEach((v) {
        data!.add(Data2.fromJson(v));
      });
    }
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = <String, dynamic>{};
    data['page'] = page;
    if (this.data != null) {
      data['data'] = this.data!.map((v) => v.toJson()).toList();
    }
    return data;
  }
}

class Data2 {
  int? id;
  String? title;
  String? content;
  String? pic;
  String? link;
  String? url;
  String? createTime;

  Data2(
      {this.id,
      this.title,
      this.content,
      this.pic,
      this.link,
      this.url,
      this.createTime});

  Data2.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    title = json['title'];
    content = json['content'];
    pic = json['pic'];
    link = json['link'];
    url = json['url'];
    createTime = json['create_time'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = <String, dynamic>{};
    data['id'] = id;
    data['title'] = title;
    data['content'] = content;
    data['pic'] = pic;
    data['link'] = link;
    data['url'] = url;
    data['create_time'] = createTime;
    return data;
  }
}


import 'dart:math';

class TickerPriceChange {
  String? symbol;
  String? priceChange;
  String? priceChangePercent;
  String? weightedAvgPrice;
  String? prevClosePrice;
  String? lastPrice;
  String? lastQty;
  String? bidPrice;
  String? bidQty;
  String? askPrice;
  String? askQty;
  String? openPrice;
  String? highPrice;
  String? lowPrice;
  String? volume;
  String? quoteVolume;
  int? openTime;
  int? closeTime;
  int? firstId;
  int? lastId;
  int? count;

  TickerPriceChange(
      {this.symbol,
      this.priceChange,
      this.priceChangePercent,
      this.weightedAvgPrice,
      this.prevClosePrice,
      this.lastPrice,
      this.lastQty,
      this.bidPrice,
      this.bidQty,
      this.askPrice,
      this.askQty,
      this.openPrice,
      this.highPrice,
      this.lowPrice,
      this.volume,
      this.quoteVolume,
      this.openTime,
      this.closeTime,
      this.firstId,
      this.lastId,
      this.count});

  TickerPriceChange.fromJson(Map<String, dynamic> json) {
    symbol = json['symbol'];
    priceChange = json['priceChange'];
    priceChangePercent = json['priceChangePercent'];
    weightedAvgPrice = json['weightedAvgPrice'];
    prevClosePrice = json['prevClosePrice'];
    lastPrice = json['lastPrice'];
    lastQty = json['lastQty'];
    bidPrice = json['bidPrice'];
    bidQty = json['bidQty'];
    askPrice = json['askPrice'];
    askQty = json['askQty'];
    openPrice = json['openPrice'];
    highPrice = json['highPrice'];
    lowPrice = json['lowPrice'];
    volume = json['volume'];
    quoteVolume = json['quoteVolume'];
    openTime = json['openTime'];
    closeTime = json['closeTime'];
    firstId = json['firstId'];
    lastId = json['lastId'];
    count = json['count'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['symbol'] = this.symbol;
    data['priceChange'] = this.priceChange;
    data['priceChangePercent'] = this.priceChangePercent;
    data['weightedAvgPrice'] = this.weightedAvgPrice;
    data['prevClosePrice'] = this.prevClosePrice;
    data['lastPrice'] = this.lastPrice;
    data['lastQty'] = this.lastQty;
    data['bidPrice'] = this.bidPrice;
    data['bidQty'] = this.bidQty;
    data['askPrice'] = this.askPrice;
    data['askQty'] = this.askQty;
    data['openPrice'] = this.openPrice;
    data['highPrice'] = this.highPrice;
    data['lowPrice'] = this.lowPrice;
    data['volume'] = this.volume;
    data['quoteVolume'] = this.quoteVolume;
    data['openTime'] = this.openTime;
    data['closeTime'] = this.closeTime;
    data['firstId'] = this.firstId;
    data['lastId'] = this.lastId;
    data['count'] = this.count;
    return data;
  }

  static TickerPriceChange fromAvascriptionsJson(e, avaxPrice) {
    var priceByAvax =
        double.parse(e['floorPrice']) * e['perMint'] * pow(0.1, 18);
    var priceByUsdt = double.parse(avaxPrice) * priceByAvax;
    return TickerPriceChange(
      symbol: e['tick'].toUpperCase(),
      lastPrice: (priceByAvax.toStringAsFixed(4) +
          ' / \$' +
          priceByUsdt.toStringAsFixed(2)),
      priceChange: '0',
      priceChangePercent: '--',
    );
  }
}

