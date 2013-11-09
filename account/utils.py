import string
from random import choice

from django.conf import settings

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from models import EmailConfirmation

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

    host = util_get_host_address(request)
  
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

    host = util_get_host_address(request)
  
    # get url for email verification
    url_password_change = reverse('url_password_change')
  
    link = "http://%s%s" % (host, url_password_change)

    message = """
    <p>Hi,</p>
    <p>Your <a href="http://jungletasks.com">Jungle Tasks</a> 
       password has been reset.</p>
    <p>Your new password is: %s</p>
    <p>Please change your password as soon as possible: 
       <a href="%s">change password</a>.</p>
    <p>Thank you!</p>
    """ % (password, link)
  
    email_noreply_send_html(subject=subject, body=message, to=[to])


def email_noreply_send_html(subject, body, to):
  """ 
  Sends an HTML email, given subject, body and list of recepients
  """
  from_email = "Jungle Tasks (No-Reply) <noreply@metajungle.net>"
  #old = settings.EMAIL_HOST_USER
  #settings.EMAIL_HOST_USER = 'noreply@metajungle.net'
  
  email_send(subject, body, from_email, to, html=True)
  
  #settings.EMAIL_HOST_USER = old


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
                       from_email=from_email, to=to_list,
                       headers = {'Reply-To': 'Jungle Tasks <tasks@metajungle.net>'})
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
  

def util_get_host_address(request):
  """
  Returns the host address used for a request
  """
  host = util_get_client_ip(request)
  if 'SERVER_PORT' in request.META:
    port = request.META['SERVER_PORT']
    # if the port is the standard "80" we do not need to include it
    if port != "80":
      host += ":" + port
  return host 
  
  
def util_get_client_ip(request):
  """
  Returns the client IP address 
  """
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip  

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
    to = "Jakob Henriksson <jakob@metajungle.net>"
    subject = "User signed up"
    message = """
    <p>Hi,</p>
    <p>A user signed up to Jungle Tasks.</p>
    <p>Cheers,<br/>Jakob</p>
    """ 
    email_noreply_send_html(subject=subject, body=message, to=[to])
    
