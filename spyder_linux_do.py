# -*- coding: utf-8 -*-
"""
Created on 2024-09-20 16:46:14
---------
@summary:
---------
@author: ysl
"""
from datetime import datetime

import feapder
from DrissionPage import Chromium
from feapder.utils.webdriver import PlaywrightDriver, InterceptResponse, InterceptRequest

from items.reply_item import ReplyItem
from items.subject_item import SubjectItem


# 访问网址
class SpyderLinuxDo(feapder.AirSpider):
    platform = "https://linux.do/"
    def start_requests(self):
        tab = Chromium().latest_tab
        tab.get("https://linux.do/latest")
        yield feapder.Request("https://linux.do/latest.json?no_definitions=true&page=0",tab=tab)

    def shift_time(self,date_string):
        date_string = date_string.replace('Z', '+0000')
        format_string = '%Y-%m-%dT%H:%M:%S.%f%z'
        return datetime.strptime(date_string, format_string)
    def download_midware(self,request):
        tab = request.tab
        url = request.url
        tab.get(url)
        return request,tab.response

    def parse(self, request, response):
        # print(response)
        json_body = response.json
        topic_list = json_body.get('topic_list',{}).get('topics',[])
        for topic in topic_list:
            res = {
                "title":topic.get('title'),
                "reply_time":self.shift_time(topic.get('created_at')),
                "url":"https://linux.do/t/topic/" + str(topic.get('id')),
                "platform":self.platform,
                "reply_url":f"https://linux.do/t/{str(topic.get('id'))}.json?track_visit=true&forceLoad=true",
                "topic_id":str(topic.get('id'))
            }
            yield feapder.Request(res['reply_url'],callback=self.parse_content,res=res,tab=request.tab)
        # res= {
        #     "title":"我怎么等级变成1级了",
        #     "reply_time": "2024-09-25T07:25:11.010Z",
        #     "url": "https://linux.do/t/topic/" +"216096",
        #     "platform": self.platform,
        #     "reply_url": "https://linux.do/t/216096.json?track_visit=true&forceLoad=true",
        #     "topic_id": "216096"
        # }
        yield feapder.Request(res['reply_url'], callback=self.parse_content, res=res, tab=request.tab)
    def split_list_into_groups(self,input_list, group_size):
        # Use list comprehension to create sublists of the specified size
        return [input_list[i:i + group_size] for i in range(0, len(input_list), group_size)]

    def parse_content(self,request,response):
        res = request.res
        stream_list= response.json['post_stream']['stream']
        url = f"https://linux.do/t/{request.res['topic_id']}/posts.json?"
        group_stream = self.split_list_into_groups(stream_list,10)
        sub_item = SubjectItem(**res).to_UpdateItem()
        yield sub_item
        for group in group_stream:
            param_list = ["include_suggested=true"]
            for i in group:
                param_list.append(f"post_ids%5B%5D={str(i)}")
            url = url + '&'.join(param_list)
            yield feapder.Request(url,callback=self.parse_reply,res=request.res,tab=request.tab,subject_item=sub_item)

    def parse_reply(self,request,response):
        posts = response.json['post_stream']['posts']
        for post in posts:
            res = {
                'sub_id': request.subject_item.id,
                'reply_id': post['id'],
                'content': post['cooked'],
                'reply_time': self.shift_time(post['created_at'])
            }
            reply_item = ReplyItem(**res).to_UpdateItem()
            yield reply_item

if __name__ == "__main__":
    SpyderLinuxDo().run()