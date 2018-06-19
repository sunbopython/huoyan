# coding=utf-8
import re
import time
import json
import requests
import xmltodict
from Crypto.Cipher import DES3

url = 'http://cservice.client.189.cn:8004/map/clientXML?encrypted=true'
key = "1234567`90koiuyhgtfrdewsaqaqsqde"
k = bytearray(key)
k = k[0:24]

v = bytearray(8)
for i in range(len(v)):
    v[i] = 0

def decrypt(k, v, text):
    cipher = DES3.new(str(k), DES3.MODE_CBC, str(v))
    s = text.decode('hex_codec')
    y = cipher.decrypt(s)
    return y

def encrypt(k, v, text):
    cipher = DES3.new(str(k), DES3.MODE_CBC, str(v))
    i = 8 - len(text) % 8
    tmp = ""
    for each in range(i):
        tmp = tmp + chr(i)
    text = text + tmp
    res = cipher.encrypt(text)
    return res.encode('hex_codec').upper()

def str2byte(s):
    base='0123456789ABCDEF'
    i=0
    s = s.upper()
    s1=''
    while i < len(s):
        c1=s[i]
        c2=s[i+1]
        i+=2
        b1=base.find(c1)
        b2=base.find(c2)
        if b1 == -1 or b2 == -1:
            return None
        s1+=chr((b1 << 4)+b2)
    return s1

def httppost(url, data):
    postdata = encrypt(k, v, data)
    bs = bytearray(postdata)
    dictheader = {'Content-length': str(len(bs)), 'Content-Type': 'text/xml', 'Host': 'cservice.client.189.cn:8004', 'User-Agent': 'samsung GT-I9500/5.0.0'}
    res = requests.post(url, postdata, dictheader)
    r = decrypt(k, v, res.text)
    r = re.findall(r'<Response>.*?</Response>', r)[0]
    json = xmltodict.parse(r, encoding='utf-8')
    return json


def password_login(username, password):
    data = "<Request><HeaderInfos><Code>loginInfo</Code><Timestamp>" + time.strftime('%Y%m%d%H%M%S', time.localtime()) + "</Timestamp><ClientType>#6.0.0#channel45#OPPO OPPO R9s#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>null</Token><UserLoginName>"+ username +"</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><PswType>01</PswType><PhonePsw>"+password+"</PhonePsw><PhoneNbr>"+ username +"</PhoneNbr><AccountType>c2000004</AccountType><Token></Token></FieldData></Content></Request>"
    json = httppost(url, data)
    if json['Response']['ResponseData']['ResultCode'] == u'0000':
        account = {}
        account['username'] = username
        account['password'] = password
        account['Token'] = json['Response']['ResponseData']['Data']['Token']
        account['PhoneNbr'] = json['Response']['ResponseData']['Data']['PhoneNbr']
        account['UserId'] = json['Response']['ResponseData']['Data']['UserId']
        return account
    return None


def verifycode_login(username, verifycode):
    data = "<Request><HeaderInfos><Code>loginInfo</Code><Timestamp>" + time.strftime('%Y%m%d%H%M%S', time.localtime()) + "</Timestamp><ClientType>#6.0.0#channel45#OPPO OPPO R9s#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>null</Token><UserLoginName>"+ username +"</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><PswType>04</PswType><PhonePsw>"+ verifycode +"</PhonePsw><PhoneNbr>"+ username +"</PhoneNbr><AccountType>c2000004</AccountType><Token></Token></FieldData></Content></Request>"
    json = httppost(url, data)
    if json['Response']['ResponseData']['ResultCode'] == u'0000':
        account = {}
        account['username'] = username
        account['password'] = verifycode
        account['Token'] = json['Response']['ResponseData']['Data']['Token']
        account['PhoneNbr'] = json['Response']['ResponseData']['Data']['PhoneNbr']
        account['UserId'] = json['Response']['ResponseData']['Data']['UserId']
        return account
    return None



def get_detail_verifycode(account):
    """ 向用户发送详单验证码 """
    # print account['Token']
    data = "<Request><HeaderInfos><Code>getRandomV2</Code><Timestamp>" + time.strftime('%Y%m%d%H%M%S', time.localtime()) + "</Timestamp><ClientType>#6.0.0#channel45#OPPO OPPO R9s#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>" + account["Token"] + "</Token><UserLoginName>" + account["username"] + "</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><SceneType>7</SceneType><Imsi></Imsi><PhoneNbr>" + account["username"] + "</PhoneNbr></FieldData></Content></Request>"
    json = httppost(url, data)
    return json

def get_login_verifycode(username): 
    """ 向用户发送登录验证码 """
    data = "<Request><HeaderInfos><Code>getRandomV2</Code><Timestamp>" + time.strftime('%Y%m%d%H%M%S', time.localtime()) + "</Timestamp><ClientType>#6.0.0#channel45#OPPO OPPO R9s#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token></Token><UserLoginName>" + username + "</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><PhoneNbr>" + username + "</PhoneNbr></FieldData></Content></Request>"
    json = httppost(url, data)
    return json


def send_detail_verifycode(account):
    
    res = get_detail_verifycode(account)
    # print json.dumps(res, ensure_ascii=False).encode('utf-8')
        
    if res['Response']['ResponseData']['ResultDesc'] == u'同网短信条数超过限制！':
        return '发送短信条数已超过限制'
    if res['Response']['HeaderInfos']['Code'] == u'0000':
        return
    return '验证码发送失败'

def send_login_verifycode(account):
    
    res = get_login_verifycode(account)
    if res['Response']['HeaderInfos']['Code'] == u'0000':
        return 200
    return 202


def fetch_detail(account, verifycode, date, data_type):
    """ 查询详单 """

    data = "<Request><HeaderInfos><ClientType>#5.0.0#channel11#samsung GT-I9500#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>" + account["Token"] + "</Token><UserLoginName>" + account["username"] + "</UserLoginName><Code>jfyBillDetail</Code><Timestamp>" + time.strftime('%Y%m%d%H%M%S', time.localtime()) + "</Timestamp></HeaderInfos><Content><Attach>test</Attach><FieldData><EndTime>" + date + "</EndTime><StartTime>" + date + "</StartTime><Random>" + verifycode + "</Random><PhoneNum>" + account["username"] + "</PhoneNum><Type>" + data_type + "</Type></FieldData></Content></Request>"
    json = httppost(url, data)
    return json

def fetch_hisBill(account, month):
    # print account["Token"]
    """ 查询历史账单 """
    data = "<Request><HeaderInfos><Code>jfyHisBill</Code><Timestamp>" + time.strftime('%Y%m%d%H%M%S', time.localtime()) + "</Timestamp><ClientType>#6.0.0#channel45#OPPO OPPO R9s#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>" + account["Token"] + "</Token><UserLoginName>" + account["username"] + "</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><Random>123456</Random><Month>"+ month +"</Month><PhoneNum>" + account["username"] + "</PhoneNum><Type>1</Type></FieldData></Content></Request>"
    json = httppost(url, data)
    return json



if __name__ == '__main__':
    req1 = '2966aa9f9a149371483724b75dc53d50ad1ebceb8d1c521b9d16f30428f4ef6c22bed5c720f6c4a892c821315831667cc5f92567cff7932f5d30209f43584faeac5f37ceafe41c4169d525e1a1e2e0f94893f5cfbf77502a62a3e21efcf89e8ab41c2ef33a6639f9e744b94435bc089d1a8560e515612d304188662ef6ae7fbe02cb177a2c1cfd71fcfe7cdb486cb635c7c968e0687ef5499bc561a9b69cf2915f0eedf744befadbd9633c8da841d4ac10be227ca7528c901a5471e53b5c7eed27873fd94579eeee7d09d77fe11a89e974936912ff37120676690b8ac93d4f0ccb128307c30641c0bcb6b72055308152b2c9070ba844fe95363bcdbe197022d73bf2be7f34ecac12fc4f29ebc35921356261b8445a70545b598ab9203525285e230ad832589e16b8888a728ed9ec73629be0809a5b8e9a79b06882984381c5d7621ff098a1b130ab4930bd426812d7d88cc7d77baf8a53b24dc8d2a8f47541276e387a8a2520a8c75d4cfdcd7f178293fe97061af92886ac097bc0ba2021ffce21bad27240ccc6e14bdf94c50401dc03633754668b635bd55ce76217a45b0ba9f80ca6f031a555afba4dbae4d92c0d7e19be57a0cdeceadf5273857da574d58dc3e903ab91d3079a1667e20eb597868394fa1b6aedbf249e'
    res1= 'b5720f816f50db5eb94116fd795b9f770f4af1f252692aa8c138f0e8150856db0b52b7c8000a7be699aabc4ab106f380f9e488a10e8269792beb5b46a667cdf32e20cf7649e74841dcfc49d871e100bda5b005efdca1abf6d8f95b802b6db01dc0bc44d9f75be7b899fcac6bf3674bff51429cb76f9ea218fa2bad0b88a6c6c80d9edbb96f284e26c08a514ffe89869973b1d297873df3042f7fed5cff21498279cee5c1521deab082083b21bbdbcdcb220296bf63016e23a7800ae70535cd97687bce15f61797d28dcc5b4ae76750b5'
    
    req2 = '2966aa9f9a149371483724b75dc53d50ad1ebceb8d1c521bccb10714772b5a71803f582057d7b073f0f991aca16c951430142c92ee708e057e7a9a4d94942527682d33237ef1d960f282894d151ba1970ed291d58a04490871750108b218c3e4f41f4b6736e6c11f8b7132f63978654d618fbd5829f6c3456b8348038de2e2e5e55bf638a32465a20d8322eeed9e34bf6f8f885534448e7b356c62a17a8461f86810b3a783ec47b45172e79e744859706ecc630df1a555569eeeaf001627fac19c526a30cb9685a0e185c4d491f889144ca55618f3e53f33d665e8a2b89706c52b4d080de902374acefa1a39b7467707ca3e7611c8a700f5bfc035800b800f70a018eea74afb7e3fab7ffcaf4aa6e92daf4735796787469f4bcb200f95a55b9e82596cadc8e45c8fc059b343fb683dceb99b44d67817b58ebe45e0b48249147c0bfa6c48207f21cd62dc2b7449fd84070c437d7083be251c0bf8957f284415769443bac0c24ef708739c3503e8a1072b3908570f8b0f097b7ff24d954645cda857d7354e981154b304b4776a13e6ff43d8c928d5841e79b9a3a598383f10209ba1cee90dc6ef2789addba175e6751f5f5e57ab2edbdff53624cf4fa4837a20537b423e8db8dbed3b8d3648f9540062d1bcbfe8017484a0053f65b119e5a7cec3c9488a091492ec9757371a4089a57722ab74dc3cc644e54adc1c7968b13264fad43dd29da667c9b58c3d24d4a07d1a09325439016061cf4c9b5d4bf6b5da1602303ef79284df4b9abe274fdd2af209af22c2d1ddf7d1f089a5667cd4c565baf97366252cf6dbb1d0dbee355617140e7a204ca2a65e9d0cb8'
    res2 = 'b5720f816f50db5eb94116fd795b9f770f4af1f252692aa8c138f0e8150856db0b52b7c8000a7be699aabc4ab106f380f9e488a10e8269792beb5b46a667cdf32e20cf7649e74841dcfc49d871e100bda5b005efdca1abf6d8f95b802b6db01dc0bc44d9f75be7b899fcac6bf3674bff51429cb76f9ea218cb851dd7971eef8b4210ae9087833a0c5a255dffc072c4cf850075973874c879def070bd371f343fb9a502ef1e55fe16bdbb3058fa730f01df57c2b4998d3502cf34eca68e02fb3ac861bff5cd5006b9ae4d6a045a4ea59fc9b0e374d84e562d2b454fb2f3281b56ddbffd95c923af407a550154ecec646df95be513d5dd2154'
    print decrypt(k, v, req1)
    print decrypt(k, v, res1)
    print decrypt(k, v, req2)
    print decrypt(k, v, res2)




# <Request><HeaderInfos><Code>getRandomV2</Code><Timestamp>20171211131033</Timestamp><ClientType>#6.2.1#channel38#Xiaomi MI 6#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>YsTbSDV+xXdijwS4lB8G2eUhGkP88TsQZtCedbD1RA3atGC1djz79g==</Token><UserLoginName>18001167287</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><SceneType>7</SceneType><Imsi></Imsi><PhoneNbr>18001167287</PhoneNbr></FieldData></Content></Request>
# <Response><HeaderInfos><Code>0000</Code><Reason>成功</Reason></HeaderInfos><ResponseData><Attach>test</Attach><ResultCode>0000</ResultCode><ResultDesc>操作成功</ResultDesc></ResponseData></Response>
# <Request><HeaderInfos><Code>randomCodeAndAuthValidate</Code><Timestamp>20171211131129</Timestamp><ClientType>#6.2.1#channel38#Xiaomi MI 6#</ClientType><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>YsTbSDV+xXdijwS4lB8G2eUhGkP88TsQZtCedbD1RA3atGC1djz79g==</Token><UserLoginName>18001167287</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><RandomCode>378086</RandomCode><ValidateType>1</ValidateType><Username>bac</Username><ShopId>20002</ShopId><IdCardNum>412726139612102456</IdCardNum><PhoneNum>18001167287</PhoneNum></FieldData></Content></Request>
# <Response><HeaderInfos><Code>0000</Code><Reason>成功</Reason></HeaderInfos><ResponseData><Attach>test</Attach><ResultCode>0001</ResultCode><ResultDesc>非实名制用户</ResultDesc><Data>
#   <Result>1</Result>
# </Data></ResponseData></Response>
