#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
# http://192.168.30.135:8080/9f_insight/gsxt/crawlData?idCard=7800405392b8ac4bb69ebcf7f470ddc760eb771d3af3f9d715d87703a0777f719e4d001b750698b70b21264e49ec0f73&userid=xxx-xxx-xxx&nocache=1
#------------------------------------------------------------------------
import sys
# sys.setdefaultencoding('utf8')
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
from datetime import datetime, timedelta
import requests
from PIL import Image
from bs4 import BeautifulSoup
import re
import StringIO
import math
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.support import ui
from pyvirtualdisplay import Display
from lxml import etree
from __Utils import damatuWeb
from __Utils.StandFormat import hypc_enterprise_credit,hypc_accumulation_fund
from __Utils.constants import PROXYADDR
from __Utils.pyact import image_to_string
from __Utils.redis_utils import RedisUtils
from  country import country1
from driverclean import DriverClean
from types import MethodType
from qiyegsxtConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE,FIRSTHEADER,INFOHEADERS,RUSER_AGENTS,BCODE_IS_NULL,BCODE_IS_NULL_DESC,PASSWORD_IS_NULL,PASSWORD_IS_NULL_DESC
logging.config.fileConfig('gsxt/gsxtlogger.conf')

import threading
reload(sys)
sys.setdefaultencoding('utf-8')

globallogger=""

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

def get1(self,url):
    self.dc.setts(time.time())
    self.dc.setstatus(0)
    return self.get(url)

def find_element_by_xpath1(self, xpath):
    self.dc.setts(time.time())
    self.dc.setstatus(0)
    return self.find_element_by_xpath(xpath)

class SpiderMain(hypc_accumulation_fund):

    logger = logging.getLogger()
    def __init__(self, user):
        self.url_area = {
            "北京":"http://bj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml",
            "天津":"http://tj.gsxt.gov.cn/index.html",
            "河北":"http://he.gsxt.gov.cn/notice/",
            "山西":"http://sx.gsxt.gov.cn/index.jspx",
            "内蒙古":"http://nm.gsxt.gov.cn:58888/",
            "辽宁":"http://ln.gsxt.gov.cn/saicpub/",
            "吉林":"http://jl.gsxt.gov.cn/",
            "黑龙江":"http://hl.gsxt.gov.cn/index.jspx",
            "上海":"http://sh.gsxt.gov.cn/notice",
            "江苏":"http://www.jsgsj.gov.cn:58888/province/",
            "浙江":"http://zj.gsxt.gov.cn/client/entsearch/toEntSearch",
            "安徽":"http://ah.gsxt.gov.cn/index.jspx",
            "福建":"http://fj.gsxt.gov.cn/notice",
            "江西":"http://jx.gsxt.gov.cn/",
            "山东":"http://sd.gsxt.gov.cn/",
            "广东":"http://gd.gsxt.gov.cn/",
            "广西":"http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml",
            "海南":"http://hi.gsxt.gov.cn/index.jspx",
            "河南":"http://ha.gsxt.gov.cn/index.jspx",
            "湖北":"http://hb.gsxt.gov.cn/index.jspx",
            "湖南":"http://hn.gsxt.gov.cn/notice/",
            "重庆":"http://cq.gsxt.gov.cn/",
            "四川":"http://sc.gsxt.gov.cn/notice/",
            "贵州":"http://gz.gsxt.gov.cn/",
            "云南":"http://yn.gsxt.gov.cn/notice/",
            "西藏":"http://xz.gsxt.gov.cn/index.jspx",
            "陕西":"http://sn.gsxt.gov.cn/ztxy.do?method=index&random=",
            "甘肃":"http://gs.gsxt.gov.cn/gsxygs/",
            "青海":"http://qh.gsxt.gov.cn/index.jspx",
            "宁夏":"http://nx.gsxt.gov.cn/",
            "新疆":"http://xj.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml"
            }

        self.session = requests.session()
        self.redisUtils = RedisUtils()
        self.PROXYADDR = PROXYADDR
        self.bcode = NOT_NEED_BCODE
        self.status = CRAWL_READY
        self.desc = ""
        self.area = user.get("area","")

        self.keyword = user.get("idCard", "")
        self.token = user.get("token", "")
        self.LoginUrl = self.url_area.get(self.area, "") if self.area else "http://www.gsxt.gov.cn/index.html"
        self.result = user.get("result", "")
        self.GJJInfo = []
        self.br = self.get_webdriver("chrome")

        self.br.dc = DriverClean(1,time.time(),self.br.service.process.pid,self.br)
        self.br.get1 = MethodType(get1,self.br,webdriver.Chrome)
        self.br.find_element_by_xpath1 = MethodType(find_element_by_xpath1,self.br,webdriver.Chrome)

        global globallogger
        globallogger = self.logger

        # self.br.maximize_window()
        # self.br.set_window_size(1300,900)
        # self.proxy = self._proxy()
        # proxy=webdriver.Proxy()
        # proxy.proxy_type=ProxyType.MANUAL
        # proxy.http_proxy=self.proxy
        # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中

        # proxy.add_to_capabilities(self.dcap)
        # self.br.start_session(self.dcap)
        # self.br.get('http://httpbin.org/ip')
        # print self.br.page_source
        self.wait = WebDriverWait(self.br, 10, 0.5)
        self.br.set_page_load_timeout(10)
        self.br.set_script_timeout(15)
        self.br.implicitly_wait(10);
        # 加入当次代理
        # self.proxy = self._proxy()

    def _proxy(self):
        proxy = self.session.get(self.PROXYADDR).content
        # return {"http": "http://" + proxy, "https": "http://" + proxy}
        return proxy

    def run(self,keyword):
        content = self.hack_geetest(keyword.decode('utf8'))
        if not content[0].get("base_info", "") and not content[0].get("admin_penalty_info","") and not content[0].get("operate_abnormal_info","") and not content[0].get("key_person_info","") and not content[0].get("change_info","") and not content[0].get("check_info","") and not content[0].get("chattel_info","") and not content[0].get("branch_info","") and not content[0].get("equity_pledged_info","") and not content[0].get("Shareholder_info","") and not content[0].get("judicial_assist_info","") and not content[0].get("knowledge_info","") and not content[0].get("brand_info","") and not content[0].get("annual_shareholder_info","") and not content[0].get("annual_info",""):
            self.status = PASSWORD_IS_NULL
        self.quit_webdriver()
        return content

    def wait_for(self, by1, by2):
        self.br.dc.setts(time.time())
        self.br.dc.setstatus(0)
        return self.wait.until(EC.presence_of_element_located((by1, by2)))

    def input_params(self, name):
        self.logger.info('正在打开官网URL')
        try:
            self.br.get1(self.LoginUrl) 
            # self.br.refresh()
        except Exception as e:
            self.logger.error(e)
            try:
                # 防止再次刷新的时候出现卡死,所以没用热刷新的方式
                self.br.get1(self.br.current_url)
            except Exception as f:
                self.logger.error(f)

        self.logger.info('已经进入官网')
        ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="btn_query"]')))
        element = self.wait_for(By.ID, "keyword")
        element.send_keys(name)
        element = self.wait_for(By.ID, "btn_query")
        element.click()
        self.status= CRAWL_SUCCESS

    def _save_captcha(self, codeurl):
        """
        下载验证码，返回图片b64编码，
        """
        self.logger.info("刷新验证码")
        try:
            codeContent = self.session.get(codeurl, headers=IMGHEADERS).content
            self.logger.debug("验证码二进制内容：{0}".format(codeContent)[:50])
            self.logger.info("下载验证码")
            self.status = NEED_BCODE
            with open(os.path.join(os.path.dirname(__file__), "captcha.png").replace("\\", "/"), 'wb') as f:
                f.write(codeContent)
            self.logger.info("验证码图片已保存!")
            bcode = base64.b64encode(codeContent)
            self.status= CRAWL_SUCCESS
            return bcode
        except:
            s = traceback.format_exc()
            self.logger.error("刷新验证码错误：%s" % s)
            self.status, self.desc = BCODE_IS_NULL, BCODE_IS_NULL_DESC
            # return {"error": "超时或代码异常"}

    def quit_webdriver(self):
        self.br.quit()
        self.br.dc.setterm(1)

    def get_webdriver(self, name):
        '''选择爬取的方式'''
        try:
            if name.lower() == "phantomjs":
                self.dcap = dict(DesiredCapabilities.PHANTOMJS)
                self.dcap["phantomjs.page.customHeaders.User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
                self.status= CRAWL_SUCCESS
                return webdriver.PhantomJS(desired_capabilities = self.dcap)
            elif name.lower() == "chrome":
                display = Display(visible=0, size=(1920,1080))
                display.start()
                self.status= CRAWL_SUCCESS
                # return webdriver.Chrome("/usr/local/bin/chromedriver")
                return webdriver.Chrome()
            elif name.lower() == "firefox":
                display = Display(visible=0, size=(1920,1080))
                display.start()
                self.status= CRAWL_SUCCESS
                return webdriver.Firefox()
        except Exception as e:
            self.logger.error('运行无头浏览器错误')
            self.status, self.decs = PASSWORD_IS_NULL, PASSWORD_IS_NULL_DESC

    def get_bcode(self):
        '''获取从redis中获取的坐标值'''
        self.startTime = datetime.now()
        while True:
            self.logger.info(u'等待用户传入坐标')
            inputValue = self.redisUtils.getNotify(self.token, 'bcode')
            if inputValue:
                coordinate = self.prase_bcode(inputValue)
                self.redisUtils.DelNotify(self.token, "bcode")
                return coordinate
            else:
                self.finishTime = datetime.now()
                tail_time = self.finishTime - self.startTime
                if tail_time.total_seconds() > 120:
                    self.logger.info('接收用输入超时:%s' % self.token)
                    self.desc = '接收用户输入超时'
                    time.sleep(1)
                    break
            time.sleep(1)

    def prase_bcode(self, zuobiao):
        '''坐标处理'''
        try:
            zuobiao_list1 = zuobiao.split('_')
            zuobiao_list = zuobiao_list1[1:]
            len_zuobiao = len(zuobiao_list)/2
            coordinate = []
            for num in range(len_zuobiao):
                list_n = []
                list_n.append(zuobiao_list[2*num])
                list_n.append(zuobiao_list[2*num + 1])
                coordinate.append(list_n)
            self.status= CRAWL_SUCCESS
            return coordinate
        except Exception as e:
            self.logger.error('处理坐标异常: %s' %e)
            self.status = IDCARD_ERROR
            return ''

    def element_click(self, coor):
        '''模拟依次点击'''
        try:
            if coor and self.br.find_element_by_class_name("geetest_item_img"):
                for i in range(len(coor)):
                    element = self.br.find_element_by_class_name("geetest_item_img")
                    ActionChains(self.br).move_to_element_with_offset(
                                    to_element = element,
                                    xoffset=int(coor[i][0])-7,
                                    yoffset=int(coor[i][1])-5).perform()
                    ActionChains(self.br).click().perform()
                    time.sleep(0.8)
                element_cli = self.wait_for(By.CLASS_NAME, "geetest_commit_tip")
                element_cli.click()
                time.sleep(0.5)
                element = self.wait_for(By.CLASS_NAME, "geetest_result_tip")
                ans = element.text.encode("utf-8")
                self.status= CRAWL_SUCCESS
                return ans
            else:
                self.logger.info('暂无图片点击')
                return '失败'
        except Exception as e:
            self.logger.error('破解验证码失败')
            self.status = PASSWORD_ERROR

    def click_pic(self, info):
        '''获取图片,将图片的base64发送给服务或第三方来处理'''
        self.logger.info('需要用户提供点击操作')
        try:
            ima_url = ifNotEmptyGetIndex(info.xpath("//*[@class='geetest_item_img']/@src"))
            card_base = self._save_captcha(ima_url)
            Data = {
                'token':self.token,
                'img_base64': card_base,
                'spider_name': 'gsxt',
                'userid': 'yinzhouyinhang'
            }
            content = self.session.post(url='http://127.0.0.1:8000/img',data=Data).content
            content = eval(content)
            url_imag = content.get("result", "")
            self.decs = '请输入url,请求图片并点击'
            redis_dict = {
                "image_url": url_imag,
                "image_base64":"data:image/jpg;base64,"+card_base,
                "token":self.token
            }
            self.redisUtils.setNotify(token = self.token, val = "1", decs=self.decs, result=redis_dict)
            self.br.dc.setstatus(1)
            self.br.dc.setts(time.time())
            self.logger.info("begin wait bcode....")
            co_ordinate = self.get_bcode()
            self.logger.info("begin set status....")
            self.br.dc.setstatus(0)
            self.br.dc.setts(time.time())
            ans = self.element_click(co_ordinate)
            return ans
        except Exception as e:
            self.logger.error(e)
            self.status= CRAWL_SUCCESS


    def hack_geetest(self, company='大连火眼征信管理有限公司北京'):
        '''爬取的流程'''
        try:
            self.input_params(company)
            for i in range(10):
                self.logger.info(u'开始判断验证码的类型')
                time.sleep(1)
                info = etree.HTML(str(self.br.page_source))
                if info.xpath("//*[@class='geetest_item_img']/@src"):
                    for j in range(3):
                        info2 = etree.HTML(str(self.br.page_source))
                        ans = self.click_pic(info2)
                        self.logger.info('破解验证码结果: %s' %ans)
                        if '成功' in ans:
                            ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="search_result_span1"]')))
                            self.status= CRAWL_SUCCESS
                            return country1(self.br).data()
                        elif '失败' in ans and j < 2:
                            time.sleep(3)
                            self.logger.info('图片验证点击失败')
                            self.status = BCODE_ERROR
                        elif '失败' in ans and j == 2:
                            self.logger.info('最后一次图片验证点击失败')
                            self.status = BCODE_ERROR
                            return
                        else:
                            self.logger.info('图片验证点击失败,正在重新请求')
                            self.status = BCODE_ERROR

                elif info.xpath("//*[@class='geetest_slider_track']/div/text()"):
                    self.logger.info('系统正在重试')
                    self.input_params(company)

                else:
                    time.sleep(2)
                    info = etree.HTML(str(self.br.page_source))
                    if info.xpath("//*[@class='ads-right']/div[1]/div/text()"):
                        self.status= CRAWL_SUCCESS
                        return country1(self.br).data()
                    else:
                        self.logger.info('尝试再次访问')
                        time.sleep(1)
                        self.input_params(company)
        except Exception as e:
            self.logger.error('智能检测程序错误%s'%e)
            self.status = CRAWL_FAIL
            # return e

    def login(self,flag):
        if self.area == '陕西':
            millis = int(round(time.time() * 1000))
            self.LoginUrl = self.LoginUrl + str(millis)
        try:
            content = self.run(self.keyword)
            return content
        except Exception as e:
            self.status = CRAWL_FAIL
            self.logger.error('抓取错误：%s' % e)
        
    @Time()
    def crawl(self, flag=""):
        CurTime = datetime.now().strftime("%Y-%m-%d")
        PastTime = (datetime.now() - timedelta(days=729)).strftime("%Y-%m-%d")
        try:

            content = self.login(flag)
            self.GJJInfo.append(content)
            self.result.append(self.GJJInfo[0])

        except:
            s = traceback.format_exc()
            self.logger.error("抓取错误：%s" % s)
            self.status, self.desc = self.status, PROGRAM_ERROR_DESC
        finally:
                try:
                    if len(self.result) == 1 and self.status == CRAWL_SUCCESS:
                        self.desc = CRAWL_SUCCESS_DESC
                        result_json = json.dumps(self.result[0], ensure_ascii=False)
                        print result_json
                        self.redisUtils.setNotify(type=TYPEVALUE,token=self.token, val="1", decs="抓取成功！", result=result_json)
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

                    elif self.status == PASSWORD_IS_NULL:
                        self.desc = PASSWORD_IS_NULL_DESC
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
    # millis = str(int(round(time.time() * 1000)))
    # url = url_area.get('陕西','') +millis
    # user = {"idCard": "大连火眼征信管理有限公司北京", "token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    # user = {"area":"河北","idCard": "河北兰科", "token": "tokentokentokentokentoken","userid":"xxxxxxxxxxxxxxxx"}
    user = {"idCard":"山西建龙钢铁有限公司", "token": "tokentokentokentokentoken", "userid":"xxxxxxxxxxxxxxxx"}
    user.update({"result": []})
    sp = SpiderMain(user)
    sp.crawl("auto")
    

