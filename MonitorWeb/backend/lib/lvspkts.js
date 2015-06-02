$(document).ready(function(){

  // LVS总数据包
    $('#nav_lvspkts_sum').click(function (e) {
      e.preventDefault();
      $(this).tab('show');

      var tpl =  '<div class="row">' +
      '<select id="cluster_filter_tpl"  class="inline" ></select>' +
        '<select id="lb_filter_tpl"  class="inline" ></select>' +
      '</div>' +
      '<ul class="nav nav-tabs" id="TimeTab">' +
        '<li class="active" ><a href="#1A" data-toggle="tab">近一小时</a></li>' +
        '<li><a href="#2A" data-toggle="tab">近一天</a></li>' +
        '<li><a href="#3A" data-toggle="tab">近一个月</a></li>' +
      '</ul>' +
      '<div id="body_tpl">' +
      '</div>' ;
      console.log()
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
       lvspkts_cluster_sum(id,time_type) ;

     })

      $.ajax({
          url: '/api/clusterinfo/' ,
          dataType: "json",
          cache: false ,
          success: function(data) {
               lvspkts_cluster_sum(data[0].id) ;
          },
      });
      

      $("#lb_filter_tpl").change(function() {
          var id = $(this).val() ;
          lvspkts_sum(id,time_type) ;
      });

      $("#cluster_filter_tpl").change(function() {
          var id = $(this).val() ;
          init_lb_filter(id) ;
          lvspkts_cluster_sum(id,time_type) ;
      });

      function lvspkts_sum(id) {
          var tpl =  '<dl class="palette palette-green-sea">' +
                    '<p class="text-center">{{$T}}</p>' +
                  '</dl>' +
                  '<dl class="palette palette-turquoise">' +
                    '<div id="charts_body" ></div>' +
                  '</dl>'  ;
          create_agent_tpl(id,tpl) ;

          end = Math.round(+new Date()/1000);
          start = end - 3600 ;
          url = '/api/getlvstraffic/?agent=' + id  + '&start=' + start + '&end=' + end
          series = {"inpkts_sum": "总进包数/每秒" , "outpkts_sum": "总出包数/每秒"}
          init_charts_lvs_traffic(url,'hours',series) ;
      };

      function lvspkts_cluster_sum(id,time_type) {
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

          url = '/api/getlvstrafficcluster/?agent=' + id  + '&start=' + start + '&end=' + end
          series = {"inpkts_sum": "总进包数/每秒" , "outpkts_sum": "总出包数/每秒"}
          init_charts_lvs_traffic(url,'hours',series) ;
      }

    });

    // LVS各业务数据包



    $('#nav_lvspkts_vip').click(function (e) {
      e.preventDefault();
      $(this).tab('show');

      var tpl =  '<div class="row">' +
        '<select id="cluster_filter_tpl"  class="inline" ></select>' +
      '</div>' +
      '<ul class="nav nav-tabs" id="TimeTab">' +
        '<li class="active" ><a href="#1A" data-toggle="tab">近一小时数据</a></li>' +
        '<li><a href="#2A" data-toggle="tab">每日数据</a></li>' +
      '</ul>' +
      '<div id="body_tpl">' +
      '</div>' ;

      create_tpl(tpl) ;
      init_cluster_filter() ;

      time_type = 'hours'
      end = Math.round(+new Date()/1000);
      start = end - 3600 ;

     $('#TimeTab a').click(function (e) {
       e.preventDefault();
       $(this).tab('show');
       console.log(this) ;
       var id = $("#cluster_filter_tpl").val() ;
       var _time_type = $(this).attr("href")
       switch (_time_type) {
        case "#1A":
            time_type = 'hours' ;
            end = Math.round(+new Date()/1000);
            start = end - 3600 ;
            pkts_viptable_hours(id,start,end);
            break;
        case "#2A":
            time_type = 'days' ;
            tpl = '</br><p>选择日期: <input type="text" id="datepicker" /></p>'  +
                              '<div id="charts_table"></div>';
            $('#body_tpl').setTemplate(tpl).processTemplate() ;
            $( "#datepicker" ).datepicker({
              onSelect: function(selectedDate,inst) { 
                start = Date.parse(selectedDate + ' 00:00:00') / 1000
                end = Date.parse(selectedDate + ' 23:59:59') / 1000
                pkts_viptable_day(id,start,end)
              },
              minDate: -20, 
              maxDate: "+1M +10D",
              dateFormat: "yy/mm/dd"});
            break;
       }
       //lvstraffic_cluster_vip(id,time_type) ;

     })

      $.ajax({
          url: '/api/clusterinfo/' ,
          dataType: "json",
          cache: false ,
          success: function(data) {
               //lvstraffic_cluster_vip(data[0].id) ;
               pkts_viptable_hours(data[0].id,start,end) ;
          },
      });


      $("#cluster_filter_tpl").change(function() {
          var id = $(this).val() ;
          switch (time_type) {
            case "hours":
              end = Math.round(+new Date()/1000);
              start = end - 3600 ;
              pkts_viptable_hours(id,start,end);
              break;
            case "days":
              console.log(time_type) ;
              tpl = '</br><p>选择日期: <input type="text" id="datepicker" /></p>'  +
                                '<div id="charts_table"></div>';
              $('#body_tpl').setTemplate(tpl).processTemplate() ;
              $( "#datepicker" ).datepicker({
                onSelect: function(selectedDate,inst) { 
                  start = Date.parse(selectedDate + ' 00:00:00') / 1000
                  end = Date.parse(selectedDate + ' 23:59:59') / 1000
                  pkts_viptable_day(id,start,end)
                },
                minDate: -20, 
                maxDate: "+1M +10D",
                dateFormat: "yy/mm/dd"});
              break;
          }
          //lvstraffic_cluster_vip(id,time_type) ;
          //pkts_viptable_hours(id,start,end)
      });


      function pkts_viptable_hours(cluster,start,end) {
        var loading=new ol.loading({id:"body_tpl"}) ;
        $.ajax({
            url: '/api/getlvsclusterviplist/?agent=' + cluster + '&start=' + start + '&end=' + end, 
            beforeSend: function() { loading.show()} ,
            dataType: "json",
            cache: false ,
            success: function(data) {
              loading.hide() ;
              var tpl = '<div>' +
              '<table class="table table-bordered table-hover">' +
                '<thead>' +
                  '<tr>' +
                    '<th>VIP</th>' +
                    '<th>业务</th>' +
                    '<th>负责人</th>' +
                    '<th>图像</th>' +
                  '</tr>' +
                '</thead>' +
                '<tbody>' +
                '{#foreach $T as VIP}' +
                  '<tr>' +
                    '<td>{$T.VIP.vip}</td>' +
                    '<td>{$T.VIP.descript}</td>' +
                    '<td>{$T.VIP.owners}</td>' +
                    '<td><a id="{$T.VIP.cluster}-{$T.VIP.vip}" class="btn btn-block btn-warning vipcharts">近一小时数据</a></td>' +
                  '</tr>' +
                '{#/for}' +
                '</tbody>' +
              '</table> ' +
              '</div>' ;
              $('#body_tpl').setTemplate(tpl).processTemplate(data) ;
              $(".vipcharts").click(function() {
                var _id = $(this).attr("id") ;
                var arr = _id.split("-")
                var id = arr[0]
                var vip = arr[1]
                $("#messagemodal").modal();
                lvspkts_cluster_vip(id,vip,start,end); 
                
              });
            },
        });

      };

      function pkts_viptable_day(cluster,start,end) {
        var loading=new ol.loading({id:"body_tpl"}) ;
        $.ajax({
            url: '/api/getlvsclusterviplist/?agent=' + cluster ,
            beforeSend: function() { loading.show()} ,
            dataType: "json",
            cache: false ,
            success: function(data) {
              loading.hide() ;
              var tpl = '<div>' +
              '<table class="table table-bordered table-hover">' +
                '<thead>' +
                  '<tr>' +
                    '<th>VIP</th>' +
                    '<th>业务</th>' +
                    '<th>负责人</th>' +
                    '<th>图像</th>' +
                  '</tr>' +
                '</thead>' +
                '<tbody>' +
                '{#foreach $T as VIP}' +
                  '<tr>' +
                    '<td>{$T.VIP.vip}</td>' +
                    '<td>{$T.VIP.descript}</td>' +
                    '<td>{$T.VIP.owners}</td>' +
                    '<td><a id="{$T.VIP.cluster}-{$T.VIP.vip}" class="btn btn-block btn-warning vipcharts">每日数据</a></td>' +
                  '</tr>' +
                '{#/for}' +
                '</tbody>' +
              '</table> ' +
              '</div>' ;
              $('#charts_table').setTemplate(tpl).processTemplate(data) ;
              $(".vipcharts").click(function() {
                var _id = $(this).attr("id") ;
                var arr = _id.split("-")
                var id = arr[0]
                var vip = arr[1]
                console.log("ID: %s  VIP:%s",id,vip);
                $("#messagemodal").modal();
                lvspkts_cluster_vip(id,vip,start,end); 
                
              });
            },
        });

      };

      function lvspkts_cluster_vip(id,vip,start,end) {
          //var tpl =  '<dl class="palette palette-green-sea">' +
          //          '<p class="text-center">{{$T}}</p>' +
          //        '</dl>' +
          //        '<dl class="palette palette-turquoise">' +
          //          '<div id="charts_body" ></div>' +
          //        '</dl>'  ;
          //create_agent_tpl(id,tpl) ;

          url = '/api/getlvstrafficclustervip/?agent=' + id  +'&vip=' + vip + '&start=' + start + '&end=' + end
          series = {"inpkts": "进包数/每秒" , "outpkts": "出包数/每秒"}
          init_charts(url,'hours',series) ;
      }
    


    });


});