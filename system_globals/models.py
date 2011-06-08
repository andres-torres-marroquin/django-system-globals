import re
from django.db import models
from django.utils.translation import ugettext_lazy as _

class SytemGlobalManager(models.Manager):
    
    def get_value(self, var_name):
        """
        Given a variable name, returns SystemGlobal coerced value.
        """
        return self.get(var_name=var_name).coerced_value()
    
    def as_dict(self, prefix='', to_lower=False, coerce=True):
        """
        Given a prefix, searches all the SystemGlobals which starts with that
        prefix, and create a dictionary where the keys haven't that prefix,
        otherwise gets all the SystemGlobals. The prefix is case-insensitive.

        If to_lower parameter is set to True the dict keys would be lowercase.
        """
        if prefix:
            system_globals = self.filter(var_name__istartswith=prefix)
            prefix_len = len(prefix)
        else:
            system_globals = self.all()
            prefix_len = 0

        system_globals = system_globals.values('var_name', 'value')
        value_dict = {}
        for system_global in system_globals:
            var_name = system_global['var_name']
            value = system_global['value']
            var_name = var_name.lower() if to_lower else var_name
            var_name = var_name[prefix_len:]
            value_dict[var_name] = SystemGlobal.coerce(value) if coerce else value

        return dict([(str(k), v) for k, v in value_dict.items()])
    
    def set(self, var_name, value):
        """
        Make a atomic query for set a new value for a existent SystemGlobal, or
        create the new variable and set the new value.
        """
        updated_rows = self.filter(var_name=var_name).update(value=value)
        if updated_rows is 0:
            self.create(var_name=var_name, value=value)

class SystemGlobal(models.Model):
    """
    This model stores all the Globals that could be used in a System.
    """
    var_name = models.CharField(_(u'variable name'), max_length=100, unique=True)
    value = models.TextField(_(u'value'))
    description = models.TextField(_(u'description'), blank=True)
    
    objects = SytemGlobalManager()
    
    class Meta:
        verbose_name_plural = _(u'System Globals')
        
    def __unicode__(self):
        return "%s = %s" % (self.var_name, self.value)
    
    def coerced_value(self):
        return self.coerce(self.value)
    
    @staticmethod
    def coerce(raw_value):
        """
        Do some friendly type conversion.
        """
        val = raw_value.strip()
        if re.match(r'^(\d*)\.\d+$', val):  # float
            return float(val)
        elif re.match(r'^\d+$', val):  # int
            return int(val)
        elif val.lower() in ('true', 't', 'yes', 'y'):
            return True
        elif val.lower() in ('false', 'f', 'no', 'n'):
            return False
        else:   # must be a string
            return val
