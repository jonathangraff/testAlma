from enum import Enum
from random import Random
import asyncio


REAL_LIFE_SECOND = 0.01


class Mineral(Enum):
   FOO = "Foo"
   BAR = "Bar"


class Status(Enum):
   IDLE = "Idle"
   MINING_FOO = "Mining Foo"
   MINING_BAR = "Mining Bar"
   ASSEMBLING = "Assembling a Foo and a Bar"
   SELLING = "Selling Foobar"
   BUYING = "Buying a new Robot"
   CHANGING_ACTIVITY = "Changing Activity"


async def wait(t: float):
   """This function waits for t seconds, applying the factor REAL_LIFE_SECOND."""
   asyncio.sleep(t * REAL_LIFE_SECOND)


class Robot:
   robots = []
   foo = bar = foobar = euros = 0

   def __init__(self):
       self.id: int = len(Robot.robots)
       self.status: Status = Status.IDLE
       self.last_action: Status = Status.IDLE
       Robot.robots.append(self)

   async def mine(self, mineral: Mineral):
       if mineral == Mineral.FOO:
           self.status = Status.MINING_FOO
           await wait(1)
           Robot.foo += 1
           self.last_action: Status = Status.MINING_FOO
       elif mineral == Mineral.BAR:
           self.status = Status.MINING_BAR
           await wait(Random.random() * 1.5 + 0.5)
           Robot.bar += 1
           self.last_action: Status = Status.MINING_BAR
       else:
           raise Exception("Mineral not taken in account")
       self.status = Status.IDLE

   async def assemble(self):
       self.status == Status.ASSEMBLING
       await wait(2)
       if Random.random() < 0.6: # Success case
           Robot.foo -= 1
           Robot.bar -= 1
           Robot.foobar += 1
       else:
           Robot.foo -= 1
       self.last_action: Status = Status.ASSEMBLING
       self.status = Status.IDLE

   async def sell(self, nb_foobar):
       self.status = Status.SELLING
       await wait(10)
       Robot.foobar -= nb_foobar
       Robot.euros += nb_foobar
       self.last_action: Status = Status.SELLING
       self.status = Status.IDLE

   async def buy_robot(self):
       self.status = Status.BUYING
       await wait(1)
       Robot()
       Robot.euros -= 3
       Robot.foo -= 6
       self.last_action: Status = Status.BUYING

   async def change_activity(self):
       self.status = Status.CHANGING_ACTIVITY
       await wait(5)
       self.last_action: Status = Status.CHANGING_ACTIVITY
       self.status = Status.IDLE
       
