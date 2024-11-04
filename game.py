import pygame
from pygame.locals import *
from help import Info
from start_gui import StartGui
from board import Board
from computer import Computer
from copy import deepcopy
from math import sqrt
from random import randint


class Game:
    def __init__(self):
        self.win = pygame.display.set_mode((Info.WIN_WIDTH, Info.WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.start_gui = StartGui()
        self.board = Board()
        self.computer = Computer(self.board.check_winner)
        self.game_end = False
        self.game_start = True
        self.game_state = None
        self.player1 = True     # player 1 is X, player 2 is O
        self.hover_pos = None
        self.game_over = False
        self.in_cooldown = False
        self.computer_cooldown = 0  # cooldown for the computer to make a move -> so it doesn't make a move instantly
        self.max_cooldown = Info.FPS / 10
        self.win_loc = None
        self.end_line_width = Info.WIN_WIDTH // 40
        self.line_length = None
        self.draw = True

        self.final_surf = None
        self.final_rect = None


    
    def mainloop(self):

        run = True
        while run:
            self.clock.tick(Info.FPS)

            if self.in_cooldown:
                self.computer_cooldown += 1

            if not self.player1 and self.game_state == "pvc" and not self.game_over and self.computer_cooldown >= self.max_cooldown:
                self.in_cooldown = False
                self.computer_cooldown = 0
                _, (i, j) = self.computer.computer_move(deepcopy(self.board.board), self.player1)
                self.board.make_move(i, j, self.player1)
                winner, win_loc = self.board.check_winner(self.board.board)
                if winner is not None:
                    self.game_over = True
                    self.win_loc = win_loc
                    if winner != 0:  # draw
                        self.create_end_line(win_loc)
                        self.draw = False
                self.player1 = not self.player1

            mouse_x, mouse_y = pygame.mouse.get_pos()
            #self.hover_pos = None 
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.game_end = True
                    return
                # game start
                if self.game_start:
                    self.start_gui.pvp_hover = False
                    self.start_gui.pvc_hover = False
                    # check if the mouse is over the pvp button
                    if self.start_gui.pvp_rect.collidepoint(mouse_x, mouse_y):
                        self.start_gui.pvp_hover = True
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.game_start = False
                            self.game_state = "pvp"
                    # check if the mouse is over the pvc button
                    elif self.start_gui.pvc_rect.collidepoint(mouse_x, mouse_y): 
                        self.start_gui.pvc_hover = True
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.game_start = False
                            self.game_state = "pvc"
                            if randint(0, 1) == 1:
                                self.player1 = not self.player1   # 50/50 chance which player begins when playing against the computer
                                self.in_cooldown = True
                # during game
                elif not self.game_over:   # game starts
                    if (self.player1 and self.game_state == "pvc") or self.game_state == "pvp":
                        col = min(2, mouse_x // ((Info.WIN_WIDTH) // 3))  # min so row or col can't be 3 there's no IndexError
                        row = min(2, mouse_y // ((Info.WIN_HEIGHT) // 3))
                        self.hover_pos = (row, col)
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if self.board.make_move(row, col, self.player1): # returning False if the move is invalid
                                self.player1 = not self.player1
                                winner, win_loc = self.board.check_winner(self.board.board)
                                if winner is not None:
                                    self.game_over = True
                                    self.win_loc = win_loc
                                    if winner != 0:     # draw
                                        self.create_end_line(win_loc)
                                        self.draw = False
                                self.in_cooldown = True
                # game end
                else:
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        return

            self.redraw_window()

    
    def create_end_line(self, win_loc):
        rect_target_begin = pygame.Rect(*self.board.pos_to_coords(win_loc[0]), self.board.cell_size, self.board.cell_size)
        rect_target_end = pygame.Rect(*self.board.pos_to_coords(win_loc[1]), self.board.cell_size, self.board.cell_size)
        if self.win_loc == ((0, 2), (2, 0)) or self.win_loc == ((0, 0), (2, 2)):    # diagonal
            self.line_length = sqrt((rect_target_end.center[0] - rect_target_begin.center[0]) ** 2 + (rect_target_end.center[1] - rect_target_begin.center[1]) ** 2) * 1.2
        else:   # horizontal or vertical
            self.line_length = self.board.cell_size * 2 * 1.3

        rect_surf = pygame.Surface((self.board.img.get_rect().size), SRCALPHA)  # create surf
        line_rect = pygame.Rect(0, 0, self.line_length, self.end_line_width)    # create rect for the line
        line_rect.center = rect_surf.get_rect().center                          # center the line on the surface
        pygame.draw.rect(rect_surf, Info.colors["gray"], line_rect)             # draw the line on the surface
        
        # rotate the line
        if self.win_loc == ((0, 2), (2, 0)):               # diagonal from top right to bottom left 
            self.final_surf = pygame.transform.rotate(rect_surf, 45)                # rotate the surface
        elif self.win_loc == ((0, 0), (2, 2)):             # diagonal from top left to bottom right
            self.final_surf = pygame.transform.rotate(rect_surf, -45)                 
        elif self.win_loc[0][1] == self.win_loc[1][1]:     # vertical
            self.final_surf = pygame.transform.rotate(rect_surf, 90)
        else:
            self.final_surf = rect_surf      # horizontal -> leave it like it is
        
        # place the line correctly
        self.final_rect = self.final_surf.get_rect(center=self.board.img.get_rect().center) # get the center of the rotated surface
        if self.win_loc[0][1] == self.win_loc[1][1]:
            self.final_rect.x += (self.win_loc[0][1] - 1) * self.board.cell_size
        elif self.win_loc[0][0] == self.win_loc[1][0]:
            self.final_rect.y += (self.win_loc[0][0] - 1) * self.board.cell_size

    
    def redraw_window(self):
        if not self.game_over:
            self.win.fill(Info.colors["bg"])
        else:
            self.win.fill(Info.colors["end_bg"])
        if self.game_start:
            self.start_gui.draw(self.win)
        else:
            if self.hover_pos is not None and self.board.board[self.hover_pos[0]][self.hover_pos[1]] == '':
                target = pygame.Rect(*self.board.pos_to_coords(self.hover_pos), self.board.cell_size, self.board.cell_size)
                pos_rect = self.board.player_x_img.get_rect(center=target.center)
                transparent_img = self.board.player_x_img.copy() if self.player1 else self.board.player_o_img.copy()
                transparent_img.set_alpha(50)
                self.win.blit(transparent_img, pos_rect)
            self.board.draw(self.win)
            if self.game_over and not self.draw:
                self.win.blit(self.final_surf, self.final_rect)     
        pygame.display.flip()


pygame.init()
pygame.display.set_caption('TicTacToe')

while True:
    game = Game()
    game.mainloop()
    if game.game_end:
        break