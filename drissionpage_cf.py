import os
import platform
import time
import traceback

from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage._base.chromium import Chromium
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._pages.mix_tab import MixTab
from dotenv import load_dotenv
from lxml import etree


# pip install DrissionPage #https://drissionpage.cn
def god_index(tab: MixTab, token: str):
    """首页点击"""
    tab.get("https://gptgod.online/#/session/42zim85h27okj37t5icb04o2k")
    '''ele1 = tab.eles('xpath:/html/body')  # 微信截图的position 减标签及url栏高度得到 按钮相对body的高度
    if len(ele1) > 0:
        print(ele1[0])
        ele1[0].click.at(312, 927.5)
        ele1[0].click.at(312, 859)'''
    time.sleep(5)
    print("sleep5...")
    tab.wait.load_start()
    print("wait.load_start...")
    click_cloudflare_turnstile(tab, None)


def god_checkin(tab: MixTab, token: str):
    cookies = f'EGG_SESS={token}; path=/; domain=gptgod.online;'
    tab.set.cookies(cookies)
    print(tab.cookies())
    tab.get("https://gptgod.online/#/token?tab=rule")
    # tab.scroll.down(20)

    # buttons = tab.eles("css:button.ant-btn.css-1jr6e2p.ant-btn-default.ant-btn-color-default.ant-btn-variant-outlined")
    buttons = tab.eles("xpath=//button[span[text()='签到 领取2000积分']]")
    if len(buttons) == 0:
        print("没有找到按钮")
        return
    button_el = buttons[0]
    # 滚动页面使自己可见
    # button_el.scroll.to_see()
    # 按类型查找 同类型样式的多个按钮
    print(button_el.text)  # 签到
    button_el.click()
    print(f"{button_el.rect.click_point} click...")
    print(f"{button_el.rect.viewport_click_point} click...")
    print(f"{button_el.states.has_rect} click...")
    tab.wait.load_start()  # 等待页面进入加载状态
    click_cloudflare_turnstile(tab, button_el)


def click_cloudflare_turnstile(tab: MixTab, button: ChromiumElement = None):
    """点击cf真人认证"""
    # tab.wait.ele_displayed()
    if button and button.text == "今天已签到": return
    elements = tab.eles('css:#cf-turnstile')
    if len(elements) == 0:
        print("没有找到#cf-turnstile")
        # return
        tab.wait(40, 40)
        elements = tab.eles('css:#cf-turnstile')
        if len(elements) == 0: return
    cf_turnstile_ele = elements[0]
    width, height = cf_turnstile_ele.rect.size
    print(f"{width, height}: {cf_turnstile_ele}")
    cf_turnstile_ele.click.right()
    # 点击元素上中部，x相对左上角向右偏移50，y保持在元素中点
    cf_turnstile_ele.click.at(offset_x=28, offset_y=32, button="right", count=1)
    time.sleep(2)
    cf_turnstile_ele.click.at(offset_x=28, offset_y=32)  # 正中复选框

    print("tab.wait.load_start...")
    tab.get_screenshot(path='tmp', name='wait_load_start.jpg', full_page=True)
    tab.wait.load_start()  # 等待页面加载
    tab.get_screenshot(path='tmp', name='wait_done.jpg', full_page=True)
    if button:
        print(button.text)
        if button.text == "今天已签到": return
    tab.wait(20, 20)
    print("wait20...")
    tab.wait.load_start()  # 等待页面加载
    try:
        top_left, top_right, bottom_right, bottom_left = cf_turnstile_ele.states.has_rect
        if top_left:
            print(top_left, top_right, bottom_right, bottom_left)
            print("===")
            width, height = cf_turnstile_ele.rect.size
            # cf_turnstile_ele
            print(width, height)
            print(tab.eles('css:#cf-turnstile')[0].rect.size)
            print(tab.eles('css:button.ant-btn.css-hs5kb5.ant-btn-text.ant-btn-color-default.ant-btn-variant-text')[
                      4].rect.size)

            # cf_turnstile_ele.click(by_js=True)
            # 获取元素大小
            width, height = tab.run_js("""
                    const element = document.querySelector('#cf-turnstile');  // 替换为你的元素选择器
                    const rect = element.getBoundingClientRect();
                    console.log("element.getBoundingClientRect"+rect)
                    return rect.width, rect.height;
                """)
            print(width, height)
            cf_turnstile_ele.click.at(width / 4, height / 2)
    except Exception as e:
        print(f"\033[35m{traceback.format_exc()}\033[0m")
    finally:
        pass


def main():
    chromium_options = ChromiumOptions()
    os_name = platform.system()
    if os_name != "Windows":
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        chromium_options.headless(on_off=True).set_user_agent(user_agent).set_argument('--window-size', '1920, 1080')
        '''chromium_options.set_argument("--no-sandbox")
        chromium_options.set_argument("--disable-setuid-sandbox")
        chromium_options.set_argument('--start-maximized')
        chromium_options.set_argument("--headless=new")  # 无界面系统添加'''
        # chromium_options.incognito()  # chrome.exe --incognito
    else:
        chromium_options.headless(on_off=False)
    # 设置不加载图片、静音
    chromium_options.no_imgs(True).mute(True)
    # https://drissionpage.cn/versions/4.0.x #linux取消了自动无头模式浏览器，使用 chrome 关键字路径
    chromium_page = ChromiumPage(chromium_options.set_load_mode('normal').set_paths(browser_path=None))
    tab = Chromium().latest_tab

    load_dotenv()
    token = os.getenv("EGG_SESS")
    time.sleep(1)
    god_checkin(tab, token)
    # god_index(tab, token)

    print(f"cf-turnstile-response: {etree.HTML(tab.html).xpath('//*[@name="cf-turnstile-response"]')}")
    if os_name != "Windows": chromium_page.quit()  # 关闭浏览器


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
        main()  # 异常就重试一次
    finally:
        print("done.")
        time.sleep(60)
        pass
