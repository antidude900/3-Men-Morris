# MODULES
import pygame, sys,socket,threading,time


# initializes pygame
pygame.init()
pygame.font.init()

# ---------
# CONSTANTS
# ---------

WIDTH, HEIGHT = 690, 690
LINE_WIDTH = 15
org_x,org_y=55,55
des_x,des_y=0,0
inc_x,inc_y=242,245
org_x_centre,org_y_centre=100,100
x_centres,y_centres=[100,340,580],[100,340,580]
radius=60
dist=240 #all the centres of whose we are seeing distance are in the same level(y-cord).So only see the x_direction distance will show the distance between the centres
BOARD_ROWS = 3
BOARD_COLS = 3

# rgb: red green blue
RED = (255, 0, 0)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# ------
# IMAGES,FONTS
# ------
game_board=pygame.image.load('assets/brd.png')
game_board=pygame.transform.scale(game_board,(WIDTH,HEIGHT))

eraser=pygame.image.load('assets/eraser.png')
eraser= pygame.transform.scale(eraser, (90,90))

sharpner=pygame.image.load('assets/sharpner.png')
sharpner= pygame.transform.scale(sharpner, (90,90))

title=pygame.image.load('assets/title.png')
title= pygame.transform.scale(title, (90,90))

tutorial=pygame.image.load('assets/tutorial.png')
tutorial= pygame.transform.scale(tutorial, (90,90))

about=pygame.image.load('assets/about.png')
about= pygame.transform.scale(about, (90,90))

font1 =pygame.font.Font('freesansbold.ttf',20)
font2=pygame.font.Font('freesansbold.ttf',42)
gui_font = pygame.font.Font(None, 30)

# ---------
# VARIABLES
# ---------
player = 1
turn=None
start_game=False
game_over = False
selected=False
valid=False
wrong_select=False
played=0
eraser_won_times=0
sharpner_won_times=0
connected=False


# ------
# SCREEN
# ------
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption( '3 Men Morris' )

# -------------
# CONSOLE BOARD
# -------------
board = [[  0  ,  0  ,  0  ],
         [  0  ,  0  ,  0  ],
         [  0  ,  0  ,  0  ]]

# ---------
# FUNCTIONS
# ---------
def click_valid(x,y):
    row,col=None,None
    for row in range(3):
        for col in range(3):
            if x_centres[col]-radius<x<x_centres[col]+radius and y_centres[row]-radius<y<y_centres[row]+radius and available_square(row,col):
                mark_square(row,col,player)
                return True,row,col

    return False,row,col

def location(row,col):
    x_step_far = (x_centres[col] - org_x_centre) / dist     #how much step far is the inital circle from the destionation circle in x_direction
    y_step_far = (y_centres[row] - org_y_centre) / dist     #how much step far is the inital circle from the destionation circle in y_direction
    des_x=org_x+inc_x*x_step_far     #taking the inital cordinate that is in initial circle to final circle in x direction
    des_y=org_y+inc_y*y_step_far     #taking the inital cordinate that is in initial circle to final circle in u direction

    return des_x,des_y

def select(x,y,selected):
    prev_row,prev_col,wrong_select=None,None,False
    for row in range(3):
        for col in range(3):
            if x_centres[col]-radius<x<x_centres[col]+radius and y_centres[row]-radius<y<y_centres[row]+radius:
                if not available_square(row,col):
                    if board[row][col]==player:
                        prev_row,prev_col=row,col
                        board[row][col]=0
                        selected=True
                        valid=True
                        wrong_select=False
                        break
                    else:
                        valid=False
                        wrong_select=True
                else:
                    valid=False
                    return prev_row,prev_col,selected,valid,wrong_select 

    return prev_row,prev_col,selected,valid,wrong_select

def move(x,y,prev_row,prev_col):
    selected,valid=True,False
    row,col=valid_click_for_move(x,y)
    if available_square(row,col):
        if  prev_row- row in [1, -1, 0] and prev_col - col in [1, -1, 0]:
            if prev_row- row in [1, -1] and prev_col - col in [1, -1]:
                if (row == col == 1) or (prev_row == prev_col == 1):
                    board[row][col]=player
                    selected,valid=False,True
            else:
                if prev_row == row and prev_col == col:
                    valid=False
                else:
                    board[row][col]=player
                    selected,valid=False,True
    else:
        if board[row][col]==player:
            board[prev_row][prev_col]=player
            prev_row,prev_col=row,col
            board[row][col]=0
            valid=True
    return prev_row,prev_col,valid,selected

def valid_click_for_move(x,y):
    row,col=None,None
    for row in range(3):
        for col in range(3):
            if x_centres[col]-radius<x<x_centres[col]+radius and y_centres[row]-radius<y<y_centres[row]+radius:
                return row,col

    return row,col

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                screen.blit(eraser,location(row,col))
            elif board[row][col] == 2:
                screen.blit(sharpner,location(row,col))

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] == 0

def is_board_full():
    eraser=0
    sharpner=0
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                eraser+=1
            if board[row][col] == 2:
                sharpner+=1
    if eraser == 3 and sharpner == 3:
        return True

    return False


def check_win(player):
    # vertical win check
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            return True

    # horizontal win check
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            return True

    # asc diagonal win check
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        return True

    # desc diagonal win chek
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True

    return False


def restart():
    global player,game_over,selected,valid,wrong_select
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0
    player = 1
    game_over = False
    selected=False
    valid=False
    wrong_select=False 

def close_connection():
    if connected==True:
        client.close()

# ---------
# Multiplayer
# ---------

# Connecting To Server
def multiplayer():
    global client,connected
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5555))
    connected=True

    def receive():
        global board,player,turn,start_game,game_over
        while True:
            try:
                # Receive Message From Server
                message = eval(client.recv(4096).decode('utf-8'))            
        
                if message[0] == 'turn':
                    turn=message[1]
                    if turn==2:
                        client.send(str(['Start',True]).encode())
        
                elif message[0] == 'Start':
                    start_game=message[1]
        
                elif message[0] == 'board':
                    board=message[2]
                    if message[1]!=turn:
                        player = player % 2 + 1
    
                elif message[0] == 'win':
                    board=message[2]
                    game_over=True
                     
                elif message[0]=='left':
                    print(message[1])
        
                else:
                    print(message)
            except:
                # Close Connection When Error
                print("An error occured!")
                client.close()
                break
        
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()


# ---------
# GUI
# ---------
class Button:
    def __init__(self,text,width,height,pos,elevation):
        #Core attributes
        self.not_running=True
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'
        #text
        self.text_surf = gui_font.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self,screen):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(screen,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(screen,self.top_color, self.top_rect,border_radius = 12)
        screen.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#475F77'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    self.not_running=False
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#D74B4B'

def start_scene(screen):
    title=pygame.image.load('assets/title.PNG')
    on_start_scene=True
    clock = pygame.time.Clock()

    button1 = Button('Start', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 80), 5)
    button2 = Button('Tutorial', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 140), 5)
    button3 = Button('About', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 200), 5)
    button4 = Button('Quit', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 260), 5)

    while on_start_scene:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_connection()
                sys.exit()

        screen.fill('#DCDDD8')
        screen.blit(title,(40,200))
        button1.draw(screen)
        button2.draw(screen)
        button3.draw(screen)
        button4.draw(screen)

        if button1.not_running==False:
            on_start_scene = False
            multiplayer()
        elif button2.not_running == False:
            tutorial_scene(screen)
            button2.not_running = True
        elif button3.not_running == False:
            about_scene(screen)
            button3.not_running = True
        elif button4.not_running == False:
            close_connection()
            sys.exit()


        pygame.display.update()
        clock.tick(60)

def tutorial_scene(screen,on_tutorial_scene=True):
    tutorial=pygame.image.load('assets/tutorial.png')
    button5=Button('Back', 100, 40, (530 , 640), 5)
    while on_tutorial_scene:
        screen.blit(tutorial,(0,0))
        button5.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_connection()
                sys.exit()
        pygame.display.update()
        on_tutorial_scene = button5.not_running

########################################################################################################################

def about_scene(screen,on_about_scene=True):
    about=pygame.image.load('assets/about.png')
    button5=Button('Back', 100, 40, (530 , 640), 5)
    while on_about_scene:
        screen.blit(about,(0,0))
        button5.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_connection()
                sys.exit()
        pygame.display.update()
        on_about_scene = button5.not_running

########################################################################################################################

def win_scene(screen):
    global played,eraser_won_times,sharpner_won_times

    if check_win(1):
        player=1
        eraser_won_times+=1
    else:
        player=2
        sharpner_won_times+=1

    win=True
    if played < 3:
        if eraser_won_times- sharpner_won_times in [-1,1,0]:
            msg1 = f"{'Eraser' if player==1 else 'Sharpner' } won Round {played+1}!"
            msg2 = f'Next Round: Round {played+2}'
            played+=1

        else:
            played=3
    if played == 3:
        msg1 = f"{'Eraser' if eraser_won_times>sharpner_won_times else 'Sharpner' } is the ultimate winner!"
        msg2=f"{'Eraser' if eraser_won_times<sharpner_won_times else 'Sharpner' } You suck!!!!!!!!!!!!!!!!!!!!!!!!!"

    button2 = Button('Continue!', 300, 40, ((WIDTH / 2) - 150, (HEIGHT/2)+80), 5)
    button3 = Button('Play again (For true gamers)', 300, 40, (30, (HEIGHT/2)+80), 5)
    button4=  Button('Exit (If you are a loser)', 300, 40, (360, (HEIGHT/2)+80), 5)
    while win:
        screen.fill((255,255,255))
        if played<3:
            button2.draw(screen)
            if button2.not_running==False:
                restart()
                if turn==2:
                    client.send(str(['Start',True]).encode())
                win=False
        else:
            button3.draw(screen)
            button4.draw(screen)
            if button3.not_running==False:
                restart()
                if turn==2:
                    client.send(str(['Start',True]).encode())
                eraser_won_times,sharpner_won_times,played=0,0,0
                win=False
            elif button4.not_running==False:
                close_connection()
                sys.exit()

        textobj = font2.render(msg1, True, (0, 0, 0))
        text_rect = textobj.get_rect(center=(WIDTH / 2, HEIGHT / 2))

        textobj2 = font1.render(msg2, True, (0, 0, 0))
        text_rect2 = textobj2.get_rect(center=(WIDTH/2, (HEIGHT / 2)+40))

        screen.blit(textobj, text_rect)
        screen.blit(textobj2, text_rect2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_connection()
                sys.exit()
        pygame.display.update()



# --------
# MAINLOOP
# --------
start_scene(screen)
while True:
    screen.blit(game_board, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            close_connection()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and player == turn and start_game:
            x, y = pygame.mouse.get_pos()

            if selected == False:
                if not is_board_full():
                    valid,row,col=click_valid(x,y)

                else:
                    prev_row,prev_col,selected,valid,wrong_select=select(x, y,selected)
            else:
                prev_row,prev_col,valid,selected=move(x, y, prev_row,prev_col)


            if valid == True and selected == False:
                if check_win(player):
                    game_over=True
                    client.send(str(['win',game_over,board]).encode())
                else:
                    client.send(str(['board',turn,board]).encode())
                player = player % 2 + 1

            if valid == False:
                textobj = font1.render('Invalid Move!', True, (0,0,0))
                text_rect = textobj.get_rect(center=(WIDTH / 2, 30))
                screen.blit(textobj, text_rect)
                
            if wrong_select == True:
                score3 = font1.render(f"{'Eraser' if player == 1 else 'Sharpner' }'s turn!", True, (0, 0, 0))
                text_rect = score3.get_rect(center=((WIDTH / 2) + 10, 670))
                screen.blit(score3, text_rect)

    score1 = font1.render(f'Eraser: {eraser_won_times}', True, (0, 0, 0))
    screen.blit(score1, (30,10))

    score2 = font1.render(f'Sharpner: {sharpner_won_times}', True, (0, 0, 0))
    screen.blit(score2, (550,10))

    draw_figures()   
    pygame.display.update()
    if game_over:
        time.sleep(0.2)
        start_game=False
        win_scene(screen)
            
