import pygame,sys,random

pygame.init()
SCREEN_WIDTH = 1100
BOARD_SIZE = SCREEN_HEIGHT = 800
WHITE = (255,) * 3
BLACK = (0,) * 3
RED = (255,0,0)
TILE_COLOR = (222,184,135)
BGCOLOR = (210,105,30)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))


pygame.display.set_caption("N Puzzle")


clock = pygame.time.Clock()
FPS = 60

class Button(pygame.sprite.Sprite):

    def __init__(self,x,y,button_width,button_height,text,button_font,button_color=RED,text_color=BLACK):
        super().__init__()

        self.original_image = pygame.Surface((button_width,button_height))

        self.original_image.fill(button_color)


        text = button_font.render(text,True,text_color)

        self.original_image.blit(text,(self.original_image.get_width()//2 - text.get_width()//2,self.original_image.get_height()//2 - text.get_height()//2))


        self.original_rect = self.original_image.get_rect(topleft=(x,y))


        self.expanded_image = pygame.Surface((button_width + 20,button_height + 20))
        self.expanded_image.fill(button_color)

        self.expanded_image.blit(text,(self.expanded_image.get_width()//2 - text.get_width()//2,self.expanded_image.get_height()//2 - text.get_height()//2))
        self.expanded_rect = self.expanded_image.get_rect(center=self.original_rect.center)

        self.hovered_on = False
        self.image = self.original_image
        self.rect = self.original_rect

    def update(self,point):
        collided = self.rect.collidepoint(point)

        if not self.hovered_on and collided:
            self.hovered_on = True
            self.image = self.expanded_image
            self.rect = self.expanded_rect
        elif self.hovered_on and not collided:
            self.hovered_on = False
            self.image = self.original_image
            self.rect = self.original_rect

    
    def collided_on(self,point):

        return self.rect.collidepoint(point)








class NPuzzle:

    font = pygame.font.SysFont("calibri",40)
    button_font = pygame.font.SysFont("calibri",80)
    class Tile(pygame.sprite.Sprite):

        normal_font = pygame.font.SysFont("calibri",40)
         
        def __init__(self,x,y,number,square_size):
            super().__init__()


            self.image = pygame.Surface((square_size,square_size))

            number_text = self.normal_font.render(str(number),True,BLACK)

            self.image.fill(TILE_COLOR)

            self.image.blit(number_text,(square_size//2 - number_text.get_width()//2,square_size//2 - number_text.get_height()//2))



            self.rect = self.image.get_rect(topleft=(x,y))


        def draw(self,x,y):
            screen.blit(self.image,(x,y))




    def __init__(self,n=4):


        self.numbers = list(range(1,n**2))
        self.n = n
        pygame.display.set_caption(f"{n**2}-Puzzle")
        self.numbers.append(None)
        self.square_size = BOARD_SIZE//n
        top_gap = 50
        self.board_size = self.square_size * n
        pygame.display.set_mode((SCREEN_WIDTH,self.board_size))
        button_width = 200
        button_height = button_width//2
        self.reset_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,top_gap + button_height//2,button_width,button_height,"RESET",self.button_font)
        self.menu_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,top_gap + button_height + top_gap * 2,button_width,button_height,"MENU",self.button_font)
        self.buttons = pygame.sprite.Group(self.reset_button,self.menu_button)



        self._create_board()
        self._play_game()
    
    
    def _draw_board(self):


        for row in range(self.n):
            for col in range(self.n):
                if self.board[row][col] is None:
                    continue
                self.board[row][col].draw(col * self.square_size,row * self.square_size)

        for y in range(0,self.board_size,self.square_size):
            pygame.draw.line(screen,BLACK,(0,y),(self.board_size,y))

        for x in range(0,self.board_size + 1,self.square_size):
            pygame.draw.line(screen,BLACK,(x,0),(x,self.board_size))

        self.buttons.draw(screen)



    def _play_game(self):


        while True:


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    point = pygame.mouse.get_pos()
                    x,y = point


                    if x <= self.board_size:
                        row,col = y//self.square_size,x//self.square_size

                        for neighbor_row,neighbor_col in ((row -1,col),(row + 1,col),(row,col -1),(row,col +1)):
                            if 0 <= neighbor_row < self.n and 0 <= neighbor_col < self.n and self.board[neighbor_row][neighbor_col] is None:
                                self.board[neighbor_row][neighbor_col],self.board[row][col] = self.board[row][col],self.board[neighbor_row][neighbor_col]
                                self.none_location = (row,col)
                    else:

                        for i,button in enumerate(self.buttons):
                            if button.collided_on(point):
                                if i == 0:
                                    self._create_board()
                                else:
                                    return

                if event.type == pygame.KEYDOWN:
                    row,col = self.none_location
                    if event.key == pygame.K_DOWN:

                        if row - 1 >= 0:
                            self.board[row][col],self.board[row -1][col] = self.board[row -1][col],self.board[row][col]
                            self.none_location = (row - 1,col)
                    if event.key  == pygame.K_UP:
                        if row + 1 < self.n:
                            self.board[row][col],self.board[row +1][col] = self.board[row +1][col],self.board[row][col]
                            self.none_location = (row + 1,col)
                    if event.key == pygame.K_RIGHT:
                        if col - 1 >= 0:
                            self.board[row][col],self.board[row][col - 1] = self.board[row][col - 1],self.board[row][col]
                            self.none_location = (row,col -1 )
                    if event.key == pygame.K_LEFT:
                        if col + 1 < self.n:
                            self.board[row][col],self.board[row][col + 1] = self.board[row][col + 1],self.board[row][col]
                            self.none_location = (row,col +1 )







            point = pygame.mouse.get_pos()


            self.buttons.update(point)









            
            screen.fill(BGCOLOR)
            self._draw_board()
            pygame.display.update()
            clock.tick(FPS)







    


    def _create_board(self):


        random.shuffle(self.numbers)

        self.board = []
        self.tiles = pygame.sprite.Group()
        for row in range(self.n):
            new_row = []
            for col in range(self.n):
                number = self.numbers[row * self.n + col]
                if number is None:
                    self.none_location = (row,col)
                    new_row.append(None)
                    continue
                tile = self.Tile(col * self.square_size,row * self.square_size,number,self.square_size)
                new_row.append(tile)



            self.board.append(new_row)




def menu():


    title_font = pygame.font.SysFont("calibri",100)

    title_text = title_font.render("N-PUZZLE",True,BLACK)
    top_gap = 50
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2,top_gap + title_text.get_height()//2))
    button_width = 450
    button_height = 125
    play_button= Button(SCREEN_WIDTH//2 - button_width//2,title_rect.bottom + top_gap,button_width,button_height,"PLAY",title_font)
    ai_solver = Button(SCREEN_WIDTH//2 - button_width//2,title_rect.bottom + top_gap + button_height + top_gap,button_width,button_height,"AI SOLVER",title_font)
    buttons = pygame.sprite.Group(play_button,ai_solver)

    
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                point = pygame.mouse.get_pos()

                for i,button in enumerate(buttons):
                    if button.collided_on(point):
                        if i == 0:
                            NPuzzle()




        point = pygame.mouse.get_pos() 
        buttons.update(point)

        screen.fill(BGCOLOR)

        buttons.draw(screen)
        screen.blit(title_text,title_rect)

        pygame.display.update()




if __name__ == "__main__":
    
    menu()









