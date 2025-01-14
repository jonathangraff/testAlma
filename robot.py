from random import random
import threading, logging
from contextlib import contextmanager
from time import sleep

from action import Action
from const import REAL_LIFE_SECOND, MAX_ROBOTS


def wait(t: float):
   """This function theoretically waits for t seconds, practically it applies the factor REAL_LIFE_SECOND."""
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

    def get_resources_string():
        res = Robot.resources
        return f"foo : {res['foo']}   bar : {res['bar']}   foobar : {res['foobar']}   euros : {res['euros']}   Nb Robots : {len(Robot.robots)}."

    def __init__(self):
        logging.info("Initialization of a new robot")
        super().__init__(target=self.choose_task_to_do_when_idle, args=())
        self.id: int = len(Robot.robots)
        self.status = Action.IDLE
        self.last_action = Action.IDLE
        Robot.robots.append(self)
        self.start()

    def change_status(self, action: Action):
        logging.info(f"Robot {self.id} : {action.value}")
        logging.info(Robot.get_resources_string())
        self.status = action

    @contextmanager
    def activity(self, action: Action, waiting_time: float, message: str =""):
        """Creates a context manager to uniformize the different actions of the robots"""

        self.change_status(action)
        wait(waiting_time)
        Robot.lock.acquire()
        yield
        Robot.lock.release()
        self.last_action = action
        if message:
            logging.info(f"Robot {self.id} " + message)
        self.change_status(Action.IDLE)

    def mine_foo(self):
        with self.activity(Action.MINE_FOO, waiting_time=1, message="MINED 1 FOO"):
            Robot.resources["foo"] += 1

    def mine_bar(self):
        with self.activity(Action.MINE_BAR, waiting_time=random() * 1.5 + 0.5, message="MINED 1 BAR"):
            Robot.resources["bar"] += 1

    def assemble(self):
        with self.activity(Action.ASSEMBLE, waiting_time=2):
            if random() < 0.6:      # Success case
                Robot.resources["foobar"] += 1
                message = f"ROBOT {self.id} SUCCESSFULLY ASSEMBLED 1 FOOBAR"
            else:
                Robot.resources["bar"] += 1
                message = f"ROBOT {self.id} FAILED TO ASSEMBLE 1 FOOBAR"
        logging.info(message)

    def sell(self, nb_foobar: int):
        with self.activity(Action.SELL_FOOBAR, waiting_time=10, message=f"SOLD {nb_foobar} FOOBAR"):
            Robot.resources["euros"] += nb_foobar
        
    def buy_robot(self):
        with self.activity(Action.BUY_ROBOT, waiting_time=1, message="BOUGHT A ROBOT"):
            Robot()

    def change_activity(self):
        with self.activity(Action.CHANGE_ACTIVITY, waiting_time=5, message="CHANGED ACTIVITY"):
            pass

    def get_function_from_action(self, action: Action):
        """matches an action with the function asssociated"""
        match action:
            case Action.MINE_FOO: 
                return self.mine_foo
            case Action.MINE_BAR: 
                return self.mine_bar
            case Action.ASSEMBLE: 
                return self.assemble
            case Action.SELL_FOOBAR:
                return self.sell
            case Action.BUY_ROBOT:
                return self.buy_robot
            case Action.CHANGE_ACTIVITY:
                return self.change_activity
            case _:
                raise Exception(f"Action {action} not taken in account")
    
    def pay_ressources(action: Action) -> tuple[int | None]:
        """ Pays the necessary resources before performing an action and returns the resources used in case
            it is necessary to have them for earning resources (exemple : selling foobar). 
            Returns an empty tuple if not necessary.
        """
        match action:
            case Action.ASSEMBLE: 
                Robot.resources["foo"] -= 1
                Robot.resources["bar"] -= 1
            case Action.SELL_FOOBAR:
                nb_foobar = min(5, Robot.resources["foobar"])
                Robot.resources["foobar"] -= nb_foobar
                return (nb_foobar,)
            case Action.BUY_ROBOT:
                Robot.resources["foo"] -= 6
                Robot.resources["euros"] -= 3
            case Action.MINE_FOO | Action.MINE_BAR | Action.IDLE | Action.CHANGE_ACTIVITY:
                pass
            case _:
                raise Exception(f"Action {action.value} not taken in account")
        return ()


    def choose_task_to_do_when_idle(self):
        while len(Robot.robots) <= MAX_ROBOTS:
            with Robot.lock:
                if self.do_the_same_action():
                    action_to_perform = self.last_action
                elif self.last_action in {Action.CHANGE_ACTIVITY, Action.IDLE}:
                    action_to_perform = self.choose_new_action()
                else:
                    action_to_perform = Action.CHANGE_ACTIVITY
                args = Robot.pay_ressources(action_to_perform)
            self.get_function_from_action(action_to_perform)(*args)

    def do_the_same_action(self) -> bool:
        """decides if the robot performs the same action than before or not"""
        match self.last_action:
            case Action.IDLE | Action.CHANGE_ACTIVITY:
                return False
            case Action.MINE_FOO:
                return Robot.resources["foo"] >= 10
            case Action.MINE_BAR:
                return Robot.resources["bar"] >= 10
            case Action.ASSEMBLE:
                return Robot.resources["foo"] >= 1 and Robot.resources["bar"] >= 1
            case Action.SELL_FOOBAR:
                return Robot.resources["foobar"] >= 1
            case Action.BUY_ROBOT:
                return Robot.resources["euros"] >= 3 and Robot.resources["foo"] >= 6
            case _:
                raise Exception(f"Action {self.last_action} not taken in account")

    def choose_new_action(self):
        if Robot.resources["euros"] >= 3:
            if Robot.resources["foo"] >= 6:
                return Action.BUY_ROBOT
            return Action.MINE_FOO
        if Robot.resources["foobar"] >= 1:
            return Action.SELL_FOOBAR
        if Robot.resources["foo"] >= 1 and Robot.resources["bar"] >= 1:
            return Action.ASSEMBLE
        if Robot.resources["foo"] > Robot.resources["bar"]:
            return Action.MINE_BAR
        return Action.MINE_FOO