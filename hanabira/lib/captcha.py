# -*- coding: utf-8 -*-
from hanabira.model import meta

import datetime
import string
import random
import io
import time
import os
from PIL import Image, ImageDraw, ImageFont

from pylons import app_globals as g, session

import logging
log = logging.getLogger(__name__)

class Captcha(object):
    captchas = None
    time     = None
    # Should be sync'ed with session properly
    language = None
    complexity = None
    def __init__(self, session):
        self.captchas = {}
        self.time = {}
        self.complexity = {}
        self.language = session['language']
        
    def set(self, lang=None, max_length=None):
        if lang:
            if self.language != lang:
                self.captchas = {}
                self.time = {}
            self.language = lang
        if max_length:
            self.max_length = max_length

    def new(self, board, complexity=None):
        if not complexity:
            complexity = g.settings.captcha.default_complexity
        complexity += session['enforced_captcha_complexity']
        self.captchas[board] = g.captchas.generate(language=self.language, complexity=complexity)
        self.time[board] = time.time()
        self.complexity[board] = complexity

    def get(self, board):
        # Temporary hack to sync to changes
        if type(self.captchas) != dict:
            self.captchas = {}
            self.language = 'ru'
        if type(self.complexity) != dict:
            self.complexity = {}
        if not board in self.captchas or time.time() - self.time[board] > 300000:
            self.new(board)
        return self.captchas[board]
    
    def get_complexity(self, board):
        if type(self.complexity) != dict:
            self.complexity = {}
        return self.complexity.get(board, 0)
    
    def check_complexity(self, board, complexity):
        if board.board in self.captchas:
            if self.complexity[board.board] >= complexity:
                return True
            else:
                self.new(board.board, complexity=complexity)
        else:
            self.new(board.board, complexity=complexity)
            return False
        
    def draw(self, board):
        width = 300
        height = 20
        img = Image.new("RGB", (width, height), '#FFFFFF')
        font = g.captchas.get_font(self.language)
        #log.info(font['path'])
        font = ImageFont.truetype(font['path'], size=14)
        draw = ImageDraw.Draw(img)
        
        text = self.get(board)
        #log.info("Captcha text: {}".format(text))
        complexity = self.get_complexity(board)
        if complexity >= 100:
            text = text.replace(' ', '')
        draw.text((5, 5), text, font=font, fill=127)
        """
        if complexity >= 100:
            #lt = 0
            #while lt < complexity:  
            #    lt += 100
            a = int(complexity/20) + random.randint(-2, 2)
            if a > 10:
                a = 10
            b = int(180 - complexity/2) + random.randint(-20, 20)
            if b < 40:
                b = 40
            b = b * random.choice([-1, 1])
            img.wave(a, b)
            a = complexity/25 + random.randint(-2, 5)
            if a > 25:
                a = 25.0
            a = a * random.choice([-1, 1])
            img.shear(a, 0.0)
            a = complexity/50 + random.randint(-1, 2)
            if a > 15:
                a = 15.0
            a = a * random.choice([-1, 1])
            img.swirl(a)
        """
        #if complexity >= 200:
        #    b = complexity/200 + random.randint(-1, 1)
        #    #img.gaussianBlur(1.0, 1.0)
        sio = io.BytesIO()
        img.save(sio, "PNG")
        imgraw = sio.getvalue()
        return imgraw

    def check(self, b, params, admin=None):
        board = b.board
        if admin and admin.has_permission('no_captcha', b.id):
            del self.captchas[board]
            return True
        req_captcha = str(params.get('captcha', '')).strip()
        if board in self.captchas:
            captcha = self.captchas[board]
            del self.captchas[board]
            req_captcha = "".join(req_captcha.lower().split()).\
                          replace('.', '').replace(',', '').replace(':', '').replace('-', '').replace(';', '').replace('—', '')
            captcha     = "".join(captcha.lower().split()).\
                          replace('.', '').replace(',', '').replace(':', '').replace('-', '').replace(';', '').replace('—', '')
            return req_captcha == captcha

class Captchas(object):
    default = None
    words   = None
    # Language-specific properties
    languages = {
        'ru': {'font': 'arial', 'complexity':1.0},
        'ja': {'font': 'vlgothic', 'complexity':0.5},
        'en': {'font': 'arial', 'complexity':1.0},
        }
    def __init__(self, g):
        settings = g.settings
        self.default = settings.chan.language
        self.words = {}
        for fn in [x for x in os.listdir(os.path.join(g.root, 'config')) if 'captcha' in x]:
            lang = fn.split('.')[1]
            fp = os.path.join(g.root, 'config', fn)
            self.words[lang] = list(filter(bool, [x.lower().strip() for x in open(fp, 'r+b').read().decode('utf-8').split("\n")]))
            log.info("%s words in %s captcha dict" % (len(self.words[lang]), lang))

    def get_font(self, language):
        if not language in self.words or not language in self.languages:
            language = self.default
        props = self.languages[language]
        return g.fonts.get(props['font'])

    def generate(self, language, complexity=20):
        if not language in self.words or not language in self.languages:
            language = self.default
        props = self.languages[language]
        captcha = []
        length  = 0
        max_length = complexity * props['complexity']
        if max_length > 40:
            max_length = 40
        min_length = max_length - 10
        while length < min_length:
            word = random.choice(self.words[language])
            length += len(word)
            if length > max_length: break
            captcha.append(word)
        return " ".join(captcha)
