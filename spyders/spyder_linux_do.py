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
from DrissionPage._configs.chromium_options import ChromiumOptions
from feapder.utils import tools

from custom.CustomRequestBuffer import CustomRequestBufferNoEffort
from items.reply_item import ReplyItem
from items.subject_item import SubjectItem
from feapder.utils.log import log

from spyders.common import create_chrome

chrome = create_chrome()
tab = chrome.latest_tab
tab.get("https://linux.do/latest")
# 访问网址
class SpyderLinuxDo(feapder.Spider):
    platform = "https://linux.do/"
    white_list = ['linux.do/latest.json?','track_visit=true&forceLoad=true']
    def __init__(self, redis_key=None, min_task_count=1, check_task_interval=5, thread_count=None, begin_callback=None,
                 end_callback=None, delete_keys=(), keep_alive=None, auto_start_requests=None, batch_interval=0,
                 wait_lock=True, **kwargs):
        redis_key = tools.get_domain(self.platform)
        super(SpyderLinuxDo,self).__init__(redis_key, min_task_count, check_task_interval, thread_count, begin_callback, end_callback,
                         delete_keys, keep_alive, auto_start_requests, batch_interval, wait_lock, **kwargs)

        self._request_buffer = CustomRequestBufferNoEffort(redis_key)
    def start_requests(self):
        log.info('v1')

        yield feapder.Request("https://linux.do/latest.json?no_definitions=true&page=2",white_list=self.white_list)

    def shift_time(self,date_string):
        date_string = date_string.replace('Z', '+0000')
        format_string = '%Y-%m-%dT%H:%M:%S.%f%z'
        return datetime.strptime(date_string, format_string)
    def download_midware(self,request):
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
            yield feapder.Request(res['reply_url'],callback=self.parse_content,res=res,white_list=self.white_list)
        yield feapder.Request(res['reply_url'], callback=self.parse_content, res=res,white_list=self.white_list)
    def split_list_into_groups(self,input_list, group_size):
        # Use list comprehension to create sublists of the specified size
        input_list.sort()
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
            yield feapder.Request(url,callback=self.parse_reply,res=request.res,subject_item=sub_item,white_list=self.white_list)

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
    SpyderLinuxDo().start()