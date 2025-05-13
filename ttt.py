import pygame
import sys
import random

# ========================
# 1. BOARD: encapsulation of state & logic, with re-randomizable obstacles
# ========================
class Board:
    def __init__(self, rows=5, cols=5, win_len=4, num_obstacles=5):
        self._rows = rows
        self._cols = cols
        self._win_len = win_len
        self._num_obstacles = num_obstacles
        self._init_board()

    def _init_board(self):
        # initialize empty cells
        self._cells = [['.' for _ in range(self._cols)] for _ in range(self._rows)]
        # place obstacles
        self._place_obstacles()
        # cache legal moves
        self._legal = {(i, j)
                       for i in range(self._rows)
                       for j in range(self._cols)
                       if self._cells[i][j] == '.'}

    def _place_obstacles(self):
        placed = 0
        while placed < self._num_obstacles:
            i = random.randrange(self._rows)
            j = random.randrange(self._cols)
            if self._cells[i][j] == '.':
                self._cells[i][j] = '#'
                placed += 1

    def reset(self):
        # completely reinitialize board and obstacles
        self._init_board()

    def is_legal_move(self, i, j):
        return (i, j) in self._legal

    def place_mark(self, i, j, sym):
        if (i, j) in self._legal:
            self._cells[i][j] = sym
            self._legal.remove((i, j))
            return True
        return False

    def is_full(self):
        return not self._legal

    def check_winner(self, sym):
        dirs = [(1,0), (0,1), (1,1), (1,-1)]
        for i in range(self._rows):
            for j in range(self._cols):
                if self._cells[i][j] != sym:
                    continue
                for di, dj in dirs:
                    count, x, y = 1, i+di, j+dj
                    while (0 <= x < self._rows and
                           0 <= y < self._cols and
                           self._cells[x][y] == sym):
                        count += 1
                        if count >= self._win_len:
                            return True
                        x += di; y += dj
        return False

    def draw(self, screen, cell_size, margin, fonts):
        for i in range(self._rows):
            for j in range(self._cols):
                rect = pygame.Rect(
                    margin + j*(cell_size+margin),
                    margin + i*(cell_size+margin),
                    cell_size, cell_size
                )
                val = self._cells[i][j]
                color = (200,200,200) if val == '#' else (255,255,255)
                pygame.draw.rect(screen, color, rect)
                if val in ('X','O'):
                    text = fonts[val].render(
                        val, True,
                        (200,0,0) if val == 'X' else (0,0,200)
                    )
                    screen.blit(text, text.get_rect(center=rect.center))


# ===========================
# 2. PLAYER: inheritance
# ===========================
class Player:
    def __init__(self, symbol):
        self.symbol = symbol

    def make_move(self, board, *args):
        raise NotImplementedError

class HumanPlayer(Player):
    def make_move(self, board, pos, cell_size, margin):
        x, y = pos
        j = (x - margin) // (cell_size + margin)
        i = (y - margin) // (cell_size + margin)
        return board.place_mark(i, j, self.symbol)

# (Could add AIPlayer subclass here if desired)


# ========================
# 3. GAME: manages players & UI
# ========================
class Game:
    def __init__(self):
        pygame.init()
        # game parameters
        self._rows = 5
        self._cols = 5
        self._win_len = 4
        self._num_obstacles = 5

        cell_size, margin = 80, 5
        width  = self._cols*(cell_size+margin) + margin
        height = self._rows*(cell_size+margin) + margin + 60

        # initialize board & players
        self._board   = Board(self._rows, self._cols, self._win_len, self._num_obstacles)
        self._players = [HumanPlayer('X'), HumanPlayer('O')]
        self._turn    = 0  # index into players

        self._cell_size = cell_size
        self._margin    = margin
        self._screen    = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2-Player TicTacToe 5×5 (4 in a row)")
        self._fonts = {
            'X':   pygame.font.SysFont(None, 48),
            'O':   pygame.font.SysFont(None, 48),
            'MSG': pygame.font.SysFont(None, 60)
        }

        self._game_over = False
        self._winner    = None

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN and self._game_over:
                    if event.key == pygame.K_r:
                        # restart: reset board (including new obstacles)
                        self._board.reset()
                        self._turn = 0
                        self._game_over = False
                        self._winner = None

                elif event.type == pygame.MOUSEBUTTONDOWN and not self._game_over:
                    player = self._players[self._turn]
                    moved = player.make_move(
                        self._board,
                        event.pos,
                        self._cell_size,
                        self._margin
                    )
                    if moved:
                        sym = player.symbol
                        if self._board.check_winner(sym):
                            self._game_over = True
                            self._winner = sym
                        elif self._board.is_full():
                            self._game_over = True
                            self._winner = None
                        else:
                            self._turn = 1 - self._turn

            self._draw()
            clock.tick(30)

    def _draw(self):
        self._screen.fill((0,0,0))
        self._board.draw(
            self._screen,
            self._cell_size,
            self._margin,
            self._fonts
        )
        if self._game_over:
            if self._winner:
                msg = f"{self._winner} wins!"
            else:
                msg = "Draw!"
            text = self._fonts['MSG'].render(msg, True, (0,255,0))
            self._screen.blit(
                text,
                text.get_rect(center=self._screen.get_rect().center)
            )
            hint = self._fonts['MSG'].render("Press R to restart", True, (200,200,200))
            self._screen.blit(hint, (10, self._screen.get_height()-50))

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
