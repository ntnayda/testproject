from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    
    # Django automatically creates a primary key ID... No need to create one here

    user = models.OneToOneField(User)
    group = models.CharField(max_length=128, default=None, null=True, blank=True)
    reports_owned = models.ManyToManyField('Report', blank=True)
    

    def __str__(self):
    	return self.firstName + " " + self.lastName

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

# Create Reports model
class Report(models.Model):

	owned_by = models.ForeignKey('Profile')
	created = models.DateTimeField(auto_now_add=True)
	short_desc = models.CharField(max_length=128)
	long_desc = models.TextField()
	file_attached = models.CharField(max_length=128) # will eventually be a field that holds any file type
	
	'''ACCESSIBILITY_CHOICES = [
		('Public', 'Can be seen by any user of the system.')
		('Private', 'Can only be seen by those given access.')
	]

	accessibilty = models.CharField(choices=ACCESSIBILITY_CHOICES, default="Public")'''


class Conversation(models.Model):

    sender = models.ForeignKey(User, related_name="sender")
    reciever = models.ForeignKey(User,related_name="reciever")
    reciever_name = models.CharField(max_length=128)
    recently_used = models.DateTimeField(auto_now_add=True)
    messages = models.ManyToManyField('Message',blank=True)

    def __str__(self):
        return self.reciever_name

class Message(models.Model):
    owned_by = models.ForeignKey('Conversation')
    sender = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    messagecontent = models.CharField(max_length = 1000)

    def __str__(self):
        return self.messagecontent