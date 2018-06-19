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
#   1.税务
#   2.公积金
#   3.社保
#   4.运营商
# -------------------------------------------------------------------------

class hypc_taxpayer_qualification():
    @staticmethod
    def taxpayer(identity="", taxpayer_name="", taxpayer_qname="", expiry="", taxes="", taxes_type="", unit_address=""):
        return {  # 一般纳税人资格
                    "general_taxpayer": {
                        "identity": identity,  # 纳税人识别号
                        "taxpayer_name": taxpayer_name,  # 纳税人名称
                        "taxpayer_qname": taxpayer_qname,  # 纳税人资格名称
                        "expiry": expiry  # 有效期起止日期
                    },
                    # 欠税信息
                    "owe_taxes": {
                        "taxes": taxes,  # 欠税金额
                        "taxes_type": taxes_type,  # 欠税税种
                        "unit_address": unit_address,  # 经营地址
                    }
                }



# print hypc_taxpayer_qualification.taxpayer(
#     type="hypc_taxpayer_qualification",
#     userid="shuiwu_userid",
#     identity="110106590611038",
#     taxpayer_name="北京东方披克科技有限公司",
#     taxpayer_qname="一般纳税人",
#     expiry="2012年03月08日",
#     taxes=["1203.11", "569"],
#     taxes_type=["企业所得税", "增值税"],
#     unit_address="河北省石家庄市新华区泰华街567号香格礼小区一号楼一单元901室"
# )


class hypc_accumulation_fund():
    @staticmethod
    def baseinfo(curamount="",
                 curbalance="",
                 curextract="",
                 departmentid="",
                 departmentname="",
                 idno="",
                 lastbalance="",
                 lastdate="",
                 openerunit1="",
                 openerunit2="",
                 orgid="",
                 orgname="",
                 outamount="",
                 curstatus="",
                 paytimes="",
                 paybase="",
                 pername="",
                 personalid="",
                 record="",
                 ):
        return {"baseinfo": {
                    "curamount": curamount,  # 当前余额
                    "curbalance": curbalance,  # 当前缴存余额
                    "curextract": curextract,  # 当年提取金额
                    "curstatus": curstatus,  # 用户状态
                    "departmentid": departmentid,  # 所属管理部编号
                    "departmentname": departmentname,  # 所属管理部名称
                    "idno.": idno,  # 个人登记号
                    "lastbalance": lastbalance,  # 上年结转余额
                    "lastdate": lastdate,  # 最后业务时间
                    "openerunit1":openerunit1,  # 开户单位1
                    "openerunit2": openerunit2,  # 开户单位2
                    "orgid": orgid,  # 机构登记号
                    "orgname": orgname,  # 机构名称
                    "outamount": outamount,  # 转出金额
                    "paybase":paybase,  # 缴费基数
                    "paytimes": paytimes,  # 连续缴费时间
                    "pername": pername,  # 用户姓名
                    "personalid": personalid,  # 身份证号
                },
                "record": record
            }

    @staticmethod
    def record(loan="",
               orgname="",
               trade_status="",
               abstract="",
               trade_date="",
               deal_with="",
               start_date="",
               month_balance="",
               end_date="",
               trade_type="",
               month_pay=""
               ):
        return {
                "loan": loan,  # 贷方发生额
                "orgname": orgname,  # 单位名称
                "trade_status": trade_status,  # 交易状态
                "abstract": abstract,  # 摘要
                "trade_date": trade_date,  # 交易日期
                "deal_with": deal_with,  # 办理方式
                "start_date": start_date,  # 起始日期
                "month_balance": month_balance,  # 本月余额
                "end_date": end_date,  # 终止日期
                "trade_type": trade_type,  # 业务类型
                "month_pay": month_pay,  # 公积金月缴存额
        }

# print hypc_accumulation_fund.baseinfo(record=[hypc_accumulation_fund.record(loan="hello kitty"),hypc_accumulation_fund.record()])

class hypc_phone_operator():
    @staticmethod
    def baseinfo(
                province='',
                city='',
                id_card='',
                addr='',
                level='',
                user_source='',
                starLevel='',
                state='',
                real_name='',
                phone='',
                flag='',
                open_time='',
                custsex='',
                packageName='',
                certaddr='',
                lasttime='',
                call_info=[],
                pay_info=[],
                net_info=[],
                sms_info=[]
                 ):
        return {

                "per_info": {
                    "province":province,                                # 账号归属省份
                    "city":city,                                    # 账号归属城市
                    "id_card":id_card,                                   # 身份证,
                    "addr":addr,                       # 地址
                    "level":level,                                  # 等级
                    "user_source":user_source,                   # 数据源
                    "starLevel":starLevel,                                # 账号星级
                    "state":state,                                   # 账号状态
                    "real_name":real_name,                              # 姓名
                    "phone":phone,                          # 用户手机号码
                    "flag":flag,                          # 运营商标识
                    "open_time":open_time,                       # 入网时间
                    "custsex":custsex,                              # 客户性别
                    "packageName":packageName,                        # 使用套餐
                    "certaddr":certaddr,                   # 注册地址
                    "lasttime":lasttime                         # 最近登陆时间
                },
                "call_info":call_info,
                "pay_info":pay_info,
                "net_info":net_info,
                "sms_info":sms_info
            }


    @staticmethod
    def call_info(trade_type='',
                call_time='',
                receive_phone='',
                called_home='',
                call_fee='',
                trade_time='',
                trade_addr='',
                call_type='',
                call_data=''
                ):
        return {
                "trade_type":trade_type,          #  呼叫类型
                "call_time":call_time,            #  拨打时间
                "receive_phone":receive_phone,    #  对方号码
                "called_home":called_home,        #  对方归属地
                "call_fee":call_fee,              #  通话费
                "trade_time":trade_time,          #  通话时长
                "trade_addr":trade_addr,          #  本机通话地
                "call_type":call_type,            #  通话类型
                "call_data":call_data             #  记录内容
        }

    @staticmethod
    def pay_info(charge_pay='',
                charge_paid='',
                charge_all='',
                acct_name='',
                account_info='',
                pay_date='',
                charge_discount=''
               ):
        return {
                "charge_pay":charge_pay,                    # 未付费用
                "charge_paid":charge_paid,                  # 已付费用
                "charge_all":charge_all,                    # 该月消费总额
                "acct_name":acct_name,                      # 用户名（姓名）
                "account_info":account_info,                # 账户信息
                "pay_date":pay_date,                        # 日期
                "charge_discount":charge_discount           # 可用预存款及可用赠款抵扣
        }
    @staticmethod
    def net_info(net_type='',
                net_time='',
                net_flow='',
                net_fee='',
                net_area='',
                net_business=''
                ):
        return {
                "net_type":net_type,               # 上网类型
                "net_time":net_time,               # 上网时间
                "net_flow":net_flow,               # 上网流量/KB
                "net_fee":net_fee,                 # 花费金额
                "net_area":net_area,               # 上网地区
                "net_business":net_business        # 网络业务
        }
    @staticmethod
    def sms_info(
        sms_time='',
        sms_type='',
        sms_mobile='',
        sms_style='',
        sms_fee='',
        sms_area=''
               ):
        return {
                "sms_time":sms_time,               # 起始时间
                "sms_type":sms_type,                                 # 传送方式，1为接收，2为发送
                "sms_mobile":sms_mobile,                     # 对方号码
                "sms_style":sms_style,                               # 业务类型，01为国内短信，02为国际短信
                "sms_fee":sms_fee,                               # 通话费
                "sms_area":sms_area                                # 发送地区
            }

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














class hypc_soufun():
    @staticmethod
    def baseinfo(
            sum_price="",# 总价
            first_pay="",# 首付
            house_type="",# 户型
            construction_area="",# 建筑面积
            unit_price="",# 单价
            orientation="",# 朝向
            floor="",# 楼层
            decoration="",# 装修
            district="",# 小区
            area="",# 区域
            contact_person="",# 联系人
            economic_company="",# 经纪公司
            phone="",# 电话
            build_age="",# 建筑年代
            elevator="",# 有无电梯
            property_right="",# 产权性质
            category="",# 住宅类别
            build_structure="",# 建筑结构
            build_category="",# 建筑类别
            list_time="",# 挂牌时间
            fang_info="",# 房源描述
            reference_price="",# 参考均价
            district_than_year="",# 同比去年
            district_than_month="",# 环比上月
            district_property_type="",# 物业类型
            district_property_costs="",# 物业费用
            district_build_type="",# 建筑类型
            district_build_age="",# 建筑年代
            district_green_rate="",# 绿化率
            district_volume_tate="",# 容积率
            district_diversion="" # 人车分流
    ):
        return {
            'sum_price':sum_price,                         
            'first_pay':first_pay,                         
            'house_type':house_type,                     
            'construction_area':construction_area,
            'unit_price':unit_price,
            'orientation':orientation,
            'floor':floor,
            'decoration':decoration,
            'district':district,
            'area':area,
            'contact_person':contact_person,
            'economic_company':economic_company,
            'phone':phone,
            'build_age':build_age,
            'elevator':elevator,
            'property_right':property_right,
            'category':category,
            'build_structure':build_structure,
            'build_category':build_category,
            'list_time':list_time,
            'fang_info':fang_info,
            'reference_price':reference_price,
            'district_than_year':district_than_year,
            'district_than_month':district_than_month,
            'district_property_type':district_property_type,
            'district_property_costs':district_property_costs,
            'district_build_type':district_build_type,
            'district_build_age':district_build_age,
            'district_green_rate':district_green_rate,
            'district_volume_tate':district_volume_tate,
            'district_diversion':district_diversion
        }

class hypc_translate():
    @staticmethod
    def baseinfo(
        project_name = '', # 项目名称
        alias_name = '', # 别名
        positioning = '', #定位
        company_name = '', # 公司名称
        project_id = '', #项目编号
        counts = '', # 套数
        area = '', # 面积
        marketable_area = '', # 可销售面积
        sales_area = '', #已销售面积
        has_sold_area = '', #已销售非住宅面积
        number_sellable_households = '', # 可售户数
        has_sold_number = '', # 已销售户数
        has_sold_households = '', # 已销售非住宅户数
        permit_number = '', #    许可证号
        permission_date = '', # 许可日期
        sales_address = '', # 售楼地址
        sales_call = '', # 售楼电话
        number_buildings = '', # 幢数
        construction_area = '', # 建筑面积
        opening_time = '', # 开盘时间
        supervision_account = '', # 资金监管账户
        document_authority = '', # 证件发布机构
        financial_bank = '', # 资金监管银行
        bulding = []
    ):
        return {
            'project_name' : project_name,
            'alias_name' : alias_name, # 别名
            'positioning' : positioning, #定位
            'company_name' : company_name, # 公司名称
            'project_id' : project_id, #项目编号
            'counts' : counts, # 套数
            'area' : area, # 面积
            'marketable_area' : marketable_area, # 可销售面积
            'sales_area' : sales_area, #已销售面积
            'has_sold_area' : has_sold_area, #已销售非住宅面积
            'number_sellable_households' : number_sellable_households, # 可售户数
            'has_sold_number' : has_sold_number, # 已销售户数
            'has_sold_households' : has_sold_households, # 已销售非住宅户数
            'permit_number' : permit_number, #    许可证号
            'permission_date' : permission_date, # 许可日期
            'sales_address' : sales_address, # 售楼地址
            'sales_call' : sales_call, # 售楼电话
            'number_buildings' : number_buildings, # 幢数
            'construction_area' : construction_area, # 建筑面积
            'opening_time' : opening_time, # 开盘时间
            'supervision_account' : supervision_account, # 资金监管账户
            'document_authority' : document_authority, # 证件发布机构
            'financial_bank' :financial_bank, # 资金监管银行
            'bulding' : bulding      # 楼栋信息
        }

    @staticmethod
    def detail_building(
        num_floors = '', # 楼号
        total_floors = '', # 总层数 
        total_houses = '', # 总户数
        permitted_households = '', # 许可户数
        has_sold_number_households = '', # 已销售户数
        has_sold_residential_households = '', # 已销售非住宅户数
        wangqian_nubm = ''     # 已网签门户
    ):
        return {
            'num_floors' : num_floors, 
            'total_floors' : total_floors,
            'total_houses' : total_houses,
            'permitted_households' : permitted_households,
            'has_sold_number_households' : has_sold_number_households,
            'has_sold_residential_households' : has_sold_residential_households,
            'wangqian_nubm' : wangqian_nubm,
        }

class hypc_enterprise_credit_ningbo():
    @staticmethod
    def baseinfo(
            branch_dept_code='',
            company_name='',
            common_type='',
            person='',
            register_money='',
            establish_date='',
            address='',
            start_date='',
            end_time='',
            register_dept='',
            verify_date='',
            common_range='',
            Shareholder_info=[],
            Change_info=[],
            key_person_info=[],
            Branch_info=[],
            Xingzheng_info=[],
            sifa_info=[],
            bnormal_info=[],
            evaluation_info=[],
            honor_info = [],
            license_info=[]
                 ):
        return {
            "Base_info":{
                "branch_dept_code":branch_dept_code,   # 统一社会信用代码                          # 统一社会信用代码/注册号
                "company_name":company_name,           # 名称
                "common_type":common_type,             # 类型
                "person":person,                       # 法定代表人
                "register_money":register_money,       # 注册资本
                "establish_date":establish_date,       # 成立日期
                "address":address,                     # 住所
                "start_date":start_date,               # 营业期限自
                "end_time":end_time,                   # 营业期限至
                "register_dept":register_dept,         # 登记机关
                "verify_date":verify_date,             # 核准日期
                "common_range":common_range,           # 经营范围
            },
            'Shareholder_info':Shareholder_info,   # 股东信息
            'Change_info':Change_info,             # 变更信息
            'key_person_info':key_person_info,     # 主要人员信息
            'Branch_info':Branch_info,              # 分支机构信息
            'Xingzheng_info':Xingzheng_info,       # 行政处罚信息
            'sifa_info':sifa_info,                #司法信息
            'bnormal_info':bnormal_info,          #异常信息
            'evaluation_info':evaluation_info,    #评价信息
            'honor_info':honor_info,              #荣誉信息
            'license_info':license_info
        }

    @staticmethod
    def Shareholder_info(
                shareholder_type='',         #股东类型
                shareholder='',              #股东
                card_type='',                # 证照/证件类型
                card_num='',                 # 证照/证件号码
                detail_info=''               # 详情
               ):
        return {
                "shareholder_type":shareholder_type,
                "shareholder":shareholder,
                "card_type":card_type, 
                "card_num":card_num,
                "detail_info":detail_info
        }

    @staticmethod
    def honor_info(   # 荣誉信息
            date_approval='', #认定日期
            validity_period='', # 有效期限
            defense_level='', # 守重等级
            named_authority='', # 命名机关
            date_canceled='', # 被取消日期
            rejected_reason='', # 被取消原因
        ):
        return {
            "date_approval":date_approval,
            "validity_period":validity_period,
            "defense_level":defense_level,
            "named_authority":named_authority,
            "date_canceled":date_canceled,
            "rejected_reason":rejected_reason,
        }

    @staticmethod
    def Change_info(
                change_active='',            # 变更事项
                change_content_pr='',        # 变更前内容
                change_content_after='',     # 变更后内容
                change_date='',              # 变更日期
               ):
        return {
                "change_active":change_active,
                "change_content_pr":change_content_pr,
                "change_content_after":change_content_after,
                "change_date":change_date,
        }

    @staticmethod
    def key_person_info(
                person_name='',                 # 主要人员姓名
                person_position='',             # 主要人员职位    
               ):
        return {
                "person_name":person_name,
                "person_position":person_position,   
        }

    @staticmethod
    def Branch_info(
                common_code='',             # 注册号
                knowledge_name='',          # 名称
                branch_dept_register='',    # 登记机关    
               ):
        return {
                "common_code":common_code,                      
                "knowledge_name":knowledge_name,
                "branch_dept_register":branch_dept_register,    
        }

    @staticmethod
    def license_info(
            name_permit='',    #许可证名称
            permit_number='',#许可证号
            effective_date='', #有效日期起
            valid_until='', #有效日期至
            issuing_authority='', #发证机关
            date_issue='', #发证日期
        ):
        return {
            "name_permit":name_permit,
            "permit_number":permit_number,
            "effective_date":effective_date,
            "valid_until":valid_until,
            "issuing_authority":issuing_authority,
            "date_issue":date_issue,
        }

    @staticmethod
    def xing_info(
            com_per_name = '',
            execution_number = '',
            type_violation = '',
            made_penalty = '',
            penalty_content = '',
            penalty_date = '',  
            ):
        return {
            "com_per_name" : com_per_name,#违法企业名称或违法自然人名称
            "execution_number" : execution_number,# 行政处决文号 
            "type_violation" : type_violation,#违法行为类型   
            "made_penalty" : made_penalty,#作出处罚决定机关名称    
            "penalty_content" : penalty_content,#  处罚内容 
            "penalty_date" : penalty_date #作出行政处罚决定日期
        }
    @staticmethod
    def sifa_info(
        case_number = '',        #案号
        execution_basis = '',        #执行依据
        nature_case = '',        #案件性质
        executive_content = '',        #执行内容
        amount_subject = '',        #标的金额
        organization_code = '',        #组织机构代码
        legal_representative = ''        #法定代表人
        ):
        return {
            "case_number" : case_number,
            "execution_basis" : execution_basis,
            "nature_case" : nature_case,
            "executive_content" : executive_content,
            "amount_subject" : amount_subject,
            "organization_code" : organization_code,
            "legal_representative" : legal_representative,
        }

    @staticmethod
    def bnormal_info(
        include_date = '',#列入日期
        decision_included = '',# 做出决定机关(列入)
        remove_date = '',# 移出日期
        decision_listed = '',# 作出决定机关(列出)
        ):
        return {
            "include_date" : include_date,              #列入信息
            "decision_included" : decision_included,    # 做出决定机关(列入)
            "remove_date" : remove_date,                # 移出日期
            "decision_listed" : decision_listed,        # 作出决定机关(列出)
        }



class craw_taxpayer_qualification():
    @staticmethod
    def baseinfo(
            sales_name = '',   # 销售方名字【1】
            purchaser_taxpayer_id = '',   # 购买方纳税人识别号【4】
            purchaser_bank_account = '',   # 购买方开户行级账号【5】
            sales_taxpayer_id = '',   # 销售方纳税识别号【6】
            sales_add_phone = '',   # 销售方地址电话【7】
            sales_bank_account = '',   # 销售方开户行及账号【9】
            purchaser_add_phone = '',   # 购买方地址电话
            purchaser_name = '',   # 购买方名称
            service_name = '',   # 服务名称
            specification = '',   # 规格型号
            unit = '',    #单位
            quantity = '',    #数量
            unit_price = '',    #单价
            amount = '',    #金额
            tax_rate = '',    #税率
            tax = '',    #税额
            invoice_code = '',      # 发票代码
            invoice_number = '',      # 发票号码
            billing_date = '',      # 开票日期
            check_number = '',      # 校验号
            machine_code = '',      # 机器码
            before_tax = '',      # 税前金额
            total_tax = '',      # 纳税合计

        ):
            return {
                'sales_name' : sales_name,
                'purchaser_taxpayer_id' : purchaser_taxpayer_id,
                'purchaser_bank_account' : purchaser_bank_account,
                'sales_taxpayer_id' : sales_taxpayer_id,
                'sales_add_phone' : sales_add_phone,
                'sales_bank_account' : sales_bank_account,
                'purchaser_add_phone' : purchaser_add_phone,
                'purchaser_name' : purchaser_name,
                'service_name' : service_name,
                'specification' : specification,
                'unit' : unit,
                'quantity' : quantity,
                'unit_price' : unit_price,
                'amount' : amount,
                'tax_rate' : tax_rate,
                'tax' : tax,
                'invoice_code' : invoice_code,      # 发票代码
                'invoice_number' : invoice_number,      # 发票号码
                'billing_date' : billing_date,      # 开票日期
                'check_number' : check_number,      # 校验号
                'machine_code' : machine_code,      # 机器码
                'total_tax' : total_tax,
                'before_tax' : before_tax,    #税前金额
            }



class craw_dishonest():
    @staticmethod
    def gaofa(
            unperformPart="",  # 被执行人的未履行部分
            shixinid="",  # 失信人ID
            sexy="",  # 性别
            regDate="",  # 立案时间
            publishDate="",  # 发布时间
            performedPart="",  # 被执行人的履行部分
            performance="",  # 被执行人的履行情况
            partyTypeName="",  # 类型号
            iname="",  # 被执行人姓名/名称
            disruptTypeName="",  # 失信被执行人行为具体情形
            courtName="",  # 执行法院
            caseCode="",  # 案号
            cardNum="",  # 身份证号码/组织机构代码
            businessEntity="",  # 法定代表人或负责人姓名
            areaName="",  # 省份
            age="",  # 年龄（企业默认为0）
            duty = "",  # 生效法律文书确定的义务
            gistId = "",  # 执行依据文号
            gistUnit = "",  # 做出执行依据单位
    ):
        return {
         "unperformPart": unperformPart,
         "shixinid": shixinid,
         "sexy": sexy,
         "regDate": regDate,
         "publishDate": publishDate,
         "performedPart": performedPart,
         "performance": performance,
         "partyTypeName": partyTypeName,
         "iname": iname,
         "disruptTypeName": disruptTypeName,
         "courtName": courtName,
         "caseCode": caseCode,
         "cardNum": cardNum,
         "businessEntity": businessEntity,
         "areaName": areaName,
         "age": age,
         "duty" : duty,
         "gistId" : gistId,
         "gistUnit" : gistUnit,
        }
#国家企业网
class hypc_enterprise_credit():
    @staticmethod
    def enterprise_info(
            base_info={},
            admin_penalty_info=[],
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
    ):
        return {
            "base_info":base_info,
            "admin_penalty_info":admin_penalty_info,
            "operate_abnormal_info":operate_abnormal_info,
            "key_person_info":key_person_info,
            "change_info":change_info,
            "check_info":check_info,
            "chattel_info":chattel_info,
            "branch_info":branch_info,
            "equity_pledged_info":equity_pledged_info,
            "Shareholder_info":Shareholder_info,
            "judicial_assist_info":judicial_assist_info,
            "knowledge_info":knowledge_info,
            "brand_info":brand_info,
            "annual_shareholder_info":annual_shareholder_info,
            "annual_info":annual_info,
        }

    @staticmethod
    def base_info(  #基础信息
            company_name="",  # 企业名称
            old_name="",  # 曾用名称
            eng_name="",  # 英文名称
            register_status="",  # 企业状态
            registration_number="",  # 工商注册号
            organization_code="",  # 组织机构代码
            branch_dept_code="",  # 统一社会信用代码
            common_type="",  # 公司类型
            person="",  # 法定代表人
            industry="",  # 所属行业
            register_money="",  # 注册资本
            paidup_capital="",  # 实收资本
            end_time="",  # 营业期限自
            start_date="",  # 营业期限至
            verify_date="",  # 发照日期
            register_dept="",  # 登记机关
            register_addr="",  # 注册地址
            zip_code="",  # 邮编
            address="",  # 经营地址
            phone="",  # 移动电话
            telephone="",  # 固定电话
            fax="",  # 传真号码
            website="",  # 网址
            establish_date="",  # 成立日期
            common_range="",  # 经营范围
            email=""  # 电子邮箱
    ):
        return {"company_name":company_name,	#企业名称
"old_name":old_name,	#曾用名称
"eng_name":eng_name,	#英文名称
"register_status":register_status,	#企业状态
"registration_number":registration_number,	#工商注册号
"organization_code":organization_code,	#组织机构代码
"branch_dept_code":branch_dept_code,	#统一社会信用代码
"common_type":common_type,	#公司类型
"person":person,	#法定代表人
"industry":industry,	#所属行业
"register_money":register_money,	#注册资本
"paidup_capital":paidup_capital,	#实收资本
"end_time":end_time,	#营业期限自
"start_date":start_date,	#营业期限至
"verify_date":verify_date,	#发照日期
"register_dept":register_dept,	#登记机关
"register_addr":register_addr,	#注册地址
"zip_code":zip_code,	#邮编
"address":address,	#经营地址
"phone":phone,	#移动电话
"telephone":telephone,	#固定电话
"fax":fax,	#传真号码
"website":website,	#网址
"establish_date":establish_date,	#成立日期
"common_range":common_range,	#经营范围
"email":email,	#电子邮箱
}

    @staticmethod
    def admin_penalty_info( #行政处罚信息
            reference_number="",  # 决定书文号
            illegal_type="",  # 违法行为类型
            content="",  # 行政处罚内容
            judgmenter_name="",  # 决定机关名称
            judgment_date="",  # 处罚决定日期
            publish_date="",  # 公示日期
            detail=""  # 详情
    ):
        return {"reference_number":reference_number,	#决定书文号
"illegal_type":illegal_type,	#违法行为类型
"content":content,	#行政处罚内容
"judgmenter_name":judgmenter_name,	#决定机关名称
"judgment_date":judgment_date,	#处罚决定日期
"publish_date":publish_date,	#公示日期
"detail":detail,	#详情
}

    @staticmethod
    def operate_abnormal_info(  #列入经营异常名录信息
            run_anomaly_reason="",  # 列入经营异常名录原因
            in_date="",  # 列入日期
            actuator_in="",  # 作出决定机关(列入)
            out_reason="",  # 移出经营异常名录原因
            out_date="",  # 移出日期
            actuator_out=""  # 作出决定机关(移出)
    ):
        return {"run_anomaly_reason":run_anomaly_reason,	#列入经营异常名录原因
"in_date":in_date,	#列入日期
"actuator_in":actuator_in,	#作出决定机关(列入)
"out_reason":out_reason,	#移出经营异常名录原因
"out_date":out_date,	#移出日期
"actuator_out":actuator_out,	#作出决定机关(移出)
}

    @staticmethod
    def key_person_info(   #主要人员信息
            person_position="",  # 主要人员职位
            person_name="" # 主要人员姓名
    ):
        return {
            "person_position":person_position,	#主要人员职位
            "person_name":person_name,	#主要人员姓名
        }

    @staticmethod
    def change_info( # 变更信息
            change_active="",  # 变更事项
            change_content_pr="",  # 变更前内容
            change_content_after="",  # 变更后内容
            change_date="",  # 变更日期
    ):
        return {"change_active":change_active,	#变更事项
"change_content_pr":change_content_pr,	#变更前内容
"change_content_after":change_content_after,	#变更后内容
"change_date":change_date,	#变更日期
}

    @staticmethod
    def check_info(  #抽查检查结果信息
            actuator_check="",  # 检查实施机关
            check_type="",  # 类型
            check_date="",  # 日期
            check_result="",  # 结果
    ):
        return {"actuator_check":actuator_check,	#检查实施机关
"check_type":check_type,	#类型
"check_date":check_date,	#日期
"check_result":check_result,	#结果
}

    @staticmethod
    def chattel_info(      #动产抵抵押登记信息
            chattel_reg_no="",  # 登记编号
            chattel_reg_date="",  # 登记日期
            chattel_organ_name="",  # 登记机关
            chattel_loan_amount="",  # 被担保债权数额
            chattel_status="",  # 状态
            chattel_pub_date="",  # 公示日期
            detail="",  # 详情
    ):
        return {"chattel_reg_no":chattel_reg_no,	#登记编号
"chattel_reg_date":chattel_reg_date,	#登记日期
"chattel_organ_name":chattel_organ_name,	#登记机关
"chattel_loan_amount":chattel_loan_amount,	#被担保债权数额
"chattel_status":chattel_status,	#状态
"chattel_pub_date":chattel_pub_date,	#公示日期
"detail":detail,	#详情
}

    @staticmethod
    def branch_info(  # 分支机构信息
            branch_name="",  # 名称
            branch_reg_no="",  # 注册号
            branch_reg_organ="",  # 登记机关
    ):
        return {"branch_name":branch_name,	#名称
"branch_reg_no":branch_reg_no,	#注册号
"branch_reg_organ":branch_reg_organ,	#登记机关
}

    @staticmethod
    def equity_pledged_info(  # 股权出质登记信息
            equity_pledged_no="",  # 登记编号
            equity_pledged_pledgor="",  # 出质人
            equity_pledged_idcard="",  # 证照/证件号码
            equity_pledged_amount="",  # 出质股权数额
            equity_pledged_pawnee="",  # 质权人
            equity_pledged_reg_date="",  # 股权出质设立登记日期
            equity_pledged_status="",  # 状态
            equity_pledged_pub_date="",  # 公示日期
            detail="",  # 详情

    ):
        return {"equity_pledged_no":equity_pledged_no,	#登记编号
"equity_pledged_pledgor":equity_pledged_pledgor,	#出质人
"equity_pledged_idcard":equity_pledged_idcard,	#证照/证件号码
"equity_pledged_amount":equity_pledged_amount,	#出质股权数额
"equity_pledged_pawnee":equity_pledged_pawnee,	#质权人
"equity_pledged_reg_date":equity_pledged_reg_date,	#股权出质设立登记日期
"equity_pledged_status":equity_pledged_status,	#状态
"equity_pledged_pub_date":equity_pledged_pub_date,	#公示日期
"detail":detail,	#详情
}


    @staticmethod
    def Shareholder_info( # 股东发起人及出资信息
            shareholder="",  # 股东名称
            card_type="",  # 证照/证件类型
            card_num="",  # 证照/证件号码
            shareholder_type="",  # 股东类型
            detail="",  # 详情
            amount="",  # 出资额
            ratio="",  # 出资比例
    ):
        return {"shareholder":shareholder,	#股东名称
"card_type":card_type,	#证照/证件类型
"card_num":card_num,	#证照/证件号码
"shareholder_type":shareholder_type,	#股东类型
"detail":detail,	#详情
"amount":amount,	#出资额
"ratio":ratio,	#出资比例
}


    @staticmethod
    def judicial_assist_info( # 司法协助信息
            executed="",  # 被执行人
            amount="",  # 股权数额
            court="",  # 执行法院
            reference_number="",  # 执行通知书文号
            type="",  # 类型|状态
            detail="",  # 详情
    ):
        return {"executed":executed,	#被执行人
"amount":amount,	#股权数额
"court":court,	#执行法院
"reference_number":reference_number,	#执行通知书文号
"type":type,	#类型|状态
"detail":detail,	#详情
}

    @staticmethod
    def knowledge_info( #知识产权出质登记信息
            knowledge_code="",  # 知识产权登记证号
            knowledge_name="",  # 名称
            knowledge_type="",  # 种类
            knowledge_person="",  # 出质人名称
            knowledge_personed="",  # 质权人名称
            knowledge_date="",  # 质权登记期限
            knowledge_state="",  # 状态
            knowledge_show_date="",  # 公示日期
            detail_info="",  # 详情
    ):
        return {"knowledge_code":knowledge_code,	#知识产权登记证号
"knowledge_name":knowledge_name,	#名称
"knowledge_type":knowledge_type,	#种类
"knowledge_person":knowledge_person,	#出质人名称
"knowledge_personed":knowledge_personed,	#质权人名称
"knowledge_date":knowledge_date,	#质权登记期限
"knowledge_state":knowledge_state,	#状态
"knowledge_show_date":knowledge_show_date,	#公示日期
"detail_info":detail_info,	#详情
}

    @staticmethod
    def brand_info( # 商标注册信息
            brand_number="",  # 商标注册号
            type="",  # 类别
            pub_date="",  # 注册公告日期
    ):
        return {"brand_number":brand_number,	#商标注册号
"type":type,	#类别
"pub_date":pub_date,	#注册公告日期
}

    @staticmethod
    def annual_shareholder_info( # 股东及出资信息
            shareholder="",  # 股东姓名1
            contributive_amount="",  # 认缴出资额（万元）5
            contributive_date="",  # 认缴出资时间6
            contributive_way="",  # 认缴出资方式4
            pay_amount="",  # 实缴出资额（万元）10
            pay_date="",  # 实缴出资时间11
            pay_way="",  # 实缴出资方式9
    ):
        return {"shareholder":shareholder,	#股东姓名
"contributive_amount":contributive_amount,	#认缴出资额（万元）
"contributive_date":contributive_date,	#认缴出资时间
"contributive_way":contributive_way,	#认缴出资方式
"pay_amount":pay_amount,	#实缴出资额（万元）
"pay_date":pay_date,	#实缴出资时间
"pay_way":pay_way,	#实缴出资方式
}
    @staticmethod
    def annual_info( # 企业年报信息
            pub_date="",  # 发布日期
            general_assets="",  # 资产总额
            total_liability="",  # 负债合计
            total_equity="",  # 所有者权益合计
            gross_revenue="",  # 营业总收入
            main_business_income="",  # 主营业务收入
            total_profit="",  # 利润总额
            retained_profit="",  # 净利润
            pay_taxes="",  # 纳税总额
            Contact_info="",  # 联系信息
            annual_year="",  # 年报年份
            mailing_address="",  # 企业通信地址
            zip_code="",  # 邮政编码
            phone="",  # 企业联系电话
            email="",  # 电子邮箱
            run_status="",  # 企业经营状态
            employee_number="",  # 从业人数
            online_store_exist="",  # 是否有网站或网店
            online_store_type="",  # 类型 （网站/网店）
            online_store_name="",  # 名称 （网站/网店）
            website="",  # 网址
    ):
        return {"pub_date":pub_date,	#发布日期
"general_assets":general_assets,	#资产总额
"total_liability":total_liability,	#负债合计
"total_equity":total_equity,	#所有者权益合计
"gross_revenue":gross_revenue,	#营业总收入
"main_business_income":main_business_income,	#主营业务收入
"total_profit":total_profit,	#利润总额
"retained_profit":retained_profit,	#净利润
"pay_taxes":pay_taxes,	#纳税总额
"Contact_info":Contact_info,	#联系信息
"annual_year":annual_year,	#年报年份
"mailing_address":mailing_address,	#企业通信地址
"zip_code":zip_code,	#邮政编码
"phone":phone,	#企业联系电话
"email":email,	#电子邮箱
"run_status":run_status,	#企业经营状态
"employee_number":employee_number,	#从业人数
"online_store_exist":online_store_exist,	#是否有网站或网店
"online_store_type":online_store_type,	#类型 （网站/网店）
"online_store_name":online_store_name,	#名称 （网站/网店）
"website":website,	#网址
}
