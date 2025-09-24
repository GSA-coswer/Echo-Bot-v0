from flask import Flask, request, abort
import os

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    RichMenuRequest,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    RichMenuAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature.")
        abort(400)

    return 'OK'


# 👉 初始化 Rich Menu，只需要手動打一次
@app.route("/init_richmenu", methods=['GET'])
def init_richmenu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 定義 Rich Menu
        rich_menu = RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="圖文選單 1",
            chat_bar_text="查看更多資訊",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=720, height=1288),
                    action=RichMenuAction(type="message", text="活動地圖")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1780, y=0, width=720, height=1288),
                    action=RichMenuAction(type="message", text="活動內容")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=720, y=0, width=1060, height=1288),
                    action=RichMenuAction(type="message", text="校園青春日")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=1288, width=834, height=398),
                    action=RichMenuAction(type="message", text="學位服")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=834, y=1288, width=833, height=398),
                    action=RichMenuAction(type="message", text="攝影方案")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1667, y=1288, width=833, height=398),
                    action=RichMenuAction(
                        type="uri",
                        uri="https://www.instagram.com/ntut_gsa/?utm_source=ig_web_button_share_sheet"
                    )
                ),
            ]
        )

        # 建立 Rich Menu
        rich_menu_id = line_bot_api.create_rich_menu(rich_menu).rich_menu_id

        # 上傳背景圖 (要確保 repo 裡有 menu.png)
        with open("menu.png", "rb") as f:
            line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)

        # 設為所有用戶的預設
        line_bot_api.set_default_rich_menu(rich_menu_id)

        return f"Rich menu created and set as default: {rich_menu_id}"


# 加好友事件
@line_handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="哈嘍同學！我終於等到你啦 🎉\n選單已經幫你打開囉 👇")]
            )
        )


# 訊息事件
@line_handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_message = event.message.text

        if "制服" in user_message:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="你🫵🏼\n就準備穿著\n「制服」or「學位服」\n來學校吧😍\n\n制服日就在：\n📆活動日期：9/24(三)\n⏰活動時間：9:00～16:00\n📍活動地點：北科大/一大川堂\n\n記得穿上\n高中職制服或大學學位服\n來拍照並留下專屬回憶 📸\n🎊 當天還有擺攤小驚喜，別錯過！"
                    )]
                )
            )


@line_handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback':
        print('Postback event is triggered')


if __name__ == "__main__":
    app.run()
