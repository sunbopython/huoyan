# coding=utf-8
import os
import re
import json
import time
from datetime import datetime

import requests
from lxml import etree
import pytesseract
from PIL import Image

from crawl_base import CrawlBase
from constants_spider import CRAWL_SUCCESS
from constants_spider import CRAWL_FAIL
from constants_spider import NEED_MORE
from constants_spider import CRAWL_TIMEOUT
from constants_spider import INPUT_ERROR
from constants_spider import OTHER_INFO
from constants_spider import TYPEVALUE
from constants_spider import WAITTIME
import data_parse





class SpiderMain(CrawlBase):
    # 北京社保拥有职工用户和居民用户两种用户类型，由于没有居民用户类型的测试账号，
    # 无法得知两种用户类型的页面结构和社保信息是否一致，现爬虫只能爬取职工用户
    # 测试地址：
    # 刘亚奇： http://192.168.30.135:8080/9f_insight/ss_beijing/crawlData?userid=testuserid_12345&password=c3b94f2e170033a82b5635003e4cf6ac&idcard=f4c3ba15949b54bb08119359af1dfb339f88053c66e0959fe4148e425764fb53&nocache=1
    # 廖德强： http://192.168.30.135:8080/9f_insight/ss_beijing/crawlData?userid=testuserid_12345&password=71bb84f567d4a864b7c4386e7009bbd7&idcard=b5a9d19c20f0562309b69ac2a1de32ffd4163d3dea28042c0fca8fd7a06e9e80&nocache=1
    #     未注册账户或账户手机号未完善:
    #         http://192.168.30.135:8080/9f_insight/ss_beijing/crawlData?userid=testuserid_12345&password=fcd8d5ac109767b5456d2546284d06e0&idcard=101876a4e27045b03cde13c262d3f2b5&nocache=1
    #     密码错误:
    #         http://192.168.30.135:8080/9f_insight/ss_beijing/crawlData?userid=testuserid_12345&password=fcd8d5ac109767b5456d2546284d06e0&idcard=b5a9d19c20f0562309b69ac2a1de32ffd4163d3dea28042c0fca8fd7a06e9e80&nocache=1
    #     提交短信验证码： http://192.168.30.135:8080/9f_insight/ss_beijing/crawlData?&token=ed5c6413-f983-48dd-a1fd-d18fc125dfc4&smscode=1234

    def __init__(self, dict_json):
        super(SpiderMain, self).__init__(dict_json, key=['password'])
        self.idcard = dict_json['idcard']
        self.password = dict_json['password']
        self.tokens = dict_json['token']
        self.session = requests.session()

    def crawl(self):
        self.login()
        if self.status is None:
            personal = self.personal_information_handler()
            time_now_year = int(datetime.now().strftime('%Y'))
            # 养老：
            oldage = data_parse.oldage_information_handler(self.session, time_now_year, self.card)
            # 失业：
            unemployment = data_parse.unemployment_information_handler(self.session, time_now_year, self.card)
            # 工伤：
            injuries = data_parse.injuries_information_handler(self.session, time_now_year, self.card)
            # 生育：
            maternity = data_parse.maternity_information_handler(self.session, time_now_year, self.card)
            # 医疗：
            medicalcare = data_parse.medicalcare_information_handler(self.session, time_now_year, self.card)
            record = oldage+unemployment+injuries+maternity+medicalcare
            personal['type_B'] = record
            result = json.dumps([personal], ensure_ascii=False).encode('utf-8')
            self.takePage('result.json', result)
            self.redisUtils.setNotify(type=TYPEVALUE, 
                                        token=self.token, val="1", 
                                        decs="抓取成功！", result=result)
            # return True
            return self.rmuserdirFlag
        self.logger.info(self.desc.decode('utf-8'))
        self.redisUtils.setNotify(token=self.token, val=self.status, 
                                    decs=self.desc)
        # return True
        return self.rmuserdirFlag

    def login(self):
        # 城镇职工用户登录页
        login_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/login.jsp'
        # 图片验证码地址
        response = self.session.get(login_url)
        self.takePage('home.html', response.text, '城镇职工用户登录页')
        codeUrl = lambda : 'http://www.bjrbj.gov.cn/csibiz/indinfo/validationCodeServlet.do?d=%s' % self.current_milli_time
        self.verifycode_handler(codeUrl=codeUrl)
        if self.status is not None:
            return
        self.redisUtils.setNotify(token = self.token, val = NEED_MORE, decs='需要短信验证码')
        self.logger.info(u'短信验证码已发送')
        self.message_verfycode_handler()

        # # 构建登录数据
        # postData = {
        #     'type' : 1,
        #     'flag' : 3,
        #     'j_username' : self.username,      # 身份证号
        #     'j_password' : self.password,      # 密码
        #     'safecode' : safecode,             # 验证码
        #     'x' : 41,
        #     'y' : 18,
        # }

        # self.session.post(loginURL, data = postData)
        # page = self.session.get(home_url).text
        # page = etree.HTML(page)
        # info = page.xpath('//form[@id="printForm"]')
        # if len(info) == 0:
        #     return 0
        # return 1

    def judge_verifycode(self, inputValue, ResetCode):
        # 提交身份证号、密码、图片验证码、并请求短信
        sms_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/passwordSetAction!getTelSafeCode'
        form = {
            'idCode': self.idcard,
            'logPass': self.password,
            'safeCode': inputValue,
        }
        response = self.session.post(sms_url, data=form)
        self.takePage('sms.html', response.text, '提交身份证号、密码、图片验证码、并请求短信') 
        if re.findall(ur'0-附加码错误', response.text):
            return
        elif re.findall(ur'1-短信验证码已发送至您的手机', 
                response.text):
            self.safecode = inputValue
            return True
        elif re.findall(ur'0-密码输入错误', response.text):
            self.status = INPUT_ERROR
            self.desc = '密码错误'
        elif re.findall(ur'请您完善您的注册手机号或者通过”我要注册“功能进行用户注册', 
                response.text):
            self.status = OTHER_INFO
            self.desc = '未注册账户或账户手机号未完善'
        elif re.findall(ur'您的短信验证码还在有效期内', 
                response.text):
            count = re.findall(ur'请\d+秒后再获取。', response.text)
            self.status = OTHER_INFO
            self.desc = '您的短信验证码还在有效期内，请%s秒后再获取。' % count[0]
        else:
            self.logger.info(u'爬虫遇到了意料之外的情况，已记录html页面')
            self.rmuserdirFlag = True
        return True

    def message_verfycode_handler(self):
        stime = datetime.now()
        self.logger.info(u'等待用户输入')
        while True:
            inputValue = self.redisUtils.getNotify(self.token, 'smscode')
            if inputValue:
                self.login_check(inputValue)
                return
            else:
                eclipseTimes = datetime.now() - stime
                if eclipseTimes.total_seconds() > WAITTIME:
                    self.logger.info('接收用输入超时:%s' % self.token)
                    self.status = INPUT_ERROR
                    self.desc = '接收用输入超时'
                    time.sleep(1)
                    return

    def login_check(self, smscode):
        url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/login_check'
        form = {
            'type' : '1',
            'flag' : '3',
            'j_username' : self.idcard,
            'j_password' : self.password,
            'safecode' : self.safecode,
            'i_phone' : smscode,
        }
        response = self.session.post(url, data=form)
        self.takePage('login_check.html', response.text, '提交短信验证码')
        if re.findall(u'短信验证码错误', response.text):
            self.status = INPUT_ERROR
            self.desc = '短信验证码输入有误'
        if re.findall(u'服务器繁忙，请稍后再试', response.text):
            self.status = OTHER_INFO
            self.desc = '服务器繁忙，请稍后再试'

    def personal_information_handler(self):
        """ 获取个人信息 """

        # 个人信息：
        self.logger.info('获取个人信息')
        personal_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indNewInfoSearchAction'
        personal_information = self.session.get(personal_url)
        self.takePage('personalInfo.html', personal_information.text, '个人信息页')
        result = etree.HTML(personal_information.text)
        form = result.xpath('//body/form[@id="printForm"]')[0]
        repl = lambda res : res.replace('\r', '').replace('\n', '').replace('\t', '')
        personal = {}
        info_1 = repl(''.join(form.xpath('./table[1]//text()')))
        info_2 = repl(''.join(form.xpath('./table[2]//tr[2]//text()')))
        info_3 = repl(''.join(form.xpath('./table[2]//tr[3]//text()')))
        info_4 = repl(''.join(form.xpath('./table[2]//tr[4]//text()')))
        info_5 = repl(''.join(form.xpath('./table[2]//tr[5]//text()')))
        info_6 = repl(''.join(form.xpath('./table[2]//tr[6]//text()')))
        info_7 = repl(''.join(form.xpath('./table[2]//tr[7]//text()')))
        info_8 = repl(''.join(form.xpath('./table[2]//tr[8]//text()')))
        info_9 = repl(''.join(form.xpath('./table[2]//tr[9]//text()')))
        info_10 =repl( ''.join(form.xpath('./table[2]//tr[10]//text()')))
        info_11 =repl( ''.join(form.xpath('./table[2]//tr[11]//text()')))
        info_12 =repl( ''.join(form.xpath('./table[2]//tr[12]//text()')))
        info_13 =repl( ''.join(form.xpath('./table[2]//tr[13]//text()')))
        info_14 =repl( ''.join(form.xpath('./table[2]//tr[14]//text()')))
        info_15 =repl( ''.join(form.xpath('./table[2]//tr[15]//text()')))
        info_16 =repl( ''.join(form.xpath('./table[2]//tr[16]//text()')))
        info_17 =repl( ''.join(form.xpath('./table[2]//tr[17]//text()')))
        info_18 =repl( ''.join(form.xpath('./table[2]//tr[18]//text()')))
        info_19 =repl( ''.join(form.xpath('./table[2]//tr[19]//text()')))
        info_20 =repl( ''.join(form.xpath('./table[2]//tr[20]//text()')))
        info_21 =repl( ''.join(form.xpath('./table[2]//tr[21]//text()')))

        # 单位名称
        personal['company_name'] = re.findall(ur'单位名称：(.*)统一社会信用代码', info_1)[0].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '').strip()
        # 组织机构代码/单位编号
        personal['unitNumber'] = re.findall(ur'统一社会信用代码（组织机构代码）：(.*)社会保险登记号', info_1)[0].strip()
        # 姓名/用户姓名
        personal['pername'] = re.findall(ur'姓 名(.*)\*公民身份号', info_2)[0]
        # 公民身份号码（社会保障号码）/社保卡号码/个人编号
        self.card = re.findall(ur'会保障号码）(.*)', info_2)[0]
        personal['socialSecurityCardNumber'] = self.card
        personal['personalid'] = self.card
        personal['number'] = self.card
        # 性别
        personal['gender'] = re.findall(ur'性 别(.*)\*出生', info_3)[0]
        # 生日/出生日期
        personal['birthday'] = re.findall(ur'出生日期(.*)', info_3)[0]
        # 民族
        personal['nationalities'] = re.findall(ur'民 族(.*)\*国家', info_4)[0]
        # 国家/地区/国家
        # personal['region'] = re.findall(ur'地区(.*)', info_4)[0]
        personal['country'] = re.findall(ur'地区(.*)', info_4)[0]
        # 参加工作日期/起始年月
        personal['beigin_data'] = re.findall(ur'工作日期(.*)', info_5)[0]
        # 户口性质
        personal['account'] = re.findall(ur'户口性质(.*)', info_6)[0]
        # 户口所在地
        personal['account_add'] = re.findall(ur'所在地地址(.*)\*户口所在地邮政编码', info_7)[0]
        # # 户口所在地邮编  
        # personal['account_add_zip'] = re.findall(ur'所在地邮政编码(.*)', info_7)[0]
        # 居住地址/家庭住址/通讯地址
        personal['home_add'] = re.findall(ur'地址(.*)居住地', info_8)[0]
        personal['phone_add'] = re.findall(ur'地址(.*)居住地', info_8)[0]
        # # 居住地址邮编
        # personal['home_add_zip'] = re.findall(ur'邮政编码(.*)', info_8)[0]
        # # 选择邮寄社会保险对账单地址 
        # personal['bill_address'] = re.findall(ur'账单地址(.*)对账单', info_9)[0]
        # # 获取对账单方式
        # personal['get_bill'] = re.findall(ur'对账单方式(.*)电子邮件地址', info_10)[0]
        # # 电子邮件地址
        # personal['person_email'] = re.findall(ur'电子邮件地址(.*)\*文化程度', info_10)[0]
        # 文化程度
        personal['culture'] = re.findall(ur'文化程度(.*)', info_10)[0]
        # # 参保人电话
        # personal['telephone'] = re.findall(ur'保人电话(.*)参保人手机', info_11)[0]
        # 参保人手机/联系电话
        personal['phone'] = re.findall(ur'参保人手机(.*)\*申报月均工资', info_11)[0]
        # 申报月均工资收入/申报工资/月缴费基数
        personal['wages'] = re.findall(ur'均工资收入（元）(.*)', info_11)[0]
        personal['month_pay'] = re.findall(ur'均工资收入（元）(.*)', info_11)[0]
        # # 证件类型
        # personal['id_type'] = re.findall(ur'证件类型(.*)\*证件号码', info_12)[0]
        # # 证件号码
        # personal['id_number'] = re.findall(ur'证件号码(.*)', info_12)[0]
        # 委托代发银行名称/当年公司缴划账户
        personal['companyaccount'] = re.findall(ur'委托代发银行名称(.*)\*委托代发银行账号', info_13)[0]
        # 委托代发银行账号/当年个人缴划账户
        personal['account'] = re.findall(ur'委托代发银行账号(.*)', info_13)[0]
        # # 离退休类别
        # personal['retire_type'] = re.findall(ur'离退休类别(.*)离退休日期', info_15)[0]
        # # 离退休日期
        # personal['retire_date'] = re.findall(ur'离退休日期(.*)', info_15)[0]
        # 定点医疗机构1
        # personal['medical_institution_1'] = re.findall(ur'定点医疗机构1(.*)定点医疗机构', info_16)[0]
        # # 定点医疗机构2
        # personal['medical_institution_2'] = re.findall(ur'定点医疗机构2(.*)', info_16)[0]
        # # 定点医疗机构3
        # personal['medical_institution_3'] = re.findall(ur'定点医疗机构3(.*)定点医疗机构', info_17)[0]
        # # 定点医疗机构4
        # personal['medical_institution_4'] = re.findall(ur'定点医疗机构4(.*)', info_17)[0]
        # # 定点医疗机构5
        # personal['medical_institution_5'] = re.findall(ur'定点医疗机构5(.*)\*是否患有特殊病', info_18)[0]
        
        # # 是否患有特殊病
        # personal['special_disease'] = re.findall(ur'是否患有特殊病(.*)', info_18)[0]
        # # 护照号码    
        # personal['passport_number'] = re.findall(ur'护照号码(.*)外国人居留证号码', info_20)[0]
        # # 外国人居留证号码
        # personal['foreign_permits_id'] = re.findall(ur'外国人居留证号码(.*)', info_20)[0]
        # # 外国人证件类型
        # personal['foreign_id_type'] = re.findall(ur'外国人证件类型(.*)外国人证件号码', info_21)[0]
        # # 外国人证件号码
        # personal['foreign_id_number'] = re.findall(ur'外国人证件号码(.*)', info_21)[0]

        # # 社会保险登记证编号
        # personal['socialSecurityNumber'] = re.findall(ur'社会保险登记证编号：(.*)所属区县', info_1)[0].strip()
        # # 所属区县
        # personal['districtsCounties'] = re.findall(ur'所属区县：(.*)', info_1)[0].strip()
        # # 个人身份
        # personal['identity'] = re.findall(ur'个人身份(.*)\*参加', info_5)[0]
        # # 户口所在区县街乡
        # personal['hukouCountyStreet'] = re.findall(ur'区县街乡(.*)\*户口性质', info_6)[0]
        # # 对账单邮编
        # personal['billAddressZipcode'] = re.findall(ur'邮政编码(.*)', info_9)[0]
        # 缴费人员类别/人员状态
        personal['renyuanstatus'] = re.findall(ur'缴费人员类别(.*)\*医疗参保人员类别', info_14)[0]
        # 医疗参保人员类别/行政职务
        personal['Work'] = re.findall(ur'医疗参保人员类别(.*)', info_14)[0]
        # 单位缴费
        personal['company_pay'] = ''
        # 联系人
        personal['con_person'] = ''
        # 婚姻状况
        personal['wedding'] = ''
        # 通讯地址
        personal['phone_add'] = ''

        personal['carDate'] = ''  # 发卡日期
        personal['socialSecurityCardStatus'] = '' # 社保卡状态
        personal['end_data'] = '' # 终止年月
        personal['inter_Month'] = '' # 中断月数
        personal['jiaofeistatus'] = '' # 缴费状态
        personal['Money'] = '' # 账户累计余额
        personal['Date'] = '' # 缴费年月
        personal['personproportion'] = '' # 个人缴费占比
        personal['companyproportion'] = '' # 公司缴费比例
        personal['proportion'] = '' # 缴费基数与社工平均工资水平
        personal['personmoney'] = '' # 个人缴费金额
        personal['finishdata'] = '' # 到账日期
        personal['months'] = '' # 当年累计缴费月数
        personal['Baseaccount'] = '' # 当年实缴缴费基数
        personal['oldmonths'] = '' # 截至上年末累计缴费月数
        personal['shouldMonth'] = '' # 应缴月数
        personal['shouldPayUtil'] = '' # 单位应缴金额
        personal['shouldPayPer'] = '' # 个人应缴金额
        personal['shouldTotal'] = '' # 应缴金额合计
        personal['oweFeeTotalPer'] = '' # 个人欠费金额
        personal['month'] = '' # 实缴月数
        personal['payUtil'] = '' # 单位实缴金额
        personal['payPer'] = '' # 个人实缴金额
        personal['Total'] = '' # 实缴金额合计
        personal['jhMonth'] = '' # 计划月份
        personal['zjMonth'] = '' # 征缴月份
        personal['hkData'] = '' # 回款日期

        newPersonal = {}
        for key, value in personal.items():
            newValue = value.replace(u' ', '')
            newPersonal[key] = newValue
        # 对账单邮箱
        newPersonal['bill_email'] = ''
        # 缴存基数
        newPersonal['deposit_base'] = ''
        return newPersonal

    # def assemble(self, data):
    #     result = [
    #                 {
    #                     "birthday": , # 出生日期
    #                     "gender": , # 性别
    #                     "nationalities": ,# 民族
    #                     "culture": "", # 文化程度
    #                     "work_data": , # 参加工作日期
    #                     "person_name": , # 姓名
    #                     "personalid": , # 公民身份证号码（社会保障号码）
    #                     "id_number": "", # 证件号码
    #                     "id_type": "", # 证件类型
    #                     "foreign_permits_id": "", # 外国人居留证号码
    #                     "foreign_id_type": "", # 外国人证件类型
    #                     "foreign_id_number": "", # 外国人证件号码
    #                     "passport_number": "", # 护照号码
    #                     "account": "", # 户口性质
    #                     "account_address": "", # 户口所在地
    #                     "account_add_zip": "", # 户口所在地邮编
    #                     "home_address": "", # 居住地址
    #                     "home_add_zip": "", # 居住地邮编
    #                     "region": "", # 国家/地区
    #                     "get_bill": "", # 获取对账单方式
    #                     "person_email": "",  # 电子邮件地址
    #                     "bill_email": "", # 对账单邮箱
    #                     "bill_address": "", # 邮寄社会保险对账单地址
    #                     "bank_name": "", # 委托代发银行名称
    #                     "bank_number": "", # 委托代发银行账号
    #                     "retire_date": "", # 离退休日期
    #                     "retire_type": "", # 离退休类别
    #                     "wages": "", # 申报月均工资收入
    #                     "organization_code": "", # 组织机构代码
    #                     "unit_name": "", # 单位名称
    #                     "telephone": "", # 参保人电话
    #                     "phone": "", # 参保人手机
    #                     "special_disease": "", # 是否患有特殊疾病
    #                     "medical_institution_1": "", # 定点医疗机构1
    #                     "medical_institution_2": "",  # 定点医疗机构2
    #                     "medical_institution_3": "",  # 定点医疗机构3
    #                     "medical_institution_4": "",  # 定点医疗机构4
    #                     "medical_institution_5": "",  # 定点医疗机构5
    #                     "deposit_base": "" # 缴存基数
    #                 }
    #             ]
    #     return json.dumps(result, ensure_ascii=False).encode('utf-8')

    # def crawl(self):
    #     try:
    #         if self.login() == 0:
    #             self.logger.info('用户名或密码错误')
    #             return 0,{}
    #         self.logger.info('登录成功')
    #     except Exception as e:
    #         self.logger.error('登录异常')
    #         s = traceback.format_exc()
    #         logger.error(s)
    #         return -2, {}
    #     try:
    #         self.logger.info('开始爬取信息')
    #         data = self.crawl_handler(self.session)
    #     except Exception as e:
    #         self.logger.error('爬取失败，未知错误')
    #         s = traceback.format_exc()
    #         logger.error(s)
    #         return -1, {}
    #     self.logger.info('爬取完成')
    #     return 1, data

    # def data_handler(self, data, year, month):
    #     """ 所有缴费记录处理 """
    #     newData = {}
    #     PaymentLastYear = []
    #     for data_item in data[-14:-1]:
    #         data_date = data_item['date'].split(u'-')
    #         data_year = int(data_date[0])
    #         data_month = int(data_date[1])
    #         if data_year == year:
    #             PaymentLastYear.append(data_item)
    #         if data_year == year-1:
    #             if data_month >= month:
    #                 PaymentLastYear.append(data_item)

    #     # 近五年总缴费月数
    #     newData['count'] = str(len(data) - data[-1] -1)
    #     # 最近一次缴费记录
    #     newData['paymentLast'] = data[-2]
    #     # 最近一年的历史记录明细
    #     newData['paymentLastYear'] = PaymentLastYear

    #     return newData


    # def crawl_handler(self, session):
    #     data = {}

    #     获取查询的当前时间
    #     time_now_year = int(datetime.now().strftime('%Y'))
    #     time_now_month = int(datetime.now().strftime('%m'))


    #     # 个人信息：
    #     personal = data_parse.personal_information_handler(session)
    #     # 养老：
    #     oldage = data_parse.oldage_information_handler(session, time_now_year)
    #     # 失业：
    #     unemployment = data_parse.unemployment_information_handler(session, time_now_year)
    #     # 工伤：
    #     injuries = data_parse.injuries_information_handler(session, time_now_year)
    #     # 生育：
    #     maternity = data_parse.maternity_information_handler(session, time_now_year)
    #     # 医疗：
    #     medicalcare = data_parse.medicalcare_information_handler(session, time_now_year)

    #     oldage = self.data_handler(oldage, time_now_year, time_now_month)
    #     unemployment = self.data_handler(unemployment, time_now_year, time_now_month)
    #     injuries = self.data_handler(injuries, time_now_year, time_now_month)
    #     maternity = self.data_handler(maternity, time_now_year, time_now_month)
    #     medicalcare = self.data_handler(medicalcare, time_now_year, time_now_month)

    #     data['personal'] = personal
    #     data['oldage'] = oldage
    #     data['unemployment'] = unemployment
    #     data['injuries'] = injuries
    #     data['maternity'] = maternity
    #     data['medicalcare'] = medicalcare
    #     return data


if __name__ == '__main__':

    # username = '220282198405185705'
    # password = 'gjy840518'
    # # username = '13063119840317122X'
    # # password = 'zhang123579'
    # # password = 'zhang12357'
    # username = '142601199007247616'
    # password = 'postoffice'

    crawl = SocialInsurance_BeiJing(username, password)
    # print crawl.login()

    print crawl.crawl()[1]


    with open('data.json', 'w') as f:
        f.write(data)

    # endtime = datetime.now()
    # print (endtime - starttime).seconds
