from enum import Enum
from random import random
import threading, logging
from time import sleep, time

REAL_LIFE_SECOND = 0.001


class Mineral(Enum):
   FOO = "Foo"
   BAR = "Bar"


class Action(Enum):
   IDLE = "Idle"
   MINING_FOO = "Mining Foo"
   MINING_BAR = "Mining Bar"
   ASSEMBLING = "Assembling a Foo and a Bar for a Foobar"
   SELLING = "Selling Foobar"
   BUYING = "Buying a new Robot"
   CHANGING_ACTIVITY = "Changing Activity"


def wait(t: float):
   """This function waits for t seconds, applying the factor REAL_LIFE_SECOND."""
   sleep(t * REAL_LIFE_SECOND)




class Robot(threading.Thread):
    
    resources = {
        "foo": 0,
        "bar": 0,
        "foobar": 0,
        "euros": 0,
    }
    lock = threading.Lock()
    robots = []

    def __init__(self):
        logging.info("Initialization of new robot")
        super().__init__(target=choose_task_to_do_if_idle, args=(self,))
        self.id: int = len(Robot.robots)
        self.status: Action = Action.IDLE
        self.last_action: Action = Action.IDLE
        Robot.robots.append(self)
        self.start()

    def change_status(self, action: Action):
        logging.info(f"Robot {self.id} : {action.value}")
        logging.info(get_resources_str())
        self.status = action

    def mine(self, mineral: Mineral):
        match mineral:
            case Mineral.FOO:
                self.change_status(Action.MINING_FOO)
                wait(1)
                with Robot.lock:
                    Robot.resources["foo"] += 1
                self.last_action = Action.MINING_FOO
            case Mineral.BAR:
                self.change_status(Action.MINING_BAR)
                wait(random() * 1.5 + 0.5) # entre 0.5 et 2 sec
                with Robot.lock:
                    Robot.resources["bar"] += 1
                self.last_action = Action.MINING_BAR
            case _:
                raise Exception("Mineral not taken in account")
        self.change_status(Action.IDLE)

    def assemble(self):
        self.change_status(Action.ASSEMBLING)
        with Robot.lock:
            if Robot.resources["foo"] < 1 or Robot.resources["bar"] < 1:
                return
            Robot.resources["foo"] -= 1
            Robot.resources["bar"] -= 1
        wait(2)
        if random() < 0.6: # Success case
            with Robot.lock:
                Robot.resources["foobar"] += 1
            logging.info(f"ROBOT {self.id} ASSEMBLING SUCCESS")
        else:
            with Robot.lock:
                Robot.resources["bar"] += 1
            logging.info(f"ROBOT {self.id} ASSEMBLING FAILURE")
        self.last_action: Action = Action.ASSEMBLING
        self.change_status(Action.IDLE)

    def sell(self):
        nb_foobar = min(5, Robot.resources["foobar"])
        self.change_status(Action.SELLING)
        with Robot.lock:
            if Robot.resources["foobar"] < nb_foobar:
                return
            Robot.resources["foobar"] -= nb_foobar
        wait(10)
        with Robot.lock:
            Robot.resources["euros"] += nb_foobar
        self.last_action = Action.SELLING
        logging.info(f"ROBOT {self.id} SOLD {nb_foobar} FOOBAR")
        self.change_status(Action.IDLE)

    def buy_robot(self):
        self.change_status(Action.BUYING)
        with Robot.lock:
            if Robot.resources["foo"] < 6 or Robot.resources["euros"] < 3:
                return
            Robot.resources["euros"] -= 3
            Robot.resources["foo"] -= 6
        wait(1)
        Robot()
        logging.info(f"ROBOT {self.id} BOUGHT A ROBOT")
        self.last_action = Action.BUYING
        self.change_status(Action.IDLE)

    def change_activity(self):
        self.change_status(Action.CHANGING_ACTIVITY)
        wait(5)
        self.last_action: Action = Action.CHANGING_ACTIVITY
        self.change_status(Action.IDLE)


def get_resources_str():
    return f"{Robot.resources["foo"]=} {Robot.resources["bar"]=} {Robot.resources["foobar"]=} {Robot.resources["euros"]=} Nb Robots : {len(Robot.robots)}."


def choose_task_to_do_if_idle(robot: Robot):
    while len(Robot.robots) <= 30:
        with Robot.lock:
            foo = Robot.resources["foo"]
            bar = Robot.resources["bar"]
            euros = Robot.resources["euros"]
            foobar = Robot.resources["foobar"]
        if euros >= 3:
            if foo >= 6:
                robot.buy_robot()
            else:
                robot.mine(Mineral.FOO)
            continue
        if foobar >= 1:
            robot.sell()
            continue
        if foo >= 1 and bar >= 1:
            robot.assemble()
            continue
        if foo > bar:
            robot.mine(Mineral.BAR)
            continue
        robot.mine(Mineral.FOO)
    


def main():
    started_at = time()
    Robot()
    Robot()
    for r in Robot.robots:
        r.join()
    total_time = (time() - started_at)/REAL_LIFE_SECOND
    print(f"{total_time = }")

if __name__=="__main__":
    format = "%(message)s"
    logging.basicConfig(format=format, level=logging.INFO)
    main()