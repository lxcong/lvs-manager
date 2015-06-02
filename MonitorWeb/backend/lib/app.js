$(document).ready(function(){
    $("select").selectpicker({style: 'btn-primary', menuStyle: 'dropdown-inverse'});

    $('#TimeTab a').click(function (e) {
      e.preventDefault();
      $(this).tab('show');
      console.log(this) ;
    })

    $('#NavTab a').click(function (e) {
      e.preventDefault();
      $(this).tab('show');
      console.log(this) ;
    })

      var tpl =  '<div class="row">' +
        '<select id="cluster_filter_tpl"  class="inline" ></select>' +
        '<select id="lb_filter_tpl"  class="inline" ></select>' +
        '<input id="lvstraffic_record" type="text" hidden>' +
      '</div>' +
      '<ul class="nav nav-tabs" id="TimeTab">' +
        '<li class="active" ><a href="#1A" data-toggle="tab">近一小时</a></li>' +
        '<li><a href="#2A" data-toggle="tab">近一天</a></li>' +
        '<li><a href="#3A" data-toggle="tab">近一个月</a></li>' +
      '</ul>' +
      '<div id="body_tpl">' +
      '</div>' ;
      create_tpl(tpl) ;
      init_cluster_filter() ;
      
     time_type = 'hours'
     $('#TimeTab a').click(function (e) {
       e.preventDefault();
       $(this).tab('show');
       console.log(this) ;
       var id = $("#cluster_filter_tpl").val() ;
       var _time_type = $(this).attr("href")
       switch (_time_type) {
        case "#1A":
            time_type = 'hours' ;
            break;
        case "#2A":
            time_type = 'days' ;
            break;
        case "#3A":
            time_type = 'month' ;
            break;
       }
       _local_cluster(id,time_type) ;

     })

      $.ajax({
          url: '/api/clusterinfo/' ,
          dataType: "json",
          cache: false ,
          success: function(data) {
                console.log(data);
               _local_cluster(data[0].id,time_type) ;
          },
      });

      $("#lb_filter_tpl").change(function() {
          var id = $(this).val() ;
          _local(id,time_type) ;
      });

      $("#cluster_filter_tpl").change(function() {
          var id = $(this).val() ;
          init_lb_filter(id) ;
          _local_cluster(id,time_type) ;
      });

      function _local(id,time_type) {
          var tpl =  '<dl class="palette palette-green-sea">' +
                    '<p class="text-center">{{$T}}</p>' +
                  '</dl>' +
                  '<dl class="palette palette-turquoise">' +
                    '<div id="charts_body" ></div>' +
                  '</dl>'  ;
          create_agent_tpl(id,tpl) ;

          switch (time_type) {
            case "hours":
              end = Math.round(+new Date()/1000);
              start = end - 3600 ;
              break;
            case "days":
              end = Math.round(+new Date()/1000);
              start = end - 86400 ; 
              break;
            case "month":
              end = Math.round(+new Date()/1000);
              start = end - 2592000 ; 
              break;
            default:
              end = Math.round(+new Date()/1000);
              start = end - 3600 ; 
              break;
          }

          if ( time_type == "hours") {
            end = Math.round(+new Date()/1000);
            start = end - 3600 ;
          }
          else {

          }
          url = '/api/getlvstraffic/?agent=' + id  + '&start=' + start + '&end=' + end
          series = {"inbytes_sum": "IN总流量 bytes/s" , "outbytes_sum": "OUT总流量 bytes/s"}
          init_charts_lvs_traffic(url,'hours',series) ;
      }

      function _local_cluster(id,time_type) {
          var tpl =  '<dl class="palette palette-green-sea">' +
                    '<p class="text-center">{{$T}}</p>' +
                  '</dl>' +
                  '<dl class="palette palette-turquoise">' +
                    '<div id="charts_body" ></div>' +
                  '</dl>'  ;
          create_agent_tpl(id,tpl) ;

          switch (time_type) {
            case "hours":
              end = Math.round(+new Date()/1000);
              start = end - 3600 ;
              break;
            case "days":
              end = Math.round(+new Date()/1000);
              start = end - 86400 ; 
              break;
            case "month":
              end = Math.round(+new Date()/1000);
              start = end - 2592000 ; 
              break;
            default:
              end = Math.round(+new Date()/1000);
              start = end - 3600 ; 
              break;
          }

          if ( time_type == "hours") {
            end = Math.round(+new Date()/1000);
            start = end - 3600 ;
          }
          else {

          }
          url = '/api/getlvstrafficcluster/?agent=' + id  + '&start=' + start + '&end=' + end
          series = {"inbytes_sum": "IN总流量 bytes/s" , "outbytes_sum": "OUT总流量 bytes/s"}
          init_charts_lvs_traffic(url,'hours',series) ;
      }

});

    function init_lb_filter(cluster) {
        $.ajax({
            url: '/api/clusterinfo/' ,
            dataType: "json",
            cache: false ,
            success: function(data) {
                 for (i in data) {
                    id = data[i].id
                    if (id == cluster) {
                        agent_list = data[i].agent
                    } ;
                    var tpl = '{#foreach $T as lb}' +
                            '<option value="{$T.lb}">{$T.lb}</option>' +
                            '{#/for}' ;
                    var tpl_c = $('#lb_filter_tpl').setTemplate(tpl).processTemplate(agent_list) ;


                 };
            },
        });
    } ;

    function init_cluster_filter() {
        $.ajax({
            url: '/api/clusterinfo/' ,
            dataType: "json",
            cache: false ,
            success: function(data) {
                 
                var tpl =   '{#foreach $T as cluster}' +
                            '<option value="{$T.cluster.id}">{$T.cluster.id}</option>' +
                            '{#/for}' ;
                var tpl_c = $('#cluster_filter_tpl').setTemplate(tpl) ;
                console.log(tpl_c) ;
                $('#cluster_filter_tpl').processTemplate(data) ;
                init_lb_filter(data[0].id) ;
            },
        });
    } ;


    function create_tpl(tpl) {
      var tpl_c = $('#tpl').setTemplate(tpl)
      console.log(tpl_c) ;
      $('#tpl').processTemplate();
      $("select").selectpicker({style: 'btn-primary', menuStyle: 'dropdown-inverse'});
    };
    
    function init_fliter_vip_select(obj) {
        var tpl =   '{#foreach $T as vip}' +
                    '<option value="{$T.vip.vip}">{$T.vip.vip}</option>' +
                    '{#/for}' ;
        $("#vip_filter_tpl").setTemplate(tpl).processTemplate(obj)
    };
    
    function init_charts_lvs_traffic(url,time_type,series) {
        var loading=new ol.loading({id:"charts_body"}) ;
        var loading_nav=new ol.loading({id:"charts_nav"}) ;
        
        $.ajax({
            url: url,
            beforeSend: function() { loading.show() ; loading_nav.show() } ,
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert(errorThrown) ;
            },
            success: function (obj) {
                loading.hide() ;
                loading_nav.hide();

                $.each(obj,function(id,id_dict) {
                    tpl = '<div id="' + id + '" style="min-width:400px;height:400px;margin:0 auto;"></div></br>'
                    $("#charts_body").append(tpl) ;
                    _series = [] ;
                    for (i in series) {
                        _series.push({"name":series[i], "data":id_dict[i]}) ;
                    };
                    var arg = {"renderTo": id ,"title": id_dict.title, "time_type": time_type, "series":_series }
                    var traffic_charts = highchartsformat(arg) ;
                    //traffic_charts.series[0].data = id_dict.inbytes_sum ;
                    //traffic_charts.series[1].data = id_dict.outbytes_sum ;
                    var chart = new Highcharts.Chart(traffic_charts) ;
                    init_fliter_vip_select(obj) ;
                });
                //create_charts_tpl(obj);
                //init_fliter_vip_select(obj) ;
                //lvstraffic(obj,'hours');
            },
            cache: false
        });
    
    };

    function init_charts(url,time_type,series) {
        var loading=new ol.loading({id:"viptable_day_table"}) ;
        
        $.ajax({
            url: url,
            beforeSend: function() { loading.show() } ,
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert(errorThrown) ;
            },
            success: function (obj) {
                loading.hide() ;
                $.each(obj,function(id,id_dict) {
                    _series = [] ;
                    for (i in series) {
                        _series.push({"name":series[i], "data":id_dict[i]}) ;
                    };
                    var arg = {"renderTo": 'messagecharts' ,"title": id_dict.title, "time_type": time_type, "series":_series }
                    var traffic_charts = highchartsformat(arg) ;
                    var chart = new Highcharts.Chart(traffic_charts) ;

                });
            },
            cache: false
        });
    
    };

    function create_agent_tpl(id,tpl) {
        var tpl_c = $('#body_tpl').setTemplate(tpl) ;
        $('#body_tpl').processTemplate(id) ;
    
    };
    
    //function create_charts_tpl(obj) {
    //    var tpl = '{#foreach $T as vip_dict}' +
    //               '<div id="{{$T.vip_dict.id}}" style="min-width:400px;height:400px;margin:0 auto;"></div>' +
    //               '</br>' +
    //               '{#/for}'
    //    var tpl_c = $("#charts_body").setTemplate(tpl)
    //    console.log(tpl_c) ;
    //    $("#charts_body").processTemplate(obj) ;
    //};
    
    function format_date_sample(timestamp) {
        var date = new Date(timestamp * 1000) ;
        var hours = date.getHours() ;
        var minutes = date.getMinutes() ;
        return (hours + ':' + minutes) ;
    }
    
    function format_date_full(timestamp) {
        var date = new Date(timestamp * 1000) ;
        var years = date.getFullYear() ;
        var month = date.getMonth() -1 ;
        var day = date.getDate() ;
        var hours = date.getHours() ;
        var minutes = date.getMinutes() ;
        var formattedTime = years + '.' + month + '.' + day + '-' + hours + ':' + minutes
        return (formattedTime)
    }
    
    //function lvstraffic(obj,time_type) {
    //    if ( time_type == "hours" ) {
    //        end = Math.round(+new Date()/1000);
    //        start = end - 3600 ;
    //    } ;
    //
    //    $.each(obj,function(id,id_dict) {
    //        var renderTo = id_dict.id ;
    //        var title = id_dict.id + '  LVS流量'
    //        var arg = {"renderTo": renderTo ,"title": title, "time_type": time_type, "series":["inbytes","outbytes"] }
    //        console.log(arg) ;
    //        var traffic_charts = highchartsformat(arg) ;
    //
    //        traffic_charts.series[0].data = id_dict.inbytes_sum ;
    //        traffic_charts.series[1].data = id_dict.outbytes_sum ;
    //        var chart = new Highcharts.Chart(traffic_charts) ;
    //    });
    //
    //}

// {"renderTo":"highcharts1" ,title": "LvsTriffic", "time_type": "hours", "series":["iowait","sys"] }
function highchartsformat(arg) {
    //_series = [] ;
    title = arg.title ;
    renderTo = arg.renderTo ;
    time_type = arg.time_type ;
    series = arg.series ;
    if (time_type == "hours") {
        ytitle = "per minute"
    } ;

    //for (i in series) {
    //    _series.push({name:series[i]}) ;
    //} ;

    var charts = {
        chart: {
            renderTo: renderTo,
            zoomType: 'x' ,
            type: 'area'
        },
        title: {
            text: title,
            x: -20 //center
        },
        plotOptions: {
            area: {
                marker: {
                    enabled: false,
                    symbol: 'circle',
                    radius: 2,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                }
            }
        },
        tooltip: {
            formatter: function() {
                return '<b>' + 'Time:' + format_date_full(this.x) + '</b><br/>' + this.series.name + ':' + this.y ;
            },
            crosshairs: {
                width: 2
            },
            style: {
                padding: '10px',
            }
        },
        xAxis: {
            type: 'datetime',
            labels: {
                formatter: function() {
                    return format_date_sample(this.value)
                }
            }
        },
        yAxis: {
            title: {
                text: ytitle
            },min: 0
        },
        series: series
    };

    return charts
}