# coding=utf-8
import os
import re
import json
import time
import copy
from datetime import datetime
from datetime import timedelta
import traceback

import requests
from lxml import etree

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

from city_code import city_code
from city_code import province_code


class SpiderMain(CrawlBase):
    # 测试地址：
        # 雷雨：http://192.168.30.135:8080/9f_insight/unicom/crawlData?userid=testuserid_12345&password=4ac839efaa845b8df53eb7544dd2c234&phoneNum=8ca02cd076ec5a2ef7c9a0a53a225b85&nocache=1

        # 密码错误：http://192.168.30.135:8080/9f_insight/unicom/crawlData?userid=testuserid_12345&password=d43be604d21b7f4ccb94e94f51cb3225&phoneNum=c9b789e90b4fbf2cf52b18f2d27b1c04&nocache=1

    # 发送验证码：http://192.168.30.135:8080/9f_insight/unicom/crawlData?token=8c72e674-a9c9-4765-8dfd-6138645418c8&smscode=428979
    # token=&smscode=428979
    # 有时无法抓取流量详单，手动登陆联通查询也无法查到
    # 联通登陆密码输入共有五次机会，并需要短信验证码，输入错误三次，短信验证码更换为图片验证码，此爬虫给用户密码输入错误次数为三次，网站出现图片验证码时即告知用户密码尝试已到最大次数




    def __init__(self, dict_json):
        
        super(SpiderMain, self).__init__(dict_json, key=['password'])
        self.session = requests.session()
        self.username = dict_json['phoneNum']
        self.password = dict_json['password']
        self.token = dict_json['token']
        self.session = requests.session()
        self.month = 6
        # 这里是尝试使用cookie跳过验证码，尝试没有成功
        # cookie = {'uacverifykey':'3md725b1a4b66eee551949189765f7e8b33tyf'}
        # requests.utils.add_dict_to_cookiejar(self.session.cookies,cookie)
        
    def crawl(self):
        self.logger.info('登陆开始')
        if self.CheckNeedVerify() == u'true':
            self.logger.info('需要图片验证码')
            self.status = OTHER_INFO
            self.desc = '已达到最大尝试次数'
        else:
            self.logger.info('不需要图片验证码')
            self.get_verifycode()
            if self.status == None:
                self.verifycode_handler()
                if self.status == None:
                    self.login()
                    if self.status == None:
                        self.logger.info('登陆成功')
                        data = {}
                        data['per_info'] = self.get_baseInfo()
                        data['pay_info'] = self.get_hisBill()
                        data['call_info'] = self.get_detail('语音',
                                                        self.crawlVoice_detail,
                                                        self.voiceParse)
                        data['sms_info'] = self.get_detail('短信',
                                                        self.crawlMessage_detail,
                                                        self.messageParse)
                        data['net_info'] = self.get_detail('网络',
                                                        self.crawlNetFlow_detail,
                                                        self.netFlowPparse)
                        result = json.dumps([data], ensure_ascii= False).encode('utf-8')
                        self.takePage('data.json', result, '爬取结果')
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


    # def get_verifycode(self):
    #     url = 'https://uac.10010.com/portal/Service/CreateImage'
    #     par = {
    #         't': self.current_milli_time()
    #     }
    #     response = self.session.get(url, params = par)
    #     with open(self.code_path, 'w') as f:
    #         f.write(response.content)

    def login(self):
        url = 'https://uac.10010.com/portal/Service/MallLogin'
        hea = {
            'Connection':  'keep-alive',
            'Accept' : 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Referer': 'https://uac.10010.com/portal/homeLogin',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }
        par = {
            'callback' : 'jQuery172016378588867923072_' + self.current_milli_time(),
            'redirectURL' : 'http://www.10010.com',
            'req_time' : self.current_milli_time(),
            'userName' : self.username,
            'password' : self.password,
            'verifyCKCode': self.verifycode,
            'pwdType' : '01',
            'productType' : '01',
            'redirectType' : '01',
            'rememberMe' : '1',
            '_' : self.current_milli_time(),
        }

        response = self.session.get(url, headers = hea, params = par)
        self.takePage('login.html', response.text, '登陆返回')
        resultCode = re.findall(ur'resultCode:"(.*?)"', response.text)[0]
        pas = re.findall(ur'用户名或密码不正确', response.text)
        count = re.findall(ur'还有(\d)次机会', response.text)
        if resultCode == u'0000':
            return
        if resultCode == u'7231':
            self.status = INPUT_ERROR
            self.desc = '短信验证码不正确'
            return
        if pas:
            self.status = INPUT_ERROR
            if count:
                if count[0] == u'3':
                    self.desc = u'用户名或密码不正确，还有1次尝试机会'
                    return
                if count[0] == u'2':
                    self.desc = u'用户名或密码不正确，已达到最大尝试次数'
                    return
            else:
                self.desc = '用户名或密码不正确，还有2次尝试机会'
                return

                # 用户名或动态密码不正确，请重新输入。
                # 用户名或动态密码不正确，还有3次机会。
                # 用户名或动态密码不正确，还有2次机会。

    def verifycode_handler(self):
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
                    self.desc = '接收用用户输入超时'
                    time.sleep(1)
                    return

    def get_verifycode(self, codeUrl=None):
        # 发送登陆短信验证码，发送不成成功会重试，最多重试3次
        c = 0
        while c < 4:
            self.logger.info('发送登陆短信验证码')
            url = 'https://uac.10010.com/portal/Service/SendCkMSG'
            header = {
                'Connection': 'keep-alive',
                'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                'Referer': 'https://uac.10010.com/portal/homeLogin',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.8',
            }
            par = {
                'callback' : 'jQuery172016378588867923072_' + self.current_milli_time(),
                'req_time' : self.current_milli_time(),
                'mobile' : self.username,
                '_' : self.current_milli_time(),
            }
            response = self.session.get(url, headers = header, params = par)
            self.takePage('SendCkMSG.html', 
                            response.text, 
                            '发送短信验证码的请求结果')
            resultCode = re.findall(ur'resultCode:"(.*?)"', response.text)[0]
            if resultCode == u'0000':
                self.logger.info('发送成功')
                self.redisUtils.setNotify(token = self.token,
                                        val = NEED_MORE, 
                                        decs='需要短信验证码')
                return
            if resultCode == u'7096':
                # 距离上次发送不足1分钟，一分钟只能发送一条
                self.logger.info('距离上次发送不足1分钟')
                self.status = OTHER_INFO
                self.desc = '随机码发送频繁，距离上次发送不足1分钟，请稍后再试！'
                return
            if resultCode == u'7098':
                # 发送次数超过限制
                self.logger.info('发送次数超过限制')
                self.status = OTHER_INFO
                self.desc = '当日随机码 发送次数已达上限，请明日再试！'
                return
            c += 1
        self.rmuserdirFlag = True
        self.logger.info('验证码发送失败')
        self.status = OTHER_INFO
        self.desc = '系统繁忙，请稍后再试！'
        return

    def CheckNeedVerify(self):
        self.logger.info('检测是否需要图片验证码')
        url = 'https://uac.10010.com/portal/Service/CheckNeedVerify'
        par = {
            'callback' : 'jQuery172016378588867923072_1507626446505',
            'userName' : self.username,
            'pwdType' : '01',
            '_' : self.current_milli_time(),
        }
        response = self.session.get(url, params = par)
        self.takePage('CheckNeedVerify.html', 
                        response.text, 
                        '检查是否出现图片验证码的请求结果')
        res_json = re.findall(ur'\{.*\}', response.text)[0]
        return json.loads(res_json)['resultCode']

    def get_baseInfo(self):
        #访问联通用户中心页面会checklogin然后添加两个新的cookie
        self.logger.info('获取个人信息')
        url = 'http://iservice.10010.com/e3/static/check/checklogin/'
        param = {'_' : self.current_milli_time()}
        res = self.session.post(url, params = param, verify=False)
        self.takePage('baseInfo.html', res.text, '个人信息返回')
        res = json.loads(res.text.encode('utf-8'))
        data = {}
        # 账号归属省份
        data['province'] = province_code.get(res['userInfo']['provincecode'])
        # 账号归属城市
        data['city'] = city_code.get(res['userInfo']['citycode'])
        # 身份证
        data['id_card'] = res['userInfo']['certnum']
        # 地址
        data['addr'] = res['userInfo']['certaddr']
        # 等级
        data['level'] = ''
        # 数据源
        data['user_source'] = 'CHINA_UNICOM'
        # 账号星级
        data['starLevel'] = res['userInfo']['custlvl']
        # 账号状态
        data['state'] = ''
        # 姓名
        data['real_name'] = res['userInfo']['custName']
        # 用户手机号码
        data['phone'] = self.username
        # 运营商标识
        data['flag'] = 'China Unicom'
        # 入网时间
        data['open_time'] = res['userInfo']['opendate']
        # 客户性别
        data['custsex'] = res['userInfo']['custsex']
        # 使用套餐
        data['packageName'] = res['userInfo']['packageName']
        # 注册地址
        data['certaddr'] = ''
        # 最近登陆时间
        data['lasttime'] = res['userInfo']['lastLoginTime']
        # print json.dumps(data, ensure_ascii = False).encode('utf-8')
        return data

    def get_hisBill(self):
        url = 'http://iservice.10010.com/e3/static/query/queryHistoryBill'
        daylist = self.get_date_list()
        mset = set([d[:6] for d in daylist])
        # 这个集合供提取每月的第一天和最后一天使用
        self.month_list = copy.copy(mset)
        # 查询当月历史账单会返回上一个月的历史账单，这里把当月删掉
        mset.remove(datetime.now().strftime('%Y%m'))
        data_list = []
        for month in mset:
            self.logger.info('爬取历史账单，月份：%s'%month)
            param = {
                '_' : self.current_milli_time(),
                'accessURL' : 'http://iservice.10010.com/e4/skip.html?',
                'menuCode' : '000100020001',
                'menuCode' : '000100020001',
                'menuid' : '000100020001',
            }
            form = {
                'querytype' : '0001',
                'querycode' : '0001',
                'billdate' : month,
                'flag' : '2',
            }
            res = self.session.post(url, params = param, data = form, verify=False).text
            self.takePage('hisBill_%s.html'%month, res, '历史账单返回')
            data = self.hisBill_parse(json.loads(res), month)
            if data:
                data_list.append(data)
        return data_list


    def hisBill_parse(self, res, month):
        print res
        self.logger.info('解析历史账单返回数据')
        if res.has_key('errorMessage'):
            self.logger.info('联通服务器错误')
            self.logger.info(res['errorMessage']['respDesc'])
            return {}
        if res.has_key('errormessage'):
            self.logger.info('联通服务器错误')
            self.logger.info(res['errormessage']['errmessage'])
            # print res['errormessage']['errmessage']
            return {}
        try:
            data = {}
            # 未付费用
            data['charge_pay'] = ''
            # 已付费用
            data['charge_paid'] = ''
            # 该月消费总额
            data['charge_all'] = res['result']['allfee']
            # 用户名（姓名）
            data['acct_name'] = res['userinfo']['custname']
            # 账户信息
            data['account_info'] = res['userinfo']['currentid']
            # 日期
            data['pay_date'] = month
            # 可用预存款及可用赠款抵扣
            data['charge_discount'] = res['result']['writeofffee']
            # # 实际应缴合计
            # data['ChargePaid'] = res['result']['balance']
            # # 日期
            # data['Date'] = res['result']['cycleid']
        except KeyError as e:
            s = traceback.format_exc()
            self.logger.error(s)
            self.logger.info('历史账单数据解析格式错误，尝试第二种格式匹配')
            data = self.hisBill_parse2(res, month)
        return data

    def hisBill_parse2(self, res, month):
        data = {}
        # 未付费用
        data['charge_pay'] = ''
        # 已付费用
        data['charge_paid'] = ''
        # 该月消费总额
        data['charge_all'] = res['nowFee']
        # 用户名（姓名）
        data['acct_name'] = res['userInfo']['custName']
        # 账户信息
        data['account_info'] = res['userInfo']['currentID']
        # 日期
        data['pay_date'] = month
        # 可用预存款及可用赠款抵扣，或者本月充值
        try:
            data['charge_discount'] = res['paySum']
        except KeyError as e:
            data['charge_discount'] = ''
        # # 实际应缴合计
        # data['ChargePaid'] = res['payTotal']
        # # 日期
        # data['Date'] = res['billcycle']
        self.logger.info('第二种格式匹配成功')
        return data

    def get_detail(self, dtype, craw_fun, parse_fun):
        seDate = self.startEndList()
        result = []
        for m, d in seDate.items():
            start_day = d[-1]
            end_day = d[0]
            pageSize = '100'
            if dtype == '网络':
                start_day = start_day[:4]+ '-' +start_day[4:6] + '-' + start_day[6:]
                end_day = end_day[:4]+ '-' +end_day[4:6] + '-' + end_day[6:]
                pageSize = '100'
            # self.logger.info('爬取从%s到%s的%s详单第1页'%(start_day, end_day, dtype))
            item = craw_fun(start_day, end_day, '1', pageSize)
            item, pages = parse_fun(item)
            result += item
            if len(item) != 0:
                if dtype == '网络':
                    pages = [str(p) for p in range(2, int(pages)+1)]
                else:
                    pages = [str(p['pageNo']) for p in pages[1:]]
                for pageNo in pages:
                    self.logger.info('爬取从%s到%s的%s详单第%s页'%(start_day, end_day, pageNo, dtype))
                    item = craw_fun(start_day, end_day, pageNo, pageSize)
                    item, pages = parse_fun(item)
                    result += item
        return result

    def crawlVoice_detail(self, start_day, end_day, pageNo, pageSize):
        error_flag = 0
        while True:
            url = 'http://iservice.10010.com/e3/static/query/callDetail'
            param = {
                '_': self.current_milli_time(),
                'accessURL' : 'http//iservice.10010.com/e4/query/bill/call_dan-iframe.html?',
                'menuCode' : '000100030001',
                'menuid' : '000100030001',
            }
            form = {
                'pageNo' : pageNo,
                'pageSize' : pageSize,
                'beginDate' : start_day,
                'endDate' : end_day,
            }
            response = self.session.post(url, params = param, data = form, verify=False).text
            self.logger.info('爬取从%s到%s第%s页的语音详单'%(start_day, end_day, pageNo))
            self.takePage('voice_%s_%s_%s.html'%(start_day, end_day, pageNo), response, '语音详单')
            if re.findall(ur'出了一点点问题，请您稍候再试或立即反馈我们处理',response) or \
                    re.findall(ur'业..务..连..接..超....时....过一会再来吧', response) or \
                    re.findall(ur'4114030193', response):
                error_flag += 1
                if error_flag == 5:
                    self.logger.info('爬取从%s到%s第%s页的语音详单时，联通服务器错误'%(start_day, end_day, pageNo))
                    return
                continue
            if re.findall(ur'无详单记录', response) or \
                    re.findall(ur'2114030170', response):
                self.logger.info('%s到%s第%s页，无语音详单记录'%(start_day, end_day, pageNo))
                return

            response = json.loads(response)
            return response

    def crawlMessage_detail(self, start_day, end_day, pageNo, pageSize):
        error_flag = 0
        while True:
            url ='http://iservice.10010.com/e3/static/query/sms'
            param = {
                '_': self.current_milli_time(),
                'accessURL': 'http://iservice.10010.com/e4/query/calls/call_sms-iframe.html?',
                'menuCode': '000100030002',
                'menuid': '000100030002',
            }
            form = {
                'pageNo' : pageNo,
                'pageSize' : pageSize,
                'begindate' : start_day,
                'enddate' : end_day,
            }
            response = self.session.post(url, params = param, data = form, verify=False).text
            self.logger.info('爬取从%s到%s第%s页的短信详单'%(start_day, end_day, pageNo))
            self.takePage('message_%s_%s_%s.html'%(start_day, end_day, pageNo), response, '短信详单')
            if re.findall(ur'出了一点点问题，请您稍候再试或立即反馈我们处理',response) or \
                    re.findall(ur'业..务..连..接..超....时....过一会再来吧', response) or \
                    re.findall(ur'4114030193', response):
                error_flag += 1
                if error_flag == 5:
                    self.logger.info('爬取从%s到%s第%s页的短信详单时，联通服务器错误'%(start_day, end_day, pageNo))
                    return
                continue
            if re.findall(ur'无详单记录', response) or \
                    re.findall(ur'2114030170', response):
                self.logger.info('%s到%s第%s页，无短信详单记录'%(start_day, end_day, pageNo))
                return
            response = json.loads(response)
            return response

    def crawlNetFlow_detail(self, start_day, end_day, pageNo, pageSize):
        error_flag = 0
        while True:
            # pageSize = '20'
            url = 'http://iservice.10010.com/e3/static/query/CallWlanRecord'
            # url ='http://iservice.10010.com/e3/static/query/callFlow'
            param = {
                '_': self.current_milli_time(),
                'accessURL': 'http://iservice.10010.com/e4/query/basic/call_flow_iframe1.html?menuCode=000100030006&menuid=000100030006',
                # 'accessURL': 'http://iservice.10010.com/e4/query/basic/call_flow_iframe1.html',
                # 'menuCode': '000100030004',
                # 'menuid': '000100030004',
            }
            form = {
                'pageNo' : pageNo,
                'pageSize' : pageSize,
                'beginDate' : start_day,
                'endDate' : end_day,
            }
            response = self.session.post(url, params = param, data = form, verify=False).text
            self.logger.info('爬取从%s到%s第%s页的网络详单'%(start_day, end_day, pageNo))
            self.takePage('netflow_%s_%s_%s.html'%(start_day, end_day, pageNo), response, '网络详单')
            if re.findall(ur'出了一点点问题，请您稍候再试或立即反馈我们处理',response) or \
                    re.findall(ur'业..务..连..接..超....时....过一会再来吧', response) or \
                    re.findall(ur'4114030193', response):
                error_flag += 1
                if error_flag == 5:
                    self.logger.info('爬取从%s到%s第%s页的网络详单时，联通服务器错误'%(start_day, end_day, pageNo))
                    return
                continue
            if re.findall(ur'暂无详单数据', response) or \
                    re.findall(ur'2114030170', response):
                self.logger.info('%s到%s第%s页，无网络详单记录'%(start_day, end_day, pageNo))
                return
            response = json.loads(response)
            return response

    def voiceParse(self, data):
        if data is None:
            return [],[]
        self.logger.info('解析语音详单返回数据')
        data_list = []
        for i in data['pageMap']['result']:
            newData = {}
            # 呼叫类型
            newData['trade_type'] = i['calltypeName']
            # 拨打时间
            newData['call_time'] = i['calldate'] + '-' + i['calltime']
            # 对方号码
            newData['receive_phone'] = i['othernum']
            # 对方归属地
            newData['called_home'] = i['calledhome']
            # 通话费
            newData['call_fee'] = i['totalfee']
            # 通话时长
            newData['trade_time'] = i['calllonghour']
            # 本机通话地
            # 这个还有一个homearea字段两个字段总是相同的
            newData['trade_addr'] = i['homeareaName']
            # 通话类型
            newData['call_type'] = i['landtype']
            # 记录内容
            newData['call_data'] = ''
            data_list.append(newData)
        pages = data['pageMap']['pages']
        return data_list, pages

    def messageParse(self, data):
        if data is None:
            return [],[]
        self.logger.info('解析短信详单返回数据')
        data_list = []
        # 出现这种情况是因为可能请求发送日期久于联通所允许查询日期
        if data.get('isSuccess') == False:
            self.logger.info('请求未成功，联通服务器异常')
            return [], []
        for i in data['pageMap']['result']:
            newData = {}
            # 起始时间
            newData['sms_time'] = i['smsdate'] + '-' + i['smstime']
            # 传送方式，1为接收，2为发送
            newData['sms_type'] = i['smstype']
            # 对方号码
            newData['sms_mobile'] = i['othernum']
            # 业务类型，01为国内短信，02为国际短信
            newData['sms_style'] = i['businesstype']
            # 通话费
            newData['sms_fee'] = i['amount']
            # 发送地区
            newData['sms_area'] = ''
            data_list.append(newData)
        pages = data['pageMap']['pages']
        return data_list, pages

    def netFlowPparse(self, data):
        data_list = []
        if data == '-1':
            return [], []
        if data is None:
            return [],[]
        self.logger.info('解析网络详单返回数据')
        try:
            for item in data['pagelist']:
                newData = {}
                # 上网时间
                newData['net_time'] = item['begindate'].replace('-', '') + '-' + item['begintime'].replace('-', '')
                # 网络类型
                newData['net_type'] = item['nettypeformat']
                # 上网地区
                newData['net_area'] = item['homearea']
                # 上网流量/KB
                newData['net_flow'] = item['pertotalsm']
                # 花费金额
                newData['net_fee'] = item['totalfee']
                # 网络业务
                newData['net_business'] = ''
                data_list.append(newData)
            pages = data['totalpage']
        except KeyError as e:
            s = traceback.format_exc()
            self.logger.error(s)
            self.logger.info('网络账单数据解析格式错误，尝试第二种格式匹配')
            data_list, pages = self.netFlowParse2(data)
        return data_list, pages

    def netFlowParse2(self, data):
        self.logger.info('尝试第二种格式匹配')
        data_list = []
        for item in data['result']['pagemap']['result']:
            newData = {}
            # 上网时间
            newData['net_time'] = item['begindate'].replace('-', '') + '-' + item['begintime'].replace('-', '')
            # 网络类型
            newData['net_type'] = item['nettypename']
            # 上网地区
            newData['net_area'] = item['homeareaname']
            # 上网流量/KB
            newData['net_flow'] = item['totalbytes']
            # 花费金额
            newData['net_fee'] = item['totalfee']
            # 网络业务
            newData['net_business'] = ''
            data_list.append(newData)
        pages = data['result']['pagemap']['totalpages']
        self.logger.info('第二种格式匹配成功')
        return data_list, pages

    def startEndList(self):
        daylist = self.get_date_list()
        res = {m:[] for m in self.month_list}
        for d in daylist:
            res[d[0:6]].append(int(d))
        res = {k:[str(max(v)), str(min(v))] for k, v in res.items()}
        return res

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


if __name__ == '__main__':


    # 雷雨_河北
    username = ''
    password = ''




    token = 'fadskjfjfasdjldsnfda'
    dict_json = {
        'username':username,
        'password':password,
        'token':token,
    }
    liantong = Liantong(dict_json)
    liantong.crawl()
