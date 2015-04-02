执行结果：
{% for result in cmd_result %}
{{ result.id }} : {% if result.result %}ok{% else %}failed{% endif %}
{% if result.result %}{{ result.ret }}{% endif %}
############################################################################
{% endfor %}