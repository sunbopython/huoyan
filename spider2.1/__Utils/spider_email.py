#!/usr/bin/python
# -*- coding: utf-8 -*-
import smtplib
def sendMail(body, mailAddress):
    smtp_server = 'smtp.163.com'
    from_mail = 'willow0k@163.com'
    mail_pass = 'spider123456'
    to_mail = [mailAddress]
    cc_mail = ['liujingyuan@insightcredit.cn']
    from_name = 'SpiderMonitor'
    subject = u'监控'.encode('gbk')   # 以gbk编码发送，一般邮件客户端都能识别
    mail = [
        "From: %s <%s>" % (from_name, from_mail),
        "To: %s" % ','.join(to_mail),   # 转成字符串，以逗号分隔元素
        "Subject: %s" % subject,
        "Cc: %s" % ','.join(cc_mail),
        "",
        body.encode('gbk')
        ]
    msg = '\n'.join(mail)  # 这种方式先将头信息放到列表中，然后用join拼接，并以换行符分隔元素，结果就是和上面注释一样了
    try:
        s = smtplib.SMTP()
        s.connect(smtp_server, '25')
        s.login(from_mail, mail_pass)
        s.sendmail(from_mail, to_mail+cc_mail, msg)
        s.quit()
    except smtplib.SMTPException as e:
        print "Error: %s" %e
if __name__ == "__main__":
    sendMail("hello kittle! ", 'liujingyuan@insightcredit.cn')