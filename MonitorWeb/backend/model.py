#!/usr/bin/env python
# -*- coding: utf8 -*- 
import os , time
from setting import config ,agentlist
from tornado.options import define, options
from pymongo import Connection
import yaml
import json
from operator import itemgetter, attrgetter
from bson.objectid import ObjectId

class mongo_conn():
    def __init__(self):
        self.conn = Connection(options.mongodb,options.mongodb_port)
    def db(self):
        return self.conn[options.db]

class Model():
    def __init__(self,method):
        self.method = method
        self.id = id
        self.mongo = mongo_conn()
        self.db = self.mongo.db()
        self.config = yaml.load(open(options.config))
        self.agentlist = config['agent']

    def getsum(self,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes_sum.push([obj.time,obj.inbytes_sum]) ;
                    prev.outbytes_sum.push([obj.time,obj.outbytes_sum]) ;
                    prev.inpkts_sum.push([obj.time,obj.inpkts_sum]) ;
                    prev.outpkts_sum.push([obj.time,obj.outpkts_sum]) ;
                    prev.conns_sum.push([obj.time,obj.conns_sum]) ;
                }'''
        initial = {"inbytes_sum":[],"outbytes_sum":[],"inpkts_sum":[],"outpkts_sum":[],"conns_sum":[]}
        db_result = self.db[self.method].group(['id'],{"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes_sum'], key=itemgetter(0))
            sorted(i['outbytes_sum'],key=itemgetter(0))
            sorted(i['inpkts_sum'],key=itemgetter(0))
            sorted(i['outpkts_sum'],key=itemgetter(0))
            sorted(i['conns_sum'],key=itemgetter(0))
            dict[i["id"]] = i
        return dict

    def getlbsum(self,id,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes_sum.push([obj.time,obj.inbytes_sum]) ;
                    prev.outbytes_sum.push([obj.time,obj.outbytes_sum]) ;
                    prev.inpkts_sum.push([obj.time,obj.inpkts_sum]) ;
                    prev.outpkts_sum.push([obj.time,obj.outpkts_sum]) ;
                    prev.conns_sum.push([obj.time,obj.conns_sum]) ;
                }'''
        initial = {"inbytes_sum":[],"outbytes_sum":[],"inpkts_sum":[],"outpkts_sum":[],"conns_sum":[]}
        db_result = self.db[self.method].group(['id'],{"id":id,"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes_sum'], key=itemgetter(0))
            sorted(i['outbytes_sum'],key=itemgetter(0))
            sorted(i['inpkts_sum'],key=itemgetter(0))
            sorted(i['outpkts_sum'],key=itemgetter(0))
            sorted(i['conns_sum'],key=itemgetter(0))
            i["title"] = i["id"]
            dict[i["id"]] = i
        return dict

    def getclustersum(self,cluster,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes_sum.push([obj.time,obj.inbytes_sum]) ;
                    prev.outbytes_sum.push([obj.time,obj.outbytes_sum]) ;
                    prev.inpkts_sum.push([obj.time,obj.inpkts_sum]) ;
                    prev.outpkts_sum.push([obj.time,obj.outpkts_sum]) ;
                    prev.conns_sum.push([obj.time,obj.conns_sum]) ;
                }'''
        initial = {"inbytes_sum":[],"outbytes_sum":[],"inpkts_sum":[],"outpkts_sum":[],"conns_sum":[]}
        db_result = self.db[self.method].group(['cluster'],{"cluster":cluster,"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes_sum'], key=itemgetter(0))
            sorted(i['outbytes_sum'],key=itemgetter(0))
            sorted(i['inpkts_sum'],key=itemgetter(0))
            sorted(i['outpkts_sum'],key=itemgetter(0))
            sorted(i['conns_sum'],key=itemgetter(0))
            i["title"] = i["cluster"]
            dict[i["cluster"]] = i
        return dict

    def getclustervip(self,cluster,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes.push([obj.time,obj.inbytes_sum_per]) ;
                    prev.outbytes.push([obj.time,obj.outbytes_sum_per]) ;
                    prev.inpkts.push([obj.time,obj.inpkts_sum_per]) ;
                    prev.outpkts.push([obj.time,obj.outpkts_sum_per]) ;
                    prev.conns.push([obj.time,obj.conns_sum_per]) ;
                }'''
        initial = {"inbytes":[],"outbytes":[],"inpkts":[],"outpkts":[],"conns":[]}
        db_result = self.db[self.method].group(['cluster','vip'],{"cluster":cluster,"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes'], key=itemgetter(0))
            sorted(i['outbytes'],key=itemgetter(0))
            sorted(i['inpkts'],key=itemgetter(0))
            sorted(i['outpkts'],key=itemgetter(0))
            sorted(i['conns'],key=itemgetter(0))
            i["title"] = i["vip"]
            dict[i["vip"]] = i
        return dict

    def getoneclustervip(self,cluster,vip,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes.push([obj.time,obj.inbytes_sum_per]) ;
                    prev.outbytes.push([obj.time,obj.outbytes_sum_per]) ;
                    prev.inpkts.push([obj.time,obj.inpkts_sum_per]) ;
                    prev.outpkts.push([obj.time,obj.outpkts_sum_per]) ;
                    prev.conns.push([obj.time,obj.conns_sum_per]) ;
                }'''
        initial = {"inbytes":[],"outbytes":[],"inpkts":[],"outpkts":[],"conns":[]}
        db_result = self.db[self.method].group(['cluster','vip'],{"cluster":cluster,"vip":vip,"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes'], key=itemgetter(0))
            sorted(i['outbytes'],key=itemgetter(0))
            sorted(i['inpkts'],key=itemgetter(0))
            sorted(i['outpkts'],key=itemgetter(0))
            sorted(i['conns'],key=itemgetter(0))
            i["title"] = i["vip"]
            dict[i["vip"]] = i
        return dict


    def getclusterviplist(self,cluster,start,end):
        dict = {}
        func = '''function(obj, prev) {
                }'''
        initial = {}
        db_result = self.db[self.method].group(['cluster','vip'],{"cluster":cluster,"time":{"$lt":end ,"$gt":start}},initial,func)
        return db_result


    def getlbdata(self,id,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes.push([obj.time,obj.inbytes_sum_per]) ;
                    prev.outbytes.push([obj.time,obj.outbytes_sum_per]) ;
                    prev.inpkts.push([obj.time,obj.inpkts_sum_per]) ;
                    prev.outpkts.push([obj.time,obj.outpkts_sum_per]) ;
                    prev.conns.push([obj.time,obj.conns_sum_per]) ;
                }'''
        initial = {"inbytes":[],"outbytes":[],"inpkts":[],"outpkts":[],"conns":[]}
        db_result = self.db[self.method].group(['id','vip'],{"id":id,"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes'], key=itemgetter(0))
            sorted(i['outbytes'],key=itemgetter(0))
            sorted(i['inpkts'],key=itemgetter(0))
            sorted(i['outpkts'],key=itemgetter(0))
            sorted(i['conns'],key=itemgetter(0))
            i["title"] = i["vip"]
            dict[i["vip"]] = i
        return dict

    def getlbtovipdata(self,id,vip,start,end):
        dict = {}
        func = '''function(obj, prev) {
                    prev.inbytes.push([obj.time,obj.inbytes_sum_per]) ;
                    prev.outbytes.push([obj.time,obj.outbytes_sum_per]) ;
                    prev.inpkts.push([obj.time,obj.inpkts_sum_per]) ;
                    prev.outpkts.push([obj.time,obj.outpkts_sum_per]) ;
                    prev.conns.push([obj.time,obj.conns_sum_per]) ;
                }'''
        initial = {"inbytes":[],"outbytes":[],"inpkts":[],"outpkts":[],"conns":[]}
        db_result = self.db[self.method].group(['id','vip'],{"id":id,"vip":vip,"time":{"$lt":end ,"$gt":start}},initial,func)
        for i in db_result:
            sorted(i['inbytes'],key=itemgetter(0))
            sorted(i['outbytes'],key=itemgetter(0))
            sorted(i['inpkts'],key=itemgetter(0))
            sorted(i['outpkts'],key=itemgetter(0))
            sorted(i['conns'],key=itemgetter(0))
            dict[vip] = i
        return dict


    def getStatusForAgent(self,id):
        db_result = self.db['GetLvsConn_status'].find_one({"id":id})
        return db_result

    def getStatusDiffCount(self,id,start,end):
        db_result = self.db['GetLvsConn_diff'].find({"id":id,"time":{"$lt":end ,"$gt":start}}).count()
        return db_result

    def getStatusDiff(self,id,start,end):
        db_result = self.db['GetLvsConn_diff'].find({"id":id,"time":{"$lt":end ,"$gt":start}}).sort("time", -1)
        return list(db_result)

    def getLvsPublish(self):
        db_result = self.db['LvsPublish'].find().sort("time" , -1)
        return db_result

    def getLvsPublishOne(self,id):
        db_result = self.db['LvsPublish'].find_one({"_id":ObjectId(id)})
        return db_result

    def getLvsPublishLast(self,cluster_id):
        db_result = self.db['LvsManagerPublish'].find({"cluster_id":cluster_id}).sort("time",-1)
        return db_result[0]

    def getLvsReport(self,id,date):
        try:
            db_result = self.db['LvsReport'].find({"id":id, "time":date})
            return db_result[0]
        except Exception, e:
            return False
    def insertlvsalert(self,message):
        db_result = self.db['LvsAlert'].insert(message)
        return db_result
    
    def getLvsAlert(self,find_dict,start,end):
        find_dict["time"] = {"$lt":end ,"$gt":start}
        db_result = self.db['LvsAlert'].find(find_dict).sort("time",-1)
        return db_result

    def getLvsAlertTypeCount(self,alert_type,start,end):
        db_result = self.db['LvsAlert'].find({"alert_type":alert_type,"time":{"$lt":end ,"$gt":start}}).count()
        return db_result

    def _search_yaml(self,input):
        for i in self.agentlist:
           if input == i['id']:
                return i
        return False


    def getLvsManagerConfigVipInstanceList(self,id):
        db_result = self.db['LvsManagerConfig'].find({"cluster_id":id})
        return list(db_result)
    
    def insertLvsManagerConfigVipInstance(self,data):
        self.db['LvsManagerConfig'].insert(data)
        return True

    def DelLvsManagerConfigVipInstance(self,id):
        self.db['LvsManagerConfig'].remove({"_id":ObjectId(id)})
        return True

    def getLvsManagerConfigVipInstanceInfo(self,id):
        result = self.db['LvsManagerConfig'].find_one({"_id":ObjectId(id)})
        return result

    def UpdateLvsManagerConfigVipInstance(self,id,update_data):
        self.db['LvsManagerConfig'].update({"_id":ObjectId(id)},update_data)
        return True
    
    def getLvsManagerPublishLastRev(self,id):
        result = self.db['LvsManagerPublish'].find({"cluster_id":id}).sort("time",-1)
        if result.count() != 0 :
            return list(result)[0]
        else:
            return False

    def insertLvsManagerPublish(self,data):
        result = self.db['LvsManagerPublish'].insert(data)
        return str(result)
    
    def updateLvsManagerPublishResult(self,id,publishresult):
        self.db['LvsManagerPublish'].update({"_id":ObjectId(id)},{"$set":{"publish_result":publishresult}})
        return  True
    
    def getLvsManagerPublishList(self,cluster_id):
        result = self.db['LvsManagerPublish'].find({"cluster_id":cluster_id}).sort("time",-1)
        return list(result)
        
    def getLvsManagerPublishOne(self,id):
        result = self.db['LvsManagerPublish'].find_one({"_id":ObjectId(id)})
        return result
    
    def removeLvsManagerConifghForCluster(self,cluster_id):
        self.db['LvsManagerConfig'].remove({"cluster_id":cluster_id})
        return True

    def getLvsManagerConfigSearchvip(self,vip):
        result = self.db['LvsManagerConfig'].find({"vip_group":{"$elemMatch":{"vip":{"$regex":vip}}}})
        return list(result)
    
    def getLvsManagerConfigSearchrs(self,rs):
        result = self.db['LvsManagerConfig'].find({"rs":{"$elemMatch":{"manager_ip":{"$regex":rs}}}})
        return result
    
    def UpdateLvsManagerConfigVipInstanceToOffline(self,id):
        self.db['LvsManagerConfig'].update({"_id":ObjectId(id)},{"$set":{"status":"offline"}})
        return True
    
    def UpdateLvsManagerConfigVipInstanceToOnline(self,id):
        self.db['LvsManagerConfig'].update({"_id":ObjectId(id)},{"$set":{"status":"online"}})
        return True
    
    def getAccountOne(self,user):
        result = self.db['LvsAccount'].find_one({"username":user})
        return result
    
    def InsertAccount(self,user_data):
        result = self.db['LvsAccount'].insert(user_data)
        return True
    
    def updateAccountLogintime(self,user,time):
        self.db['LvsAccount'].update({"username":user},{"$set":{"login_time":time}})