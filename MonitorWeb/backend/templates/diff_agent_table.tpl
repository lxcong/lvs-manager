<table class="table table-bordered table-hover">
  <thead>
    <tr>
      <th>LB</th>
      <th>触发时间</th>
      <th>diff</th>
    </tr>
  </thead>
  <tbody>
  {% for diff in diff_dict %}
    <tr>
      <td>{{ diff.id }}</td>
      <td>{{ diff._time }}</td>
      <td><pre>{{ diff.diff }}</pre></td>
    </tr>
  {% endfor %}
  </tbody>
</table>