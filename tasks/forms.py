from django import forms

import models

class TaskForm(forms.ModelForm):
  """
  A form for adding a task 
  """
  class Meta:
    model = models.Task
    exclude = ['user', 'completed', 'date_due', 'date_completed', 'labels']
    widgets = {
      'task': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task'}),
      'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notes', 'rows': 10}),
      'priority': forms.Select(attrs={'class': 'form-control'}),
    }
    
  def clean_task(self):
    task = self.cleaned_data.get('task', '')
    if task == '':
      raise forms.ValidationError(_('The task cannot be empty'))
    return task
    

