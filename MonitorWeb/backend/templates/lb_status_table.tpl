<table class="table table-bordered table-hover">
  <thead>
    <tr>
      <th>Loadblance</th>
      <th>agent状态</th>
      <th>ip</th>
      <th>vip</th>
      <th>更新时间</th>
    </tr>
  </thead>
  <tbody>
  {% for lb in lblist %}
    <tr>
      <td>{{ lb.id }}</td>
      <td><button class="btn btn-success">在线</button></td>
      <td>{{ lb.ipadd }}</td>
      <td><button id="{{ lb.id }}" class="btn btn-block btn-warning status_vip_click">VIP: {{ lb.vipcount }}</button></td>
      <td>{{ lb.time.strftime('%Y-%m-%d   %H:%M:%S') }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>