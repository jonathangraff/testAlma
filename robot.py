from random import random
import threading, logging
from contextlib import contextmanager
from time import sleep

from const import Action, Rss, REAL_LIFE_SECOND, MAX_ROBOTS


def wait(t: float):
   """This function theoretically waits for t seconds, practically it applies the factor REAL_LIFE_SECOND."""
   sleep(t * REAL_LIFE_SECOND)


class Robot(threading.Thread):
    
    resources = {rss: 0 for rss in Rss}
    lock = threading.Lock()
    robots = []

    def __init__(self):
        logging.info("Initialization of a new robot")
        super().__init__(target=self.choose_task_to_do_when_idle, args=())
        self.id: int = len(Robot.robots)
        self.status = Action.IDLE
        self.last_action = Action.IDLE
        Robot.robots.append(self)
        self.start()

    def _change_status(self, action: Action):
        logging.info(f"Robot {self.id} : {action.value}")
        # displays the current resources and number of robots :
        logging.info(f"{'   '.join([f'{rss.value} : {Robot.resources[rss]}' for rss in Rss])}   Nb Robots : {len(Robot.robots)}.")
        self.status = action

    @contextmanager
    def _activity(self, action: Action, nb_foobar=0):
        """Creates a context manager to regroup all stuff to do before and after an action"""

        self._change_status(action)
        wait(self.get_waiting_time_from_action(action))
        Robot.lock.acquire()

        yield
        
        Robot.lock.release()
        self.last_action = Action.ASSEMBLE if action in {Action.ASSEMBLE_SUCCESS, Action.ASSEMBLE_FAIL} else action
        message = self.get_parameters_from_action(action, "message", nb_foobar)
        if message:
            logging.info(f"Robot {self.id} " + message)
        self._change_status(Action.IDLE)

    def mine_foo(self):
        with self._activity(Action.MINE_FOO):
            Robot.resources[Rss.FOO] += 1

    def mine_bar(self):
        with self._activity(Action.MINE_BAR):
            Robot.resources[Rss.BAR] += 1

    def assemble(self):
        if random() < 0.6:      # Success case
            with self._activity(Action.ASSEMBLE_SUCCESS):
                Robot.resources[Rss.FOOBAR] += 1
        else:
            with self._activity(Action.ASSEMBLE_FAIL):
                Robot.resources[Rss.BAR] += 1

    def sell_foobar(self, nb_foobar: int):
        with self._activity(Action.SELL_FOOBAR, nb_foobar):
            Robot.resources[Rss.EUROS] += nb_foobar
        
    def buy_robot(self):
        with self._activity(Action.BUY_ROBOT):
            Robot()

    def change_activity(self):
        with self._activity(Action.CHANGE_ACTIVITY):
            pass
    
    def get_parameters_from_action(self, action: Action, parameter: str, nb_foobar=0):
        if parameter in {"function", "time", "price", "message"}:
            actions_dictionary = {
                Action.MINE_FOO: {"function": self.mine_foo, "time": 1, "price": (), "message": "MINED 1 FOO"},
                Action.MINE_BAR: {"function": self.mine_bar, "time": [0.5, 2], "price": (), "message": "MINED 1 BAR"},
                Action.ASSEMBLE: {"function": self.assemble, "price": ((Rss.FOO, 1), (Rss.BAR, 1))},
                Action.ASSEMBLE_SUCCESS: {"time": 2, "message": "ASSEMBLED 1 FOOBAR SUCCESSFULLY"},
                Action.ASSEMBLE_FAIL: {"time": 2, "message": "FAILED TO ASSEMBLE 1 FOOBAR"},
                Action.SELL_FOOBAR: {"function": self.sell_foobar, "time": 10, "price": ((Rss.FOOBAR, [5]),), "message": f"SOLD {nb_foobar} FOOBAR"},
                Action.BUY_ROBOT: {"function": self.buy_robot, "time": 1, "price": ((Rss.FOO, 6), (Rss.EUROS, 3)), "message": "BOUGHT A ROBOT"},
                Action.CHANGE_ACTIVITY: {"function": self.change_activity, "time": 5, "price": (), "message": "CHANGED ACTIVITY"},
            }
            return actions_dictionary[action][parameter]
        raise Exception(f"Parameter {parameter} not taken in account")  
            
    def get_waiting_time_from_action(self, action: Action):
        """returns the waiting time from the action. If the time is an interval, returns a random number in this interval """
        time = self.get_parameters_from_action(action, "time")
        if isinstance(time, int):
            return time
        return time[0] + random() * (time[1] - time[0])
    
    def pay_resources(self, action: Action) -> list[int | None]:
        """ Pays the necessary resources before performing an action and returns the resources used in case
            it is necessary to know them for earning resources (exemple : selling foobar). 
            Returns an empty list if not necessary.
        """
        price = self.get_parameters_from_action(action, "price")
        args = []
        for item in price:
            rss = item[0]        
            if isinstance(item[1], int):
                Robot.resources[rss] -= item[1]
            else:
                cost = min(item[1][0], Robot.resources[rss])
                Robot.resources[rss] -= cost
                args.append(cost)
        return args

    def choose_task_to_do_when_idle(self):
        while len(Robot.robots) <= MAX_ROBOTS:
            with Robot.lock:
                if self.do_the_same_action():
                    action = self.last_action
                elif self.last_action in {Action.CHANGE_ACTIVITY, Action.IDLE}:
                    action = self.choose_new_action()
                else:
                    action = Action.CHANGE_ACTIVITY
                args = self.pay_resources(action)
            
            self.get_parameters_from_action(action, "function")(*args)
    
    def do_the_same_action(self) -> bool:
        """decides if the robot performs the same action than before or not"""
        match self.last_action:
            case Action.IDLE | Action.CHANGE_ACTIVITY:
                return False
            case Action.MINE_FOO:
                return Robot.resources[Rss.FOO] <= 10
            case Action.MINE_BAR:
                return Robot.resources[Rss.BAR] <= 10
            case Action.ASSEMBLE:
                return Robot.resources[Rss.FOO] >= 1 and Robot.resources[Rss.BAR] >= 1
            case Action.SELL_FOOBAR:
                return Robot.resources[Rss.FOOBAR] >= 1
            case Action.BUY_ROBOT:
                return Robot.resources[Rss.EUROS] >= 3 and Robot.resources[Rss.FOO] >= 6
            case _:
                raise Exception(f"Action {self.last_action} not taken in account")

    def choose_new_action(self):
        """chooses a new action to do after the robot has finished his "Changing activity" task"""
        if Robot.resources[Rss.EUROS] >= 3:
            if Robot.resources[Rss.FOO] >= 6:
                return Action.BUY_ROBOT
            return Action.MINE_FOO
        if Robot.resources[Rss.FOOBAR] >= 1:
            return Action.SELL_FOOBAR
        if Robot.resources[Rss.FOO] >= 1 and Robot.resources[Rss.BAR] >= 1:
            return Action.ASSEMBLE
        if Robot.resources[Rss.FOO] > Robot.resources[Rss.BAR]:
            return Action.MINE_BAR
        return Action.MINE_FOO
    