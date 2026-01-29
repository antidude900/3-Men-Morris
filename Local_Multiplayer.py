# Local Multiplayer Mode - Network play between two devices
from game_core import *
import socket
import threading


# ------
# SCREEN
# ------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('3 Men Morris - Local Multiplayer')

# ---------
# MULTIPLAYER SPECIFIC VARIABLES
# ---------
player = 1
turn = None
start_game = False
game_over = False
selected = False
valid = False
wrong_select = False
played = 0
eraser_won_times = 0
sharpner_won_times = 0
connected = False
left = False
clients = []
prev_row, prev_col = None, None


def restart():
    global player, game_over, selected, valid, wrong_select
    restart_board()
    player = 1
    game_over = False
    selected = False
    valid = False
    wrong_select = False


def close_connection():
    if turn == 1:
        for clnt in clients:
            clnt.close()
        server.close()
    else:
        client.close()


def send(msg):
    if turn == 1:
        for clnt in clients:
            clnt.send(msg)
    else:
        client.send(msg)


# ---------
# Multiplayer-specific game functions (different from game_core)
# ---------
def select_multiplayer(x, y, selected, current_player):
    """Multiplayer version - clears the board position instead of using selected state"""
    prev_row, prev_col, wrong_select, valid = None, None, False, False
    for row in range(3):
        for col in range(3):
            if x_centres[col] - radius < x < x_centres[col] + radius and y_centres[row] - radius < y < y_centres[row] + radius:
                if not available_square(row, col):
                    if board[row][col] == current_player:
                        prev_row, prev_col = row, col
                        board[row][col] = 0  # Clear the position for multiplayer sync
                        selected = True
                        valid = True
                        wrong_select = False
                        break
                    else:
                        valid = False
                        wrong_select = True
                else:
                    valid = False
                    return prev_row, prev_col, selected, valid, wrong_select

    return prev_row, prev_col, selected, valid, wrong_select


def move_multiplayer(x, y, prev_row, prev_col, current_player):
    """Multiplayer version - handles piece movement without selected visual state"""
    selected, valid = True, False
    row, col = valid_click_for_move(x, y)
    if available_square(row, col):
        if prev_row - row in [1, -1, 0] and prev_col - col in [1, -1, 0]:
            if prev_row - row in [1, -1] and prev_col - col in [1, -1]:
                if (row == col == 1) or (prev_row == prev_col == 1):
                    board[row][col] = current_player
                    selected, valid = False, True
            else:
                if prev_row == row and prev_col == col:
                    valid = False
                else:
                    board[row][col] = current_player
                    selected, valid = False, True
    else:
        if board[row][col] == current_player:
            board[prev_row][prev_col] = current_player
            prev_row, prev_col = row, col
            board[row][col] = 0  # Clear the position for multiplayer sync
            valid = True
    return prev_row, prev_col, valid, selected


# ---------
# Multiplayer Network Functions
# ---------
def is_server():
    global client
    server = False
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5555))
    except:
        server = True
    return server

#for clients
def client_run():
    global client, turn
    turn = 2

    def receive():
        global board, player, start_game, game_over, left
        while True:
            try:
                # Receive Message From Server
                message = eval(client.recv(4096).decode('utf-8'))
                
                if message[0] == 'turn':
                    client.send(str(['Start', True]).encode())
                    start_game = True
        
                elif message[0] == 'board':
                    board = message[2]
                    if message[1] != turn:
                        player = player % 2 + 1
    
                elif message[0] == 'win':
                    board = message[2]
                    game_over = True
                     
                elif message[0] == 'left':
                    print(message[1])
        
                else:
                    print(message)
            except:
                # Close Connection When Error
                print("Server closed")
                left = True
                client.close()
                break
        
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

#for servers
def server_run():
    global server, turn
    turn = 1

    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(1)
    
    # Handling Messages From Clients
    def handle(client):
        global board, player, start_game, game_over, left
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(4096)
                message = eval(message.decode('utf-8'))
    
                if message[0] == 'Start':
                    start_game = message[1]

                elif message[0] == 'board':
                    board = message[2]
                    if message[1] != turn:
                        player = player % 2 + 1

                elif message[0] == 'win':
                    board = message[2]
                    game_over = True
                     
                elif message[0] == 'left':
                    print(message[1])
                else:
                    print(message)
                
            except:
                # Removing And Closing Clients
                print("Client Left")
                index = clients.index(client)
                clients.remove(client)
                client.close()
                left = True
                break
    
    # Receiving / Listening Function
    def receive():
        global clients
        while len(clients) < 1:
            try:
                # Accept Connection
                client, address = server.accept()
    
                print("Connected with {}".format(str(client)))
        
                # Request And Store Nickname
                clients.append(client)
        
                # Giving its turn
                client.send(str(['turn', 2]).encode())
        
                # Start Handling Thread For Client
                thread = threading.Thread(target=handle, args=(client,))
                thread.start()
            except:
                break
    print("Server is listening......")
    thread = threading.Thread(target=receive)
    thread.start()



# Custom start_scene for multiplayer (overrides game_core version)
def multiplayer_start_scene(screen):
    title_img = pygame.image.load('assets/title.PNG')
    on_start_scene = True
    clock = pygame.time.Clock()

    button1 = Button('Start', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 80), 5)
    button2 = Button('Tutorial', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 140), 5)
    button3 = Button('About', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 200), 5)
    button4 = Button('Quit', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 260), 5)

    while on_start_scene:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill('#DCDDD8')
        screen.blit(title_img, (40, 200))
        button1.draw(screen)
        button2.draw(screen)
        button3.draw(screen)
        button4.draw(screen)

        if button1.not_running == False:
            on_start_scene = False
            if is_server():
                server_run()
            else:
                client_run()

        elif button2.not_running == False:
            tutorial_scene(screen)
            button2.not_running = True
        elif button3.not_running == False:
            about_scene(screen)
            button3.not_running = True
        elif button4.not_running == False:
            sys.exit()

        pygame.display.update()
        clock.tick(60)



def win_scene(screen):
    global played, eraser_won_times, sharpner_won_times, start_game

    if check_win(1):
        winner_player = 1
        eraser_won_times += 1
    else:
        winner_player = 2
        sharpner_won_times += 1

    win = True
    if played < 3:
        if eraser_won_times - sharpner_won_times in [-1, 1, 0]:
            msg1 = f"{'Eraser' if winner_player == 1 else 'Sharpner'} won Round {played + 1}!"
            msg2 = f'Next Round: Round {played + 2}'
            played += 1
        else:
            played = 3
    if played == 3:
        msg1 = f"{'Eraser' if eraser_won_times > sharpner_won_times else 'Sharpner'} is the ultimate winner!"
        msg2 = f"{'Eraser' if eraser_won_times < sharpner_won_times else 'Sharpner'} You suck!!!!!!!!!!!!!!!!!!!!!!!!!"

    button2 = Button('Continue!', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 80), 5)
    button3 = Button('Play again (For true gamers)', 300, 40, (30, (HEIGHT / 2) + 80), 5)
    button4 = Button('Exit (If you are a loser)', 300, 40, (360, (HEIGHT / 2) + 80), 5)
    while win:
        screen.fill((255, 255, 255))
        if played < 3:
            button2.draw(screen)
            if button2.not_running == False:
                restart()
                if turn == 2:
                    send(str(['Start', True]).encode())
                    start_game = True
                win = False
        else:
            button3.draw(screen)
            button4.draw(screen)
            if button3.not_running == False:
                restart()
                if turn == 2:
                    send(str(['Start', True]).encode())
                    start_game = True
                eraser_won_times, sharpner_won_times, played = 0, 0, 0
                win = False
            elif button4.not_running == False:
                close_connection()
                sys.exit()

        textobj = font2.render(msg1, True, (0, 0, 0))
        text_rect = textobj.get_rect(center=(WIDTH / 2, HEIGHT / 2))

        textobj2 = font1.render(msg2, True, (0, 0, 0))
        text_rect2 = textobj2.get_rect(center=(WIDTH / 2, (HEIGHT / 2) + 40))

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
# --------
# MAINLOOP
# --------
multiplayer_start_scene(screen)
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
                    valid, row, col = click_valid(x, y, player)
                else:
                    prev_row, prev_col, selected, valid, wrong_select = select_multiplayer(x, y, selected, player)
            else:
                prev_row, prev_col, valid, selected = move_multiplayer(x, y, prev_row, prev_col, player)

            if valid == True and selected == False:
                if check_win(player):
                    game_over = True
                    send(str(['win', game_over, board]).encode())
                else:
                    send(str(['board', turn, board]).encode())
                player = player % 2 + 1

            if valid == False:
                textobj = font1.render('Invalid Move!', True, (0, 0, 0))
                text_rect = textobj.get_rect(center=(WIDTH / 2, 30))
                screen.blit(textobj, text_rect)
                
            if wrong_select == True:
                score3 = font1.render(f"{'Eraser' if player == 1 else 'Sharpner'}'s turn!", True, (0, 0, 0))
                text_rect = score3.get_rect(center=((WIDTH / 2) + 10, 670))
                screen.blit(score3, text_rect)

    draw_figures(screen)
    pygame.display.update()
    if left:
        sys.exit()

    if game_over:
        start_game = False
        time.sleep(0.2)
        win_scene(screen)
            



