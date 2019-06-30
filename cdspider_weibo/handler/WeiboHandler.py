#-*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

"""
:author:  Zhang Yi <loeyae@gmail.com>
:date:    2018-12-16 14:34:28
"""
import time
from cdspider_wemedia.handler import WemediaListHandler
from cdspider.libs import utils
from cdspider.libs.constants import *
from cdspider.database.base import *
from cdspider.parser.lib import TimeParser


class WeiboHandler(WemediaListHandler):
    """
    weibo handler
    :property task 爬虫任务信息 {"mode": "comment", "uuid": SpiderTask.weibo uuid}
                   当测试该handler，数据应为 {"mode": "weibo", "url": url, "authorListRule": 评论规则，参考评论规则}
    """

    def build_result_info(self, **kwargs):
        """
        构造文章数据
        :param result: 解析到的文章信息 {"title": 标题, "author": 作者, "pubtime": 发布时间, "content": 内容}
        :param final_url: 请求的url
        :param typeinfo: 域名信息 {'domain': 一级域名, 'subdomain': 子域名}
        :param crawlinfo: 爬虫信息
        :param unid: 文章唯一索引
        :param ctime: 抓取时间
        :param status: 状态
        """
        now = int(time.time())
        result = kwargs.get('result', {})
        pubtime = TimeParser.timeformat(str(result.pop('pubtime', '')))
        if pubtime and pubtime > now:
            pubtime = now
        r = {
            "status": kwargs.get('status', ArticlesDB.STATUS_INIT),
            'url': kwargs['final_url'],
            'domain': kwargs.get("typeinfo", {}).get('domain', None),          # 站点域名
            'subdomain': kwargs.get("typeinfo", {}).get('subdomain', None),    # 站点域名
            'title': "%s的微博",                                # 标题
            'mediaType': self.process.get('mediaType', self.task['task'].get('mediaType', MEDIA_TYPE_OTHER)),
            'author': result.pop('author', None),
            'pubtime': pubtime,                                                # 发布时间
            'channel': result.pop('channel', None),                            # 频道信息
            'result': result,
            'crawlinfo': kwargs.get('crawlinfo'),
            'acid': kwargs['unid'],                                            # unique str
            'ctime': kwargs.get('ctime', self.crawl_id),
        }
        return r

    def build_item_task(self, rid, mode, save):
        """
        生成详情抓取任务并入队
        """
        typeinfo = utils.typeinfo(self.response['final_url'])
        self.extension("result_handle", {"save": save, **typeinfo}, ns="item_handler")
