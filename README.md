# django-system-globals
> Version 0.0.1

# What

django-system-globals is a Django App to manage any system globals from a DB 

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
