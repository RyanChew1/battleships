#===========================================================================
# Description: Settings for a game
#
# State Attributes
#    settings - Dictionary - the various parameter settings for a game
#
# Methods
#    setSetting(name, initValue) - creates or modifies a setting of the given name and value
#    getValue(name) - returns the value of the 'name' 
#    settingIs(name, value) - returns True if setting of given name is the value
#                             if setting doesn't exist, it returns False
#===========================================================================
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