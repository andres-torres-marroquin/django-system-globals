# django-system-globals
> Version 0.0.4

# What

django-system-globals is a Django App to manage any system globals from a DB.

# Installing

## First of all

    pip install django-system-globals

## Add it to your Django Project

INSTALLED_APPS on settings.py

    INSTALLED_APPS = (
        ...
        'system_globals',
        ...
    )

additionally you can add it to TEMPLATE_CONTEXT_PROCESSORS

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'system_globals.context_processors.system_globals',
        ...
    )

# Using it

    >>> from system_globals.models import SystemGlobal

    # setting PI
    >>> SystemGlobal.objects.set('MATH_PI', '3.1416')
    >>> SystemGlobal.objects.set('MATH_E', ' 2.7182 ')

    # retrieving PI
    >>> SystemGlobal.objects.get_value('MATH_PI')
    3.1416

    # retrieving E
    >>> SystemGlobal.objects.get_value('MATH_E')
    2.7182

    # retrieving various system globals
    >>> SystemGlobal.objects.as_dict()
    {'MATH_PI': 3.1416, 'MATH_E': 2.7182}

    >>> SystemGlobal.objects.as_dict(coerce=False)
    {'MATH_PI': '3.1416', 'MATH_E': ' 2.7182 '}

    >>> SystemGlobal.objects.as_dict(to_lower=True)
    {'math_pi': 3.1416, 'math_e': 2.7182}

    >>> SystemGlobal.objects.as_dict(prefix='MATH_')
    {'PI': 3.1416, 'E': 2.7182}

    >>> SystemGlobal.objects.as_dict(prefix='math_')
    {'PI': 3.1416, 'E': 2.7182}
