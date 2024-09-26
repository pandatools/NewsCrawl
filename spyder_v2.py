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
from DrissionPage import Chromium
class SpyderV2(feapder.AirSpider):
    platform = "https://www.v2ex.com/"

    def start_requests(self):
        tab = Chromium().latest_tab
        tab.get("https://www.v2ex.com/")
        yield feapder.Request("https://www.v2ex.com/?tab=hot", callback=self.parse_list,tab=tab)
        # for i in range(1,21):
        #     yield feapder.Request(f"https://www.v2ex.com/recent?p={str(i)}",callback=self.parse_list)

    def download_midware(self,request):
        tab = request.tab
        url = request.url
        tab.get(url)
        return request,tab.response

    def shift_time(self,date_string):
        format_string = "%Y-%m-%d %H:%M:%S %z"
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
            yield feapder.Request(url,callback=self.parse_content,res=res,page=1,base_url =url,tab=request.tab )

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