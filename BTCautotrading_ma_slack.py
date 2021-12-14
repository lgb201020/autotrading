import time
import pyupbit
import datetime
import requests

#algorithm봇 토큰

access = "r8O17xzMiEBlgTznKrPxj6d1JtGcLMJhOcI2GLhj"
secret = "h2R0NkwZBg7YMJzPFE5XawoDzh2K9ZKtQdU4ILmO"
myToken = "xoxb-2032756729879-2132589771234-ac8ffH1Bc5L9sR3faaFrff4i"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = pyupbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.43)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken,"#autotrade-no-ai-only-algorithm", "BTC buy : " +str(buy_result))
        else:
            btc = get_balance("BTC")
            btcprice = get_current_price("KRW-BTC")
            mybalance = btc * btcprice
            if mybalance > 5000:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                post_message(myToken,"#autotrade-no-ai-only-algorithm", "BTC sell : " +str(sell_result))

        time.sleep(1)
    except Exception as e:
        print(e)
        
        post_message(myToken,"#autotrade-no-ai-only-algorithm", "오류가 났습니다." )

        time.sleep(1)