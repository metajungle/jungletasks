from django.template import RequestContext 
from django.shortcuts import render_to_response, redirect

from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from django.contrib.auth.models import User
# from django.contrib.auth import logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import django.contrib.auth as auth

from django.http import HttpResponseRedirect

from django.db.models.signals import post_save

from forms import SignupForm, LoginForm, ChangePasswordForm, ResetPasswordForm

import utils 
import models

def login(request):
    """
    A view for logging in users 
    """

    # forward users who are already logged in to their homepage
    if request.user.is_authenticated():
        msg = 'You are already logged in and are forwarded to your Inbox'
        messages.info(request, msg)
        return HttpResponseRedirect(reverse('url_index'))

    next = None
    invalid = False
    if request.method == 'POST':

        # propagate 'next'
        if 'next' in request.POST:
            next = request.POST['next']

        form = LoginForm(request.POST)
        if form.is_valid():
            # get the username
            # (if there is no username, the form is not valid)
            username = form.get_username()
            password = form.cleaned_data['password']
            # authenticate 
            user = auth.authenticate(username=username, password=password)
            # (if the User object is not active, the form is not valid)
            if user is not None:
                # login
                auth.login(request, user)
                # check redirect
                if 'next' in request.POST:
                    next = request.POST['next']
                    return HttpResponseRedirect(next)
                # re-direct to home page
                return HttpResponseRedirect(reverse('url_index'))
            else:
                invalid = True
    else:
        # create an empty form
        form = LoginForm()

    # propagate 'next' 
    if request.method == 'GET' and 'next' in request.GET:
        next = request.GET['next']

    return render_to_response('registration/login.html', 
                              { 'form' : form,
                                'next' : next, 
                                'invalid' : invalid },
                  context_instance=RequestContext(request)) 


def register(request):
    """
    A view for registering a new user
    """

    if request.method == 'POST': 
        form = SignupForm(request.POST) 
        if form.is_valid(): 
            # create the user account itself
            # (it will be inactive) 
            user = form.create_user()
            # send email with verification code 
            utils.send_email_verification_email(request, user)
            # re-direct to information message 
            msg = """
            Thanks for registering! A verification email with further 
            instructions has been sent. 
            """
            messages.success(request, msg)
            return redirect('url_login')
    else:
        form = SignupForm()

    return render_to_response('registration/register.html', 
                              { 'form' : form }, 
                  context_instance=RequestContext(request)) 


@require_GET
def confirm_email(request):
    """
    Confirm an email address
    """
    success = False
    if 'code' in request.GET:
        code = request.GET.get('code') or ''
        try:
            ec = models.EmailConfirmation.objects.get(code=code)
            user = ec.user
            # make the user active
            user.is_active = True
            user.save()
            success = True
            # remove confirmation code 
            ec.delete()
            # send notification email 
            utils.send_signup_notification_msg()
            msg = """
                Your email was successfully confirmed.
                You can now login.
                """
            messages.success(request, msg)
            return redirect('url_login')
        except models.EmailConfirmation.DoesNotExist:
            msg = """
                The confirmation code you used could not be recognized.
                """
            messages.error(request, msg)
            return redirect('url_index')
            
    msg = """
        An error occurred with your email confirmation, please try again. 
        """
    messages.error(request, msg)
    return redirect('url_index')


@login_required
def password_change(request):
    """
    A view for changing a password
    """

    if request.method == 'POST': 
      form = ChangePasswordForm(request.POST) 
      if form.is_valid(): 
        email = form.cleaned_data.get('email')
        if email == 'demo@jungletasks.com':
          msg = 'The demo user cannot change the password'
          messages.error(request, msg)
        else:
          # change the password
          form.change_password(request.user)
          # re-direct to information message 
          msg = """
          Your password was successfully changed!
          """
          messages.success(request, msg)
    else:
        form = ChangePasswordForm()

    return render_to_response('account/password_change.html', 
                              { 'form' : form }, 
                  context_instance=RequestContext(request)) 


def password_reset(request):
    """
    A view for resetting a user's password
    """
    if request.method == 'POST': 
        form = ResetPasswordForm(request.POST) 
        if form.is_valid(): 
            email = form.cleaned_data.get('email')
            if email == 'demo@jungletasks.com':
              msg = 'The demo user cannot reset the password'
              messages.error(request, msg)
            else:
              user = form.get_user()
              # generate and set new password
              password = utils.user_password_reset(user)
              # send email 
              utils.send_reset_password_email(request, user, password)
              # message 
              msg = 'Your new password has been sent to your email address'
              messages.success(request, msg)
    else:
        form = ResetPasswordForm()

    # display information if user is already logged in 
    if request.user.is_authenticated():
        url = reverse('url_password_change')
        msg = '''You are currently logged in, you may instead want to
                 <a href="%s" class="alert-link">change your password</a>.''' % url
        messages.info(request, msg)

    return render_to_response('account/password_reset.html', 
                              { 'form' : form, 'request' : request }, 
                  context_instance=RequestContext(request)) 



## 
## SIGNALS
##

def user_post_save(sender, instance, **kwargs):
    """
    Gets or creates a user profile for the saved user
    """
    profile, new = models.UserProfile.objects.get_or_create(user=instance)

post_save.connect(user_post_save, sender=User)

