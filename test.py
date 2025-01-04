from enum import Enum
from random import random
import threading, logging
from time import sleep, time

REAL_LIFE_SECOND = 0.001


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

    class activity:
        """Crée un context manager pour uniformiser les différentes actions des robots"""
        def __init__(self, robot, action: Action, waiting_time: float, message: str):
            self.__robot = robot
            self.__action = action
            self.__waiting_time = waiting_time
            self.__message = message

        def __enter__(self):
            self.__robot.change_status(self.__action)
            wait(self.__waiting_time)
            Robot.lock.acquire()

        def __exit__(self, a, b, c):
            Robot.lock.release()
            self.__robot.last_action = self.__action
            logging.info(self.__message)
            self.__robot.change_status(Action.IDLE)

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

    def mine_foo(self):
        with Robot.activity(self, Action.MINING_FOO, 1, f"Robot {self.id} MINED 1 FOO"):
            Robot.resources["foo"] += 1

    def mine_bar(self):
        with Robot.activity(self, Action.MINING_BAR, random() * 1.5 + 0.5, f"Robot {self.id} MINED 1 BAR"):
            Robot.resources["bar"] += 1

    def assemble(self):
        with Robot.activity(self, Action.ASSEMBLING, 2, f"Robot {self.id} TRIED TO ASSEMBLE 1 FOOBAR"):
            if random() < 0.6: # Success case
                Robot.resources["foobar"] += 1
                message = f"ROBOT {self.id} ASSEMBLING SUCCESS"
            else:
                Robot.resources["bar"] += 1
                message = f"ROBOT {self.id} ASSEMBLING FAILURE"
        logging.info(message)

    def sell(self, nb_foobar: int):
        with Robot.activity(self, Action.SELLING, 10, f"ROBOT {self.id} SOLD {nb_foobar} FOOBAR"):
            Robot.resources["euros"] += nb_foobar
        
    def buy_robot(self):
        with Robot.activity(self, Action.BUYING, 1, f"ROBOT {self.id} BOUGHT A ROBOT"):
            Robot()

    def change_activity(self):
        with Robot.activity(self, Action.CHANGING_ACTIVITY, 5, f"ROBOT {self.id} CHANGED ACTIVITY"):
            pass

def get_resources_str():
    return f"foo : {Robot.resources["foo"]}   bar : {Robot.resources["bar"]}   foobar : {Robot.resources["foobar"]}   euros : {Robot.resources["euros"]}   Nb Robots : {len(Robot.robots)}."


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