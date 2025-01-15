from enum import Enum

class Action(Enum):
    IDLE = "Being idle"
    MINE_FOO = "Mining Foo"
    MINE_BAR = "Mining Bar"
    ASSEMBLE = "Trying to assemble a Foo and a Bar for a Foobar"
    ASSEMBLE_SUCCESS = "Managing to assemble"
    ASSEMBLE_FAIL = "Failing to assemble"
    SELL_FOOBAR = "Selling Foobar"
    BUY_ROBOT = "Buying a new Robot"
    CHANGE_ACTIVITY = "Changing Activity"
    


class Rss(Enum):
    FOO ="foo"
    BAR = "bar"
    FOOBAR = "foobar"
    EUROS = "euros"

REAL_LIFE_SECOND = 0.001
MAX_ROBOTS = 30