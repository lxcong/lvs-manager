#!/usr/bin/env python
# -*- coding: utf8 -*- 
import os
import yaml
from tornado.options import define, options

cur_dir = os.path.dirname(os.path.abspath(__file__))

define("port", default=8888, help="run on the given port", type=int)
define("mongodb", default="localhost", help="mongodb host")
define("mongodb_port", default=27017, help="mongodb port")
define("db", default="LvsMonitor", help="default Lvs Monitor Db Name")
define("config", default=os.path.join(cur_dir,"../../","config.yaml"), help="config.yaml file")
define("publishdir", default=os.path.join(cur_dir,"lvspublish"), help="lvspublish dir")
define("ksso_url", default="https://sso.xxx.xxx/",help="ksso url")
define("lvs_url", default="http://lvs.xxx.xxx/",help="lvs_url")
define("cookies_expires", default=1,help="cookies_expires_days")

config = yaml.load(open(options.config))
#agent列表
agentlist = config['agent']
