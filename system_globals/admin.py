from django.contrib import admin
from system_globals.models import SystemGlobal

class SystemGlobalAdmin(admin.ModelAdmin):
    list_display = ('var_name', 'value', 'description',)

admin.site.register(SystemGlobal, SystemGlobalAdmin)

