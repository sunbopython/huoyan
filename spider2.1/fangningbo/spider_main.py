#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
#
#-------------------------------------------------------------------------
import sys
sys.path.append('.')
from datetime import datetime
from __Utils.constants import WAITTING
from __Utils.param_crypto import decryptKwargs
from __Utils.redis_utils import RedisUtils
from __Utils.spider_email import sendMail
from crawl_main import SpiderMain, Time
from ningboConstants import THREAD_NUM, THREAD_Q_SIZE, SOURCE
import time
import logging.config
from threadpool import ThreadPool
from threadpool import makeRequests
import traceback
import threading
import os
import functools

reload(sys)
sys.setdefaultencoding("utf8")
logging.config.fileConfig('fangningbo/ningbologger.conf')
logger = logging.getLogger()

def Path():
    def _deco(func):
        @functools.wraps(func)
        def _func():
            print os.path.abspath(os.path.dirname(__file__))
            # logger.info('日志路径如下:')
            # print os.path.abspath(os.path.join(os.getcwd(), "./logs/dishonesty/dishonesty.log"))
            value = func()
            return 
        return _func
    return _deco


class SpiderClient():

    def __init__(self):
        """
        初始化
        :param spider:
        :return:
        """

        # 线程数
        self.thread_num = THREAD_NUM
        # 队列数：1
        self.thread_q_size = THREAD_Q_SIZE
        # redis操作类
        self.redisUtils = RedisUtils()


    def progressWork(self):
        """
        进程工作，用来启动多个线程
        :param x:
        :return:
        """
        thread_pool = ThreadPool(self.thread_num, q_size=self.thread_q_size)
        for i in range(self.thread_num):
            dict_t = {}
            requests = makeRequests(self.threadWork, [dict_t])
            thread_pool.putRequest(requests[0])
        thread_pool.wait()


    def threadWork(self, t):
        """
        线程工作的方法，主要用户获取任务
        :param t:
        :return:
        """
        startTime = datetime.now()
        while True:
            try:
                # 从任务队列中获取任务数据
                dict_json = self.redisUtils.getCon(SOURCE)
                # print dict_json,'1234'
                if dict_json is not None:
                    dict_json = decryptKwargs(dict_json)
                    name = dict_json.get('keyword','')
                    # 将token放入到thread中
                    logger.info("获取到任务,%s" % name)
                    # sendMail(u"邮件log测试",'liujingyuan@insightcredit.cn')
                    dict_json.update({"result": []})
                    self.taskWork(dict_json)
                else:

                    finishTime = datetime.now()
                    if abs(finishTime.minute - startTime.minute) >= WAITTING:
                        break
                    time.sleep(1)
            except Exception:
                s = traceback.format_exc()
                logger.error(s)

    @Time()
    def taskWork(self, dict_json):
        """
        具体任务的工作方法,主要调用爬虫完成数据爬取
        :param dict_json:
        :return:
        """
        token = dict_json['token']
        try:
            client = SpiderMain(dict_json)
            logger.info("不需要抓取图片验证码,token:%s" % token)
            p1 = threading.Thread(target=client.crawl, args=("user",))
            # p2 = threading.Thread(target=client.crawl, args=("auto",))
            p1.start()
            # p2.start()

        except Exception:
            s = traceback.format_exc()
            logger.error(s)
@Path()
def run():
    """
    入口
    :param x:
    :return:
    """
    global logger
    client = SpiderClient()
    client.progressWork()

# 读取配置文件
logger.info("waiting tasks ...")
run()











