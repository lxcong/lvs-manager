#!/usr/bin/python 
# -*- coding: utf8 -*- 
import os,sys,logging
from pymongo import MongoClient
import yaml
import operator
import time
import datetime

cur_dir = os.path.dirname(os.path.abspath(__file__))
settings = {
    'config': os.path.join(cur_dir,"config.yaml"),
    'logfile': os.path.join(cur_dir,"log","lvsreport.log"),
    'mongodb': 'localhost',
    'mongodb_port': 27017,
    'db': 'LvsMonitor',
}


try:
    logging.basicConfig(level=logging.NOTSET,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=settings['logfile'],
        filemode='a')
    logging = logging.getLogger()

except AttributeError as err:
    print("Error: %s %s" %(err, settings['logfile']))
    sys.exit(2)
    
def get_yesterday():
    dt = datetime.date.today() - datetime.timedelta(1)
    return datetime.datetime.strftime(dt,'%Y-%m-%d')

class lvsreport():
    def __init__(self,dt):
        self.dt = dt
        self.start = self.datetotimestamp('%s 00:00:00' %dt)
        self.end = self.datetotimestamp('%s 23:59:59' %dt)
        self.conn = MongoClient(settings['mongodb'],settings['mongodb_port'])
        self.db = self.conn[settings['db']]
        try:
            self.cluster_dict = yaml.load(open(settings['config']))['cluster']
        except Exception, e:
            raise e

    def search_vip_info(self,cluster_id,vip):
        '''
        从LvsPublish表找出vip的info信息
        '''
        try:
            last_cluster_info = self.db['LvsManagerPublish'].find({"cluster_id":cluster_id}).sort("time",-1)[0]
            for i in last_cluster_info['server']:
                for vip_gourp in i['vip_group']:
                    _vip = '%s:%s' %(vip_gourp['vip'],vip_gourp['port'])
                    if vip == _vip:
                        return i
            return False
        except Exception, e:
            return False

    def timestamptodate(self,timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def datetotimestamp(self,date):
        time_obj = time.strptime(date,"%Y-%m-%d %H:%M:%S")
        return time.mktime(time_obj)

    def mongo_cluster_max_min_traffic(self,id):
        '''
        求集群流量的最大值最小值平均值差异值与发生时间
        '''
        cluster_traffic_sum = {}
        #in方向的最大最小值
        #in_traffic_max_dict = list(self.db['GetLvsTraffic_cluster_sum'].find({"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}}).sort("inbytes_sum",-1).limit(1))[0]
        #in_traffic_min_dict = list(self.db['GetLvsTraffic_cluster_sum'].find({"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}}).sort("inbytes_sum" ,1).limit(1))[0]
        #cluster_traffic_sum['in_traffic_max'] = in_traffic_max_dict['inbytes_sum']
        #cluster_traffic_sum['in_traffic_max_time'] = in_traffic_max_dict['time']
        #cluster_traffic_sum['in_traffic_min'] = in_traffic_min_dict['inbytes_sum']
        #cluster_traffic_sum['in_traffic_min_time'] = in_traffic_min_dict['time']
        #out方向的最大最小值
        #out_traffic_max_dict = list(self.db['GetLvsTraffic_cluster_sum'].find({"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}}).sort("outbytes_sum" ,-1).limit(1))[0]
        #out_traffic_min_dict = list(self.db['GetLvsTraffic_cluster_sum'].find({"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}}).sort("outbytes_sum" ,1).limit(1))[0]
        #cluster_traffic_sum['out_traffic_max'] = out_traffic_max_dict['outbytes_sum']
        #cluster_traffic_sum['out_traffic_max_time'] = out_traffic_max_dict['time']
        #cluster_traffic_sum['out_traffic_min'] = out_traffic_min_dict['outbytes_sum']
        #cluster_traffic_sum['out_traffic_min_time'] = out_traffic_min_dict['time']
        #diff
        #cluster_traffic_sum['in_traffic_diff'] = cluster_traffic_sum['in_traffic_max'] - cluster_traffic_sum['in_traffic_min'] 
        #cluster_traffic_sum['out_traffic_diff'] = cluster_traffic_sum['out_traffic_max'] - cluster_traffic_sum['out_traffic_min']
        #平均值
        in_traffic_avg_dict = self.db['GetLvsTraffic_cluster_sum'].aggregate([{"$match":{"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}}},{"$group":{"_id":'null',"avg":{"$avg":"$inbytes_sum"}}}])
        out_traffic_avg_dict = self.db['GetLvsTraffic_cluster_sum'].aggregate([{"$match":{"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}}},{"$group":{"_id":'null',"avg":{"$avg":"$outbytes_sum"}}}])
        if len(in_traffic_avg_dict['result']) != 0:
            cluster_traffic_sum['in_traffic_avg'] = in_traffic_avg_dict['result'][0]['avg']
        else:
            cluster_traffic_sum['in_traffic_avg'] = None
        if len(out_traffic_avg_dict['result']) != 0:
            cluster_traffic_sum['out_traffic_avg'] = out_traffic_avg_dict['result'][0]['avg']
        else:
            cluster_traffic_sum['out_traffic_avg'] = None
        return cluster_traffic_sum


    def mongo_vip_max_min_traiffic(self,vip):
        '''
        求单个VIP的最大值最小值平均值差异值与发生时间
        '''
        vip_traffic = {}
        vip_traffic['vip'] = vip
        in_traffic_max_dict = list(self.db['GetLvsTraffic_cluster'].find({"vip":vip,"time":{"$lt":self.end ,"$gt":self.start}}).sort("inbytes_sum_per" ,-1).limit(1))[0]
        in_traffic_min_dict = list(self.db['GetLvsTraffic_cluster'].find({"vip":vip,"time":{"$lt":self.end ,"$gt":self.start}}).sort("inbytes_sum_per" ,1).limit(1))[0]
        vip_traffic['in_traffic_max'] = in_traffic_max_dict['inbytes_sum_per']
        vip_traffic['in_traffic_max_time'] = in_traffic_max_dict['time']
        vip_traffic['in_traffic_min'] = in_traffic_min_dict['inbytes_sum_per']
        vip_traffic['in_traffic_min_time'] = in_traffic_min_dict['time']
        out_traffic_max_dict = list(self.db['GetLvsTraffic_cluster'].find({"vip":vip,"time":{"$lt":self.end ,"$gt":self.start}}).sort("outbytes_sum_per" ,-1).limit(1))[0]
        out_traffic_min_dict = list(self.db['GetLvsTraffic_cluster'].find({"vip":vip,"time":{"$lt":self.end ,"$gt":self.start}}).sort("outbytes_sum_per" ,1).limit(1))[0]
        vip_traffic['out_traffic_max'] = out_traffic_max_dict['outbytes_sum_per']
        vip_traffic['out_traffic_max_time'] = out_traffic_max_dict['time']
        vip_traffic['out_traffic_min'] = out_traffic_min_dict['outbytes_sum_per']
        vip_traffic['out_traffic_min_time'] = out_traffic_min_dict['time']
        #diff
        vip_traffic['in_traffic_diff'] = vip_traffic['in_traffic_max'] - vip_traffic['in_traffic_min']
        vip_traffic['out_traffic_diff'] = vip_traffic['out_traffic_max'] - vip_traffic['out_traffic_min']
        #平均值
        in_traffic_avg_dict = self.db['GetLvsTraffic_cluster'].aggregate([{"$match":{"vip":vip,"time":{"$lt":self.end ,"$gt":self.start}}},{"$group":{"_id":'null',"avg":{"$avg":"$inbytes_sum_per"}}}])
        out_traffic_avg_dict = self.db['GetLvsTraffic_cluster'].aggregate([{"$match":{"vip":vip,"time":{"$lt":self.end ,"$gt":self.start}}},{"$group":{"_id":'null',"avg":{"$avg":"$outbytes_sum_per"}}}])
        if len(in_traffic_avg_dict['result']) != 0:
            vip_traffic['in_traffic_avg'] = in_traffic_avg_dict['result'][0]['avg']
        else:
            vip_traffic['in_traffic_avg'] = None
        if len(out_traffic_avg_dict['result']) != 0:
            vip_traffic['out_traffic_avg'] = out_traffic_avg_dict['result'][0]['avg']
        else:
            vip_traffic['out_traffic_avg'] = None
        return vip_traffic

    def mongo_vip_traffic(self,id):
        '''
        求集群所有VIP的流量最大值最小值平均值
        '''
        list = []
        func = '''function(obj, prev) {
                }'''
        initial = {}
        mongo_vip_list = self.db['GetLvsTraffic_cluster'].group(['cluster','vip'],{"cluster":id,"time":{"$lt":self.end ,"$gt":self.start}},initial,func)
        for vip in mongo_vip_list:
            vip = vip['vip']
            vip_info = self.search_vip_info(id, vip)
            dict = self.mongo_vip_max_min_traiffic(vip)
            if vip_info:
                dict['descript'] = vip_info['descript']
                dict['owners'] = vip_info['owners']
            else:
                dict['descript'] = 'UnKown'
                dict['owners'] = 'UnKown'
            list.append(dict)
        return list
    
    def find_in_vip_max_five(self,vip_traffic_sum_dict):
        '''
        find input tfaffic max 5 at vip_dict
        '''
        sorted_vip_traffic_sum = sorted(vip_traffic_sum_dict, key=lambda i: i['in_traffic_avg'],reverse=True)
        in_max_five = sorted_vip_traffic_sum[:5]
        return in_max_five
    
    def find_out_vip_max_five(self,vip_traffic_sum_dict):
        '''
        find output tfaffic max 5 at vip_dict
        '''
        sorted_vip_traffic_sum = sorted(vip_traffic_sum_dict, key=lambda i: i['out_traffic_avg'],reverse=True)
        out_max_five = sorted_vip_traffic_sum[:5]
        return out_max_five
    
    def find_cluster_diff_sum(self,id):
        cluster_diff_sum = self.db['GetLvsConn_diff'].find({"id":id,"time":{"$lt":self.end ,"$gt":self.start}}).count()
        return cluster_diff_sum
    
    
    def insert_result_lvsreport(self,dict):
        self.db['LvsReport'].insert(dict)
        return None
        
    def cluster_report(self,cluster):
        id = cluster['id']
        descript = cluster['descript']
        lb_list = cluster['agent']

        dict = {}
        #id
        dict['id'] = id
        #descript
        dict['descript'] = descript
        #Report时间
        dict['time'] = self.dt
        #集群总流量统计数据
        dict['cluster_traffic_sum'] = self.mongo_cluster_max_min_traffic(id)
        #集群内所有VIP的统计数据
        vip_traffic_sum = self.mongo_vip_traffic(id)
        dict['vip_traffic_sum'] = vip_traffic_sum
        #集群中VIP业务平均流量前五大
        dict['in_vip_traffic_max_five'] = self.find_in_vip_max_five(vip_traffic_sum)
        dict['out_vip_traffic_max_five'] = self.find_out_vip_max_five(vip_traffic_sum)
        #集群状态发生的状态变化次数
        dict['cluster_diff_sum'] = self.find_cluster_diff_sum(id)
        
        return dict
        
    def run(self):
        for cluster in self.cluster_dict:
            dict = self.cluster_report(cluster)
            #存入数据库LvsReport
            self.insert_result_lvsreport(dict)

if __name__ == "__main__":
    dt = get_yesterday()
    handler = lvsreport(dt)
    handler.run()