#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
程序：HuoYanSpider
版本：1.0
作者：LiuJingYuan
日期：2017/9/6 15:35
语言：Python 2.7.13
操作：python start.py
''' 


# http://192.168.30.135:8080/9f_insight/af_dezhou/crawlData?username=0eaa7616b7da8dc41b8595a0d8b68061&userid=testuserid_12345&password=9c8d3aa81700a27cbc95f6ee92355e7c&idcard=f3338b3eb64d004b2cb807d56148a138a48a4c24b7a8b5d3c8f8b406f6d8c2c0&nocache=1
# http://192.168.30.135:8080/9f_insight/af_shaoyang/crawlData?username=bac043009be167bb088d7b658106ac95&idcard=6a0c4860f5b0b8bdde30b28984aab18dae01b5b4d4db7f20a8f6b9b55a37a398&userid=testuserid_12345&nocache=1
# http://192.168.30.135:8080/9f_insight/af_shijiazhuang/crawlData?userid=testuserid_12345&password=2db53967bd8323d823b9a78b2bed5c77&idcard=0c573a199033f6c76ef728a15e9622f67ad5e770bc71efc86595c19e6d552401&nocache=1
# http://192.168.30.135:8080/9f_insight/af_xianyang/crawlData?username=c648ad9312ef8d230c89ddd5c24435f8&idcard=eb8790e4d7346184947cc1b151c08a25e69a3ad92e7ebaf5f1a64fa75d48f96f&userid=testuserid_12345&nocache=1
# http://192.168.30.135:8080/9f_insight/af_zibo/crawlData?account=8441de8d5e61cf986a75b563097ce731&idcard=e3a47f39ac05a032d0368e313d101764cacff63dac846d88a2491b5b76f831e3&userid=testuserid_12345
from af_dezhou.constants_spider import SOURCE
from af_shaoyang.constants_spider import SOURCE
from af_shijiazhuang.constants_spider import SOURCE
from af_xianyang.constants_spider import SOURCE
# from af_zibo.constants_spider import SOURCE

# # http://192.168.30.135:8080/9f_insight/ccb/crawlData?username=9a46be7e7b929b230f7cf0c0d488e0f4&password=18b755b15166e3ab5cddcff6088c46a7&userid=testuserid_12345&nocache=1
# # 查询关键词：黄海波 http://192.168.30.135:8080/9f_insight/court_announcement/crawlData?key=f39b9af6f5b80a56936e154cb58bbec1&userid=testuserid_12345&nocache=1
# # 查询企业名：河南省漯河市双汇实业集团有限责任公司 http://192.168.30.135:8080/9f_insight/iso9000/crawlData?userid=testuserid_12345&companyName=308fbcae63b731edf5f1814d5daa533296d5636b8b35cf7926eeeacf51a85e409a0d29c51822e6c4772dc2335befca6466ca41d54caf38ef3d906bba988a6122&nocache=1
# # 火眼征信 http://192.168.30.135:8080/9f_insight/position/crawlData?userid=testuserid_12345&nocache=1&companyName=4f4789d6db6477633f5b90c0dca77ff8
# # 灰盒子（上海）咖啡有限公司 http://192.168.30.135:8080/9f_insight/position/crawlData?userid=testuserid_12345&nocache=1&companyName=9dbfa9283e248cf684e9aca289597f1a073ea113176ddcb2da8197097c8c87e000d99590258088643bf8231ffb35469f
# # 查询敏感词为谢永菊 http://192.168.30.135:8080/9f_insight/seach58_ningbo/crawlData?userid=testuserid_12345&key=5b478ea98073ed40d6aaf36c09f6d583&nocache=1
# key=姚相宇 http://192.168.30.135:8080/9f_insight/wenshu/crawlData?userid=testuserid_12345&key=5fac959386f8ee5621dcfea983396c25&nocache=1
# from ccb.constants_spider import SOURCE
# from abchina.constants_spider import SOURCE
from court_announcement.constants_spider import SOURCE
# from iso9000.constants_spider import SOURCE
# from position.constants_spider import SOURCE
# from seach58_ningbo.constants_spider import SOURCE
from wenshu.constants_spider import SOURCE

# # http://192.168.30.135:8080/9f_insight/ss_anyang/crawlData?username=59c668735cb89486747466ffd29c50628535ad4e08b264800a72b8dfef322871&password=dc0c2dd629cdb049e8cc222ed7cc6814&userid=testuserid_12345&nocache=1
# # http://192.168.30.135:8080/9f_insight/ss_chongqing/crawlData?userid=testuserid_12345&password=ea506988ee3ed8986fb2093346615abc&idcard=ba5c3caed159f89348d7c7114ed5f2f6085e4d50a082efa71593fd2f35c5ad03&nocache=1
# # http://192.168.30.135:8080/9f_insight/ss_ningbo/crawlData?username=6f7f0cfcde8a4393580eda3c3dc7b93ee5717816b109fa782feb5d6697c173e8&password=423fe0df8095cf1afd558d370feddf30&userid=testuserid_12345&nocache=1
# # http://192.168.30.135:8080/9f_insight/ss_zhuzhou/crawlData?username=8de71b4dd295c4673ef27a5bfc53e89c&userid=testuserid_12345&password=2548c26e36c4680a564eca2262c0ef9d&idcard=5895d115f18307b3eba2609bf6166c76ee9263447bdc60b834d36392ad9fd361&nocache=1
from ss_anyang.constants_spider import SOURCE
# from ss_chongqing.constants_spider import SOURCE
# from ss_ningbo.constants_spider import SOURCE
# from ss_zhuzhou.constants_spider import SOURCE
# from ss_beijing.constants_spider import SOURCE
# from ss_dalian.constants_spider import SOURCE

# # 测试地址 http://192.168.30.135:8080/9f_insight/telecom/crawlData?phoneNum=9a46be7e7b929b230f7cf0c0d488e0f4&password=666309b93e7c8cc0937b913437bfed74&userid=testuserid_12345&nocache=1
# # 发送验证码 http://192.168.30.135:8080/9f_insight/telecom/crawlData?smscode=134910&token=6ef93b24-c1ca-4d63-9da9-be4c13a852b7
# # 雷雨：http://192.168.30.135:8080/9f_insight/unicom/crawlData?userid=testuserid_12345&password=4ac839efaa845b8df53eb7544dd2c234&phoneNum=8ca02cd076ec5a2ef7c9a0a53a225b85&nocache=1
# from telecom.constants_spider import SOURCE
# from unicom.constants_spider import SOURCE



print SOURCE
execfile(SOURCE+"/spider_main.py")











# 安阳社保
# 宁波58同城敏感词查询
# 咸阳公积金
# 北京城镇职工社保信息
# 宁波社保
# 运营商
# 农业银行账户
# 质量管理体系认证（ISO9000）
# 大连社保
# 企业招聘信息文档接口         
# 中国裁判文书网
# 德州公积金
# 人民法院公告网
# 重庆社保
# 电信掌厅app接口文档        
# 邵阳公积金
# 株洲社保
# 建设银行账户
# 石家庄公积金
# 淄博公积金爬虫
# 联通运营商



"""

# 改版：
	# 大连社保需要手机号，个人编号，密码；测试账号缺少手机号
	# 北京社保需要身份证号，密码，短信验证码；测试账号无法提供短信验证码

"""












