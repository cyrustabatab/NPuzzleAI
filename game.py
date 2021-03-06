import pygame,sys,random,math
from pprint import pprint
import time
import threading
import heapq

# IDA Deepening A* Search and add ability to make custom board

vec = pygame.math.Vector2

pygame.init()
SCREEN_WIDTH = 1100
BOARD_SIZE = SCREEN_HEIGHT = 800
WHITE = (255,) * 3
BLACK = (0,) * 3
GREEN = (0,255,0)
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
    button_font = pygame.font.SysFont("calibri",70)
    back_button = pygame.image.load('back.png').convert_alpha()
    back_button = pygame.transform.scale(back_button,(50,50))
    class Tile(pygame.sprite.Sprite):

        normal_font = pygame.font.SysFont("calibri",40)
         
        def __init__(self,x,y,number,square_size,font):
            super().__init__()


            self.image = pygame.Surface((square_size,square_size))
            self.number = number
            self.font = font 
            self.square_size = square_size
            self.number_text = font.render(str(number),True,BLACK)

            self.image.fill(TILE_COLOR)

            self.image.blit(self.number_text,(square_size//2 - self.number_text.get_width()//2,square_size//2 - self.number_text.get_height()//2))
            self.text = number



            self.rect = self.image.get_rect(topleft=(x,y))
        
        def move(self,amount):
            self.rect.center += amount
        
        def unfocus(self):
            self.image.fill(TILE_COLOR)
            self.image.blit(self.number_text,(self.square_size//2 - self.number_text.get_width()//2,self.square_size//2 - self.number_text.get_height()//2))
        def focus(self):
            self.image.fill(WHITE)
            self.image.blit(self.number_text,(self.square_size//2 - self.number_text.get_width()//2,self.square_size//2 - self.number_text.get_height()//2))
        


        def standardize(self):
            self.number = int(self.text)
            self.image.fill(TILE_COLOR)
            self.image.blit(self.number_text,(self.square_size//2 - self.number_text.get_width()//2,self.square_size//2 - self.number_text.get_height()//2))
        
        def set_text(self,number):
            self.text = number
            self.number_text = self.font.render(str(number),True,BLACK)
            self.image.fill(WHITE)
            self.image.blit(self.number_text,(self.square_size//2 - self.number_text.get_width()//2,self.square_size//2 - self.number_text.get_height()//2))

        def draw(self,x,y):
            screen.blit(self.image,(x,y))

    
    
    
    



    def __init__(self,n=4,solver_mode=False):


        self.numbers = list(range(1,n**2))
        self.n = n
        self.solver_mode = solver_mode

        if n <= 10:
            self.tile_font = self.font
        elif n <= 24:
            self.tile_font = pygame.font.SysFont("calibri",20)
        elif n <= 39:
            self.tile_font = pygame.font.SysFont("calibri",10)
        elif n <= 45:
            self.tile_font = pygame.font.SysFont("calibri",8)
        elif n <= 50:
            self.tile_font = pygame.font.SysFont("calibri",7)
        pygame.display.set_caption(f"{n**2}-Puzzle")
        self.numbers.append(None)

        self.square_size = BOARD_SIZE//n
        top_gap = 50
        self.board_size = self.square_size * n
        pygame.display.set_mode((SCREEN_WIDTH,self.board_size))
        button_width = 250
        button_height = button_width//3
        self.reset_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,top_gap + button_height//2,button_width,button_height,"RESET",self.button_font)
        self.menu_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,top_gap + button_height + top_gap * 2,button_width,button_height,"MENU",self.button_font)


        self.back_button_rect = self.back_button.get_rect(topleft=(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - self.back_button.get_width()//2,20))
        self.buttons = pygame.sprite.Group(self.reset_button,self.menu_button)
        if self.solver_mode:
            self.custom_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,top_gap + 2 * button_height + top_gap * 3,button_width,button_height,"CUSTOM",self.button_font)
            self.solve_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,top_gap + 3  *button_height + top_gap * 4,button_width,button_height,"SOLVE",self.button_font)
            self.buttons.add(self.custom_button)
            self.buttons.add(self.solve_button)




        self._create_board()
        pygame.mixer.music.load('music.ogg')
        pygame.mixer.music.play(-1)
        #self._play_game()
    
    
    def _draw_board(self,tile_to_skip=None):


        for row in range(self.n):
            for col in range(self.n):
                if self.board[row][col] is None or self.board[row][col] is tile_to_skip:
                    continue
                self.board[row][col].draw(col * self.square_size,row * self.square_size)

        for y in range(0,self.board_size,self.square_size):
            pygame.draw.line(screen,BLACK,(0,y),(self.board_size,y))

        for x in range(0,self.board_size + 1,self.square_size):
            pygame.draw.line(screen,BLACK,(x,0),(x,self.board_size))
        
        
        self.buttons.draw(screen)

        screen.blit(self.back_button,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - self.back_button.get_width()//2,20))

    
    def _get_custom_board(self):
        

        tiles = [[self.Tile(col * self.square_size,row * self.square_size,'',self.square_size,self.tile_font) for col in range(self.n)] for row in range(self.n)]


        empty_tile = random.choice(tiles)


        
        goal = list(range(1,self.n**2 ))
        goal.append(None)


        


        info_font = pygame.font.SysFont("calibri",20)
        

        missing_text = info_font.render("ONLY ONE EMPTY SQUARE!",True,BLACK)
        duplicate_text = info_font.render("UNIQUE NUMBERS ONLY!",True,BLACK)
        not_solvable = info_font.render(f"NOT SOLVABLE",True,BLACK)
        already_solved = info_font.render("ALREADY SOLVED",True,BLACK)
        
        
        button_width = 200
        button_height = button_width//2
        create_button = Button(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - button_width//2,SCREEN_HEIGHT//2 - button_height//2,button_width,button_height,"CREATE",self.button_font)
        

        def check_validity():
            
            numbers = set()
            for row in tiles:
                for tile in row:
                    number = tile.text
                    if number in numbers:
                        if number.isdigit():
                            if int(number) > maximum:
                                return invalid_range_text
                            return duplicate_text
                        else:
                            return missing_text
                    numbers.add(number)






        button = pygame.sprite.GroupSingle(create_button)


        focused = tiles[0][0]
        focused.focus()
        text = ''
        maximum = self.n**2 - 1
        result = None
        current_row = current_col = 0
        while True:

            current_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    point = pygame.mouse.get_pos()

                    x,y = point

                    if x <= self.board_size:
                        row,col = y//self.square_size,x//self.square_size
                        tiles[row][col].focus()
                        current_row,current_col = row,col
                        if focused:
                            focused.unfocus()
                            text = tiles[row][col].text
                        focused = tiles[row][col]
                    else:
                        if create_button.collided_on(point):
                            result = check_validity()
                            if result:
                                start_time = time.time()
                            else:
                                self.numbers = [(int(tile.text) if tile.text != '' else None) for row in tiles for tile in row]

                                if self.numbers == goal:
                                    result = already_solved
                                    start_time = time.time()
                                elif self._is_solvable():




                                    for i in range(len(tiles)):
                                        for j in range(len(tiles[0])):
                                            print(tiles[i][j].text,end='')
                                            if tiles[i][j].text == '':
                                                tiles[i][j] = None
                                                self.none_location = (i,j)
                                            else:
                                                tiles[i][j].standardize()
                                        print()
                                    self.board = tiles
                                    return
                                else:
                                    result = not_solvable
                                    start_time = time.time()









                if focused and event.type == pygame.KEYDOWN:
                    if pygame.K_0 <=event.key <= pygame.K_9: 
                        number = chr(event.key)
                        if not text and number == '0':
                            continue
                        if int(text + number) <= maximum:
                            text += number
                            focused.set_text(text)
                    elif event.key == pygame.K_BACKSPACE:
                        if text:
                            text = text[:-1]
                            focused.set_text(text)
                    else:
                        hit_arrow = False
                        if event.key == pygame.K_DOWN:
                            current_row = (current_row + 1) % self.n

                            hit_arrow = True
                        elif event.key == pygame.K_RIGHT:
                            current_col = (current_col + 1) % self.n
                            hit_arrow = True
                        elif event.key == pygame.K_LEFT:
                            current_col = (current_col - 1) % self.n
                            hit_arrow = True
                        elif event.key == pygame.K_UP:
                            current_row = (current_row - 1) % self.n
                            hit_arrow = True

                            
                        if hit_arrow:
                            tiles[current_row][current_col].focus()
                            if focused:
                                focused.unfocus()
                                text = tiles[current_row][current_col].text
                            focused = tiles[current_row][current_col]
            
            if result:
                if current_time - start_time >= 1:
                    result = None







            point = pygame.mouse.get_pos()

            button.update(point)





            
            screen.fill(BGCOLOR)

            button.draw(screen)
            for row in tiles:
                for tile in row:
                    tile.draw(*tile.rect.topleft)

            for y in range(0,self.board_size,self.square_size):
                pygame.draw.line(screen,BLACK,(0,y),(self.board_size,y))

            for x in range(0,self.board_size + 1,self.square_size):
                pygame.draw.line(screen,BLACK,(x,0),(x,self.board_size))
            

            if result:
                screen.blit(result,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - result.get_width()//2,SCREEN_HEIGHT//2 + 2 * button_height))


            pygame.display.update()



        


    def _play_game(self):

        

        game_win = pygame.mixer.Sound("game_win.wav")
        finished = False
        font = pygame.font.SysFont("calibri",80)
        info_font = pygame.font.SysFont("calibri",50)
        win_text = font.render("SOLVED!",True,GREEN)
        moves = 0
        moves_text = info_font.render("MOVES: 0",True,BLACK)
        start_time = time.time()

        time_text = info_font.render("00:00.0",True,BLACK)
            
        def reset():
            nonlocal finished,moves,moves_text,start_time,time_text
            self._create_board()
            finished = False
            moves = 0
            moves_text = info_font.render("MOVES: 0",True,BLACK)
            start_time = time.time()
            time_text = info_font.render("00:00.0",True,BLACK)
            if self.solver_mode:
                self.buttons.add(self.solve_button)

        while True:
            

            if not self.solver_mode and not finished:
                current_time = time.time()

                time_elapsed = current_time - start_time
                time_elapsed_minutes = int(time_elapsed//60)
                time_elapsed_seconds = time_elapsed - time_elapsed_minutes * 60

                time_text = info_font.render(f"{str(time_elapsed_minutes).zfill(2)}:{str(round(time_elapsed_seconds,1)).zfill(4)}",True,BLACK)



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if  event.type == pygame.MOUSEBUTTONDOWN:
                    point = pygame.mouse.get_pos()
                    x,y = point
                    
            
                    if self.back_button_rect.collidepoint(point):
                        return 'back'

                    if not finished and not self.solver_mode and  x <= self.board_size:
                        row,col = y//self.square_size,x//self.square_size

                        for neighbor_row,neighbor_col in ((row -1,col),(row + 1,col),(row,col -1),(row,col +1)):
                            if 0 <= neighbor_row < self.n and 0 <= neighbor_col < self.n and self.board[neighbor_row][neighbor_col] is None:
                                self.board[neighbor_row][neighbor_col],self.board[row][col] = self.board[row][col],self.board[neighbor_row][neighbor_col]
                                self.none_location = (row,col)
                                finished = self._check_finished()
                                if finished:
                                    game_win.play()
                                moves += 1
                                moves_text = info_font.render(f"MOVES: {moves}",True,BLACK)

                    else:
                        for i,button in enumerate(self.buttons):
                            if button.collided_on(point):
                                if i == 0:
                                    self._create_board()
                                    finished = False
                                    moves = 0
                                    moves_text = info_font.render("MOVES: 0",True,BLACK)
                                    start_time = time.time()
                                    time_text = info_font.render("00:00.0",True,BLACK)
                                    if self.solver_mode:
                                        self.buttons.add(self.solve_button)
                                elif i == 1:
                                    return
                                elif self.solver_mode and i == 2:
                                   self._get_custom_board() 
                                elif self.solver_mode and i == 3:
                                    solver = NPuzzleSolver(self.board)
                                    self.solve_button.kill()
                                    actions = solver.solve_ida()
                                    moves_text= self._animate_solve(actions)
                                    if moves_text == 'back':
                                        return moves_text
                                    if moves_text == "menu":
                                        return
                                    if moves_text == "reset":
                                        reset()
                                    else:
                                        finished = True




                if not finished and not self.solver_mode and event.type == pygame.KEYDOWN:
                    row,col = self.none_location
                    moved = False
                    if event.key == pygame.K_DOWN:

                        if row - 1 >= 0:
                            self.board[row][col],self.board[row -1][col] = self.board[row -1][col],self.board[row][col]
                            self.none_location = (row - 1,col)
                            moved = True
                    if event.key  == pygame.K_UP:
                        if row + 1 < self.n:
                            self.board[row][col],self.board[row +1][col] = self.board[row +1][col],self.board[row][col]
                            self.none_location = (row + 1,col)
                            moved = True
                    if event.key == pygame.K_RIGHT:
                        if col - 1 >= 0:
                            self.board[row][col],self.board[row][col - 1] = self.board[row][col - 1],self.board[row][col]
                            self.none_location = (row,col -1 )
                            moved = True
                    if event.key == pygame.K_LEFT:
                        if col + 1 < self.n:
                            self.board[row][col],self.board[row][col + 1] = self.board[row][col + 1],self.board[row][col]
                            self.none_location = (row,col +1 )
                            moved = True

                    if moved:
                        finished = self._check_finished()
                        if finished:
                            game_win.play()
                        moves += 1
                        moves_text = info_font.render(f"MOVES: {moves}",True,BLACK)








            point = pygame.mouse.get_pos()


            self.buttons.update(point)









            
            screen.fill(BGCOLOR)
            self._draw_board()
            screen.blit(moves_text,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - moves_text.get_width()//2,SCREEN_HEIGHT - 50))
            if not self.solver_mode:
                screen.blit(time_text,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - time_text.get_width()//2,SCREEN_HEIGHT - 100))
            if finished:
                screen.blit(win_text,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - win_text.get_width()//2,SCREEN_HEIGHT - 200 - win_text.get_height()))
            pygame.display.update()
            clock.tick(FPS)


    
    def _make_move(self,action,moves_text,action_text,action_text_arrow):
        

        empty_row,empty_col = self.none_location
        
        if action == 'L':
            #self.board[empty_row][empty_col] ,self.board[empty_row][empty_col +1] = self.board[empty_row][empty_col +1],self.board[empty_row][empty_col]
            target_row,target_col =  empty_row,empty_col + 1
            direction = vec(-1,0)

            self.none_location = (empty_row,empty_col + 1)
        elif action == 'R':
            #self.board[empty_row][empty_col] ,self.board[empty_row][empty_col -1] = self.board[empty_row][empty_col -1],self.board[empty_row][empty_col]
            direction = vec(1,0)
            self.none_location = (empty_row,empty_col - 1)
            target_row,target_col =  empty_row,empty_col - 1
        elif action == 'U':
            #self.board[empty_row][empty_col] ,self.board[empty_row + 1][empty_col] = self.board[empty_row + 1][empty_col],self.board[empty_row][empty_col]
            self.none_location = (empty_row + 1,empty_col)
            direction = vec(0,-1)
            target_row,target_col =  empty_row + 1,empty_col
        else:
            #self.board[empty_row][empty_col] ,self.board[empty_row - 1][empty_col] = self.board[empty_row - 1][empty_col],self.board[empty_row][empty_col]
            direction = vec(0,1)
            self.none_location = (empty_row - 1,empty_col)
            target_row,target_col =  empty_row - 1,empty_col

        

        tile = self.board[target_row][target_col]



        current_location = vec(target_col * self.square_size,target_row * self.square_size)

        start = vec(empty_col * self.square_size,empty_row * self.square_size)


        
    
        
        




        while start != current_location:


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    point = pygame.mouse.get_pos()
                    if self.back_button_rect.collidepoint(point):
                        return "back"
                    for i,button in enumerate(self.buttons):
                        if button.collided_on(point):
                            if i == 0:
                                return "reset"

                            elif i == 1:
                                return "menu"
        
            
            point = pygame.mouse.get_pos()

            self.buttons.update(point)

            current_location +=  1 * direction  
        

            screen.fill(BGCOLOR)
            self._draw_board(tile) 
            tile.draw(*current_location)
            pygame.draw.rect(screen,BLACK,(*current_location,self.square_size,self.square_size),1)


            screen.blit(moves_text,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - moves_text.get_width()//2,SCREEN_HEIGHT - 50))
            screen.blit(action_text,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - action_text.get_width()//2,SCREEN_HEIGHT - 200))
            screen.blit(action_text_arrow,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - action_text_arrow.get_width()//2,SCREEN_HEIGHT - 150))
            pygame.display.update()
            clock.tick(FPS * 3)

        
        self.board[empty_row][empty_col],self.board[target_row][target_col] = self.board[target_row][target_col],self.board[empty_row][empty_col]

    
    def _animate_solve(self,actions):
        


        moves = 0
        info_font = pygame.font.SysFont("calibri",50)
        moves_text = info_font.render(f"MOVES: {moves}",True,BLACK)
        

        start_time = time.time()

        actions_index =0
        action_mapping_to_text= {'U': 'UP','D': 'DOWN','L': 'LEFT','R': 'RIGHT'}
        action_mapping_to_arrow = {'U': u"\u2191",'D':u"\u2193",'L':u"\u2190" ,'R':u"\u2192"}
        action_text = info_font.render(f"{action_mapping_to_text[actions[actions_index]]}",True,BLACK)
        action_text_arrow = info_font.render(f"{action_mapping_to_arrow[actions[actions_index]]}",True,BLACK)
        


        while True:
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    point = pygame.mouse.get_pos()

                    if self.back_button_rect.collidepoint(point):
                        return "back"
                    for i,button in enumerate(self.buttons):
                        if button.collided_on(point):
                            if i == 0:
                                return "reset"

                            elif i == 1:
                                return "menu"
            
            
            point = pygame.mouse.get_pos()

            self.buttons.update(point)

            current_time = time.time()

            if current_time - start_time >= 2:
                moves += 1
                moves_text = info_font.render(f"MOVES: {moves}",True,BLACK)
                result = self._make_move(actions[actions_index],moves_text,action_text,action_text_arrow)
                if result in ("menu","reset","back"):
                    return result

                actions_index += 1

                if actions_index == len(actions):
                    self.solve_button.kill()
                    return moves_text

                action_text = info_font.render(f"{action_mapping_to_text[actions[actions_index]]}",True,BLACK)
                action_text_arrow = info_font.render(f"{action_mapping_to_arrow[actions[actions_index]]}",True,BLACK)
                start_time = current_time

            screen.fill(BGCOLOR)

            self._draw_board()

            screen.blit(moves_text,(self.board_size + (SCREEN_WIDTH - self.board_size)//2 - moves_text.get_width()//2,SCREEN_HEIGHT - 50))

            pygame.display.update()





    
    def _is_solvable(self):
        '''later on try to figure out how to do it using merge sort for O(nlogn) efficiency'''
        inversions = 0
        none_index = None
        for i in range(len(self.numbers) - 1):
            if self.numbers[i] is None:
                none_index = i
                continue


            for j in range(i + 1,len(self.numbers)):
                if self.numbers[j] is None:
                    continue
                if self.numbers[j] < self.numbers[i]:
                    inversions += 1

        
        if none_index is None:
            none_index = self.n**2 - 1
        
        n = self.n
        if n % 2 == 1:
            return inversions % 2 == 0
        else:
            empty_row = none_index // self.n

            from_bottom = self.n - empty_row

            if from_bottom % 2 == 0 and inversions % 2 == 1:
                return True

            if from_bottom % 2 == 1 and inversions % 2 == 0:
                return True


        return False




    

    def _check_finished(self):


        start_number = 1
        
        pprint(self.board)
        if self.board[self.n -1][self.n -1] is not None:
            return False

        for row in range(self.n):
            for col in range(self.n):
                if self.board[row][col] is None:
                    continue

                if self.board[row][col].number != start_number:
                    return False

                start_number += 1

        return True



    def _create_board(self):

        

        random.shuffle(self.numbers)
        
        goal = list(range(1,self.n**2))
        goal.append(None)
        while not self._is_solvable() or self.numbers == goal:
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
                tile = self.Tile(col * self.square_size,row * self.square_size,number,self.square_size,self.tile_font)
                new_row.append(tile)



            self.board.append(new_row)




def menu():
    

    pygame.mixer.music.load('mainmenu.ogg')
    pygame.mixer.music.play(-1)

    
    back_image = pygame.image.load('back.png').convert_alpha()
    back_image = pygame.transform.scale(back_image,(50,50))
    back_image_rect = back_image.get_rect(topleft=(0,0))
    def get_board_size():
        
    

        title_text = title_font.render("BOARD SIZE",True,BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2,top_gap + title_text.get_height()//2))
        
        flickering_event = pygame.USEREVENT + 1
        
        text = '|'
        last_text =  title_font.render(text,True,BLACK)
        pygame.time.set_timer(flickering_event,200)
        
        button_width = 600
        button_height = 100
        start_button = Button(SCREEN_WIDTH//2 - button_width//2,SCREEN_HEIGHT - top_gap - button_height,button_width,button_height,"START GAME",title_font)
        button = pygame.sprite.GroupSingle(start_button)


        invalid_text_1 = title_font.render("Please Enter A Value!",True,BLACK)
        invalid_text_2 = title_font.render("Size has to be >= 2!",True,BLACK)
        invalid_text_3 = title_font.render("Size has to be <= 50!",True,BLACK)


        
        def check_validity():
            nonlocal invalid_text,invalid_start_time
            if text != '|' and text != '':
                last = text[-1]

                if last == '|':
                    number = int(text[:-1])
                else:
                    number = int(text)

                if number <= 1:
                    invalid_text = invalid_text_2
                    invalid_start_time = time.time()
                elif number > 50:
                    invalid_text = invalid_text_3
                    invalid_start_time = time.time()
                else:                            
                    return number 
            else:
                invalid_text = invalid_text_1
                invalid_start_time = time.time()


        invalid_start_time = None
        invalid_text = None
        while True:
            
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == flickering_event:

                    if text:
                        last = text[-1]
                    else:
                        last = None

                    if last == '|':
                        text = text[:-1]
                    else:
                        text += '|'

                    last_text =  title_font.render(text,True,BLACK)
                elif event.type == pygame.KEYDOWN:
                    last = None
                    if text:
                        last = text[-1]
                    if pygame.K_0 <= event.key <= pygame.K_9:
                        number = chr(event.key)

                        last = None
                        if text:
                            last = text[-1]

                        if last == '|':
                            text = text[:-1] + number + '|'
                        else:
                            text += number


                        last_text =  title_font.render(text,True,BLACK)
                    elif event.key == pygame.K_BACKSPACE:


                        if last == '|':
                            text = text[:-2]
                        elif text:
                            text = text[:-1]


                        last_text =  title_font.render(text,True,BLACK)
                    elif event.key == pygame.K_RETURN:
                        n = check_validity()
                        if n:
                            return n
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    point = pygame.mouse.get_pos()

                    if button.sprite.collided_on(point):
                        n = check_validity()
                        if n:
                            return n
                    elif back_image_rect.collidepoint(point):
                        return 


            

            if invalid_start_time:
                if current_time - invalid_start_time >= 1:
                    invalid_start_time = None







            point = pygame.mouse.get_pos()

            button.update(point)
            '''            
            on_back_button = back_image_rect.collidepoint(point)

            if on_back_button:
                image = back_image_bigger
            else:
                image = back_image
            '''



            screen.fill(BGCOLOR)
            screen.blit(title_text,title_rect)
            if text and text[-1] == '|':
                text_one_less = title_font.render(text[:-1],True,BLACK)
                width = text_one_less.get_width()//2
            else:
                width = last_text.get_width()//2

            button.draw(screen)

            screen.blit(last_text,(SCREEN_WIDTH//2 - width,SCREEN_HEIGHT//2 - last_text.get_height()//2))
            if invalid_start_time:
                screen.blit(invalid_text,(SCREEN_WIDTH//2 - invalid_text.get_width()//2,SCREEN_HEIGHT -  top_gap-button_height - invalid_text.get_height()))

        
            screen.blit(back_image,(0,0))

            pygame.display.update()





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
                        solver_mode = False
                        n = get_board_size()
                        if n is None:
                            break
                        if i == 1:
                            solver_mode = True


                            
                        result = NPuzzle(n,solver_mode)._play_game()

                        while result == 'back':
                            pygame.mixer.music.load('mainmenu.ogg')
                            pygame.mixer.music.play(-1)
                            pygame.display.set_caption("N-Puzzle")
                            n = get_board_size()
                            if n is None:
                                break
                            result = NPuzzle(n,solver_mode)._play_game()


                        pygame.mixer.music.load('mainmenu.ogg')
                        pygame.mixer.music.play(-1)
                        pygame.display.set_caption("N-Puzzle")


        point = pygame.mouse.get_pos() 
        buttons.update(point)

        screen.fill(BGCOLOR)

        buttons.draw(screen)
        screen.blit(title_text,title_rect)

        pygame.display.update()


class NPuzzleSolver:
    


    class State:

        def __init__(self,board,distance=0,action=None,previous_state=None):
            self.board = board
            self.distance = distance
            self.action = action
            self.previous_state = previous_state


        @property
        def heuristic(self):
            return self.board.heuristic


        @property
        def tiles(self):
            return self.board.tiles

        

        def __lt__(self,other): 

            if isinstance(other,NPuzzleSolver.State):
                return self.distance + self.heuristic <= other.distance + other.heuristic



    class Board:


        def __init__(self,tiles):

            self.n = int(math.sqrt(len(tiles)))
            self.tiles = tiles
            self.empty_index = self.tiles.index(None)

            self._calculate_heuristic()
        
        def _manhattan_distance(self,a,b):


            a_row,b_row = a//self.n,b//self.n
            a_col,b_col = a % self.n,b % self.n

            return abs(a_row - b_row) + abs(a_col - b_col)




        def _calculate_heuristic(self):


            total = 0


            for i,number in enumerate(self.tiles):
                if number is None:
                    continue

                total += self._manhattan_distance(i,number -1)

            
            self.heuristic = total
        

        def _swap(self,i,j):

            tiles = self.tiles.copy()

            tiles[i],tiles[j] = tiles[j],tiles[i]

            return tiles
        
        def get_successors(self):


            successors = []

            empty_index = self.empty_index
            empty_row,empty_col = self.empty_index//self.n,self.empty_index % self.n


            if empty_row > 0:
                successor = NPuzzleSolver.Board(self._swap(empty_index,empty_index- self.n))
                successors.append((successor,'D'))

            if empty_row < self.n - 1:
                successor = NPuzzleSolver.Board(self._swap(empty_index,empty_index+ self.n))
                successors.append((successor,'U'))


            if empty_col > 0:
                successor = NPuzzleSolver.Board(self._swap(empty_index,empty_index - 1))
                successors.append((successor,'R'))


            if empty_col < self.n - 1:
                successor = NPuzzleSolver.Board(self._swap(empty_index,empty_index + 1))
                successors.append((successor,'L'))


            return successors







    def __init__(self,board):


        self.tiles = []

        self.n = len(board)

        
        for row in board:
            for tile in row:
                if tile is None:
                    self.tiles.append(tile)
                else:
                    self.tiles.append(tile.number)
        
        print(self.tiles)
        self.goal_state = list(range(1,self.n**2))
        self.goal_state.append(None)

    


    def solve_ida(self):

        start_board =self.Board(self.tiles)
        start_state = self.State(start_board)

        threshold = start_state.heuristic
        print(threshold)


        def search(state,threshold,visited):
            

            heuristic = state.distance + state.heuristic
            if heuristic > threshold:
                return heuristic,None

            if state.tiles == self.goal_state:
                return "FOUND",state

            minimum = float("inf")


            for successor,action in state.board.get_successors():
                tiles = tuple(successor.tiles)
                if tiles not in visited:
                    visited.add(tiles)
                    next_state = self.State(successor,state.distance+ 1,action,state)
                    result,end_state = search(next_state,threshold,visited)

                    if result == 'FOUND':
                        return 'FOUND',end_state

                    if result < minimum:
                        minimum = result

                    visited.remove(tiles)
            

            return minimum,None




        while True:
            visited = {tuple(start_board.tiles)}
            result,end_state = search(start_state,threshold,visited)

            if result == 'FOUND':
                break

            threshold = result 


        actions = []
        current_state = end_state
        while current_state:
            actions.append(current_state.action)
            current_state = current_state.previous_state

        

        actions.pop()

        actions.reverse()

        return actions





    















    def solve(self):
        start_board = self.Board(self.tiles)
        start_state = self.State(start_board)

        states = []

        heapq.heappush(states,start_state)


        visited = set()

        visited.add(tuple(start_board.tiles))


        while states:
            current_state = heapq.heappop(states)

            if current_state.tiles == self.goal_state:
                break



            for successor,action in current_state.board.get_successors():
                successor_tiles = tuple(successor.tiles)
                if successor_tiles not in visited:
                    visited.add(tuple(successor_tiles))
                    next_state = self.State(successor,current_state.distance+ 1,action,current_state)
                    heapq.heappush(states,next_state)


        actions = []
        while current_state:
            actions.append(current_state.action)
            current_state = current_state.previous_state

        

        actions.pop()

        actions.reverse()

        return actions












if __name__ == "__main__":
    
    menu()









