import sys, os
hanabira_root = os.path.dirname(os.path.abspath(__file__))
hanabira_extlibs = os.path.join(hanabira_root, "extlibs")
sys.path.insert(0, hanabira_root)
sys.path.insert(0, hanabira_extlibs)
sys.path.append(hanabira_root)
sys.path.append(hanabira_extlibs)

from paste.deploy import loadapp, loadserver
from logging.config import fileConfig
from six.moves import configparser

class HanabiraPasterServe(object):
    def __init__(self):
        app_spec = sys.argv[1]
        app_name = 'main'
        app_spec = 'config:' + app_spec
        server_name = 'main'
        server_spec = app_spec
        base = os.getcwd()
        
        log_fn = sys.argv[1]
        log_fn = os.path.join(base, log_fn)
        self.logging_file_config(log_fn)
            
        server = loadserver(server_spec, name=server_name, relative_to=base)
        print("Server: {}".format(server))
        app = loadapp(app_spec, name=app_name, relative_to=base)
        print("App: {}".format(app))
        
        def serve():
            try:
                server(app)
            except (SystemExit, KeyboardInterrupt) as e:
                if self.verbose > 1:
                    raise
                if str(e):
                    msg = ' '+str(e)
                else:
                    msg = ''
                print('Exiting%s (-v to see traceback)' % msg)

        serve()
        
    def logging_file_config(self, config_file):
        parser = configparser.ConfigParser()
        parser.read([config_file])
        if parser.has_section('loggers'):
            config_file = os.path.abspath(config_file)
            fileConfig(config_file, dict(__file__=config_file,
                                         here=os.path.dirname(config_file)))    
        
        
s = HanabiraPasterServe()