import os
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    RichMenuRequest,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    RichMenuAction,
)

# 讀取環境變數
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))

def create_rich_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

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
        result = line_bot_api.create_rich_menu(rich_menu=rich_menu)
        rich_menu_id = result.rich_menu_id
        print("✅ 圖文選單建立成功！RichMenu ID:", rich_menu_id)

        # 上傳圖片
        with open("menu.png", 'rb') as f:  # 換成你的圖檔名稱
            line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
            print("✅ 圖片上傳完成！")

        # 設定為預設圖文選單
        line_bot_api.set_default_rich_menu(rich_menu_id)
        print("✅ 已設定為預設圖文選單！")

if __name__ == "__main__":
    create_rich_menu()
