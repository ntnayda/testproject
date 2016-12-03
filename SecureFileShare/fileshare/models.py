from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
    # Django automatically creates a primary key ID... No need to create one here

    user = models.OneToOneField(User)
    reports_owned = models.ManyToManyField('Report', blank=True)
    groups_in = models.ManyToManyField('ProfileGroup', blank=True)
    publickey = models.CharField(null=True, max_length=10000)
    unreadmessages = models.CharField(max_length=10,default="false")

    def __str__(self):
        return self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)


# Create Reports model
class Report(models.Model):
	owned_by = models.ForeignKey(User)
	created = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now_add=True, null=True)
	last_modified_by = models.CharField(default="Owner", max_length=128)
	short_desc = models.CharField("Title", max_length=128, unique=True)
	long_desc = models.TextField("Description")
	private = models.BooleanField("Restrict access to this file?", default=False)
	files = models.ManyToManyField('Documents', blank=True)
	is_encrypted = models.BooleanField("Is the attached file encrypted?", default=False, help_text="Leave blank if no file is attached.")
	in_folder = models.BooleanField(default=False)
	group_in = models.ManyToManyField('ProfileGroup', blank=True)
	
	def __str__(self):
		return self.short_desc


class Documents(models.Model):
    datetime = '%Y/%m/%d'
    file_attached = models.FileField("Upload a file", upload_to='reports/' + datetime, blank=True, null=True)

    def __str__(self):
        return str(self.file_attached)


class Folder(models.Model):
    name = models.CharField(max_length=128, unique=True)
    owned_by = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    reports = models.ManyToManyField(Report, blank=True)


class ProfileGroup(models.Model):
    creator = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField('Profile', related_name='group_members', blank=True)
    reports = models.ManyToManyField('Report', blank=True)
    def __str__(self):
        return self.name


class Conversation(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    reciever = models.ForeignKey(User, related_name="reciever")
    reciever_name = models.CharField(max_length=128)
    recently_used = models.DateTimeField()
    messages = models.ManyToManyField('Message', blank=True)
    unreadmessages = models.CharField(max_length=1000,default="0")

    def __str__(self):
        return self.reciever_name


class Message(models.Model):
    owned_by = models.ForeignKey('Conversation')
    sender = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    messagecontent = models.CharField(max_length=10000)
    key = models.CharField(null=True, max_length=10000)

    def __str__(self):
        return self.messagecontent
