import yaml

cfg = False
configfile = ""


class Get(object):
    cfg = False

    def __init__(self, config="config.yml"):
        global cfg
        self.configfile = config
        self.load()
        cfg = self.cfg

    def load(self):
        with open(self.configfile, 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)
