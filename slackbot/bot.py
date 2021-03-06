# -*- coding: utf-8 -*-
from __future__ import absolute_import
import imp
import importlib
import logging
import re
import time
from glob import glob
from six.moves import _thread
from slackbot.conf import settings
from slackbot.manager import PluginsManager
from slackbot.slackclient import SlackClient
from slackbot.dispatcher import MessageDispatcher
from slackbot.utils import set_thread_name, set_default_thread_name

logger = logging.getLogger(__name__)


class Bot(object):

    def __init__(self, bot_access_token, plugins=None, thread_name=None):
        self.thread_name = thread_name
        set_default_thread_name(self.thread_name)

        plugins = plugins or ['slackbot.plugins']
        PluginsManager.set_plugins(plugins)

        self._client = SlackClient(
            token=bot_access_token,
            bot_icon=settings.BOT_ICON if hasattr(settings, 'BOT_ICON') else None,
            bot_emoji=settings.BOT_EMOJI if hasattr(settings, 'BOT_EMOJI') else None
        )
        self._plugins = PluginsManager()
        self._dispatcher = MessageDispatcher(self._client, self._plugins)

    def run(self):
        self._plugins.init_plugins()
        self._dispatcher.start()
        self._client.rtm_connect()
        _thread.start_new_thread(self._keepactive, tuple())
        logger.info('connected to slack RTM api')
        self._dispatcher.loop()

    def _keepactive(self):
        set_thread_name('KeepActive')
        logger.debug('keep active thread started')
        while True:
            time.sleep(30 * 60)
            self._client.ping()


def respond_to(matchstr, flags=0):
    def wrapper(func):
        PluginsManager.commands['respond_to'][re.compile(matchstr, flags)] = func
        logger.info('registered respond_to plugin "%s" to "%s"', func.__name__, matchstr)
        return func
    return wrapper


def listen_to(matchstr, flags=0):
    def wrapper(func):
        PluginsManager.commands['listen_to'][re.compile(matchstr, flags)] = func
        logger.info('registered listen_to plugin "%s" to "%s"', func.__name__, matchstr)
        return func
    return wrapper
