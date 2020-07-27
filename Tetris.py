"""
By Alexander Yanuar Koentjara - my attempt to learn Python by creating simple app
"""

import pygame
from random import randrange
from pygame.locals import *
from pygame.draw import lines, line

displaySize = width, height = (240, 400)
blockSize = 20
score = 0
level = 1
downTick = 30

class RecyclingColors:
    from pygame.color import THECOLORS as c
    colors = [ c['darkseagreen3'], c['firebrick'], c['mediumpurple3'], c['deepskyblue1'],
               c['gray'], c['gold4'], c['mediumorchid4'], c['azure4'] ]

    def __init__(self):
        self.current = 0

    def next(self):
        c = RecyclingColors.colors[self.current]
        self.current = (self.current + 1) % len(RecyclingColors.colors)
        return c

class Checkers:
    def __init__(self, blocks):
        self.blocks = blocks

    def draw(self, surface, x, y):
        def darken(rgb, d = 40):
            return max(rgb - d, 0)

        def lighten(rgb, d = 40):
            return min(rgb + d, 255)

        maxV = len(self.blocks)
        maxH = len(self.blocks[0])
        for py in range(maxV):
            for px in range(maxH):
                col = self.blocks[py][px]
                if col:
                    shadow = Color(*[darken(col[i]) for i in range(3)])
                    bright = Color(*[lighten(col[i]) for i in range(3)])
                    bx = (x + px) * blockSize
                    by = (y + py) * blockSize
                    r = Rect(bx + 1, by + 1, blockSize - 1, blockSize -1)
                    surface.fill(col, r)
                    lines(surface, shadow, False, [(bx, by), (bx, by + blockSize - 1),
                                                   (bx + blockSize - 1, by + blockSize - 1)])
                    lines(surface, bright, False, [(bx, by), (bx + blockSize - 1 , by),
                                                   (bx + blockSize - 1, by + blockSize - 1)])

class Board(Checkers):
    def __init__(self, blocks):
        Checkers.__init__(self, blocks)

    def draw(self, surface, block):
        minX = 99
        maxX = 0
        for y in range(block.shape.dim):
            for x in range(block.shape.dim):
                if block.shape.blocks[y][x]:
                    minX = min(x, minX)
                    maxX = max(x, maxX)

        maxV = len(self.blocks)
        maxH = len(self.blocks[0])
        for px in range(maxH):
            if block.x + minX <= px <= block.x + maxX:
                surface.fill((20, 20, 20), Rect(px * blockSize, 0, blockSize, maxV * blockSize))
            line(surface, (30, 30, 30), (px * blockSize, 0), (px * blockSize, maxV * blockSize))
        for py in range(maxV):
            line(surface, (30, 30, 30), (0, py * blockSize), (maxH * blockSize, py * blockSize))
        super().draw(surface, 0, 0)

class Shape(Checkers):
    def __init__(self, data = None, color = Color(0, 0, 0)):
        if not data:
            data = [[]]
        self.dim = max(len(data), max([len(d) for d in data]))
        blocks = Shape.__emptyBlocks(self.dim)
        rows = 0
        for row in data:
            cols = 0
            for v in row:
                blocks[rows][cols] = color if v else 0
                cols += 1
            rows += 1
        self.color = color
        Checkers.__init__(self, blocks)

    def __emptyBlocks(slot):
        return [[0 for _ in range(slot)] for _ in range(slot)]

    def clone(self, color = None):
        c = color if color else self.color
        s = Shape(0, c)
        s.blocks = [ [ c if col else 0 for col in row ] for row in self.blocks ]
        s.dim = self.dim
        return s

    def rotateRight(self):
        bl = Shape.__emptyBlocks(self.dim)
        for py in range(self.dim):
            for px in range(self.dim):
                bl[px][self.dim - 1 - py] = self.blocks[py][px]
        self.blocks = bl
        return self

    def rotateLeft(self):
        bl = Shape.__emptyBlocks(self.dim)
        for py in range(self.dim):
            for px in range(self.dim):
                bl[self.dim - 1 - px][py] = self.blocks[py][px]
        self.blocks = bl
        return self

    def draw(self, surface, x, y):
        super().draw(surface, x, y)

    def checkBound(self, board, x, y):
        maxV = len(board)
        maxH = len(board[0])
        for py in range(self.dim):
            for px in range(self.dim):
                if self.blocks[py][px]:
                    vx = x + px
                    vy = y + py
                    if 0 <= vy < maxV and 0 <= vx < maxH:
                        if board[vy][vx]:
                            return False
                    else:
                        return False
        return True

    def mark(self, board, x, y):
        maxV = len(board)
        maxH = len(board[0])
        global score
        score += 10
        for py in range(self.dim):
            for px in range(self.dim):
                vy = py + y
                vx = px + x
                if 0 <= vy < maxV and 0 <= vx < maxH and self.blocks[py][px]:
                    board[vy][vx] = self.color

        for row in range(maxV - 1, 0, -1):
            complete = 0
            while True:
                filled = True
                for col in range(maxH):
                    if not board[row][col]:
                        filled = False
                        break
                if filled:
                    del board[row]
                    board.insert(0, [ 0 for _ in range(maxH) ])
                    complete += 1
                else:
                    break
            if complete:
                global level
                score += 100 * (complete ** 2)
                level = int(score / 1000) + 1

class Blocks:
    def __init__(self, board, x, y, shape):
        self.board = board
        self.x = x
        self.y = y
        self.shape = shape

    def checkBound(self, x, y, shape = None):
        if not shape:
            shape = self.shape
        return shape.checkBound(self.board, x, y)

    def draw(self, surface):
        self.shape.draw(surface, self.x, self.y)

    def down(self):
        if self.checkBound(self.x, self.y + 1):
            self.y += 1
            return True
        else:
            self.shape.mark(self.board, self.x, self.y)
            return False

    def right(self):
        if self.checkBound(self.x + 1, self.y):
            self.x += 1

    def left(self):
        if self.checkBound(self.x - 1, self.y):
            self.x -= 1

    def rotateRight(self):
        if self.checkBound(self.x, self.y, self.shape.clone().rotateRight()):
            self.shape.rotateRight()

    def rotateLeft(self):
        if self.checkBound(self.x, self.y, self.shape.clone().rotateLeft()):
            self.shape.rotateLeft()

    def drop(self):
        while self.down():
            pass
        return True

def main():
    shapes = [
        Shape([[1, 1], [1, 1]]),
        Shape([[], [1, 1, 1, 1]]),
        Shape([[1, 1, 1], [1]]),
        Shape([[1], [1, 1, 1]]),
        Shape([[1, 1], [0, 1, 1]]),
        Shape([[0, 1, 1], [1, 1]]),
        Shape([[0, 1, 0], [1, 1, 1]]),
    ]

    hBlocks = int(width / blockSize)
    vBlocks = int(height / blockSize)
    center = int(hBlocks / 2) - 2
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(displaySize)
    pygame.display.set_caption('Tetris')
    pygame.mouse.set_visible(False)
    font = pygame.font.Font(None, 20)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    rc = RecyclingColors()

    board = [[ 0 for _ in range(hBlocks)] for _ in range(vBlocks)]
    repeat = True
    ticks = 0
    current = 0
    gameBoard = Board(board)
    spawn = True

    def randomShape():
        return shapes[randrange(0, len(shapes))].clone(rc.next())

    while repeat:
        if spawn:
            spawn = False
            if current:
                del current
            current = Blocks(board, center, 0, randomShape())
            if not current.checkBound(current.x, current.y):
                # game over
                repeat = False
                current = 0

        ticks += 1
        clock.tick(30)
        background.fill((0, 0, 0))
        if current:
            gameBoard.draw(background, current)
            current.draw(background)

        text = font.render("Level %s Score %s" % (level, score), 1, (255, 255, 255))
        background.blit(text, (1, 1))

        if ticks % (downTick - level * 2) == 0:
            if not current.down():
                spawn = True

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_q:
                    current.rotateLeft()
                elif event.key == K_w or event.key == K_KP5:
                    current.rotateRight()
                elif event.key == K_LEFT or event.key == K_KP4:
                    current.left()
                elif event.key == K_RIGHT or event.key == K_KP6:
                    current.right()
                elif event.key == K_DOWN or event.key == K_KP2:
                    current.down()
                elif event.key == K_SPACE or event.key == K_KP0:
                    spawn = current.drop()

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                repeat = False

        screen.blit(background, (0, 0))
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
