from django import template
from datetime import datetime 

register = template.Library()

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
  
@register.simple_tag
def adjust_color(hex_color, offset=-30):
  if hex_color.startswith('#'):
    return color_variant(hex_color, offset)
  return color_variant(('#%s' % hex_color), offset)  
  
def color_variant(hex_color, brightness_offset=1):  
    """ 
    takes a color like #87c95f and produces a lighter or darker variant 
    
    from: http://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
    """  
    if len(hex_color) != 7:  
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)  
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]  
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]  
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255  
    # hex() produces "0x88", we want just "88"  
    return "#%02x%02x%02x" % tuple(new_rgb_int)
    # return "#" + "".join([hex(i)[2:] for i in new_rgb_int])  
  