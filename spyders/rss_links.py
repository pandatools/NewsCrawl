# -*- coding: utf-8 -*-
"""
Created on 2024-10-30 15:21:36
---------
@summary:
---------
@author: ysl
"""

import feapder
import feedparser

from task.task_rss import rss_redis


class RssLinks(feapder.AirSpider):
    def start_requests(self):
        while not rss_redis.rss_empty():
            url = rss_redis.get_rss_lists().decode('utf-8')
            yield feapder.Request(url)

    def parse(self, request, response):
        feed = feedparser.parse(response.content)
        for entry in feed.entries:
            res  = {
                "title": entry.title,
                "published": entry.published,
                "link": entry.link,
                "title": feed.entries[0].title,
                "platform":''
            }
            print(entry.title)
            print(entry.published)
            print(entry.link)
            print(entry.summary)



if __name__ == "__main__":
    RssLinks().start()