from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessageContent
)

import os

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# 加入好友事件
@line_handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="哈嘍同學！我終於等到你啦 🎉\n\n你🫵🏼\n快畢業了吧？\n還是你假裝是畢業生？\n或是你準備當「岩壁戰士」了☹️\n不管怎樣，都歡迎加入我們❤️‍🔥\n\n🫵🏼跟你正式介紹一下：\n我們是「畢業學生聯誼會」(畢聯會)\n\n✨我們負責：\n1️⃣ 辦理畢業生的各種活動\n（畢業舞會、畢業典禮…等等）\n2️⃣ 『訂購學位服』相關事項\n3️⃣ 協助解答畢業生的疑問\n\n💡小彩蛋提示：\n偶爾也會丟點小梗、搞笑互動\n讓你笑著迎接畢業 🎊\n\n有任何問題都可以隨時問我們！\n記得準時 follow 最新資訊\n各式活動、精彩回憶都別錯過啦 💖")]
            )
        )

# 訊息事件
@line_handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_message = event.message.text
        # Reply message
        if "制服" in user_message:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text ='你🫵🏼\n就準備穿著\n「制服」or「學位服」\n來學校吧😍\n我會恨帥潮還會恨美潮的🤧\n\n制服日就在：\n📆活動日期：9/24(三)\n⏰活動時間：9:00～16:00\n📍活動地點：北科大/一大川堂\n\n記得穿上\n高中職制服或大學學位服\n來拍照並留下專屬回憶 📸\n🎊 當天還有擺攤小驚喜，別錯過！')]
                )
            )

#圖文訊息事件
@line_handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_message = event.message.text
        # Reply message
        if "制服" in user_message:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        ImageMessage(
                            original_content_url="https://github.com/GSA-coswer/Echo-Bot-v0/blob/main/%E6%B4%BB%E5%8B%95%E5%9C%B0%E5%9C%96.jpg?raw=true",
                            preview_image_url="https://github.com/GSA-coswer/Echo-Bot-v0/blob/main/%E6%B4%BB%E5%8B%95%E5%9C%B0%E5%9C%96.jpg?raw=true"
                        )
                    ]
                )
            )


@line_handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback':
        print('Postback event is triggered')


if __name__ == "__main__":
    app.run()
