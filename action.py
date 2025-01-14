from enum import Enum

class Action(Enum):
   IDLE = "Being idle"
   MINE_FOO = "Mining Foo"
   MINE_BAR = "Mining Bar"
   ASSEMBLE = "Assembling a Foo and a Bar for a Foobar"
   SELL_FOOBAR = "Selling Foobar"
   BUY_ROBOT = "Buying a new Robot"
   CHANGE_ACTIVITY = "Changing Activity"
   