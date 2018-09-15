# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import random
import os
import sys
import requests
import urllib.request
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from googletrans import Translator
from weather import Weather, Unit

weather = Weather(unit=Unit.CELSIUS)
translator= Translator()
ans=random.sample(range(10),4)
a=0
b=0
game=1
max=0
min=0
guessCount=0
guessAnswer=0
guessNum=0
wea=''


from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)



# get channel_secret and channel_access_token from your environment variable
#channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
#channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
#if channel_secret is None:
#    print('Specify LINE_CHANNEL_SECRET as environment variable.')
#    sys.exit(1)
#if channel_access_token is None:
#    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
#    sys.exit(1)

channel_secret='1cf9aec0b1ab9aa1071e415518fd5a57'
channel_access_token='zSdvYfnQcuibHS9rtJQpyNCAIkqrJdnqpZyJpzbU4NUhRgOq3QAk3cqQy3pRyWz76JdtsAAfPw5vfrQzO9WMwWsVFydimDsGS85lzc5CGGKzZXqGFMP+IQwgfOz/guhB0dbyInUTLh5asspZWAAuIgdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@app.route("/callback", methods=['POST'])



def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        msg = event.message.text

        global game
        global a
        global b
        global ans
        global min
        global max
        global guessNum
        global guessAnswer
        global wea

        typ = sys.getfilesystemencoding()

        if msg[:4] == '天氣預報':
             location = weather.lookup_by_location(msg[4:])
             forecasts = location.forecast
             for forecast in forecasts:
                 if forecast.text == 'Thunderstorms':
                    met=forecast.text[0:-1]
                 else:
                     met=forecast.text
                 translation = translator.translate(met.lower(),dest='zh-tw')
                 wea=wea+'\n日期: '+forecast.date+'\n氣象: '+translation.text+'\n最高氣溫: '+forecast.high+'℃'+'\n最低氣溫: '+forecast.low+'℃\n'
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg[4:]+ "地區一周的天氣為: "+wea))


        if msg[:4] == '天氣氣溫':
             lookup = weather.lookup_by_latlng(msg[4:],'zh-tw')
             condition = lookup.condition
             weat = ''
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg[4:]+"目前氣溫為: "+condition.temp +'℃'))
        if msg[:2] == '翻譯':
             if msg[3:5] == 'zh':
                lan = 'zh-tw'
             else:
                lan = msg[3:5]
             tran_text = msg[5:]
             translation = translator.translate(tran_text,dest=lan)     #使用套件去翻譯
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text="翻譯的結果為: "+translation.text))

        if '猜數字' in msg:
           game=3
           line_bot_api.reply_message(event.reply_token, TextSendMessage(text="開始猜數字"))
           max=100
           min=0
           guessCount=0
           guessAnswer=random.randint(1,99)
           guessNum=0


        if (game==3):
           if "改題目" in msg:
                 guessAnswer=random.randint(1,99)
                 line_bot_api.reply_message(event.reply_token, TextSendMessage(text="改好了"))
           if "答案" in msg:
                 line_bot_api.reply_message(event.reply_token, TextSendMessage(text="猜數字的答案為:"+ str(guessAnswer)))
           if "結束" in msg:
                game=1
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="OVER GAME"))
           if msg.isdigit():
                if  int(msg) > min and int(msg) < max:
                    guessNum+=1
                    if (int(msg) > guessAnswer):
                       print("再小一點")
                       max=int(msg)
                       line_bot_api.reply_message(event.reply_token,TextSendMessage(text="再小一點\n"+"已猜次數"+str(guessNum)+'\n'+ str(min)  +'< ans <'+str(max) ))
                       print(max)
                    if (int(msg) < guessAnswer):
                       print("再大一點")
                       min=int(msg)
                       line_bot_api.reply_message(event.reply_token,TextSendMessage(text="再大一點\n"+"已猜次數"+str(guessNum)+'\n'+ str(min)  +'< ans <'+str(max)))
                    if (int(msg) == guessAnswer) :
                       line_bot_api.reply_message(event.reply_token,TextSendMessage(text="恭喜答對\n"+"已猜次數"+str(guessNum)))
                       game=1
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="錯誤範圍"))


        if "1A2B" in msg:
            game=2
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="開始1A2B"))
            ans=random.sample(range(10),4)
        if(game==2):
            a=0
            b=0
            if "改題目" in msg:
               ans=random.sample(range(10),4)
               line_bot_api.reply_message(event.reply_token, TextSendMessage(text="改好了"))
            if "結束" in msg:
                game=1
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="OVER GAME"))
#           if(a==4):
#                game=1
#                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="OVER GAME"))

            if "ans" in msg:
                 for i in range(0,4):
                     if(int(ans[i])==int(msg[i+3])):
                         a=a+1

                     for j in range(0,4):
                         if(i!=j):
                             if(int(msg[i+3])==int(ans[j])):
                                 b=b+1
                 if(a==4):
                     game=1
                     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(a)+"A"+str(b)+"B"+",結束遊戲"))

                 line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(a)+"A"+str(b)+"B"))
                 a=0
                 b=0

#

            if "答案" in msg:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(ans)))
#           for i in range(0,4):
#              if(int(ans[i])==int(msg[i])):
#                  a=a+1
#              if(int(ans[0])==int(msg[0])):
#                  a=1
            if "aa" in msg:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(a)))
            if "結束" in msg:
                game=1
#           if (msg=="game"):
#               line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(game)))



        if '頭條' in msg :
           url = 'https://today.line.me/TW/pc/popular/100259'
           res = requests.get(url)
           res.encoding = 'UTF-8'
           line_news=""
           soup = BeautifulSoup(res.text, 'html.parser')
           for news in soup.select('.txt '):
               h2 = news.select('p')
           for i in range(0,6):
               if i>0:
                  line_news=line_news+soup.select('.txt ')[i].text
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text=line_news))

        if '運動' in msg :
           url = 'https://today.line.me/TW/pc/popular/100265'
           res = requests.get(url)
           res.encoding = 'UTF-8'
           soup = BeautifulSoup(res.text, 'html.parser')
           line_news=""
           for news in soup.select('.txt '):
               h2 = news.select('p')
           for i in range(0,6):
               if i>0:
                  line_news=line_news+soup.select('.txt ')[i].text
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text=line_news))

        if '娛樂' in msg :
           url = 'https://today.line.me/TW/pc/popular/100260'
           res = requests.get(url)
           res.encoding = 'UTF-8'
           soup = BeautifulSoup(res.text, 'html.parser')
           for news in soup.select('.txt '):
              h2 = news.select('p')
           for i in range(0,6):
              if i>0:
                 line_news=line_news+soup.select('.txt ')[i].text
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text=line_news))

        if '國內' in msg :
           url = 'https://today.line.me/TW/pc/popular/100262'
           res = requests.get(url)
           res.encoding = 'UTF-8'
           soup = BeautifulSoup(res.text, 'html.parser')
           line_news=""
           for news in soup.select('.txt '):
              h2 = news.select('p')
           for i in range(0,6):
              if i>0:
                 line_news=line_news+soup.select('.txt ')[i].text
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text=line_news))

        if '生活' in msg :
           url = 'https://today.line.me/TW/pc/popular/100264'
           res = requests.get(url)
           res.encoding = 'UTF-8'
           soup = BeautifulSoup(res.text, 'html.parser')
           line_news=""
           for news in soup.select('.txt '):
              h2 = news.select('p')
           for i in range(0,6):
              if i>0:
                 line_news=line_news+soup.select('.txt ')[i].text
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text=line_news))

        if '國際' in msg :
           url = 'https://today.line.me/TW/pc/popular/100267'
           res = requests.get(url)
           res.encoding = 'UTF-8'
           soup = BeautifulSoup(res.text, 'html.parser')
           line_news=""
           for news in soup.select('.txt '):
              h2 = news.select('p')
           for i in range(0,6):
              if i>0:
                 line_news=line_news+soup.select('.txt ')[i].text
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text=line_news))

        if 'id' in msg :
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text='252461504'))

        if 'line' in msg :
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text='eric21364'))

        if 'fb' in msg :
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text='https://www.facebook.com/eric21364'))

        if '早安' in msg :
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text='Hola!!!!!'))

        if '包大人' in msg :
           line_bot_api.reply_message(event.reply_token,TextSendMessage(text='威~~~~~武~~~~~~~~~~~~~~~~~!'))


    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)

