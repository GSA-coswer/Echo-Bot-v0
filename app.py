import os
from flask import Flask, request, abort
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

# ---------- 建立圖文選單 ----------
def create_rich_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        rich_menu = RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="圖文選單 1",
            chat_bar_text="查看更多資訊",
            areas=[
                RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=720, height=1288),
                             action=RichMenuAction(type="message", text="活動地圖")),
                RichMenuArea(bounds=RichMenuBounds(x=1780, y=0, width=720, height=1288),
                             action=RichMenuAction(type="message", text="活動內容")),
                RichMenuArea(bounds=RichMenuBounds(x=720, y=0, width=1060, height=1288),
                             action=RichMenuAction(type="message", text="校園青春日")),
                RichMenuArea(bounds=RichMenuBounds(x=0, y=1288, width=834, height=398),
                             action=RichMenuAction(type="message", text="學位服")),
                RichMenuArea(bounds=RichMenuBounds(x=834, y=1288, width=833, height=398),
                             action=RichMenuAction(type="message", text="攝影方案")),
                RichMenuArea(bounds=RichMenuBounds(x=1667, y=1288, width=833, height=398),
                             action=RichMenuAction(
                                 type="uri",
                                 uri="https://www.instagram.com/ntut_gsa/?utm_source=ig_web_button_share_sheet"
                             ))
            ]
        )

        result = line_bot_api.create_rich_menu(rich_menu=rich_menu)
        rich_menu_id = result.rich_menu_id
        print("✅ RichMenu 建立成功:", rich_menu_id)

        # 上傳圖片
        with open("menu.png", 'rb') as f:
            line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
            print("✅ 圖片上傳完成！")

        # 設為預設選單
        line_bot_api.set_default_rich_menu(rich_menu_id)
        print("✅ 已設定為預設圖文選單！")


# ---------- 啟動時建立圖文選單（可用旗標控制） ----------
if os.getenv("SETUP_RICHMENU", "false").lower() == "true":
    create_rich_menu()


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


@line_handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="哈嘍同學！我終於等到你啦 🎉\n\n(這裡是歡迎訊息...)")]
            )
        )

@line_handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_message = event.message.text
        if "制服" in user_message:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="你🫵🏼\n就準備穿著\n「制服」or「學位服」\n來學校吧😍\n...")]
                )
            )

@line_handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback':
        print('Postback event is triggered')


if __name__ == "__main__":
    app.run()
