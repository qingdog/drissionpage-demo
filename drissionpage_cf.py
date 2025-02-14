import datetime
import logging
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
        logger.info(ele1[0])
        ele1[0].click.at(312, 927.5)
        ele1[0].click.at(312, 859)'''
    time.sleep(5)
    logger.info("sleep5...")
    tab.wait.load_start()
    logger.info("wait.load_start...")
    click_cloudflare_turnstile(tab, None)


def god_checkin(tab: MixTab, token: str):
    # tab.get("https://gptgod.online/#/token?tab=rule")
    cookies = f'EGG_SESS={token}; path=/; domain=gptgod.online;'
    tab.set.cookies(cookies)
    # tab.get("https://www.baidu.com")
    time.sleep(0.5)
    tab.get("https://gptgod.online/#/token?tab=rule")
    logger.info(tab.cookies())
    # logger.info(tab.eles('xpath=//*[@id="root"]/div/div[2]/aside/div/div[3]/div/div[2]/div/div[7]/button/div')[0].text)
    buttons = tab.eles('css=div.ant-space-item>div>div.ant-space-item>button.ant-btn')
    if len(buttons) >= 7:
        logger.info(buttons[6].text)
    else:
        logger.warning("疑似不在首页...")
    # tab.scroll.down(20)

    css_buttons = tab.eles("css:button.ant-btn.css-1jr6e2p.ant-btn-default.ant-btn-color-default.ant-btn-variant-outlined")
    tab.wait(30, 30)
    # buttons = tab.eles("xpath=//button[span[text()='签到 领取2000积分']]")
    buttons = css_buttons
    if len(buttons) == 0:
        if len(css_buttons) > 0: logger.info(css_buttons[0].text)
        logger.info("没有找到按钮")
        return
    button_el = buttons[0]
    # 滚动页面使自己可见
    # button_el.scroll.to_see()
    # 按类型查找 同类型样式的多个按钮
    logger.info(button_el.text)  # 签到
    try:
        # logger.info(f"{button_el.rect.click_point} click...")
        # logger.info(f"{button_el.rect.viewport_click_point} viewport_click_point...")
        pass
    except Exception as e:
        logger.info(e)
    finally:
        # logger.info(f"{button_el.states.has_rect} click...")
        # button_el.click(by_js=True)
        button_el.click()
        start_time = time.time()
        tab.wait.load_start()  # 等待页面进入加载状态
        logger.info(time.time() - start_time)
        tab.wait(30, 30)
        click_cloudflare_turnstile(tab, button_el)


def click_cloudflare_turnstile(tab: MixTab, button: ChromiumElement = None):
    """点击cf真人认证"""
    # tab.wait.ele_displayed()
    elements = tab.eles('css:#cf-turnstile')
    if len(elements) == 0:
        logger.info("没有找到#cf-turnstile")
        # return
        tab.wait(40, 40)
        elements = tab.eles('css:#cf-turnstile')
        if len(elements) == 0: return
    cf_turnstile_ele = elements[0]
    '''
    # width, height = cf_turnstile_ele.rect.size
    # logger.info(f"{width, height}: {cf_turnstile_ele}")'''

    # cf_turnstile_ele.click.right()
    # 点击元素上中部，x相对左上角向右偏移50，y保持在元素中点
    # cf_turnstile_ele.click.at(offset_x=28, offset_y=32, button="right", count=1)
    time.sleep(2)
    if cf_turnstile_ele.states.has_rect:
        cf_turnstile_ele.click.at(offset_x=28, offset_y=32)  # 正中复选框
    else:
        logger.info("该元素没有位置及大小。疑似页面已经发生变化或已操作过...")
    logger.info("86 tab.wait.load_start...")
    tab.wait.load_start()  # 等待页面加载

    if button:
        logger.info(button.text)
        if button.text == "今天已签到": return
    tab.wait(20, 20)
    logger.info("已经点击wait20s...")
    tab.wait.load_start()  # 等待页面加载
    try:
        if cf_turnstile_ele.states.has_rect:
            top_left, top_right, bottom_right, bottom_left = cf_turnstile_ele.states.has_rect
            logger.info(f"top_left: {top_left}, top_right: {top_right}, bottom_right: {bottom_right}, bottom_left: {bottom_left}")
            width, height = tab.eles('css:#cf-turnstile')[0].rect.size
            logger.info(f"{width, height}: {tab.eles('css:#cf-turnstile')[0]}")
            # tab.eles('css:#cf-turnstile')[0].click.at(offset_x=28, offset_y=32)
            # tab.get_screenshot(path='temp', name='wait_click_bak.jpg', full_page=True)
            tab.wait(1, 2)

            # 获取元素大小
            width = tab.run_js("""
                console.log(document.querySelector('#cf-turnstile'))
                return document.querySelector('#cf-turnstile').getBoundingClientRect().width;
                """)
            logger.info(f"width: {width}, height: {height}")
            button.click()
            tab.scroll.down(61)
            # tab.get_screenshot(path='temp', name='wait_click1_hide.jpg', full_page=True)
            tab.wait(60)
            tab.scroll.up(82)
            button.click()
            # tab.get_screenshot(path='temp', name='wait_click2_display.jpg', full_page=True)
            tab.wait(3)
            tab.scroll.down(30)
            tab.wait(60)
            # tab.get_screenshot(path='temp', name='wait_click2_wait.jpg', full_page=True)
            cf_turnstile_ele.click.at(width / 4, 30)  # 不点击
            time.sleep(20)
    except Exception as e:
        logger.info(f"\033[35m{traceback.format_exc()}\033[0m")
        w = 238
        height = 782
        # 40,698
    finally:
        ele1 = tab.eles('xpath:/html/body')  # 微信截图的position 减标签及url栏高度得到 按钮相对body的高度
        if len(ele1) > 0:
            time.sleep(30)
            ele1[0].click.at(238, 720)
            logger.info(button.text)
            time.sleep(30)
            ele1[0].click.at(40, 720)
        logger.info(button.text)


global chromium


def main_bak():
    # 配置 Chromium 选项
    chromium_options = ChromiumOptions().set_load_mode("normal")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    chromium_options.headless(on_off=False).set_user_agent(user_agent).set_argument('--start-maximized')  # .set_argument('--window-size', '1800, 900')
    chromium_options.set_argument("--no-sandbox")  # .set_argument("--disable-setuid-sandbox").set_argument("--lang=zh-CN").set_paths(local_port=9222)
    # chromium_options.set_argument("--headless=new")  # 无界面系统添加
    chromium_options.no_imgs(True).mute(True)
    # 兼容无头模式中的参数 --headless=new
    if not chromium_options.is_headless:
        chromium_options.remove_argument("--headless=new")
    global chromium
    try:
        chromium = Chromium(chromium_options)
        tab = chromium.latest_tab
        token = os.getenv("EGG_SESS")

        def set_cookies(_tab, _token):
            cookies = f'EGG_SESS={_token}; path=/; domain=gptgod.online;'
            _tab.set.cookies(cookies)

        def click_turnstile(tab: MixTab):
            """处理 Turnstile 验证和点击动作"""
            ele = tab.ele('css:#cf-turnstile')
            # tab.get_screenshot(path='temp', name=f'wait_{time.strftime("%Y%m%d%H%M%S")}.jpg', full_page=True)
            time.sleep(10)
            # tab.get_screenshot(path='temp', name=f'click_{time.strftime("%Y%m%d%H%M%S")}.jpg', full_page=True)

            if ele:
                if ele.states.has_rect:
                    ele.click.at(28, 32)  # 点击验证码复选框
                    logger.info("Clicked on Turnstile.")
                else:
                    logger.info("Turnstile 元素没有大小.")
                    # 查找按钮并点击
                    bb = tab.ele('xpath=//*[@role="tabpanel"]/div/button')
                    if bb:
                        logger.info(bb.text)
            else:
                logger.info("未找到 Turnstile 元素.")
                # 查找按钮并点击
                bb = tab.ele('xpath=//*[@role="tabpanel"]/div/button')
                if bb:
                    logger.info(bb.text)

        def wait_for_load(tab):
            """等待页面加载完成"""
            logger.info("Waiting for page to load...")
            tab.wait.load_start()  # 等待页面加载开始
            # tab.get_screenshot(path='temp', name='wait_load_start.jpg')
            tab.wait.load_start()  # 等待页面加载完成
            # tab.get_screenshot(path='temp', name='wait_done.jpg')

        # 设置 Cookies
        set_cookies(tab, token)

        url = "https://gptgod.online/#/token?tab=rule"
        tab.get(url)
        time.sleep(5)
        logger.info(tab.cookies())

        # tab.get_screenshot(path='temp', name=f'start_{time.strftime("%Y%m%d%H%M%S")}.jpg', full_page=True)
        buttons = tab.eles('css=div.ant-space-item>div>div.ant-space-item>button.ant-btn')
        if len(buttons) >= 7: logger.info(buttons[6].text)

        # 查找按钮并点击
        # tab.scroll.down(1700)
        check_button = tab.ele('xpath=//*[@role="tabpanel"]/div/button')
        if check_button:
            # tab.actions.scroll(on_ele=check_button)
            # tab.scroll.down(100)
            # check_button = tab.ele('xpath=//*[@role="tabpanel"]/div/button')
            time.sleep(1)
            # tab.get_screenshot(path='temp', name=f'scroll_{time.strftime("%Y%m%d%H%M%S")}.jpg', full_page=False)
            time.sleep(1)

            logger.info(check_button.text)
            check_button.click()
            logger.info("Button clicked.")
            wait_for_load(tab)

            click_turnstile(tab)  # 处理验证码

        # 打印 cf-turnstile-response 的值
        time.sleep(20)
        # tab.get_screenshot(path='temp', name=f'done_{time.strftime("%Y%m%d%H%M%S")}.jpg', full_page=True)
        cf_turnstile_response = etree.HTML(tab.html).xpath('//*[@name="cf-turnstile-response"]/@value')
        logger.info(f"cf_turnstile_response: {cf_turnstile_response}")
    except Exception as e:
        logger.info(e, exc_info=True)
    finally:
        if globals().get("chromium"):
            logger.info("quit...")
            chromium.quit()


def main():
    os_name = platform.system()
    chromium_options = ChromiumOptions()
    if os_name != "Windows":
        # TODO: 获取ubuntu2204的chrome的 user_agent版本，设置到无头模式中
        chromium_options.headless(on_off=True).set_argument('--window-size', '1920, 1080')
        # chromium_options.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        # chromium_options.set_argument('--start-maximized')
        chromium_options.set_argument("--no-sandbox")
        # chromium_options.set_argument("--disable-setuid-sandbox")
        # chromium_options.set_argument("--headless=new")  # 无界面系统添加
        chromium_options.incognito(on_off=True)  # chrome.exe --incognito
    else:
        chromium_options.headless(on_off=False).set_argument('--window-size', '1920, 1080')
        chromium_options.incognito(True)
        # chromium_options.set_argument("--no-sandbox")
        # chromium_options.set_argument("--disable-setuid-sandbox")
        # chromium_options.set_argument("--headless=new")  # 无界面系统添加
    # 设置加载图片、静音
    chromium_options.no_imgs(False).mute(True)
    # https://drissionpage.cn/versions/4.0.x #linux取消了自动无头模式浏览器，使用 chrome 关键字路径
    chromium_page = ChromiumPage(chromium_options.set_load_mode('normal').set_paths(browser_path=None))
    try:
        tab = Chromium().latest_tab
        # tab.screencast.start()  # 开始录制

        user_agent = tab.run_js("""
                        return navigator.userAgent;
                        """)
        logging.info(user_agent)
        tab.get("https://useragent.buyaocha.com/")
        ua = tab.ele('css=table.mt-2.table.table-sm.table-bordered')
        logging.info(ua.text)

        load_dotenv()
        token = os.getenv("EGG_SESS")
        time.sleep(1)
        god_checkin(tab, token)
        # god_index(tab, token)

        # tab.screencast.stop(video_name="headless.mp4")
        # logger.info(f"cf-turnstile-response: {etree.HTML(tab.html).xpath('//*[@name="cf-turnstile-response"]')}")
    except Exception as e:
        raise e
    finally:
        logger.info("done.")
        time.sleep(10)
        chromium_page.quit()  # 关闭浏览器


def init_logger_for_script_run():
    """初始化logger为了作为脚本运行。自定义日志文件将一周时间内产生的日志输出到同一个文件中"""
    _logger = None
    try:
        import sys

        sys.path.extend(['D:\\mytest\\UnittestDemo', '/mnt/d/mytest/UnittestDemo'])
        from utils import color_format_logging, myutil

        current_directory = myutil.get_project_path()  # 存储日志的目录
        # 获取当前日期和 ISO 日历信息
        today = datetime.date.today()
        year, week, _ = today.isocalendar()
        # 构造日志文件路径：年月周
        log_path_name = os.path.join(current_directory, "logs", f'week_{today.strftime("%Y%m")}_{week}.log')
        _logger, log_file_path = color_format_logging.main(config_logger_name="week", log_path=log_path_name)
    except Exception as e:
        print(f"\033[34m{traceback.format_exc()}\033[0m")
        _logger = logging.getLogger()
        _logger.setLevel(logging.INFO)
    return _logger


if __name__ == '__main__':
    logger = init_logger_for_script_run()

    load_dotenv()
    try:
        # main_bak()
        main()
    except Exception:
        logger.critical(f"\033[34m{traceback.format_exc()}\033[0m")
        # main()  # 异常就重试一次
