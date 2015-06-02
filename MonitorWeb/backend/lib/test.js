
    function init_lb_filter() {
        $.ajax({
            url: '/api/agentinfo/' ,
            dataType: "json",
            cache: false ,
            success: function(data) {
                 
                var tpl =   '{#foreach $T as agent}' +
                            '<option value="{$T.agent.id}">{$T.agent.id}</option>' +
                            '{#/for}' ;
                var tpl_c = $('#lb_filter_tpl').setTemplate(tpl) ;
                $('#lb_filter_tpl').processTemplate(data) ;
            },
        });
    } ;

    function create_tpl() {
       var tpl =  '<div class="row">' +
        '<select id="lb_filter_tpl"  class="inline" ></select>' +
      '</div>' +
      '<ul class="nav nav-tabs" id="TimeTab">' +
        '<li class="active" ><a href="#1A" data-toggle="tab">近一小时</a></li>' +
        '<li><a href="#2A" data-toggle="tab">近一天</a></li>' +
        '<li><a href="#3A" data-toggle="tab">近一个月</a></li>' +
      '</ul>' +
      '<div id="body_tpl">' +
      '</div>' ;
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
    
    function init_charts_lvs_traffic(id) {
        var loading=new ol.loading({id:"charts_body"}) ;
        end = Math.round(+new Date()/1000);
        start = end - 3600 ;
        $.ajax({
            url: '/api/getlvstraffic/?agent=' + id  + '&start=' + start + '&end=' + end,
            beforeSend: function() { loading.show() ;} ,
            dataType: "json",
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert(errorThrown) ;
            },
            success: function (obj) {
                loading.hide() ;
                create_charts_tpl(obj);
                init_fliter_vip_select(obj) ;
                lvstraffic(obj,'hours');
            },
            cache: false
        });
    
    };
    function create_agent_tpl(id) {
        
        var tpl =  '<dl class="palette palette-green-sea">' +
                    '<p class="text-center">{{$T}}</p>' +
                  '</dl>' +
                  '<dl class="palette palette-turquoise">' +
                    '<div id="charts_body" ></div>' +
                  '</dl>'  ;
    
        var tpl_c = $('#body_tpl').setTemplate(tpl) ;
        $('#body_tpl').processTemplate(id) ;
    
    };
    
    function create_charts_tpl(obj) {
        var tpl = '{#foreach $T as vip_dict}' +
                   '<div id="{{$T.vip_dict.id}}" style="min-width:400px;height:400px;margin:0 auto;"></div>' +
                   '</br>' +
                   '{#/for}'
        var tpl_c = $("#charts_body").setTemplate(tpl)
        console.log(tpl_c) ;
        $("#charts_body").processTemplate(obj) ;
    };
    
    function format_date_sample(timestamp) {
        var date = new Date(timestamp * 1000) ;
        var hours = date.getHours() ;
        var minutes = date.getMinutes() ;
        return (hours + ':' + minutes) ;
    }
    
    function format_date_full(timestamp) {
        var date = new Date(timestamp * 1000) ;
        var years = date.getFullYear() ;
        var month = date.getMonth() ;
        var day = date.getDate() ;
        var hours = date.getHours() ;
        var minutes = date.getMinutes() ;
        var formattedTime = years + '.' + month + '.' + day + '-' + hours + ':' + minutes
        return (formattedTime)
    }
    
    function lvstraffic(obj,time_type) {
        if ( time_type == "hours" ) {
            end = Math.round(+new Date()/1000);
            start = end - 3600 ;
        } ;
    
        $.each(obj,function(id,id_dict) {
            var renderTo = id_dict.id ;
            var title = id_dict.id + '  LVS流量'
            var arg = {"renderTo": renderTo ,"title": title, "time_type": time_type, "series":["inbytes","outbytes"] }
            console.log(arg) ;
            var traffic_charts = highchartsformat(arg) ;
    
            traffic_charts.series[0].data = id_dict.inbytes_sum ;
            traffic_charts.series[1].data = id_dict.outbytes_sum ;
            var chart = new Highcharts.Chart(traffic_charts) ;
        });
    
    }

// {"renderTo":"highcharts1" ,title": "LvsTriffic", "time_type": "hours", "series":["iowait","sys"] }
function highchartsformat(arg) {
    _series = [] ;
    title = arg.title ;
    renderTo = arg.renderTo ;
    time_type = arg.time_type ;
    series = arg.series ;
    if (time_type == "hours") {
        ytitle = "per minute"
    } ;

    for (i in series) {
        _series.push({name:series[i]}) ;
    } ;

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
        series: _series
    };

    return charts
}