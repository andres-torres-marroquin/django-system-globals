#!/usr/bin/env python
import os
from system_globals import version
from setuptools import setup

def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('system_globals'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

setup(name='django-system-globals',
    version=version,
    description='A Django App to manage any system globals from a DB table.',
    author=u'Andres Torres Marroquin',
    author_email='andres.torres.marroquin@gmail.com',
    url='https://github.com/andres-torres-marroquin/django-system-globals',
    packages=get_packages(),
)
