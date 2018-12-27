#!/usr/bin/python

from jinja2 import Template
from jinja2 import Environment, BaseLoader
jinja_env = Environment(loader=BaseLoader,extensions=['jinja2.ext.do'])

txt ="""
{%- set stick_table_found = { 'val': false } %}
{%- for item in listen.get('sticks', []) if item.startswith('stick-table ') %}
{%- do stick_table_found.update({'val': true}) %}
{%- endfor %}
{%- if not stick_table_found.val %}
  stick-table type string size 100k store gpc0_rate(60)
{%- endif %}

"""



tmpl = jinja_env.from_string(txt)
print tmpl.render({"listen":{'xxx':'ccc'}})
#print tmpl.render()

