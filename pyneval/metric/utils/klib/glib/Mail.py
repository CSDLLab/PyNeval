#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
* @Filename: mail.py
* @Author: Zhefeng Wang(jevons@gmail.com)
* @Created on: 2016年 04月 24日 星期日 21:37:54 CST
* @desc: function to send emails
* @history:
"""

import sys,os
from imp import reload
reload(sys)

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

def notifyMe(subject, mailto='425172133@qq.com',content=u'官万先\r\nguanwanxian@zju.edu.cn'):

    from_addr = "guanwanxian@zju.edu.cn"
    password = "64544861"

    #to_addr = "972562104@qq.com"
    to_addr = mailto
    smtp_server = "smtp.zju.edu.cn"

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = '官万先<%s>' % from_addr
    msg['To'] = mailto
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

if __name__ == "__main__":
    mailto = "972562104@qq.com"
    subject = "你好"
    content = "Hello World!"
    send_email(mailto, subject, content)
