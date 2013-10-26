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

@register.simple_tag 
def active(request, pattern):
  import re
  if re.search(pattern, request.path):
      return 'active'
  return ''
  
@register.simple_tag 
def active_exact(request, pattern):
  import re
  # require exact match 
  pattern = '^%s$' % pattern
  if re.search(pattern, request.path):
      return 'active'
  return ''  