#coding=utf-8
import re
from lxml import etree






# 个人信息：
personal_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indNewInfoSearchAction'
# 养老：
oldage_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indPaySearchAction!oldage?searchYear='
# 失业：
unemployment_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indPaySearchAction!unemployment?searchYear='
# 工伤：
injuries_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indPaySearchAction!injuries?searchYear='
# 生育：
maternity_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indPaySearchAction!maternity?searchYear='
# 医疗：
medicalcare_url = 'http://www.bjrbj.gov.cn/csibiz/indinfo/search/ind/indPaySearchAction!medicalcare?searchYear='


def personal_information_handler(session):
    """ 获取个人信息 """

    personal_information = session.get(personal_url)
    result = etree.HTML(personal_information.text)
    personal = {}

    info_1 = ''.join(result.xpath('//body/form[@id="printForm"]/table[1]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_2 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[2]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_3 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[3]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_4 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[4]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_5 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[5]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_6 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[6]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_7 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[7]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_8 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[8]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_9 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[9]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_10 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[10]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_11 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[11]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_12 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[12]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_13 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[13]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_14 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[14]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_15 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[15]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_16 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[16]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_17 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[17]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_18 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[18]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_19 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[19]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_20 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[20]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')
    info_21 = ''.join(result.xpath('//body/form[@id="printForm"]/table[2]//tr[21]//text()')).replace('\r', '').replace('\n', '').replace('\t', '')


    # 单位名称
    personal['workUnits'] = re.findall(ur'单位名称：(.*)组织机构代码', info_1)[0].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '')
    # 组织机构代码
    personal['organizationCode'] = re.findall(ur'组织机构代码：(.*)社会保险登记证编号', info_1)[0].strip()
    # 社会保险登记证编号
    personal['socialSecurityNumber'] = re.findall(ur'社会保险登记证编号：(.*)所属区县', info_1)[0].strip()
    # 所属区县
    personal['districtsCounties'] = re.findall(ur'所属区县：(.*)', info_1)[0].strip()
    # 姓名
    personal['name'] = re.findall(ur'姓 名(.*)\*公民身份号', info_2)[0]
    # 公民身份号码（社会保障号码）
    personal['socialSecurityID'] = re.findall(ur'会保障号码）(.*)', info_2)[0]
    # 性别
    personal['gender'] = re.findall(ur'性 别(.*)\*出生', info_3)[0]
    # 生日
    personal['birthday'] = re.findall(ur'出生日期(.*)', info_3)[0]
    # 民族
    personal['nationality'] = re.findall(ur'民 族(.*)\*国家', info_4)[0]
    # 国家/地区
    personal['country'] = re.findall(ur'地区(.*)', info_4)[0]
    # 个人身份
    personal['identity'] = re.findall(ur'个人身份(.*)\*参加', info_5)[0]
    # 参加工作日期
    personal['dateWork'] = re.findall(ur'工作日期(.*)', info_5)[0]
    # 户口所在区县街乡
    personal['hukouCountyStreet'] = re.findall(ur'区县街乡(.*)\*户口性质', info_6)[0]
    # 户口性质
    personal['hukouProperties'] = re.findall(ur'户口性质(.*)', info_6)[0]
    # 户口所在地
    personal['hukouAddress'] = re.findall(ur'所在地地址(.*)\*户口所在地邮政编码', info_7)[0]
    # 户口所在地邮编  
    personal['hukouAddressZipcode'] = re.findall(ur'所在地邮政编码(.*)', info_7)[0]
    # 居住地址
    personal['residentialAddress'] = re.findall(ur'地址(.*)居住地', info_8)[0]
    # 居住地址邮编
    personal['residentialAddressZipcode'] = re.findall(ur'邮政编码(.*)', info_8)[0]
    # 选择邮寄社会保险对账单地址 
    personal['billAddress'] = re.findall(ur'账单地址(.*)对账单', info_9)[0]
    # 对账单邮编
    personal['billAddressZipcode'] = re.findall(ur'邮政编码(.*)', info_9)[0]
    # 获取对账单方式
    personal['billType'] = re.findall(ur'对账单方式(.*)电子邮件地址', info_10)[0]
    # 电子邮件地址
    personal['email'] = re.findall(ur'电子邮件地址(.*)\*文化程度', info_10)[0]
    # 文化程度
    personal['education'] = re.findall(ur'文化程度(.*)', info_10)[0]
    # 参保人电话
    personal['telephone'] = re.findall(ur'保人电话(.*)参保人手机', info_11)[0]
    # 参保人手机
    personal['phone'] = re.findall(ur'参保人手机(.*)\*申报月均工资', info_11)[0]
    # 申报月均工资收入
    personal['monthlyWage'] = re.findall(ur'均工资收入（元）(.*)', info_11)[0]
    # 证件类型
    personal['credentialsType'] = re.findall(ur'证件类型(.*)\*证件号码', info_12)[0]
    # 证件号码
    personal['credentialsNumber'] = re.findall(ur'证件号码(.*)', info_12)[0]
    # 委托代发银行名称
    personal['bankName'] = re.findall(ur'委托代发银行名称(.*)\*委托代发银行账号', info_13)[0]
    # 委托代发银行账号
    personal['bankNumber'] = re.findall(ur'委托代发银行账号(.*)', info_13)[0]
    # 缴费人员类别
    personal['paymentPersonnelType'] = re.findall(ur'缴费人员类别(.*)\*医疗参保人员类别', info_14)[0]
    # 医疗参保人员类别
    personal['healthCarePersonnelType'] = re.findall(ur'医疗参保人员类别(.*)', info_14)[0]
    # 离退休类别
    personal['retireType'] = re.findall(ur'离退休类别(.*)离退休日期', info_15)[0]
    # 离退休日期
    personal['retiredate'] = re.findall(ur'离退休日期(.*)', info_15)[0]
    # 定点医疗机构1
    personal['sentinelMedicalInstitutions_1'] = re.findall(ur'定点医疗机构1(.*)定点医疗机构', info_16)[0]
    # 定点医疗机构2
    personal['sentinelMedicalInstitutions_2'] = re.findall(ur'定点医疗机构2(.*)', info_16)[0]
    # 定点医疗机构3
    personal['sentinelMedicalInstitutions_3'] = re.findall(ur'定点医疗机构3(.*)定点医疗机构', info_17)[0]
    # 定点医疗机构4
    personal['sentinelMedicalInstitutions_4'] = re.findall(ur'定点医疗机构4(.*)', info_17)[0]
    # 定点医疗机构5
    personal['sentinelMedicalInstitutions_5'] = re.findall(ur'定点医疗机构5(.*)\*是否患有特殊病', info_18)[0]
    # 是否患有特殊病
    personal['isSufferSpecialIllnesses'] = re.findall(ur'是否患有特殊病(.*)', info_18)[0]
    # 护照号码    
    personal['passportNumber'] = re.findall(ur'护照号码(.*)外国人居留证号码', info_20)[0]
    # 外国人居留证号码
    personal['foreignerResidencePermitNumber'] = re.findall(ur'外国人居留证号码(.*)', info_20)[0]
    # 外国人证件类型
    personal['foreignerCredentialsType'] = re.findall(ur'外国人证件类型(.*)外国人证件号码', info_21)[0]
    # 外国人证件号码
    personal['foreignerCredentialsNumber'] = re.findall(ur'外国人证件号码(.*)', info_21)[0]

    newPersonal = {}
    for key, value in personal.items():

        newValue = value.replace(u' ', '')
        newPersonal[key] = newValue


    return newPersonal


def oldage_information_handler(session, time_now_year, idcard):
    """ 获取养老保险缴费记录 """
    oldage = []
    count = 0

    for year in range(time_now_year-5, time_now_year+1):
        oldage_information = session.get(oldage_url + str(year))
        if len(re.findall(ur'没有找到符合条件的个人用户信息', oldage_information.text)) == 0:
            result = etree.HTML(oldage_information.text)
            info = result.xpath('//tr')[2: -1]
            for info_item in info:
                oldage_item = {}
                item = info_item.xpath('./td/text()')
                if item[2] != u'-':
                    if len(re.findall('\d+', item[0])) == 0:
                        item.insert(0, oldage[-1]['date'])
                        count += 1
                    
                    # 社保卡号码
                    oldage_item['socialSecurityCardNumber'] = idcard.strip()
                    # 险种类型
                    oldage_item['type_B'] = u'养老'
                    # 缴费年月    
                    oldage_item['Date'] = item[0].strip()
                    # # 缴费类型    
                    # oldage_item['type'] = item[1]
                    # # 缴费基数    
                    # oldage_item['base'] = item[2]
                    # 单位缴费    
                    oldage_item['company_pay'] = item[3].strip()
                    # 个人缴费    
                    oldage_item['personmoney'] = item[4].strip()
                    # # 缴费单位名称
                    # oldage_item['unitName'] = item[5]

                    oldage.append(oldage_item)

    oldage.append(count)
    return oldage



def unemployment_information_handler(session, time_now_year, idcard):
    """ 获取失业保险缴费记录 """

    unemployment = []
    count = 0

    for year in range(time_now_year-5, time_now_year+1):
        unemployment_information = session.get(unemployment_url + str(year))
        if len(re.findall(ur'没有找到符合条件的个人用户信息', unemployment_information.text)) == 0:
            result = etree.HTML(unemployment_information.text)
            info = result.xpath('//tr')[2: -1]
            for info_item in info:
                unemployment_item = {}
                item = info_item.xpath('./td/text()')
                if item[1] != u'-':
                    if len(re.findall('\d+', item[0])) == 0:
                        item.insert(0, unemployment[-1]['date'])
                        count += 1

                    # 社保卡号码
                    unemployment_item['socialSecurityCardNumber'] = idcard.strip()
                    # 险种类型
                    unemployment_item['type_B'] = u'失业'
                    # 缴费年月    
                    unemployment_item['Date'] = item[0].strip()
                    # # 缴费基数    
                    # unemployment_item['base'] = item[1]
                    # 单位缴费    
                    unemployment_item['company_pay'] = item[2].strip()
                    # 个人缴费
                    unemployment_item['personmoney'] = item[3].strip()

                    unemployment.append(unemployment_item)

    unemployment.append(count)
    return unemployment

def injuries_information_handler(session, time_now_year, idcard):
    """ 获取工伤保险缴费记录 """

    injuries = []
    count = 0

    for year in range(time_now_year-5, time_now_year+1):
        injuries_information = session.get(injuries_url + str(year))
        if len(re.findall(ur'没有找到符合条件的个人用户信息', injuries_information.text)) == 0:
            result = etree.HTML(injuries_information.text)
            info = result.xpath('//tr')[2: -1]
            for info_item in info:
                injuries_item = {}
                item = info_item.xpath('./td/text()')
                if item[1] != u'-':
                    if len(re.findall('\d+', item[0])) == 0:
                        item.insert(0, injuries[-1]['date'])
                        count += 1
                    # 社保卡号码
                    injuries_item['socialSecurityCardNumber'] = idcard.strip()
                    # 险种类型
                    injuries_item['type_B'] = u'工伤'
                    # 缴费年月
                    injuries_item['Date'] = item[0].strip()
                    # # 缴费基数
                    # injuries_item['base'] = item[1]
                    # 单位缴费
                    injuries_item['company_pay'] = item[2].strip()
                    # 个人缴费
                    injuries_item['personmoney'] = ''

                    injuries.append(injuries_item)

    injuries.append(count)    
    return injuries


def maternity_information_handler(session, time_now_year, idcard):
    """ 获取生育保险缴费记录 """

    maternity = []
    count = 0

    for year in range(time_now_year-5, time_now_year+1):
        maternity_information = session.get(maternity_url + str(year))
        if len(re.findall(ur'没有找到符合条件的个人用户信息', maternity_information.text)) == 0:
            result = etree.HTML(maternity_information.text)
            info = result.xpath('//tr')[2: -1]
            for info_item in info:
                maternity_item = {}
                item = info_item.xpath('./td/text()')
                if item[1] != u'-':
                    if len(re.findall('\d+', item[0])) == 0:
                        item.insert(0, maternity[-1]['date'])
                        count += 1
                    # 社保卡号码
                    maternity_item['socialSecurityCardNumber'] = idcard.strip()
                    # 险种类型
                    maternity_item['type_B'] = u'生育'
                    # 结算日期   
                    maternity_item['Date'] = item[0].strip()
                    # # 缴费基数    
                    # maternity_item['base'] = item[1]
                    # 单位缴费    
                    maternity_item['company_pay'] = item[2].strip()
                    # 个人缴费
                    maternity_item['personmoney'] = ''

                    maternity.append(maternity_item)
    maternity.append(count)
    return maternity


def medicalcare_information_handler(session, time_now_year, idcard):
    """ 获取医疗保险缴费记录 """

    medicalcare = []
    count = 0

    for year in range(time_now_year-5, time_now_year+1):
        medicalcare_information = session.get(medicalcare_url + str(year))
        if len(re.findall(ur'没有找到符合条件的个人用户信息', medicalcare_information.text)) == 0:
            result = etree.HTML(medicalcare_information.text)
            info = result.xpath('//tr')[2: -1]
            # print len(info)
            for info_item in info:
                medicalcare_item = {}
                item = info_item.xpath('./td/text()')
                if item[1] != u'-':
                    # 页面可能会出现补基金的情况
                    if len(re.findall('\d+', item[0])) == 0:
                        item.insert(0, medicalcare[-1]['date'])
                        count += 1
                    # 社保卡号码
                    medicalcare_item['socialSecurityCardNumber'] = idcard.strip()
                    # 险种类型
                    medicalcare_item['type_B'] = u'医疗'
                    # 缴费年月    
                    medicalcare_item['Date'] = item[0].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '').strip()
                    # # 缴费类型    
                    # medicalcare_item['type'] = item[1].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '')
                    # # 缴费基数    
                    # medicalcare_item['base'] = item[2].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '')
                    # 单位缴费    
                    medicalcare_item['company_pay'] = item[3].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '').strip()
                    # 个人缴费    
                    medicalcare_item['personmoney'] = item[4].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '').strip()
                    # # 缴费单位名称
                    # medicalcare_item['unitName'] = item[5].replace(u'\r', '').replace(u'\t', '').replace(u'\n', '')

                    medicalcare.append(medicalcare_item)

    medicalcare.append(count)
    return medicalcare