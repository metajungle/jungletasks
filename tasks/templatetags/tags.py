from django import template
from datetime import datetime 

register = template.Library()

@register.simple_tag 
def current(active, name):
  if active.lower() == name.lower():
    return 'active-label'
  return ''


@register.simple_tag
def today(date_dt):
  if date_dt.date() == datetime.now().date():
    return 'today'
  return ''
