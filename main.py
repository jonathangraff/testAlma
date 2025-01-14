from time import time
import logging

from robot import Robot
from const import REAL_LIFE_SECOND


def main():
    start = time()
    Robot()
    Robot()
    for r in Robot.robots:
        r.join()
    total_time = (time() - start) / REAL_LIFE_SECOND
    print(f"{total_time = }")

if __name__=="__main__":
    format = "%(message)s"
    logging.basicConfig(format=format, level=logging.INFO)
    main()
    