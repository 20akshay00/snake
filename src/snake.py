import numpy as np

KEY_MAP = {ord("w"): [-1, 0], ord("s"): [1, 0], ord("a"): [0, -1], ord("d"): [0, 1]}

def plus(l1, l2):
    return [l1[0] + l2[0], l1[1] + l2[1]]

def clamp(n, smallest, largest): return max(smallest, min(n, largest)) 

class Snake:
    def __init__(self, len = 3):
        self.dir = [1, 0]
        
        # generate initial snake tail
        self.tail = [[7, 7]]
        for i in range(len):
            self.tail.append(plus(self.tail[-1], [-1, 0]))

        self.char = '▖'

    def move(self, key, board):

        # keep track of directions
        dir = KEY_MAP.get(key) or self.dir

        # dont allow backtracking
        if plus(dir, self.dir) == [0, 0]: dir = self.dir
        self.dir = dir

        # shift the snake
        if board.is_periodic:
            head = [(self.tail[0][0] + dir[0]) % board.l, (self.tail[0][1] + dir[1]) % board.w]
        else:
            head = plus(self.tail[0], dir)

            # wall collision signal
            if head[0] == 0 or head[0] == board.l - 1 or head[1] == 0 or head[1] == board.w - 1:
                return -1, None

        # update the snake
        self.tail.insert(0, head)
        self.tail.pop()

        # self collision signal
        if(head in self.tail[1:]): return -1, None

        # object collision signal
        for i, elt in enumerate(board.apples):
            if(head == elt.pos): return 1, i

        # uneventful move signal
        return 0, None

    def extend(self, point):
        for i in range(point):
            self.tail = [plus(self.tail[0], self.dir)] + self.tail

    def render(self, screen):
        screen[tuple(zip(*self.tail))] = np.repeat([self.char], len(self.tail))

class Apple:
    def __init__(self, board, char = 'o', points = 1, action = None):

        # generate spawn position without overlap with other elements
        pos = [np.random.randint(1, board.l-2), np.random.randint(1, board.w-2)]
        while pos in (board.snake.tail + [elt.pos for elt in board.apples]):
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
            ['⬤', 0, ("set_pause", -0.035)],
            ['◯', 2, ("set_pause", 0.025)]]

        # generate initial apples
        for i in range(3):
            self.apples.append(Apple(self, *self.apple_types[i]))

    def render(self):
        screen = np.full((self.l, self.w), [' '], dtype=str)

        # render the walls
        wall_char = self.wall_chars[0], self.wall_chars[1], self.wall_chars[2] 
        if self.is_periodic:
            wall_char = self.wall_chars[3], self.wall_chars[4], self.wall_chars[5]
        
        screen[1:(self.l-1), 0] = np.repeat([wall_char[0]], self.l-2)
        screen[1:(self.l-1), -1] = np.repeat([wall_char[0]], self.l-2)
        screen[0, 1:(self.w-1)] = np.repeat([wall_char[1]], self.w-2)
        screen[-1, 1:(self.w-1)] = np.repeat([wall_char[2]], self.w-2)

        # render the player and apples
        self.snake.render(screen)
        for elt in self.apples:
            elt.render(screen)
    
        return "\n".join(["".join(elt) for elt in screen.tolist()])

    def collect_apple(self, pos):
        # extend the snake
        self.snake.extend(self.apples[pos].points)

        # apply action specific to the apple
        getattr(self, self.apples[pos].action)(self.apples[pos].action_args)
        self.apples.pop(pos)

        # increment total score
        self.points += 1
        
        # generate new apple
        apple_params = self.apple_types[np.random.randint(0, len(self.apple_types))]
        self.apples.append(Apple(self, *apple_params))

        return 0, None

    # convenience functions to change attributes of the board

    def set_pause(self, *args):
        self.pause = clamp(self.pause + args[0], 0.05, 0.3)

    def toggle_boundary(self, *args):
        self.is_periodic = ~self.is_periodic

    def do_nothing(self, *args):
        pass