import string
from random import choice

from django.conf import settings

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from models import EmailConfirmation
from jungletasks.settings import * 

import logging

logger = logging.getLogger(__name__)

def send_email_verification_email(request, user):
  """
  Generate a confirmation code and send it to a user 
  """
  # generate unique activation code and store in db
  while True:
    # create code 
    code = util_generate_code(24)
    # make sure it does not already exist
    try: 
      EmailConfirmation.objects.get(code=code)
    except EmailConfirmation.DoesNotExist:
      # store code in db
      ec = EmailConfirmation(user=user, code=code)
      ec.save()
      # break because we created a unique code 
      break 
  # send email 
  send_verification_email(request, user, code)


def send_verification_email(request, user, code):
  """
  Sends the given (activation) code to the user
  """
  to = user.email
  subject = "Verify email address"

  host = 'localhost:8000'
  if not DEBUG:
    try:
      host = JUNGLETASKS_DOMAIN
    except NameError:
      pass

  # get url for email verification
  url_verification = reverse('url_email_confirmation')

  link = "http://%s%s?code=%s" % (host, url_verification, code)

  message = """
  <p>Hello,</p>
  <p>Thanks for signing up with Jungle Tasks!</p>
  <p>This email is sent to verify your email address. 
  Please do not reply to this message.</p>
  <p>To verify your email address, please click on the link below:</p>
  <p>%s</p>
  <p>You may also copy and paste the link into your Web browser manually.</p>
  <p>Thank you!</p>
  """ % (link)

  email_noreply_send_html(subject=subject, body=message, to=[to])
    

def send_reset_password_email(request, user, password):
  """
  Notifies the user of the new password via email
  """
  to = user.email
  subject = "Password reset"

  host = 'localhost:8000'
  if not DEBUG:
    try:
      host = JUNGLETASKS_DOMAIN
    except NameError:
      pass  
      
  # get url for email verification
  url_password_change = reverse('url_password_change')

  link = "http://%s%s" % (host, url_password_change)

  message = """
  <p>Hi,</p>
  <p>Your <a href="%s">Jungle Tasks</a> 
     password has been reset.</p>
  <p>Your new password is: %s</p>
  <p>Please change your password as soon as possible: 
     <a href="%s">change password</a>.</p>
  <p>Thank you!</p>
  """ % (host, password, link)

  email_noreply_send_html(subject=subject, body=message, to=[to])


def email_noreply_send_html(subject, body, to):
  """ 
  Sends an HTML email, given subject, body and list of recipients
  """
  try:
    from_email = JUNGLETASKS_SEND_EMAIL_FROM
  except NameError:
    from_email = "Jungle Tasks (No-Reply) <noreply@localhost>"
  
  email_send(subject, body, from_email, to, html=True)


def email_send(subject, body, from_email, to, html=False):
  """ 
  Sends an email 
  """
  to_list = []
  if type(to).__name__ == 'list':
    to_list += to
  elif type(to).__name__ == "str":
    to_list.append(to)
    
  email = EmailMessage(subject=subject, body=body, 
                       from_email=from_email, to=to_list)
  if html:
    email.content_subtype = "html"
  email.send()


def user_password_reset(user):
  """ 
  Creates, sets and returns a random password for the user 
  """
  password = util_generate_password()
  user.set_password(password)
  user.save()
  return password


def util_generate_password():
  """ 
  Returns a generated password of length 8 
  """
  return util_generate_code(8)


def util_generate_code(num_chars):
  """ 
  Returns a num_chars long random string with letters and digits 
  """
  return ''.join([choice(string.letters + string.digits) for i in range(num_chars)])

def util_generate_uppercase_code(num_chars):
  """ 
  Returns a num_chars long random string with uppercase letters and digits 
  """
  return ''.join([choice(string.uppercase + string.digits) for i in range(num_chars)])
  

def util_remove_port(host):
  """
  Removes the port from a host and returns the result 
  """
  try:
    idx = host.index(":")
    return host[:idx]
  except ValueError:
    return host


def send_signup_notification_msg():
  subject = "User signed up"
  message = """
  <p>Hi,</p>
  <p>A user signed up to Jungle Tasks.</p>
  <p>Cheers,<br/>Admin</p>
  """ 
  try:
    if len(ADMINS) > 0:
      for admin in ADMINS:
        try:
          name = admin[0]
          email = admin[1]
          to = "%s <%s>" % (name, email)
          email_noreply_send_html(subject=subject, body=message, to=[to])
        except IndexError:
          logger.warning('Index error when getting admin name and email')
  except NameError:
    logger.warning("No admins defined in settings.py")
    
