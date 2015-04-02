<table class="table table-bordered table-hover">
  <thead>
    <tr>
      <th>VIP</th>
      <th>业务</th>
      <th>负责人</th>
      <th>调度方法</th>
      <th>在线RS列表</th>
      <th>掉线RS列表</th>
    </tr>
  </thead>
  <tbody>
  {% for vip in vip_dict.node %}
    <tr>
      <td>{{ vip.vip }}</td>
      <td>{{ vip.descript }}</td>
      <td>{{ vip.owners }}</td>
      <td>{{ vip.lb_algo }}</td>
      <td ><div id='rs_alived_list_{{ vip.vip }}' class="rs_alived_list"><pre>{% for rs in vip.node if rs.weight is rs_is_lived %}
      RS:{{ rs.rs }} Weight:{{ rs.weight }}{% endfor %}</pre></div></td>
      <td ><div id='rs_alived_list_{{ vip.vip }}' class="rs_alived_list"><pre>{% for rs in vip.node if rs.weight is not rs_is_lived %}
      RS:{{ rs.rs }} Weight:{{ rs.weight }}{% endfor %}</pre></div></td>
    </tr>
  {% endfor %}
  </tbody>
</table>