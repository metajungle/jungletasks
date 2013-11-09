from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.utils.translation import ugettext_lazy as _

class LoginForm(forms.Form):
    """
    A form for logging in users
    """
    email = forms.EmailField(label="E-mail", help_text = "Required",
                             required=True, 
                             widget=forms.TextInput(attrs={'class':'form-control special-form-control'})) 
    password = forms.CharField(label="Password", help_text = "Required", 
                              required=True, 
                              widget=forms.PasswordInput(attrs={'class':'form-control special-form-control'}))

    def clean_email(self):
        """
        Checks that the email has a User object associated with it
        and that the User object is active 
        """
        e = self.cleaned_data['email']
        try:
            user = User.objects.get(email=e)
            if not user.is_active:
                msg = 'This user account has not been confirmed yet'
                raise forms.ValidationError(msg)
        except User.DoesNotExist:
            pass
            # msg = 'This email is not associated with an account'
            # raise forms.ValidationError(msg)
        return e

    def get_username(self):
        """
        Returns the User object if the form is valid
        """
        if not self.is_valid():
            return None
        try:
            # NOTE: all emails stored in lower-case
            email = self.clean_email().lower()
            return User.objects.get(email=email).username
        except User.DoesNotExist:
            pass
        return None


class SignupForm(forms.Form):
    """
    A for for signing up users 
    """
    email = forms.EmailField(label="E-mail", help_text = "Required",
                             required=True,
                             widget=forms.TextInput(attrs={'class':'form-control special-form-control'})) 
    password1 = forms.CharField(label="Password", help_text = "Required", 
                                required=True, 
                                widget=forms.PasswordInput(attrs={'class':'form-control special-form-control'}))
    password2 = forms.CharField(label="Password confirmation", help_text = "Required", 
                                required=True,
                                widget=forms.PasswordInput(attrs={'class':'form-control special-form-control'}))

    def clean_email(self):
        """ 
        Checks that the email is not already in use
        """
        # NOTE: all emails are stored in lower case
        e = self.cleaned_data['email'].lower()
        if User.objects.filter(email=e).count() > 0:
            raise forms.ValidationError('An existing account is using that email address.')
        return e

    def clean_password2(self):
        """
        Checks that the passwords are the same
        """
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError('The passwords did not match.')
        return password2

    def create_user(self):
        """
        Creates a User object (it will be inactive) 
        """
        if not self.is_valid():
            return None
        # generate a username 
        ids = User.objects.values_list('id', flat=True).order_by('-id')[:1]
        if len(ids) > 0:
            # ids[0] will be the maximum value (due to order_by: '-id')
            idnum = ids[0] + 1
        else:
            idnum = 1
        # create User object 
        username = "user%s" % idnum
        # NOTE: store email in lower case
        email = self.clean_email().lower()
        password = self.clean_password2()
        user = User(username=username, email=email, password='tmp')
        user.save()
        # set the real password
        user.set_password(password)
        # make user inactive (until user has confirmed account)
        user.is_active = False
        # update
        user.save()
        return user 


class ChangePasswordForm(forms.Form):
    """
    A form for changing password 
    """
    password1 = forms.CharField(label="Password", help_text = "Required", 
                                required=True, 
                                widget=forms.PasswordInput(attrs={'class':'form-control special-form-control'}))
    password2 = forms.CharField(label="Password confirmation", help_text = "Required", 
                                required=True,
                                widget=forms.PasswordInput(attrs={'class':'form-control special-form-control'})) 

    def clean_password2(self):
        """
        Checks that the passwords are the same
        """
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError('The passwords did not match.')
        return password2


    def change_password(self, user):
        """
        Changes the password for the given user
        """
        if not self.is_valid():
            return None
        password = self.clean_password2()
        user.set_password(password)
        user.save()
        return user
        
        
class ResetPasswordForm(forms.Form):
    """
    A form for resetting a password 
    """
    email = forms.EmailField(label="E-mail", help_text = "Required",
                             required=True,
                             widget=forms.TextInput(attrs={'class':'form-control special-form-control'})) 
                             
    def clean_email(self):
        """
        Checks that the email is valid 
        """
        # NOTE: all emails are stored in lower-case
        e = self.cleaned_data['email'].lower()
        try:
            user = User.objects.get(email=e)
            if not user.is_active:
                msg = 'This user account has not been confirmed yet'
                raise forms.ValidationError(msg)
        except User.DoesNotExist:
            msg = 'This email is not associated with an account'
            raise forms.ValidationError(msg)
        return e

    def get_user(self):
        """
        Returns the User object for the email address
        """
        if not self.is_valid():
            return None
        # error checking done in: clean_email
        # NOTE: all emails are stored in lower-case
        e = self.clean_email().lower()
        return User.objects.get(email=e)
        
