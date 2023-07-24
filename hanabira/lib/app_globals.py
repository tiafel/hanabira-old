"""The application's Globals object"""
import os

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from hanabira.model.settings import Settings
from hanabira.model.files import Extensions
from hanabira.model.restrictions import Restrictions
from hanabira.model.boards import Boards
from hanabira.model.permissions import Permissions
from hanabira.model.sessions.beaker import BeakerSessionManager
from hanabira.model.sessions.bot import BotSession
from hanabira.model import meta
from hanabira.lib import wakabaparse
from hanabira.lib.searches import Searches
from hanabira.lib.newfiles import NewFiles
from hanabira.lib.filters import Filters
from hanabira.lib.filesystem import FileSystem
from hanabira.lib.captcha import Captchas
from hanabira.lib.fonts import FontsManager
from hanabira.lib.countries import country_codes

import logging
log = logging.getLogger(__name__)


class Globals(object):
    def __init__(self, config, paths):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = CacheManager(**parse_cache_config_options(config))
        self.paths = paths
        self.root  = self.paths.get('root')
        self.config = config

    def init_model(self, config, setup_mode):
        if setup_mode:
            meta.metadata.create_all(bind=meta.engine)
        appconf = config['app_conf']
        self.settings = Settings(config)
        self.fs = FileSystem(self.settings)
        self.boards = Boards(settings=self.settings, fs=self.fs)
        self.sections = self.boards.sections
        self.permissions = Permissions()
        self.captchas = Captchas(self)
        self.extensions = Extensions()
        self.restrictions = Restrictions()
        self.styles = [('Futaba', 'futaba.css'),('Photon', 'photon.css'), ('Snow', 'snow_static.css'), ('Snow[animated]', 'snow.css')]
                                    #('Spring', 'photon_green.css')]
        self.default_style = 'Futaba'
        self.parser = wakabaparse.WakabaParser(self)
        #self.searches = Searches(self.settings)
        self.newfiles = NewFiles(self.settings)
        self.filters  = Filters()
        self.fonts    = FontsManager(self.settings)
        self._404images = list(map(lambda x: "{0.path.static_web}{1}".format(self.settings, x), os.listdir(self.fs.local('images/404'))))
        self.country_codes = country_codes
        self.local_domains = list(map(lambda x: x.strip(), str(self.settings.chan.local_domains).split(',')))
        self.ignore_referers = list(map(lambda x: x.strip(), appconf.get('chan.ignore_referers', '').split(',')))
        self.ignore_queries = list(map(lambda x: x.strip(), appconf.get('chan.ignore_queries', '').split(',')))
        self.slave_nodes = list(map(lambda x: x.strip(), str(self.settings.cluster.slave_nodes).split(',')))
        self.sessions = BeakerSessionManager(config)
        self.bot_session = BotSession(self)
        
