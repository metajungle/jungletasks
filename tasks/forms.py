from django import forms

import models

class TaskForm(forms.ModelForm):
  """
  A form for adding a task 
  """
  class Meta:
    model = models.Task
    exclude = ['user', 'done', 'due', 'labels']
    widgets = {
      'task': forms.TextInput(attrs={'class': 'form-control'}),
      'priority': forms.Select(attrs={'class': 'form-control'}),
    }    
  

