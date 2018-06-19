#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
# http://localhost:8080/gjjchangchun/crawlData?password=7163589c3c80f3eefe04a6d90ba6787f&userid=xxx-xxx-xxx&idCard=b54e390e5a23af65545a260b7f777bbb9d38659c15866562a96f96b61ec82dab&nocache=1
#-------------------------------------------------------------------------
import base64
import functools
import json
import logging
import logging.config
import os
import re
import random
import time
import traceback
import uuid
import zlib
from datetime import datetime, timedelta
import requests
from PIL import Image
import urllib

from __Utils import damatuWeb
from __Utils.StandFormat import craw_dishonest
from __Utils.constants import PROXYADDR
from __Utils.pyact import image_to_string
from __Utils.redis_utils import RedisUtils
from dishonestyConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, LOGINHEADERS, PERHEADERS, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE, KONG, KONG_DESC, EXEMPLE_IS_NOT_FULL, EXEMPLE_IS_NOT_FULL_DESC


logging.config.fileConfig('dishonesty/dishonestylogger.conf')

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

def ifNotEmptyGetIndex(somelist,index=0):
    """check to see it's not empty"""
    if somelist: 
        return somelist[index]
    else:
        return ''


class SpiderMain(craw_dishonest):

    logger = logging.getLogger()

    def __init__(self, user):
        self.session = requests.session()
        self.redisUtils = RedisUtils()
        self.PROXYADDR = PROXYADDR
        self.bcode = NOT_NEED_BCODE
        self.status = CRAWL_READY
        self.desc = ""

        # self.username = urllib.quote(user.get("name", ""))
        # self.idcard = urllib.quote(user.get("idcard", ""))
        # self.area = urllib.quote(user.get("area", ""))
        self.username = user.get("name", "")#.encode('utf-8')
        self.idcard = user.get("idcard", "")#.encode('utf-8')
        self.area = user.get("area", "")#.encode('utf-8')
        self.token = user.get("token", "")
        self.userid = user.get("userid", "")

        self.LoginUrl = "https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?"+"resource_id=6899&query=%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA%E5%90%8D%E5%8D%95&cardNum="+self.idcard+"&iname="+self.username+"&areaName="+self.area+"&ie=utf-8&oe=utf-8&format=json&t="+str(int(round(time.time() * 1000)))+"&cb=jQuery110207690611877233657_"+str(int(round(time.time() * 1000)))+"&_="+str(int(round(time.time() * 1000)))

        self.result = user.get("result", "")
        self.GJJInfo = []
        self.PerInfo = {}
        self.PayRecord = {}


        # 加入当次代理
        # self.proxy = self._proxy()

    def _proxy(self):
        proxy = self.session.get(self.PROXYADDR).content
        return {"http": "http://" + proxy, "https": "http://" + proxy}

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
            self.logger.error("{0}".format(s))

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
        '''
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
                        self.logger.debug("Get url：{0}, proxy: {1}".format(url, proxy))
                    else:
                        content = self.session.get(url, headers=headers, timeout=timeout, allow_redirects=False)
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
            self.logger.error("刷新验证码错误：%s" % s)
            return PROGRAM_ERROR, {"error": "超时或代码异常"}

    def _captcha_recognize(self,imgpath):
        '''
        自动识别验证码
        :param fileName:
        :return:
        '''
        img = Image.open(imgpath)
        for i in range(10):
            code = image_to_string(img, lang='eng').encode('utf-8')
            if code.isalnum() and len(code) == 4:
                self.logger.info(code)
                return code
            self._save_captcha()
            time.sleep(0.05)

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
        # self._ChioceIdent(flag)
        if self.username or self.idcard:
            # print self.LoginUrl
            content = self._fetchUrl(url=self.LoginUrl, header=LOGINHEADERS, fileName="login.html")
            return content
        else:
            return ''
    @Time()
    def crawl(self, flag=""):
        CurTime = datetime.now().strftime("%Y-%m-%d")
        PastTime = (datetime.now() - timedelta(days=729)).strftime("%Y-%m-%d")
        try:
            # login
            # for i in range(10):
            content = self.login(flag)
            if content:
                info_re = re.compile(r'\/\*\*\/jQuery[0-9]+_[0-9]+\((.*)\)')
                info_detail = ifNotEmptyGetIndex(info_re.findall(content.content))
                info_dict = eval(info_detail)
                date_info = ifNotEmptyGetIndex(info_dict.get('data',''))
                if not date_info:
                    date_info = {'result':[]}

                info_result = date_info.get('result','')
                for detail in info_result:
                    re_id = re.compile(r'id=([0-9]*)')
                    shixinid = ifNotEmptyGetIndex(re_id.findall(detail.get("loc","")))
                    self.GJJInfo.append(craw_dishonest.gaofa(
                        unperformPart=detail.get("unperformPart",""),  # 被执行人的未履行部分
                        shixinid=shixinid,  # 失信人ID
                        sexy=detail.get("sexy",""),  # 性别
                        regDate=detail.get("regDate",""),  # 立案时间
                        publishDate=detail.get("publishDate",""),  # 发布时间
                        performedPart=detail.get("performedPart",""),  # 被执行人的履行部分
                        performance=detail.get("performance",""),  # 被执行人的履行情况
                        partyTypeName=detail.get("partyTypeName",""),  # 类型号
                        iname=detail.get("iname",""),  # 被执行人姓名/名称
                        disruptTypeName=detail.get("disruptTypeName",""),  # 失信被执行人行为具体情形
                        courtName=detail.get("courtName",""),  # 执行法院
                        caseCode=detail.get("caseCode",""),  # 案号
                        cardNum=detail.get("cardNum",""),  # 身份证号码/组织机构代码
                        businessEntity=detail.get("businessEntity",""),  # 法定代表人或负责人姓名
                        areaName=detail.get("areaName",""),  # 省份
                        age=detail.get("age",""),  # 年龄（企业默认为0）
                        duty=detail.get("duty", ""), # 生效法律文书确定的义务
                        gistId=detail.get("gistId", ""), # 执行依据文号
                        gistUnit=detail.get("gistUnit", ""), # 做出执行依据单位
                        ))
                self.status= CRAWL_SUCCESS
                self.result.append(self.GJJInfo)
            else:
                self.status = CRAWL_SUCCESS
                self.result.append(self.GJJInfo)
            # break
        except:
            s = traceback.format_exc()
            self.logger.error("抓取错误：%s" % s)
            self.status, self.desc = PROGRAM_ERROR, PROGRAM_ERROR_DESC
        finally:
                try:
                    if len(self.result) == 1 and self.status == CRAWL_SUCCESS:
                        self.desc = CRAWL_SUCCESS_DESC
                        # print self.result
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
    # user = {"pwd": "040413", "username": "801157483790", "loginType":"1", "token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    # user.update({"result": []})
    # sp = SpiderMain(user)
    # sp.crawl("auto")
    print hypc_taxpayer_qualification.taxpayer(
        identity="110106590611038",
        taxpayer_name="北京东方披克科技有限公司",
        taxpayer_qname="一般纳税人",
        expiry="2012年03月08日",
        taxes=["1203.11", "569"],
        taxes_type=["企业所得税", "增值税"],
        unit_address="河北省石家庄市新华区泰华街567号香格礼小区一号楼一单元901室"
    )


