#!/usr/bin/env python
# -*- coding: utf8 -*- 
import os , time
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
#import motor
import yaml
import json
from tornado import gen
import pymongo
from pymongo import Connection
from setting import config ,agentlist
from tornado.options import define, options

from model import Model
from operator import itemgetter, attrgetter

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

class mongo_conn():
    def __init__(self):
        self.conn = Connection(options.mongodb,options.mongodb_port)
    def db(self):
        return self.conn[options.db]

class Handler():
    def __init__(self,method,id):
        self.method = method
        self.id = id
        self.mongo = mongo_conn()
        self.db = self.mongo.db()
        self.config = yaml.load(open(options.config))
        self.agentlist = config['agent']

    def getalldata(self):
        dict = {}
        for i in self.agentlist:
            dict[i['id']] = self.getnodedata(i['id'])
        return dict

    def getnodedata(self,id):
        agent = self._search_yaml(id)
        if agent:
            agent['data'] = self._agentdata(agent)
            return agent
        raise tornado.web.HTTPError(500, error)

    def _agentdata(self,agent):
        list = []
        for row in self.db[self.method].find({"id":agent['id']},{"_id":0,"time":1,"data":1}).sort([("time",-1)]).limit(60):
            list.append(row)
        return list

    def _search_yaml(self,input):
        for i in self.agentlist:
           if input == i['id']:
                return i
        return False


class GetCpuDetail(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetCpuDetail',id)
            result = handler.getnodedata(id)
            self.write(json.dumps(result))
            self.finish()
        else:
            handler = Handler('GetCpuDetail',id)
            result = handler.getalldata()
            self.write(json.dumps(result))
            self.finish()

class GetCpuInfo(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetCpuInfo',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetCpuInfo',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetHddInfo(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetHddInfo',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetHddInfo',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetIfTraffic(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetIfTraffic',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetIfTraffic',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetLoadAvg(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetLoadAvg',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetLoadAvg',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetLvsConn(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetLvsConn',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetLvsConn',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetLvsExtStatsSumm(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetLvsExtStatsSumm',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetLvsExtStatsSumm',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetLvsStatsSumm(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetLvsStatsSumm',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetLvsStatsSumm',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetMemInfo(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument("agent", None)
        if id:
            handler = Handler('GetMemInfo',id)
            result = handler.getnodedata(id)
            self.write(result)
            self.finish()
        else:
            handler = Handler('GetMemInfo',id)
            result = handler.getalldata()
            self.write(result)
            self.finish()

class GetLvsTraffic(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        hoursago = int(time.time()-3600)
        now = int(time.time())
        id = self.get_argument("agent", None)
        start = self.get_argument("start", hoursago)
        end = self.get_argument("end", now)
        start = round(float(start))
        end = round(float(end))

        if id:
            handler = Model('GetLvsTraffic_sum')
            result = handler.getlbsum(id,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()
        else:
            handler = Model('GetLvsTraffic_sum')
            result = handler.getsum(start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()

class AgentInfo(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        config = yaml.load(open(options.config))
        agentlist = config['agent']
        self.write(json.dumps(agentlist))
        self.finish()

class ClusterInfo(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        config = yaml.load(open(options.config))
        cluster = config['cluster']
        self.write(json.dumps(cluster,sort_keys=False, indent=4, separators=(',', ': ')))
        self.finish()

class GetLvsTrafficVip(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        hoursago = int(time.time()-3600)
        now = int(time.time())
        id = self.get_argument("agent", None)
        vip = self.get_argument("vip", None)
        start = self.get_argument("start", hoursago)
        end = self.get_argument("end", now)
        start = round(float(start))
        end = round(float(end))
        
        if id and vip:
            handler = Model('GetLvsTraffic_demo')
            result = handler.getlbtovipdata(id,vip,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()
        elif id:
            handler = Model('GetLvsTraffic_demo')
            result = handler.getlbdata(id,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()
        else:
            handler = Model('GetLvsTraffic_demo')
            result = handler.getalldata(start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()

class GetLvsTrafficCluster(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        hoursago = int(time.time()-3600)
        now = int(time.time())
        id = self.get_argument("agent", None)
        start = self.get_argument("start", hoursago)
        end = self.get_argument("end", now)
        start = round(float(start))
        end = round(float(end))

        if id:
            handler = Model('GetLvsTraffic_cluster_sum')
            result = handler.getclustersum(id,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()
        else:
            handler = Model('GetLvsTraffic_cluster_sum')
            result = handler.getcluster(id,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()

class GetLvsTrafficClusterVip(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        hoursago = int(time.time()-3600)
        now = int(time.time())
        id = self.get_argument("agent", None)
        vip = self.get_argument("vip", None)
        start = self.get_argument("start", hoursago)
        end = self.get_argument("end", now)
        start = round(float(start))
        end = round(float(end))

        if id and vip:
            handler = Model('GetLvsTraffic_cluster')
            result = handler.getoneclustervip(id,vip,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()
        elif id:
            handler = Model('GetLvsTraffic_cluster')
            result = handler.getclustervip(id,start,end)
            self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
            self.finish()

class GetLvsClusterVipList(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        hoursago = int(time.time()-3600)
        now = int(time.time())
        id = self.get_argument("agent", None)
        start = self.get_argument("start", hoursago)
        end = self.get_argument("end", now)
        start = round(float(start))
        end = round(float(end))

        handler = Model('GetLvsTraffic_cluster')
        result = handler.getclusterviplist(id,start,end)
        for i in result:
            vip_info = search_vip_info(id,i['vip'])
            if vip_info:
                i['descript'] = vip_info['descript']
                i['owners'] = vip_info['owners']
            else:
                i['descript'] = u'未记录'
                i['owners'] = u'未记录'
        self.write(json.dumps(result,sort_keys=False, indent=4, separators=(',', ': ')))
        self.finish()
        
class LvsAlertApiMessage(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        '''
        lvs alert api for record message
        '''
        message = tornado.escape.json_decode(self.request.body)
        handler = Model('LvsAlert')
        result = handler.insertlvsalert(message)
        self.finish()

class getClusterInfo(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        '''
        获取 lvs集群的信息
        @parm id= cluster的id
        返回 lvscluterid vip:port 业务用途 负责人 机房 邮件地址 协议
        '''
        id = self.get_argument('id',None)
        if not id: raise tornado.web.HTTPError(500, 'please provide cluster id')

        handler = Model('LvsManagerPublish')
        _clusters = handler.getLvsManagerPublishLastRev(id)
        if not _clusters: raise tornado.web.HTTPError(500, 'cluster id is not exsits')

        cluster_keys = ['area','cluster_id']
        server_keys = ['mailto','owners','protocol','vip_group','descript']

        def _update(server):
            my_dict = {}
            for key in server_keys:
                my_dict[key] = server[key]
            return my_dict

        _server = map(_update,_clusters['server'])
        cluster = dict(map(lambda x: (x,_clusters[x]) ,cluster_keys))
        cluster['server'] = _server

        self.write(json.dumps(cluster,sort_keys=False, indent=4, separators=(',', ': ')))
        self.finish()