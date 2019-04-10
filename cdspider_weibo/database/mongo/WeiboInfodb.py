#-*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"),
# see LICENSE for more details: http://www.apache.org/licenses/LICENSE-2.0.

"""
:author:  Zhang Yi <loeyae@gmail.com>
:date:    2018-1-9 21:30:20
:version: SVN: $Id: Resultdb.py 2338 2018-07-08 05:58:24Z zhangyi $
"""
import time
from cdspider.database.base import WeiboInfoDB as BaseWeiboInfoDB
from cdspider.database.mongo.Mongo import Mongo, SplitTableMixin

class WeiboInfoDB(Mongo, BaseWeiboInfoDB, SplitTableMixin):

    __tablename__ = 'weibo_info'

    def __init__(self, connector, table=None, **kwargs):
        super(WeiboInfoDB, self).__init__(connector, table = table, **kwargs)
        self._check_collection()

    def insert(self, obj = {}):
        obj.setdefault("ctime", int(time.time()))
        table = self._get_collection(obj['ctime'])
        id = self._get_increment(table)
        obj['rid'] = BaseWeiboInfoDB.build_id(obj['ctime'], id)
        super(WeiboInfoDB, self).insert(setting=obj, table=table)
        return obj['rid']

    def update(self, id, obj = {}):
        table = self._table_name(id)
        obj['utime'] = int(time.time())
        return super(WeiboInfoDB, self).update(setting=obj, where={"rid": id}, table=table)

    def get_detail(self, id, select = None):
        table = self._table_name(id)
        return self.get(where={"rid": id}, table=table, select=select)

    def get_detail_by_unid(self, unid, ctime):
        table = self._get_collection(ctime)
        return self.get(where = {"acid", unid}, table=table)

    def get_list(self, ctime, where = {}, select = None, **kwargs):
        table = self._get_collection(ctime)
        kwargs.setdefault('sort', [('ctime', 1)])
        return self.find(table=table, where=where, select=select, **kwargs)

    def get_count(self, ctime, where = {}, select = None, **kwargs):
        table = self._get_collection(ctime)
        return self.count(table=table, where=where, select=select, **kwargs)

    def _get_collection(self, ctime):
        suffix = time.strftime("%Y%m", time.localtime(ctime))
        name = super(WeiboInfoDB, self)._collection_name(suffix)
        if not name in self._collections:
            self._create_collection(name)
        return name

    def _table_name(self, id):
        suffix, _ = BaseWeiboInfoDB.unbuild_id(id)
        name = super(WeiboInfoDB, self)._collection_name(suffix)
        if not name in self._collections:
            self._create_collection(name)
        return name

    def _check_collection(self):
        self._list_collection()
        suffix = time.strftime("%Y%m")
        name = super(WeiboInfoDB, self)._collection_name(suffix)
        if not name in self._collections:
            self._create_collection(name)

    def _create_collection(self, table):
        collection = self._db.get_collection(table)
        indexes = collection.index_information()
        if not 'rid' in indexes:
            collection.create_index('rid', unique=True, name='rid')
        if not 'acid' in indexes:
            collection.create_index('acid', unique=True, name='acid')
        if not 'domain' in indexes:
            collection.create_index('domain', name='domain')
        if not 'subdomain' in indexes:
            collection.create_index('subdomain', name='subdomain')
        if not 'status' in indexes:
            collection.create_index('status', name='status')
        if not 'pubtime' in indexes:
            collection.create_index('pubtime', name='pubtime')
        if not 'ctime' in indexes:
            collection.create_index('ctime', name='ctime')
        if not 'pid' in indexes:
            collection.create_index('crawlinfo.pid', name='pid')
        if not 'sid' in indexes:
            collection.create_index('crawlinfo.sid', name='sid')
        if not 'tid' in indexes:
            collection.create_index('crawlinfo.tid', name='tid')
        if not 'uid' in indexes:
            collection.create_index('crawlinfo.uid', name='uid')
        if not 'kid' in indexes:
            collection.create_index('crawlinfo.kid', name='kid')
        if not 'listRule' in indexes:
            collection.create_index([('crawlinfo.listMode', 1), ('crawlinfo.listRule', 1)], name='listRule')
        self._collections.add(table)
