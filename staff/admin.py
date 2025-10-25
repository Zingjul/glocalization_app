from django.contrib import admin
from .models import StaffBoardPost, AuditLog

admin.site.register(StaffBoardPost)
admin.site.register(AuditLog)
