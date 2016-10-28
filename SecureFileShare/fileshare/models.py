from django.db import models

# Create your models here.
class User(models.Model):
    
    # Django automatically creates a primary key ID... No need to create one here

    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    userName = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    group = models.CharField(max_length=128, default=None)
    

    def __str__(self):
    	return self.firstName + " " + self.lastName


# Create Reports model