#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/8/11 2:20
# 语言：Python 2.7.13
# 功能：
#
#-------------------------------------------------------------------------
import hashlib
import urllib
import urllib2
import cookielib
import json
import base64

cookieJar = cookielib.CookieJar()
openner = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
urllib2.install_opener(openner)

def md5str(str):
	'''
	md5加密字符串
	:param str:
	:return:
	'''
	m=hashlib.md5(str.encode(encoding = "utf-8"))
	return m.hexdigest()
		
def md5(byte):
	'''
	md5加密byte
	:param byte:
	:return:
	'''
	md5_str = hashlib.md5(byte).hexdigest()
	return md5_str

'''
打码兔工具类
'''
class DamatuApi():
	ID = '46729'
	KEY = '618823b02e034087a2dc4685c1e89dfe'
	HOST = 'http://api.dama2.com:7766/app/'
	
	def __init__(self,username,password):
		self.username=username
		self.password=password
		
	def getSign(self,param=b''):
		return (md5(bytes(self.KEY) + bytes(self.username) + param))[:8]
		
	def getPwd(self):
		return md5str(self.KEY +md5str(md5str(self.username) + md5str(self.password)))
		

	def post(self,path,params={}):
		data = urllib.urlencode(params).encode('utf-8')
		url = self.HOST + path
		response = urllib2.Request(url, data=data)
		return urllib2.urlopen(response).read()
	
	def getBalance(self):
		'''
		查询余额
		:return: 是正数为余额 如果为负数 则为错误码
		'''
		data={'appID':self.ID,
			'user':self.username,
			'pwd':self.getPwd(),
			'sign':self.getSign()
		}
		res = self.post('d2Balance',data)
		res = str(res)
		jres = json.loads(res)
		if jres['ret'] == 0:
			return jres['balance']
		else:
			return jres['ret']
    

	def decode(self,filePath,type):
		'''
		上传验证码
		:param filePath: 验证码图片路径 如d:/1.jpg
		:param type: 类型
		:return: 是答案为成功 如果为负数 则为错误码
		'''
		f=open(filePath,'rb')
		fdata=f.read()
		filedata=base64.b64encode(fdata)
		print filedata
		f.close()
		data={'appID':self.ID,
			'user':self.username,
			'pwd':self.getPwd(),
			'type':type,
			'fileDataBase64':filedata,
			'sign':self.getSign(fdata)
		}
		res = self.post('d2File',data)
		res = str(res)
		jres = json.loads(res)
		if jres['ret'] == 0:
			# 注意这个json里面有ret，id，result，cookie，根据自己的需要获取
			return(jres['result'])
		else:
			return jres['ret']


	def decodeUrl(self, url, type):
		'''
		url地址打码
		:param url: 地址
		:param type: 类型(类型查看http://wiki.dama2.com/index.php?n=ApiDoc.Pricedesc)
		:return: 答案为成功 如果为负数 则为错误码
		'''
		data={'appID':self.ID,
			'user':self.username,
			'pwd':self.getPwd(),
			'type':type,
			'url': url,
			'sign':self.getSign(url.encode(encoding = "utf-8"))
		}
		res = self.post('d2Url',data)
		res = str(res)
		jres = json.loads(res)
		if jres['ret'] == 0:
			# 注意这个json里面有ret，id，result，cookie，根据自己的需要获取
			return(jres['result'])
		else:
			return jres['ret']
	
	def reportError(self,id):
		'''
		报错
		:param id: (string类型)由上传打码函数的结果获得
		:return: 0为成功 其他见错误码
		'''
		#f=open('0349.bmp','rb')
		#fdata=f.read()
		#print(md5(fdata))
		data={'appID':self.ID,
			'user':self.username,
			'pwd':self.getPwd(),
			'id':id,
			'sign':self.getSign(id.encode(encoding = "utf-8"))
		}	
		res = self.post('d2ReportError',data)
		res = str(res)
		jres = json.loads(res)
		return jres['ret']

if __name__ == '__main__':
	# 调用类型实例：
	# 1.实例化类型 参数是打码兔用户账号和密码
	dmt = DamatuApi("29.跨文件全局变量", "29.跨文件全局变量")
	#2.调用方法：
	print(dmt.getBalance()) #查询余额
	# print(dmt.decode('./captcha.png', 200)) #上传打码
	# print(dmt.decodeUrl('http://shixin.court.gov.cn/captchaNew.do?captchaId=8f5dc06c27e94225b4c74175dad3c056&random=0.5135552410045265', 200)) #上传打码
	#print(dmt.reportError('894657096')) #上报错误

