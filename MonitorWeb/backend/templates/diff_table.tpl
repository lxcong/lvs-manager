<table class="table table-bordered table-hover">
  <thead>
    <tr>
      <th>Loadblance</th>
      <th>ip</th>
      <th>状态发生的变化</th>
    </tr>
  </thead>
  <tbody>
  {% for diff in difflist %}
    <tr id="{{ diff.id }}">
      <td>{{ diff.id }}</td>
      <td>{{ diff.ipadd }}</td>
      <td class="diff_click"><button class="btn btn-block btn-warning">Diff: {{ diff.diffcount }}</button></td>
    </tr>
  {% endfor %}
  </tbody>
</table>