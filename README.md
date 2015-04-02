# About
lvs-manager 是lvs cluster的web管理系统

# 功能
* 性能图标
   * lvs集群整体流量
   * 各vip的流量
   * lvs集群整体包数目
   * 各vip的包数目
* lvs管理
   * 页面配置上线,下线,修改,回滚,发布服
   * 管理keepalived
   * 查看业务负责人等信息
* lvs数据报表
   * 当天集群的流量曲线
   * 集群vip max 5业务的平均流量
   * 集群下每个业务的最大流量,平均流量

# Requirements
* pymongo
* salt
* tornado
* yaml
* urllib2

# Screenshots
## 性能图表
![lvs_charts](https://github.com/lxcong/lvs-manager/blob/master/screenshots/lvs_charts.png?raw=true)

## lvs管理
![lvs_manger_index](https://github.com/lxcong/lvs-manager/blob/master/screenshots/lvs_manager_index.png?raw=true)

## lvs管理-添加服务
![lvs_manager_add](https://github.com/lxcong/lvs-manager/blob/master/screenshots/lvs_manager_add.png?raw=true)