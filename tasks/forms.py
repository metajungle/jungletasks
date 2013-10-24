from django import forms

import models

class AddTaskForm(forms.ModelForm):
  """
  A form for adding a task 
  """
  class Meta:
    model = models.Task
    exclude = ['user', 'done', 'due', 'labels']
  

