# #!/usr/bin/env python
# # -*- coding: UTF-8 -*-
# #-------------------------------------------------------------------------
# # 程序：#HuoYan
# # 版本：1.0
# # 作者：LiuJingYuan
# # 日期：2017/8/11 2:20
# # 语言：Python 2.7.13
# # 功能：
# #
# #-------------------------------------------------------------------------
# # redis常量定义
# import random

SOURCE = "unicom"
'''推送常量定义'''
TYPEVALUE = 'craw_operator_phone_number_info'


# 与服务端的交互状态常量定义
# 爬虫异常的情况：
# 对于由爬虫自身问题导致，而且服务不能改善已出现的异常(例如：样本不足)爬虫不会告知服务异常原因，只返回状态码２，desc'爬虫爬取失败';
# 对于由服务端输入参数引起的问题（例如：用户名密码错误，验证码错误），状态码返回4，desc视具体情况而定
# 对于需要交互的情况（例如：需要验证码），状态码10，desc视具体情况而定
# 对于由用户账户导致的问题，或者需要告知用户错误原因的情况（例如：密码过于简单，只用修改密码后网站才允许登陆）desc为5，desc视具体情况而定

# 爬虫爬取成功
CRAWL_SUCCESS = '1'
# CRAWL_SUCCESS_DESC = '爬虫爬取成功'

# 爬虫爬取失败
CRAWL_FAIL = '2'
# CRAWL_FAIL_DESC = '爬虫爬取失败'

# 爬虫抓取超时
CRAWL_TIMEOUT = '3'
# CRAWL_TIMEOUT_DESC = '爬虫抓取超时'

INPUT_ERROR = '4'
OTHER_INFO = '5'
NEED_MORE = '10'


#爬虫类常量
# 请求重试次数
REQUEST_RETRY = 3
# 请求超时设置
TIMEOUT = 30
# 交互情况下，用户输入最大时长(秒)
WAITTIME = 5*60

#调度类常量
# 默认线程数
THREAD_NUM = 10
# 默认线程队列深度
THREAD_Q_SIZE = 1






# CRAWL_READY = '0'
# CRAWL_READY_DESC = '准备爬取'
# NEED_BCODE = '102'
# NEED_BCODE_DESC = '需要图片验证码'
# NOT_NEED_BCODE = '101'
# NOT_NEED_BCODE_DESC = '不需要图片验证码'
# PROGRAM_ERROR = '119'
# PROGRAM_ERROR_DESC = '爬虫程序异常'
# # 此处的用户名含义广泛，针对不同的网站，用户名可以不同的含义，可以为真实姓名、社保号、公积金账号等登录账号
# IDCARD_ERROR = '201'
# IDCARD_ERROR_DESC = '身份证号错误'
# PASSWORD_ERROR = '202'
# PASSWORD_ERROR_DESC = '密码错误'
# LONGINTYPE_ERROR = '206'
# LONGINTYPE_ERROR_DESC = '登陆方式标识错误'
# BCODE_ERROR = '205'
# BCODE_ERROR_DESC = '图片验证码错误'
# TOKEN_IS_NULL = '203'
# TOKEN_IS_NULL_DESC = 'token为空'
# IDCARD_IS_NULL = '207'
# IDCARD_IS_NULL_DESC = '账号为空'
# PASSWORD_IS_NULL = '208'
# PASSWORD_IS_NULL_DESC = '密码为空'
# BCODE_IS_NULL = '204'
# BCODE_IS_NULL_DESC = '图片验证码为空'
# CRAWL_TIMEOUT = '209'
# CRAWL_TIMEOUT_DESC = '爬虫抓取超时'
# EXEMPLE_IS_NOT_FULL = '302'
# EXEMPLE_IS_NOT_FULL_DESC = '样本不足'
# REDIS_CONNECTION_FAIL = '304'
# REDIS_CONNECTION_FAIL_DESC = '连接redis操作出现异常'






# # 头部
# USER_AGENTS = [
#     "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
#     "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
#     "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
#     "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
#     "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
#     "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
#     "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
#     "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
#     "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
#     "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
#     "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
#     "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
#     "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
#     "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
#     "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
#     "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
#     "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
#     "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
#     "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
# ]
# RUSER_AGENTS = random.choice(USER_AGENTS)


# LOGINHEADERS = {
#     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'Accept': 'application/json, text/javascript, */*; q=0.01',
#     'X-Requested-With': 'XMLHttpRequest',
#     'Referer': 'http://www.cczfgjj.gov.cn/grlogin.jhtml',
#     'Accept-Language': 'zh-CN',
#     'Accept-Encoding': 'gzip, deflate',
#     'User-Agent': RUSER_AGENTS,
#     'Host': 'www.cczfgjj.gov.cn',
#     'Connection': 'Keep-Alive',
#     'Pragma': 'no-cache',
# }

# PERHEADERS = {
#     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'Accept': 'application/json, text/javascript, */*; q=0.01',
#     'X-Requested-With': 'XMLHttpRequest',
#     'Referer': 'http://www.cczfgjj.gov.cn/grquery.jhtml',
#     'Accept-Language': 'zh-CN',
#     'Accept-Encoding': 'gzip, deflate',
#     'User-Agent': RUSER_AGENTS,
#     'Host': 'www.cczfgjj.gov.cn',
#     'Connection': 'Keep-Alive',
#     'Pragma': 'no-cache',
# }

# IMGHEADERS ={
# "Accept": "image/png, image/svg+xml, image/jxr, image/*;q=0.8, */*;q=0.5",
# "Referer": "http://www.cczfgjj.gov.cn/grlogin.jhtml",
# "Accept-Language": "zh-CN",
# "User-Agent": RUSER_AGENTS,
# "Accept-Encoding": "gzip, deflate",
# "Host": "www.cczfgjj.gov.cn",
# "Connection": "Keep-Alive",
# }

