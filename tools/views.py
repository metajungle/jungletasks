from django.template import RequestContext 
from django.shortcuts import render_to_response

from django.http import HttpResponse, Http404

from django.contrib.auth.decorators import login_required

from tasks.models import Task, Label

from utils import orgmode_write

@login_required
def tasks_export(request):
  """
  View for exporting tasks (into a file that can be downloaded)
  """

  label = None
  error_no_such_label = False
  tasks = None
  
  # limit of number of tasks to fetch for preview
  no = 10
  count = 0

  #
  # PREVIEW tasks
  #
  if request.method == 'GET' and 'label' in request.GET:
    label = request.GET['label']
    try:
      l = Label.objects.get(user=request.user, name__iexact=label)
      # limit number of tasks for the preview 
      count = Task.objects.filter(user=request.user, labels=l).count()
      tasks = Task.objects.filter(user=request.user, labels=l)[:no]
    except Label.DoesNotExist:
      if label.lower() == "inbox":
        # limit number of tasks for the preview 
        count = Task.objects.filter(user=request.user, done=False).count()
        tasks = Task.objects.filter(user=request.user, done=False)[:no]
      elif label.lower() == "all":
        # limit number of tasks for the preview 
        count = Task.objects.filter(user=request.user).count()
        tasks = Task.objects.filter(user=request.user)[:no]
      else:
        error_no_such_label = True
    
    if not tasks:
      msg = """
            <p>There are no tasks to export.</p>
            """
      return render_to_response('message.html', 
                                { 'msg' : msg, 'success' : False }, 
                                context_instance=RequestContext(request)) 

  #
  # EXPORT tasks
  #
  elif request.method == 'POST' and 'label' in request.POST:
    label = request.POST['label']
    # get tasks 
    try:
      l = Label.objects.get(user=request.user, name__iexact=label)
      tasks = Task.objects.filter(user=request.user, labels=l)
    except Label.DoesNotExist:
      if label.lower() == "inbox":
        tasks = Task.objects.filter(user=request.user, done=False)
      elif label.lower() == "all":
        tasks = Task.objects.filter(user=request.user)
    # export tasks 
    if tasks:
      # create the HttpResponse object with the appropriate header
      response = HttpResponse(mimetype='text/plain')
      response['Content-Disposition'] = 'attachment; filename=tasks.org'
      # write tasks 
      contents = orgmode_write(tasks)
      response.write(contents)
      # return attachment
      return response
    else:
      raise Http404

  # True if all tasks that will be exported are shown in the preview, 
  # False otherwise 
  if count > no:
    all_shown = False
  else:
    all_shown = True

  return render_to_response('export.html', 
                            { 'tasks' : tasks[:no], 
                              'all_shown' : all_shown, 
                              'label' : label, 
                              'error_no_such_label' : error_no_such_label }, 
                  context_instance=RequestContext(request)) 


@login_required
def tasks_import(request):

  return render_to_response('import.html', 
                            { }, 
                  context_instance=RequestContext(request)) 
