from django.db import models
from django.contrib.auth.models import User

class ActiveLabelManager(models.Manager):
  def get_query_set(self):
    """
    Returns only active labels
    """
    return super(ActiveLabelManager, self).get_query_set().filter(active=True)


class Label(models.Model):
  """
  A label
  """
  user = models.ForeignKey(User) 
  name = models.CharField(max_length=48,
                          help_text="No spaces, case-insensitive.")
  # auto_now_add is set when the object is created
  created = models.DateTimeField(auto_now_add=True)
  # auto_now is set when the object is saved
  edited = models.DateTimeField(auto_now=True)
  color = models.CharField(max_length=6, 
                           help_text="Hex code for color.", default='ffff99')
  # true if the label should not be shown in the home view 
  hidden = models.BooleanField(default=False)
  # active if False if the label is deleted 
  active = models.BooleanField(default=True)

  # the default manager (only handling active labels)
  objects = ActiveLabelManager()
  # access to all labels 
  history = models.Manager()

  def num_tasks(self):
    """
    Returns the number of tasks that have this (unique) label
    """
    return Task.objects.filter(labels=self).count()

  def num_not_done_tasks(self):
    """
    Returns the number of tasks that have this (unique) label
    and are not done
    """
    return Task.objects.filter(labels=self, done=False).count()  

  def is_hidden(self):
    """
    Returns True if the label is hidden, False otherwise
    """
    return self.hidden

  def is_active(self):
    """
    Returns True if the label is active, False otherwise
    """
    return self.active 


class SmartLabel(Label):
  """
  A smart label
  """
  OPERATOR_CHOICES = (
        ('AND', 'Conjunction'),
        ('OR', 'Disjunction'),
  )
  labels = models.ManyToManyField(Label, related_name='labels')
  operator = models.CharField(max_length=3, choices=OPERATOR_CHOICES)


class SystemLabel(models.Model):
  """
  A system label
  """
  SYSTEM_LABELS = (
        ('UNLABELED', 'Unlabeled'),
        ('PRIORITY', 'Priority'),
  )
  label = models.CharField(max_length=24, choices=SYSTEM_LABELS)


class Task(models.Model):
  """
  A task 
  """
  PRIORITIES = (
        ('HIG', 'High'),
        ('NOR', 'Normal'),
  )

  user = models.ForeignKey(User) 

  # TODO: add optional 'notes' field (TextField) 
  task = models.TextField(help_text="Content of a task")
  done = models.BooleanField(default=False)
  priority = models.CharField(max_length=3, choices=PRIORITIES, default='NOR')
  labels = models.ManyToManyField(Label)

  # auto_now_add is set when the object is created
  created = models.DateTimeField(auto_now_add=True)
  # auto_now is set when the object is saved
  edited = models.DateTimeField(auto_now=True)
  # auto_now is set when the object is saved
  finished = models.DateTimeField(auto_now=True)
  due = models.DateTimeField(blank=True, null=True)

  class Meta:
    ordering = ('priority', 'due', '-edited')

  def __unicode__(self):
    return self.task

  def pri_letter(self):
    if self.priority == 'HIG':
      return 'H'
    elif self.priority == 'NOR':
      return 'N'
    elif self.priority == 'LOW':
      return 'L'
    return self.priority

  def pri_high(self):
    return self.priority == 'HIG'
