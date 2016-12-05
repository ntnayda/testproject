from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from fileshare.models import *
from Crypto.PublicKey import RSA
from Crypto import Random
from django import forms
import os

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))
"""
class signup_form(forms.ModelForm):

    A form that creates a user, with no privileges, from the given username and
    password.

    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        'incorrect_email': ("The email address entered is incorrect"),
    }
    #email = forms.CharField(label= _("Email"),widget=forms.TextInput)

    password1 = forms.CharField(label=("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username","email","first_name","last_name",)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not validate_email(email):
            raise forms.ValidationError(self.error_messages['incorrect_email'],code='incorrect_email')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(signup_form, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        privatekey = None
        if commit:
            user.save()
            random_generator = Random.new().read
            key = RSA.generate(1024, random_generator)
            pubkey = key.publickey()
            privatekey = key.privatekey()
            user.profile.publickey = pubkey
        return user
"""
class signup_form(forms.ModelForm):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        'incorrect_email': ("The email address entered is incorrect"),
    }
    #email = forms.CharField(label= _("Email"),widget=forms.TextInput)

    password1 = forms.CharField(label=("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username","email","first_name","last_name",)


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['short_desc', 'long_desc', 'private', 'is_encrypted']

class UpdateProfile(forms.ModelForm):

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name','email',)


class messageForm(forms.ModelForm):
    messagecontent = forms.CharField(required=True)
    newmessagefield = forms.CharField(required=False)
    thekey = forms.CharField(required=False)
    class Meta:
        model = Message
        fields = ('owned_by','sender','messagecontent','thekey','newmessagefield')

class GroupForm(forms.ModelForm):
    class Meta:
        model = ProfileGroup
        fields = ['name', 'members']

class UpdateGroupForm(forms.ModelForm):
    class Meta:
        model = ProfileGroup
        fields = ['name']

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class UpdateFolder(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'reports']


class DecryptMessageForm(forms.ModelForm):
    password = forms.CharField(required=True)
    #message = forms.ModelMultipleChoiceField(queryset=Message.objects.all())

    class Meta:
        model = Message
        fields = ['password']


class SearchForm(forms.Form):
    search = forms.CharField(max_length='128', widget=forms.TextInput(attrs={'cols': 50, 'rows': 1, 'placeholder': "Search for a report"}))
    SEARCH_OPTIONS = (
            ('desc', "Description"),
            ('owner', "Owned By"),
            ('created', "Created",),
            ('modified', "Last Modified"),
        )
    parameter = forms.CharField(widget=forms.Select(choices=SEARCH_OPTIONS))
    datepicker = forms.DateField(widget=forms.SelectDateWidget())

class ReportCommentsForm(forms.ModelForm):
    comment = forms.CharField(required=True, max_length="1000", widget=forms.TextInput(attrs={'cols': 75, 'rows': 2, 'placeholder': "Leave a comment"}))

    class Meta:
        model = ReportComments
        fields = ['comment']

