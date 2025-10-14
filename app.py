from flask import Flask, request, abort, jsonify
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, MessagingApiBlob,
    RichMenuSize, RichMenuRequest, RichMenuArea, RichMenuBounds, MessageAction
)
import os

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def create_rich_menu_1():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        # 先檢查是否已有 rich menu
        existing_menus = line_bot_api.get_rich_menu_list().richmenus
        if existing_menus:
            return existing_menus[0].rich_menu_id

        areas = [
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=833, height=843), action=MessageAction(text='A')),
            RichMenuArea(bounds=RichMenuBounds(x=834, y=0, width=833, height=843), action=MessageAction(text='B')),
            RichMenuArea(bounds=RichMenuBounds(x=1663, y=0, width=834, height=843), action=MessageAction(text='C')),
            RichMenuArea(bounds=RichMenuBounds(x=0, y=843, width=833, height=843), action=MessageAction(text='D')),
            RichMenuArea(bounds=RichMenuBounds(x=834, y=843, width=833, height=843), action=MessageAction(text='E')),
            RichMenuArea(bounds=RichMenuBounds(x=1662, y=843, width=834, height=843), action=MessageAction(text='F')),
        ]

        rich_menu_to_create = RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="圖文選單1",
            chat_bar_text="查看更多資訊",
            areas=areas
        )

        rich_menu_id = line_bot_api.create_rich_menu(rich_menu_request=rich_menu_to_create).rich_menu_id

        with open('./static/richmenu-1.jpeg', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/jpeg'}
            )

        line_bot_api.set_default_rich_menu(rich_menu_id)
        return rich_menu_id

@app.route("/create-richmenu", methods=["GET"])
def create_menu():
    rich_menu_id = create_rich_menu_1()
    return f"Rich menu created successfully! ID: {rich_menu_id}"

@app.route("/list-richmenu", methods=["GET"])
def list_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        menus = line_bot_api.get_rich_menu_list().richmenus
        return jsonify([menu.rich_menu_id for menu in menus])
    
@app.route("/link-richmenu/<user_id>", methods=["GET"])
def link_richmenu_to_user(user_id):
    """強制綁定圖文選單給指定使用者"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 取得目前 default rich menu ID
        try:
            rich_menu_id = line_bot_api.get_default_rich_menu_id().rich_menu_id
        except:
            return "No default rich menu found. Please create one first.", 400

        # 強制綁定給使用者
        line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id)
        return f"Linked rich menu {rich_menu_id} to user {user_id}"


if __name__ == "__main__":
    app.run()
