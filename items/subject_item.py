# -*- coding: utf-8 -*-
"""
Created on 2024-09-20 15:46:10
---------
@summary:
---------
@author: ysl
"""

from feapder import Item
from feapder.utils import tools


class SubjectItem(Item):
    """
    This class was generated by feapder
    command: feapder create -i subject 1
    """

    __table_name__ = "subject"
    __unique_key__ = ["title", "url"]
    def __init__(self, *args, **kwargs):
        self.title = kwargs.get('title')
        self.content = kwargs.get('content')
        self.reply_time = kwargs.get('reply_time')
        self.url = kwargs.get('url')
        self.id = tools.get_md5(self.title,self.url)
        self.platform = kwargs.get('platform')
