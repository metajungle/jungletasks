from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.http import HttpResponseRedirect

def dev_login(request):
  """
  Displays a form for a user to login 
  """
  error = False
  if request.method == 'POST': 
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
      # only staff can login using this method 
      if user.is_staff:
        login(request, user)
        return HttpResponseRedirect(reverse('url_index')) 
    error = True
  return render_to_response("dev/login.html", 
                            { 'error' : error }, 
                            context_instance=RequestContext(request)) 
  
