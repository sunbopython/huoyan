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
# redis常量定义
WAITTING = 3 # 程序等待时间（分）

DEFAULT_EXPIRE_TIME = 3600      # 所有key的失效时间，1小时
WAIT_EXPIRE_TIME = 300          # 失效时间，用于分步骤爬虫，下一步骤等待用户交互的时间
DEFAULT_BLOCK_TIME = 60         # list阻塞pop时间，120s
EXPIRE_TIME_1D = 86400          # cache的失效时间，1天
TASK_VALID_TIME = 10            # 任务的有效时间s

'''redis地址'''
# 以逗号分隔
# REDIS = "192.168.30.135:6380,192.168.30.135:6381,192.168.30.135:6382,192.168.30.135:6383,192.168.30.135:6384,192.168.30.135:6385"
REDIS = "127.0.0.1:6380,127.0.0.1:6381,127.0.0.1:6382,127.0.0.1:6383,127.0.0.1:6384,127.0.0.1:6385"
# REDIS = "192.168.30.123:6380,192.168.30.123:6381,192.168.30.123:6382,192.168.30.123:6383,192.168.30.123:6384,192.168.30.123:6385"
# HOST = "192.168.30.135"
# PORT = "6380,6381,6382,6383,6384,6385"


'''ip代理服务器'''
PROXYADDR = "http://127.0.0.1:5000/ip"


'''推送常量定义'''
PUSH_DATA_URL = 'http://10.0.3.12:9090/ent/credit'      # 推送大数据平台的接口测试地址（服务器29）


'''调度类常量'''
# 默认线程数
THREAD_NUM = 5
# THREAD_NUM = 1
# 默认线程队列深度
THREAD_Q_SIZE = 1



