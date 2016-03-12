# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings as django_settings
from slackbot import default_settings

defaults = dict()
for k in default_settings.__dict__:
    if k.isupper() and not k.startswith('_'):
        defaults[k] = getattr(default_settings, k)

changed = dict()

for k in defaults.keys():
    key = 'SLACKBOT_%s' % k
    try:
        changed[key.replace('SLACKBOT_', '')] = django_settings.__getattr__(key)
    except AttributeError:
        pass


class Settings(object):

    def __init__(self, changed, defaults):
        self._wrapped = defaults
        self._wrapped.update(changed)

    def __getattribute__(self, name):
        if name != '_wrapped' and name in self._wrapped:
            return self._wrapped[name]
        return super(Settings, self).__getattribute__(name)


settings = Settings(changed, defaults)