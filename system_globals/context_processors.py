from system_globals.models import SystemGlobal 

def system_globals(request):
    return { 'system_globals': SystemGlobal.objects.as_dict()}