#!/usr/bin/env python
# -*- coding: utf8 -*- 
import sys, time ,os
import json
import statsd

cur_dir = os.path.dirname(os.path.abspath(__file__))

lvsstats_lastfile = os.path.join(cur_dir,'tmp/','lastlvsstats.tmp')
lvsstats_result_file = os.path.join(cur_dir,'data/','lvsstats')
iftraffic_lastfile = '/tmp/lastiftraffic.tmp'
iftraffic_result_file = '/tmp/iftraffic'
lvstraffic_lastfile = os.path.join(cur_dir,'tmp/','lastlvstraffic.tmp')
lvstraffic_result_file = os.path.join(cur_dir,'data/','lvstraffic')

prefix = "lvs.dg.172_28_26_82."
statsd_server = "10.10.18.20"
statsd_port = 9101

class MyDaemon():
    def __init__(self):
        self.c = statsd.StatsClient(statsd_server, statsd_port, prefix=prefix)

    def run(self):
        while True:
            #self.lvsstats()
            self.lvstraffic()
            #self.iftraffic()
            time.sleep(10)

    def push_statsd(self,k,v,type):
        if type == 'time':
            self.c.timing(k, v)
        return None

    def lvstraffic(self):
        timestamp = time.time()
        if not os.path.isfile(lvstraffic_lastfile):
            result = self.lvstraffic_resolve()
            f = open(lvstraffic_lastfile,'w')
            f.write(result)
            f.close()
            return None
        last_result = json.loads(open(lvstraffic_lastfile).read())
        now = self.lvstraffic_resolve()
        now_result = json.loads(now)
        f = open(lvstraffic_lastfile,'w')
        f.write(now)
        f.close()

        list = []
        for vip_dict in now_result:
            for last_vip_dict in last_result:
                if vip_dict['vip'] == last_vip_dict['vip']:
                    last_vip_value = last_vip_dict
            if not last_vip_value: continue
            
            vip_per_dict =  self.lvstraffic_count_per(last_vip_value,vip_dict)
            list.append(vip_per_dict)
            statsd_vip = vip_per_dict['vip']
            _statsd_vip = statsd_vip.replace('.','_').replace(':','_')
            self.push_statsd('vip.%s.conns' % (_statsd_vip),vip_per_dict['conns_sum_per'],'time')
            self.push_statsd('vip.%s.inpkts' % (_statsd_vip),vip_per_dict['inpkts_sum_per'],'time')
            self.push_statsd('vip.%s.outpkts' % (_statsd_vip),vip_per_dict['outpkts_sum_per'],'time')
            self.push_statsd('vip.%s.inbytes' % (_statsd_vip),vip_per_dict['inbytes_sum_per'],'time')
            self.push_statsd('vip.%s.outbytes' % (_statsd_vip),vip_per_dict['outbytes_sum_per'],'time')
        try:
            f = open(lvstraffic_result_file,'w')
            f.write(json.dumps(list,sort_keys=False, indent=4, separators=(',', ': ')))
            f.close
            return True
        except Exception, e:
            return False

    def lvstraffic_count_per(self,last,now):
        dict = {}
        list = []
        dict['conns_sum_per'] = now['conns_sum'] - last['conns_sum']
        dict['inpkts_sum_per'] = now['inpkts_sum'] - last['inpkts_sum']
        dict['outpkts_sum_per'] = now['outpkts_sum'] - last['outpkts_sum']
        dict['inbytes_sum_per'] = now['inbytes_sum'] - last['inbytes_sum']
        dict['outbytes_sum_per'] = now['outbytes_sum'] - last['outbytes_sum']
        dict['vip'] = now['vip']
        return dict


    '''
    [{"vip": "x.x.x.x:x", 
      "conns_sum": 10, 
      "inpkts_sum": 10, 
      "outpkts_sum": 10, 
      "inbytes_sum": 10, 
      "outpkts_sum":10,
      "node": [{"rs": "x.x.x.x:x" ,"conns": 10,"inpkts": 10, "outpkts": 10,"inbytes":100, "outbytes": 100 }]},
    {"vip": "x.x.x.x:x", 
      "conns_sum": 10, 
      "inpkts_sum": 10, 
      "outpkts_sum": 10, 
      "inbytes_sum": 10, 
      "outpkts_sum":10,
      "node": [{"rs": "x.x.x.x:x" ,"conns": 10,"inpkts": 10, "outpkts": 10,"inbytes":100, "outbytes": 100 }]}
    ]
    '''
    def lvstraffic_resolve(self):
        Conn = []
        node_list = []
        dict = {}
        num = 0
        cmd = "ipvsadm -Ln --stats --exact"
        lines = os.popen(cmd).readlines()
        for line in lines[3:]:
            num += 1
            con = line.split()
            if con[0] == "TCP" or con[0] == "UDP":
                if num == 1:
                        pass
                else:
                        Conn.append(dict)
                dict = {}
                dict['conns_sum'] =  int(con[2])
                dict['inpkts_sum'] = int(con[3])
                dict['outpkts_sum'] = int(con[4])
                dict['inbytes_sum'] = int(con[5])
                dict['outbytes_sum'] = int(con[6])
                dict['vip'] = str(con[1])
                dict['node'] = []
                continue
            node_dict = {"rs":str(con[1]),"conns":int(con[2]),"inpkts":int(con[3]),"outpkts":int(con[4]),"inbytes":int(con[5]),"outbytes":int(con[6])}
            dict['node'].append(node_dict)
            if num == len(lines[3:]):
                Conn.append(dict)
        return json.dumps(Conn, sort_keys=False, indent=4, separators=(',', ': '))

    def lvsstats(self):
        timestamp = time.time()
        if not os.path.isfile(lvsstats_lastfile):
            result = self.lvsstatsresolve()
            f = open(lvsstats_lastfile,'w')
            f.write(result)
            f.close()
            return None
        last_result = json.loads(open(lvsstats_lastfile).read())
        now = self.lvsstatsresolve()
        now_result = json.loads(now)
        f = open(lvsstats_lastfile,'w')
        f.write(now)
        f.close()

        dict = {}
        for (k,v) in now_result.items():
            new_key = '%s_per' % k
            dict[new_key] = (v - last_result[k]) / 10
        dict['time'] = timestamp
        try:
            f = open(lvsstats_result_file,'w')
            f.write(json.dumps(dict))
            f.close
            return True
        except Exception, e:
            return False

    def lvsstatsresolve(self):
        conns = 0
        in_pks = 0
        out_pks = 0
        in_bytes = 0
        out_bytes = 0
        f = open("/proc/net/ip_vs_stats")
        lines = f.readlines()
        f.close()
        for line in lines[2:]:
            con = line.split(':')[1].split()
            conns += int(con[0])
            in_pks += int(con[1])
            out_pks += int(con[2])
            in_bytes += int(con[3])
            out_bytes += int(con[4])
        result = {"conns":conns,"in_pks":in_pks,"out_pks":out_pks,"in_bytes":in_bytes,"out_bytes":out_bytes}
        return json.dumps(result)

if __name__ == "__main__":
    daemon = MyDaemon()
    print "ksmonitor is running"
    daemon.run()
