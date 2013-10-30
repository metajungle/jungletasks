from django.template import RequestContext 
from django.shortcuts import render_to_response, redirect 

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.views.decorators.http import require_http_methods

from django.core.urlresolvers import reverse
from django.core import serializers
from django.utils import simplejson
from datetime import datetime, timedelta
import time 

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from tasks.models import Task, Label, SystemLabel

from tasks.forms import AddTaskForm

import account.models as a_models

@require_http_methods(['GET'])
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
def home(request, label=None): 
  """
  A users home view
  """

  # Label
  user_label = None

  if request.method == 'GET':
    if 'l' in request.GET:
      label = request.GET['l']

  #
  # TASKS
  #
    
  if label == None:
    label = "inbox"

  # 'standard' labels
  if label.lower() == "inbox" or label.lower() == "all":
    if label.lower() == "inbox":
      tasks = Task.objects.filter(user=request.user, done=False)
    else:
      tasks = Task.objects.filter(user=request.user)      
    pass
  # 'system' labels 
  elif label.lower().startswith('s:'):
    system = label.upper()[2:]
    if system == 'UNLABELED':
      tasks = Task.objects.filter(user=request.user, labels=None, done=False)
    elif system == 'PRIORITY':
      tasks = Task.objects.filter(user=request.user, priority='HIG', done=False)
    else:
      # fall back to 'inbox'
      tasks = Task.objects.filter(user=request.user, done=False)
      # ... but leave a message 
      msg = """
            Did not understand the given system label "%s", showing
            <b>Inbox</b> instead
            """ % system 
      messages.error(request, msg)
  else:
    # user-defined labels 
    try:
      l = Label.objects.get(user=request.user, name=label)
      user_label = l 
      tasks = Task.objects.filter(user=request.user, labels=l, done=False) 
    except Label.DoesNotExist:
      # use 'inbox' tasks, but give an error 
      tasks = Task.objects.filter(user=request.user, done=False)
      # write message 
      msg = 'The label "%s" is not recognized, showing the Inbox instead.' % label
      messages.error(request, msg)

  # sort 
  if label and label.lower() != "all":
    pass
    #tasks = sorted(tasks, key=lambda task: task.priority)


  num_not_done = Task.objects.filter(user=request.user, done=False).count()
    
  #
  # LABELS
  #
  labels = Label.objects.filter(user=request.user, hidden=False)

  paginator = Paginator(tasks, 10) 

  # make sure page request is an int. If not, deliver first page.
  try:
    page = int(request.GET.get('page', '1'))
  except ValueError:
    page = 1

  # If page request (9999) is out of range, deliver last page of results.
  try:
    paged_items = paginator.page(page)
  except (EmptyPage, InvalidPage):
    paged_items = paginator.page(paginator.num_pages)
  
  # pass on GET values
  get_values = ""
  for key in request.GET:
    get_values += "%s=%s&" % (key, request.GET[key])

  return render_to_response('home.html', 
                            { 'paged_items' : paged_items, 
                              'num_not_done' : num_not_done, 
                              'user_label' : user_label, 
                              'labels' : labels, 
                              'active_label' : label, 
                              'get_values' : get_values, 
                              'get' : request.GET },
                  context_instance=RequestContext(request)) 


@login_required
@require_http_methods(['GET'])
def tasks(request):
  """
  Re-directs to the tasks in the 'inbox'
  """
  return HttpResponseRedirect(reverse('url_tasks_inbox'))

@login_required
@require_http_methods(['GET', 'POST'])
def tasks_inbox(request):
  """
  Display tasks in the 'inbox'
  """
  
  # if request.method == 'POST':
  #   add_task(request)
  
  labels = Label.objects.filter(user=request.user, hidden=False, active=True)

  num_tasks_not_done = Task.objects.filter(user=request.user, done=False).count()
  
  tasks = Task.objects.filter(user=request.user, done=False)
  paginator = Paginator(tasks, 10) 

  # make sure page request is an int. If not, deliver first page.
  try:
    page = int(request.GET.get('page', '1'))
  except ValueError:
    page = 1

  # If page request (9999) is out of range, deliver last page of results.
  try:
    paged_items = paginator.page(page)
  except (EmptyPage, InvalidPage):
    paged_items = paginator.page(paginator.num_pages)
      
  return render_to_response('tasks/index.html', 
                            { 'tasks': paged_items, 
                              'labels': labels, 
                              'num_tasks_not_done': num_tasks_not_done }, 
                  context_instance=RequestContext(request)) 
  
@login_required
@require_http_methods(['GET'])
def tasks_all(request):
  """
  Display all tasks 
  """
  return render_to_response('tasks/index.html', 
                            { }, 
                  context_instance=RequestContext(request)) 

@login_required
@require_http_methods(['GET'])
def tasks_label(request, id):
  """
  Display tasks by a label
  """
  return render_to_response('tasks/index.html', 
                            { }, 
                  context_instance=RequestContext(request)) 

@login_required
@require_http_methods(['POST'])
def tasks_add(request):
  
  if 'task' in request.POST:
    task = request.POST['task']
    # create task
    task = Task(user=request.user, task=task)
    task.save()

  # return tasks_inbox(request)
  return redirect('url_tasks_inbox')
  

def add_task(request):
  # create task
  if request.method == 'POST':
    task = request.POST['task']
    if task != None:
      task = Task(user=request.user, task=task)
      task.save()
      # TODO: add label


@login_required
@require_http_methods(['GET', 'POST'])
def tasks_edit(request, id):
  """
  Edit a task 
  """
  return render_to_response('tasks/index.html', 
                            { }, 
                  context_instance=RequestContext(request)) 


@login_required
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
@require_http_methods(['POST'])
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
      l = request.POST['label'].strip()
      # check for empty labels 
      if l == '':
        messages.add_message(request, messages.ERROR, 'The label cannot be empty')
      else:
        # check for existing labels
        try:
          Label.objects.get(user=request.user, name__iexact=l)
          messages.add_message(request, messages.ERROR, 'That label already exists (labels are case-insensitive)')
        except Label.DoesNotExist:
          # TODO: should catch error if the label is too long, for example. 
          label.name = l
          label.save()
          messages.add_message(request, messages.SUCCESS, 'The label was updated')
    
    return render_to_response('label/edit.html', 
                              { 'label' : label }, 
                    context_instance=RequestContext(request)) 
  except:
    raise Http404
    
  
@login_required
@require_http_methods(['POST'])
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
      
  return HttpResponseRedirect(reverse('url_label'))

@login_required
@require_http_methods(['POST'])
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
        task.save()
      elif action == 'remove':
        label.task_set.remove(task)
        label.save()
      json = simplejson.dumps({ 'status': 'OK' })
    except Task.DoesNotExist, Label.DoesNotExist: 
      json = simplejson.dumps({ 
        'status': 'KO', 
        'message': 'An error occurred, the task could not be updated' 
      })
      
  return HttpResponse(json, mimetype = 'application/json', 
                      content_type = 'application/json; charset=utf8')


@login_required
@require_http_methods(['POST'])
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
      label.save()
      json = simplejson.dumps({ 'status': 'OK' })
    except Label.DoesNotExists:
      json = simplejson.dumps({ 
        'status': 'KO', 
        'message': 'An error occurred, the label could not be found' 
      })

  return HttpResponse(json, mimetype = 'application/json', 
                      content_type = 'application/json; charset=utf8')
      


  
@login_required
def settings(request):
  return render_to_response('settings.html', 
                            { }, 
                  context_instance=RequestContext(request)) 

@login_required
def tools(request):

  return render_to_response('tools.html', 
                            { }, 
                  context_instance=RequestContext(request)) 


def faq(request):
  """
  Displays the FAQ
  """
  return render_to_response('faq.html', 
                            { }, 
                  context_instance=RequestContext(request)) 


@login_required
def log(request):
  """
  Displays a log of completed tasks
  """
  now = datetime.now()
  year,week,dow = now.isocalendar()

  today_week = week
  today_year = year
  
  if request.method == 'GET':
    if 'week' in request.GET:
      try:
        week = int(request.GET['week'])
      except ValueError:
        msg = 'Week value %s was not a number' % week
        messages.error(request, msg)
        week = today_week
    if 'year' in request.GET:
      try:
        year = int(request.GET['year'])
      except ValueError:
        msg = 'Year value %s was not a number' % year
        messages.error(request, msg)
        year = today_year

  try:
    monday_struct = time.strptime('%s %s 1' % (year, week), '%Y %W %w')
    monday = datetime.fromtimestamp(time.mktime(monday_struct))
  except ValueError:
    week = today_week
    year = today_year
    monday_struct = time.strptime('%s %s 1' % (year, week), '%Y %W %w')
    monday = datetime.fromtimestamp(time.mktime(monday_struct))
    msg = 'Did not understand the specified week and/or year, using <b>today</b>'
    messages.error(request, msg)


  total = Task.objects.filter(user=request.user, done=True).count()

  total_week = 0
  tasks = {}
  dates = []
  for i in range(7):
    day = monday + timedelta(days=i)
    # add to the list of dates
    dates.append(day)
    # create a map from dates to tasks 
    tasks_ = Task.objects.filter(user=request.user, done=True, finished__year=day.year, finished__month=day.month, finished__day=day.day)
    tasks[day] = tasks_
    # count
    total_week += len(tasks_)

  prev_year, prev_week, dow = (monday - timedelta(weeks=1)).isocalendar()
  next_year, next_week, dow = (monday + timedelta(weeks=1)).isocalendar()

  return render_to_response('log.html', 
                            { 'week' : week, 
                              'year' : year, 
                              'today_week' : today_week, 
                              'prev_week' : prev_week, 
                              'next_week' : next_week, 
                              'today_year' : today_year, 
                              'prev_year' : prev_year, 
                              'next_year' : next_year, 
                              'dates' : dates, 
                              'tasks' : tasks, 
                              'total' : total, 
                              'total_week' : total_week, },  
                  context_instance=RequestContext(request)) 

@login_required
def form_task_add(request, template='add.html'):

  if request.method == 'POST': 
    form = AddTaskForm(request.POST) 
    if form.is_valid(): 
      # save
      data = form.cleaned_data
      # create task
      task = Task(user=request.user, **data)
      task.save()
      # add labels, if there are any specified 
      label_ids = request.POST['labels']
      if label_ids != "":
        l_ids = label_ids.split(",")
        for l_id in l_ids:
          try:
            label = Label.objects.get(id=l_id)
            task.labels.add(label)
          except Label.DoesNotExist:
            pass
        # save again
        task.save()

      # provide a message to the user
      messages.success(request, 'Your task was added')

      # attempt to return to the label we were in before adding a task 
      return HttpResponseRedirect(util_return_url(request))
  else:
    form = AddTaskForm() 

  labels = Label.objects.filter(user=request.user)

  return render_to_response(template, 
                            { 'form' : form, 
                              'labels' : labels, 
                              'get' : request.GET }, 
                  context_instance=RequestContext(request)) 


@login_required
def form_task_edit(request, template='edit.html'):

  # list of Label IDs for task
  l_ids = None

  if request.method == 'POST' and 't_id' in request.POST: 
    t_id = request.POST['t_id']
    try:
      task = Task.objects.get(id=t_id)
      # update the task text
      text = request.POST['task']
      delete_task = False

      if text and text.strip() != "": 
        # save the new text
        task.task = text
      else:
        delete_task = True

      if 'delete' in request.POST:
        delete_task = True

      # should the task be deleted? two things can cause this:
      # 1) 'Delete' button is pressed; 
      # 2) Task is saved with empty text 
      if delete_task:
        # if there is no text, delete the task 
        task.delete()
        # write message 
        messages.info(request, 'The task was deleted!')
        # re-direct to the home page 
        return HttpResponseRedirect(util_return_url(request))

      # remove old labels (that are active) 
      util_clear_labels(task)
      # write new labels 
      label_ids = request.POST['labels']
      if label_ids != "":
        l_ids = label_ids.split(",")
        for l_id in l_ids:
          try:
            label = Label.objects.get(id=l_id)
            task.labels.add(label)
          except Label.DoesNotExist:
            pass
      # upate priority
      pri = request.POST['priority']
      task.priority = pri
      # save task object 
      task.save()
    except Task.DoesNotExist:
      pass

    return HttpResponseRedirect(util_return_url(request))

  else:
    # if request.method == 'GET', create the form that
    # the user will use to edit the task 
    # (the values will be loaded on the client side) 
    if 't_id' in request.GET:
      t_id = request.GET['t_id']
      try:
        task = Task.objects.get(id=t_id)
        form = AddTaskForm({'task':task.task, 'priority': task.priority})
        # provide the ids of the labels that the task is associated with 
        l_ids = task.labels.values_list('id', flat=True)
      except Task.DoesNotExist:
        return util_unknown_task(request)
    else:
      return util_unknown_task(request)

  # the var 'orig_l' contains the string name of the label 
  # we were 'in' when the user clicked to edit a task
  orig_l_id = None
  if request.method == 'GET' and 'orig_l' in request.GET:
    try:
      # get the ID of that label 
      orig_l_id = Label.objects.get(name=request.GET['orig_l']).id
    except Label.DoesNotExist:
      pass

  labels = Label.objects.filter(user=request.user)

  return render_to_response(template, 
                            { 'form' : form, 
                              't_id' : t_id, 
                              'l_ids' : l_ids, 
                              'labels' : labels, 
                              'orig_l_id' : orig_l_id, 
                              'get' : request.GET }, 
                  context_instance=RequestContext(request)) 

def util_clear_labels(task):
  """
  Removes all labels associated with the task that are active
  """
  for label in task.labels.all():
    if label.active and not label.hidden:
      task.labels.remove(label)


def util_unknown_task(request):
  """
  Sets an error message and returns the user to the appropriate
  task view 
  """
  # in this case we do not know what which task to edit
  messages.error(request, 'Could not edit the specified task')
  # re-direct to the home page 
  return HttpResponseRedirect(util_return_url(request))


def util_return_url(request):
  """
  Returns a URL to which to forward the user to 
  """
  # attempt to return to the label we were in before adding a task 
  if request.method == 'POST' and 'orig_l_id' in request.POST:
    l_id = request.POST['orig_l_id']
    # TODO: handle system labels, starting with 's:'
    try:
      label = Label.objects.get(id=l_id)
      url = '%s?l=%s' % (reverse('url_index'), label.name)
      return url
    except Label.DoesNotExist:
      pass
  # default
  return reverse('url_index')


@login_required
def bookmarklet_task_add(request):
  return form_task_add(request, 'add_bookmarklet.html')


@login_required
def api_task_add(request):
  """
  Adds a task 
  
  Example incoming JSON data: 

  { 'task' : 'Task text', 'l_ids' : [1,2,3], 'priority' : 'HIG' }
  { 'task' : 'Task text', 'l_ids' : [3], 'priority' : 'NOR' }
  """

  if request.method == 'POST' and 'json' in request.POST:
    data = simplejson.loads(request.POST['json'])

    if 'task' in data:
      text = data['task']
      l_ids = data['l_ids']

      # create task
      task = Task(user=request.user, task=text)
      task.save()
      # save new labels
      for s_l_id in l_ids:
        try:
          l_id = int(s_l_id)
          label = Label.objects.get(id=l_id)
          # task labeled 
          task.labels.add(label)
        except (Label.DoesNotExist, ValueError):
          pass

      # update priority if it is available
      if 'priority' in data:
        pri = data['priority']
        if pri == 'HIG' or pri == 'NOR':
          task.priority = pri;
          
      # save
      task.save()

      return HttpResponse('True')
          
  return HttpResponse('False')


@login_required
def api_task_edit(request):
  """
  Renames a task
  """
  if request.method != 'POST':
    return HttpResponse('False')

  if 't_id' in request.POST and 't_text' in request.POST:
    t_id = request.POST['t_id']
    t_text = request.POST['t_text']
    try:
      task = Task.objects.get(id=t_id)
      if (t_text == ""):
        # delete task
        task.delete()
      else:
        # update task 
        task.task = t_text
        task.save()
      return HttpResponse('True')
    except Task.DoesNotExist:
      pass

  return HttpResponse('False')
    

@login_required
def api_task_toggle(request):
  """
  Toggles a task between 'done' and 'not done'
  """
  if request.method == 'POST' and 'task_id' in request.POST:
    t_id = request.POST['task_id']
    try:
      task = Task.objects.get(id=t_id)
      task.done = not task.done
      task.save()
      return HttpResponse('True')
    except Task.DoesNotExist:
      pass

  return HttpResponse('False')


@login_required
def api_task_labels_save(request):
  """
  Saves labels for a given task
  """
  if request.method == 'POST' and 'json' in request.POST:
    data = simplejson.loads(request.POST['json'])
    if 't_id' in data:
      t_id = data['t_id']
      l_ids = data['l_ids']
      try:
        # remove old labels
        task = Task.objects.get(id=t_id)
        util_clear_labels(task)
        # save new labels
        for s_l_id in l_ids:
          try:
            l_id = int(s_l_id)
            label = Label.objects.get(id=l_id)
            # task labeled 
            task.labels.add(label)
          except (Label.DoesNotExist, ValueError):
            pass

        # update priority if it is available
        if 'priority' in data:
          pri = data['priority']
          if pri == 'HIG' or pri == 'NOR':
            task.priority = pri;
          
        # save
        task.save()
          
      except Task.DoesNotExist:
        pass
      
  return HttpResponse('False')


@login_required
def api_task_date_save(request):
  """
  Saves the due date for a task
  """
  if request.method == 'POST':
    if 't_id' in request.POST and 'date' in request.POST:
      t_id = request.POST['t_id']
      date = request.POST['date']
      try:
        task = Task.objects.get(id=t_id)
        if date == "":
          # remove due date
          due = None
        else:
          # parse and validate date format
          # ValueError thrown if date cannot be parsed 
          due = datetime.strptime(date, '%m/%d/%Y')
        task.due = due
        task.save()
        return HttpResponse('True')
      except Task.DoesNotExist:
        pass
      except ValueError:
        # date in wrong format 
        pass
  return HttpResponse('False')


@login_required
@require_http_methods(['POST'])
def api_label_add(request):
  """
  Adds a label
  """
  if 'label' in request.POST:
    label = request.POST['label']
    # check that the label name does not already exist
    try:
      Label.objects.get(user=request.user, name=label)
      messages.add_message(request, messages.ERROR, 'The label already exists')
    except Label.DoesNotExist:
      label = Label(user=request.user, name=label)
      label.save()
      messages.add_message(request, messages.SUCCESS, 'The label was created')
  return HttpResponseRedirect(reverse('url_label'))

# @login_required
# def api_label_add(request):
#   """
#   Adds a label
#   """
#   if request.method == 'POST' and 'label' in request.POST:
#     name = request.POST['label']
#     # check that the label name does not already exist
#     try:
#       Label.objects.get(user=request.user, name=name)
#       # do nothing if the label exists
#       pass
#     except Label.DoesNotExist:
#       # ffff99 is the 'default' color
#       label = Label(user=request.user, name=name, color="ffff99")
#       label.save()
#       json_wrapper = { 'l_id' : label.id }
#       json_dump = simplejson.dumps(json_wrapper)
#       return HttpResponse(json_dump, mimetype = 'application/json', 
#                           content_type = 'application/json; charset=utf8')

  return HttpResponse('False')


@login_required
def api_label_rename(request):
  """
  Renames a label
  """
  if request.method == 'POST':
    if 'l_id' in request.POST and 'label' in request.POST:
      l_id = request.POST['l_id']
      name = request.POST['label']
  
      try:
        label = Label.objects.get(id=l_id, user=request.user)
        label.name = name
        label.save()
      except Label.DoesNotExist:
        pass

      return HttpResponse('True')

  return HttpResponse('False')


@login_required
def api_label_delete(request):
  """
  Deletes a label (actually, marks it inactive) 
  """
  if request.method == 'POST' and 'l_id' in request.POST:
    try:
      l_id = request.POST['l_id']
      label = Label.objects.get(id=l_id)
      # mark label as inactive 
      # (the label will no longer be part of the default QuerySet)
      label.active = False
      label.save()
      return HttpResponse('True')
    except Label.DoesNotExist:
      pass
  return HttpResponse('False')


@login_required
def api_label_save(request):
  """
  Saves information for a single label, including color preferences
  and hidden status
  """
  if request.method == 'POST':
    if 'l_id' in request.POST:
      l_id = request.POST['l_id']
      try:
        label = Label.objects.get(id=l_id)
        # color 
        if 'color' in request.POST:
          color = request.POST['color']          
          label.color = color
        # hidden status 
        if 'hidden' in request.POST:
          hidden = request.POST['hidden']
          label.hidden = True if hidden == 'True' else False
        # save label 
        label.save()
        return HttpResponse('True')
      except Label.DoesNotExist:
        pass
  # default 
  return HttpResponse('False')


@login_required
def api_labels_save(request):
  """
  Saves label information (color preferences) for a set of labels
  """
  if request.method == 'POST' and 'json' in request.POST:
    data = simplejson.loads(request.POST['json'])
    for d in data:
      try:
        label = Label.objects.get(id=d['id'])
        label.color = d['color']
        label.save()
      except Label.DoesNotExist:
        pass
    return HttpResponse('True')
  print "NO"
  return HttpResponse('False')
  

@login_required
def ajax_response_test(request):
  """
  Only for testing
  """
  return HttpResponse('True')


def test(request):
  """
  A view for testing
  """
  messages.info(request, 'You did it!')
  #messages.success(request, 'You did it!')
  #messages.error(request, 'You did it!')

  return render_to_response('test.html', 
                            { }, 
                            context_instance=RequestContext(request)) 

def robots(request):
  """
  Returns a robots.txt file
  """
  return render_to_response('robots.txt', {}, mimetype = 'text/plain') 


def googlesitemap(request):
  """
  Returns an XML sitemap
  """
  return render_to_response('sitemap.xml', {}, mimetype = 'application/xml') 

