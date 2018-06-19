#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
程序:SpiderProject
版本:1.0
作者:LiuJingYuan
日期:2017/9/5 16:22
语言:Python 2.7.13
操作:python __init__.py
'''
import json

{
    'sum_price':"",# 总价
    'first_pay':"",# 首付
    'house_type':"",# 户型
    'construction_area':"",# 建筑面积
    'unit_price':"",# 单价
    'orientation':"",# 朝向
    'floor':"",# 楼层
    'decoration':"",# 装修
    'district':"",# 小区
    'area':"",# 区域
    'contact_person':"",# 联系人
    'economic_company':"",# 经纪公司
    'phone':"",# 电话
    'build_age':"",# 建筑年代
    'elevator':"",# 有无电梯
    'property_right':"",# 产权性质
    'category':"",# 住宅类别
    'build_structure':"",# 建筑结构
    'build_category':"",# 建筑类别
    'list_time':"",# 挂牌时间
    'fang_info':"",# 房源描述
    'reference_price':"",# 参考均价
    'district_than_year':"",# 同比去年
    'district_than_month':"",# 环比上月
    'district_property_type':"",# 物业类型
    'district_property_costs':"",# 物业费用
    'district_build_type':"",# 建筑类型
    'district_build_age':"",# 建筑年代
    'district_green_rate':"",# 绿化率
    'district_volume_tate':"",# 容积率
    'district_diversion':"" # 人车分流
}


print json.dumps(a, ensure_ascii=False, indent=4)
