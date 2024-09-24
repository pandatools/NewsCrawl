# -*- coding: utf-8 -*-
"""
Created on 2024-09-20 16:46:14
---------
@summary:
---------
@author: ysl
"""

import feapder
from feapder.utils.webdriver import PlaywrightDriver, InterceptResponse, InterceptRequest


class SpyderLinuxDo(feapder.AirSpider):
    platform = "https://linux.do/"
    __custom_setting__ = dict(
        RENDER_DOWNLOADER="feapder.network.downloader.PlaywrightDownloader",
        PLAYWRIGHT=dict(
            user_agent=None,  # 字符串 或 无参函数，返回值为user_agent
            proxy=None,  # xxx.xxx.xxx.xxx:xxxx 或 无参函数，返回值为代理地址
            headless=True,
            driver_type="chromium",  # chromium、firefox、webkit
            timeout=30,  # 请求超时时间
            window_size=(1024, 800),  # 窗口大小
            executable_path=None,  # 浏览器路径，默认为默认路径
            download_path=None,  # 下载文件的路径
            render_time=0,  # 渲染时长，即打开网页等待指定时间后再获取源码
            wait_until="networkidle",  # 等待页面加载完成的事件,可选值："commit", "domcontentloaded", "load", "networkidle"
            use_stealth_js=False,  # 使用stealth.min.js隐藏浏览器特征
            # page_on_event_callback=dict(response=on_response),  # 监听response事件
            # page.on() 事件的回调 如 page_on_event_callback={"dialog": lambda dialog: dialog.accept()}
            storage_state_path=None,  # 保存浏览器状态的路径
            url_regexes=["wallpaper/list"],  # 拦截接口，支持正则，数组类型
            save_all=True,  # 是否保存所有拦截的接口
        ),
    )
    def start_requests(self):
        yield feapder.Request("https://linux.do/latest")

    def parse(self, request, response):
        driver: PlaywrightDriver = response.driver

        intercept_response: InterceptResponse = driver.get_response("wallpaper/list")
        intercept_request: InterceptRequest = intercept_response.request
        req_url = intercept_request.url
        req_header = intercept_request.headers
        req_data = intercept_request.data


if __name__ == "__main__":
    SpyderLinuxDo().run()