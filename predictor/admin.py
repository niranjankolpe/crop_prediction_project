from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CropDetails)
admin.site.register(ContactUsTicket)
admin.site.register(ErrorLogs)
admin.site.register(ActivityLogs)
admin.site.register(LoginActivity)