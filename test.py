from enum import Enum
from random import random
import asyncio, time


REAL_LIFE_SECOND = 0.001


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
   await asyncio.sleep(t * REAL_LIFE_SECOND)


class Robot:
    robots = []
    foo = bar = foobar = euros = 0

    def __init__(self):
        self.id: int = len(Robot.robots)
        self.status: Status = Status.IDLE
        self.last_action: Status = Status.IDLE
        Robot.robots.append(self)

    async def mine(self, mineral: Mineral):
        print_resources()
        if mineral == Mineral.FOO:
            self.status = Status.MINING_FOO
            await wait(1)
            Robot.foo += 1
            self.last_action: Status = Status.MINING_FOO
        elif mineral == Mineral.BAR:
            self.status = Status.MINING_BAR
            await wait(random() * 1.5 + 0.5) # entre 0.5 et 2 sec
            Robot.bar += 1
            self.last_action: Status = Status.MINING_BAR
        else:
            raise Exception("Mineral not taken in account")
        self.print_status_and_resources()
        self.status = Status.IDLE

    async def assemble(self):
        print(f"ASSEMBLING")
        print_resources()
        self.status == Status.ASSEMBLING
        await wait(2)
        if random() < 0.6: # Success case
            Robot.foo -= 1
            Robot.bar -= 1
            Robot.foobar += 1
            print(f"ASSEMBLING SUCCESS {Robot.foobar = }")
        else:
            Robot.foo -= 1
            print(f"ASSEMBLING FAILURE {Robot.foobar = }")
        self.print_status_and_resources()
        self.last_action: Status = Status.ASSEMBLING
        self.status = Status.IDLE

    async def sell(self):
        print_resources()
        nb_foobar = min(5, Robot.foobar)
        self.status = Status.SELLING
        await wait(10)
        Robot.foobar -= nb_foobar
        Robot.euros += nb_foobar
        self.last_action: Status = Status.SELLING
        self.status = Status.IDLE
        print(f"SOLD {nb_foobar} FOOBAR")
        self.print_status_and_resources()

    async def buy_robot(self):
        print_resources()
        self.status = Status.BUYING
        await wait(1)
        Robot()
        Robot.euros -= 3
        Robot.foo -= 6
        self.last_action: Status = Status.BUYING
        self.status = Status.IDLE
        self.print_status_and_resources()

    async def change_activity(self):
        self.status = Status.CHANGING_ACTIVITY
        await wait(5)
        self.last_action: Status = Status.CHANGING_ACTIVITY
        self.status = Status.IDLE
       
    def print_status_and_resources(self):
        print(f"{self.status.value}")
        print_resources()
       

def get_idle_robots():
    return [robot for robot in Robot.robots if robot.status == Status.IDLE]


def print_resources():
    print(f"{Robot.foo=} {Robot.bar=} {Robot.foobar=} {Robot.euros=}.")


def choose_task_to_do(robot: Robot):
    if Robot.euros >= 3:
        if Robot.foo >= 6:
            return robot.buy_robot()
        else:
            return robot.mine(Mineral.FOO)
    if Robot.foobar >= 1:
        return robot.sell()
    if Robot.foo >= 1 and Robot.bar >= 1:
        return robot.assemble()
    if Robot.foo > Robot.bar:
        return robot.mine(Mineral.BAR)
    return robot.mine(Mineral.FOO)


async def main():
    started_at = time.monotonic()
    Robot()
    Robot()
    while len(Robot.robots) < 10:
        idle_robots: list[Robot] = get_idle_robots()
        print("*"*100, len(idle_robots))
        # tasks = []
        for robot in idle_robots:
            task = asyncio.create_task(choose_task_to_do(robot))
            # tasks.append(task)
            await task

    total_time = (time.monotonic() - started_at)/REAL_LIFE_SECOND
    print(f"{total_time = }")

asyncio.run(main())