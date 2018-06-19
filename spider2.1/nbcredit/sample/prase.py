#coding=utf8
import os
import re
from lxml import etree

with open('detail1.html', 'r+') as f:
	file = f.read()
	print file
detaill = etree.HTML(file)
# person = detaill.xpath("//*[@class='form-box']/table[1]/tbody/tr[3]/td[2]/text()")
# person_re = re.compile(r'<!-- 企业类型4521 普通合伙企业   4522 有限合伙企业 -->[\s]*(.*)[\s]*</td>')
person_re = re.compile(r'法定代表人 </th> [\s]* <td> (.*) </td> ')
person = person_re.findall(file)[0]

print person