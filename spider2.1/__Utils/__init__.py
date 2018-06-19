#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# -------------------------------------------------------------------------
# 程序：#HuoYan
# 版本：1.0
# 作者：LiuJingYuan
# 日期：2017/9/22 2:25
# 语言：Python 2.7.13
# 操作：python standFormat.py
# 功能：
#
# -------------------------------------------------------------------------
# coding:utf-8
"""
python 2.7
社保 数据字段模板
"""

class hypc_social_insurance():
    @staticmethod
    def baseinfo(
            birthday="",  # 出生日期
            gender="",  # 性别
            nationalities="",  # 民族
            culture="",  # 文化程度
            work_data="",  # 参加工作日期
            person_name="",  # 姓名
            personalid="",  # 公民身份证号码（社会保障号码）
            id_number="",  # 证件号码
            id_type="",  # 证件类型
            foreign_permits_id="",  # 外国人居留证号码
            foreign_id_type="",  # 外国人证件类型
            foreign_id_number="",  # 外国人证件号码
            passport_number="",  # 护照号码
            account="",  # 户口性质
            account_address="",  # 户口所在地
            account_add_zip="",  # 户口所在地邮编
            home_address="",  # 居住地址
            home_add_zip="",  # 居住地邮编
            region="",  # 国家/地区
            get_bill="",  # 获取对账单方式
            person_email="",  # 电子邮件地址
            bill_email="",  # 对账单邮箱
            bill_address="",  # 邮寄社会保险对账单地址
            bank_name="",  # 委托代发银行名称
            bank_number="",  # 委托代发银行账号
            retire_date="",  # 离退休日期
            retire_type="",  # 离退休类别
            wages="",  # 申报月均工资收入
            organization_code="",  # 组织机构代码
            unit_name="",  # 单位名称
            telephone="",  # 参保人电话
            phone="",  # 参保人手机
            special_disease="",  # 是否患有特殊疾病
            medical_institution_1="",  # 定点医疗机构1
            medical_institution_2="",  # 定点医疗机构2
            medical_institution_3="",  # 定点医疗机构3
            medical_institution_4="",  # 定点医疗机构4
            medical_institution_5="",  # 定点医疗机构5
            deposit_base="",  # 缴存基数
    ):
        return {
            "birthday": birthday,  # 出生日期
            "gender": gender,  # 性别
            "nationalities": nationalities,  # 民族
            "culture": culture,  # 文化程度
            "work_data": work_data,  # 参加工作日期
            "person_name": person_name,  # 姓名
            "personalid": personalid,  # 公民身份证号码（社会保障号码）
            "id_number": id_number,  # 证件号码
            "id_type": id_type,  # 证件类型
            "foreign_permits_id": foreign_permits_id,  # 外国人居留证号码
            "foreign_id_type": foreign_id_type,  # 外国人证件类型
            "foreign_id_number": foreign_id_number,  # 外国人证件号码
            "passport_number": passport_number,  # 护照号码
            "account": account,  # 户口性质
            "account_address": account_address,  # 户口所在地
            "account_add_zip": account_add_zip,  # 户口所在地邮编
            "home_address": home_address,  # 居住地址
            "home_add_zip": home_add_zip,  # 居住地邮编
            "region": region,  # 国家/地区
            "get_bill": get_bill,  # 获取对账单方式
            "person_email": person_email,  # 电子邮件地址
            "bill_email": bill_email,  # 对账单邮箱
            "bill_address": bill_address,  # 邮寄社会保险对账单地址
            "bank_name": bank_name,  # 委托代发银行名称
            "bank_number": bank_number,  # 委托代发银行账号
            "retire_date": retire_date,  # 离退休日期
            "retire_type": retire_type,  # 离退休类别
            "wages": wages,  # 申报月均工资收入
            "organization_code": organization_code,  # 组织机构代码
            "unit_name": unit_name,  # 单位名称
            "telephone": telephone,  # 参保人电话
            "phone": phone,  # 参保人手机
            "special_disease": special_disease,  # 是否患有特殊疾病
            "medical_institution_1": medical_institution_1,  # 定点医疗机构1
            "medical_institution_2": medical_institution_2,  # 定点医疗机构2
            "medical_institution_3": medical_institution_3,  # 定点医疗机构3
            "medical_institution_4": medical_institution_4,  # 定点医疗机构4
            "medical_institution_5": medical_institution_5,  # 定点医疗机构5
            "deposit_base": deposit_base,  # 缴存基数
        }

if __name__ == '__main__':
    result_json = hypc_social_insurance().baseinfo(deposit_base='500')
    print result_json