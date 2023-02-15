class Board:
    def __init__(self):
        pass
class OceanBoard(Board):
    def __init__(self):
        super().__init__()
    def placeShip(self,ship,r,c,orientation):
        pass
    def allShipSunk():
        pass
class TargetBoard(Board):
    def __init__(self):
        super().__init__()
    def markHit(self,r,c):
        pass
    def markMiss(self,r,c):
        pass
    def isHit(self,r,c):
        pass
    def isEmpty(self,r,c):
        pass
class Letter:
    def __init__(self):
        pass

class Ship:
    def __init__(self):
        pass

class Display:
    def __init__(self):
        pass

class Setting:
    def __init__(self):
        pass

class BattleshipPlayer:
    def __init__(self,name,r,c):
        pass
    def placeShip(self,ship,loc,orientation):
        pass
    def shipAt(self,r,c):
        pass
    def shotAt(self,r,c):
        pass  
    def markTargetHit(self,r,c):
        pass