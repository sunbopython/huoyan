#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
#http://192.168.30.135:8080/9f_insight/translate/crawlData?title=55b2d00a69cdd4eacb8be77ef311055d54c5a228e94722467f61659206e470658048351314c77a52e6a55b4196384319&date_filter_max=2bcda7f5e23933078a1e071427160dec&date_filter_min=2bcda7f5e23933078a1e071427160dec&userid=xxx-xxx-xxx&project=2bcda7f5e23933078a1e071427160dec&project_district=ade28f53668e272e457e14de121be4ff&nocache=1
#-------------------------------------------------------------------------
import sys
import base64
reload(sys)
sys.setdefaultencoding('UTF-8')
import functools
import json
import urllib
import logging
import logging.config
import os
import re
import chardet
import random
import time
import traceback
import uuid
import zlib
from datetime import datetime, timedelta
import requests
from PIL import Image
from lxml import etree

from __Utils import damatuWeb
from __Utils.StandFormat import hypc_accumulation_fund, hypc_taxpayer_qualification, hypc_translate
from __Utils.constants import PROXYADDR
from __Utils.pyact import image_to_string
from __Utils.redis_utils import RedisUtils
from translateConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, LOGINHEADERS, PERHEADERS, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE


logging.config.fileConfig('spider_translate/translatelogger.conf')

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

class SpiderMain(hypc_translate):

    logger = logging.getLogger()

    def __init__(self, user):
        self.session = requests.session()
        self.redisUtils = RedisUtils()
        self.PROXYADDR = PROXYADDR
        self.bcode = NOT_NEED_BCODE
        self.status = CRAWL_READY
        self.desc = ""

        self.title = user.get("title", "")
        # print chardet.detect(self.title)
        self.title = urllib.quote(self.title.encode('utf8'))

        self.project_district = user.get("project_district")
        self.project_developer_name_value = user.get("project", "")
        self.date_filter_min = user.get("date_filter_min","")
        self.date_filter_max = user.get("date_filter_max","")
        # print self.title,self.project_developer_name_value,self.project_district,self.date_filter_max,self.date_filter_min

        # self.title = urllib.quote(self.title.decode(sys.stdin.encoding).encode('utf-8'))
        # self.project_district = urllib.quote(self.project_district.decode(sys.stdin.encoding).encode('utf8'))
        # self.project_developer_name_value = urllib.quote(self.project_developer_name_value.decode(sys.stdin.encoding).encode('utf8'))
        # self.date_filter_min = urllib.quote(self.date_filter_min.decode(sys.stdin.encoding).encode('utf8'))
        # self.date_filter_max = urllib.quote(self.date_filter_max.decode(sys.stdin.encoding).encode('utf8'))
        #
        self.token = user.get("token", "")
        self.userid = user.get("userid", "")


        self.LoginUrl = "https://newhouse.cnnbfdc.com"


        self.result = user.get("result", "")
        self.GJJInfo = []
        self.bild = []


        # 加入当次代理
        # self.proxy = self._proxy()
    def ifNotEmptyGetIndex(self, somelist, index=0):
        """check to see it's not empty"""
        if somelist: 
            return somelist[index]
        else:
            return ''

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
                f.write(str(content))
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
                        content = self.session.get(url, headers=headers, timeout=timeout, allow_redirects=False)
                        # print content.encoding
                        self.logger.debug("Get url：{0}".format(url))
                if fileName and SAMPLEFLAG:
                    self._sampleRecord(fileName, content.content)
                return content
            except:
                self.logger.error(traceback.format_exc())
        self.logger.error("request url {0} failed ,check pls".format(url))
        self.status = CRAWL_TIMEOUT
        raise Exception("Failed to load url (%s)" % url)

    def login(self,flag):
        first_url = "https://newhouse.cnnbfdc.com/publicity/project-licenses?title="+str(self.title)+"&project_district="+str(self.project_district)+"&project_developer_name_value="+str(self.project_developer_name_value)+"&date_filter%5Bmin%5D%5Bdate%5D="+str(self.date_filter_min)+"&date_filter%5Bmax%5D%5Bdate%5D="+str(self.date_filter_min)
        content = self._fetchUrl(url=first_url, header=LOGINHEADERS, fileName="login.html")

        return str(content.text)

    @Time()
    def crawl(self, flag=""):
        CurTime = datetime.now().strftime("%Y-%m-%d")
        PastTime = (datetime.now() - timedelta(days=729)).strftime("%Y-%m-%d")
        try:
            # login
            content = self.login(flag)
            url_num = re.compile(r'/project_license_view/([0-9]+)">')
            url_num_list = url_num.findall(content)
            if len(url_num_list) > 0:
                for url_num in url_num_list:
                    url_detail = self.LoginUrl + '/project_license_view/' + str(url_num)
                    self.logger.info("可查询到您查的信息：%s" % self.title)
                    # 项目详情信息
                    content = self._fetchUrl(url=url_detail, header=PERHEADERS, fileName="person.html")
                    detail = etree.HTML(content.text)
                    project_name = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='project-detail__info']/div[1]/h1/text()")) # 项目名称
                    alias_name = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='project-detail__info']/div[1]/div/text()")) # 别名
                    positioning = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='project-detail__info']/div[2]//span/text()"))#定位
                    company_name = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='project-detail__info']/div[3]//span/text()")) # 公司名称
                    project_id = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='project-detail__info']/div[4]/span/text()")) #项目编号
                    counts = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-entity-view pane-node']/div[2]/div[2]/div/div[1]/div/text()")) or self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-entity-view pane-node']/div[2]/div/div[2]/div[1]/div/strong/text()")) # 套数
                    area = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-entity-view pane-node']/div[2]/div[2]/div/div[2]/div/text()")) or self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-entity-view pane-node']/div[2]/div/div[2]/div[2]/div/strong/text()"))# 面积
                    #数据汇总
                    marketable_area = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-panel panel-col-first']/div/div[1]/div/text()"))# 可销售面积
                    sales_area = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-panel panel-col-first']/div/div[2]/div/text()"))#已销售面积
                    has_sold_area = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-panel panel-col-first']/div/div[3]/div/text()")) #已销售非住宅面积
                    number_sellable_households = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-panel panel-col-last']/div/div[1]/div/text()")) # 可售户数
                    has_sold_number = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-panel panel-col-last']/div/div[2]/div/text()")) # 已销售户数
                    has_sold_households = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-panel panel-col-last']/div/div[3]/div/text()")) # 已销售非住宅户数
                    # 详细参数
                    permit_number = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[1]/td[2]/text()"))#    许可证号
                    permission_date = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[1]/td[4]/span/text()"))# 许可日期
                    sales_address = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[2]/td[2]/text()"))# 售楼地址
                    sales_call = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[2]/td[4]/text()"))# 售楼电话
                    number_buildings = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[3]/td[2]/text()"))# 幢数
                    construction_area = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[3]/td[4]/text()"))# 建筑面积
                    opening_time = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[4]/td[2]/span/text()"))# 开盘时间
                    supervision_account = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[4]/td[4]/text()"))# 资金监管账户
                    document_authority = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[5]/td[2]/text()"))# 证件发布机构
                    financial_bank = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='parameter-table']/tr[5]/td[4]/text()"))# 资金监管银行
                    #  楼栋信息
                    loudong_list = detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div")
                    if len(loudong_list) > 0:
                        for i in range(len(loudong_list)):
                            i = i + 1
                            num_floors = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[1]/div/text()")) # 楼号
                            total_floors = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[2]/div/text()")) # 总层数 
                            # total_houses = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[3]/div/text()")) # 总户数
                            total_houses = ''
                            permitted_households = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[3]/div/text()")) # 许可户数
                            has_sold_number_households = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[4]/div/text()")) # 已销售户数
                            has_sold_residential_households = self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[5]/div/text()")) # 已销售非住宅户数
                            
                            wangqian_list = []
                            wangqian = str(self.ifNotEmptyGetIndex(detail.xpath("//*[@class='panel-pane pane-views-panes pane-project-license-buildings-panel-pane-1']/div/div/div["+str(i)+"]/div[6]/span/a/@href"))) # 网签的URL
                            if wangqian:
                                lou_numb = re.compile(r'buildingId=([0-9]+)')
                                wang_numb = self.ifNotEmptyGetIndex(lou_numb.findall(wangqian))
                                wangqian_url = "https://newhouse.cnnbfdc.com//map-api-v1/building_units?args[]=" + wang_numb
                                wang_content = self._fetchUrl(url=wangqian_url, header=IMGHEADERS, fileName="wangqian.html")
                                wangqian_info = etree.HTML(str(wang_content.text))
                                
                                for j in range(len(wangqian_info.xpath("//result/item"))):
                                    j = j + 1
                                    if self.ifNotEmptyGetIndex(wangqian_info.xpath("//result/item["+str(j)+"]/state/text()")) == '3':
                                        number = self.ifNotEmptyGetIndex(wangqian_info.xpath("//result/item["+str(j)+"]/number/text()"))
                                        wangqian_list.append(number)
                            
                            self.bild.append(hypc_translate.detail_building(
                                num_floors = num_floors,
                                total_floors = total_floors,
                                total_houses = total_houses,
                                permitted_households = permitted_households,
                                has_sold_number_households = has_sold_number_households,
                                has_sold_residential_households = has_sold_residential_households,
                                wangqian_nubm=wangqian_list
                                ))
                    else:
                        self.bild.append(hypc_translate.detail_building(
                            num_floors = '',
                            total_floors = '',
                            total_houses = '',
                            permitted_households = '',
                            has_sold_number_households = '',
                            has_sold_residential_households = '',
                            ))


                    self.GJJInfo.append(hypc_translate.baseinfo(
                        project_name = project_name, 
                        alias_name = alias_name, # 别名
                        positioning = positioning, #定位
                        company_name = company_name, # 公司名称
                        project_id = project_id, #项目编号
                        counts = counts, # 套数
                        area = area, # 面积
                        marketable_area = marketable_area, # 可销售面积
                        sales_area = sales_area, #已销售面积
                        has_sold_area = has_sold_area, #已销售非住宅面积
                        number_sellable_households = number_sellable_households, # 可售户数
                        has_sold_number = has_sold_number, # 已销售户数
                        has_sold_households = has_sold_households, # 已销售非住宅户数
                        permit_number = permit_number, #    许可证号
                        permission_date = permission_date, # 许可日期
                        sales_address = sales_address, # 售楼地址
                        sales_call = sales_call, # 售楼电话
                        number_buildings = number_buildings, # 幢数
                        construction_area = construction_area, # 建筑面积
                        opening_time = opening_time, # 开盘时间
                        supervision_account = supervision_account, # 资金监管账户
                        document_authority = document_authority, # 证件发布机构
                        financial_bank = financial_bank, # 资金监管银行
                        bulding = self.bild
                        ))
                self.logger.info("解析完成")
                self.status= CRAWL_SUCCESS
                self.result.append(self.GJJInfo)
            else:
                self.logger.info("暂无您查询的信息：%s" % IDCARD_ERROR_DESC)
                self.status= CRAWL_SUCCESS
                self.result.append(self.GJJInfo)

        except:
            s = traceback.format_exc()
            self.logger.error("抓取错误：%s" % s)
            self.status, self.desc = CRAWL_FAIL, PROGRAM_ERROR_DESC
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
    pass
    # user = {"pwd": "040413", "username": "801157483790", "loginType":"1", "token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    # user = {
    #     "title":"仑房预许字（2017）第10号",
    #     "project_district":"61",s
    #     "project_developer_name_value":'',
    #     "date_filter_min":''
    #     "date_filter_max":''
    # }
    # # https://newhouse.cnnbfdc.com/publicity/project-licenses?title=%E4%BB%91%E6%88%BF%E9%A2%84%E8%AE%B8%E5%AD%97%EF%BC%882017%EF%BC%89%E7%AC%AC10%E5%8F%B7&project_district=61&project_developer_name_value=&date_filter%5Bmin%5D%5Bdate%5D=&date_filter%5Bmax%5D%5Bdate%5D=
    # s = "https://newhouse.cnnbfdc.com/publicity/project-licenses?title=仑房预许字（2017）第10号&project_district=61&project_developer_name_value=&date_filter[min][date]=&date_filter[max][date]="
    # utf_url = urllib.quote(s.decode(sys.stdin.encoding).encode('utf8'))
    # print utf_url
    # # user.update({"result": []})
    # # sp = SpiderMain(user)
    # # sp.crawl("auto")
    


