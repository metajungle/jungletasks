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
  color = models.CharField(max_length=9, 
                           help_text="Hex code for color.", default='#ffff99')
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
    return Task.objects.filter(labels=self, completed=False).count()  

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

  task = models.CharField(max_length=1024, help_text="The task")
  notes = models.TextField(blank=True, null=True)
  completed = models.BooleanField(default=False)
  priority = models.CharField(max_length=3, choices=PRIORITIES, default='NOR')
  labels = models.ManyToManyField(Label)

  # auto_now_add is set when the object is created
  date_created = models.DateTimeField(auto_now_add=True)
  # auto_now is set when the object is saved
  date_edited = models.DateTimeField(auto_now=True)
  date_completed = models.DateTimeField(blank=True, null=True)
  # due date 
  date_due = models.DateTimeField(blank=True, null=True)

  class Meta:
    ordering = ('priority', 'date_due', '-date_edited')

  def __unicode__(self):
    return self.task

  def is_completed(self):
    """ returns True if the task is marked as completed, False otherwise """
    return self.completed

  def is_important(self):
    return self.priority == 'HIG'

  def label_ids(self):
    """ returns the IDs of the associated labels """
    return [l.id for l in self.labels.all()]
    
  def label_ids_str(self):
    """ returns a string with the label IDs space-separated """
    return ' '.join([str(l) for l in self.label_ids()])

