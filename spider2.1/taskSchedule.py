#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 30线程+100请求 -》 6-7s
from multiprocessing import Process
from threadpool import ThreadPool, makeRequests
import time, os, re, sys
from __Utils.constants import THREAD_NUM, THREAD_Q_SIZE
from __Utils.redis_utils import RedisUtils
import logging.config
logging.config.fileConfig('__Utils/logger.conf')
logger = logging.getLogger()
# import sys
# sys.path.append('../../RealTime')
spider_list = [
    'ss_beijing',
    'telecom',
    'unicom',
    # 孙博
    # 宁波搜房网
    'fangningbo',
    'chinamobile',
    'gjjbeijing',
    # 宁波房产交易
    'spider_translate',
    # 宁波企业信用网
    'nbcredit',
    # 国税局发票
    'tax',
    'gsxt',
    'executor',
    'executored',
    'dishonesty'
]

def imptask(name):
    try:
        if name not in spider_list:
            # logger.info('爬虫不存在:%s'%name)
            return
        command_string = "python "+name+"/spider_main.py"
        logger.info("Running -> "+command_string)
        os.system(command_string)
    except Exception as e:
        print e

def threadWork(t):
    """
    进程工作，用来启动多个线程
    :param x:
    :return:
    """
    redisUtils = RedisUtils()
    thread_pool = ThreadPool(THREAD_NUM*10, q_size=THREAD_Q_SIZE)
    dict_json = redisUtils.getCons()
    logger.debug("Now have tasks -> " + str(dict_json))
    if dict_json != []:
        try:
            for i in dict_json:
                spider_name = re.findall('spider_(.*):task', i)[0]
            # for i in [i.split(":")[0] for i in dict_json]:
                requests = makeRequests(imptask, [spider_name])
                thread_pool.putRequest(requests[0])
            thread_pool.wait()
        except Exception as e:
            logger.error(e)
    else:
        time.sleep(1)

if __name__ == "__main__":
    print spider_list
    while 1:
        # print "*",
        for i in xrange(1):
            # logger.info("thread -> "+str(i))
            Process(target=threadWork, args=('',)).start()
        time.sleep(1)

# 德州公积金
# 邵阳公积金
# 石家庄公积金
# 咸阳公积金
# 安阳社保
# 北京社保
# 宁波社保
# 大连社保
# 重庆社保
# 株洲社保
# 电信运营商
# 联通运营商实
# 宁波58同城敏感词
# 质量管理体系认证（ISO9000）
# 企业招聘信息
# 人民法院公告网
# 建设银行账户

# 中国裁判文书网
# 失信人
# 被执行人
# 宁波搜房网
# 宁波房产交易
# 宁波企业信用网
# 国税局发票
# 国家企业信息公示系统

# 搜索引擎-不良嗜好
# 搜索引擎-敏感词

# 公积金-河南新乡
# 公积金-广西宜春
# 山东德州社保信息
# 山西太原市社保信
# 湖南邵阳市社保信
# {'status': '', 'nocache': '1',
#  'date_filter_min': '\x87zD\xc1\x9e-\xd0E\x07`\xc4\\\x18\xa1\x82e',
#  'date_filter_max': '\x87zD\xc1\x9e-\xd0E\x07`\xc4\\\x18\xa1\x82e',
#  'title': '\xf2_\xa8\xae\xdb\xb8\xa3v\xd8\x1d\xb19\x12\x90d\x1c7\xd0W\x17\xd1h\x07\x92\xce\x11F\xbd\xd1\xa9?\xfar\xe9j\xf5O+"\xb4\xf4xO\xc5\x9d\xc0\x1b\xe2',
#  'userid': 'yinzhouyinhang', 'project': '\x87zD\xc1\x9e-\xd0E\x07`\xc4\\\x18\xa1\x82e',
#  'token': '4840bcb9-ae4c-4fcf-946b-b0cac1fc3745',
#  'project_district': '\xe1\x8c_ \xc0\xdfWi\x99\xdf\x0b\xe2#W\xd1\x82',
#  'desc': '\xe6\xad\xa3\xe5\x9c\xa8\xe7\x88\xac\xe5\x8f\x96...'}




