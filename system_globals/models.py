from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

class SytemGlobalManager(models.Manager):
    
    def set(self, var_name, value):
        self.filter(var_name=var_name).update(value=value)

class SystemGlobal(models.Model):
    var_name = models.CharField(_(u'variable name'), max_length=100, unique=True)
    value = models.TextField(_(u'value'))
    description = models.TextField(blank=True)
    
    objects = SytemGlobalManager()
    
    class Meta:
        verbose_name_plural = _(u'System Globals')
        
    def __unicode__(self):
        return "%s = %s" % (self.var_name, self.value)
