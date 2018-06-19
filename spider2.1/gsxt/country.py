#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
#-----------------------------------------------------------------------
import sys
# sys.path.append('../..')
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
import re
import math
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import ui
from selenium import webdriver
from lxml import etree
from driverclean import DriverClean

from __Utils.StandFormat import hypc_enterprise_credit,hypc_accumulation_fund
from __Utils.constants import PROXYADDR
from qiyegsxtConstants import TIMEOUT, REQUEST_RETRY, SAMPLEFLAG, NEED_BCODE, NOT_NEED_BCODE, PROGRAM_ERROR,NOT_NEED_BCODE_DESC, IDCARD_ERROR, IDCARD_ERROR_DESC, PASSWORD_ERROR, PASSWORD_ERROR_DESC, CRAWL_TIMEOUT, CRAWL_READY, CRAWL_SUCCESS, PROGRAM_ERROR_DESC, CRAWL_FAIL, CRAWL_FAIL_DESC, CRAWL_TIMEOUT_DESC, CRAWL_SUCCESS_DESC, IMGHEADERS, BCODE_ERROR, BCODE_ERROR_DESC, \
    TYPEVALUE,FIRSTHEADER,INFOHEADERS,RUSER_AGENTS

logging.config.fileConfig('gsxt/gsxtlogger.conf')


def ifNotEmptyGetIndex(somelist,index=0):
    """check to see it's not empty"""
    if somelist: 
        return somelist[index]
    else:
        return ''

class country1(object):

    logger = logging.getLogger()
    def __init__(self, br):
        self.br = br
        self.info = []
        self.baseInfo = {}
        self.orignInfo = []
        self.mainPersonInfo = []
        self.branchDeptInfo=[]
        self.changeInfo = []
        self.chattelInfo = []
        self.stockInfo = []
        self.knowledgeInfo = []
        self.trademarkInfo = []
        self.directoryInfo = []
        self.checkInfo = []
        self.assistanceInfo = []
        self.administrativeInfo = []
        self.OrigndetailInfo = []
        self.annualInfo = []
        self.wait = WebDriverWait(self.br, 10, 0.5)
        self.br.set_page_load_timeout(10)
        self.br.set_script_timeout(15)


    def wait_for(self, by1, by2):
        # print __file__, "wait_for"
        self.br.dc.setts(time.time())
        self.br.dc.setstatus(0)
        return self.wait.until(EC.presence_of_element_located((by1, by2)))

    def parseBaseinfo(self,content):
        '''
        获取公司主要信息
        :param content:
        :return:
        '''
        try:
            self.logger.info("【开始解析公司基本信息】")
            # 基础信息
            common_code_re = re.compile(r'<!-- 这里还需要添加业务逻辑 -->[\s]*(.+)[\s]*')
            common_code = ifNotEmptyGetIndex(common_code_re.findall(content))   # 统一社会信用代码
            company_name_re = re.compile(r'企业名称：</dt>[\s]*<dd class="result" title=\".+\">(.*)[\s]*</dd>')
            company_name_re1 = re.compile(r'名称：</dt>[\s]*<dd class="result" title=\".+\">(.*)[\s]*</dd>')
            company_name = ifNotEmptyGetIndex(company_name_re.findall(content)) or ifNotEmptyGetIndex(company_name_re1.findall(content)) # 企业名称/名称：
            common_type_re = re.compile(r'类型：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            common_type = ifNotEmptyGetIndex(common_type_re.findall(content))# 类型
            person_re = re.compile(r'法定代表人：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            person_re1 = re.compile(r'负责人：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>') # 法定代表人/负责人/投资人/经营者：
            person_re2 = re.compile(r'投资人：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            person_re3 = re.compile(r'经营人：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            person = ifNotEmptyGetIndex(person_re.findall(content)) or ifNotEmptyGetIndex(person_re1.findall(content)) or ifNotEmptyGetIndex(person_re2.findall(content)) or ifNotEmptyGetIndex(person_re3.findall(content)) # 法定代表人
            register_money_re = re.compile(r'注册资本：</dt>[\s]*<dd class="result">[\s]*(.*)[\s]*</dd>')
            register_money = ifNotEmptyGetIndex(register_money_re.findall(content)) # 注册资本
            establish_date_re = re.compile(r'成立日期：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            establish_date_re1 = re.compile(r'注册日期：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            establish_date = ifNotEmptyGetIndex(establish_date_re.findall(content)) or ifNotEmptyGetIndex(establish_date_re1.findall(content)) # 成立日期/注册日期：
            start_date_re = re.compile(r'营业期限自：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            start_date_re1 = re.compile(r'经营期限自：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            start_date = ifNotEmptyGetIndex(start_date_re.findall(content)) or ifNotEmptyGetIndex(start_date_re1.findall(content)) # 营业期限自/经营期限自
            end_time_re = re.compile(r'营业期限至：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            end_time_re1 = re.compile(r'经营期限至：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            end_time = ifNotEmptyGetIndex(end_time_re.findall(content)) or ifNotEmptyGetIndex(end_time_re1.findall(content))# 营业期限至/经营期限至
            register_dept_re = re.compile(r'登记机关：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            register_dept = ifNotEmptyGetIndex(register_dept_re.findall(content)) # 登记机关
            verify_date_re = re.compile(r'核准日期：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            verify_date = ifNotEmptyGetIndex(verify_date_re.findall(content)) # 核准日期
            register_state_re = re.compile(r'登记状态：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            register_state = ifNotEmptyGetIndex(register_state_re.findall(content)) # 登记状态
            address_re = re.compile(r'营业场所：</dt>[\s]*<dd class="result" title=".*">(.*)[\s]*</dd>')
            address_re1 = re.compile(r'住所：</dt>[\s]*<dd class="result" title=".*">(.*)[\s]*</dd>')
            address_re2 = re.compile(r'经营场所：</dt>[\s]*<dd class="result" title=".*">(.*)[\s]*</dd>')
            address = ifNotEmptyGetIndex(address_re.findall(content)) or ifNotEmptyGetIndex(address_re1.findall(content)) or ifNotEmptyGetIndex(address_re2.findall(content))   # 住所/营业场所/经营场所
            common_range_re = re.compile(r'经营范围：</dt>[\s]*<dd>(.*)[\s]*</dd>')
            common_range_re1 = re.compile(r'经营范围：</dt>[\s]*<dd class="result">(.*)[\s]*</dd>')
            common_range = ifNotEmptyGetIndex(common_range_re.findall(content)) or ifNotEmptyGetIndex(common_range_re1.findall(content))    # 经营范围
            self.baseInfo = hypc_enterprise_credit.base_info(
                company_name=company_name,# 企业名称
                branch_dept_code=common_code,# 统一社会信用代码
                common_type=common_type,# 类型
                person=person,# 法定代表人
                register_money=register_money,# 注册资本
                establish_date=establish_date,# 成立日期
                start_date=start_date,# 营业期限自
                end_time=end_time,# 营业期限至
                register_dept=register_dept,# 登记机关
                verify_date=verify_date,# 核准日期
                register_status=register_state,# 登记状态
                address=address,# 住所
                common_range=common_range# 经营范围
                )
            self.logger.info("【公司基本信息解析】【完成】")
        except Exception as e:
            s = traceback.format_exc()
            #     status = '0'
            #     # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            self.status = CRAWL_TIMEOUT
            raise Exception("【解析公司基本信息】【出错】%s" % s)

    def parseOrigninfo(self,page_source):
        '''
        股东出资信息
        :param page_source:
        :return:
        '''
        try:
            self.logger.info("【开始股东出资信息解析】")
            if page_source.xpath('//*[@id="shareholderInfo_info"]/text()'):
                page_change = page_source.xpath('//*[@id="shareholderInfo_info"]/text()')[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = 0
            # 发起人及出资人信息列表
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    orign_list = page_source.xpath('//*[@id="sharfdeholderInfo"]/tbody/tr')
                    if len(orign_list) > 0:
                        # self.logger.warn('【存在发起人及出资人信息，公司名称为：%s】' % self.key_name)
                        for i in range(len(orign_list)):
                            i = i + 1
                            orign_name_list = page_source.xpath(
                                '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[2]/text()')
                            orign_name = orign_name_list[0].strip() if len(orign_name_list) > 0 else ''
                            orign_type_list = page_source.xpath(
                                '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[3]/text()')
                            orign_type = ''
                            for j in range(len(orign_type_list)):
                                orign_type1 = orign_type_list[j].strip() if len(orign_type_list) > 0 else ''
                                orign_type = orign_type + orign_type1
                            card_type_list = page_source.xpath(
                                '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[4]/text()')
                            card_type = card_type_list[0].strip() if len(card_type_list) > 0 else ''
                            card_num_list = page_source.xpath(
                                '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[5]/text()')
                            card_num = ''.join(card_num_list)
                            # card_num = card_num_list[0].strip() if len(card_num_list) > 0 else ''
                            detail_list = page_source.xpath('//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[6]/text()')
                            detail = detail_list[0].strip() if len(detail_list) > 0 else ''
                            self.orignInfo.append(hypc_enterprise_credit.Shareholder_info(
                                    shareholder = orign_name,
                                    shareholder_type = orign_type,
                                    card_type = card_type,
                                    card_num = card_num,
                                    detail = detail,
                                ))
                            
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        orign_list = page_source.xpath('//*[@id="shareholderInfo"]/tbody/tr')
                        if len(orign_list) > 0:
                            # self.logger.warn('【存在发起人及出资人信息，公司名称为：%s】' % self.key_name)
                            for i in range(len(orign_list)):
                                i = i + 1
                                orign_name_list = page_source.xpath(
                                    '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[2]/text()')
                                orign_name = orign_name_list[0].strip() if len(orign_name_list) > 0 else ''
                                orign_type_list = page_source.xpath(
                                    '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[3]/text()')
                                orign_type = ''
                                for j in range(len(orign_type_list)):
                                    orign_type1 = orign_type_list[j].strip() if len(orign_type_list) > 0 else ''
                                    orign_type = orign_type + orign_type1
                                card_type_list = page_source.xpath(
                                    '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[4]/text()')
                                card_type = card_type_list[0].strip() if len(card_type_list) > 0 else ''
                                card_num_list = page_source.xpath(
                                    '//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[5]/text()')
                                card_num = card_num_list[0].strip() if len(card_num_list) > 0 else ''
                                detail_list = page_source.xpath('//*[@id="shareholderInfo"]/tbody/tr[' + str(i) + ']/td[6]/text()')
                                detail = detail_list[0].strip() if len(detail_list) > 0 else ''
                                self.orignInfo.append(hypc_enterprise_credit.Shareholder_info(
                                    shareholder = orign_name,
                                    shareholder_type = orign_type,
                                    card_type = card_type,
                                    card_num = card_num,
                                    detail = detail,
                                ))
                            element = self.br.find_element_by_xpath1("//*[@id='shareholderInfo_wrapper']/div[3]//div[2]//li[last()-1]")
                            element.click()
                            time.sleep(1)
                            page_source = etree.HTML(self.br.page_source)
            else:
                self.logger.info("【暂无发起人及出资人信息解析】【完成】")
                self.orignInfo.append(hypc_enterprise_credit.Shareholder_info(
                        shareholder = "",
                        shareholder_type = "",
                        card_type = "",
                        card_num = "",
                        detail = "",
                    ))
            self.logger.info("【发起人及出资人信息解析】【完成】")
        except:
            s = traceback.format_exc()
            self.status = CRAWL_FAIL
            # self.push.push_data(self.status, CRAWL_FAIL_DESC)
            raise Exception("【解析发起人及出资人信息】【出错】%s" % s)



    def parsePerson(self,page_source):
        '''
        解析主要人员信息
        :param page_source:
        :return:
        '''
            
        try:
            self.logger.info("【主要人员信息解析】【完成】")
            person_list = page_source.xpath('//*[@id="personInfo"]/ul/li')
            if len(person_list) > 0:
                # self.logger.warn('【存在主要人员信息，公司名称为：%s】' % self.key_name)
                for i in range(len(person_list)):
                    # 循环获取人员列表信息
                    i = i + 1
                    person_name_list = page_source.xpath('//*[@id="personInfo"]/ul/li[' + str(i) + ']/a/div[1]/text()')
                    person_name = ''
                    for j in range(len(person_name_list)):
                        orign_type1 = person_name_list[j].strip() if len(person_name_list) > 0 else ''
                        person_name = person_name + orign_type1

                    person_position_list = page_source.xpath(
                        '//*[@id="personInfo"]/ul/li[' + str(i) + ']/a/div[2]/span/img') 
                    # or page_source.xpath('//*[@id="personInfo"]/ul/li[' + str(i) + ']/a/div[2]/span/@title')
                    person_position = person_position_list[0].attrib['src'].strip() if len(person_position_list) > 0 else ''
                    
                    person_position1_list = page_source.xpath('//*[@id="personInfo"]/ul/li[' + str(i) + ']/a/div[2]/span/@title')
                    person_position1 = person_position1_list[0].strip() if len(person_position1_list) > 0 else ''
                    
                    person_position = person_position if person_position else person_position1

                    self.mainPersonInfo.append(hypc_enterprise_credit.key_person_info(
                            person_name = person_name,
                            person_position = person_position,
                        ))
            else:
                self.logger.info("【暂无主要人员信息解析】【完成】")
                self.mainPersonInfo.append(hypc_enterprise_credit.key_person_info(
                        person_name = '',
                        person_position = '',
                    ))
            self.logger.info("【主要人员信息解析】【完成】")
            # return mainPersonInfo
        except Exception as e:
            s = traceback.format_exc()
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【主要人员信息解析】【出错】%s" % s)

    def parseBranchDeptinfo(self,page_source):
        '''
        解析分支机构信息
        :return:
        '''
        try:
            self.logger.info("【开始解析分支机构信息】")
            # 获取分支机构信息
            branch_dept_list = page_source.xpath('//*[@id="branchGroupForAll"]/li')
            if len(branch_dept_list) > 0:
                # self.logger.warn('【存在分支机构信息，公司名称为：%s】' % self.key_name)
                for i in range(len(branch_dept_list)):
                    i = i + 1
                    branch_dept_name_list = page_source.xpath(
                        '//*[@id="branchGroupForAll"]/li[' + str(i) + ']/a/div/text()')
                    branch_dept_name = branch_dept_name_list[0].strip() if len(branch_dept_name_list) > 0 else ''
                    branch_dept_code_list = page_source.xpath(
                        '//*[@id="branchGroupForAll"]/li[' + str(i) + ']/a/span/span/text()')
                    branch_dept_code = branch_dept_code_list[0].strip() if len(branch_dept_code_list) > 0 else ''
                    branch_dept_register_list = page_source.xpath(
                        '//*[@id="branchGroupForAll"]/li[' + str(i) + ']/a/span/div/span/text()')
                    branch_dept_register = branch_dept_register_list[0].strip() if len(branch_dept_register_list) > 0 else ''
                    
                    self.branchDeptInfo.append(hypc_enterprise_credit.branch_info(
                            branch_name = branch_dept_name,
                            branch_reg_no = branch_dept_code,
                            branch_reg_organ = branch_dept_register,
                        ))
                    
            else:
                self.logger.info("【暂无分支机构信息解析】")
                self.branchDeptInfo.append(hypc_enterprise_credit.branch_info(
                        branch_name = "",
                        branch_reg_no = "",
                        branch_reg_organ = "",
                    ))
            self.logger.info("【分支机构信息解析】【完成】")
            # return branchDeptInfo
        except Exception as e:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【分支结构信息解析】【出错】%s" % s)


    def parseChangeinfo(self,page_source):
        '''
        变更信息解析
        :return:
        '''
        try:
            self.logger.info("【开始解析变更信息】")
            if page_source.xpath("//*[@id='altInfo_info']/text()"):
                page_change = page_source.xpath("//*[@id='altInfo_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = '0'
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    change_list = page_source.xpath('//*[@id="altInfo"]/tbody/tr')
                    if len(change_list) > 0:
                        # self.logger.warn('【存在知变更信息，公司名称为：%s】' % self.key_name)
                        for i in range(len(change_list)):
                            i = i + 1
                            change_active_list = page_source.xpath('//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[2]/text()')
                            change_active = ''.join(change_active_list)
                            # change_active = change_active_list[0].strip() if len(change_active_list) > 0 else ''
                            change_content_pre_list = page_source.xpath(
                                '//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[3]/div/span/text()')
                            change_content_pr = change_content_pre_list[0].strip() if len(change_content_pre_list) > 0 else ''
                            change_content_after_list = page_source.xpath(
                                '//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[4]/div/span/text()')
                            change_content_after = change_content_after_list[0].strip() if len(change_content_after_list) > 0 else ''
                            change_date_list = page_source.xpath('//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[5]/text()')
                            change_date = change_date_list[0].strip() if len(change_date_list) > 0 else ''
                            self.changeInfo.append(hypc_enterprise_credit.change_info(
                                    change_active = change_active,
                                    change_content_pr = change_content_pr,
                                    change_content_after = change_content_after,
                                    change_date = change_date,
                                ))
                            
                elif int(page_change_count) > 1:
                    for i in range(int(page_change_count)):
                        change_list = page_source.xpath('//*[@id="altInfo"]/tbody/tr')
                        if len(change_list) > 0:
                            # self.logger.warn('【存在知变更信息，公司名称为：%s】' % self.key_name)
                            for i in range(len(change_list)):
                                i = i + 1
                                change_active_list = page_source.xpath('//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[2]/text()')
                                change_active = ''.join(change_active_list)
                                # change_active = change_active_list[0].strip() if len(change_active_list) > 0 else ''
                                change_content_pre_list = page_source.xpath(
                                    '//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[3]/div/span/text()')
                                change_content_pr = change_content_pre_list[0].strip() if len(change_content_pre_list) > 0 else ''
                                change_content_after_list = page_source.xpath(
                                    '//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[4]/div/span/text()')
                                change_content_after = change_content_after_list[0].strip() if len(change_content_after_list) > 0 else ''
                                change_date_list = page_source.xpath('//*[@id="altInfo"]/tbody/tr[' + str(i) + ']/td[5]/text()')
                                change_date = change_date_list[0].strip() if len(change_date_list) > 0 else ''
                                self.changeInfo.append(hypc_enterprise_credit.change_info(
                                    change_active = change_active,
                                    change_content_pr = change_content_pr,
                                    change_content_after = change_content_after,
                                    change_date = change_date,
                                ))
                        element = self.br.find_element_by_xpath1("//*[@id='altInfo_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        # ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="altInfo"]/tbody/tr')))
                        page_source = etree.HTML(self.br.page_source)
            else:
                self.logger.info("【暂无变更信息解析】")
                self.changeInfo.append(hypc_enterprise_credit.change_info(
                        change_active = "",
                        change_content_pr = "",
                        change_content_after = "",
                        change_date = "",
                    ))
            self.logger.info("【变更信息解析】【完成】")
            # return changeInfo
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【变更信息解析】【出错】%s" % s)

    def parseChattelinfo(self,page_source):
        '''
        解析动产抵押信息
        :return:
        '''
        try:
            self.logger.info("【开始解析动产抵押信息】")
            if page_source.xpath("//*[@id='needPaging_guaranty_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_guaranty_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = '0'
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    chattel_list = page_source.xpath("//*[@id='needPaging_guaranty_wrapper']//tbody/tr")
                    if len(chattel_list) > 0:
                        # 动产抵押信息存在
                        for i in range(len(chattel_list)):
                            i = i + 1
                            registrat_number_list = page_source.xpath(
                            "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                            registrat_number = registrat_number_list[0].strip() if len(registrat_number_list) > 0 else ''
                            registrat_date_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                            registrat_date = registrat_date_list[0].strip() if len(registrat_date_list) > 0 else ''
                            registrat_authory_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                            registrat_authory = registrat_authory_list[0].strip() if len(registrat_authory_list) > 0 else ''
                            amount_claims_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                            amount_claims = amount_claims_list[0].strip() if len(amount_claims_list) > 0 else ''
                            state_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[6]/text()")
                            state = state_list[0].strip() if len(state_list) > 0 else ''
                            announcement_date_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[7]/text()")
                            announcement_date = announcement_date_list[0].strip() if len(announcement_date_list) > 0 else ''
                            details_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[8]/span/text()")
                            details = details_list[0].strip() if len(details_list) > 0 else ''
                            self.chattelInfo.append(hypc_enterprise_credit.chattel_info(
                                    chattel_reg_no = registrat_number,
                                    chattel_reg_date = registrat_date,
                                    chattel_organ_name = registrat_authory,
                                    chattel_loan_amount = amount_claims,
                                    chattel_status = state,
                                    chattel_pub_date = announcement_date,
                                    detail = details,
                                ))
                            
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        chattel_list = page_source.xpath("//*[@id='needPaging_guaranty_wrapper']//tbody/tr")
                        if len(chattel_list) > 0:
                            # self.logger.warn('【存在动产抵押出质登记信息，公司名称为：%s】' % self.key_name)
                            for i in range(len(chattel_list)):
                                i = i + 1
                                registrat_number_list = page_source.xpath(
                                "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                                registrat_number = registrat_number_list[0].strip() if len(registrat_number_list) > 0 else ''
                                registrat_date_list = page_source.xpath(
                                    "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                                registrat_date = registrat_date_list[0].strip() if len(registrat_date_list) > 0 else ''
                                registrat_authory_list = page_source.xpath(
                                    "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                                registrat_authory = registrat_authory_list[0].strip() if len(registrat_authory_list) > 0 else ''
                                amount_claims_list = page_source.xpath(
                                    "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                                amount_claims = amount_claims_list[0].strip() if len(amount_claims_list) > 0 else ''
                                state_list = page_source.xpath(
                                    "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[6]/text()")
                                state = state_list[0].strip() if len(state_list) > 0 else ''
                                announcement_date_list = page_source.xpath(
                                    "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[7]/text()")
                                announcement_date = announcement_date_list[0].strip() if len(announcement_date_list) > 0 else ''
                                details_list = page_source.xpath(
                                    "//*[@id='needPaging_guaranty_wrapper']//tbody/tr[" + str(i) + "]/td[8]/span/text()")
                                details = details_list[0].strip() if len(details_list) > 0 else ''
                                self.chattelInfo.append(hypc_enterprise_credit.chattel_info(
                                    chattel_reg_no = registrat_number,
                                    chattel_reg_date = registrat_date,
                                    chattel_organ_name = registrat_authory,
                                    chattel_loan_amount = amount_claims,
                                    chattel_status = state,
                                    chattel_pub_date = announcement_date,
                                    detail = details,
                                ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_guaranty_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)
                    
            else:
                self.logger.info("【暂无动产抵押信息】")
                # 动产抵押信息不存在
                self.chattelInfo.append(hypc_enterprise_credit.chattel_info(
                        chattel_reg_no = "",
                        chattel_reg_date = "",
                        chattel_organ_name = "",
                        chattel_loan_amount = "",
                        chattel_status = "",
                        chattel_pub_date = "",
                        detail = "",
                    ))
            self.logger.info("【动产抵押信息解析】【完成】")
            # return chattelInfo
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【动产抵押信息解析】【出错】%s" % s)




    def parseStockinfo(self, page_source):
        '''
        解析获取股权出质登记信息
        :return:
        '''
        try:
            self.logger.info("【开始解析股权出质登记信息】")
            if page_source.xpath("//*[@id='needPaging_pledge_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_pledge_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = 0
            # 总共有多少页
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    stock_list = page_source.xpath('//*[@id="needPaging_pledge"]/tbody/tr')
                    if len(stock_list) > 0:
                        # 动产抵押信息存在
                        # self.logger.warn('【存在股权出质登记信息，公司名称为：%s】' % self.key_name)
                        for i in range(len(stock_list)):
                            i = i + 1
                            equity_pledged_no_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[2]/text()')
                            equity_pledged_no = equity_pledged_no_list[0].strip() if len(equity_pledged_no_list) > 0 else ''
                            equity_pledged_pledgor_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[3]/text()')
                            equity_pledged_pledgor = equity_pledged_pledgor_list[0].strip() if len(equity_pledged_pledgor_list) > 0 else ''
                            equity_pledged_idcard_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[4]/text()')
                            equity_pledged_idcard = equity_pledged_idcard_list[0].strip() if len(
                                equity_pledged_idcard_list) > 0 else ''
                            equity_pledged_amount_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[5]/text()')
                            equity_pledged_amount = equity_pledged_amount_list[0].strip() if len(equity_pledged_amount_list) > 0 else ''
                            equity_pledged_pawnee_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[6]/text()')
                            equity_pledged_pawnee = equity_pledged_pawnee_list[0].strip() if len(equity_pledged_pawnee_list) > 0 else ''
                            equity_pledged_reg_date_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[8]/text()')
                            equity_pledged_reg_date = equity_pledged_reg_date_list[0].strip() if len(equity_pledged_reg_date_list) > 0 else ''
                            equity_pledged_status_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[9]/text()')
                            equity_pledged_status = equity_pledged_status_list[0].strip() if len(equity_pledged_status_list) > 0 else ''
                            equity_pledged_pub_date_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[10]/text()')
                            equity_pledged_pub_date = equity_pledged_pub_date_list[0].strip() if len(equity_pledged_pub_date_list) > 0 else ''
                            
                            detail_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[11]/span/text()')
                            detail = detail_list[0].strip() if len(detail_list) > 0 else ''
                            self.stockInfo.append(hypc_enterprise_credit.equity_pledged_info(
                                    equity_pledged_no=equity_pledged_no,  # 登记编号
                                    equity_pledged_pledgor=equity_pledged_pledgor,  # 出质人
                                    equity_pledged_idcard=equity_pledged_idcard,  # 证照/证件号码
                                    equity_pledged_amount=equity_pledged_amount,  # 出质股权数额
                                    equity_pledged_pawnee=equity_pledged_pawnee,  # 质权人
                                    equity_pledged_reg_date=equity_pledged_reg_date,  # 股权出质设立登记日期
                                    equity_pledged_status=equity_pledged_status,  # 状态
                                    equity_pledged_pub_date=equity_pledged_pub_date,  # 公示日期
                                    detail=detail,  # 详情
                                ))
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        stock_list = page_source.xpath('//*[@id="needPaging_pledge"]/tbody/tr')
                        if len(stock_list) > 0:
                            # self.logger.warn('【存在股权出质登记信息，公司名称为：%s】' % self.key_name)
                            for i in range(len(stock_list)):
                                i = i + 1
                                # //*[@id="needPaging_pledge"]/tbody/tr//tbody/tr/td[1]/text()
                                equity_pledged_no_list = page_source.xpath(
                                '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[2]/text()')
                                equity_pledged_no = equity_pledged_no_list[0].strip() if len(equity_pledged_no_list) > 0 else ''
                                equity_pledged_pledgor_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[3]/text()')
                                equity_pledged_pledgor = equity_pledged_pledgor_list[0].strip() if len(equity_pledged_pledgor_list) > 0 else ''
                                equity_pledged_idcard_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[4]/text()')
                                equity_pledged_idcard = equity_pledged_idcard_list[0].strip() if len(
                                    equity_pledged_idcard_list) > 0 else ''
                                equity_pledged_amount_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[5]/text()')
                                equity_pledged_amount = equity_pledged_amount_list[0].strip() if len(equity_pledged_amount_list) > 0 else ''
                                equity_pledged_pawnee_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[6]/text()')
                                equity_pledged_pawnee = equity_pledged_pawnee_list[0].strip() if len(equity_pledged_pawnee_list) > 0 else ''
                                equity_pledged_reg_date_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[8]/text()')
                                equity_pledged_reg_date = equity_pledged_reg_date_list[0].strip() if len(equity_pledged_reg_date_list) > 0 else ''
                                equity_pledged_status_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[9]/text()')
                                equity_pledged_status = equity_pledged_status_list[0].strip() if len(equity_pledged_status_list) > 0 else ''
                                equity_pledged_pub_date_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[10]/text()')
                                equity_pledged_pub_date = equity_pledged_pub_date_list[0].strip() if len(equity_pledged_pub_date_list) > 0 else ''
                                
                                detail_list = page_source.xpath(
                                    '//*[@id="needPaging_pledge"]/tbody/tr[' + str(i) + ']//tbody/tr/td[11]/span/text()')
                                detail = detail_list[0].strip() if len(detail_list) > 0 else ''
                                self.stockInfo.append(hypc_enterprise_credit.equity_pledged_info(
                                        equity_pledged_no=equity_pledged_no,  # 登记编号
                                        equity_pledged_pledgor=equity_pledged_pledgor,  # 出质人
                                        equity_pledged_idcard=equity_pledged_idcard,  # 证照/证件号码
                                        equity_pledged_amount=equity_pledged_amount,  # 出质股权数额
                                        equity_pledged_pawnee=equity_pledged_pawnee,  # 质权人
                                        equity_pledged_reg_date=equity_pledged_reg_date,  # 股权出质设立登记日期
                                        equity_pledged_status=equity_pledged_status,  # 状态
                                        equity_pledged_pub_date=equity_pledged_pub_date,  # 公示日期
                                        detail=detail,  # 详情
                                    ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_pledge_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)

            else:
                self.logger.info("【暂无股权出质登记信息】")
                self.stockInfo.append(hypc_enterprise_credit.equity_pledged_info(
                        equity_pledged_no="",  # 登记编号
                        equity_pledged_pledgor="",  # 出质人
                        equity_pledged_idcard="",  # 证照/证件号码
                        equity_pledged_amount="",  # 出质股权数额
                        equity_pledged_pawnee="",  # 质权人
                        equity_pledged_reg_date="",  # 股权出质设立登记日期
                        equity_pledged_status="",  # 状态
                        equity_pledged_pub_date="",  # 公示日期
                        detail="",  # 详情
                    ))
            self.logger.info("【股权出质登记信息解析】【完成】")
            # return stockInfo
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【股权出质登记信息解析】【出错】%s" %s)


    def parseKnowledgeinfo(self, page_source):
        '''
        获取知识产权出质登记
        :return:
        '''
        
        try:
            self.logger.info("【开始解析知识产权出质登记】")
            if page_source.xpath("//*[@id='copyright_baseinfo_info']/text()"):
                page_change = page_source.xpath("//*[@id='copyright_baseinfo_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = '0'
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    knowledge_list = page_source.xpath("//*[@id='copyright_baseinfo_wrapper']//tbody/tr")
                    if len(knowledge_list) > 0:
                        # self.logger.warn('【存在知识产权出质登记信息，公司名称为：%s】'%self.key_name)
                        for i in range(len(knowledge_list)):
                            i = i + 1
                            knowledge_code_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[2]/text()')
                            knowledge_code = knowledge_code_list[0].strip() if len(knowledge_code_list) > 0 else ''
                            knowledge_name_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[3]/text()')
                            knowledge_name = knowledge_name_list[0].strip() if len(knowledge_name_list) > 0 else ''
                            knowledge_type_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[4]/text()')
                            knowledge_type = knowledge_type_list[0].strip() if len(knowledge_type_list) > 0 else ''
                            knowledge_person_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[5]/text()')
                            knowledge_person = knowledge_person_list[0].strip() if len(knowledge_person_list) > 0 else ''
                            knowledge_personed_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[6]/text()')
                            knowledge_personed = knowledge_personed_list[0].strip() if len(
                                knowledge_personed_list) > 0 else ''
                            knowledge_date_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[7]/text()')
                            knowledge_date = knowledge_date_list[0].strip() if len(knowledge_date_list) > 0 else ''
                            knowledge_state_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[8]/text()')
                            knowledge_state = knowledge_state_list[0].strip() if len(knowledge_state_list) > 0 else ''
                            knowledge_show_date_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[9]/text()')
                            knowledge_show_date = knowledge_show_date_list[0].strip() if len(knowledge_show_date_list) > 0 else ''
                            knowledge_detail_list = page_source.xpath(
                                '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[10]/text()')
                            knowledge_detail = knowledge_detail_list[0].strip() if len(knowledge_detail_list) > 0 else ''
                            self.knowledgeInfo.append(hypc_enterprise_credit.knowledge_info(
                                    knowledge_code=knowledge_code,  # 登记编号
                                    knowledge_name=knowledge_name,  # 出质人
                                    knowledge_type=knowledge_type,  # 证照/证件号码
                                    knowledge_person=knowledge_person,  # 出质股权数额
                                    knowledge_personed=knowledge_personed,  # 质权人
                                    knowledge_date=knowledge_date,  # 股权出质设立登记日期
                                    knowledge_state=knowledge_state,  # 状态
                                    knowledge_show_date=knowledge_show_date,  # 公示日期
                                    detail_info=knowledge_detail,
                                ))

                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        knowledge_list = page_source.xpath("//*[@id='copyright_baseinfo_wrapper']//tbody/tr")
                        if len(knowledge_list) > 0:
                            # self.logger.warn('【存在知识产权出质登记信息，公司名称为：%s】'%self.key_name)
                            for i in range(len(knowledge_list)):
                                i = i + 1
                                knowledge_code_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[2]/text()')
                                knowledge_code = knowledge_code_list[0].strip() if len(knowledge_code_list) > 0 else ''
                                knowledge_name_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[3]/text()')
                                knowledge_name = knowledge_name_list[0].strip() if len(knowledge_name_list) > 0 else ''
                                knowledge_type_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[4]/text()')
                                knowledge_type = knowledge_type_list[0].strip() if len(knowledge_type_list) > 0 else ''
                                knowledge_person_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[5]/text()')
                                knowledge_person = knowledge_person_list[0].strip() if len(knowledge_person_list) > 0 else ''
                                knowledge_personed_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[6]/text()')
                                knowledge_personed = knowledge_personed_list[0].strip() if len(
                                    knowledge_personed_list) > 0 else ''
                                knowledge_date_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[7]/text()')
                                knowledge_date = knowledge_date_list[0].strip() if len(knowledge_date_list) > 0 else ''
                                knowledge_state_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[8]/text()')
                                knowledge_state = knowledge_state_list[0].strip() if len(knowledge_state_list) > 0 else ''
                                knowledge_show_date_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[9]/text()')
                                knowledge_show_date = knowledge_show_date_list[0].strip() if len(knowledge_show_date_list) > 0 else ''
                                knowledge_detail_list = page_source.xpath(
                                    '//*[@id="copyright_baseinfo_wrapper"]//tbody/tr[' + str(i) + ']/td[10]/text()')
                                knowledge_detail = knowledge_detail_list[0].strip() if len(knowledge_detail_list) > 0 else ''
                                self.knowledgeInfo.append(hypc_enterprise_credit.knowledge_info(
                                    knowledge_code=knowledge_code,  
                                    knowledge_name=knowledge_name, 
                                    knowledge_type=knowledge_type,  
                                    knowledge_person=knowledge_person,  
                                    knowledge_personed=knowledge_personed,  
                                    knowledge_date=knowledge_date,  
                                    knowledge_state=knowledge_state,  
                                    knowledge_show_date=knowledge_show_date,  
                                    detail_info=knowledge_detail,
                                ))
                        element = self.br.find_element_by_xpath1("//*[@id='copyright_baseinfo_info']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)

            else:
                self.logger.info("【暂无知识产权出质登记】")
                self.knowledgeInfo.append(hypc_enterprise_credit.knowledge_info(
                    knowledge_code="",  # 登记编号
                    knowledge_name="",  # 出质人
                    knowledge_type="",  # 证照/证件号码
                    knowledge_person="",  # 出质股权数额
                    knowledge_personed="",  # 质权人
                    knowledge_date="",  # 股权出质设立登记日期
                    knowledge_state="",  # 状态
                    knowledge_show_date="",  # 公示日期
                    detail_info="",
                ))
            self.logger.info("【知识产权出质登记完成】")
            # return knowledgeInfo
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【知识产权出质登记解析】【出错】%s" % s)

    def parseTrademarkinfo(self, page_source):
        '''
        商标注册信息解析
        :return:
        '''
        try:
            self.logger.info("【开始解析商标注册信息】")
            trademark_list = page_source.xpath('//*[@id="trademarkInfo"]/ul/li')
            if len(trademark_list) > 0:
                for i in range(len(trademark_list)):
                    i = i + 1
                    brand_number_list = page_source.xpath('//*[@id="trademarkInfo"]/ul/li[' + str(i) + ']/div/div/div[1]/span[2]/text()')
                    brand_number = brand_number_list[0].strip() if len(brand_number_list) > 0 else ''
                    
                    type_b_list = page_source.xpath(
                        '//*[@id="trademarkInfo"]/ul/li[' + str(i) + ']/div/div/div[2]/span[2]/text()')
                    type_b = type_b_list[0].strip() if len(type_b_list) > 0 else ''
                    
                    pub_date_list = page_source.xpath(
                        '//*[@id="trademarkInfo"]/ul/li[' + str(i) + ']/div/div/div[3]/span[2]/text()')
                    pub_date = pub_date_list[0].strip() if len(pub_date_list) > 0 else ''
                    self.trademarkInfo.append(hypc_enterprise_credit.brand_info(
                            brand_number = brand_number,
                            type = type_b,
                            pub_date = pub_date,
                        ))
                    
            else:
                self.logger.info("【暂无商标注册信息解析】")
                self.trademarkInfo.append(hypc_enterprise_credit.brand_info(
                    brand_number = "",
                    type = "",
                    pub_date = "",
                ))
            self.logger.info("【商标注册信息解析】【完成】")
            # return trademarkInfo
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【商标注册信息解析】【出错】%s" % s)

    def parseOrigninfo_detail(self, page_source):
        '''
        股东出资信息
        :param page_source:
        :return:
        '''
        try:
            self.logger.info("【公司股东出资人详情信息解析】【开始】")
            # 先获取页数进行判断
            if page_source.xpath("//*[@id='needPaging_stock_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_stock_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = 0
            
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                # 发起人及出资人信息列表
                    orign_list = page_source.xpath("//*[@id='needPaging_stock']/tbody/tr")
                    if len(orign_list) > 0:
                        # self.logger.warn('【存在发起人及出资人信息，公司名称为：%s】' % self.key_name)
                        for i in range(len(orign_list)):
                            i = i + 1
                            orign_name_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]/td[2]/text()")
                            orign_name = orign_name_list[0].strip() if len(orign_name_list) > 0 else ''  

                            subscribe_funding_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[4]//td/text()")
                            asubscribe_funding = subscribe_funding_list[0].strip() if len(subscribe_funding_list) > 0 else ''           
                            amount_investment_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[5]//td/text()")
                            amount_investment = amount_investment_list[0].strip() if len(amount_investment_list) > 0 else ''
                            subscribe_time_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[6]//td/text()")
                            subscribe_time = subscribe_time_list[0].strip() if len(subscribe_time_list) > 0 else ''

                            way_paid_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[8]//td/text()")
                            way_paid = way_paid_list[0].strip() if len(way_paid_list) > 0 else ''
                            amount_paid_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[9]//td/text()")
                            amount_paid = amount_paid_list[0].strip() if len(amount_paid_list) > 0 else ''
                            time_paid_list = page_source.xpath(
                                "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[10]//td/text()")
                            time_paid = time_paid_list[0].strip() if len(time_paid_list) > 0 else ''
                            self.OrigndetailInfo.append(hypc_enterprise_credit.annual_shareholder_info(
                                    shareholder = orign_name,
                                    contributive_way = asubscribe_funding,
                                    contributive_amount = amount_investment,
                                    contributive_date = subscribe_time,
                                    pay_way = way_paid,
                                    pay_amount = amount_paid,
                                    pay_date = time_paid,
                                ))
                           
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        orign_list = page_source.xpath("//*[@id='needPaging_stock']/tbody/tr")
                        if len(orign_list) > 0:
                            # self.logger.warn('【存在发起人及出资人信息，公司名称为：%s】' % self.key_name)
                            for i in range(len(orign_list)):
                                i = i + 1
                                orign_name_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]/td[1]/text()")
                                orign_name = orign_name_list[0].strip() if len(orign_name_list) > 0 else ''  

                                subscribe_funding_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[4]//td/text()")
                                asubscribe_funding = subscribe_funding_list[0].strip() if len(subscribe_funding_list) > 0 else ''           
                                amount_investment_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[5]//td/text()")
                                amount_investment = amount_investment_list[0].strip() if len(amount_investment_list) > 0 else ''
                                subscribe_time_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[6]//td/text()")
                                subscribe_time = subscribe_time_list[0].strip() if len(subscribe_time_list) > 0 else ''

                                way_paid_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[8]//td/text()")
                                way_paid = way_paid_list[0].strip() if len(way_paid_list) > 0 else ''
                                amount_paid_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[9]//td/text()")
                                amount_paid = amount_paid_list[0].strip() if len(amount_paid_list) > 0 else ''
                                time_paid_list = page_source.xpath(
                                    "//*[@id='needPaging_stock']/tbody/tr[" + str(i) + "]//td[10]//td/text()")
                                time_paid = time_paid_list[0].strip() if len(time_paid_list) > 0 else ''
                                
                                self.OrigndetailInfo.append(hypc_enterprise_credit.annual_shareholder_info(
                                    shareholder = orign_name,
                                    contributive_way = asubscribe_funding,
                                    contributive_amount = amount_investment,
                                    contributive_date = subscribe_time,
                                    pay_way = way_paid,
                                    pay_amount = amount_paid,
                                    pay_date = time_paid,
                                ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_stock_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)
            else:
                self.logger.info("【暂无公司股东出资人详情信息解析】")
                self.OrigndetailInfo.append(hypc_enterprise_credit.annual_shareholder_info(
                        shareholder = "",
                        contributive_way = "",
                        contributive_amount = "",
                        contributive_date = "",
                        pay_way = "",
                        pay_amount = "",
                        pay_date = "",
                    ))
            self.logger.info("【公司股东出资人详情信息解析】【完成】")
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【股东出资信息解析】【出错】%s" % s)

    def businessDirectory(self,page_source):
        '''列入经营异常名录信息'''
        try:
            self.logger.info('【开始解析列入经营异常名录信息】')
            
            if page_source.xpath("//*[@id='needPaging_abnormal_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_abnormal_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = 0
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    directory_list = page_source.xpath("//*[@id='needPaging_abnormal_wrapper']//tbody/tr")
                    if len(directory_list) > 0:
                        for i in range(len(directory_list)):
                            i = i + 1
                            included_reasons_list = page_source.xpath(
                                "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[2]/div/span/text()")
                            included_reasons = included_reasons_list[0].strip() if len(included_reasons_list) > 0 else ''
                            date_included_list = page_source.xpath(
                                "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                            date_included = date_included_list[0].strip() if len(date_included_list) > 0 else ''
                            decision_included_list = page_source.xpath(
                                "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                            decision_included = decision_included_list[0].strip() if len(decision_included_list) > 0 else ''
                            remove_cause_list = page_source.xpath(
                                "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[5]/div/span/text()")
                            remove_cause = remove_cause_list[0].strip() if len(remove_cause_list) > 0 else ''
                            remove_date_list = page_source.xpath(
                                "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[6]/div/span/text()")
                            remove_date = remove_date_list[0].strip() if len(remove_date_list) > 0 else ''
                            decision_remove_list = page_source.xpath(
                                "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[7]/div/span/text()")
                            decision_remove = decision_remove_list[0].strip() if len(decision_remove_list) > 0 else ''
                            self.directoryInfo.append(hypc_enterprise_credit.operate_abnormal_info(
                                run_anomaly_reason = included_reasons,
                                in_date = date_included,
                                actuator_in = decision_included,
                                out_reason = remove_cause,
                                out_date = remove_date,
                                actuator_out = decision_remove,
                                ))
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        directory_list = page_source.xpath("//*[@id='needPaging_abnormal_wrapper']//tbody/tr")
                        if len(directory_list) > 0:
                            for i in range(len(directory_list)):
                                # directory = {}
                                i = i + 1
                                included_reasons_list = page_source.xpath(
                                    "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[2]/div/span/text()")
                                included_reasons = included_reasons_list[0].strip() if len(included_reasons_list) > 0 else ''
                                date_included_list = page_source.xpath(
                                    "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                                date_included = date_included_list[0].strip() if len(date_included_list) > 0 else ''
                                decision_included_list = page_source.xpath(
                                    "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                                decision_included = decision_included_list[0].strip() if len(decision_included_list) > 0 else ''
                                remove_cause_list = page_source.xpath(
                                    "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[5]/div/span/text()")
                                remove_cause = remove_cause_list[0].strip() if len(remove_cause_list) > 0 else ''
                                remove_date_list = page_source.xpath(
                                    "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[6]/div/span/text()")
                                remove_date = remove_date_list[0].strip() if len(remove_date_list) > 0 else ''
                                decision_remove_list = page_source.xpath(
                                    "//*[@id='needPaging_abnormal_wrapper']//tbody/tr[" + str(i) + "]/td[7]/div/span/text()")
                                decision_remove = decision_remove_list[0].strip() if len(decision_remove_list) > 0 else ''
                                self.directoryInfo.append(hypc_enterprise_credit.operate_abnormal_info(
                                    run_anomaly_reason = included_reasons,
                                    in_date = date_included,
                                    actuator_in = decision_included,
                                    out_reason = remove_cause,
                                    out_date = remove_date,
                                    actuator_out = decision_remove,
                                    ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_abnormal_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)

            else:
                self.logger.info('【暂无列入异常名单信息解析】')
                self.directoryInfo.append(hypc_enterprise_credit.operate_abnormal_info(
                    run_anomaly_reason = "",
                    in_date = "",
                    actuator_in = "",
                    out_reason = "",
                    out_date = "",
                    actuator_out = "",
                    ))
            self.logger.info('【列入异常名单信息解析】【完成】')
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            raise Exception("【列入异常名单信息解析】【出错】%s" % s)

    def check_results(self, page_source):
        '''抽查'''
        try:
            self.logger.info('【抽查检查信息解析】【开始】')
            if page_source.xpath("//*[@id='needPaging_inspect_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_inspect_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = '0'
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    directory_list = page_source.xpath("//*[@id='needPaging_inspect_wrapper']//tbody/tr")
                    if len(directory_list) > 0:
                        for i in range(len(directory_list)):
                            i = i + 1
                            check_authority_list = page_source.xpath(
                                "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                            check_authority = check_authority_list[0].strip() if len(check_authority_list) > 0 else ''
                            check_type_list = page_source.xpath(
                                "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                            check_type = check_type_list[0].strip() if len(check_type_list) > 0 else ''
                            check_date_list = page_source.xpath(
                                "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                            check_date = check_date_list[0].strip() if len(check_date_list) > 0 else ''
                            check_result_list = page_source.xpath(
                                "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                            check_result = check_result_list[0].strip() if len(check_result_list) > 0 else ''
                            self.checkInfo.append(hypc_enterprise_credit.check_info(
                                    actuator_check = check_authority,
                                    check_type = check_type,
                                    check_date = check_date,
                                    check_result = check_result,
                                ))
                            
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        directory_list = page_source.xpath("//*[@id='needPaging_inspect_wrapper']//tbody/tr")
                        if len(directory_list) > 0:
                            for i in range(len(directory_list)):
                                i = i + 1
                                check_authority_list = page_source.xpath(
                                    "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                                check_authority = check_authority_list[0].strip() if len(check_authority_list) > 0 else ''
                                check_type_list = page_source.xpath(
                                    "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                                check_type = check_type_list[0].strip() if len(check_type_list) > 0 else ''
                                check_date_list = page_source.xpath(
                                    "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                                check_date = check_date_list[0].strip() if len(check_date_list) > 0 else ''
                                check_result_list = page_source.xpath(
                                    "//*[@id='needPaging_inspect_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                                check_result = check_result_list[0].strip() if len(check_result_list) > 0 else ''
                                self.checkInfo.append(hypc_enterprise_credit.check_info(
                                    actuator_check = check_authority,
                                    check_type = check_type,
                                    check_date = check_date,
                                    check_result = check_result,
                                ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_inspect_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)
            else:
                self.logger.info('【暂无抽查检查结果信息解析】')
                self.checkInfo.append(hypc_enterprise_credit.check_info(
                    actuator_check = "",
                    check_type = "",
                    check_date = "",
                    check_result = "",
                ))
            self.logger.info('【抽查检查结果信息解析】【完成】')
            # return checkInfo
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【抽查检查结果信息解析】【出错】%s" % s)

    def assistance_info(self,page_source):
        '''司法协助'''
        try:
            self.logger.info('【司法协助信息解析】【开始】')
            if page_source.xpath("//*[@id='needPaging_freeze_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_freeze_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = 0
            # 总共有多少页
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    directory_list = page_source.xpath("//*[@id='needPaging_freeze_wrapper']//tbody/tr")
                    if len(directory_list) > 0:
                        for i in range(len(directory_list)):
                            i = i + 1
                            executed_person_list = page_source.xpath(
                                "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                            executed_person = executed_person_list[0].strip() if len(executed_person_list) > 0 else ''
                            amount_equity_list = page_source.xpath(
                                "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                            amount_equity = amount_equity_list[0].strip() if len(amount_equity_list) > 0 else ''
                            executive_court_list = page_source.xpath(
                                "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                            executive_court = executive_court_list[0].strip() if len(executive_court_list) > 0 else ''
                            execution_number_list = page_source.xpath(
                                "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                            execution_number = execution_number_list[0].strip() if len(execution_number_list) > 0 else ''
                            type_statu_list = page_source.xpath(
                                "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[6]/text()")
                            type_statu = type_statu_list[0].strip() if len(type_statu_list) > 0 else ''
                            details_list = page_source.xpath(
                                "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[7]/text()")
                            details = details_list[0].strip() if len(details_list) > 0 else ''
                            self.assistanceInfo.append(hypc_enterprise_credit.judicial_assist_info(
                                    executed = executed_person,
                                    amount = amount_equity,
                                    court = executive_court,
                                    reference_number = execution_number,
                                    type = type_statu,
                                    detail = details,
                                ))
                            
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        directory_list = page_source.xpath("//*[@id='needPaging_freeze_wrapper']//tbody/tr")
                        if len(directory_list) > 0:
                            for i in range(len(directory_list)):
                                i = i + 1
                                executed_person_list = page_source.xpath(
                                    "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                                executed_person = executed_person_list[0].strip() if len(executed_person_list) > 0 else ''
                                amount_equity_list = page_source.xpath(
                                    "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                                amount_equity = amount_equity_list[0].strip() if len(amount_equity_list) > 0 else ''
                                executive_court_list = page_source.xpath(
                                    "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                                executive_court = executive_court_list[0].strip() if len(executive_court_list) > 0 else ''
                                execution_number_list = page_source.xpath(
                                    "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                                execution_number = execution_number_list[0].strip() if len(execution_number_list) > 0 else ''
                                type_statu_list = page_source.xpath(
                                    "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[6]/text()")
                                type_statu = type_statu_list[0].strip() if len(type_statu_list) > 0 else ''
                                details_list = page_source.xpath(
                                    "//*[@id='needPaging_freeze_wrapper']//tbody/tr[" + str(i) + "]/td[7]/text()")
                                details = details_list[0].strip() if len(details_list) > 0 else ''
                                self.assistanceInfo.append(hypc_enterprise_credit.judicial_assist_info(
                                    executed = executed_person,
                                    amount = amount_equity,
                                    court = executive_court,
                                    reference_number = execution_number,
                                    type = type_statu,
                                    detail = details,
                                ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_freeze_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)

            else:
                self.logger.info('【暂无司法协助信息解析】')
                self.assistanceInfo.append(hypc_enterprise_credit.judicial_assist_info(
                        executed = "",
                        amount = "",
                        court = "",
                        reference_number = "",
                        type = "",
                        detail = "",
                    ))
            self.logger.info('【司法协助信息解析】【完成】')
        except:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【司法协助信息解析】【出错】%s" % s)

    def admin_penalty(self,page_source):
        '''行政处罚信息'''
        try:
            self.logger.info('【行政处罚信息解析】【开始】')
            if page_source.xpath("//*[@id='needPaging_punish_info']/text()"):
                page_change = page_source.xpath("//*[@id='needPaging_punish_info']/text()")[0]
                # 总共有多少页
                page_change_count = str(re.findall("\d+", page_change)[1])
            else:
                page_change_count = 0
            if int(page_change_count) > 0:
                if int(page_change_count) == 1:
                    directory_list = page_source.xpath("//*[@id='needPaging_punish_wrapper']//table[@id='needPaging_punish']/tbody/tr")
                    if len(directory_list) > 0:
                        for i in range(len(directory_list)):
                            i = i + 1
                            decision_number_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                            decision_number = decision_number_list[0].strip() if len(decision_number_list) > 0 else ''
                            types_violations_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                            types_violations = types_violations_list[0].strip() if len(types_violations_list) > 0 else ''
                            administrative_content_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                            administrative_content = administrative_content_list[0].strip() if len(administrative_content_list) > 0 else ''
                            name_organ_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                            name_organ = name_organ_list[0].strip() if len(name_organ_list) > 0 else ''
                            penalty_date_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[6]/text()")
                            penalty_date = penalty_date_list[0].strip() if len(penalty_date_list) > 0 else ''
                            announcement_date_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[7]/text()")
                            announcement_date = announcement_date_list[0].strip() if len(announcement_date_list) > 0 else ''
                            remarks_list = page_source.xpath(
                                "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[8]/text()")
                            remarks = remarks_list[0].strip() if len(remarks_list) > 0 else ''
                            self.administrativeInfo.append(hypc_enterprise_credit.admin_penalty_info(
                                reference_number = decision_number,
                                illegal_type = types_violations,
                                content = administrative_content,
                                judgmenter_name = name_organ,
                                judgment_date = penalty_date,
                                publish_date = announcement_date,
                                detail = remarks,
                                ))
                elif int(page_change_count) > 1:
                    for j in range(int(page_change_count)):
                        directory_list = page_source.xpath("//*[@id='needPaging_punish_wrapper']//table[@id='needPaging_punish']/tbody/tr")
                        if len(directory_list) > 0:
                            for i in range(len(directory_list)):
                                # administrative = {}
                                i = i + 1
                                decision_number_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[2]/text()")
                                decision_number = decision_number_list[0].strip() if len(decision_number_list) > 0 else ''
                                types_violations_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[3]/text()")
                                types_violations = types_violations_list[0].strip() if len(types_violations_list) > 0 else ''
                                administrative_content_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[4]/text()")
                                administrative_content = administrative_content_list[0].strip() if len(administrative_content_list) > 0 else ''
                                name_organ_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[5]/text()")
                                name_organ = name_organ_list[0].strip() if len(name_organ_list) > 0 else ''
                                penalty_date_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[6]/text()")
                                penalty_date = penalty_date_list[0].strip() if len(penalty_date_list) > 0 else ''
                                announcement_date_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[7]/text()")
                                announcement_date = announcement_date_list[0].strip() if len(announcement_date_list) > 0 else ''
                                remarks_list = page_source.xpath(
                                    "//*[@id='needPaging_punish_wrapper']//tbody/tr[" + str(i) + "]/td[8]/text()")
                                remarks = remarks_list[0].strip() if len(remarks_list) > 0 else ''
                                self.administrativeInfo.append(hypc_enterprise_credit.admin_penalty_info(
                                    reference_number = decision_number,
                                    illegal_type = types_violations,
                                    content = administrative_content,
                                    judgmenter_name = name_organ,
                                    judgment_date = penalty_date,
                                    publish_date = announcement_date,
                                    detail = remarks,
                                    ))
                        element = self.br.find_element_by_xpath1("//*[@id='needPaging_insPunishment_wrapper']/div[3]//div[2]//li[last()-1]")
                        element.click()
                        time.sleep(1)
                        page_source = etree.HTML(self.br.page_source)
            else:
                self.logger.info('【暂无行政处罚信息解析】')
                self.administrativeInfo.append(hypc_enterprise_credit.admin_penalty_info(
                    reference_number = "",
                    illegal_type = "",
                    content = "",
                    judgmenter_name = "",
                    judgment_date = "",
                    publish_date = "",
                    detail = "",
                    ))
            self.logger.info('【行政处罚信息解析】【完成】')
            # return self.administrativeInfo
        except Exception as e:
            s = traceback.format_exc()
            # self.status = constants.CRAWL_FAIL
            # self.push.push_data(self.status, constants.CRAWL_FAIL_DESC)
            raise Exception("【行政处罚信息解析】【出错】%s" % s)
    def annual_click(self, br, i):
        try:
            element = br.find_element_by_xpath1(
                "//*[@id='annual_menu_table']/tbody/tr[" + str(i) + "]/td[4]/a")
            size = element.location_once_scrolled_into_view
            size_dic = eval(str(size))
            x_js = size_dic.get(u'x','')
            js = "var q=document.documentElement.scrollTop="+str(x_js)
            br.execute_script(js)
            element.click()
        except Exception as f:
            self.logger.error(f)
            self.logger.info('年报点击查看出错')

        br.switch_to_window(self.br.window_handles[1])
        try:
            ui.WebDriverWait(br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="tc f24"]')))
        except Exception as e:
            self.logger.error(e)
            try:
                br.get1(self.br.current_url)
            except Exception as f:
                self.logger.error(f)

    def annualReport(self, page_source, url):
        '''企业年度报告'''
        try:
            self.logger.info('【企业年报信息解析】【开始】')
            directory_list = page_source.xpath("//*[@id='annual_menu_table']/tbody/tr")

            if len(directory_list) > 0:
                for i in range(len(directory_list)):
                    i = i + 1
                    announcement_date = ''
                    annual_year = ''
                    general_assets = ''
                    total_liability = ''
                    total_equity = ''
                    gross_revenue = ''
                    main_business_income = ''
                    total_profit = ''
                    retained_profit = ''
                    pay_taxes = ''
                    Contact_info = ''
                    mailing_address = ''
                    zip_code = ''
                    phone = ''
                    email = ''
                    run_status = ''
                    employee_number = ''
                    online_store_exist = ''
                    online_store_type = ''
                    online_store_name = ''
                    website = ''
                    try:
                        announcement_date_list = page_source.xpath(
                            "//*[@id='annual_menu_table']/tbody/tr[" + str(i) + "]/td[3]/text()")
                        announcement_date = announcement_date_list[0].strip() if len(announcement_date_list) > 0 else ''
                        annual_year_list = page_source.xpath(
                            "//*[@id='annual_menu_table']/tbody/tr[" + str(i) + "]/td[2]/text()")
                        annual_year = annual_year_list[0].strip() if len(annual_year_list) > 0 else ''
                        self.annual_click(self.br,i)
                        content = etree.HTML(self.br.page_source)
                        if ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='uniscId']/text()")):# 统一信用代码
                            self.logger.info('信用代码: '+ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='uniscId']/text()")))
                        else:
                            if len(self.br.window_handles) > 1:
                                self.br.close()
                            self.br.switch_to_window(self.br.window_handles[0])
                            try:
                                self.br.get1(url)
                                ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="content1"]')))
                            except Exception as f:
                                self.logger.error(f)
                            try:
                                element = self.wait_for(By.XPATH, '//*[@id="addmore" and @style="display: block;"]')
                                element.click()
                                ui.WebDriverWait(self.br, 10, 0.5).until(EC.visibility_of_element_located((By.ID, "needPaging_insPunishment_info")))
                            except Exception as e:
                                self.logger.error(e)
                                self.logger.info('重新访问后,页面加载出现问题')
                                js = "var q=document.documentElement.scrollTop=10000" 
                                for j in range(2):
                                    self.br.execute_script(js)
                                    time.sleep(2)
                            self.annual_click(self.br, i)
                            content = etree.HTML(self.br.page_source)

                        self.logger.info('正在解析基本数据')
                        general_assets = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='assGroDisIs']/text()"))# 资产总额
                        total_liability = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='liaGroDisIs']/text()"))# 负债合计
                        total_equity = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='totEquDisIs']/text()"))# 所有者权益合计
                        gross_revenue = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='vendIncDisIs']/text()"))# 营业总收入
                        main_business_income = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='maiBusIncDisIs']/text()"))# 主营业务收入
                        total_profit = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='proGroDisIs']/text()"))# 利润总额
                        retained_profit = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='netIncDisIs']/text()"))# 净利润
                        pay_taxes = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_assert']/tbody/tr/td[@id='ratGroDisIs']/text()"))# 纳税总额
                        Contact_info = ''# 联系信息
                        mailing_address = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='addr']/text()"))# 企业通信地址
                        zip_code = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='postalCode']/text()")) # 邮政编码
                        phone = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='tel']/text()"))# 企业联系电话
                        email = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='email']/text()"))# 电子邮箱
                        run_status = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='busSt']/text()"))# 企业经营状态
                        employee_number = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='empNum']/text()"))# 从业人数
                        online_store_exist = ifNotEmptyGetIndex(content.xpath("//*[@class='overview']/dl/dd[@id='webIsOrNot']/text()"))# 是否有网站或网店
                        
                        if content.xpath("//*[@id='needPaging_onlineshop']/ul/li"):
                            online_store_type = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_onlineshop']/ul[1]/li[1]/a/span/span/text()"))# 类型 （网站/网店）
                            online_store_name = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_onlineshop']/ul[1]/li[1]/a/div[1]/text()"))# 名称 （网站/网店）
                            website = ifNotEmptyGetIndex(content.xpath("//*[@id='needPaging_onlineshop']/ul[1]/li[1]/a/div[2]/span/text()"))# 网址
                        else:
                            online_store_type = ''   # 类型 （网站/网店）
                            online_store_name = ''   # 名称 （网站/网店）
                            website = ''
                        
                    except Exception as e:
                        self.logger.error(e)

                    finally:
                        if len(self.br.window_handles) > 1:
                            self.br.close()
                        self.br.switch_to_window(self.br.window_handles[0])
                        self.annualInfo.append(hypc_enterprise_credit.annual_info(
                                pub_date=announcement_date,
                                annual_year=annual_year,
                                general_assets=general_assets,
                                total_liability=total_liability,
                                total_equity=total_equity,
                                gross_revenue=gross_revenue,
                                main_business_income=main_business_income,
                                total_profit=total_profit,
                                retained_profit=retained_profit,
                                pay_taxes=pay_taxes,
                                Contact_info=Contact_info,
                                mailing_address=mailing_address,
                                zip_code=zip_code,
                                phone=phone,
                                email=email,
                                run_status=run_status,
                                employee_number=employee_number,
                                online_store_exist=online_store_exist,
                                online_store_type=online_store_type,  # 类型 （网站/网店）
                                online_store_name=online_store_name,  # 名称 （网站/网店）
                                website=website,  # 网址
                            ))
                    
            else:
                self.logger.info('【暂无企业年报信息解析】')
                self.annualInfo.append(hypc_enterprise_credit.annual_info(
                        pub_date="",
                        general_assets="",
                        total_liability="",
                        total_equity="",
                        gross_revenue="",
                        main_business_income="",
                        total_profit="",
                        retained_profit="",
                        pay_taxes="",
                        Contact_info="",
                        mailing_address="",
                        zip_code="",
                        phone="",
                        email="",
                        run_status="",
                        employee_number="",
                        online_store_exist="",
                        online_store_type="",  # 类型 （网站/网店）
                        online_store_name="",  # 名称 （网站/网店）
                        website="",
                    ))
            self.logger.info('【企业年报信息解析】【完成】')
        except:
            s = traceback.format_exc()
            # self.status = CRAWL_FAIL
            self.status = CRAWL_TIMEOUT
            raise Exception("【企业年度报告信息解析】【出错】%s" % s)

    def data(self):
        content = etree.HTML(self.br.page_source)
        page = ifNotEmptyGetIndex(content.xpath("//*[@class='search_result_span1']/text()"))
        page = page[0] if page else '0'
        try:
            if page != '0':  
                self.logger.info('共查询到%s条数据'%page) 
                com_list = []
                page_num = content.xpath("//*[@id='pageForm']/span")
                if len(page_num) > 3:   # 只有一页数据的情况
                    company_url_list = content.xpath("//*[@class='search_list_item db']/@href")
                    for i in company_url_list:
                        com_list.append(i)
                else:   # 多页的情况
                    numble = ifNotEmptyGetIndex(content.xpath("//*[@id='pageForm']/a[last()-2]/text()")) if content.xpath("//*[@id='pageForm']/a[last()-2]/text()") else '1'
                    for j in range(int(numble)):
                        company_url_list = content.xpath("//*[@class='search_list_item db']/@href")
                        for i in company_url_list:
                            com_list.append(i)
                        element = self.br.find_element_by_xpath1("//*[@id='pageForm']/a[last()-1]")
                        element.click()
                        time.sleep(1)
                        content = etree.HTML(self.br.page_source)

                for company_url in com_list:
                    detail_url = 'http://www.gsxt.gov.cn'+str(company_url)
                    try:                        
                        self.br.implicitly_wait(10)
                        self.br.get1(detail_url)
                    except Exception as e:
                        self.logger.error(e)
                        try:
                            # 防止再次刷新的时候出现卡死,所以没用热刷新的方式
                            self.br.get1(self.br.current_url)
                        except Exception as f:
                            self.logger.error(f)
                    element = self.wait_for(By.ID, "tab_primary3")
                    element.click()
                    try:
                        ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="needPaging_punish_info"]')))
                    except Exception as e:
                        self.logger.error(e)
                    self.admin_penalty(etree.HTML(self.br.page_source))
                    element = self.wait_for(By.ID, "tab_primary4")
                    element.click()
                    try:
                        ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="needPaging_abnormal_info"]')))
                    except Exception as e:
                        self.logger.error(e)
                    self.businessDirectory(etree.HTML(self.br.page_source))
                    element = self.wait_for(By.ID, "tab_primary1")
                    element.click()
                    try:
                        ui.WebDriverWait(self.br, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="content1"]')))
                    except Exception as e:
                        self.logger.error(e)
                    try:
                        element = self.wait_for(By.XPATH, '//*[@id="addmore" and @style="display: block;"]')
                        element.click()
                        ui.WebDriverWait(self.br, 10, 0.5).until(EC.visibility_of_element_located((By.ID, "needPaging_insPunishment_info")))
                    except Exception as e:
                        self.logger.error(e)
                        self.logger.info('页面加载出现问题')
                        js = "var q=document.documentElement.scrollTop=10000" 
                        for i in range(2):
                            self.br.execute_script(js)
                            time.sleep(2)
                    self.parseBaseinfo(str(self.br.page_source))
                    details_info = etree.HTML(self.br.page_source)
                    self.parseOrigninfo(details_info)
                    self.parsePerson(details_info)
                    self.parseBranchDeptinfo(details_info)
                    self.parseChangeinfo(details_info)
                    self.parseChattelinfo(details_info)
                    self.parseStockinfo(details_info)
                    self.parseKnowledgeinfo(details_info)
                    self.parseTrademarkinfo(details_info)
                    self.parseOrigninfo_detail(details_info)
                    self.check_results(details_info)
                    self.assistance_info(details_info)
                    self.annualReport(etree.HTML(self.br.page_source),detail_url)
                    self.info.append(hypc_enterprise_credit.enterprise_info(
                            base_info = self.baseInfo,
                            Shareholder_info = self.orignInfo,
                            key_person_info = self.mainPersonInfo,
                            branch_info = self.branchDeptInfo,
                            change_info = self.changeInfo,
                            chattel_info = self.chattelInfo,
                            equity_pledged_info = self.stockInfo,
                            knowledge_info = self.knowledgeInfo,
                            brand_info = self.trademarkInfo,
                            annual_shareholder_info = self.OrigndetailInfo,
                            operate_abnormal_info = self.directoryInfo,
                            check_info = self.checkInfo,
                            judicial_assist_info = self.assistanceInfo,
                            admin_penalty_info = self.administrativeInfo,
                            annual_info = self.annualInfo,
                        ))
                    self.baseInfo = {}
                    self.orignInfo = []
                    self.mainPersonInfo = []
                    self.branchDeptInfo=[]
                    self.changeInfo = []
                    self.chattelInfo = []
                    self.stockInfo = []
                    self.knowledgeInfo = []
                    self.trademarkInfo = []
                    self.directoryInfo = []
                    self.checkInfo = []
                    self.assistanceInfo = []
                    self.administrativeInfo = []
                    self.OrigndetailInfo = []
                    self.annualInfo = []
            else:
                # 没有要查的公司数据
                self.logger.info(u'暂无您查询的企业数据')
                self.info.append(hypc_enterprise_credit.enterprise_info(
                                base_info = {},
                                admin_penalty_info = [],
                                operate_abnormal_info=[],
                                key_person_info=[],
                                change_info=[],
                                check_info=[],
                                chattel_info=[],
                                branch_info=[],
                                equity_pledged_info=[],
                                Shareholder_info=[],
                                judicial_assist_info=[],
                                knowledge_info=[],
                                brand_info=[],
                                annual_shareholder_info=[],
                                annual_info=[],
                            ))
        except Exception as e:
            self.status = CRAWL_TIMEOUT
            self.logger.info("【查询信息解析】【出错】%s" % e)
        finally:
            self.logger.info('正在返回数据')
            if self.baseInfo or self.orignInfo or self.mainPersonInfo or self.branchDeptInfo or self.changeInfo or self.chattelInfo or self.stockInfo or self.knowledgeInfo or self.trademarkInfo or self.OrigndetailInfo or self.directoryInfo or self.checkInfo or self.assistanceInfo or self.administrativeInfo or self.annualInfo:
                self.info.append(hypc_enterprise_credit.enterprise_info(
                                base_info = self.baseInfo,
                                Shareholder_info = self.orignInfo,
                                key_person_info = self.mainPersonInfo,
                                branch_info = self.branchDeptInfo,
                                change_info = self.changeInfo,
                                chattel_info = self.chattelInfo,
                                equity_pledged_info = self.stockInfo,
                                knowledge_info = self.knowledgeInfo,
                                brand_info = self.trademarkInfo,
                                annual_shareholder_info = self.OrigndetailInfo,
                                operate_abnormal_info = self.directoryInfo,
                                check_info = self.checkInfo,
                                judicial_assist_info = self.assistanceInfo,
                                admin_penalty_info = self.administrativeInfo,
                                annual_info = self.annualInfo,
                            ))
            return self.info