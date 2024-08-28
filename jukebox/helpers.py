import time
from codrone_edu.drone import *


def draw_lines(drone: Drone, inp_str: str, x, y_start):
    l_space = 8  # space between lines (px)
    lines = inp_str.split("\n")  # create an array of lines
    y = y_start
    for line in lines:
        drone.controller_draw_string(x, y, line)
        time.sleep(0.05)  # lines tend to get skipped (not displayed) if there is no delay between drawing lines
        y += l_space  # next y value