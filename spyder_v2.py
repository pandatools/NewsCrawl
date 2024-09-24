# -*- coding: utf-8 -*-
"""
Created on 2024-09-20 14:14:32
---------
@summary:
---------
@author: ysl
"""
from datetime import datetime

import feapder

from items.reply_item import ReplyItem
from items.subject_item import SubjectItem
import feapder.utils.tools

class SpyderV2(feapder.AirSpider):
    platform = "https://www.v2ex.com/"
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
        yield feapder.Request("https://www.v2ex.com/?tab=hot", callback=self.parse_list)
        # for i in range(1,21):
        #     yield feapder.Request(f"https://www.v2ex.com/recent?p={str(i)}",callback=self.parse_list)

    def shift_time(self,date_string):
        format_string = "%Y-%m-%d %H:%M:%S %z"

        # Convert the string to a datetime object
        return datetime.strptime(date_string, format_string)
    def parse_list(self, request, response):
       for item in response.xpath('.//div[@class="box"]/div[@class="cell item"]'):
            title = item.xpath('.//span[@class="item_title"]/a/text()').get()
            url = item.xpath('.//span[@class="item_title"]/a/@href').get()
            last_reply = item.xpath('.//span[@class="topic_info"]/span/@title').get()

            if "#" in url:
                url = url.split("#",1)[0]
            res = {
                "title": title,
                "url": url,
                "reply_time": self.shift_time(last_reply),
                "content":"",
                "replys": {},
                "platform":self.platform,
            }
            yield feapder.Request(url,callback=self.parse_content,res=res,page=1,base_url =url )

    def parse_content(self, request,response):

        res = request.res
        replys = res['replys']
        header_items = response.xpath('//div[@id="Main"]/div[@class="box"]//div[@class="topic_content"]')
        for item in header_items:
            word_list =[i for i in item.xpath('.//text()').extract()]
            res['content'] = res['content'] + ''.join(word_list)

        content_items = response.xpath('//div[@id="Main"]/div[@class="box"][2]/div[@class="cell"]')

        for item in content_items:
            txt = ''.join(item.xpath('.//td[@align="left"]//div[@class="reply_content"]/text()').extract())
            id = item.xpath('./@id').get()
            reply_time = item.xpath('.//span[@class="ago"]/@title').get()
            if not reply_time:
                continue
            replys[id] = {
                "content":txt,
                "reply_time":self.shift_time(reply_time)
            }
        res['replys'] = replys
        try:
            max_page = int(response.xpath('//input[@class="page_input"]/@max').get())
        except Exception as e:
            max_page = 1
        if request.page == max_page:
            subject_item = SubjectItem(**res).to_UpdateItem()
            yield subject_item
            for key,value in res['replys'].items():
                value['reply_id'] = key
                value['sub_id'] = subject_item.id
                reply_item = ReplyItem(**value).to_UpdateItem()
                yield reply_item

        if request.page < max_page:

            page = request.page +1
            base_url = request.base_url
            reply_url = base_url + "?p=" + str(page)
            yield feapder.Request(reply_url,callback=self.parse_content,res=res,page=page,base_url =base_url )


if __name__ == "__main__":
    SpyderV2().start()