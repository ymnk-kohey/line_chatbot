from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('個人情報')
handler = WebhookHandler('個人情報')

@app.route("/")
def test():
    return "OK"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

from time import time
users = {}
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userId = event.source.user_id
    if event.message.text == "勉強開始":
        reply_message = "計測を開始⏰します。"
        if not userId in users:
            users[userId] = {}
            users[userId]['total'] = 0
        users[userId]["start"] = time()

    elif event.message.text == "途中経過":

        end = time()
        difference = int(end - users[userId]["start"])
        users[userId]['total'] += difference

        hour = difference // 3600
        minute = (difference % 3600) // 60
        second = difference % 60

        reply_message = f"只今の勉強時間は「{hour}時間{minute}分{second}秒」経過しています。"

    elif event.message.text == "勉強終了":

        end = time()
        difference = int(end - users[userId]["start"])
        users[userId]['total'] += difference
        
        hour1 = users[userId]['total'] // 3600
        minute1 = (users[userId]['total'] % 3600) // 60
        second1 = users[userId]['total'] % 60

        reply_message = f"累計の勉強時間は「{hour1}時間{minute1}分{second1}秒」となります。お疲れ様でした、ゆっくり休んでください😆"

    else:
        if len(event.message.text) > 4:
            reply_message = "⚠️全角5文字以内で入力し、送信してください。\n送信するとStudyくんの[操作方法]を確認することができます。"

        else:
            reply_message = "Studyくん🤖は勉強時間を計測します。\n↓操作方法は①、②、③を参照してくだい。\n\n[操作方法]\n①まず初めに、勉強開始 と入力してください。入力開始から勉強時間の計測を行います。\n②現時点での時間経過を確認したい場合は、途中経過 と入力してください。\n③勉強が終了した場合は、勉強終了 と入力してくだい。\n\nさあ、頑張っていきましょう❗️"

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))


if __name__ == "__main__":
    app.run()