<table class="table table-bordered table-hover">
  <thead>
    <tr>
      <th>VIP_GROUP</th>
      <th>业务</th>
      <th>负责人</th>
      <th>RS列表</th>
    </tr>
  </thead>
  <tbody>
  {% for i in info.server %}
    <tr>
      <td><p>{% for vip_group in i['vip_group'] %}
      {{ vip_group.vip }}:{{ vip_group.port }}{% endfor %}</p></td>
      <td>{{ i.descript }}</td>
      <td>{{ i.owners }}</td>
      <td ><pre>{% for rs in i.rs %}
      管理IP:{{ rs.manager_ip }} 服务IP:{{ rs.server_ip }} 端口:{{ rs.port }}{% endfor %}</pre></td>
    </tr>
  {% endfor %}
  </tbody>
</table>