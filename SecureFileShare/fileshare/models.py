from django.db import models

# Create your models here.
class User(models.Model):
    
    # Django automatically creates a primary key ID... No need to create one here

    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    userName = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True)
    group = models.CharField(max_length=128, default=None, blank=True)
    reports_owned = models.ManyToManyField('Report', blank=True)
    

    def __str__(self):
    	return self.firstName + " " + self.lastName


# Create Reports model
class Report(models.Model):

	owned_by = models.ForeignKey('User')
	created = models.DateTimeField(auto_now_add=True)
	short_desc = models.CharField(max_length=128)
	long_desc = models.TextField()
	file_attached = models.CharField(max_length=128) # will eventually be a field that holds any file type
	
	'''ACCESSIBILITY_CHOICES = [
		('Public', 'Can be seen by any user of the system.')
		('Private', 'Can only be seen by those given access.')
	]

	accessibilty = models.CharField(choices=ACCESSIBILITY_CHOICES, default="Public")'''