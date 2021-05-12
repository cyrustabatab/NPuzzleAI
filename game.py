import pygame,sys,random

pygame.init()
SCREEN_WIDTH = 1100
BOARD_SIZE = SCREEN_HEIGHT = 800
WHITE = (255,) * 3
BLACK = (0,) * 3
TILE_COLOR = (222,184,135)
BGCOLOR = (210,105,30)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))


pygame.display.set_caption("N Puzzle")


clock = pygame.time.Clock()
FPS = 60




class NPuzzle:

    font = pygame.font.SysFont("calibri",40)
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
        self.board_size = self.square_size * n
        pygame.display.set_mode((SCREEN_WIDTH,self.board_size))

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
                                self.none_location = (neighbor_row,neighbor_col)

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




if __name__ == "__main__":
    
    NPuzzle()




















