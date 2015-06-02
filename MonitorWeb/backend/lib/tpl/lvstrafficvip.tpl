<div class='col-md-9' id="tpl">
  <div class='row'>
    <select id="lb_filter_tpl"  class='inline' >
    </select>
    <select id="vip_filter_tpl"  class='inline'>
    </select>
  </div>
  <ul class="nav nav-tabs" id="TimeTab">
    <li class="active" ><a href="#1A" data-toggle="tab">近一小时</a></li>
    <li><a href="#2A" data-toggle="tab">近一天</a></li>
    <li><a href="#3A" data-toggle="tab">近一个月</a></li>
  </ul>
  <dl class="palette palette-green-sea">
    <p class="text-center">{{$T}}</p>
  </dl>
  <dl class="palette palette-turquoise">
    {#foreach $T as vip_dict}
    <div id="{{$T.vip_dict.id}}{{$T.vip_dict.vip}}" style="min-width:400px;height:400px;margin:0 auto;"></div>
    </br>
    {#/for}
  </dl>
</div>