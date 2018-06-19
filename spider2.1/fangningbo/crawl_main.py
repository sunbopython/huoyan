#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
#------------------------------------------------------------------------
import sys
# sys.path.append('..')
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
import urllib
from lxml import etree
from bs4 import BeautifulSoup
from PIL import Image

from __Utils import damatuWeb
from __Utils.StandFormat import hypc_soufun
from __Utils.constants import PROXYADDR
from __Utils.pyact import image_to_string
from __Utils.redis_utils import RedisUtils
from ningboConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, LOGINHEADERS, PERHEADERS, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE,FANGAGE,LOUCENG,HUXING


logging.config.fileConfig('fangningbo/ningbologger.conf')

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

class SpiderMain(hypc_soufun):

    logger = logging.getLogger()

    def __init__(self, user):
        self.session = requests.session()
        self.redisUtils = RedisUtils()
        self.PROXYADDR = PROXYADDR
        self.bcode = NOT_NEED_BCODE
        self.status = CRAWL_READY
        self.desc = ""

        self.keyword = user.get("keyword", "")
        # self.gjjaccnum = self.username if len(self.username) <= 15 else ""
        # self.pwd = user.get("password", "")
        self.age = FANGAGE.get(user.get('age',''),'') or FANGAGE.get(user.get('year',''), '')
        self.token = user.get("token", "")
        self.flower = LOUCENG.get(user.get('flower',''),'') or LOUCENG.get(user.get('floor',''),'')
        self.hu_type = HUXING.get(user.get('hu_type',''),'') or HUXING.get(user.get('housetype',''),'')
        # self.userid = user.get("userid", "")

        self.startUrl = "http://esf.nb.fang.com/NewSecond/sale_info/searchlist_new2014.aspx"
        self.hostUrl = "http://esf.nb.fang.com/"
        self.result = user.get("result", "")
        self.GJJInfo = []

        # self.proxy = {'http':'http://143.0.188.8:80','https':'https://143.0.188.8:80'}
        # 加入当次代理
        # self.proxy = self._proxy()

    def _proxy(self):
        proxy = self.session.get(self.PROXYADDR).content
        # proxy = self.session.get('http://192.168.30.185:13579/ip').content
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
                        self.logger.debug("GET url：{0}, proxy: {1}".format(url, proxy))
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


    def prase_detail(self, detail_content):
        detail_info = etree.HTML(detail_content.text)
        sum_price = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='trl-item_top']/div/i/text()"))# 总价
        first_pay = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div/div[@class='trl-item_top']/div[2]/text()"))# 首付
        # month_pay = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[2]/div[3]/a/div/span/i/text()"))# 月供
        house_type = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[2]/div[1]/div[1]/text()")).strip()# 户型
        construction_area = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[2]/div[2]/div[1]/text()"))# 建筑面积
        unit_price = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[2]/div[3]/div[1]/text()"))# 单价
        orientation = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[3]/div[1]/div[1]/text()"))# 朝向
        floor = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[3]/div[2]/div[1]/text()"))+self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[3]/div[2]/div[2]/text()"))# 楼层
        decoration = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[3]/div[3]/div[1]/text()"))# 装修
        district = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='tab-cont-right']/div[4]/div[1]/div[2]/a[1]/text()"))# 小区
        
        quyu = detail_info.xpath("//div[@id='address']/a")# 区域
        quyu_list = []
        for qu in quyu:
            quyu_list.append(self.ifNotEmptyGetIndex(qu.xpath("text()")).strip())
        area = ','.join(quyu_list) # 区域
        
        contact_person = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@id='agantesfxq_C04_02']/text()"))# 联系人
        economic_company = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='tjcont-list-cline2']/span[2]/text()"))# 经纪公司
        phone = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='tjcont-list-cline3 font16']/span/text()"))# 电话
        #房源信息
        build_age_list = re.compile(r'<span class=\"lab\">建筑年代</span>[\s]*<span class=\"rcont\">(.*)</span>')
        build_age = self.ifNotEmptyGetIndex(build_age_list.findall(str(detail_content.text)))
        elevator_list = re.compile(r'<span class=\"lab\">有无电梯</span>[\s]*<span class=\"rcont\">(.*)</span>')
        elevator = self.ifNotEmptyGetIndex(elevator_list.findall(str(detail_content.text)))
        property_right_list = re.compile(r'<span class="lab">产权性质</span>[\s]*<span class="rcont">(.*)</span>')
        property_right = self.ifNotEmptyGetIndex(property_right_list.findall(str(detail_content.text)))
        category_list = re.compile(r'<span class="lab">住宅类别</span>[\s]*<span class="rcont">(.*)</span>')
        category = self.ifNotEmptyGetIndex(category_list.findall(str(detail_content.text)))
        build_structure_list = re.compile(r'<span class="lab">建筑结构</span>[\s]*<span class="rcont">(.*)</span>')
        build_structure = self.ifNotEmptyGetIndex(build_structure_list.findall(str(detail_content.text)))
        build_category_list = re.compile(r'<span class="lab">建筑类别</span>[\s]*<span class="rcont">(.*)</span>')
        build_category = self.ifNotEmptyGetIndex(build_category_list.findall(str(detail_content.text)))
        list_time_list = re.compile(r'<span class="lab">挂牌时间</span>[\s]*<span class="rcont">[\s]*(.*)[\s]*.*</span>')
        list_time = self.ifNotEmptyGetIndex(list_time_list.findall(str(detail_content.text))).strip()
        fang_info = self.ifNotEmptyGetIndex(detail_info.xpath("//div[@class='content-item'][2]/div[2]/div/div/div/text()")) # 房源描述
        # 小区信息
        reference_price = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div/div[1]/span[2]/i/text()"))#参考均价
        district_than_year = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div/div[2]/span[2]/em/span/text()")) # 同比去年
        district_than_month = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div/div[3]/span[2]/em/span/text()")) # 环比上月
        district_property_type = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[1]/span[2]/text()")).strip() # 物业类型 
        district_property_costs = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[2]/span[2]/text()")).strip() # 物业费用
        district_build_type = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[3]/span[2]/text()")).strip() # 建筑类型
        district_build_age = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[4]/span[2]/text()")).strip() # 建筑年代
        district_green_rate = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[5]/span[2]/text()")).strip() # 绿化率
        district_volume_tate = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[6]/span[2]/text()")).strip() # 容积率
        district_diversion = self.ifNotEmptyGetIndex(detail_info.xpath("//*[@class='cont pt30']/div[2]/div[7]/span[2]/text()")).strip() # 人车分流
        self.GJJInfo.append(hypc_soufun.baseinfo(
            sum_price=sum_price,
            first_pay=first_pay,
            house_type=house_type,
            construction_area=construction_area,
            unit_price=unit_price,
            orientation=orientation,
            floor=floor,
            decoration=decoration,
            district=district,
            area=area,
            contact_person=contact_person,
            economic_company=economic_company,
            phone=phone,
            build_age=build_age,
            elevator=elevator,
            property_right=property_right,
            category=category,
            build_structure=build_structure,
            build_category=build_category,
            list_time=list_time,
            fang_info=fang_info,
            reference_price=reference_price,
            district_than_year=district_than_year,
            district_than_month=district_than_month,
            district_property_type=district_property_type,
            district_property_costs=district_property_costs,
            district_build_type=district_build_type,
            district_build_age=district_build_age,
            district_green_rate=district_green_rate,
            district_volume_tate=district_volume_tate,
            district_diversion=district_diversion,
            ))

    def login(self,flag):
        # self._ChioceIdent(flag)
        '''there are divided into bulk and real time'''
        if self.keyword:
            LoginData = {
                'input_keyw1':self.keyword,
                'city':'宁波',
                'district':'',
                'purpose':'סլ',
                'room':'',
                'pricemin':'',
                'pricemax':'',
                'trackLine':'',
                'keyword':self.keyword,
                'renttype':'',
                'strCity':'宁波',
                'strDistrict':'',
                'Strprice':'',
                'StrNameKeyword':self.keyword,
                'houseType':'',
                'isnewhouse':0,
                'isFinder':0,
                'fromdianshang':'',
                'fromhouseprom':'',
                'fromesfchengjiao':''
            }
            # content = self._fetchUrl(url=self.startUrl, header=LOGINHEADERS, proxy=self.proxy, data=LoginData, fileName="login.html")
            content = self._fetchUrl(url=self.startUrl, header=LOGINHEADERS, data=LoginData, fileName="login.html")
            return content
        else:
            # content = self._fetchUrl(url=self.hostUrl, header=PERHEADERS, proxy=self.proxy, fileName="login.html")
            content = self._fetchUrl(url=self.hostUrl, header=PERHEADERS, fileName="login.html")
            return content

    @Time()
    def crawl(self, flag=""):
        CurTime = datetime.now().strftime("%Y-%m-%d")
        PastTime = (datetime.now() - timedelta(days=729)).strftime("%Y-%m-%d")
        try:
            # login
            # for i in range(10):
            content = self.login(flag)
            # try:
            if 'keyword=' not in content.text.encode('utf8') and content.text.encode('utf8'):
                self.logger.info("获取信息成功：%s"%'good info')
                secondUrl = 'http://esf.nb.fang.com/house/'+self.hu_type+self.flower+self.age+'kw'+'/'
                # content = self._fetchUrl(url=secondUrl, header=PERHEADERS, proxy=self.proxy, fileName="person.html")
                content = self._fetchUrl(url=secondUrl, header=PERHEADERS, fileName="person.html")
                infohtml = etree.HTML(content.text)
                num_info = str(self.ifNotEmptyGetIndex(infohtml.xpath("//div[@class='fanye gray6']/span/text()")).encode('utf8'))
                if num_info:
                    zong = re.compile(r'共(\d*)页')
                    num = zong.search(num_info).group(1)#提取页数
                    for i in range(int(num)):
                        # proxy1 = self._proxy()
                        fang_url = 'http://esf.nb.fang.com/house/'+self.hu_type+self.flower+self.age+'i3'+str(i+1)+'-'+'kw'+'/'
                        # list_content = self._fetchUrl(url=fang_url, header=PERHEADERS, proxy=self.proxy, fileName="list.html")
                        list_content = self._fetchUrl(url=fang_url, header=PERHEADERS, fileName="list.html")
                        list_info = etree.HTML(list_content.text)
                        html = list_info.xpath("//div[@class='houseList']/dl")
                        for ht in html[:-1]:
                            a = self.ifNotEmptyGetIndex(ht.xpath("dd[@class='info rel floatr']/p[1]/a/@href"))
                            if a:
                                detail_url = 'http://esf.nb.fang.com' + str(a)
                                # 具体的房产页信息
                                detail_content = self._fetchUrl(url=detail_url, header=PERHEADERS, fileName="detail.html")
                                self.prase_detail(detail_content)
                    self.status= CRAWL_SUCCESS
                self.result.append(self.GJJInfo)
                # a = json.dumps(self.result[0],ensure_ascii=False) 
                # print a
            # except:
            elif not content.text.encode('utf8'):   
                self.logger.info("获取信息成功：%s"%content)

                # data = urllib.quote(self.keyword.decode(sys.stdin.encoding).encode('gb2312'))
                data = urllib.quote(self.keyword.decode('utf-8').encode('gb2312'))
                secondUrl = 'http://esf.nb.fang.com/house/'+self.hu_type+self.flower+self.age+'kw'+data.lower()+'/'
                # content = self._fetchUrl(url=secondUrl, header=PERHEADERS, proxy=self.proxy, fileName="person.html")
                content = self._fetchUrl(url=secondUrl, header=PERHEADERS, fileName="person.html")
                infohtml = etree.HTML(content.text)
                num_info = str(self.ifNotEmptyGetIndex(infohtml.xpath("//div[@class='fanye gray6']/span/text()")).encode('utf8'))
                if num_info:
                    zong = re.compile(r'共(\d*)页')
                    num = zong.search(num_info).group(1)#提取页数
                    for i in range(int(num)):
                        # proxy1 = self._proxy()
                        fang_url = 'http://esf.nb.fang.com/house/'+self.hu_type+self.flower+self.age+'i3'+str(i+1)+'-'+'kw'+data.lower()+'/'
                        # list_content = self._fetchUrl(url=fang_url, header=PERHEADERS, proxy=self.proxy, fileName="list.html")
                        list_content = self._fetchUrl(url=fang_url, header=PERHEADERS, fileName="list.html")
                        list_info = etree.HTML(list_content.text)
                        html = list_info.xpath("//div[@class='houseList']/dl")
                        for ht in html:
                            a = self.ifNotEmptyGetIndex(ht.xpath("dd[@class='info rel floatr']/p[1]/a/@href"))
                            if a:
                                detail_url = 'http://esf.nb.fang.com' + str(a)
                                # 具体的房产页信息
                                detail_content = self._fetchUrl(url=detail_url, header=PERHEADERS, fileName="detail.html")                
                                self.prase_detail(detail_content)
                    self.status= CRAWL_SUCCESS
                else:
                    self.status= CRAWL_SUCCESS
                    self.GJJInfo.append(hypc_soufun.baseinfo())
                self.result.append(self.GJJInfo)
                # a = json.dumps(self.result[0],ensure_ascii=False) 
                # print a
            else:
                self.logger.info("信息失败：%s" % 'bad info')
                self.logger.info(IDCARD_ERROR_DESC)
                self.status, self.desc = IDCARD_ERROR, IDCARD_ERROR_DESC
                self.result.append(self.GJJInfo)
                # break
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
    user = {"keyword": "时代华庭",'flower':'6层以下','age':'2-5年',"token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    # user = {"keyword": "时代华庭", 'hu_type':'三居','flower':'6层以下','age':'2-5年',"token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    # user = {'hu_type':'五居以上','flower':'顶层','age':'2年以下',"token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}    
    user.update({"result": []})
    sp = SpiderMain(user)
    sp.crawl("auto")
    


