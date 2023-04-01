
class Setting:

    def __init__(self):
        '''
        Constructor
        '''
        self.settings = {}

    def setSetting(self, name, initValue):
        self.settings[name] = initValue

    def getValue(self, name):
        if name in self.settings: 
            return self.settings[name]
        else:
            return None

    def settingIs(self, name, value):
        if name in self.settings:
            return self.settings[name] == value
        else:
            return False
