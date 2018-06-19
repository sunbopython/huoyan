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
import time
import logging.config
import traceback
import threading
import functools
from datetime import datetime
from threadpool import ThreadPool
from threadpool import makeRequests

from __Utils.param_crypto import decryptKwargs
# from spider_email import sendMail
from __Utils.constants import WAITTING
from __Utils.redis_utils import RedisUtils


from unicom.crawl_main import SpiderMain
from unicom.constants_spider import THREAD_NUM, THREAD_Q_SIZE, SOURCE

reload(sys)
sys.setdefaultencoding("utf8")
logging.config.fileConfig('unicom/logging.config')
logger = logging.getLogger('flow')

def Time():
    def _deco(func):
        @functools.wraps(func)
        def _func(self, *args, **kwargs):
            start_time = datetime.now()
            value = func(self, *args, **kwargs)
            end_time = datetime.now()
            logger.info("共耗时：%ss"%(end_time - start_time))
            return value
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


    # def threadWork(self, t):
    def threadWork(self):
        """
        线程工作的方法，主要用户获取任务
        :param t:
        :return:
        """
        startTime = datetime.now()
        logger.info('开始等待获取任务')
        while True:
            try:
                # 从任务队列中获取任务数据
                dict_json = self.redisUtils.getCon(SOURCE)
                if dict_json is not None:
                    dict_json = decryptKwargs(dict_json)
                    name = dict_json['token']
                    # 将token放入到thread中
                    logger.info("获取到任务,%s" % name)
                    # sendMail(u"邮件log测试",'liujingyuan@insightcredit.cn')
                    dict_json.update({"result": []})
                    self.taskWork(dict_json)
                    break
                else:
                    finishTime = datetime.now()
                    # abs():返回数字的绝对值
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
        # token = dict_json['token']
        try:
            client = SpiderMain(dict_json)
            f = client.crawl()
            logger.info('任务结束：%s'%dict_json['token'])
            # 抓取成功则删除所保存的样本，如需保存可在爬虫中返回Ture
            if not f:
                client.rmUserdir(client.userdir)

            # logger.info("不需要抓取图片验证码,token:%s" % token)
            # p1 = threading.Thread(target=client.crawl, args=("user",))
            # p2 = threading.Thread(target=client.crawl)
            # p1.start()
            # p2.start()

        except Exception:
            self.redisUtils.setNotify(token=dict_json['token'], val='2', decs='爬虫爬取失败')
            s = traceback.format_exc()
            logger.error(s)
            logger.info('任务结束：%s'%dict_json['token'])






def run():
    """
    入口
    :param x:
    :return:
    """
    # global logger
    client = SpiderClient()
    # client.progressWork()
    client.threadWork()

if __name__ == '__main__':
    
    # # 读取配置文件
    # logger.info("waiting tasks ...")
    run()










