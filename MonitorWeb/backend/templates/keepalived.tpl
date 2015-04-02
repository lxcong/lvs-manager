global_defs {  
   router_id {{ cluster_id }}
}

include ./local_address.conf

{% for vipinstance in vip_instance_list %}
{% if vipinstance.status != 'offline' %}
virtual_server_group {{ vipinstance.vip_instance }} {
    {% for vip in vipinstance.vip_group %}
    {{ vip.vip }} {{ vip.port }} #{{ vipinstance.descript }}
    {% endfor %}
}

virtual_server group  {{ vipinstance.vip_instance }} {
  delay_loop {{ vipinstance.delay_loop }}
  lb_algo {{ vipinstance.lb_algo }} 
  lb_kind {{ vipinstance.lb_kind }}
  protocol {{ vipinstance.protocol }}
  persistence_timeout {{ vipinstance.persistence_timeout }}
  {% if vipinstance.sync_proxy %}syn_proxy{% endif %}
  laddr_group_name laddr_g1
  {% if vipinstance.alpha %}alpha{% endif %}
  {% if vipinstance.omega %}omega{% endif %}
  quorum {{ vipinstance.quorum }}
  hysteresis {{ vipinstance.hysteresis }}
  quorum_up "{% for vip in vipinstance.vip_group %}ip addr add {{ vip.vip }}/32 dev lo ;{% endfor %}"
  {% if vipinstance.omega %}
  quorum_down "{% for vip in vipinstance.vip_group %}ip addr del {{ vip.vip }}/32 dev lo ;{% endfor %}"
  {% endif %}
 
  {% for rs in vipinstance.rs %}
	  {% for rs_port in rs.port %}
	  real_server {{ rs.server_ip }} {{ rs_port }} {
	    weight {{ rs.weight }}                                         
	    inhibit_on_failure
	    {% if rs.monitor.type == 'HTTP_GET' %}
	    HTTP_GET {
	    url {
	        path {{ rs.monitor.path }}
	        digest {{ rs.monitor.digest }}
	      }
	        connect_timeout {{ rs.monitor.connect_timeout }}
	        nb_get_retry {{ rs.monitor.nb_get_retry }}
	        delay_before_retry {{ rs.monitor.delay_before_retry }}
	        connect_port {{ rs_port }}
	    }
	    {% elif rs.monitor.type == 'TCP_CHECK' %}
	    TCP_CHECK {
        	connect_timeout {{ rs.monitor.connect_timeout }}
        	connect_port {{ rs_port }}
    	}
    	{% elif rs.monitor.type == 'MISC_CHECK' %}
    	MISC_CHECK {
           misc_path "{{ rs.monitor.misc_path }}"
           misc_timeout {{ rs.monitor.misc_timeout }}
       	}
	    {% endif %}  
    }                       
	  {% endfor %}
  {% endfor %}
}
{% endif %}

{% endfor %}
