from django.template import RequestContext 
from django.shortcuts import render_to_response, redirect 

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.views.decorators.http import require_http_methods, require_GET, require_POST

from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
from datetime import datetime

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from tasks.models import Task, Label, SystemLabel

from tasks.forms import TaskForm

import account.models as a_models

@require_GET
def index(request): 
  """
  Home page
  """
  if request.user.is_authenticated():
    if not 'hp' in request.GET:
      return redirect('url_tasks_inbox')
  
  return render_to_response('index.html', {}, 
                  context_instance=RequestContext(request)) 


@login_required
@require_GET
def tasks(request):
  """
  Re-directs to the tasks in the 'inbox'
  """
  return redirect('url_tasks_inbox')  


@login_required
@require_http_methods(['GET', 'POST'])
def tasks_inbox(request):
  """
  Display tasks in the 'inbox'
  """
  tasks = Task.objects.filter(user=request.user, completed=False)
  return tasks_display(request, tasks)


@login_required
@require_GET
def tasks_completed(request):
  """
  Display completed tasks 
  """
  tasks = Task.objects.filter(user=request.user, completed=True).order_by('-date_completed')
  return tasks_display(request, tasks)


@login_required
@require_GET
def tasks_by_label(request, id):
  """
  Display tasks by a label
  """
  try:
    label = Label.objects.get(id=id)
    tasks = Task.objects.filter(user=request.user, labels=label, completed=False)
    return tasks_display(request, tasks, label)
  except Label.DoesNotExist:
    raise Http404


def tasks_display(request, tasks, label=None):
  """
  Utility method for displaying the given tasks 
  """
  # all the users labels
  labels = Label.objects.filter(user=request.user, hidden=False, active=True)
  # the number of tasks not done (used to display 'inbox' count)
  num_tasks_not_done = Task.objects.filter(user=request.user, completed=False).count()
  # paginate the tasks 
  paginator = Paginator(tasks, 10) 
  # make sure page request is an int. If not, deliver first page.
  try:
    page = int(request.GET.get('page', '1'))
  except ValueError:
    page = 1
  # if page request (9999) is out of range, deliver last page of results.
  try:
    paged_items = paginator.page(page)
  except (EmptyPage, InvalidPage):
    paged_items = paginator.page(paginator.num_pages)
  
  return render_to_response('tasks/index.html', 
                            { 'tasks': paged_items, 
                              'active_label': label, 
                              'labels': labels, 
                              'num_tasks_not_done': num_tasks_not_done }, 
                  context_instance=RequestContext(request)) 


@login_required
@require_POST
def tasks_add_task(request):
  """ Adds a new task """
  if 'task' in request.POST:
    task = request.POST.get('task') or ''
    if task != '': 
      # create task
      task = Task(user=request.user, task=task)
      task.save()
      # add label
      if 'active_label' in request.POST:
        l_id = request.POST.get('active_label')
        try:
          label = Label.objects.get(id=l_id)
          task.labels.add(label)
          return redirect('url_tasks_label', id=l_id)
        except Label.DoesNotExist:
          pass
    else:
      messages.error(request, 'A task cannot be empty')

  return redirect('url_tasks_inbox')


@login_required
@require_http_methods(['GET', 'POST'])
def tasks_edit(request, id):
  """
  Edit a task 
  """
  try:
    
    task = Task.objects.get(user=request.user, id=id)
    
    if request.method == 'POST':
      form = TaskForm(request.POST) 
      if form.is_valid(): 
        # update task 
        data = form.cleaned_data
        task.task = data.get('task')
        task.notes = data.get('notes')
        task.priority = data.get('priority')
        task.save()
        # set message 
        messages.add_message(request, messages.SUCCESS, 'Task updated')
        return redirect('url_tasks')
    else:
      form = TaskForm(instance=task)

    return render_to_response('tasks/edit.html', 
                              { 'task': task, 
                                'form' : form }, 
                    context_instance=RequestContext(request)) 
    
  except Task.DoesNotExist:
    pass
    
  raise Http404


@login_required
@require_POST
def tasks_delete(request, id):
  """
  Delete a task 
  """
  try:
    task = Task.objects.get(user=request.user, id=id)
    task.delete()
    messages.add_message(request, messages.SUCCESS, 'The task was deleted')
  except Label.DoesNotExist:
    messages.add_message(request, messages.ERROR, 'An error occurred, the task could not be deleted')
      
  return redirect('url_tasks')


@login_required
@require_POST
def tasks_mark_done(request):
  """
  Marks a task done (or not done)
  """
  t_id = request.POST['task']
  action = request.POST['action']
  
  # default 
  json = simplejson.dumps({ 'status': 'KO' })
  
  if t_id != None and action != None:
    try: 
      task = Task.objects.get(user=request.user, id=t_id)
      if action == 'done':
        task.completed = True
        task.date_completed = datetime.now()
      elif action == 'undone':
        task.completed = False
        task.date_completed = None
      task.save()
      json = simplejson.dumps({ 'status': 'OK' })
    except Task.DoesNotExist, Label.DoesNotExist: 
      json = simplejson.dumps({ 
        'status': 'KO', 
        'message': 'An error occurred, the task could not be updated' 
      })
      
  return HttpResponse(json, mimetype = 'application/json', 
                      content_type = 'application/json; charset=utf8')


@login_required
@require_GET
def label(request):
  """
  A view to create, delete and modify labels (categories)
  """
  
  labels = Label.objects.filter(user=request.user)

  try:
    profile = request.user.get_profile()
    system_labels = profile.system_labels.all()
  except a_models.UserProfile.DoesNotExist:
    system_labels = None

  return render_to_response('label/index.html', 
                            { 'labels' : labels,
                              'system_labels' : system_labels }, 
                  context_instance=RequestContext(request)) 


@login_required
@require_POST
def label_add(request):
  """
  Add a label
  """
  if 'label' in request.POST:
    label = request.POST['label'].strip()
    
    if label == '':
      messages.add_message(request, messages.ERROR, 'The label cannot be empty')
    else:
      # check that the label name does not already exist
      try:
        Label.objects.get(user=request.user, name__iexact=label)
        messages.add_message(request, messages.ERROR, 'The label already exists (labels are case-insensitive)')
      except Label.DoesNotExist:
        label = Label(user=request.user, name=label)
        label.save()
        messages.add_message(request, messages.SUCCESS, 'The label was created')
      
  return HttpResponseRedirect(reverse('url_label'))
  
  
@login_required
@require_http_methods(['GET', 'POST'])
def label_edit(request, id):
  """
  Edit a label
  """
  try: 
    label = Label.objects.get(user=request.user, id=id)
    
    if request.method == 'POST':
      l = request.POST.get('label') or ''
      l = l.strip()
      # check for empty labels 
      if l == '':
          messages.add_message(request, messages.ERROR, 'The label cannot be empty')
      else:
        # check for existing labels
        ls = Label.objects.filter(user=request.user, name__iexact=l).exclude(id=id)
        if len(ls) > 0:
          messages.add_message(request, messages.ERROR, 'That label already exists (labels are case-insensitive)')
        else:
          # TODO: should catch error if the label is too long, for example. 
          label.name = l
          # color
          label.color = request.POST.get('color') or '#ffff99'
          label.save()
          messages.add_message(request, messages.SUCCESS, 'The label was updated')
          return redirect('url_label')
          
    return render_to_response('label/edit.html', 
                              { 'label' : label }, 
                    context_instance=RequestContext(request)) 
  except:
    raise Http404


@login_required
@require_POST
def label_delete(request, id):
  """
  Delete a label (actually, just marks it as inactive)
  """
  try:
    label = Label.objects.get(user=request.user, id=id)
    label.active = False
    label.save()
    messages.add_message(request, messages.SUCCESS, 'The label was deleted')
  except Label.DoesNotExist:
    messages.add_message(request, messages.ERROR, 'An error occurred, the label could not be deleted')
      
  return redirect('url_label')


@login_required
@require_POST
def label_task_assign_json(request):
  """
  Assigns a label to a task
  """
  t_id = request.POST['task']
  l_id = request.POST['label']
  action = request.POST['action']
  
  # default 
  json = simplejson.dumps({ 'status': 'KO' })
  
  if t_id != None and l_id != None and action != None:
    try: 
      # assign label to task 
      task = Task.objects.get(user=request.user, id=t_id)
      label = Label.objects.get(user=request.user, id=l_id)
      if action == 'add':
        task.labels.add(label)
      elif action == 'remove':
        label.task_set.remove(task)
      json = simplejson.dumps({ 'status': 'OK' })
    except Task.DoesNotExist, Label.DoesNotExist: 
      json = simplejson.dumps({ 
        'status': 'KO', 
        'message': 'An error occurred, the task could not be updated' 
      })
      
  return HttpResponse(json, mimetype = 'application/json', 
                      content_type = 'application/json; charset=utf8')


@login_required
@require_POST
def label_set_hidden_json(request):
  """
  Sets the hidden flag of a label
  """
  l_id = request.POST['id']
  l_hidden = request.POST['hidden']

  # default 
  json = simplejson.dumps({ 'status': 'KO' })
  
  if l_id != None and l_hidden != None:
    try:
      label = Label.objects.get(user=request.user, id=l_id)
      status = True if l_hidden == 'true' else False
      label.hidden = status
      print "Status: %s" % label.hidden
      label.save()
      json = simplejson.dumps({ 'status': 'OK' })
    except Label.DoesNotExists:
      json = simplejson.dumps({ 
        'status': 'KO', 
        'message': 'An error occurred, the label could not be found' 
      })

  return HttpResponse(json, mimetype = 'application/json', 
                      content_type = 'application/json; charset=utf8')


def about(request):
  """
  Displays the 'About' page
  """
  return render_to_response('tasks/about.html', 
                            { }, 
                  context_instance=RequestContext(request)) 



