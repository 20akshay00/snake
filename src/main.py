import curses
from curses import wrapper
from snake import Snake, Apple, Board
from time import sleep

def main(stdscr):
    # curses config
    stdscr.clear()
    stdscr.nodelay(True)
    # curses.curs_set(0)

    l, w = 20, 50
    board = Board(l, w)

    # game loop
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
        sleep(board.pause)

    stdscr.nodelay(False)
    stdscr.refresh()
    key = stdscr.getch()

wrapper(main)