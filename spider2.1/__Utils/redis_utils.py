#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
程序：SpiderProject
版本：1.0
作者：LiuJingYuan
日期：2017/9/5 14:39
语言：Python 2.7.13
操作：python redis_utils.py
'''
import json
import rediscluster
# from constants import HOST, PORT
from constants import REDIS

class RedisUtils():
    def __init__(self):

        list_host = REDIS.split(",")
        redis_nodes = []
        for i in list_host:
            i = i.split(":")
            redis_nodes.append({'host': i[0], 'port': i[1]})


        # list_host = HOST.split(",")

        # list_port = PORT.split(",")

        # redis_nodes = [
        #     {'host': list_host[0], 'port': list_port[0]},
        #     {'host': list_host[0], 'port': list_port[1]},
        #     {'host': list_host[0], 'port': list_port[2]},
        #     {'host': list_host[0], 'port': list_port[3]},
            # {'host': list_host[0], 'port': list_port[4]},
            # {'host': list_host[0], 'port': list_port[5]},
        # ]
        self.cluster = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes)
        # print "ready go..."

    def getCons(self):
        """
        从队列中获得查询任务
        :return:
        """
        element_json = self.cluster.keys("spider_*:task")
        if element_json == None:

            return None
        else:
            # print element_json
            return element_json



    def getCon(self,SOURCE):
        """
        从队列中获得查询任务
        :return:
        """
        SOURCE = 'spider_' + SOURCE
        # print SOURCE
        element_json = self.cluster.blpop(SOURCE + ":task", 1)
        if element_json == None:
            # print element_json, '12345'
            return None
        else:
            str_json = element_json[1].strip().decode("utf-8").replace("'", "\"")
            dict_json = json.loads(str_json)
            return dict_json


    def setNotify(self, type=None, token=None, val=None, decs=None, result=None):
        """
        :param token:
        :param val:
        :param step:
        :return:
        """
        notifyKey = "spider_session:" + token
        if result == None:
            dict_notify = {"type": type, "notify": val, "desc": decs}
        else:
            if isinstance(result, dict):
                result = json.dumps(result)
            dict_notify = {"type": type, "notify": val, "desc": decs, "result": result}
        self.cluster.rpush(notifyKey+"notify", {"desc":"爬取通知"})
        self.cluster.hmset(notifyKey, dict_notify)
        # notifyKey = "spider_session:" + token
        # if result == None:
        #     dict_notify = {"type": type, "notify": val, "desc": decs}
        # else:
        #     if isinstance(result, dict):
        #         result = json.dumps(result)
        #     dict_notify = {"type": type, "notify": val, "desc": decs, "result": result}
        # self.cluster.hmset(notifyKey, dict_notify)


    def getNotify(self, token, *keys):
        """
        从队列中获得查询任务
        :return:
        """
        notifyKey = "spider_session:" + token
        # notifyKey = "session:" + token
        element_json = self.cluster.hmget(notifyKey, keys)
        if element_json == None:
            return None
        else:
            return element_json[0]


    def DelNotify(self, token, keys):
        notifyKey = "spider_session:" + token
        return self.cluster.hdel(notifyKey, keys)

if __name__ == '__main__':
    pass