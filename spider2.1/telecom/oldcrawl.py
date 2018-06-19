# coding=utf-8
import os
import re
import json
import time
import urllib
from datetime import datetime
from datetime import timedelta

import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from crawl_base import CrawlBase
from constants_spider import CRAWL_SUCCESS
from constants_spider import CRAWL_FAIL
from constants_spider import NEED_MORE
from constants_spider import CRAWL_TIMEOUT
from constants_spider import INPUT_ERROR
from constants_spider import OTHER_INFO
from constants_spider import TYPEVALUE
from constants_spider import WAITTIME

import request_handler



class SpiderMain(CrawlBase):

    # 测试地址 http://192.168.30.135:8080/9f_insight/telecom/crawlData?phoneNum=9a46be7e7b929b230f7cf0c0d488e0f4&password=666309b93e7c8cc0937b913437bfed74&userid=testuserid_12345&nocache=1
    # 发送验证码 http://192.168.30.135:8080/9f_insight/telecom/crawlData?token=5751123e-d862-4a33-b166-4a930ddb6bad&smscode=625493


    def __init__(self, dict_json):
        super(SpiderMain, self).__init__(dict_json, key=['password'])
        self.phoneNum = dict_json['phoneNum']
        self.password = dict_json['password']
        self.token = dict_json['token']
        self.session = requests.session()
        # 爬取数据月数
        self.month = 6
         
    def crawl(self):
        # 登录
        self.account = self.password_login()
        if self.status == None:
            self.logger.info('登录成功')
            data = {}
            data['pay_info'] = self.crawl_hisBill()
            # print json.dumps(data['pay_info'], ensure_ascii= False).encode('utf-8')
            self.verifycode_handler()
            if self.status == None:
                data['call_info'], data['sms_info'], data['net_info'] = self.get_detail()
                if self.status == None:
                    data['per_info'] = self.get_per_info()
                    result = json.dumps([data], ensure_ascii= False).encode('utf-8')
                    self.redisUtils.setNotify(type=TYPEVALUE, 
                                                token=self.token, 
                                                val="1", 
                                                decs="抓取成功！", 
                                                result=result)
                    self.logger.info('爬取成功')
                    # return True
                    return self.rmuserdirFlag
        self.logger.info(self.desc)
        self.redisUtils.setNotify(token=self.token, val=self.status, decs=self.desc)
        # return True
        return self.rmuserdirFlag

    def password_login(self):
        # 用户名密码登录，登录成功返回账户信息
        self.logger.info('开始登陆')
        account = request_handler.password_login(self.phoneNum, self.password)
        self.takePage('login.html',
                        json.dumps(account, ensure_ascii=False).encode('utf-8'),
                        '登陆返回')
        if account:
            self.logger.info('登录成功')
            return account
        self.status = INPUT_ERROR
        self.desc = '用户名或密码错误'

    def crawl_hisBill(self):
        self.logger.info('获取历史账单')
        daylist = self.get_date_list()
        mset = set([d[:6] for d in daylist])
        data = []
        for m in mset:
            hisBill = request_handler.fetch_hisBill(self.account, m)
            self.logger.info('爬取%s的历史账单'%m)
            self.takePage('hisBill_%s.html'%m, 
                            json.dumps(hisBill, ensure_ascii=False).encode('utf-8'),
                            '历史账单')
            # 每月一日至三日为出帐日，查不到上一月的账单，所以查询时会返回服务器发生异常
            if hisBill['Response']['ResponseData']['ResultDesc'] == u'服务器发生异常':
                self.logger.info('服务器发生异常，爬取月份%s'%m)
                continue
            if hisBill['Response']['ResponseData']['ResultDesc'] == u'未检索到数据':
                self.logger.info('未检索到数据，爬取月份%s'%m)
                continue
            if hisBill['Response']['ResponseData']['ResultDesc'] == u'账单处于出账期，请出账期以后进行查询':
                self.logger.info('账单处于出账期，请出账期以后进行查询，爬取月份%s'%m)
                continue
            i = {}
            d = hisBill['Response']['ResponseData']['Data']
            # 未付费用
            i['charge_pay'] = d['ChargeShouldpay'] if d['ChargeShouldpay'] != u'null' else ''
            # 已付费用
            i['charge_paid'] = d['ChargePaid'] if d['ChargePaid'] != u'null' else ''
            # 该月消费总额
            i['charge_all'] = d['ChargeAll'] if d['ChargeAll'] != u'null' else ''
            # 用户名（姓名）
            i['acct_name'] = d['AcctName'] if d['AcctName'] != u'null' else ''
            self.AcctName = i['acct_name']
            # 账户信息
            i['account_info'] = d['ChargeAccountInfo'] if d['ChargeAccountInfo'] != u'null' else ''
            # 日期
            i['pay_date'] = m
            # 可用预存款及可用赠款抵扣
            i['charge_discount'] = ''
            data.append(i)
        return data

    def verifycode_handler(self):
        res = request_handler.send_detail_verifycode(self.account)
        self.takePage('verifycode.html', 
                        json.dumps(res, ensure_ascii=False).encode('utf-8'),
                        '发送短信验证码返回')
        if res:
            self.logger.info(res)
            self.status = OTHER_INFO
            self.desc = res
            return
        self.redisUtils.setNotify(token = self.token,
                                    val = NEED_MORE, 
                                    decs='需要短信验证码')
        stime = datetime.now()
        self.logger.info('等待用户输入')
        while True:
            time.sleep(0.2)
            inputValue = self.redisUtils.getNotify(self.token, 'smscode')
            if inputValue:
                self.logger.info('用户输入短信验证码为%s'%inputValue)
                self.verifycode = inputValue
                break
            else:
                eclipseTimes = datetime.now() - stime
                if eclipseTimes.total_seconds() > WAITTIME:
                    self.logger.info('接收用输入输入超时:%s' % self.token)
                    self.status = INPUT_ERROR
                    self.desc = '接收用输入输入超时'
                    time.sleep(1)
                    return

    def get_detail(self):
        day_list = self.get_date_list()
        call_info = self.crawl_detail_list('1', '语音', day_list)
        if call_info:
            call_info = self.get_call(call_info)
            sms_info = self.crawl_detail_list('2', '短信', day_list)
            if sms_info:
                sms_info = self.get_sms(sms_info)
                net_info = self.crawl_detail_list('3', '流量', day_list)
                if net_info:
                    net_info = self.get_net(net_info)
                    return call_info, sms_info, net_info
        return None, None, None

    def get_per_info(self):
        return {
            # 账号归属省份
            'province' : '',
            # 账号归属城市
            'city' : '',
            # 身份证
            'id_card' : '',
            # 地址
            'addr' : '',
            # 等级
            'level' : '',
            # 数据源
            'user_source' : 'CHINA_TELECOM',
            # 账号星级
            'starLevel' : '',
            # 账号状态
            'state' : '',
            # 姓名
            'real_name' : self.AcctName,
            # 用户手机号码
            'phone' : self.phoneNum,
            # 运营商标识
            'flag' : 'China Telecom',
            # 入网时间
            'open_time' : '',
            # 客户性别
            'custsex' : '',
            # 使用套餐
            'packageName' : '',
            # 注册地址
            'certaddr' : '',
            # 最近登陆时间
            'lasttime' : '',
        }


    def get_net(self, net_info):
        new_net_info = []
        for m in net_info:
            for d in m:
                i = {}
                # 上网类型
                i['net_type'] = d['NetType'] if d['NetType'] != u'null' else ''
                # 上网时间
                i['net_time'] = d['NetTime'] if d['NetTime'] != u'null' else ''
                # 上网流量/KB
                i['net_flow'] = d['NetFlow'] if d['NetFlow'] != u'null' else ''
                # 花费金额
                i['net_fee'] = d['NetFee'] if d['NetFee'] != u'null' else ''
                # 上网地区
                i['net_area'] = d['NetArea'] if d['NetArea'] != u'null' else ''
                # 网络业务
                i['net_business'] = d['NetBusiness'] if d['NetBusiness'] != u'null' else ''
                new_net_info.append(i)
        return new_net_info

    def get_sms(self, sms_info):
        new_sms_info = []
        for m in sms_info:
            for d in m:
                i = {}
                # 起始时间
                i['sms_time'] = d['SmsTime'] if d['SmsTime'] != u'null' else ''
                # 对方号码
                i['sms_mobile'] = d['SmsMobile'] if d['SmsMobile'] != u'null' else ''
                # 通话费
                i['sms_fee'] = d['SmsCost'] if d['SmsCost'] != u'null' else ''
                # 发送地区
                i['sms_area  '] = d['SmsArea'] if d['SmsArea'] != u'null' else ''
                # 传送方式，1为接收，2为发送
                # 短信详单只有发送的短信才会有记录，接受短信没有记录
                i['sms_type'] = ''
                # 原数据中有SmsType,SmsStyle两个字段，但app页面上只展示了：时间、号码、话费三个字段，不清楚这两个字段的真实含义，以及SmsStyle是否为业务类型，所以下面的业务类型暂时设为空
                # 业务类型，01为国内短信，02为国际短信
                i['sms_style'] = ''
                new_sms_info.append(i)
        return new_sms_info


    def get_call(self, call_info):
        new_call_info = []
        for m in call_info:
            for d in m:
                i = {}
                # 呼叫类型
                i['trade_type'] = d['CallStyle'] if d['CallStyle'] != u'null' else ''
                # 拨打时间
                i['call_time'] = d['CallTime'] if d['CallTime'] != u'null' else ''
                # 对方号码
                i['receive_phone'] = d['CallMobile'] if d['CallMobile'] != u'null' else ''
                # 对方归属地
                i['called_home'] = d['CallArea'] if d['CallArea'] != u'null' else ''
                # 通话费
                i['call_fee'] = d['CallFee'] if d['CallFee'] != u'null' else ''
                # 通话时长
                i['trade_time'] = d['CallTimeCost'] if d['CallTimeCost'] != u'null' else ''
                # 本机通话地
                i['trade_addr'] = ''
                # 通话类型
                if d['CallType'] == u'0':
                    CallType = u'主叫'
                if d['CallType'] == u'1':
                    CallType = u'被叫'
                if d['CallType'] == u'null':
                    CallType = ''
                i['call_type'] = CallType
                # 记录内容
                i['call_data'] = ''
                new_call_info.append(i)
        return new_call_info



    def crawl_detail_list(self, detail_type, m, day_list):
        detail_list = []
        for day in day_list:
            # 如果是电信系统的内部错误，会在尝试5次，如果不成功则跳过
            # 如果是验证码不正确，直接返回
            error_falg = 0
            while True:
                # time.sleep(0.2)
                self.logger.info('正在爬取详单：%s的%s记录'%(day, m))
                day_data = self.get_detail_list(day, detail_type, m)
                if day_data == None:
                    return
                elif day_data == -1:
                    if error_falg == 5:
                        self.status = OTHER_INFO
                        self.desc = '电信系统内部错误'
                        self.logger.info('电信系统内部错误')
                        return
                    error_falg += 1
                    continue
                else:
                    break
            detail_list.append(day_data)
        return detail_list

        
    def get_detail_list(self, day, data_type, m):
        """
        发送请求查询详单
        短信详单只有发送的短信才会有记录，接受短信没有记录
        
        """

        # 获取数据
        detail = request_handler.fetch_detail(self.account, 
                                                self.verifycode, 
                                                day.decode('utf-8'), 
                                                data_type)
        self.takePage('detail_list_%s_%s.html'%(day, data_type),
                        json.dumps(detail, ensure_ascii=False).encode('utf-8'),
                        '%s%s详单'%(day, m))
        detail['Response']['ResponseData']['Date'] = day

        # 这里判断验证码的异常问题
        if detail['Response']['ResponseData']['ResultDesc'] == u'验证码不正确':
            self.logger.info('详单验证码错误或已超时')
            self.status = INPUT_ERROR
            self.desc = '短信验证码不正确'
            return
        if detail['Response']['ResponseData']['ResultDesc'] == u'第3方系统业务失败':
            return -1
        if detail['Response']['ResponseData']['ResultDesc'] == u'服务器发生异常':
            return -1

        detail_list = []
        date = detail['Response']['ResponseData']['Date']
        if detail['Response']['ResponseData']['Data'] != None:
            if detail['Response']['ResponseData']['Data']['Items'] != None:
                detail_item = detail['Response']['ResponseData']['Data']['Items']['Item']
                if isinstance(detail_item, dict):
                    detail_list.append(detail_item)
                else:
                    for i in detail_item:
                        detail_list.append(i)
        return detail_list

    def get_date_list(self):
        endday = datetime.now()
        day = timedelta(days=-(self.month*30))
        startday = (endday + day).strftime('%Y%m%d')
        timespan = timedelta(days=1)
        daylist = []
        while True:
            day = endday = (endday - timespan)
            sday = day.strftime("%Y%m%d")
            daylist.append(sday)
            if sday == startday:
                break
        return daylist

    # def data_handler(self, status, detail_list=None, hisBill=None):
    #     """
    #     处理爬取到的数据，爬取不成功直接向redis发送爬取失败的通知直接结束爬虫，如果爬取成功向redis发送通知后会返回数据
    #     密码错误，发送的是爬取失败，服务端暂未确定状态代码，后期需要完善

    #     """
    #     self.redisUtils.notifyComplete(constants.SUCCESS_SPIDER, self.token, '爬取成功')
    #     data = {
    #         'status' : str(status),
    #         'username': self.phoneNum,
    #         'source_name' : u'中国电信',
    #         'token' : self.token,
    #         'data' : {
    #             'detail_list' : detail_list,
    #             'hisBill' : hisBill,
    #         },
    #         'desc' : u'获取成功'
    #     }

    #     data = json.dumps(data, ensure_ascii = False).encode('utf-8')
    #     return data



    # def safecode_login(self):
    #     """ 发送登录验证码，并获取验证码 """

    #     # 登录成功返回账户信息
    #     # 验证码错误时会向redis发送通知，通知redis发送的是需要短信验证码，因为服务端暂未确定验证码错误的状态代码，后期需要完善，然后会自动等待用户发送再次键入验证码或者刷新验证码的指令，刷新指令为''(空)
    #     # 用户发送验证码失败的情况暂未考虑

    #     request_handler.send_login_verifycode(self.phoneNum)
    #     self.redisUtils.notifyComplete(constants.NEED_SMSCODE_STATUS, self.token, '需要短信验证码')
    #     self.logger.info('登录验证码已发送')
    #     while True:
    #         verifycode = self.get_safecode()
    #         if verifycode == 'reset':
    #             self.redisUtils.notifyComplete(constants.NEED_SMSCODE_STATUS, self.token, '需要短信验证码')
    #             self.logger.info('用户刷新验证码')
    #             request_handler.send_login_verifycode(self.phoneNum)
    #             self.logger.info('验证码已发送')
    #             continue
    #         elif verifycode == -3:
    #             return verifycode
    #         account = request_handler.verifycode_login(self.phoneNum, verifycode)
    #         if account:
    #             return account
    #         self.redisUtils.notifyComplete(constants.NEED_SMSCODE_STATUS, self.token, '验证码不正确')
    #         logger.info('验证码错误')

    # def get_detail(self, account, month):
    #     request_handler.send_detail_verifycode(account)
    #     logger.info('详单验证码已发送')
    #     self.redisUtils.notifyComplete(constants.NEED_SMSCODE_STATUS, self.token, '需要短信验证码')
    #     while True:
    #         verifycode = self.get_safecode()
    #         if verifycode == 'reset':
    #             self.redisUtils.notifyComplete(constants.NEED_SMSCODE_STATUS, self.token, '需要短信验证码')
    #             self.logger.info('用户刷新验证码')
    #             request_handler.send_login_verifycode(self.phoneNum)
    #             self.logger.info('验证码已发送')
    #             continue
    #         elif verifycode == -3:
    #             return verifycode
    #         detail_list = self.crawl_detail_list(month, verifycode, account)
    #         if detail_list == -4:
    #             self.redisUtils.notifyComplete(constants.NEED_SMSCODE_STATUS, self.token, '验证码不正确')
    #             logger.info('验证码错误')
    #             continue
    #         return detail_list

    # def get_safecode(self):
    #     # 从redis中获取验证码，会等待5分钟，5分钟如果没有收到会会向redis发送通知，通知redis发送的是爬取失败，因为服务端暂未确定验证码超时的状态代码，后期需要完善
    #     out_time = int((time.time())) + (3*60)
    #     while True:
    #         dict_json = self.redisUtils.getCode('telecom:code:' + self.token)
    #         # print dict_json
    #         if dict_json != None:
    #             verifycode = dict_json['password']
    #             logger.info('输入验证码为%s'%verifycode)
    #             return verifycode
    #         else:
    #             print out_time
    #             print int((time.time()))
    #             if int((time.time())) > out_time:
    #                 self.logger.info('等待用户超时')
    #                 return -3
    #             self.logger.info('正在等待验证码')
if __name__ == '__main__':

    username = '18101205290'
    password = '121212'
    token = '12343453451'
    login_type = '1'
    dianxin = Dianxin(username, password, login_type, token)
    print dianxin.get_safecode('123')
    # data, status = dianxin.crawl()
    # print status
    # # data = json.dumps(data, ensure_ascii = False).encode('utf-8')
    # with open('data.json', 'w') as f:
    #     f.write(data + '\n')


    # date_list = dianxin.get_date_list(6)
    # dianxin.crawl_hisBill(6)

    # month_list = dianxin.get_date_list(6)
    # crawl_hisBill = dianxin.crawl_hisBill(month_list)
    # crawl_hisBill = json.dumps(crawl_hisBill, ensure_ascii = False).encode('utf-8')
    # print crawl_hisBill



