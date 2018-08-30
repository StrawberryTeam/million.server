#!/usr/bin/python3
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import config as config
import common as common

class db():

    # 已连接表
    _collection = {
    }

    # 已连接 db
    _db = {}

    def __init__(self):
        pass
        # 手动执行
        # if __name__ == "__main__":
        #     pass

    # 连接表
    def connect(self, table):
        # 已连接过的表
        if self._collection[table]:
            return self._collection[table]

        client = MongoClient(config.mongo_client)
        if not self._db:
            self._db = client[config.db] # 连接库

        self._collection[table] = self._db[table] # 选择表
        return self._collection[table]




if __name__ == "__main__":
    db()
