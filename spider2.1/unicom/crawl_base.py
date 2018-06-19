# coding=utf-8
import os
import time
import copy
import shutil
import base64
import logging
import logging.config
from datetime import datetime

from __Utils import damatuWeb
from __Utils.redis_utils import RedisUtils
from __Utils.constants import PROXYADDR
from constants_spider import SOURCE
from constants_spider import NEED_MORE
from constants_spider import INPUT_ERROR
from constants_spider import WAITTIME
from constants_spider import TYPEVALUE
 



 
class CrawlBase(object):

    def __init__(self, dict_json, key=[], verifycode_type='png'):
        self.redisUtils = RedisUtils()
        self.damatuWeb = damatuWeb
        self.PROXYADDR = PROXYADDR
        self.dict_json = dict_json
        self.token = self.dict_json['token']
        self.verifycode_type = verifycode_type
        self.status = None
        self.desc = None

        self.current_milli_time = lambda: str(int(round(time.time() * 1000)))
        self.startTime = self.current_milli_time()

        self.realpath = os.path.split(os.path.realpath(__file__))[0]
        filename = 'verifycode/%s_verifycode.%s'%(self.startTime, verifycode_type)
        self.code_path = os.path.join(self.realpath, filename)

        logging.config.fileConfig('unicom/logging.config')
        self.logger = logging.getLogger('flow')

        # 是否保存用户目录，默认为爬虫出错才保存，也可以手动修改
        self.rmuserdirFlag = False
        self.mkUserdir(key)


    '''  用户信息以及爬取页面记录，爬取成功会删除，失败则会保存下来便于排错 '''

    def mkUserdir(self, key=[]):
        # 创建用户文件夹
        fn = os.path.join(self.realpath,
         'sample', '%s_%s'%(self.startTime, self.dict_json['token']))
        os.mkdir(fn)
        # 覆盖敏感信息
        info_dict = copy.deepcopy(self.dict_json)
        for k in key:
            info_dict[k] = u'******'
        with open(os.path.join(fn,'dict_json.txt'), 'w') as f:
            f.write(str(info_dict))
        self.userdir = fn
        return

    def rmUserdir(self, fn):
        shutil.rmtree(fn)

    def takePage(self, n, content, msg = None):
        fn = os.path.join(self.userdir, n)
        with open(fn, 'w') as f:
            f.write(content)
        if msg:
            with open(fn, 'a') as f:
                f.write('\n'*5 + '#'*60 + '\n'*3 + msg)




    ''' 验证码交互相关 '''


    def get_verifycode(self, codeUrl=None):
        # 获取图片验证码，并发送通知，如果是短信验证码，或者必须使用driver，可重写此函数
        if callable(codeUrl):
            codeUrl = codeUrl()
        codeContent = self.session.get(codeUrl).content
        bcode = base64.b64encode(codeContent)
        self.redisUtils.setNotify(token = self.token,
                                    val = NEED_MORE, decs='需要图片验证码',
                                    result = 'data:image/jpg;base64,' + bcode)
        self.logger.info('验证码已发送')

    def judge_verifycode(self, inputValue, ResetCode):
        # verifycode_handler会根据此函数的返回值判断验证码对错
        # 判断验证码对错，爬虫自定义，如果验证码不是错误的，此函数的返回值，将被verifycode_handler()返回
        pass

    def get_input(self):
        # 获取用户输入
        stime = datetime.now()
        self.logger.info('等待用户输入')
        while True:
            inputValue = self.redisUtils.getNotify(self.token, 'bcode')
            if inputValue:
                return inputValue
            else:
                eclipseTimes = datetime.now() - stime
                if eclipseTimes.total_seconds() > WAITTIME:
                    self.logger.info('接收用输入超时:%s' % self.token)
                    self.status = INPUT_ERROR
                    self.desc = '接收用输入超时'
                    time.sleep(1)
                    return


    def verifycode_handler(self, codeUrl=None, ResetCode=False):
        # 交互流程，接受用户响应，可以选择刷新验证码，或者输入验证码
        # ResetCode 可控制是否保持会话，开启验证码刷新功能，默认不保持会话
        self.logger.info('需要验证码')
        self.get_verifycode(codeUrl)
        while True:
            inputValue = self.get_input()
            if inputValue == 'reset':
                if ResetCode:
                    self.logger.info('用户刷新验证码')
                    self.redisUtils.DelNotify(self.token, 'bcode')
                    self.get_verifycode(codeUrl)
                    continue
            elif inputValue == None:
                return
            else:
                # 验证码输入是否正确
                result = self.judge_verifycode(inputValue, ResetCode)
                if result:
                    return result
                else:
                    if ResetCode:
                        self.redisUtils.DelNotify(self.token, 'bcode')
                        self.redisUtils.setNotify(token=self.token, val=INPUT_ERROR, decs='验证码错误')
                        self.logger.info('验证码错误')
                        continue
                    self.status = INPUT_ERROR
                    self.desc = '验证码错误'
                    return



if __name__ == '__main__':

    a = CrawlBase('jpeg')
    fn = a.mkUserdir({'username':'test', 'password':'123', 'token':'a'}, ['password'])
    a.takePage('test.html', 'hiehiehie', 'hahhahahhahah')
    raw_input()
    a.rmUserdir(fn)
