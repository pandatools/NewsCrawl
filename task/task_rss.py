import json

import redis
from feapder.utils.log import log
from config import dy_settings


rss_task = {
    "https://feedx.net/rss/investing.xml": "investing.com",
    "https://feedx.net/rss/rci.xml": "加拿大国际广播电台",
    "https://feedx.net/rss/people.xml": "人民日报",
    "https://feedx.net/rss/zaobao.xml": "联合早报",
    "https://feedx.net/rss/jingjiribao.xml": "经济日报",
    "https://feedx.net/rss/jiefangjunbao.xml": "解放军报",
    "https://feedx.net/rss/infzm.xml": "南方周末",
    "https://feedx.net/rss/bjnews.xml": "新京报",
    "https://feedx.net/rss/mrdx.xml": "新华每日电讯",
}
rss_task_lists = rss_task.keys()
re_queue = redis.Redis(host=dy_settings.redis.REDISDB_IP, port=dy_settings.redis.REDISDB_PORTS,password=dy_settings.redis.REDISDB_USER_PASS,db=3)

class rssRedis:
    def add_rss_task(self):
        if re_queue.llen('url') == 0:
            log.info('add task to redis queue')
            re_queue.lpush('url', *rss_task_lists)
        log.info("queue is not empty,no push")

    def get_rss_lists(self):
        return re_queue.lpop('url')

    def rss_empty(self):
        return re_queue.llen('url') == 0

rss_redis = rssRedis()

if __name__ == '__main__':
    rss_redis.add_rss_task()