import re

import django
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class SystemGlobalQuerySet(models.query.QuerySet):
    """QuerySet implementation that refreshes the cache on update."""
    def update(self, **kwargs):
        updated_rows = super(SystemGlobalQuerySet, self).update(**kwargs)

        if 'value' in kwargs:
            for var_name in self.values_list('var_name', flat=True):
                SystemGlobal.objects._update_cache(var_name, kwargs['value'])

        return updated_rows


class SytemGlobalManager(models.Manager):
    """
    Manager for the SystemGlobal class, with
    helper methods and cache management.
    """
    def get_queryset(self):
        return SystemGlobalQuerySet(SystemGlobal)

    if django.VERSION < (1, 6):
        get_query_set = get_queryset

    def get_value(self, var_name):
        """
        Given a variable name, returns SystemGlobal coerced value.
        """
        cached_dict = self._get_dict()
        if var_name in cached_dict:
            value = cached_dict.get(var_name)
            return SystemGlobal.coerce(str(value))

        raise SystemGlobal.DoesNotExist('%s was not set in SystemGlobals.' % var_name)

    def as_dict(self, prefix='', to_lower=False, coerce=True):
        """
        Given a prefix, searches all the SystemGlobals which starts with that
        prefix, and create a dictionary where the keys haven't that prefix,
        otherwise gets all the SystemGlobals. The prefix is case-insensitive.

        If to_lower parameter is set to True the dict keys would be lowercase.
        """
        cached_dict = self._get_dict()

        result_dict = {}
        prefix_len = len(prefix)
        for key in cached_dict.keys():
            if key.lower().startswith(prefix.lower()):
                value = str(cached_dict[key])
                key = key.lower() if to_lower else key
                key = key[prefix_len:]
                result_dict[key] = SystemGlobal.coerce(value) if coerce else value

        return result_dict

    def set(self, var_name, value):
        """
        Make a atomic query for set a new value for a existent SystemGlobal, or
        create the new variable and set the new value.
        """
        updated_rows = self.filter(var_name=var_name).update(value=value)
        if not updated_rows:
            self.create(var_name=var_name, value=value)

        self._update_cache(var_name, value)

    def _update_cache(self, var_name, value):
        cached_dict = self._get_dict()
        cached_dict[var_name] = value
        cache.set('SystemGlobals', cached_dict)

    def _get_dict(self):
        cached_dict = cache.get('SystemGlobals')
        if cached_dict is not None:
            return cached_dict
        return self._update_dict_from_db()

    def _update_dict_from_db(self):
        system_globals = self.all().values('var_name', 'value')
        dictionary = {}
        for system_global in system_globals:
            var_name = system_global['var_name']
            value = system_global['value']
            dictionary[var_name] = value

        dictionary = dict([(str(k), v) for k, v in dictionary.items()])
        cache.set('SystemGlobals', dictionary)
        return dictionary


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


def update_cached_global(sender, instance, **kwargs):
    SystemGlobal.objects._update_cache(instance.var_name, instance.value)

post_save.connect(update_cached_global, sender=SystemGlobal, dispatch_uid="update_cached_global")
