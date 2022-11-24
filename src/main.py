import curses
from curses import wrapper
from snake import Board
from time import sleep
import numpy as np

def main(stdscr):
    # curses config
    stdscr.clear()

    l, w = 20, 80
    board = Board(l, w, 0.12)
    stdscr.addstr(generate_msg("start",l, w))
    stdscr.getch()
    stdscr.nodelay(True)

    # game loop
    while(True):
        key = stdscr.getch()
        stdscr.erase()
        curses.cbreak()

        status, val = board.snake.move(key, board)

        if status == -1:
            stdscr.addstr(generate_msg("end", l, w))
            stdscr.addstr(str(board.points))
            break
        elif status == 1:
            board.collect_apple(val)

        stdscr.addstr(board.render())
        stdscr.addstr(str(board.points))

        stdscr.refresh()
        sleep(board.pause)

    stdscr.nodelay(False)
    stdscr.refresh()
    key = stdscr.getch()

def generate_msg(code, l, w):

    if code == "start":
         raw = """ #####  #     #    #    #    # ####### 
#     # ##    #   # #   #   #  #       
#       # #   #  #   #  #  #   #       
 #####  #  #  # #     # ###    #####   
      # #   # # ####### #  #   #       
#     # #    ## #     # #   #  #       
 #####  #     # #     # #    # ####### """
    else:
        raw = """ #####     #    #     # #######    ####### #     # ####### ######  
#     #   # #   ##   ## #          #     # #     # #       #     # 
#        #   #  # # # # #          #     # #     # #       #     # 
#  #### #     # #  #  # #####      #     # #     # #####   ######  
#     # ####### #     # #          #     #  #   #  #       #   #   
#     # #     # #     # #          #     #   # #   #       #    #  
 #####  #     # #     # #######    #######    #    ####### #     # """
 
    raw = np.array([list(elt) for elt in raw.splitlines()])
    raw_dims = raw.shape

    msg = np.full((l, w), [' '], dtype=str) 
    msg[1:(l-1), 0] = np.repeat(["█"], l-2)
    msg[1:(l-1), -1] = np.repeat(["█"], l-2)
    msg[0, 1:(w-1)] = np.repeat(["▄"], w-2)
    msg[-1, 1:(w-1)] = np.repeat(["▀"], w-2)

    ri, ci = (l - raw_dims[0]) // 2, (w - raw_dims[1]) // 2
    msg[ri:(ri + raw_dims[0]), ci:(ci + raw_dims[1])] = raw

    return "\n".join(["".join(elt) for elt in msg.tolist()])

wrapper(main)