import curses
from curses import wrapper
from snake import Snake, Apple, Board
from time import sleep

def main(stdscr):
    # Clear screen
    stdscr.clear()
    stdscr.nodelay(True)

    l, w = 20, 50
    board = Board(l, w)

    # This raises ZeroDivisionError when i == 10.
    while(True):
        key = stdscr.getch()
        stdscr.erase()
        
        status, val = board.snake.move(key, board)

        if status == -1:
            stdscr.addstr("GAME OVER.")
            break
        elif status == 1:
            board.remove_apple(val)

        stdscr.addstr(board.render())

        stdscr.refresh()
        sleep(0.15)

    stdscr.nodelay(False)
    stdscr.refresh()
    key = stdscr.getch()

wrapper(main)