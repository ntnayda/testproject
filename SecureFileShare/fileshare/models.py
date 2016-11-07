from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    
    # Django automatically creates a primary key ID... No need to create one here

    user = models.OneToOneField(User)
    #group_member_of = models.ManyToManyField('Group', blank=True)
    reports_owned = models.ManyToManyField('Report', blank=True)
    


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

# Create Reports model
class Report(models.Model):

	owned_by = models.OneToOneField(User)
	created = models.DateTimeField(auto_now_add=True)
	short_desc = models.CharField(max_length=128)
	long_desc = models.TextField()
	private = models.BooleanField(default=False)
	file_attached = models.FileField(upload_to='documents/%Y/%m/%d', blank=True)
	#group = models.ForeignKey('ProfileGroup', blank=True)	
	
	'''ACCESSIBILITY_CHOICES = [
		('Public', 'Can be seen by any user of the system.')
		('Private', 'Can only be seen by those given access.')
	]

	accessibilty = models.CharField(choices=ACCESSIBILITY_CHOICES, default="Public")'''

class ProfileGroup(models.Model):

	name = models.CharField(max_length=128, unique=True)
	members = models.ManyToManyField('Profile', null=True, blank=True)