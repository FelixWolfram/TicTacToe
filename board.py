from pygame import image, transform, Rect, draw
from help import Info


class Board:
    def __init__(self):
        self.img = image.load('assets/images/board_white.png').convert_alpha()
        self.img = transform.scale(self.img, (Info.WIN_WIDTH, Info.WIN_HEIGHT))
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.player_x_img = image.load('assets/images/player_x.png').convert_alpha()
        self.player_o_img = image.load('assets/images/player_o.png').convert_alpha()
        self.border_width = Info.WIN_WIDTH // 48
        self.grid_line_width = Info.WIN_WIDTH // 68.5
        self.cell_size = (Info.WIN_WIDTH - 2 * self.border_width) // 3
        self.scale_factor = 0.8
        self.player_x_img = transform.smoothscale(self.player_x_img, (self.cell_size * self.scale_factor, self.cell_size * self.scale_factor))
        self.player_o_img = transform.smoothscale(self.player_o_img, (self.cell_size * self.scale_factor, self.cell_size * self.scale_factor))


    def make_move(self, row, col, player1):
        if self.board[row][col] == '':
            self.board[row][col] = 'X' if player1 else 'O'
            return True
        return False
    

    # 1 if player 1 wins, -1 if player 2 wins, 0 if draw, None if no winner
    def check_winner(self, board): 
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '':
                winner = 1 if board[i][1] == 'X' else -1 
                return winner, ((i, 0), (i, 2))
            elif board[0][i] == board[1][i] == board[2][i] != '':
                winner = 1 if board[1][i] == 'X' else -1 
                return winner, ((0, i), (2, i))
        if board[0][0] == board[1][1] == board[2][2] != '':
            winner = 1 if board[1][1] == 'X' else -1 
            return winner, ((0, 0), (2, 2))
        elif board[0][2] == board[1][1] == board[2][0] != '':
            winner = 1 if board[1][1] == 'X' else -1 
            return winner, ((0, 2), (2, 0))
        if all(board[i][j] != '' for i in range(3) for j in range(3)):
            return 0, (None, None)    # draw
        return None, (None, None)   # no winner or draw yet


    def pos_to_coords(self, pos):
        x = pos[1] * self.cell_size + self.border_width
        y = pos[0] * self.cell_size + self.border_width
        return x, y


    def draw(self, win):
        win.blit(self.img, (0, 0))
        for row in range(3):
            for col in range(3):
                target = Rect(*self.pos_to_coords((row, col)), self.cell_size, self.cell_size)
                pos_rect = self.player_x_img.get_rect(center=target.center)
                if self.board[row][col] == 'X':
                    win.blit(self.player_x_img, pos_rect)
                elif self.board[row][col] == 'O':
                    win.blit(self.player_o_img, pos_rect)
