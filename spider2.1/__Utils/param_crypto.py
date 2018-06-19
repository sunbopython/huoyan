# -*- coding: UTF-8 -*-
'''
程序：spider
版本：1.0
作者：LiuJingYuan
日期：2017/8/30 16:46
语言：Python 2.7.13
操作：python jmjm.py

包 pycrypto
'''
import json
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

"""
    加密解密类
"""
class Prpcrypt():
    """
        key: 密钥 (必须为16位的字符串)
    """
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        # cryptor = AES.new(self.key, self.mode, self.key)
        # plain_text = cryptor.decrypt(a2b_hex(text))  # 被加密的字符串为''时，加密后为'0'；对'0'进行解密时会出现‘奇数的字符串’异常
        # return '' if text == '0' else plain_text.rstrip('\0')
        if text == '0':
            return ''
        else:
            cryptor = AES.new(self.key, self.mode, self.key)
            plain_text = cryptor.decrypt(a2b_hex(text))
            return plain_text.rstrip('\0')


"""
    url参数加密、参数字典解密 类
    用固定参数userid作为密钥
"""
class ParamCrypto(object):
    # 解析url参数为json
    def getKwargs(self, url):
        parameter_list = url[url.index('?')+1:].split('&')
        dict_json = {}
        for parameter in parameter_list:
            [key, value] = parameter.split('=')
            dict_json[key] = value
        return dict_json

    # 对userid进行补位或截取（密钥固定为16位字符串）
    def useridHandler(self, userid=''):
        return userid[:16] if len(userid) >= 16 else userid + 'x' * (16 - len(userid))

    # 对参数字典进行加密或解密 默认为解密
    def kwargsHandler(self, dict_json, crypt='de'):
        secret_key = self.useridHandler(dict_json['userid'])  # 获取密钥
        pc = Prpcrypt(secret_key)  # 初始化密钥
        new_dict_json = {}
        for key, value in dict_json.items():
            if key != 'userid' and key != 'token' and key != 'bcode' and key != 'smscode' and key != 'result' and key != 'desc' and key != 'nocache':
                new_dict_json[key] = pc.decrypt(value) if crypt == 'de' else pc.encrypt(value) # 解密或加密
            else:
                new_dict_json[key] = value
        return new_dict_json


"""url加密方法"""
# 将参数为明文的原始url 加密为参数为密文的新url userid等特定参数不变
def getNewUrl(url):
    p = ParamCrypto()
    dict_json = p.getKwargs(url) # 解析url参数
    new_dict_json = p.kwargsHandler(dict_json, crypt='en') # 对参数字典的值进行加密
    # 获取新的query
    new_query = ''
    for key, value in new_dict_json.items():
        new_query += key + '=' + value + '&'
    return url.split('?')[0] + '?' + new_query[:-1] # 拼接新url 并返回


"""参数字典解密方法"""
# 将加密的dict_json进行解密
def decryptKwargs(dict_json):
    if dict_json == None:
        return
    dict_json = eval(json.dumps(dict_json, ensure_ascii=False))
    return ParamCrypto().kwargsHandler(dict_json)


def test_url(SOURCE, PARAM):
    add = 'localhost:8080'
    for i in PARAM:
        param_str = ''
        for k,v in i.items():
            param_str += '&%s=%s' % (k, v)
        param_str += '&nocache=1'
        # url = 'http://%s/9f_insight/%s/crawlData?userid=yinzhouyinhang%s'%(add, SOURCE, param_str)
        # print url
        url = 'spider.insightcredit.cn/%s/crawlData?userid=yinzhouyinhang%s'%(SOURCE, param_str)
        print ''
        print getNewUrl(url)
"""
    密钥 必须为16位
    userid token bcode smscode result 为固定参数名，不可变
"""

if __name__ == '__main__':

    # pc = Prpcrypt('testuserid_12345')  # 初始化密钥
    # e = pc.encrypt("我的天啊")  # 加密
    # d = pc.decrypt(e)  # 解密
    # print e, d
    from testUrlParam import af_dezhou
    from testUrlParam import af_shaoyang
    from testUrlParam import af_shijiazhuang
    from testUrlParam import af_xianyang
    from testUrlParam import af_zibo

    from testUrlParam import ss_anyang
    from testUrlParam import ss_beijing
    from testUrlParam import ss_chongqing
    from testUrlParam import ss_dalian
    from testUrlParam import ss_ningbo
    from testUrlParam import ss_zhuzhou

    from testUrlParam import telecom
    from testUrlParam import unicom

    from testUrlParam import ccb
    from testUrlParam import court_announcement
    from testUrlParam import iso9000
    from testUrlParam import position
    from testUrlParam import seach58_ningbo
    from testUrlParam import wenshu

    from testUrlParam import gsxt

    # 公积金
    # test_url('af_dezhou', af_dezhou)
    # test_url('af_shaoyang', af_shaoyang)
    # test_url('af_shijiazhuang', af_shijiazhuang)
    # test_url('af_xianyang', af_xianyang)
    # test_url('af_zibo', af_zibo)     # 改版

    # # 社保
    # test_url('ss_anyang', ss_anyang)
    # test_url('ss_beijing', ss_beijing) # 无法获取短信验证码
    # test_url('ss_chongqing', ss_chongqing)
    # test_url('ss_dalian', ss_dalian)
    # test_url('ss_ningbo', ss_ningbo)
    # test_url('ss_zhuzhou', ss_zhuzhou)

    # # 运营商
    # test_url('telecom', telecom) # 无法获取短信验证码
    # test_url('unicom', unicom)

    test_url('ccb', ccb)
    # test_url('court_announcement', court_announcement)
    # test_url('iso9000', iso9000)
    # test_url('position', position)
    # test_url('seach58_ningbo', seach58_ningbo)
    # test_url('wenshu', wenshu)

    # test_url('gsxt', gsxt)



    # http://localhost:8080/9f_insight/telecom/crawlData?smscode=134910&token=6ef93b24-c1ca-4d63-9da9-be4c13a852b7











    # SOURCE = 'ff_zibo'
    # PARAM = '&idcard=37030219950420292X&account=402164351&nocache=1'

    # SOURCE = 'seach58_ningbo'
    # PARAM = '&key=谢永菊&nocache=1'

    # SOURCE = 'court_announcement'
    # PARAM = '&username=黄海波&nocache=1'

    # SOURCE = 'ccb'
    # PARAM = '&username=18101205290&password=147258&nocache=1'
    # PARAM = '&username=18101205290&password=147259&nocache=1'

    # SOURCE = 'iso9000'
    # PARAM = '&companyName=河南省漯河市双汇实业集团有限责任公司&nocache=1'
    # # PARAM = '&companyName=茅台集团&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'ss_anyang'
    # PARAM = '&username=13460979027&password=w13460979027&nocache=1'
    # # # 密码错误
    # # # PARAM = '&username=huangshanshan&password=hss3333&nocache=1'
    # # # 认证失败
    # # # PARAM = '&username=huangshanshan&password=hss333&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)


    # SOURCE = 'unicom'
    # PARAM = '&phoneNum=15632661226&password=080552&nocache=1'
    # # PARAM = '&phoneNum=13161933309&password=131619&nocache=1'
    # # PARAM = '&phoneNum=13051934066&password=130519&nocache=1'
    # # # PARAM = '&phoneNum=15632661226&password=080551&nocache=1'    # 密码错误
    # # # PARAM = '&phoneNum=13161933309&password=131612&nocache=1'    # 密码错误
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)



    # SOURCE = 'af_dezhou'
    # PARAM = '&username=王衍收&password=000000&idcard=371424198812130913&nocache=1'
    # # PARAM = '&username=李亚迪&idcard=371482199707222013&password=000000&nocache=1'
    # # PARAM = '&username=巩清华&idcard=371482198904172962&password=000000&nocache=1'
    # # PARAM = '&username=曲双双&idcard=371482199106031123&password=000000&nocache=1'
    # # PARAM = '&username=公晓燕&idcard=370181199011185222&password=000000&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'telecom'
    # PARAM = '&phoneNum=18001167287&password=121212&nocache=1'
    # # # PARAM = '&phoneNum=18101205290&password=1212&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'ss_ningbo'
    # PARAM = '&username=330781199408014312&password=142536&nocache=1'
    # # PARAM = '&username=331022199001022225&password=102650926&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'af_shijiazhuang'
    # PARAM = '&idcard=140211199401194419&password=445566&nocache=1'
    # # PARAM = '&idcard=15222419970105603X&password=950814&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'af_shaoyang'
    # PARAM = '&idcard=430524198706010345&username=曾云&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)


    # SOURCE = 'af_xianyang'
    # PARAM = '&idcard=610423198904235838&username=张磊&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)


    # SOURCE = 'ss_chongqing'
    # PARAM = '&idcard=500234199205273170&password=84328X&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'ss_zhuzhou'
    # PARAM = '&username=胡金&idcard=431021198601226638&password=226638&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'ss_beijing'
    # PARAM = '&idcard=330823197912266319&password=kprcldq0&nocache=1'
    # # PARAM = '&idcard=412726199612102456&password=abcd123456&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'abchina'
    # PARAM = '&username=412726199612102456&password=abCD123456-&nocache=1'
    # # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=yinzhouyinhang%s' % (SOURCE, PARAM)

    # SOURCE = 'ss_dalian'
    # PARAM = '&phoneNum=18640981716&username=27322761&password=521299&nocache=1'
    # PARAM = '&phoneNum=18640981716&username=27322761&password=521239&nocache=1'
    # url = 'http://192.168.30.135:8080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)

    # SOURCE = 'wenshu'
    # PARAM = '&key=嘿嘿&nocache=1'
    # PARAM = '&key=孙博&nocache=1'
    # url = 'http://localhost:8080/9f_insight/fang_ningbo/crawlData?userid=yinzhouyinhang&keyword=时代新居&flower=6层以下&age=2-5年&nocache=1'080/9f_insight/%s/crawlData?userid=testuserid_12345%s'%(SOURCE, PARAM)
    # 陆莲娣 浙江
    # 被执行人
    # url = 'http://localhost:8080/9f_insight/executored/crawlData?name=烟台芝兴房地产开发有限公司&cardNum=79732178-3&userid=yinzhouyinhang&nocache=1'
    # url = 'http://localhost:8080/9f_insight/executored/crawlData?name=山东第二前进机械厂&cardNum=168270813&userid=yinzhouyinhang&nocache=1'
    url = 'http://localhost:8080/9f_insight/spider_translate/crawlData?title=大兴安岭&project_district=All&project=&date_filter_min=&date_filter_max=&userid=yinzhouyinhang&nocache=1'
    # url = 'http://192.168.30.91:8080/9f_insight/spider_translate/crawlData?title=甬新房预字（2017）第1008号&project_district=All&project=&date_filter_min=&date_filter_max=&userid=yinzhouyinhang&nocache=1'
    # url = 'http://localhost:8080/9f_insight/fangningbo/crawlData?userid=yinzhouyinhang&keyword=时代新居&flower=6层以下&nocache=1'
    url = 'http://localhost:8080/9f_insight/gsxt/crawlData?userid=yinzhouyinhang&idCard=91210200MA0QEYEB9C&nocache=1'
    url = 'http://localhost:8080/9f_insight/gsxt/crawlData?userid=yinzhouyinhang&idCard=大连火眼征信管理有限公司&nocache=1'
    url = 'http://192.168.30.91:8080/9f_insight/dishonesty/crawlData?name=陆莲娣&area=浙江&userid=yinzhouyinhang&nocache=1'
    # url = 'http://localhost:8080/9f_insight/gjjbeijing/crawlData?password=001200&userid=yinzhouyinhang&idCard=6214830161753008&nocache=1'
    # url = 'https://spider.insightcredit.cn/dishonesty/dishonesty/crawlData?name=烟台芝兴房地产开发有限公司&userid=yinzhouyinhang&nocache=1'
    # url = 'http://127.0.0.1:8080/9f_insight/telecom/crawlData?phoneNum=18001167287&password=121212&userid=yinzhouyinhang'
    # url = 'http://localhost:8080/9f_insight/fangningbo/crawlData?userid=yinzhouyinhang&keyword=时代华庭&flower=12层以上&age=5-10年&nocache=1'
    url = 'http://localhost:8080/9f_insight/gsxt/crawlData?userid=yinzhouyinhang&idCard=阿尔山市朝刚网吧&nocache=1'
    url = 'http://localhost:8080/9f_insight/gsxt/crawlData?userid=yinzhouyinhang&idCard=黑龙江建龙钢铁有限公司&nocache=1'
    # url = 'http://localhost:8080/9f_insight/nbcredit/crawlData?userid=yinzhouyinhang&idCard=宁波霸统机械有限公司&nocache=1'
    # url = 'http://localhost:8080/9f_insight/nbcredit/crawlData?userid=yinzhouyinhang&idCard=91330203254152602K&nocache=1'
    url = 'http://localhost:8080/9f_insight/nbcredit/crawlData?userid=yinzhouyinhang&idCard=宁波市鄞州中河奇华快餐店&nocache=1'
    # 410411198809145567    145567
    # url = 'http://127.0.0.1:8080/9f_insight/gjjpingdingshan/crawlData?password=145567&userid=yinzhouyinhang&idCard=410411198809145567&nocache=1'
    import chardet
    print chardet.detect(url)

    print '原始的url为：\n{}\n'.format(url)
    # 对url进行加密
    newurl = getNewUrl(url)
    print '加密后的url为：\n{}\n'.format(newurl)
    # 获取url加密之后解析出的参数字典
    dict_json = ParamCrypto().getKwargs(newurl)
    print '获取加密url的参数字典：\n{}\n'.format(dict_json)
    # 对加密后的参数字典进行解密
    print type(dict_json)
    new_dict_json = decryptKwargs(dict_json)
    print '对加密字典进行解密：\n{}\n'.format(new_dict_json)

    # b = {u'status': u'0', u'nocache': u'1', u'date_filter_min': u'2bcda7f5e23933078a1e071427160dec',
    #  u'date_filter_max': u'2bcda7f5e23933078a1e071427160dec',
    #  u'title': u'55b2d00a69cdd4eacb8be77ef311055d54c5a228e94722467f61659206e470658048351314c77a52e6a55b4196384319',
    #  u'userid': u'yinzhouyinhang', u'project': u'2bcda7f5e23933078a1e071427160dec',
    #  u'token': u'2f6b8f0d-6add-4bc8-a139-47af53469c80', u'project_district': u'ade28f53668e272e457e14de121be4ff',
    #  u'desc': u'\u6b63\u5728\u722c\u53d6...'}
    # b = {'date_filter_min': '2bcda7f5e23933078a1e071427160dec',
    #      'date_filter_max': '2bcda7f5e23933078a1e071427160dec',
    #      'title': '55b2d00a69cdd4eacb8be77ef311055d54c5a228e94722467f61659206e470658048351314c77a52e6a55b4196384319',
    #      'userid': 'yinzhouyinhang',
    #      'project': '2bcda7f5e23933078a1e071427160dec',
    #      'project_district': 'ade28f53668e272e457e14de121be4ff',
    #      }
    # print type(b), 111
    #
    # c = {'date_filter_min': '2bcda7f5e23933078a1e071427160dec',
    #      'date_filter_max': '2bcda7f5e23933078a1e071427160dec',
    #      'title': '55b2d00a69cdd4eacb8be77ef311055d54c5a228e94722467f61659206e470658048351314c77a52e6a55b4196384319',
    #      'userid': 'xxx-xxx-xxx',
    #      'project': '2bcda7f5e23933078a1e071427160dec',
    #      'project_district': 'ade28f53668e272e457e14de121be4ff',
    #      }
    #
    #
    # print decryptKwargs(b)
    # print decryptKwargs(c)







    # 姚相宇测试地址


    # baiduNGWL
    # url = 'http://localhost:8080/9f_insight/spider_baiduNGWL/crawlData?nocache=1&userid=yinzhouyinhang&key=17757834655'
    # http://localhost:8080/9f_insight/spider_baiduNGWL/crawlData?userid=yinzhouyinhang&nocache=1&key=1ffd71a4a5922552c16887098861f72f

    # baiduSWL
    # url = 'http://localhost:8080/9f_insight/spider_baiduSWL/crawlData?nocache=1&userid=yinzhouyinhang&key=17757834655'
    # http://localhost:8080/9f_insight/spider_baiduSWL/crawlData?userid=yinzhouyinhang&nocache=1&key=1ffd71a4a5922552c16887098861f72f

    # gjjxinxiang
    # url = 'http://localhost:8080/9f_insight/spider_gjjxinxiang/crawlData?nocache=1&userid=yinzhouyinhang&personalid=410727199012202642&password=111111&person_name=杨振敏'
    # http://localhost:8080/9f_insight/spider_gjjxinxiang/crawlData?userid=yinzhouyinhang&password=c220ba9a72ba63753c6d15f26971246d&person_name=cbe1f262b1f4df0eac09fbc47cff998e&personalid=60a1239e658fffef145456b034e71470efa4c2433dedfb9436e2174fccfdfc93&nocache=1

    # # gjjyichun
    # url = 'http://localhost:8080/9f_insight/spider_gjjyichun/crawlData?nocache=1&personalid=362201199201210429&password=210429&userid=yinzhouyinhang'
    # http://localhost:8080/9f_insight/spider_gjjyichun/crawlData?password=daa34596e202378654d09869d14deccb&userid=yinzhouyinhang&personalid=63ef0a58b41bb3fff4b589e9a856ced292311dba2f85c1052a72a625698fd177&nocache=1

    # # ssdezhou
    # url = 'http://localhost:8080/9f_insight/spider_ssdezhou/crawlData?nocache=1&userid=yinzhouyinhang&personalid=371482199707222013&password=lyd'
    # http://localhost:8080/9f_insight/spider_ssdezhou/crawlData?password=f2745824044b7324965c6f6735d013f8&userid=yinzhouyinhang&personalid=f3913e6674d282bf3212f9c642b51a7eaa5b8855fd95eae76311c9af20d4fda5&nocache=1

    # # ssshaoyang
    # url = 'http://localhost:8080/9f_insight/spider_ssshaoyang/crawlData?nocache=1&userid=yinzhouyinhang&personalid=430524198706010345&password=666666&person_name=曾云'
    # http://localhost:8080/9f_insight/spider_ssshaoyang/crawlData?userid=yinzhouyinhang&password=7ae02068d8ddd8be6b70c13fcf3255fa&person_name=93241a3f41276fe57b8b24eaa4391cee&personalid=138f081a512adad35369dcb15443d399f394168a87fdd797c2a98f3ed8a13a2b&nocache=1

    # # sstaiyuan
    # url = 'http://localhost:8080/9f_insight/spider_sstaiyuan/crawlData?nocache=1&userid=yinzhouyinhang&username=1081291442&password=140107198409263912'
    # http://localhost:8080/9f_insight/spider_sstaiyuan/crawlData?username=91ad0209e0deee25a8a0aec5ba9a22b4&password=a04acb0dcaca1ed7ea96cd0e34a8a51f37bc1f699fc2be35be14015134dd3c58&userid=yinzhouyinhang&nocache=1


    # 孙博测试地址

    # # 宁波搜房网
    # url = 'http://localhost:8080/9f_insight/fangningbo/crawlData?userid=yinzhouyinhang&keyword=时代华庭&flower=6层以下&nocache=1'
    # url = 'http://localhost:8080/9f_insight/fangningbo/crawlData?userid=yinzhouyinhang&keyword=时代新居&flower=6层以下&age=2-5年&nocache=1'
    # http://localhost:8080/9f_insight/fangningbo/crawlData?userid=yinzhouyinhang&keyword=9fdf6f17735dbcf3a655eb0a4e2df6ef&nocache=1

    # # 宁波房产交易
    # url = 'http://localhost:8080/9f_insight/fang_translate/crawlData?title=甬新房预字（2017）第1008号&project_district=All&project=&date_filter_min=&date_filter_max=&userid=yinzhouyinhang&nocache=1'
    # # http://localhost:8080/9f_insight/fang_translate/crawlData?title=61c0878a11da154ee5a76fed4d2c0199a1fae2ef13821f2d409548af8acc39df87462744be9540c640ef83b557811285&date_filter_max=6848073b567fd54e022b0f5a57c485cb&date_filter_min=6848073b567fd54e022b0f5a57c485cb&userid=yinzhouyinhang&project=6848073b567fd54e022b0f5a57c485cb&project_district=0f4d7287bd3a0e18986aa1b399278df8&nocache=1

    # 91210200MA0QEYEB9C
    # # # 宁波企业信用网
    # url = 'http://localhost:8080/9f_insight/nbcredit/crawlData?userid=yinzhouyinhang&idCard=百度&nocache=1'
    # # http://localhost:8080/9f_insight/nbcredit/crawlData?idCard=7e6625dbfbb8968c5b637db909f4469e&userid=yinzhouyinhang&nocache=1

    # # # 国税局发票
    # url = 'http://localhost:8080/9f_insight/tax/crawlData?fpdm=1100173130&fphm=05896251&kprq=20171108&fpje=2361.32&userid=yinzhouyinhang&nocache=1'
    # # http://localhost:8080/9f_insight/tax/crawlData?fphm=856ea0503f914d751cd02bb18d75dd3d&userid=yinzhouyinhang&fpje=fe9e933505d8ddda33b8486b3a501f37&kprq=9d327fdb3b33ff33adc35e3eee5b0d5c&fpdm=570f4fc60380f7e52e0b0c7a8ea23ad2&nocache=1

    # 国家企业公示系统
    # {"idCard":"山西建龙钢铁有限公司", "token": "tokentokentokentokentoken", "userid":"xxxxxxxxxxxxxxxx"}
    # spider.insightcredit.cn/gsxt/crawlData?idCard=70b26c333d201e3b393dc185e3237b3d&userid=yinzhouyinhang&nocache=1&area=8165a61937d6793b66418a8ba77fbc70



    # 失信人被执行人

    # 被执行人：http://spider.insightcredit.cn/executored/crawlData?userid=yinzhouyinhang&name=c312dcd38eaec280f467a9a86e46ce62&nocache=1
    # 失信人： http://spider.insightcredit.cn/executor/crawlData?userid=yinzhouyinhang&name=b27226150e8413da44709fc6c9b4942f51f3858eae3f82952ea570f0340c8076804ec5e93919fc56659615b5bbdb206d&nocache=1


    # url = 'http://localhost:8080/9f_insight/executored/crawlData?name=湖南海得工程机械&cardNum=68032880X&userid=yinzhouyinhang&nocache=1'
    # url = 'http://localhost:8080/9f_insight/executored/crawlData?name=山东第二前进机械厂&cardNum=168270813&userid=yinzhouyinhang&nocache=1'
    # http://localhost:8080/9f_insight/executored/crawlData?userid=yinzhouyinhang&name=196735c8c917b84b6ea6778dac913ac107571aa7dbe311bf25437ed169e5cfae&nocache=1&cardNum=be6a895a85f82a8cc4f2c1cf5feaea41


    # url = 'http://localhost:8080/9f_insight/executor/crawlData?name=四川众力房地产开发有限公司&userid=yinzhouyinhang&nocache=1'
    # http://localhost:8080/9f_insight/executor/crawlData?userid=yinzhouyinhang&name=b27226150e8413da44709fc6c9b4942f51f3858eae3f82952ea570f0340c8076804ec5e93919fc56659615b5bbdb206d&nocache=1


    # print getNewUrl(url)



# fang_translate
# seach58_ningbo
# af_dezhou
# af_shaoyang
# ss_dalian
# af_xianyang
# spider_baiduNGWL
# spider_gjjxinxiang
# spider_gjjyichun