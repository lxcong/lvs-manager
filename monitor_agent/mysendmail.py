#!/usr/bin/env python
# -*- coding: utf8 -*- 
import smtplib
from email.mime.text import MIMEText

class mysendmail():
    def __init__(self,mailhost,me,tolist,subject):
        '''
        mailhost = 127.0.0.1 #邮件服务器的地址
        me = 'lvs-publish<lvs-publish@ijinshan.com>' #发送邮件人的地址标识
        tolist = ['lxcong@example.com','lxcong2@example.com']  #发送的地址列表
        subject = 'Subject'  #邮件标题
        '''
        self.mailhost = mailhost
        self.me = me
        self.tolist = tolist
        self.subject = subject
        
    def send_mail(self,content):
        msg = self.write_mail(self.me, self.tolist, self.subject, content)
        try:
            s = smtplib.SMTP()
            s.connect(self.mailhost)
            s.sendmail(self.me, self.tolist, msg.as_string())
            s.close()
            print '发送邮件成功'
            return True
        except Exception, e:
            print '发送邮件错误, case by: %s' % e
            return False
    
    def write_mail(self,sender, to_list, sub, content):
        msg = MIMEText(content, _subtype = 'html', _charset='utf-8')
        msg['Subject'] = sub
        msg['From'] = sender
        msg['To'] = ';'.join(to_list)
        return msg