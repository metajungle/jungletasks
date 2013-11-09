from django.template import RequestContext 
from django.shortcuts import render_to_response, redirect 
from django.contrib import messages

from django.http import HttpResponse, Http404

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from tasks.models import Task, Label

import time 
from datetime import datetime, timedelta

from utils import orgmode_write

@login_required
def tools(request):
  """
  Index page for various tools 
  """
  return render_to_response('tools/index.html', 
                            { }, 
                  context_instance=RequestContext(request)) 

@login_required
@require_GET
def tasks_export_preview_all(request):
  """
  Preview the tasks to be exported (ALL)
  """
  max = 10
  if 'max' in request.GET:
    max = request.GET.get('max')
  tasks = Task.objects.filter(user=request.user)[:max]
  return render_to_response('tools/export.html', 
                            { 'tasks' : tasks }, 
                  context_instance=RequestContext(request)) 


@login_required
@require_GET
def tasks_export_preview_label(request, id):
  """
  Preview the tasks to be exported (by label)
  """
  max = 10
  if 'max' in request.GET:
    max = request.GET.get('max')
  try:
    label = Label.objects.get(id=id)
    tasks = Task.objects.filter(user=request.user, labels=label)[:max]
    return render_to_response('tools/export.html', 
                              { 'tasks' : tasks, 
                                'label' : label }, 
                    context_instance=RequestContext(request)) 
  except Label.DoesNotExist:
    messages.error(request, 'No such label exists')
    return redirect('url_export_preview_all')

@login_required
@require_POST
def tasks_export(request):
  """
  Exporting tasks (ALL or by LABEL)
  """
  
  # refer to label-specific tasks 
  if 'label' in request.POST:
    try:
      label = Label.objects.get(id=request.POST.get('label'))
      tasks = Task.objects.filter(user=request.user, labels=label)
    except Label.DoesNotExist:
      messages.error(request, 'No such label exists')
      return redirect('url_export_preview_all')
  else:
    tasks = Task.objects.filter(user=request.user)  
  
  if len(tasks) > 0:
    # create the HttpResponse object with the appropriate header
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=tasks.org'
    # write tasks 
    contents = orgmode_write(tasks)
    response.write(contents)
    # return attachment
    return response
  
  raise Http404


@login_required
@require_GET
def activity_log(request):
  """
  Displays a log of completed tasks
  """
  now = datetime.now()
  year,week,dow = now.isocalendar()

  today_week = week
  today_year = year
  
  week = request.GET.get('week') or today_week
  year = request.GET.get('year') or today_year 

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

  total = Task.objects.filter(user=request.user, completed=True).count()

  total_week = 0
  tasks = {}
  dates = []
  for i in range(7):
    day = monday + timedelta(days=i)
    # add to the list of dates
    dates.append(day)
    # create a map from dates to tasks 
    tasks_ = Task.objects.filter(user=request.user, completed=True, date_completed__year=day.year, date_completed__month=day.month, date_completed__day=day.day)
    tasks[day] = tasks_
    # count
    total_week += len(tasks_)

  prev_year, prev_week, dow = (monday - timedelta(weeks=1)).isocalendar()
  next_year, next_week, dow = (monday + timedelta(weeks=1)).isocalendar()

  return render_to_response('tools/log.html', 
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

