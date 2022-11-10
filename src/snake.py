import numpy as np
import curses

def plus(l1, l2):
    return [l1[0] + l2[0], l1[1] + l2[1]]

def clamp(n, smallest, largest): return max(smallest, min(n, largest)) 

class Snake:
    def __init__(self, len = 3):
        self.head = [7, 7]
        self.dir = [1, 0]
        
        self.tail = [plus(self.head, self.dir)]
        for i in range(len - 1):
            self.tail.append(plus(self.tail[-1], self.dir))

        self.char = '▖'

    def move(self, key, board):
        moves = {ord("w"): [-1, 0], ord("s"): [1, 0], ord("a"): [0, -1], ord("d"): [0, 1]}

        # keep track of directions
        dir = moves.get(key) or self.dir

        # dont allow backtracking
        if plus(dir, self.dir) == [0, 0]: dir = self.dir
        self.dir = dir

        # shift the snake
        self.tail.append(self.head)
        if board.is_periodic:
            self.head = [(self.head[0] + dir[0]) % board.l, (self.head[1] + dir[1]) % board.w]
        else:
            self.head = plus(self.head, dir)

            # wall collision signal
            if self.head[0] == 0 or self.head[0] == board.l - 1 or self.head[1] == 0 or self.head[1] == board.w - 1:
                return -1, None

        self.tail.pop(0)

        # self collision signal
        if(self.head in self.tail): return -1, None

        # object collision signal
        for i, elt in enumerate(board.apples):
            if(self.head == elt.pos): return 1, i

        # uneventful move signal
        return 0, None

    def extend(self, point):
        for i in range(point):
            self.tail.append(self.tail[-1] + self.dir)

    def render(self, screen):
        screen[tuple(zip(*([self.head] + self.tail)))] = np.repeat([self.char], len(self.tail) + 1)

class Apple:
    def __init__(self, board, char = 'o', points = 1, action = None):
        pos = [np.random.randint(1, board.l-2), np.random.randint(1, board.w-2)]
        while pos in (board.snake.tail + [board.snake.head] + [elt.pos for elt in board.apples]):
            pos = [np.random.randint(1, board.l-2), np.random.randint(1, board.w-2)]

        self.pos = pos
        self.char = char
        self.points = points

        self.action = "do_nothing" if action is None else action[0]
        self.action_args = None if action is None else action[1]

    def render(self, screen):
        screen[tuple(self.pos)] = self.char

class Board:
    def __init__(self, l, w, pause = 0.15):
        self.l, self.w = l, w
        self.pause = pause
        self.points = 0

        self.is_periodic = False
        self.wall_chars = ["█", "▄", "▀", "║", "═", "═"]

        self.snake = Snake()
        self.apples = []        
        self.apple_types = [
            ['o', 1], 
            ['¤', 2, ("toggle_boundary", None)], 
            ['⬤', 3, ("set_pause", -0.035)],
            ['◯', 2, ("set_pause", 0.025)]]

        for i in range(3):
            self.apples.append(Apple(self, *self.apple_types[i]))

    def render(self):
        screen = np.full((self.l, self.w), [' '], dtype=str)

        wall_char = self.wall_chars[0], self.wall_chars[1], self.wall_chars[2] 
        if self.is_periodic:
            wall_char = self.wall_chars[3], self.wall_chars[4], self.wall_chars[5]
        
        screen[1:(self.l-1), 0] = np.repeat([wall_char[0]], self.l-2)
        screen[1:(self.l-1), -1] = np.repeat([wall_char[0]], self.l-2)
        screen[0, 1:(self.w-1)] = np.repeat([wall_char[1]], self.w-2)
        screen[-1, 1:(self.w-1)] = np.repeat([wall_char[2]], self.w-2)

        self.snake.render(screen)
        for elt in self.apples:
            elt.render(screen)
    
        return "\n".join(["".join(elt) for elt in screen.tolist()])

    def set_pause(self, *args):
        self.pause = clamp(self.pause + args[0], 0.05, 0.3)

    def toggle_boundary(self, *args):
        self.is_periodic = ~self.is_periodic

    def do_nothing(self, *args):
        pass

    def remove_apple(self, pos):
        self.snake.extend(self.apples[pos].points)
        getattr(self, self.apples[pos].action)(self.apples[pos].action_args)
        self.apples.pop(pos)
        self.points += 1
        
        apple_params = self.apple_types[np.random.randint(0, len(self.apple_types))]
        self.apples.append(Apple(self, *apple_params))

        return 0, None