#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
# http://192.168.30.135:8080/9f_insight/nbcredit/crawlData?idCard=28336afc9c1858d8cb9df5d3c99d90f3&userid=xxx-xxx-xxx&nocache=1
#-------------------------------------------------------------------------
import base64
import functools
import json
import logging
import logging.config
import os
import random
import time
import traceback
import uuid
import zlib
import re
from datetime import datetime, timedelta
import requests
import urllib
from PIL import Image
from lxml import etree

from __Utils import damatuWeb
from __Utils.param_crypto import ParamCrypto
from __Utils.StandFormat import hypc_accumulation_fund, hypc_taxpayer_qualification, hypc_enterprise_credit_ningbo
from __Utils.constants import PROXYADDR
from __Utils.pyact import image_to_string
from __Utils.redis_utils import RedisUtils
from __Utils.spider_email import sendMail
from ningboConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, LOGINHEADERS, PERHEADERS, DETAILHEADERS, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE


logging.config.fileConfig('nbcredit/ningbologger.conf')

def Time():
    def _deco(func):
        @functools.wraps(func)
        def _func(self, *args, **kwargs):
            start_time = datetime.now()
            value = func(self, *args, **kwargs)
            end_time = datetime.now()
            SpiderMain.logger.info("共耗时：%ss"%(end_time - start_time))
            return value
        return _func
    return _deco

class SpiderMain(hypc_accumulation_fund):

    logger = logging.getLogger()

    def __init__(self, user):
        self.session = requests.session()
        self.redisUtils = RedisUtils()
        self.PROXYADDR = PROXYADDR
        self.bcode = NOT_NEED_BCODE
        self.status = CRAWL_READY
        self.desc = ""
        self.numb = 0

        self.username = user.get("idCard", "")
        self.token = user.get("token", "")

        self.sj = "%.17f" % (random.random())
        self.codeUrl = "http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=yzm&tm="+self.sj
        self.LoginUrl = "http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml"
        self.infoUrl = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getNewQydjList'


        self.result = user.get("result", "")
        self.GJJInfo = []

        # 加入当次代理
        # self.proxy = self._proxy()

    def _proxy(self):
        proxy = self.session.get(self.PROXYADDR).content
        return {"http": "http://" + proxy, "https": "http://" + proxy}

    def ifNotEmptyGetIndex(self,somelist,index=0):
        """check to see it's not empty"""
        if somelist: 
            return somelist[index]
        else:
            return ''

    def _errhtmlRecord(self, content):
        '''
        错误页面保存
        '''
        self.logger.info("保存错页内容")
        try:
            filename = str(uuid.uuid1()) + ".html"
            sampleDir = os.path.join(os.path.dirname(__file__), "errorHtml").replace("\\", "/")
            os.path.exists(sampleDir) or os.mkdir(sampleDir)
            with open("%s/%s" % (sampleDir, filename), 'w') as f:
                f.write(content)
            self.logger.debug("已保存错页内容到{0}".format(filename))
        except Exception:
            self.status = PROGRAM_ERROR
            s = traceback.format_exc()
            self.logger.info("保存错页出错")
            self.logger.warn("{0}".format(s))

    def _sampleRecord(self, filename, content):
        '''
        保存网页内容
        '''
        self.logger.info("保存网页内容")
        try:
            sampleDir = os.path.join(os.path.dirname(__file__), "sample/").replace("\\", "/")
            os.path.exists(sampleDir) or os.mkdir(sampleDir)
            with open("%s/%s" % (sampleDir, filename), 'w') as f:
                f.write(content)
            self.logger.debug("已保存网页内容到{0}".format(sampleDir))
        except Exception:
            self.status = PROGRAM_ERROR
            s = traceback.format_exc()
            self.logger.info("保存网页出错")
            self.logger.warn("{0}".format(s))

    def _fetchUrl(self, url, data=None, header=None, timeout=TIMEOUT, fileName=None, proxy=None):
        '''0
        抓取方法
        '''
        # url = urllib.quote(url)
        self.logger.info("开始抓取 {0}".format(url))
        if header:
            headers = header
            self.logger.debug("伪装头：{0}".format(headers))
        else:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"}
            self.logger.debug("伪装头：{0}".format(headers))
        for ir in range(REQUEST_RETRY):
            try:
                self.logger.debug("第{0}次 抓取".format(ir))
                if data:
                    if proxy:
                        content = self.session.get(url, params=data, headers=headers, timeout=timeout, allow_redirects=False, proxies=proxy)
                        self.logger.debug("GET url：{0}， data：{1}, proxy: {2}".format(url, data, proxy))
                    else:
                        content = self.session.get(url = url, params=data, headers=headers, timeout=timeout, allow_redirects=False)
                        self.logger.debug("GET url：{0}， data：{1}".format(url, data))
                else:
                    if proxy:
                        content = self.session.get(url, headers=headers, timeout=timeout, allow_redirects=False, proxies=proxy)
                        self.logger.debug("POST url：{0}, proxy: {1}".format(url, proxy))
                    else:
                        content = self.session.get(url, data=data, headers=headers, timeout=timeout, allow_redirects=False)
                        self.logger.debug("Get url：{0}".format(url))
                if fileName and SAMPLEFLAG:
                    self._sampleRecord(fileName, content.content)
                return content
            except:
                self.logger.error(traceback.format_exc())
        self.logger.error("request url {0} failed ,check pls".format(url))
        self.status = CRAWL_TIMEOUT
        raise Exception("Failed to load url (%s)" % url)

    def _fetchUrl_2(self, url, data=None, header=None, timeout=TIMEOUT, fileName=None, proxy=None):
        '''0
        抓取方法
        '''
        self.logger.info("开始抓取 {0}".format(url))
        if header:
            headers = header
            self.logger.debug("伪装头：{0}".format(headers))
        else:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"}
            self.logger.debug("伪装头：{0}".format(headers))
        for ir in range(REQUEST_RETRY):
            try:
                self.logger.debug("第{0}次 抓取".format(ir))
                if data:
                    if proxy:
                        content = self.session.post(url, data=data, headers=headers, timeout=timeout, allow_redirects=False, proxies=proxy)
                        self.logger.debug("POST url：{0}， data：{1}, proxy: {2}".format(url, data, proxy))
                    else:
                        content = self.session.post(url, data=data, headers=headers, timeout=timeout, allow_redirects=False)
                        self.logger.debug("POST url：{0}， data：{1}".format(url, data))
                else:
                    if proxy:
                        content = self.session.get(url, headers=headers, timeout=timeout, allow_redirects=False, proxies=proxy)
                        self.logger.debug("POST url：{0}, proxy: {1}".format(url, proxy))
                    else:
                        content = self.session.get(url, data=data, headers=headers, timeout=timeout, allow_redirects=False)
                        self.logger.debug("Get url：{0}".format(url))
                if fileName and SAMPLEFLAG:
                    self._sampleRecord(fileName, content.content)
                return content
            except:
                self.logger.error(traceback.format_exc())
        self.logger.error("request url {0} failed ,check pls".format(url))
        self.status = CRAWL_TIMEOUT
        raise Exception("Failed to load url (%s)" % url)

    def _save_captcha(self):
        """
        下载验证码，返回图片b64编码，
        """
        self.logger.info("刷新验证码")
        try:
            codeContent = self.session.get(self.codeUrl, headers=IMGHEADERS).content
            self.logger.debug("验证码二进制内容：{0}".format(codeContent)[:50])
            self.logger.info("下载验证码")
            self.status = NEED_BCODE
            with open(os.path.join(os.path.dirname(__file__), "captcha.png").replace("\\", "/"), 'wb') as f:
                f.write(codeContent)
            self.logger.info("验证码图片已保存!")
            bcode = base64.b64encode(codeContent)
            # self.logger.debug("{}".format(bcode))
            return bcode
        except:
            s = traceback.format_exc()
            sendMail(s, 'sunbo@insightcredit.cn')
            self.logger.error("刷新验证码错误：%s" % s)
            return PROGRAM_ERROR, {"error": "超时或代码异常"}

    def _captcha_recognize(self,PATH):
        '''
        自动识别验证码
        :param fileName:
        :return:
        '''
        im = Image.open(PATH)
        im = im.convert('L')
        text = image_to_string(image=im, lang="eng+chi_sim")
        # print text,'1'*30
        try:
            if not text[2].isdigit():
                one = int(text[:2])
                op = text[2]
                two = int(text[3:].replace("=", "").replace('(','0').strip())
            else:
                one = int(text[:1])
                op = text[1]
                two = int(text[2:].replace("=", "").strip())
            result = None
            if op == u"加":
                result = one + two
            elif op == u"减":
                result = one - two
            elif op == u"乘":
                result = one * two
            elif op == u"除":
                result = one / two
            return result
        except:
            return None

    def _ChioceIdent(self, flag):
        '''
        选择识别方式
        :param flag:
        :return:
        '''
        if flag == 'dmt':
            self._save_captcha()
            self.startTime = str(datetime.now())
            dmt = damatuWeb.DamatuApi("huoyan2016", "123456")
            # self.imageCode = dmt.decodeUrl(self.captchaId_url, 200)
            self.imageCode = dmt.decode(os.path.join(os.path.dirname(__file__), "captcha.png").replace("\\", "/"), 200)
            self.finishTime = str(datetime.now())
        elif flag == 'input':
            self._save_captcha()
            pngPath = os.path.join(os.path.dirname(__file__), "captcha.png").replace("\\", "/")
            self.logger.info("验证码路径：{0}".format(pngPath))
            self.imageCode = raw_input("请输入验证码:")
        elif flag == 'auto':
            self.startTime = str(datetime.now())
            self._save_captcha()
            self.logger.info("识别验证码")
            pngPath = os.path.join(os.path.dirname(__file__), "captcha.png").replace("\\", "/")
            self.imageCode = self._captcha_recognize(pngPath)
            self.logger.debug("验证码内容：{0}".format(self.imageCode))
            self.finishTime = str(datetime.now())
        # 返回给用户 通知redis 返回base64
        elif flag == 'user':
            self.startTime = datetime.now()
            bcode64 = self._save_captcha()
            self.redisUtils.setNotify(token=self.token, val="10",decs="需要图片验证码",result="data:image/jpg;base64,"+bcode64)
            # 向session中放入数据
            while True:
                # 等待获取用户输入要的图片验证码值
                dict_image_code = self.redisUtils.getNotify(self.token, "bcode")
                if dict_image_code is not None:

                    self.imageCode = dict_image_code
                    return
                else:
                    self.finishTime = datetime.now()
                    if abs(self.finishTime.minute - self.startTime.minute)>=3:
                        break
                    # 爬虫等待用户输入图片验证码超时
                    self.logger.warn("爬虫等待用户输入图片验证码超时:%s" % self.token)
                    time.sleep(1)
        else:
            self.status = NOT_NEED_BCODE
            self.logger.info(NOT_NEED_BCODE_DESC)


    def login(self,flag):
        self.sj = "%.17f" % (random.random())
        self.codeUrl = "http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=yzm&tm="+self.sj
        self._ChioceIdent(flag)
        LoginData = {
            'dispatch':'yzmCheck',
            'random':self.sj,
            'YZM':self.imageCode,
            'IP':'127.0.0.1',
            'QYMC':self.username,
            'FROMURL':'www.nbcredit.net',
            'LY':'sj',
        }
        
        content = self._fetchUrl(url=self.LoginUrl, header=LOGINHEADERS, data=LoginData, fileName="login.html")
        try:
            self.username = content.cookies.get_dict()["gjjcertinum"] if self.gjjaccnum!="" else self.username
            self.gjjaccnum = content.cookies.get_dict()["gjjaccnum"] if self.gjjaccnum=="" else self.gjjaccnum
            self.logger.info("%s  %s "%(self.username, self.gjjaccnum))
        finally:
            content = content.json()
            return content

    @Time()
    def crawl(self, flag=""):
        try:
            # login
            for i in range(10):

                content = self.login(flag)
                # print content,'123456789'
                # try:
                if content['msg'].encode("utf8") == 'false':
                    self.logger.info("验证码错误：%s" % content["msg"].encode("utf8"))
                    self.status, self.desc = BCODE_ERROR, BCODE_ERROR_DESC
                    continue
                elif content['msg'].encode("utf8") == u'true':
                    self.logger.info("登陆成功：%s"%content)
                    self.reply = content['reply']
                    # 个人信息
                    PerData = {
                        'ly':self.sj,
                        'reply':self.reply,
                        'weburl':'http://www.nbcredit.net/zx/index.html#',
                        'qymc':self.username,
                    }
                    content = self._fetchUrl_2(url=self.infoUrl, header=PERHEADERS, data=PerData, fileName="person.html")
                    companyurl = re.compile(r'dispatch=getQydjJbxx&nbxh=([\w]+\=\=)')
                    url_list = companyurl.findall(content.text)
                    # print len(url_list)/
                    for base in url_list:
                        detail_url = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getQydj&nbxh='+base
                        content = self._fetchUrl(url=detail_url, header=DETAILHEADERS, fileName="detail.html")
                        detail = etree.HTML(content.text)
                        xinyong_id = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[2]/td[1]/text()")).strip()
                        company_name = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[2]/td[2]/text()")).strip()
                        com_type = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[3]/td[1]/text()")).strip()
                        # daibiao = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tbody/tr[3]/td[2]/text()")).strip()
                        daibiao_re = re.compile(r'-->[\s]*(.*)[\s]*</td>[\s]*</tr>[\s]*<tr>[\s]*<th width="20%">注册资本</th>')#
                        daibiao = self.ifNotEmptyGetIndex(daibiao_re.findall(content.content)).strip()

                        ziben = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[4]/td[1]/text()")).strip()
                        chenglidata = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[4]/td[2]/text()")).strip()
                        address = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[5]/td[1]/text()")).strip()
                        start_data = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[6]/td[1]/text()")).strip()
                        end_data = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[6]/td[2]/text()")).strip()
                        jing_wide = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[7]/td[1]/text()")).strip()
                        dengji_name = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[8]/td[1]/text()")).strip()
                        hezhun_data = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[1]/tr[8]/td[2]/text()")).strip()
                        
                        # print xinyong_id,company_name,com_type,com_type,daibiao,ziben,chenglidata,address,start_data,end_data,jing_wide,dengji_name,hezhun_data,gudong_info
                        # 异常信息处理
                        if '异常' in self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[2]/tbody/tr[1]/th/text()")):
                            self.numb = 1
                            Abnormal_info = [] # bnormal_info
                            abnormal_list = detail.xpath("//div[@class='form-box']/table[2]/tbody/tr")
                            for i in range(len(abnormal_list) - 2):
                                i = i + 3
                                include_date = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[2]/tbody/tr["+str(i)+"]/td[1]/text()"))
                                yichang_included = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[2]/tbody/tr["+str(i)+"]/td[2]/text()"))
                                yichang_date = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[2]/tbody/tr["+str(i)+"]/td[3]/text()"))
                                yichang_listed = self.ifNotEmptyGetIndex(detail.xpath("//div[@class='form-box']/table[2]/tbody/tr["+str(i)+"]/td[4]/text()"))
                                Abnormal_info.append(hypc_enterprise_credit_ningbo.bnormal_info(
                                    include_date = include_date,
                                    decision_included = yichang_included,
                                    remove_date = yichang_date,
                                    decision_listed = yichang_listed,
                                    )            
                                )
                        else:
                            self.logger.info('暂无异常信息')
                            Abnormal_info = []
                            Abnormal_info.append(hypc_enterprise_credit_ningbo.bnormal_info(
                                    include_date = '',
                                    decision_included = '',
                                    remove_date = '',
                                    decision_listed = '',
                                    )            
                                )

                        # 股东信息处理
                        gudong_list = detail.xpath("//div[@class='form-box']/table["+str(self.numb+2)+"]/tbody/tr[@class='numq']")
                        gudong = []
                        if gudong_list:
                            for gu in gudong_list:
                                gu_type = self.ifNotEmptyGetIndex(gu.xpath("td[1]/text()")).strip()
                                gu_name = self.ifNotEmptyGetIndex(gu.xpath("td[2]/text()")).strip()
                                gu_id_type = self.ifNotEmptyGetIndex(gu.xpath("td[3]/text()")).strip()
                                gu_id = self.ifNotEmptyGetIndex(gu.xpath("td[4]/text()")).strip()
                                gu_info = self.ifNotEmptyGetIndex(gu.xpath("td[5]/text()")).strip()
                                gudong.append(hypc_enterprise_credit_ningbo.Shareholder_info(
                                    shareholder_type=gu_type,
                                    shareholder=gu_name,
                                    card_type=gu_id_type,
                                    card_num=gu_id,
                                    detail_info=gu_info,
                                    )            
                                )
                        else:
                            gudong.append(hypc_enterprise_credit_ningbo.Shareholder_info())
                            # print gu_type,gu_name,gu_id_type,gu_id,gu_info

                        # biangeng_list = detail.xpath("//div[@class='form-box']/table[3]/tr[@class='num']")
                        # 变更信息处理
                        biangeng_list = detail.xpath("//div[@class='form-box']/table[@id='bgnrtable']/tr[@class='num']")
                        change = []
                        if biangeng_list:
                            for biangeng in biangeng_list:
                                bian_shi = self.ifNotEmptyGetIndex(biangeng.xpath("td[1]/text()")).strip()
                                bian_befor = self.ifNotEmptyGetIndex(biangeng.xpath("td[2]/text()")).strip()
                                bian_after = self.ifNotEmptyGetIndex(biangeng.xpath("td[3]/text()")).strip()
                                biandata = self.ifNotEmptyGetIndex(biangeng.xpath("td[4]/text()")).strip()
                                # print bian_shi,bian_befor,bian_after,biandata

                                change.append(hypc_enterprise_credit_ningbo.Change_info(
                                    change_active=bian_shi,
                                    change_content_pr=bian_befor,
                                    change_content_after=bian_after,
                                    change_date=biandata,
                                    )  
                                )
                        else:
                            change.append(hypc_enterprise_credit_ningbo.Change_info())
                        # 主要人物信息处理
                        person_list = detail.xpath("//div[@class='form-box']/table["+str(self.numb+4)+"]/tbody/tr")
                        key_person = []
                        if person_list[2:]:
                            for person in person_list[2:]:
                                per_id = self.ifNotEmptyGetIndex(person.xpath("td[1]/text()")).strip()
                                per_name = self.ifNotEmptyGetIndex(person.xpath("td[2]/text()")).strip()
                                per_work = self.ifNotEmptyGetIndex(person.xpath("td[3]/text()")).strip()
                                
                                key_person.append(hypc_enterprise_credit_ningbo.key_person_info(
                                        person_name=per_name,
                                        person_position=per_work,
                                    )
                                )
                                if not self.ifNotEmptyGetIndex(person.xpath("td[4]/text()")):
                                    pass
                                else:
                                    per_id1 = self.ifNotEmptyGetIndex(person.xpath("td[4]/text()")).strip()
                                    per_name1 = self.ifNotEmptyGetIndex(person.xpath("td[5]/text()")).strip()
                                    per_work1 = self.ifNotEmptyGetIndex(person.xpath("td[6]/text()")).strip()
                                    
                                    key_person.append(hypc_enterprise_credit_ningbo.key_person_info(
                                        person_name=per_name1,
                                        person_position=per_work1,
                                        )
                                    )
                        else:
                            key_person.append(hypc_enterprise_credit_ningbo.key_person_info())
                        branch = [
                            {
                                "common_code":'',                      
                                "knowledge_name":'',
                                "branch_dept_register":'',    
                            }
                        ]
                        # 行政处罚信息处理
                        xingcheng_url = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getXzcfxx&nbxh='+base
                        xing_content = self._fetchUrl(url=xingcheng_url, header=DETAILHEADERS, fileName="xingzheng.html")
                        xing_detail = etree.HTML(xing_content.text)
                        xing_list = xing_detail.xpath("//*[@class='detailsList']/tbody/tr")
                        xingzheng = []
                        if len(xing_list) > 2:
                            for i in range(len(xing_list)-2):
                                i = i + 3
                                # penalty_amount = self.ifNotEmptyGetIndex(xing_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[1]/text()")).strip() # 处罚金额
                                # ticket_date = self.ifNotEmptyGetIndex(xing_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[2]/text()")).strip() # 出票日期
                                # decide_document = self.ifNotEmptyGetIndex(xing_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[3]/text()")).strip() # 决定文书 
                                # check_amount = self.ifNotEmptyGetIndex(xing_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[4]/text()")).strip() # 支票金额
                                url_xing = self.ifNotEmptyGetIndex(xing_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[6]/a/@href"))
                                if url_xing:
                                    xing_detail_url = 'http://www.nbcredit.net/zx/gjcx/' + url_xing
                                    xing_detail_con = self._fetchUrl(url=xing_detail_url, header=DETAILHEADERS, fileName="xingdetail.html")
                                    xing_detail_text = etree.HTML(xing_detail_con.text)
                                    xing_name = self.ifNotEmptyGetIndex(xing_detail_text.xpath("//*[@class='sear-imformation']/tr[2]/td/text()"))
                                    xing_chu_id =self.ifNotEmptyGetIndex(xing_detail_text.xpath("//*[@class='sear-imformation']/tr[3]/td/text()"))
                                    weifa_type = self.ifNotEmptyGetIndex(xing_detail_text.xpath("//*[@class='sear-imformation']/tr[4]/td/text()"))
                                    xing_unit = self.ifNotEmptyGetIndex(xing_detail_text.xpath("//*[@class='sear-imformation']/tr[5]/td/text()"))
                                    chufa_detail = self.ifNotEmptyGetIndex(xing_detail_text.xpath("//*[@class='sear-imformation']/tr[6]/td/text()"))
                                    xing_date = self.ifNotEmptyGetIndex(xing_detail_text.xpath("//*[@class='sear-imformation']/tr[7]/td/script/text()"))
                                    date_re = re.compile(r'\d{4}-\d{1,2}-\d{1,2}')
                                    mading_date = self.ifNotEmptyGetIndex(date_re.findall(str(xing_date)))
                                    xingzheng.append(hypc_enterprise_credit_ningbo.xing_info(
                                            com_per_name = xing_name,#违法企业名称或违法自然人名称
                                            execution_number = xing_chu_id,# 行政处决文号 
                                            type_violation = weifa_type,#违法行为类型   
                                            made_penalty = xing_unit,#作出处罚决定机关名称    
                                            penalty_content = chufa_detail,#  处罚内容 
                                            penalty_date = mading_date #作出行政处罚决定日期
                                        ))
                                else:
                                    xingzheng.append(hypc_enterprise_credit_ningbo.xing_info(
                                        com_per_name = '',
                                        execution_number = '',
                                        type_violation = '',   
                                        made_penalty = '',    
                                        penalty_content = '', 
                                        penalty_date = '' 
                                        ))
                                
                        else:
                            xingzheng.append(hypc_enterprise_credit_ningbo.xing_info(
                                    com_per_name = '',
                                    execution_number = '',
                                    type_violation = '',   
                                    made_penalty = '',    
                                    penalty_content = '', 
                                    penalty_date = '' 
                                    ))
                        # 司法信息处理
                        sifa_url = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getWlx&nbxh=' + base
                        sifa_content = self._fetchUrl(url=sifa_url, header=DETAILHEADERS, fileName="sifa.html")
                        sifa_detail = etree.HTML(sifa_content.text)
                        sifa_list = sifa_detail.xpath("//*[@class='detailsList']/tbody/tr")
                        sifa = []
                        if len(sifa_list) > 2:
                            for i in range(len(sifa_list) - 2):
                                i = i + 3
                                case_number = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[1]/text()"))
                                execution_basis = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[2]/text()"))
                                nature_case = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[3]/text()"))
                                executive_content = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[4]/text()"))
                                amount_subject = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[5]/text()"))
                                organization_code = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[6]/text()"))
                                legal_representative = self.ifNotEmptyGetIndex(sifa_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(i)+"]/td[7]/text()"))
                                sifa.append(hypc_enterprise_credit_ningbo.sifa_info(
                                        case_number = case_number,
                                        execution_basis = execution_basis,
                                        nature_case = nature_case,
                                        executive_content = executive_content,
                                        amount_subject = amount_subject,
                                        organization_code = organization_code,
                                        legal_representative = legal_representative
                                    ))
                        else:
                            sifa.append(hypc_enterprise_credit_ningbo.sifa_info(
                                        case_number = "",
                                        execution_basis = "",
                                        nature_case = "",
                                        executive_content = "",
                                        amount_subject = "",
                                        organization_code = "",
                                        legal_representative = "",
                                    ))
                        # 评价信息处理
                        pingjia_url = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getQtXydj&nbxh=' + base
                        pingjia_content = self._fetchUrl(url=pingjia_url, header=DETAILHEADERS, fileName="pingjia.html")
                        pingjia_detail = etree.HTML(pingjia_content.text)
                        pingjia_table = pingjia_detail.xpath("//*[@class='form-box']/table")
                        pingjia_list = []
                        if pingjia_table:
                            for j in range(len(pingjia_table)):
                                j = j + 1
                                dengji_list = []
                                pingjia_type = self.ifNotEmptyGetIndex(pingjia_detail.xpath("//*[@class='form-box']/table["+str(j)+"]/tbody/tr[1]/th/text()")).strip()
                                pingjia_detail_list = pingjia_detail.xpath("//*[@class='form-box']/table["+str(j)+"]/tbody/tr")
                                for k in range(len(pingjia_detail_list)-2):
                                    k = k + 3
                                    pingjia_date = self.ifNotEmptyGetIndex(pingjia_detail.xpath("//*[@class='form-box']/table["+str(j)+"]/tbody/tr["+str(k)+"]/td[1]/text()"))
                                    pingjia_grade = self.ifNotEmptyGetIndex(pingjia_detail.xpath("//*[@class='form-box']/table["+str(j)+"]/tbody/tr["+str(k)+"]/td[2]/text()"))
                                    pingjia_institution = self.ifNotEmptyGetIndex(pingjia_detail.xpath("//*[@class='form-box']/table["+str(j)+"]/tbody/tr["+str(k)+"]/td[3]/text()"))
                                    if not pingjia_grade and not pingjia_institution:
                                        pass
                                    else:
                                        dengji_list.append({
                                            'pingjia_date':pingjia_date,#评价时间
                                            'pingjia_grade':pingjia_grade,#信用等级
                                            'pingjia_institution':pingjia_institution#评定机构/部门
                                        })
                                pingjia_list.append({
                                        'evaluation_type':pingjia_type, # 评定类别
                                        'evaluation_detail':dengji_list
                                    })

                        else:
                            pingjia_list.append({
                                    "evaluation_type":"",
                                    "evaluation_detail":[]
                                })
                        # 荣誉信息处理
                        rongyu_url = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getGsRyxx&nbxh='+base
                        rongyu_content = self._fetchUrl(url=rongyu_url, header=DETAILHEADERS, fileName="rongyu.html")
                        rongyu_detail = etree.HTML(rongyu_content.text)
                        rongyu_list = rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr")
                        rongyu = []
                        if len(rongyu_list) > 2:
                            for j in range(len(rongyu_list) - 2):
                                j = j + 3
                                rongyu_date = self.ifNotEmptyGetIndex(rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(j)+"]/td[1]/text()"))# 认定日期    
                                rongyu_long = self.ifNotEmptyGetIndex(rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(j)+"]/td[2]/text()"))# 有效期限    
                                rongyu_type = self.ifNotEmptyGetIndex(rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(j)+"]/td[3]/text()"))# 守重等级    
                                rongyu_com = self.ifNotEmptyGetIndex(rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(j)+"]/td[4]/text()"))# 命名机关    
                                rongyu_baddate = self.ifNotEmptyGetIndex(rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(j)+"]/td[5]/text()"))# 被取消日期   
                                rongyu_reason = self.ifNotEmptyGetIndex(rongyu_detail.xpath("//*[@class='detailsList']/tbody/tr["+str(j)+"]/td[6]/text()"))# 被取消原因
                                rongyu.append(hypc_enterprise_credit_ningbo.honor_info(
                                    date_approval=rongyu_date,
                                    validity_period=rongyu_long,
                                    defense_level=rongyu_type,
                                    named_authority=rongyu_com,
                                    date_canceled=rongyu_baddate,
                                    rejected_reason=rongyu_reason,
                                    ))
                        else:
                            rongyu.append(hypc_enterprise_credit_ningbo.honor_info(
                                    date_approval='',
                                    validity_period='',
                                    defense_level='',
                                    named_authority='',
                                    date_canceled='',
                                    rejected_reason=''
                                ))
                        # 许可证信息处理
                        xuke_url = 'http://www.nbcredit.net/zx/gjcx/gjcxinit.shtml?dispatch=getXzxkxx&nbxh='+base
                        xuke_content = self._fetchUrl(url=xuke_url, header=DETAILHEADERS, fileName="xuke.html")
                        xuke_detail = etree.HTML(xuke_content.text)
                        xuke_list = xuke_detail.xpath("//*[@class='detailsList']/tr")
                        xuke_re = re.compile(r'[0-9]*-[0-9]*-[0-9]*')
                        xuke = []
                        if len(xuke_list) > 2:
                            for i in range(len(xuke_list)-2):
                                i = i + 3
                                xuke_name = self.ifNotEmptyGetIndex(xuke_detail.xpath("//*[@class='detailsList']/tr["+str(i)+"]/td[1]/text()"))# 许可证名称
                                xuke_id = self.ifNotEmptyGetIndex(xuke_detail.xpath("//*[@class='detailsList']/tr["+str(i)+"]/td[2]/text()"))# 许可证号
                                xuke_begain_str = self.ifNotEmptyGetIndex(xuke_detail.xpath("//*[@class='detailsList']/tr["+str(i)+"]/td[3]/script/text()"))# 有效期起
                                xuke_begain = self.ifNotEmptyGetIndex(xuke_re.findall(xuke_begain_str))
                                xuke_end_str = self.ifNotEmptyGetIndex(xuke_detail.xpath("//*[@class='detailsList']/tr["+str(i)+"]/td[4]/script/text()"))# 有效期至
                                xuke_end = self.ifNotEmptyGetIndex(xuke_re.findall(xuke_end_str))
                                xuke_com = self.ifNotEmptyGetIndex(xuke_detail.xpath("//*[@class='detailsList']/tr["+str(i)+"]/td[5]/text()"))# 发证机关
                                xuke_date_str = self.ifNotEmptyGetIndex(xuke_detail.xpath("//*[@class='detailsList']/tr["+str(i)+"]/td[6]/script/text()"))# 发证日期
                                xuke_date = self.ifNotEmptyGetIndex(xuke_re.findall(xuke_date_str))
                                xuke.append(hypc_enterprise_credit_ningbo.license_info(
                                    name_permit=xuke_name,    #许可证名称
                                    permit_number=xuke_id,#许可证号
                                    effective_date=xuke_begain, #有效日期起
                                    valid_until=xuke_end, #有效日期至
                                    issuing_authority=xuke_com, #发证机关
                                    date_issue=xuke_date, #发证日期
                                    ))
                        else:
                            xuke.append(hypc_enterprise_credit_ningbo.license_info(
                                    name_permit='',    #许可证名称
                                    permit_number='',#许可证号
                                    effective_date='', #有效日期起
                                    valid_until='', #有效日期至
                                    issuing_authority='', #发证机关
                                    date_issue='', #发证日期
                                    ))

                        self.GJJInfo.append(hypc_enterprise_credit_ningbo.baseinfo(
                                branch_dept_code=xinyong_id,
                                company_name=company_name,
                                common_type=com_type,
                                person=daibiao,
                                register_money=ziben,
                                establish_date=chenglidata,
                                address=address,
                                start_date=start_data,
                                end_time=end_data,
                                common_range=jing_wide,
                                register_dept=dengji_name,
                                verify_date=hezhun_data,
                                Shareholder_info=gudong,
                                Change_info=change,
                                key_person_info=key_person,
                                Branch_info=branch,
                                Xingzheng_info=xingzheng,
                                sifa_info=sifa,
                                bnormal_info=Abnormal_info,
                                evaluation_info=pingjia_list,
                                honor_info=rongyu,
                                license_info=xuke
                            )
                        )
                        # self.GJJInfo.append(self.PayRecord)
                    self.status= CRAWL_SUCCESS
                    self.result.append(self.GJJInfo)
                    break
                else:
                    self.logger.info("登录失败：%s" % content["msg"].encode("utf8"))
                    self.logger.info(IDCARD_ERROR_DESC)
                    self.status, self.desc = IDCARD_ERROR, IDCARD_ERROR_DESC
                    break

        except:
            s = traceback.format_exc()
            sendMail(s, 'sunbo@insightcredit.cn')
            self.logger.error("抓取错误：%s" % s)
            self.status, self.desc = self.status, PROGRAM_ERROR_DESC
        finally:
                try:
                    if len(self.result) == 1 and self.status == CRAWL_SUCCESS:
                        self.desc = CRAWL_SUCCESS_DESC
                        result_json = json.dumps(self.result[0], ensure_ascii=False)
                        # print result_json
                        self.redisUtils.setNotify(type=TYPEVALUE,token=self.token, val="1", decs="抓取成功！", result=result_json)
                        # self.push_data(TYPEVALUE, self.userid, result_json)


                    elif self.status == CRAWL_FAIL:
                        self.desc = CRAWL_FAIL_DESC

                    elif self.status == CRAWL_TIMEOUT:
                        self.desc = CRAWL_TIMEOUT_DESC

                    elif self.status == IDCARD_ERROR:
                        self.desc = IDCARD_ERROR_DESC

                    elif self.status == PASSWORD_ERROR:
                        self.desc = PASSWORD_ERROR_DESC

                    elif self.status == BCODE_ERROR:
                        self.desc = BCODE_ERROR_DESC

                    else:
                        self.desc = PROGRAM_ERROR_DESC

                except Exception as e:
                    s = traceback.format_exc()
                    sendMail(s, 'sunbo@insightcredit.cn')
                    self.logger.error(s)

                finally:
                    try:
                        self.redisUtils.setNotify(type=TYPEVALUE, token=self.token, val=self.status, decs=self.desc)
                    except Exception:
                        s = traceback.format_exc()
                        self.logger.error(s)


    def zipToStr(self, content):
        '''
        使用urllib2获取到的内容被压缩，需要进行解压缩
        :param content: 需要解压的内容
        :return:
        '''
        try:
            conn = zlib.decompress(content, 16 + zlib.MAX_WBITS)
            return conn
        except:
            self.logger.error('解压缩响应内容出错%s' % traceback.format_exc())
            raise Exception("解压缩响应内容出错%s" % traceback.format_exc())



if __name__ == '__main__':
    # user = {"pwd": "040413", "username": "220181199102040413", "loginType":"1","userid":"xxxxxxxxxxxxxxxx", "token": "tokentokentokentokentoken"}
    user = {"username": "火眼", "token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    user.update({"result": []})
    sp = SpiderMain(user)
    sp.crawl("input")
    # print hypc_taxpayer_qualification.taxpayer(
    #     identity="110106590611038",
    #     taxpayer_name="北京东方披克科技有限公司",
    #     taxpayer_qname="一般纳税人",
    #     expiry="2012年03月08日",
    #     taxes=["1203.11", "569"],
    #     taxes_type=["企业所得税", "增值税"],
    #     unit_address="河北省石家庄市新华区泰华街567号香格礼小区一号楼一单元901室"
    # )


