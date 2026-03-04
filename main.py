import threading
from datetime import datetime

from news import request_news
from price import request_price

NEWS_INTERVAL_SECONDS = 15 * 60     # 15 minutes
PRICE_INTERVAL_SECONDS = 4 * 60 * 60  # 4 hours


def _schedule(interval: int, func, tick: list):
    """Call func now, then reschedule after interval seconds."""
    tick[0] += 1
    try:
        func(tick[0])
    except Exception as e:
        print(f'{datetime.now().isoformat()}\nerror in periodic task: {e}\n')
    t = threading.Timer(interval, _schedule, args=(interval, func, tick))
    t.daemon = True
    t.start()


def main():
    # Fetch news immediately to populate the dedup queue without sending
    request_news(first=True)

    # Schedule periodic news fetch every 15 minutes
    news_tick: list = [0]
    t = threading.Timer(NEWS_INTERVAL_SECONDS, _schedule,
                        args=(NEWS_INTERVAL_SECONDS, _news_task, news_tick))
    t.daemon = True
    t.start()

    # Fetch price immediately
    request_price()

    # Schedule periodic price fetch every 4 hours
    price_tick: list = [0]
    t = threading.Timer(PRICE_INTERVAL_SECONDS, _schedule,
                        args=(PRICE_INTERVAL_SECONDS, _price_task, price_tick))
    t.daemon = True
    t.start()

    # Keep the main thread alive
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print('Stopped.')


def _news_task(tick: int):
    print(f'News timer tick #{tick}')
    request_news()


def _price_task(tick: int):
    now = datetime.now()
    print(f'Price timer ticker at hour: {now.hour}')
    request_price()


if __name__ == '__main__':
    main()
