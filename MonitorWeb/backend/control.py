#!/usr/bin/env python
# -*- coding: utf8 -*- 
import os
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import unicodedata
#import motor
import yaml
import json
from tornado import gen
import pymongo
from pymongo import Connection
from tornado.options import define, options
from model import Model
import datetime
import time
import socket
from bytesformat import bytes2human
import codecs
from bson.objectid import ObjectId
import urllib2


def search_cluster(id): 
    config = yaml.load(open(options.config))
    cluster_list = config['cluster']
    for i in cluster_list:
        if id == i['id']:
            return i
    return None

def search_agent(id):
    config = yaml.load(open(options.config))
    agent_list = config['agent']
    for i in agent_list:
        if id == i['id']:
            return i
    return None

def rs_is_lived(weight):
    if int(weight) == 0:
        return False
    else:
        return True
    
def user_is_manager(user):
    handler = Model('LvsAccount')
    user_info = handler.getAccountOne(user)
    if user_info['is_manager'] or user_info['is_super_manager'] :
        return True
    else:
        return False
    
def bytesformat(bytes):
    return bytes2human(bytes)

def format_rs_str(rs):
    _rs = rs.split(':')
    return _rs[0]


def timestamptodate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def datetotimestamp(date):
    time_obj = time.strptime(date,"%Y-%m-%d %H:%M:%S")
    return time.mktime(time_obj)
     
def check_server(address,port,protocol):
    if protocol == 'udp':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((address,port))
        s.close()
        return True
    except socket.error, e:
        s.close()
        return False

def search_vip_info(cluster_id,vip):
    try:
        handler = Model('lvsManagerPublish')
        last_cluster_info = handler.getLvsPublishLast(cluster_id)
        for i in last_cluster_info['server']:
            for vip_gourp in i['vip_group']:
                _vip = '%s:%s' %(vip_gourp['vip'],vip_gourp['port'])
                if vip == _vip:
                    return i
        return False
    except Exception, e:
        return False

class saltstackwork():
    def __init__(self):
        import salt
        self.local = salt.client.LocalClient()
    
    def run_publish_keepalived(self,tgt,source_file,dst_file):
        func = 'cp.recv'
        f = open(source_file,'r')
        file_data = f.read()
        f.close()
        _fn = {source_file:file_data}
        result = self.local.cmd(tgt,func,[_fn,dst_file],expr_form='list',timeout=10)
        return result
    
    def run_cp_file(self,tgt,source_file,dst_file,context):
        func = 'cp.recv'
        _fn = {source_file:context}
        result = self.local.cmd(tgt,func,[_fn,dst_file],expr_form='list',timeout=10)
        return result
        
    def run_cmd(self,tgt,cmd):
        _cmd = [cmd]
        result = self.local.cmd(tgt,'cmd.run',_cmd,expr_form='list',timeout=10)
        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id":i,"ret":result[i],"result":True})
            else:
                result_list.append({"id":i,"result":False})
        return result_list
        
class TemplateRendering():

    """
    A simple class to hold methods for rendering templates.
    """
    def render_template(self, template_name, **kwargs):
        template_dirs = []
        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )

        env = Environment(loader=FileSystemLoader(template_dirs))
        env.tests['rs_is_lived'] = rs_is_lived
        env.tests['user_is_manager'] = user_is_manager
        env.filters['timestamptodate'] = timestamptodate
        env.filters['bytesformat'] = bytesformat
        env.filters['format_rs_str'] = format_rs_str

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    """
    RequestHandler already has a `render()` method. I'm writing another
    method `render2()` and keeping the API almost same.
    """
    def render2(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
            'current_user':self.get_current_user() ,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)
    def template(self, template_name, **kwargs):
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        return content

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return user_id
    
    def get_context(self):
        self.context = {
                        'current_user':self.get_current_user(),
                        }
        return self.context
    
class mongo_conn():
    def __init__(self):
        self.conn = Connection(options.mongodb,options.mongodb_port)
    def db(self):
        return self.conn[options.db]

class HomeHandler(BaseHandler):
    def get(self):
        '''
        show index page
        '''
        current_user = self.get_current_user()
        if current_user:
            self.redirect('/charts/')
        else:
            ksso_url = options.ksso_url
            lvs_url = options.lvs_url
            ret = "%slogin?forward=%slogin" % (ksso_url,lvs_url)
            self.redirect(ret)

class LoginOut(BaseHandler):
    def get(self):
        '''
        user login out
        '''
        ksso_url = options.ksso_url
        lvs_url = options.lvs_url
        self.clear_cookie("user")
        ret = "%slogout?forward=%s" % (ksso_url,lvs_url)
        self.redirect(ret)
        
class Login(BaseHandler):
    def get(self):
        '''
        user login
        '''
        ticket = self.get_argument("t", None)
        lvs_url = options.lvs_url
        ksso_url = options.ksso_url
        _request = urllib2.Request("%sverify?t=%s" % (ksso_url,ticket))
        _request.add_header("referer",lvs_url)
        res = urllib2.urlopen(_request)
        user = res.read()
        if user == 'False':
            raise tornado.web.HTTPError(500, 'Ksso Retrun False')
        if user:
            handler = Model('Account')
            _find_user_result = handler.getAccountOne(user)
            if  _find_user_result:
                time_now = timestamptodate(time.time())
                handler.updateAccountLogintime(user,time_now)
            else:
                time_now = timestamptodate(time.time())
                user_data = {"username":user,"is_manager":False,"is_super_manager":False,"login_time":time_now,"register_time":time_now}
                handler.InsertAccount(user_data)
        self.set_secure_cookie("user", user,expires_days=options.cookies_expires)
        self.redirect('/charts/')
        
class ChartsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show Charts.html page
        '''
        self.render2('charts.html')

class Status(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show status.html page
        '''
        self.render2('status.html')

class ClusterStatus(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show status.html page
        '''
        dict = {}
        handler = Model('GetLvsConn_status')
        config = yaml.load(open(options.config))
        cluster_list = config['cluster']
        for cluster in cluster_list:
            agent = handler.getStatusForCluster(str(cluster['id']))
            lb_count = len(agent)
            
        handler = Model('GetLvsConn_status')
        status_dict = handler.getStatusForCluster()
        self.render2('cluster_status.html')

class LbStatus(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show status.html page
        '''
        config = yaml.load(open(options.config))
        cluster_list = config['cluster']

        self.render2('lb_status.html',cluster_list=cluster_list)

class LbStatusTable(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        ajax for lb status 
        '''
        id = self.get_argument("id", None)
        cluster_dict = {}
        list = []
        handler = Model('GetLvsConn_status')
        cluster_dict = search_cluster(id)
        for i in cluster_dict['agent']:
            agent_ip = search_agent(i)['ipadd']
            agent = handler.getStatusForAgent(i)
            if agent['node']:
                vipcount = len(agent['node'])
            else:
                vipcount = 0
            time = datetime.datetime.fromtimestamp(agent['time'])
            dict = {"id":i,"ipadd":agent_ip,"vipcount":vipcount,"time":time}
            list.append(dict)
        tpl = self.render2('lb_status_table.tpl',lblist=list)

class LbStatusVipTable(BaseHandler):
    def get(self):
        '''
        ajax for lb status 
        '''
        id = self.get_argument("id", None)
        
        handler = Model('GetLvsConn_status')
        agnet_dict = handler.getStatusForAgent(id)
        for i in agnet_dict['node']:
            vip_info = search_vip_info(agnet_dict['cluster'],i['vip'])
            if vip_info:
                i['descript'] = vip_info['descript']
                i['owners'] = vip_info['owners']
            else:
                i['descript'] = u'未记录'
                i['owners'] = u'未记录'
        self.render2('lb_vip_status_table.tpl',vip_dict=agnet_dict)

class LbStatusDiff(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show diff.html page
        '''
        config = yaml.load(open(options.config))
        cluster_list = config['cluster']

        self.render2('diff.html',cluster_list=cluster_list)

class LbDiffTable(BaseHandler):
    def get(self):
        '''
        ajax for lb status diff
        '''

        id = self.get_argument("id", None)
        start = self.get_argument("start")
        end = self.get_argument("end")
        start = round(float(start))
        end = round(float(end))

        cluster_dict = {}
        list = []
        handler = Model('GetLvsConn_diff')
        cluster_dict = search_cluster(id)
        for i in cluster_dict['agent']:
            agent_ip = search_agent(i)['ipadd']
            diff_event_count = handler.getStatusDiffCount(i,start,end)
            dict = {"id":i,"ipadd":agent_ip,"diffcount":diff_event_count}
            list.append(dict)
        tpl = self.render2('diff_table.tpl',difflist=list)

class lbDiffAgentTable(BaseHandler):
    def get(self):
        '''
        ajax for agent diff 
        '''
        id = self.get_argument("id", None)
        start = self.get_argument("start")
        end = self.get_argument("end")
        start = round(float(start))
        end = round(float(end))
        
        handler = Model('GetLvsConn_diff')
        result = handler.getStatusDiff(id,start,end)
        for i in result:
            i['_time'] = timestamptodate(i['time'])
        self.render2('diff_agent_table.tpl',diff_dict=result)

class Publish(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show publish.html page
        '''
        handler = Model('LvsPublish')
        result = handler.getLvsPublish()
        self.render2('publish.html',publish=result)

class PublishNetworkTest(BaseHandler):
    def get(self):
        '''
        ajax for publish network test table
        '''
        id = self.get_argument("id", None)
        handler = Model('LvsPublish')
        result = handler.getLvsPublishOne(id)
        info = result['info_yaml'][result['id']]
        html = ''
        success_count = 0
        fail_count = 0
        for i in info['server']:
            address_list = i['vip_group']
            protocol = str(i['protocol'])
            descript = i['descript']
            for vip_group in address_list:
                ret = check_server(vip_group['vip'],vip_group['port'],protocol)
                if ret:
                    html += '%s  %s:%s   ok\n' % (descript,vip_group['vip'],vip_group['port'])
                    success_count += 1
                else:
                    html += '%s  %s:%s   fail\n' % (descript,vip_group['vip'],vip_group['port'])
                    fail_count += 1
        dict = {"success_count":success_count,"fail_count":fail_count,"html":html}
        self.render2('publishnetworktest.tpl',network=dict)

class PublishInfoYaml(BaseHandler):
    def get(self):
        '''
        ajax for publish info yaml table
        '''
        id = self.get_argument("id", None)
        handler = Model('LvsPublish')
        result = handler.getLvsPublishOne(id)
        info = result['info_yaml'][result['id']]
        self.render2('publishinfoyaml.tpl',info=info)

class LvsReport(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsreport.html
        '''
        error_msg = ""
        config = yaml.load(open(options.config))
        cluster_list = config['cluster']
        first_id = cluster_list[0]['id']
        dt = datetime.date.today() - datetime.timedelta(1)
        yesterday = datetime.datetime.strftime(dt,'%Y-%m-%d')
        id = self.get_argument("id",first_id)
        date = self.get_argument("date",yesterday)
        start = datetotimestamp('%s 00:00:00' % date)
        end = datetotimestamp('%s 23:59:59' % date)
        handler = Model('LvsReport')
        report_result =  handler.getLvsReport(id,date)
        if not report_result:
            error_msg = "WARNING: No report in that day"
            report_result = handler.getLvsReport(id,yesterday)
        self.render2('lvsreport.html',cluster_list=cluster_list,id=id,report_result=report_result,start=start,end=end,error_msg=error_msg)
        
class LvsAlert(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsalert.html
        '''
        dt = datetime.date.today()
        today = datetime.datetime.strftime(dt,'%Y-%m-%d')
        find = {}
        find['rs'] = self.get_argument("rs",None)
        find['vip_group'] = self.get_argument("vip_group",None)
        find['vip_instance'] = self.get_argument("vip_instance",None)
        find['alert_type'] = self.get_argument("alert_type",None)
        date_time = self.get_argument("date",today)
        start = datetotimestamp('%s 00:00:00' % date_time)
        end = datetotimestamp('%s 23:59:59' % date_time)
        _find = {}
        for i in find:
            if find[i] is not None:
                _find[i] = {"$regex":find[i]}
        handler = Model('LvsAlert')
        alert_dict = handler.getLvsAlert(_find,start,end)
        rs_is_down_count = handler.getLvsAlertTypeCount('rs_is_down',start,end)
        rs_is_up_count = handler.getLvsAlertTypeCount('rs_is_up',start,end)
        service_is_down_count = handler.getLvsAlertTypeCount('service_is_down',start,end)
        service_is_up_count = handler.getLvsAlertTypeCount('service_is_up',start,end)
        self.render2('lvsalert.html',alert_dict = alert_dict, date=date_time,rs_is_down_count=rs_is_down_count , service_is_down_count=service_is_down_count ,rs_is_up_count=rs_is_up_count,service_is_up_count=service_is_up_count)

class lvsManager(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager.html
        '''
        config = yaml.load(open(options.config))
        current_user = self.get_current_user()
        handler = Model('LvsAccount')
        user_info = handler.getAccountOne(current_user)
        if user_info['is_super_manager']:
            cluster_list = config['cluster']
        elif user_info['is_manager']:
            cluster_list = [ i for i in config['cluster'] if current_user in i['manager_user'] ]
        else:
            cluster_list = []
            #self.write('Permission denied !!')
        
        for cluster in cluster_list:
            lb_list = []
            for lb in cluster['agent']:
                lb_info = search_agent(lb)
                lb_list.append({"id":lb_info['id'],"ipadd":lb_info['ipadd']})
            cluster['lb'] = lb_list
        self.render2('lvsmanager.html',cluster_list=cluster_list)

class lvsManagerDeploy(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager_deploy.html
        '''
        id = self.get_argument("id",None)
        handler = Model('LvsManagerConfig')
        vipinstanceinfo = handler.getLvsManagerConfigVipInstanceList(id)
        self.render2('lvsmanager_deploy.html',vipinstanceinfo=vipinstanceinfo,cluster=id)

class lvsManagerDeployAdd(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager_config_add.html
        '''
        id = self.get_argument("id",None)
        self.render2('lvsmanager_deploy_add.html',cluster=id)

    def post(self):
        '''
        Add new vip_instance
        '''
        data = tornado.escape.json_decode(self.request.body)
        data['status'] = 'online'
        data['mailto'] = data['mailto'].split(',')
        vip_group = data['vip_group'].split(',')
        vip_group_list = []
        for vip in vip_group:
            viplist = vip.split(':')
            vip_group_list.append({"vip":viplist[0],"port":viplist[1]})
        data['vip_group'] = vip_group_list
        for rs in data['rs']:
            rs['port'] = rs['port'].split(',')
        handler = Model('LvsManagerConfig')
        handler.insertLvsManagerConfigVipInstance(data)
        self.write('ok')
        
class lvsManagerDeployDel(BaseHandler):
    def post(self):
        '''
        Remove vip_instance
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        handler = Model('LvsManagerConfig')
        handler.DelLvsManagerConfigVipInstance(id)
        self.write('ok')

class lvsManagerDeployOffline(BaseHandler):
    def post(self):
        '''
        Remove vip_instance
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        handler = Model('LvsManagerConfig')
        handler.UpdateLvsManagerConfigVipInstanceToOffline(id)
        self.write('ok')

class lvsManagerDeployOnline(BaseHandler):
    def post(self):
        '''
        Remove vip_instance
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        handler = Model('LvsManagerConfig')
        handler.UpdateLvsManagerConfigVipInstanceToOnline(id)
        self.write('ok')
                
class lvsManagerDeployEdit(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show vip instance edit page
        '''
        id = self.get_argument("id",None)
        handler = Model('LvsManagerConfig')
        vipinstanceinfo =  handler.getLvsManagerConfigVipInstanceInfo(id)
        vipinstanceinfo['mailto'] = ','.join(vipinstanceinfo['mailto'])
        vipgroup = vipinstanceinfo['vip_group']
        vipgrouplist = ["%s:%s"%(vip['vip'],vip['port']) for vip in vipgroup ]
        vipinstanceinfo['vip_group'] = ','.join(vipgrouplist)
        for index,rs in enumerate(vipinstanceinfo['rs']):
            rs['index'] = index
            rs['port'] = ','.join(rs['port'])
        self.render2('lvsmanager_deploy_edit.html',vipinstance = vipinstanceinfo)

    def post(self):
        '''
        save vip instance edit
        '''
        id = self.get_argument("id",None)
        data = tornado.escape.json_decode(self.request.body)
        data['mailto'] = data['mailto'].split(',')
        vip_group = data['vip_group'].split(',')
        vip_group_list = []
        for vip in vip_group:
            viplist = vip.split(':')
            vip_group_list.append({"vip":viplist[0],"port":viplist[1]})
        data['vip_group'] = vip_group_list
        for rs in data['rs']:
            rs['port'] = rs['port'].split(',')
        handler = Model('LvsManagerConfig')
        handler.UpdateLvsManagerConfigVipInstance(id,data)
        self.write('ok')


class lvsManagerDeployGetRsList(BaseHandler):
    def get(self):
        '''
        get rs list
        '''
        id = self.get_argument("id",None)
        handler = Model('LvsManagerConfig')
        vipinstanceinfo =  handler.getLvsManagerConfigVipInstanceInfo(id)
        for index,rs in enumerate(vipinstanceinfo['rs']):
            rs['index'] = index
            rs['port'] = ','.join(rs['port'])
        self.write(json.dumps(vipinstanceinfo['rs']))
        
class lvsManagerPublish(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        run publish action
        '''
        time_now = time.time()
        cluster_id = self.get_argument("id",None)
        mess = self.get_argument("mess",None)
        area = search_cluster(cluster_id)['area']
        admin_mail_group = search_cluster(cluster_id)['admin_mail_group']
        handler = Model('LvsManagerConfig')
        vipinstancelist = handler.getLvsManagerConfigVipInstanceList(cluster_id)
        _vipinstancelist = handler.getLvsManagerConfigVipInstanceList(cluster_id)
        for i in _vipinstancelist:
            i["_id"] = str(i["_id"])
        if len(vipinstancelist) == 0:
            self.write('不存配置文件，停止发布')
        else:
            handler = Model('LvsManagerPublish')
            #获取最新的版本号，如果没有则为1
            last_rev = handler.getLvsManagerPublishLastRev(cluster_id)
            if last_rev:
                rev = last_rev['rev'] + 1
            else:
                rev = 1
            #insert发布记录
            lvsmanagerpublish = {"time":time_now,"message":mess,"cluster_id":cluster_id,"rev":rev,"server":_vipinstancelist,"area":area,"admin_mail_group":admin_mail_group}
            context = yaml.dump(lvsmanagerpublish)
            new_publish_id = handler.insertLvsManagerPublish(lvsmanagerpublish)
            #创建keepalived配置文件
            keepalived_config = self.template('keepalived.tpl',vip_instance_list = vipinstancelist, cluster_id = cluster_id)
            publishdir = options.publishdir
            keepalived_config_file = os.path.join(publishdir,new_publish_id)
            f = codecs.open(keepalived_config_file,'w+','utf-8')
            f.write(keepalived_config)
            f.close()
            #调用saltstack，传送配置
            config = yaml.load(open(options.config))
            tgt = search_cluster(cluster_id)['agent']
            source_file = keepalived_config_file
            dst_file = '/etc/keepalived/keepalived.conf'
            runsalt = saltstackwork()
            result = runsalt.run_publish_keepalived(tgt, source_file,dst_file)
            #publish info.yaml
            info_source_file = 'info.yaml'
            info_dst_file = '/etc/keepalived/info.yaml'
            result2 = runsalt.run_cp_file(tgt, info_source_file, info_dst_file, context)
            ret_html = ''
            ret_result = True
            print result2
            print result
            for lb in tgt:
                if result.has_key(lb) & result2.has_key(lb):
                    ret_html += '%s ok\n' %(lb)
                else:
                    ret_html += '%s failed\n' %(lb)
                    ret_result = False
            #更新发布结构
            handler.updateLvsManagerPublishResult(new_publish_id,ret_result)
            self.write(ret_html)
        
class lvsManagerRollback(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager_rollback.html
        '''
        cluster_id = self.get_argument("id",None)
        handler = Model('LvsManagerPublish')
        publishlist = handler.getLvsManagerPublishList(cluster_id)
        self.render2('lvsmanager_rollback.html',publishlist = publishlist, cluster_id = cluster_id)
    
    def post(self):
        '''
        run roll back action
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        message = data['mess']
        time_now = time.time()
        handler = Model('LvsManagerPublish')
        #获取需要rollbak的版本的记录
        rollback_record = handler.getLvsManagerPublishOne(id)
        cluster_id = rollback_record['cluster_id']
        vipinstancelist = rollback_record['server']
        area = search_cluster(cluster_id)['area']
        admin_mail_group = search_cluster(cluster_id)['admin_mail_group']
        #把rollbak的版本替换到现在的配置信息上
        ##把此集群现有的配置信息先清空
        handler.removeLvsManagerConifghForCluster(cluster_id)
        ##把rollback的配置信息insert进去
        for vipinstance in vipinstancelist:
            vipinstance["_id"] = ObjectId(vipinstance["_id"])
            handler.insertLvsManagerConfigVipInstance(vipinstance)
        #获取最新的版本号，如果没有则为1
        last_rev = handler.getLvsManagerPublishLastRev(cluster_id)
        if last_rev:
            rev = last_rev['rev'] + 1
        else:
            rev = 1
        #insert发布记录
        for i in vipinstancelist:
            i['_id'] = str(i['_id'])
        lvsmanagerpublish = {"time":time_now,"message":message,"cluster_id":cluster_id,"rev":rev,"server":vipinstancelist,"area":area,"admin_mail_group":admin_mail_group}
        context = yaml.dump(lvsmanagerpublish)
        new_publish_id = handler.insertLvsManagerPublish(lvsmanagerpublish)
        #创建keepalived配置文件
        keepalived_config = self.template('keepalived.tpl',vip_instance_list = vipinstancelist, cluster_id = cluster_id)
        publishdir = options.publishdir
        keepalived_config_file = os.path.join(publishdir,new_publish_id)
        f = codecs.open(keepalived_config_file,'w+','utf-8')
        f.write(keepalived_config)
        f.close()
        #调用saltstack，传送配置
        config = yaml.load(open(options.config))
        tgt = search_cluster(cluster_id)['agent']
        source_file = keepalived_config_file
        dst_file = '/etc/keepalived/keepalived.conf'
        runsalt = saltstackwork()
        result = runsalt.run_publish_keepalived(tgt, source_file,dst_file)
        #publish info.yaml
        info_source_file = 'info.yaml'
        info_dst_file = '/etc/keepalived/info.yaml'
        result2 = runsalt.run_cp_file(tgt, info_source_file, info_dst_file, context)
        
        ret_html = ''
        ret_result = True
        for lb in tgt:
            if result.has_key(lb) & result2.has_key(lb):
                ret_html += '%s ok\n' %(lb)
            else:
                ret_html += '%s failed\n' %(lb)
                ret_result = False
        #更新发布结构
        handler.updateLvsManagerPublishResult(new_publish_id,ret_result)
        self.write(ret_html)

class lvsManagerKeepalivedReload(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager_keepalived_reload.html page
        '''
        cluster_id = self.get_argument("id",None)
        cluster = search_cluster(cluster_id)
        cluster['lb']  = [search_agent(lb) for lb in cluster['agent']]
        self.render2('lvsmanager_keepalived_reload.html',cluster = cluster )
    
    def post(self):
        '''
        run keepalived reload action
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        lb_list = data['lb_list']
        runsalt = saltstackwork()
        #调用salt，执行keepalived reload命令
        cmd = '/etc/init.d/keepalived reload'
        cmd_result = runsalt.run_cmd(lb_list, cmd)
        self.render2('lvsmanager_keepalived_reload_result.tpl', cmd_result = cmd_result)
        
class lvsManagerKeepalivedStartOrStop(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager_keepalived_start_or_stop.html page
        '''
        cluster_id = self.get_argument("id",None)
        cluster = search_cluster(cluster_id)
        cluster['lb']  = [search_agent(lb) for lb in cluster['agent']]
        self.render2('lvsmanager_keepalived_start_or_stop.html',cluster = cluster )
    
    def post(self):
        '''
        run keepalived reload action
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        start_or_stop = data['start_or_stop']
        lb_list = data['lb_list']
        runsalt = saltstackwork()
        #调用salt，执行keepalived start or stop
        if start_or_stop == 'start':
            cmd = '/etc/init.d/keepalived start'
        else:
            cmd = '/etc/init.d/keepalived stop'
        cmd_result = runsalt.run_cmd(lb_list, cmd)
        self.render2('lvsmanager_keepalived_reload_result.tpl', cmd_result = cmd_result)

class lvsManagerKeepalivedIpvsadm(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show lvsmanager_keepalived_ipvsadm.html page
        '''
        cluster_id = self.get_argument("id",None)
        cluster = search_cluster(cluster_id)
        cluster['lb']  = [search_agent(lb) for lb in cluster['agent']]
        self.render2('lvsmanager_keepalived_ipvsadm.html',cluster = cluster )
    
    def post(self):
        '''
        run keepalived reload action
        '''
        data = tornado.escape.json_decode(self.request.body)
        id = data['id']
        lb_list = data['lb_list']
        runsalt = saltstackwork()
        #调用salt，执行keepalived ipvsadm -Ln
        cmd = 'ipvsadm -Ln'
        cmd_result = runsalt.run_cmd(lb_list, cmd)
        self.render2('lvsmanager_keepalived_reload_result.tpl', cmd_result = cmd_result)

class lvsManagerSearch(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        show search result page
        '''
        vip = self.get_argument("vip",None)
        rs = self.get_argument("rs",None)
        if vip:
            handler = Model('LvsManagerConfig')
            result = handler.getLvsManagerConfigSearchvip(vip)
            self.render2('lvsmanager_search.html',result = result)
        elif rs:
            handler = Model('LvsManagerConfig')
            result = handler.getLvsManagerConfigSearchrs(rs)
            self.render2('lvsmanager_search.html',result = result)