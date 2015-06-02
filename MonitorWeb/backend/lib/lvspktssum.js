$(document).ready(function(){

    $('#nav_lvspkts_sum').click(function (e) {
      e.preventDefault();
      $(this).tab('show');

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
      console.log()
      create_tpl(tpl) ;
      init_lb_filter() ;

      $.ajax({
          url: '/api/agentinfo/' ,
          dataType: "json",
          cache: false ,
          success: function(data) {
               lvspkts_sum(data[0].id) ;
          },
      });
      

      $("#lb_filter_tpl").change(function() {
          var id = $(this).val() ;
          lvspkts_sum(id) ;
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

    });


    $('#nav_lvspkts_vip').click(function (e) {
      e.preventDefault();
      $(this).tab('show');

      var tpl =  '<div class="row">' +
        '<select id="lb_filter_tpl"  class="inline" ></select>' +
        '<select id="vip_filter_tpl"  class="inline"></select>' +
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
      init_lb_filter() ;

      $.ajax({
          url: '/api/agentinfo/' ,
          dataType: "json",
          cache: false ,
          success: function(data) {
               lvspkts_sum(data[0].id) ;
          },
      });
      

      $("#lb_filter_tpl").change(function() {
          var id = $(this).val() ;
          lvspkts_sum(id) ;
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
          url = '/api/getlvstrafficvip/?agent=' + id  + '&start=' + start + '&end=' + end
          series = {"inpkts": "进包数/每秒" , "outpkts": "出包数/每秒"}
          init_charts_lvs_traffic(url,'hours',series) ;
      };

    });
});