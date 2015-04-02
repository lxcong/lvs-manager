#!/usr/bin/python 
# -*- coding: utf8 -*- 
import os,sys,logging
from multiprocessing import Process, Queue, current_process
from pymongo import MongoClient
#from pymongo import MongoClient
import datetime
import yaml
import urllib2
import json
import time
from datadiff import diff

cur_dir = os.path.dirname(os.path.abspath(__file__))

settings = {
    'config': os.path.join(cur_dir,"config.yaml"),
    'logfile': os.path.join(cur_dir,"log","system.log"),
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
    #st = logging.StreamHandler()
    #st.setLevel(logging.INFO)
    #st.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
    #logging.addHandler(st)
except AttributeError as err:
    print("Error: %s %s" %(err, settings['logfile']))
    sys.exit(2)

class MongoSession():
    def __init__(self):
        self.conn = MongoClient(settings['mongodb'],settings['mongodb_port'])
        #self.conn = MongoClient(settings['mongodb'],settings['mongodb_port'],auto_start_request=True)
        self.db = self.conn[settings['db']]

    def close(self):
        try:
            self.conn.end_request()
            self.conn.close()
            logging.info('close mongo connection Success !')
        except Exception, e:
            logging.warning('close mongo connection fail !')

    def insert(self,id,data_type,data):
        _time = time.time()
        collection = self.db[data_type]
        insert_data = {"id":id,"time":_time,"data": data}
        
        try:
            _id = collection.insert(insert_data)
            self.conn.end_request()
            logging.info('Insert data (ID:%s) Success !' % id)
            return id
        except Exception, e:
            return e

    def insert_demo(self,data_type,insert_data):
        _time = time.time()
        collection = self.db[data_type]
        try:
            _id = collection.insert(insert_data)
            self.conn.end_request()
            logging.info('Method: Insert | table: %s | result: Success ' % (data_type))
            return id
        except Exception, e:
            logging.warning('Method: Insert | table: %s | result: %s' % (data_type,e))

    def upsert(self,data_type,find,update):
        collection = self.db[data_type]
        try:
            _id = collection.update(find,update,True)
            self.conn.end_request()
            logging.info('Method: Upsert | table: %s | result: Success ' % (data_type))
            return id
        except Exception, e:
            logging.warning('Method: Upsert | table: %s | result: %s' % (data_type,e))

    def update(self,data_type,find,update):
        collection = self.db[data_type]
        try:
            _id = collection.update(find,update)
            self.conn.end_request()
            logging.info('Method: Update | table: %s | result: Success ' % (data_type))
            return id
        except Exception, e:
            logging.warning('Method: Update | table: %s | result: %s' % (data_type,e))

    def find_one(self,data_type,find):
        collection = self.db[data_type]
        try:
            _id = collection.find_one(find)
            self.conn.end_request()
            logging.info('Method: FindOne | table: %s | result: Success ' % (data_type))
            return _id
        except Exception, e:
            logging.warning('Method: FindOne | table: %s | result: %s' % (data_type,e))

def getmonitordata(agent,port,data_type):
    url = 'http://%s:%s/node/%s/' % (agent,port,data_type)
    fails = 0 
    retry = 5
    while True:
        try:
            if fails > retry:
                logging.warning('Get Monitor Data Failed | %s' % url)
                return None
            res = urllib2.urlopen(url, timeout=2)
            return json.loads(res.read())
        except Exception, e:
            fails += 1 
        else:
            logging.info('Get Monitor Data Success | %s ' % url)
            break

def getlvstrffic(agent_ip,port):
    url = 'http://%s:%s/node/GetLvsTraffic/' % (agent_ip,port)
    fails = 0 
    retry = 5
    while True:
        try:
            if fails > retry:
                logging.warning('Get Monitor Data Failed | %s' % url)
                return None
            res = urllib2.urlopen(url, timeout=2)
            return json.loads(res.read())
        except Exception, e:
            fails += 1 
        else:
            logging.info('Get Monitor Data Success | %s ' % url)
            break

def lvstraffic_handler(id,agent_ip,agent_port,cluster,_time):
    mongo_task = MongoSession()
    sum_dict = {}
    inpkts_sum = 0
    outpkts_sum = 0
    inbytes_sum = 0
    outbytes_sum = 0
    conns_sum = 0
    data = getlvstrffic(agent_ip,agent_port)
    for vip_dict in data:
        vip_dict["id"] = id
        vip_dict["time"] = _time
        inpkts_sum += vip_dict['inpkts_sum_per']
        outpkts_sum += vip_dict['outpkts_sum_per']
        inbytes_sum += vip_dict['inbytes_sum_per']
        outbytes_sum += vip_dict['outbytes_sum_per']
        conns_sum += vip_dict['conns_sum_per']
        vip_dict["cluster"] = cluster
        results = mongo_task.insert_demo('GetLvsTraffic_demo',vip_dict)
        find = {"cluster":cluster,"time":_time,"vip":vip_dict["vip"]}
        update = update = {"$inc": {"inpkts_sum_per":vip_dict["inpkts_sum_per"],"outpkts_sum_per":vip_dict["outpkts_sum_per"] ,"inbytes_sum_per":vip_dict["inbytes_sum_per"],"outbytes_sum_per":vip_dict["outbytes_sum_per"],"conns_sum_per":vip_dict["conns_sum_per"]}}
        mongo_task.upsert('GetLvsTraffic_cluster',find,update)
    sum_dict["inpkts_sum"] = inpkts_sum
    sum_dict["outpkts_sum"] = outpkts_sum
    sum_dict["inbytes_sum"] = inbytes_sum
    sum_dict["outbytes_sum"] = outbytes_sum
    sum_dict["conns_sum"] = conns_sum
    sum_dict["time"] = _time
    sum_dict["id"] = id
    sum_dict["cluster"] = cluster
    mongo_task.insert_demo('GetLvsTraffic_sum',sum_dict)
    find = {"cluster":cluster,"time":_time}
    update = {"$inc": {"inpkts_sum":inpkts_sum ,"outpkts_sum":outpkts_sum ,"inbytes_sum":inbytes_sum,"outbytes_sum":outbytes_sum,"conns_sum":conns_sum}}
    mongo_task.upsert('GetLvsTraffic_cluster_sum',find,update)
    mongo_task.close()
    return None

def getlvsstatus(agent_ip,port):
    url = 'http://%s:%s/node/GetLvsStatus/' % (agent_ip,port)
    fails = 0 
    retry = 5
    while True:
        try:
            if fails > retry:
                logging.warning('Get Monitor Data Failed | %s' % url)
                return None
            res = urllib2.urlopen(url, timeout=2)
            return json.loads(res.read())
        except Exception, e:
            fails += 1 
        else:
            logging.info('Get Monitor Data Success | %s ' % url)

def lvsstatus_handler(id,agent_ip,agent_port,cluster,_time):
    mongo_task = MongoSession()
    data = getlvsstatus(agent_ip,agent_port)
    last_data = mongo_task.find_one('GetLvsConn_status',{"id":id})
    now_status = data
    if last_data:
        last_status = last_data['node']
        _diff = diff(now_status,last_status)
        if _diff:
            dict_diff = {"id":id,"time":_time,"diff":str(_diff),"cluster":cluster}
            mongo_task.insert_demo('GetLvsConn_diff',dict_diff)
    find = {"id":id}
    dict = {"id":id,"time":_time,"cluster":cluster,"node":data}
    mongo_task.upsert('GetLvsConn_status',find,dict)
    mongo_task.close()

def worker(input, output):
    for func in iter(input.get,'STOP'):
        #解析出config.yaml里面的agent
        agent_dict = func['agent']
        pid = os.getpid()
        logging.info('tasks.get | pid: %s  tasks: %s is connection' %(pid,agent_dict['id']))
        _time = func['time']
        id = agent_dict['id']
        agent = agent_dict['ipadd']
        port = agent_dict['port']
        cluster = agent_dict['cluster']
        #for data_type in agent_dict['data_type']:
        #    #data = getmonitordata(agent,port,data_type)
        #    #mongo_task = MongoSession()
        #    #results = mongo_task.insert(id,data_type,data)
        #    #mongo_task.close()
        #    output.put('ok')
        _timenow = time.time()
        lvstraffic_handler(id,agent,port,cluster,_time)
        lvsstatus_handler(id,agent,port,cluster,_time)
        _timenow1 = time.time() - _timenow
        logging.warning(_timenow1)
        #for i in range(50):
        #    mongo_task = MongoSession()
        #    mongo_task.insert_demo('Test',{"test":1})
        #    time.sleep(1)
        #    mongo_task.close()
        #    output.put('ok')


def main():
    logging.info('##################Task Begining##################')
    #load config
    try:
        config = yaml.load(open(settings['config']))
        logging.info('load config.yaml Success')
    except Exception, e:
        print 'load config error!!'
    #进程数
    #NUMBER_OF_PROCESSES = config['base']['NUMBER_OF_PROCESSES']

    #agent 列表
    agent_list = config['agent']
    # Create queues 消息用于进程通信
    task_queue = Queue()
    done_queue = Queue()

    #agent有多少就开启多少个进程数
    NUMBER_OF_PROCESSES = len(agent_list)

    _time = time.time()

    logging.info('Agentlist: %s' % [a['id'] for a in agent_list]) 
    #submit tasks
    for agent in agent_list:
        dict = {}
    	dict["time"] = _time
        dict["agent"] = agent
        task_queue.put(dict)
        logging.info('tasks.put | tasks: %s ' %(agent['id']))
            
    #进程开启
    record = []
    
    for i in range(NUMBER_OF_PROCESSES):
        process = Process(target=worker, args=(task_queue, done_queue))
        process.start()
        record.append(process)

    #打印结果
    #for i in range(len(agent_list)):
    #    logging.info(done_queue.get())

    #告诉子进程要结束了
    for i in range(NUMBER_OF_PROCESSES):
        task_queue.put('STOP')
        logging.info("Stopping Process #%s" % i)

    #告诉父进程要结束了
    for process in record:
        process.join()

if __name__ == "__main__":
    main()