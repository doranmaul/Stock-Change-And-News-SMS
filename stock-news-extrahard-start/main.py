import requests
from twilio.rest import Client
import datetime as dt

STOCK = "<INPUT STOCK TICKER HERE>"
COMPANY_NAME = "<INPUT FULL COMPANY NAME HERE, e.g. 'TESLA INC.'>"
ACCOUNT_SID = "<INPUT TWILIO ACCOUNT SID HERE>"
AUTH_TOKEN = "<INPUT TWILIO AUTH TOKEN HERE>"
PHONE_NUMBER = "<INPUT PHONE NUMBER TO SEND TO HERE"
TWILIO_NUMBER = "<INPUT TWILIO NUMBER HERE>"

date = dt.datetime
today = date.today()
year = today.year
month = today.month

yesterday = today.day - 1
day_before_yesterday = today.day - 2


parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": "<INPUT ALPHAVANTAGE API KEY HERE>",

}
stock_price = requests.get("https://www.alphavantage.co/query", params=parameters)
stock_price.raise_for_status()
stock_price_data = stock_price.json()

yesterday_close = stock_price_data["Time Series (Daily)"][f"{year}-{month}-{yesterday}"]["4. close"]
day_before_yesterday_close = stock_price_data["Time Series (Daily)"][f"{year}-{month}-{day_before_yesterday}"]["4. close"]

percentage_increase = 0
percentage_decrease = 0


def get_change(yesterday_2, day_before_yesterday_2):
    global percentage_increase, percentage_decrease
    if yesterday_2 == day_before_yesterday_2:
        return 0
    try:
        math = (abs(yesterday_2 - day_before_yesterday_2) / day_before_yesterday_2) * 100.0
        if yesterday_2 < day_before_yesterday_2:
            math = math * -1
            percentage_decrease = f"down {round(math, 0)}%"
            return percentage_decrease
        else:
            percentage_increase = f"up {round(math, 0)}%"
            return percentage_increase
    except ZeroDivisionError:
        return float('inf')


get_change(yesterday_2=float(yesterday_close), day_before_yesterday_2=float(day_before_yesterday_close))

news_parameters = {
    "q": COMPANY_NAME,
    "apiKey": "<INPUT NEWSAPI KEY HERE>",
}

news = requests.get("https://newsapi.org/v2/everything", params=news_parameters)
news.raise_for_status()

news_data = news.json()

news = {
    "first_news_headline": news_data["articles"][0]["title"],
    "first_news_desc": news_data["articles"][0]["description"],
    "first_news_url": news_data["articles"][0]["url"],

    "second_news_headline": news_data["articles"][1]["title"],
    "second_news_desc": news_data["articles"][1]["description"],
    "second_news_url": news_data["articles"][1]["url"],

    "third_news_headline": news_data["articles"][2]["title"],
    "third_news_desc": news_data["articles"][2]["description"],
    "third_news_url": news_data["articles"][2]["url"],
}

if yesterday_close < day_before_yesterday_close:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages \
        .create(
        body=f"{STOCK}: {percentage_decrease}\nHeadline: {news['first_news_headline']}\nBrief: {news['first_news_desc']}",
        from_=TWILIO_NUMBER,
        to=PHONE_NUMBER
    )
    print(message.status)
else:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages \
        .create(
        body=f"{STOCK}: {percentage_increase}\nHeadline: {news['first_news_headline']}\nBrief: {news['first_news_desc']}",
        from_=TWILIO_NUMBER,
        to=PHONE_NUMBER
    )
    print(message.status)

