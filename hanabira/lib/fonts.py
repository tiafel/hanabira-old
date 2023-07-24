# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)


class FontsManager(object):
    settings = None
    # Just use fixed paths according Gentoo layout for now
    fonts = {
        # "alias": {name: displayed name, 'path':Path or X11 alias, width: relative width, mono: is mono?, subsets: unicode subsets it can render}
        # "":{'name':'', 'path':'', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "arial":{'name':'Arial', 'path':'arial', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "impact": {'name':'Impact', 'path':'impact', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "vlgothic": {'name':'VL Gothic', 'path':'@/usr/share/fonts/vlgothic/VL-PGothic-Regular.ttf', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "palatino": {'name':'URW Palladio L', 'path':'@/usr/share/fonts/default/ghostscript/p052003l.pfb', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "vera":{'name':'Bitstream Vera Sans', 'path':'@/usr/share/fonts/ttf-bitstream-vera/Vera.ttf', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        # Causes segfault
        #"helvetica":{'name':'Helvetica', 'path':'@/usr/share/fonts/100dpi/helvR12.pcf.gz', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "verdana":{'name':'Verdana', 'path':'@/usr/share/fonts/corefonts/verdana.ttf', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        # Causes segfault
        #"times":{'name':'Times', 'path':'@/usr/share/fonts/100dpi/timR12.pcf.gz', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "times new roman":{'name':'Times New Roman', 'path':'@/usr/share/fonts/corefonts/times.ttf', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        "freeserif":{'name':'FreeSerif', 'path':'@/usr/share/fonts/freefont-ttf/FreeSerif.ttf', 'width':0.5, 'mono':False, 'subsets':[], 'style':'normal'},
        }
    aliases = {
        "sans":"vera",
        'palladio':'palatino',
        }
    default = "vera"
    def __init__(self, settings):
        self.settings = settings
        self.load()

    def load(self):
        pass

    def get(self, fontname):
        fontname = fontname.lower().strip()
        if fontname in self.aliases:
            fontname = self.aliases[fontname]
        if not fontname in self.fonts:
            fontname = self.default
        return self.fonts[fontname]
    def get_path(self, fontname):
        font = self.get(fontname)
        return font['path']
