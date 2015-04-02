#!/usr/bin/env python
# -*- coding: utf8 -*- 
import os
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
from tornado.options import define, options
from setting import config ,agentlist

#import api class
import api
import control
# Have one global connection to the blog DB across all handlers
#db = motor.MotorClient(host=options.mongodb,port=options.mongodb_port).open_sync()[options.db]
cur_dir = os.path.dirname(os.path.abspath(__file__))

class mongo_conn():
    def __init__(self):
        self.conn = Connection(options.mongodb,options.mongodb_port)
    def db(self):
        return self.conn[options.db]

class Application(tornado.web.Application):
    def __init__(self):
        api_path = [
            (r"/api/agentinfo/", api.AgentInfo),
            (r"/api/clusterinfo/", api.ClusterInfo),
            (r"/api/getcpudetail/", api.GetCpuDetail),
            (r"/api/getcpuinfo/", api.GetCpuInfo),
            (r"/api/gethddinfo/", api.GetHddInfo),
            (r"/api/getiftraffic/", api.GetIfTraffic),
            (r"/api/getloadavg/", api.GetLoadAvg),
            (r"/api/getlvsconn/", api.GetLvsConn),
            (r"/api/getlvsextstatssumm/", api.GetLvsExtStatsSumm),
            (r"/api/getlvsstatssumm/", api.GetLvsStatsSumm),
            (r"/api/getmeminfo/", api.GetMemInfo),
            (r"/api/getlvstraffic/", api.GetLvsTraffic),
            (r"/api/getlvstrafficvip/", api.GetLvsTrafficVip),
            (r"/api/getlvstrafficcluster/", api.GetLvsTrafficCluster),
            (r"/api/getlvstrafficclustervip/", api.GetLvsTrafficClusterVip),
            (r"/api/getlvsclusterviplist/", api.GetLvsClusterVipList),
            (r"/api/alert", api.LvsAlertApiMessage),
            (r"/api/getclusterinfo", api.getClusterInfo),
        ]

        web_path = [
            (r"/", control.HomeHandler),
            (r"/login", control.Login),
            (r"/loginout", control.LoginOut),
            (r"/charts/", control.ChartsHandler),
            (r"/status/", control.Status),
            (r"/cluster_status/", control.ClusterStatus),
            (r"/lb_status/", control.LbStatus),
            (r"/lb_status_table", control.LbStatusTable),
            (r"/lb_vip_status_table", control.LbStatusVipTable),
            (r"/lb_status_diff/", control.LbStatusDiff),
            (r"/lb_status_diff_talbe", control.LbDiffTable),
            (r"/lb_status_diff_agent_table", control.lbDiffAgentTable),
            (r"/lb_status_publish/", control.Publish),
            (r"/lb_status_publish_networktest", control.PublishNetworkTest),
            (r"/lb_status_publish_infoyaml", control.PublishInfoYaml),
            (r"/lvsreport/", control.LvsReport),
            (r"/lvsalert/", control.LvsAlert),
            (r"/lvsmanager/", control.lvsManager),
            (r"/lvsmanager_deploy/", control.lvsManagerDeploy),
            (r"/lvsmanager_deploy_add/", control.lvsManagerDeployAdd),
            (r"/lvsmanager_deploy_del/", control.lvsManagerDeployDel),
            (r"/lvsmanager_deploy_edit/", control.lvsManagerDeployEdit),
            (r"/lvsmanager_deploy_offline/", control.lvsManagerDeployOffline),
            (r"/lvsmanager_deploy_online/", control.lvsManagerDeployOnline),
            (r"/lvsmanager_deploy_get_rs_list/", control.lvsManagerDeployGetRsList),
            (r"/lvsmanager_publish/", control.lvsManagerPublish),
            (r"/lvsmanager_rollback/", control.lvsManagerRollback),
            (r"/lvsmanager_keepalived_reload/", control.lvsManagerKeepalivedReload),
            (r"/lvsmanager_keepalived_start_or_stop/", control.lvsManagerKeepalivedStartOrStop),
            (r"/lvsmanager_keepalived_ipvsadm/", control.lvsManagerKeepalivedIpvsadm),
            (r"/lvsmanager_search/", control.lvsManagerSearch),
        ]

        handlers = api_path + web_path
        settings = dict(
            template_path=os.path.join(cur_dir,'templates/'),
            static_path=os.path.join(cur_dir,'lib/'),
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/",
        )
        tornado.web.Application.__init__(self, handlers,**settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
