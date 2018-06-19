#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
# http://192.168.30.135:8080/9f_insight/tax/crawlData?fphm=c1a393caf6f4a35d4b80a93eecf3ea4b&userid=xxx-xxx-xxx&fpje=90b2e369d3a6f01faa8f64377793daa4&kprq=906f77f4bdfbd8aec24106bf89a74ef7&fpdm=2b6c7d452b9b00d7db247f7d80f946a6&nocache=1
#-------------------------------------------------------------------------
import base64
import functools
import json
import logging
import logging.config
import os
import sys
import re
import random
import time
import traceback
import uuid
import zlib
import urllib
from datetime import datetime, timedelta
import requests
from PIL import Image
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from __Utils import damatuWeb
from __Utils.StandFormat import hypc_accumulation_fund, hypc_taxpayer_qualification, craw_taxpayer_qualification
from __Utils.constants import PROXYADDR
from __Utils.pyact import image_to_string
from __Utils.redis_utils import RedisUtils
from taxConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, LOGINHEADERS, PERHEADERS, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE, AREA, COULOR, CARD_OUT_DESC, EXEMPLE_IS_NOT_FULL, EXEMPLE_IS_NOT_FULL_DESC


logging.config.fileConfig('tax/taxlogger.conf')

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

class SpiderMain(craw_taxpayer_qualification):

    logger = logging.getLogger()

    def __init__(self, user):
        self.session = requests.session()
        self.redisUtils = RedisUtils()
        self.PROXYADDR = PROXYADDR
        self.bcode = NOT_NEED_BCODE
        self.status = CRAWL_READY
        self.desc = ""

        self.fpjy = user.get("fpjy", "")
        self.fpdm = user.get("fpdm", "")
        self.fphm = user.get("fphm", "")
        self.kprq = user.get("kprq", "")
        self.fpje = user.get("fpje", "")
        self.token = user.get("token", "")
        self.userid = user.get("userid", "")
        self.fpdm_area = self.fpdm[0:4]
        self.fpdm_url = AREA.get(self.fpdm_area, "")
        self.suiji = str(int(round(time.time() * 1000)))

        self.codeUrl = self.fpdm_url+'/WebQuery/yzmQuery?callback=jQuery110204713398352365614_'+self.suiji+'&fpdm='+self.fpdm+'&r='+str('%.16f'%(random.random()))+'&v=V1.0.04_001'+'&nowtime='+str(int(round(time.time() * 1000)))+'&publickey=B8EE27C2CFEABABBD1DB92F4D84E4EA3&_='+str(int(round(time.time() * 1000)))

        self.result = user.get("result", "")
        self.GJJInfo = []
        self.PerInfo = {}


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
                        self.logger.debug("POST url：{0}, proxy: {1}".format(url, proxy))
                    else:
                        content = self.session.get(url, data=data, headers=headers, timeout=timeout, allow_redirects=False)
                        self.logger.debug("Get url：{0}".format(url))
                if fileName and SAMPLEFLAG:
                    self._sampleRecord(fileName, content.content)
                info = re.compile(r'jQuery[0-9]+_[0-9]+\((.*)\)')

                info_list = info.findall(content.content)[0]
                content_dic = eval(info_list)
                return content_dic
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
            content = self.session.get(self.codeUrl, headers=IMGHEADERS, verify=False)
            info = re.compile(r'jQuery[0-9]+_[0-9]+\((.*)\)')
            info_list = ifNotEmptyGetIndex(info.findall(content.content))
            dic = eval(info_list)

            codeContent = dic.get('key1','')
            self.logger.debug("验证码二进制内容：{0}".format(codeContent)[:50])
            self.logger.info("下载验证码")
            self.status = NEED_BCODE
            chose_id = dic.get('key4','')
            chose_info = COULOR.get(chose_id,'')
            codeContent1 = base64.b64decode(codeContent)
            with open(os.path.join(os.path.dirname(__file__), "captcha.png").replace("\\", "/"), 'wb') as f:
                f.write(codeContent1)
            bcode = codeContent
            self.logger.info("验证码图片已保存!")

            if chose_info != '请输入验证码内容':
                im = Image.open(os.path.join(os.path.dirname(__file__), "captcha.png"))
                box = im.copy()
                u = Image.new('RGB', (90, 55))
                u.paste(box, (0,0))
                key_id = Image.open(os.path.join(os.path.dirname(__file__), chose_info))
                key_box = key_id.copy()
                u.paste(key_box,(0,35))
                u.save(os.path.join(os.path.dirname(__file__), "card.png"))
                with open(os.path.join(os.path.dirname(__file__), "card.png")) as c:
                    bcode = base64.b64encode(c.read())

            self.data = urllib.quote(dic.get('key2','').encode('utf8')).replace('%20','+')
            self.index = dic.get('key3','')
            
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
                # print dict_image_code
                if dict_image_code is not None:
                    # print dict_image_code
                    self.redisUtils.DelNotify(self.token, "bcode")
                    self.imageCode = dict_image_code
                    break
                else:
                    self.finishTime = datetime.now()
                    if abs(self.finishTime.minute - self.startTime.minute)>=2:
                        break
                    time.sleep(1)
        else:
            self.status = NOT_NEED_BCODE
            self.logger.info(NOT_NEED_BCODE_DESC)


    def login(self,flag):
        self._ChioceIdent(flag)
        if self.fpje:
            # LoginUrl = self.fpdm_url+'/WebQuery/query?callback=jQuery110204713398352365614_'+self.suiji+'&fpdm='+self.fpdm+'&fphm='+self.fphm+'&kprq='+self.kprq+'&fpje='+self.fpje+'&fplx=01&yzm='+self.imageCode+'&yzmSj='+self.data+'&index='+self.index+'&iv=31205b0a9543d0cf808f6a3a19915858'+'&salt=bc1792b6b19a7ceb8f124fc75e658cfe'+'&publickey=89FF3E78F5B40654133317B104D81634&_='+str(int(round(time.time() * 1000)))
            LoginUrl = self.fpdm_url+'/WebQuery/invQuery?callback=jQuery110204713398352365614_'+self.suiji+'&fpdm='+self.fpdm+'&fphm='+self.fphm+'&kprq='+self.kprq+'&fpje='+self.fpje+'&fplx=01&yzm='+self.imageCode+'&yzmSj='+self.data+'&index='+self.index+'&iv=31205b0a9543d0cf808f6a3a19915858'+'&salt=bc1792b6b19a7ceb8f124fc75e658cfe'+'&publickey=89FF3E78F5B40654133317B104D81634&_='+str(int(round(time.time() * 1000)))
            content = self._fetchUrl(url=LoginUrl, header=IMGHEADERS, fileName="login.html")

        elif self.fpjy:
            LoginUrl = self.fpdm_url+'/WebQuery/invQuery?callback=jQuery110204713398352365614_'+self.suiji+'&fpdm='+self.fpdm+'&fphm='+self.fphm+'&kprq='+self.kprq+'&fpje='+self.fpjy+'&fplx=04&yzm='+self.imageCode+'&yzmSj='+self.data+'&index='+self.index+'&iv=31205b0a9543d0cf808f6a3a19915858'+'&salt=bc1792b6b19a7ceb8f124fc75e658cfe'+'&publickey=89FF3E78F5B40654133317B104D81634&_='+str(int(round(time.time() * 1000)))
            content = self._fetchUrl(url=LoginUrl, header=IMGHEADERS, fileName="login.html")

        else:
            self.logger.debug("没有您查询的方式")
            content = {"key1":"009"}

        return content

    @Time()
    def crawl(self, flag=""):
        CurTime = datetime.now().strftime("%Y-%m-%d")
        PastTime = (datetime.now() - timedelta(days=729)).strftime("%Y-%m-%d")
        try:
            # login
            for i in range(5):
                content = self.login(flag)
                if content['key1'] == "007":
                    self.logger.info("验证码失效")
                    self.status, self.desc = BCODE_ERROR, CARD_OUT_DESC
                    continue

                elif content['key1'] == "008":
                    self.logger.info("验证码错误")
                    self.status, self.desc = BCODE_ERROR, BCODE_ERROR_DESC
                    continue

                elif content["key1"] == "002":
                    self.logger.info("当日查询次数已超过5次")
                    self.logger.info(PASSWORD_ERROR_DESC)
                    self.status, self.desc = PASSWORD_ERROR, PASSWORD_ERROR_DESC
                    break
                elif content['key1'] == "009":
                    self.logger.info("查无此票")
                    self.logger.info(EXEMPLE_IS_NOT_FULL)
                    self.status, self.desc = EXEMPLE_IS_NOT_FULL, EXEMPLE_IS_NOT_FULL_DESC
                    break
                
                elif content["key1"] == "001":
                    self.logger.info("登陆成功：%s"%content['key1'])
                    a_json = json.dumps(content, ensure_ascii=False)
                    bbb = json.loads(a_json,encoding="gbk")

                    sales_name = bbb.get('key2', '').encode('utf8').split('≡')[6]   # 销售方名字【6】
                    purchaser_taxpayer_id = bbb.get('key2', '').encode('utf8').split('≡')[3]  # 购买方纳税人识别号【3】
                    purchaser_bank_account = bbb.get('key2', '').encode('utf8').split('≡')[5] # 购买方开户行级账号【5】
                    sales_taxpayer_id = bbb.get('key2', '').encode('utf8').split('≡')[7]   # 销售方纳税识别号【7】
                    sales_add_phone = bbb.get('key2', '').encode('utf8').split('≡')[8]  # 销售方地址电话【8】
                    check_number = bbb.get('key2', '').encode('utf8').split('≡')[17] # 校验号
                    sales_bank_account = bbb.get('key2', '').encode('utf8').split('≡')[9] # 销售方开户行及账号【9】
                    purchaser_add_phone = bbb.get('key2', '').encode('utf8').split('≡')[4]  # 购买方地址电话[4]
                    purchaser_name = bbb.get('key2', '').encode('utf8').split('≡')[2]   # 购买方名称[2]

                    service_name = bbb.get('key3', '').encode('utf8').split('█')[0]   #  服务名称
                    specification = bbb.get('key3', '').encode('utf8').split('█')[1]  # 规格型号
                    unit = bbb.get('key3', '').encode('utf8').split('█')[2]  # 单位
                    quantity = bbb.get('key3', '').encode('utf8').split('█')[3]   # 数量
                    unit_price = bbb.get('key3', '').encode('utf8').split('█')[4]   # 单价
                    amount = bbb.get('key3', '').encode('utf8').split('█')[5]    # 金额
                    tax_rate = bbb.get('key3', '').encode('utf8').split('█')[6]  #  税率
                    tax = bbb.get('key3', '').encode('utf8').split('█')[7]     # 税额
                    
                    if self.fpjy:
                        machine_code = bbb.get('key2', '').encode('utf8').split('≡')[15] #机器码
                    else:
                        machine_code = ''
                    
                    self.PerInfo = craw_taxpayer_qualification.baseinfo(
                        sales_name = sales_name,
                        purchaser_taxpayer_id = purchaser_taxpayer_id,
                        purchaser_bank_account = purchaser_bank_account,
                        sales_taxpayer_id = sales_taxpayer_id,
                        sales_add_phone = sales_add_phone,
                        sales_bank_account = sales_bank_account,
                        purchaser_add_phone = purchaser_add_phone,
                        purchaser_name = purchaser_name,
                        service_name = service_name,
                        specification = specification,
                        unit = unit,
                        quantity = quantity,
                        unit_price = unit_price,
                        amount = amount,
                        tax_rate = tax_rate,
                        tax = tax,
                        invoice_code = self.fpdm,      # 发票代码
                        invoice_number = self.fphm,      # 发票号码
                        billing_date = self.kprq,      # 开票日期
                        check_number = check_number,      # 校验号
                        machine_code = machine_code,      # 机器码
                        before_tax = self.fpje,    #税前金额
                        total_tax = '%.2f' % (float(amount)+float(tax)),      # 纳税合计
                        )
                   
                    self.GJJInfo.append(self.PerInfo)
                    self.status= CRAWL_SUCCESS
                    self.result.append(self.GJJInfo)
                    break
                else:
                    self.logger.info("查询失败：%s" % content["key1"])
                    self.logger.info(IDCARD_ERROR_DESC)
                    self.status, self.desc = IDCARD_ERROR, IDCARD_ERROR_DESC
                    break
                    
        except:
            s = traceback.format_exc()
            self.logger.error("抓取错误：%s" % s)
            self.status, self.desc = self.status, PROGRAM_ERROR_DESC
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


