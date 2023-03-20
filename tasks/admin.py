from django.contrib import admin
from .models import Task

# Muestra un campo como solo lectura en el admin
class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created', )
    
admin.site.register(Task, TaskAdmin)
