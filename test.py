from enum import Enum
from random import random
import threading, logging
from time import sleep, time
from contextlib import contextmanager


REAL_LIFE_SECOND = 0.001


def wait(t: float):
   """This function theoretically waits for t seconds, practically it applies the factor REAL_LIFE_SECOND."""
   sleep(t * REAL_LIFE_SECOND)


class Action(Enum):
   IDLE = "Being idle"
   MINING_FOO = "Mining Foo"
   MINING_BAR = "Mining Bar"
   ASSEMBLING = "Assembling a Foo and a Bar for a Foobar"
   SELLING = "Selling Foobar"
   BUYING = "Buying a new Robot"
   CHANGING_ACTIVITY = "Changing Activity"


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
        logging.info(get_resources_string())
        self.status = action

    @contextmanager
    def activity(self, action: Action, waiting_time: float, message: str =""):
        """Creates a context manager to uniformize the different actions of the robots"""

        self.change_status(action)
        wait(waiting_time)
        Robot.lock.acquire()
        try:
            yield
        finally:
            Robot.lock.release()
            self.last_action = action
            if message:
                logging.info(f"Robot {self.id} " + message)
            self.change_status(Action.IDLE)

    def mine_foo(self):
        with self.activity(Action.MINING_FOO, waiting_time=1, message="MINED 1 FOO"):
            Robot.resources["foo"] += 1

    def mine_bar(self):
        with self.activity(Action.MINING_BAR, waiting_time=random() * 1.5 + 0.5, message="MINED 1 BAR"):
            Robot.resources["bar"] += 1

    def assemble(self):
        with self.activity(Action.ASSEMBLING, waiting_time=2):
            if random() < 0.6:      # Success case
                Robot.resources["foobar"] += 1
                message = f"ROBOT {self.id} SUCCESSFULLY ASSEMBLED 1 FOOBAR"
            else:
                Robot.resources["bar"] += 1
                message = f"ROBOT {self.id} FAILED TO ASSEMBLE 1 FOOBAR"
        logging.info(message)

    def sell(self, nb_foobar: int):
        with self.activity(Action.SELLING, waiting_time=10, message=f"SOLD {nb_foobar} FOOBAR"):
            Robot.resources["euros"] += nb_foobar
        
    def buy_robot(self):
        with self.activity(Action.BUYING, waiting_time=1, message="BOUGHT A ROBOT"):
            Robot()

    def change_activity(self):
        with self.activity(Action.CHANGING_ACTIVITY, waiting_time=5, message="CHANGED ACTIVITY"):
            pass


def get_resources_string():
    res=Robot.resources
    return f"foo : {res['foo']}   bar : {res['bar']}   foobar : {res['foobar']}   euros : {res['euros']}   Nb Robots : {len(Robot.robots)}."


def choose_task_to_do_if_idle(robot: Robot):
    while len(Robot.robots) <= 30:
        with Robot.lock:
            if Robot.resources["euros"] >= 3:
                if Robot.resources["foo"] >= 6:
                    Robot.resources["foo"] -= 6
                    Robot.resources["euros"] -= 3
                    action_to_perform, args = robot.buy_robot, ()
                else:
                    action_to_perform, args = robot.mine_foo, ()
            elif Robot.resources["foobar"] >= 1:
                nb_foobar = min(5, Robot.resources["foobar"])
                Robot.resources["foobar"] -= nb_foobar
                action_to_perform, args = robot.sell, (nb_foobar,)
            elif Robot.resources["foo"] >= 1 and Robot.resources["bar"] >= 1:
                Robot.resources["foo"] -= 1
                Robot.resources["bar"] -= 1
                action_to_perform, args = robot.assemble, ()
            elif Robot.resources["foo"] > Robot.resources["bar"]:
                action_to_perform, args = robot.mine_bar, ()
            else:
                action_to_perform, args = robot.mine_foo, ()
        action_to_perform(*args)
    


def main():
    start = time()
    Robot()
    Robot()
    for r in Robot.robots:
        r.join()
    total_time = (time() - start)/REAL_LIFE_SECOND
    print(f"{total_time = }")

if __name__=="__main__":
    format = "%(message)s"
    logging.basicConfig(format=format, level=logging.INFO)
    main()
    