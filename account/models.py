from django.db import models

from django.contrib.auth.models import User

import tasks.models as t_models

class EmailConfirmation(models.Model):
  """
  A model for holding email verification information 
  (user and confirmation code)
  """
  user = models.ForeignKey(User) 
  code = models.CharField(max_length=24, 
                          verbose_name="Email Confirmation Code", 
                          help_text="(A 24 character long verification code)")


class UserProfile(models.Model):
  """
  User profile model 
  """
  user = models.ForeignKey(User, unique=True)
  
  system_labels = models.ManyToManyField(t_models.SystemLabel)
  
