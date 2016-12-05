from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


class ProfileInLine(admin.StackedInline):
	model = Profile
	can_delete = False
	#verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
	inlines = (ProfileInLine, )

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Report)
admin.site.register(ProfileGroup)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Documents)
admin.site.register(Folder)
admin.site.register(Profile)
admin.site.register(ReportComments)