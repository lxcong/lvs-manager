#!/usr/bin/python 
# -*- coding: utf8 -*- 

import datetime
import json
import logging
import os
import re
import shelve
import sys
import time

import yaml

from mysendmail import mysendmail
import requests
import Queue
import threading  

job_queue = Queue.Queue(0) 

cur_dir = os.path.dirname(os.path.abspath(__file__))
config = yaml.load(open(os.path.join(cur_dir,'config.yaml')))
data_dir = os.path.join(cur_dir,'data/')
alert_rs_status_file = os.path.join(data_dir,'alert_rs_status.dbm')
alert_service_status_file = os.path.join(data_dir,'alert_service_status.dbm')

class Mythread(threading.Thread):
    def __init__(self,input):
        self.jobq = input
        self.lvs_alert_api_url = config['lvs_cluster_alert_api']
        self.date = self.gettoday()
        threading.Thread.__init__(self)
        
    def run(self):
        '''
        Get a job and process it
        '''
        while True:
            time.sleep(1)
            if self.jobq.qsize() > 0:
                job = self.jobq.get()
                self._process_job(job)
    
    def _process_job(self,job):
        job_type = job['job_type']
        if job_type == 'run_rs_is_enable_action':
            self.run_rs_is_enable_action(job)
        elif job_type == 'run_rs_is_disable_action':
            self.run_rs_is_disable_action(job)
        elif job_type == 'run_service_is_enable_action':
            self.run_service_is_enable_action(job)
        elif job_type == 'run_service_is_disable_action':
            self.run_service_is_disable_action(job)
    
    def run_rs_is_enable_action(self,job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']
        rs = job['rs']
        #从info.yaml获取信息
        alert_type = "rs_is_up"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' % (i['vip'],i['port']) for i in vip_dict['vip_group']]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None
        status = 'enable'
        message = u'后端服务器:%s 访问成功，已从集群列表中恢复' % rs
        logging.info(u'RS恢复 (业务:%s,虚拟IP:%s,真实IP:%s)' %(descript,vip,rs))
        #判断rs现在的状态,如果为disable则置为enable且执行下面步骤,如果为enable则不管
        rs_key = '%s_%s' % (vip_instance,rs)
        rs_status = self.search_rs_or_service_status(rs_key)
        #把状态置为enable
        self.add_rs_or_service_status(rs_key,'enable')
        if rs_status == 'disable':
            #把信息post给平台
            time_now = self.timestampnow()
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)
            
            #sendmail
            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']
            mail_subject = u'LVS恢复报警 (业务:%s,虚拟IP:%s,真实IP:%s)' %(descript,vip,rs)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'rs:%s is enable, start sendmail' % rs
            handler_mail.send_mail(content)
            
    
    def run_rs_is_disable_action(self,job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']
        rs = job['rs']
        #从info.yaml获取信息
        alert_type = "rs_is_down"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' % (i['vip'],i['port']) for i in vip_dict['vip_group']]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None
        status = 'disable'
        message = u'后端服务器:%s 无法访问，已从集群列表剔除' % rs
        logging.info(u'RS掉线 (业务:%s,虚拟IP:%s,真实IP:%s)' %(descript,vip,rs))
        #判断rs现在的状态,如果为enable则置为disable且执行下面步骤,如果为disable则不管
        rs_key = '%s_%s' % (vip_instance,rs)
        rs_status = self.search_rs_or_service_status(rs_key)
        #把状态置为disable
        self.add_rs_or_service_status(rs_key,'disable')
        if rs_status == 'enable' or rs_status == 'pending':
            #把信息post给平台
            time_now = self.timestampnow()
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)
            
            #sendmail
            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']
            mail_subject = u'LVS掉线报警 (业务:%s,虚拟IP:%s,真实IP:%s)' %(descript,vip,rs)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'rs:%s is down, start sendmail' % rs
            handler_mail.send_mail(content)
    
    def run_service_is_disable_action(self,job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']
        #从info.yaml获取信息
        alert_type = "service_is_down"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        rs = 'ALL'
        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' % (i['vip'],i['port']) for i in vip_dict['vip_group']]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None
        status = 'disable'
        message = u'严重!! 业务:%s 由于没有真实机器可用，已无法提供服务. VIP:%s' %(descript,vip)
        logging.info(u'严重!! 业务:%s 由于没有真实机器可用，已无法提供服务. VIP:%s' %(descript,vip))
        #判断service现在的状态,如果为enable则置为disable且执行下面步骤,如果为disable则不管
        service_key = '%s_service' % (vip_instance)
        service_status = self.search_rs_or_service_status(service_key)
        #把状态置为disable
        self.add_rs_or_service_status(service_key,'disable')
        if service_status == 'enable' or service_status == 'pending':
            #把信息post给平台
            time_now = self.timestampnow()
            print 'postdata'
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)
            
            #sendmail
            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']
            mail_subject = u'严重！LVS业务IP掉线报警 (业务:%s,虚拟IP:%s)' %(descript,vip)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'service:%s is down, start sendmail' % vip_instance
            handler_mail.send_mail(content)
    
    def run_service_is_enable_action(self,job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']
        #从info.yaml获取信息
        alert_type = "service_is_up"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        rs = 'ALL'
        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' % (i['vip'],i['port']) for i in vip_dict['vip_group']]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None
        status = 'enable'
        message = u'业务:%s 已经恢复. VIP:%s' %(descript,vip)
        logging.info(u'业务:%s 已经恢复. VIP:%s' %(descript,vip))
        #判断service现在的状态,如果为disable则置为enable且执行下面步骤,如果为enable则不管
        service_key = '%s_service' % (vip_instance)
        service_status = self.search_rs_or_service_status(service_key)
        #把状态置为enable
        self.add_rs_or_service_status(service_key,'enable')
        if service_status == 'disable':
            #把信息post给平台
            time_now = self.timestampnow()
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)
            
            #sendmail
            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']
            mail_subject = u'LVS业务IP恢复报警 (业务:%s,虚拟IP:%s)' %(descript,vip)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'service:%s is up, start sendmail' % vip_instance
            handler_mail.send_mail(content)
    
    
    def timestampnow(self):
        return time.time()
    
    def gettoday(self):
        dt = datetime.date.today()
        return dt.strftime('%Y-%m-%d')
    
    def add_rs_or_service_status(self,key,value):
        db = shelve.open(alert_rs_status_file,'c')
        db[str(key)] = value
        db.close()
    
    def search_rs_or_service_status(self,key):
        db = shelve.open(alert_rs_status_file,'c')
        if key in db:
            return db[key]
        else:
            return 'pending'
        db.close()
    
    def get_info_yaml(self):
        infoyaml = yaml.load(open(config['info_yaml_file']))
        return infoyaml
    
    def post_alert_message_to_api(self,cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time):
        url = self.lvs_alert_api_url
        data = {"cluster_id":cluster_id,"lb_id":lb_id,"area":area,"descript":descript,"owners":owners,"rs":rs,"status":status,"message":message,"alert_type":alert_type,"time":time_now,"vip_instance":vip_instance,"vip_group":vip,"alert_time":alert_time}
        _data = json.dumps(data)
        try:
            r = requests.post(url,data=_data,timeout=1)
            logging.info('Post Alert Message Successed !')
            return True
        except Exception,e:
            logging.warn('Post Alert Message Failed! case by: %s' %e)
            return False
            
    def write_mail_content(self,cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time):
        """
        repo: repository
        rev: revision
        """
        html_template = u"""
        <html>
                <h2 style="color:#FFFFFF; background: #008040;">LVS报警邮件</h2>
                <div> <b>报警时间：</b>%s
                </div>
                <div> <b>集群：</b>%s
                </div>
                <div> <b>调度机：</b>%s
                </div>
                </div>
                <div> <b>机房：</b>%s
                </div>
                <div>
                        <b>业务：</b>%s
                </div>
                <div>
                        <b>业务VIP：</b>%s
                </div>
                <div>
                        <b>负责人：</b>%s
                </div>
                <div>
                        <b>服务器：</b>%s
                </div>
                <div>
                        <b>状态：</b>%s
                </div>
                <h2 style="color:#FFFFFF; background: #4682B4;">报警消息</h2> 
                <font size="4" color="#BF6000"><xmp>%s</xmp></font>
                <h2 style="color:#FFFFFF; background: #5353B9;">监控平台结果</h2>
                <a href="http://lvs.ksops.com/lvsalert/?vip_instance=%s&date=%s">点击查看LVS报警页面</a>
                <hr>
        </html>
        """
        content = html_template % (alert_time,cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,self.date)
        return content
    
    def search_vip_from_infoyaml(self,vip_instance):
        infoyaml = self.get_info_yaml()
        for vip in infoyaml['server']:
            if vip_instance == vip['vip_instance']:
                return vip
        return False
                           
class keepalived_log_analyze():
    def __init__(self,filename,logfile):
        self.filename = filename
        #查找 file的 size ，移动到文件的最后
        self.file = open(self.filename,'r')
        self.st_results = os.stat(self.filename)
        self.st_size = self.st_results[6]
        self.file.seek(self.st_size)
        try:
            logging.basicConfig(level=logging.NOTSET,
                format='%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename=logfile,
                filemode='a')
            self.logging = logging.getLogger()
        except AttributeError as err:
            print("Error: %s %s" %(err, logfile))
            sys.exit(2)
        
    def run(self):    
        #启动notify监听
        while True:
            time.sleep(1)
            lines = self.file.readlines()
            if not lines: continue
            for line in lines:
                self.handler(line)
                
    def handler(self,line):
        #开始匹配规则
        self.rs_is_disable(line)
        self.rs_is_enable(line)
        self.service_is_disable(line)
        self.service_is_up(line)
    
    def service_is_disable(self,log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*Executing\s*\[ip\s*addr\s*del.*\]\s*for\s*VS\s*\[(\S*)\]:\d+$')
        match = compile_log.match(log)
        if match:
            log_group = match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            vip_instance = log_group[5]
            print 'Service:%s is down' %vip_instance
            job = {"job_type":"run_service_is_disable_action","lb_id":lb_id,"vip_instance":vip_instance,"alert_time":alert_time}
            job_queue.put(job)
    
    def service_is_up(self,log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*Executing\s*\[ip\s*addr\s*add.*\]\s*for\s*VS\s*\[(\S*)\]:\d+$')
        match = compile_log.match(log)
        if match:
            log_group = match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            vip_instance = log_group[5]
            print 'Service:%s is up' %vip_instance
            job = {"job_type":"run_service_is_enable_action","lb_id":lb_id,"vip_instance":vip_instance,"alert_time":alert_time}
            job_queue.put(job)
    
    def rs_is_enable(self,log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*(Enabling|Adding)\s*service\s*\[(\d+\.\d+\.\d+\.\d+)\]:(\d+)\s*to\s*VS \[(\S*)\]:\d+$')
        match = compile_log.match(log)
        if match:
            log_group =  match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            rs = "%s:%d" %(log_group[6],int(log_group[7]))
            vip_instance = log_group[8]
            print 'RS:%s form %s is enable' %(rs,vip_instance)
            job = {"job_type":"run_rs_is_enable_action","lb_id":lb_id,"vip_instance":vip_instance,"rs":rs,"alert_time":alert_time}
            job_queue.put(job)
        
    def rs_is_disable(self,log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*(Removing|Disabling)\s*service\s*\[(\d+\.\d+\.\d+\.\d+)\]:(\d+)\s*from\s*VS\s*\[(\S*)\]:\d+$')
        match = compile_log.match(log)
        if match:
            log_group =  match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            rs = "%s:%d" %(log_group[6],int(log_group[7]))
            vip_instance = log_group[8]
            print 'RS:%s form %s is disable' %(rs,vip_instance)
            job = {"job_type":"run_rs_is_disable_action","lb_id":lb_id,"vip_instance":vip_instance,"rs":rs,"alert_time":alert_time}
            job_queue.put(job)
            
if __name__ == '__main__':
    filename = config['keepalived_log_file']
    logfile = config['logfile']
    t= Mythread(job_queue)
    t.start()
    work = keepalived_log_analyze(filename,logfile)
    work.run()
    t.join()
    
    