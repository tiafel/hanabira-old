# -*- coding: utf-8 -*-

class UserAgent(object):
    is_bot        = False
    is_library    = False
    is_search     = False
    is_downloader = False
    is_mobile     = False

    def __repr__(self):
        return "<({0.__class__.__name__}, is_bot={0.is_bot}, is_mobile={0.is_mobile})>".format(self)

class EmptyUA(UserAgent):
    def __init__(self, ua=None):
        pass    

class Opera(UserAgent):
    def __init__(self, ua=None):
        pass

class Mobile(UserAgent):
    is_mobile = True

class Android(Mobile):
    """
    Mozilla/5.0 (Linux; U; Android 2.2.1
    """

class iOS(Mobile):
    """
    like Mac OS X
    """

class iPhone(iOS):
    """
    Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_1_2 like Mac OS X;
    """

class iPad(iOS):
    """
    Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5
    """

class OperaMobile(Mobile):
    """
    Opera/9.51 Beta (Microsoft Windows; PPC; Opera Mobi/1718; U; en)
    """

class Symbian(Mobile):
    """
    Mozilla/5.0 (SymbianOS/9.4; U; Series60/5.0 Nokia5235/12.6.092; Profile/MIDP-2.1 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413"
    """

class Bot(UserAgent):
    is_bot = True
    def __init__(self, signatures=None,
                 is_library=False, is_search=False, is_downloader=False):
        if signatures and not isinstance(signatures, list):
            signatures = [signatures]
        self.signatures = signatures
        self.is_library = is_library
        self.is_search  = is_search
        self.is_downloader = is_downloader

bots = [
    Bot('GoogleBot', is_search=True),
    Bot('Googlebot', is_search=True),
    Bot('YandexBot', is_search=True),
    Bot('yandex.com/bots', is_search=True),
    Bot('Wget', is_downloader=True),
    Bot('AppEngine-Google'),
    
    Bot('Java/1', is_library=True),
    Bot('pear.php.net', is_library=True),
    Bot('PHP/5', is_library=True),
    Bot('PycURL', is_library=True),
    Bot('Python-urllib', is_library=True),
    Bot('WordPress/', is_library=True),
    Bot('libwww-perl', is_library=True),
    Bot('htmlSQL', is_library=True),
    Bot('libcurl', is_library=True),

    Bot('httperf'),
    ]

signatures = {}
for bot in bots:
    if bot.signatures:
        for s in bot.signatures:
            signatures[s] = bot

def parse_useragent(ua):
    ## Use fast indexes to search through signatures
    if hasattr(ua, 'user_agent'):
        ua = ua.user_agent
    if not ua:
        return EmptyUA(ua)    
    if ua.startswith('Opera'):
        return Opera(ua=ua)
    for s in signatures:
        if s in ua:
            return signatures[s]
    return UserAgent()
