# MODULES
import pygame, sys, time
import math

# initializes pygame
pygame.init()
pygame.font.init()

# ---------
# CONSTANTS
# ---------

WIDTH, HEIGHT = 690, 690
LINE_WIDTH = 15
org_x, org_y = 55, 55
des_x, des_y = 0, 0
inc_x, inc_y = 242, 245
org_x_centre, org_y_centre = 100, 100
x_centres, y_centres = [100, 340, 580], [100, 340, 580]
radius = 69
dist = 240  # all the centres of whose we are seeing distance are in the same level(y-cord).So only see the x_direction distance will show the distance between the centres
BOARD_ROWS = 3
BOARD_COLS = 3
error_start_time = 0
show_error_type = None
ERROR_DISPLAY_DURATION = 250

# rgb: red green blue
RED = (255, 0, 0)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# AI constants
HUMAN = 1
AI = 2
MAX_DEPTH = 5  # Limit depth for performance

# ------
# IMAGES,FONTS
# ------
def image_loader(path, width, height):
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, (width, height))
    return img


game_board = image_loader('assets/brd2.png', WIDTH, HEIGHT)
eraser = image_loader('assets/eraser.png', 90, 90)
eraser_selected = image_loader('assets/eraser_selected.png', 90, 90)
sharpner = image_loader('assets/sharpner.png', 90, 90)
sharpner_selected = image_loader('assets/sharpner_selected.png', 90, 90)
title = image_loader('assets/title.png', 90, 90)
tutorial = image_loader('assets/tutorial.png', 90, 90)
about = image_loader('assets/about.png', 90, 90)

font1 = pygame.font.Font('freesansbold.ttf', 20)
font2 = pygame.font.Font('freesansbold.ttf', 42)
gui_font = pygame.font.Font(None, 30)

# ------
# SCREEN
# ------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('3 Men Morris - AI Mode')

# -------------
# CONSOLE BOARD
# -------------
board = [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]

# ---------
# FUNCTIONS
# ---------
def click_valid(x, y):
    row, col = None, None
    for row in range(3):
        for col in range(3):
            if x_centres[col] - radius < x < x_centres[col] + radius and y_centres[row] - radius < y < y_centres[row] + radius and available_square(row, col):
                mark_square(row, col, player)
                return True, row, col

    return False, row, col


def location(row, col):
    x_step_far = (x_centres[col] - org_x_centre) / dist  # how much step far is the inital circle from the destionation circle in x_direction
    y_step_far = (y_centres[row] - org_y_centre) / dist  # how much step far is the inital circle from the destionation circle in y_direction
    des_x = org_x + inc_x * x_step_far  # taking the inital cordinate that is in initial circle to final circle in x direction
    des_y = org_y + inc_y * y_step_far  # taking the inital cordinate that is in initial circle to final circle in u direction

    return des_x, des_y


def select(x, y, selected):
    prev_row, prev_col, wrong_select, valid = None, None, False, False
    for row in range(3):
        for col in range(3):
            if x_centres[col] - radius < x < x_centres[col] + radius and y_centres[row] - radius < y < y_centres[row] + radius:
                if not available_square(row, col):
                    if board[row][col] == player:
                        prev_row, prev_col = row, col
                        board[row][col] = 1.5 if player == 1 else 2.5
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


def move(x, y, prev_row, prev_col):
    selected, valid = True, False
    row, col = valid_click_for_move(x, y)
    if available_square(row, col):
        if prev_row - row in [1, -1, 0] and prev_col - col in [1, -1, 0]:
            if prev_row - row in [1, -1] and prev_col - col in [1, -1]:
                if (row == col == 1) or (prev_row == prev_col == 1):
                    board[row][col] = player
                    selected, valid = False, True
            else:
                if prev_row == row and prev_col == col:
                    valid = False
                else:
                    board[row][col] = player
                    selected, valid = False, True
    else:
        if board[row][col] == player:
            board[prev_row][prev_col] = player
            prev_row, prev_col = row, col
            board[row][col] = 1.5 if player == 1 else 2.5
            valid = True
    return prev_row, prev_col, valid, selected


def valid_click_for_move(x, y):
    row, col = None, None
    for row in range(3):
        for col in range(3):
            if x_centres[col] - radius < x < x_centres[col] + radius and y_centres[row] - radius < y < y_centres[row] + radius:
                return row, col

    return row, col


def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                screen.blit(eraser, location(row, col))
            elif board[row][col] == 2:
                screen.blit(sharpner, location(row, col))
            elif board[row][col] == 1.5:
                screen.blit(eraser_selected, location(row, col))
            elif board[row][col] == 2.5:
                screen.blit(sharpner_selected, location(row, col))


def mark_square(row, col, player):
    board[row][col] = player


def available_square(row, col):
    return board[row][col] == 0


def is_board_full():
    eraser = 0
    sharpner = 0
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                eraser += 1
            if board[row][col] == 2:
                sharpner += 1
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
    global player, game_over, selected, valid, wrong_select
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0
    player = 1
    game_over = False
    selected = False
    valid = False
    wrong_select = False

# ---------
# AI FUNCTIONS - MINIMAX ALGORITHM
# ---------

def get_board_copy():
    """Create a deep copy of the board"""
    return [row[:] for row in board]


def set_board(board_copy):
    """Set the board to a specific state"""
    for i in range(3):
        for j in range(3):
            board[i][j] = board_copy[i][j]


def count_pieces(player_num):
    """Count how many pieces a player has on the board"""
    count = 0
    for row in range(3):
        for col in range(3):
            if board[row][col] == player_num:
                count += 1
    return count


def get_available_moves(player_num):
    """Get all available moves for the current player"""
    moves = []
    
    # If player hasn't placed all 3 pieces yet
    if count_pieces(player_num) < 3:
        for row in range(3):
            for col in range(3):
                if available_square(row, col):
                    moves.append(('place', row, col))
    else:
        # Movement phase - find all possible moves
        for from_row in range(3):
            for from_col in range(3):
                if board[from_row][from_col] == player_num:
                    # Try all adjacent positions
                    for to_row in range(3):
                        for to_col in range(3):
                            if available_square(to_row, to_col):
                                # Check if move is valid (adjacent)
                                if from_row - to_row in [1, -1, 0] and from_col - to_col in [1, -1, 0]:
                                    # Check diagonal restrictions
                                    if from_row - to_row in [1, -1] and from_col - to_col in [1, -1]:
                                        if (to_row == to_col == 1) or (from_row == from_col == 1):
                                            moves.append(('move', from_row, from_col, to_row, to_col))
                                    else:
                                        if not (from_row == to_row and from_col == to_col):
                                            moves.append(('move', from_row, from_col, to_row, to_col))
    
    return moves


def apply_move(move, player_num):
    """Apply a move to the board"""
    if move[0] == 'place':
        _, row, col = move
        board[row][col] = player_num
    else:  # move
        _, from_row, from_col, to_row, to_col = move
        board[from_row][from_col] = 0
        board[to_row][to_col] = player_num


def undo_move(move, player_num):
    """Undo a move from the board"""
    if move[0] == 'place':
        _, row, col = move
        board[row][col] = 0
    else:  # move
        _, from_row, from_col, to_row, to_col = move
        board[to_row][to_col] = 0
        board[from_row][from_col] = player_num


def evaluate_board():
    """Evaluate the board state - positive favors AI, negative favors human"""
    if check_win(AI):
        return 10000
    if check_win(HUMAN):
        return -10000
    
    score = 0
    
    # Check potential winning lines - CRITICAL for blocking!
    ai_threats = count_two_in_row(AI)
    human_threats = count_two_in_row(HUMAN)
    
    # Blocking opponent's winning moves is crucial
    score += ai_threats * 50
    score -= human_threats * 60  # Blocking is more important than attacking
    
    # Center control bonus (center is strategic)
    if board[1][1] == AI:
        score += 15
    elif board[1][1] == HUMAN:
        score -= 15
    
    # Corner control
    corners = [(0,0), (0,2), (2,0), (2,2)]
    for r, c in corners:
        if board[r][c] == AI:
            score += 8
        elif board[r][c] == HUMAN:
            score -= 8
    
    return score


def count_two_in_row(player):
    """Count how many lines have 2 pieces of the player and one empty"""
    count = 0
    
    # Check rows
    for row in range(3):
        line = [board[row][0], board[row][1], board[row][2]]
        if line.count(player) == 2 and line.count(0) == 1:
            count += 1
    
    # Check columns
    for col in range(3):
        line = [board[0][col], board[1][col], board[2][col]]
        if line.count(player) == 2 and line.count(0) == 1:
            count += 1
    
    # Check diagonals
    line1 = [board[0][0], board[1][1], board[2][2]]
    line2 = [board[2][0], board[1][1], board[0][2]]
    
    if line1.count(player) == 2 and line1.count(0) == 1:
        count += 1
    if line2.count(player) == 2 and line2.count(0) == 1:
        count += 1
    
    return count


def minimax(depth, is_maximizing, alpha, beta, current_player):
    """Minimax algorithm with alpha-beta pruning"""

    #  Win condition
    if check_win(AI):
        return 10000 - depth  # Accept the move
    if check_win(HUMAN):
        return -10000 + depth  # Try Rejecting the move
    
    # Check if no moves available (draw)
    moves = get_available_moves(current_player)
    if not moves or depth >= MAX_DEPTH:
        return evaluate_board()
    
    if is_maximizing:
        max_eval = -math.inf
        for move in moves:
            apply_move(move, current_player)
            # Switch to opponent (HUMAN) for next level
            eval = minimax(depth + 1, False, alpha, beta, HUMAN)
            undo_move(move, current_player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            apply_move(move, current_player)
            # Switch to opponent (AI) for next level
            eval = minimax(depth + 1, True, alpha, beta, AI)
            undo_move(move, current_player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval


def get_best_move():
    """Get the best move for the AI using minimax"""
    best_score = -math.inf
    best_move = None
    moves = get_available_moves(AI)
    
    for move in moves:
        apply_move(move, AI)
        # AI just moved, so HUMAN moves next (minimizing)
        score = minimax(0, False, -math.inf, math.inf, HUMAN)
        undo_move(move, AI)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move


def make_ai_move():
    """Make the AI move"""
    global player, selected
    
    # Visual delay for better UX
    pygame.time.wait(500)
    
    best_move = get_best_move()
    
    if best_move:
        apply_move(best_move, AI)
        selected = False


# ---------
# VARIABLES
# ---------
player = 1
game_over = False
selected = False
again = False
valid = False
wrong_select = False
played = 0
eraser_won_times = 0
sharpner_won_times = 0

# ---------
# GUI
# ---------
class Button:
    def __init__(self, text, width, height, pos, elevation):
        # Core attributes
        self.not_running = True
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, height))
        self.bottom_color = '#354B5E'
        # text
        self.text_surf = gui_font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self, screen):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(screen, self.top_color, self.top_rect, border_radius=12)
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
                    self.not_running = False
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#D74B4B'


def start_scene(screen):
    title = pygame.image.load('assets/title.PNG')
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
        screen.blit(title, (40, 200))
        button1.draw(screen)
        button2.draw(screen)
        button3.draw(screen)
        button4.draw(screen)

        if button1.not_running == False:
            on_start_scene = False
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


def tutorial_scene(screen, on_tutorial_scene=True):
    tutorial = pygame.image.load('assets/tutorial.png')
    button5 = Button('Back', 100, 40, (530, 640), 5)
    while on_tutorial_scene:
        screen.blit(tutorial, (0, 0))
        button5.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()
        on_tutorial_scene = button5.not_running


########################################################################################################################

def about_scene(screen, on_about_scene=True):
    about = pygame.image.load('assets/about.png')
    button5 = Button('Back', 100, 40, (530, 640), 5)
    while on_about_scene:
        screen.blit(about, (0, 0))
        button5.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()
        on_about_scene = button5.not_running


########################################################################################################################

def win_scene(screen, player):
    global played, eraser_won_times, sharpner_won_times
    win = True
    if played < 3:
        if eraser_won_times - sharpner_won_times in [-1, 1, 0]:
            msg1 = f"{'You (Eraser)' if player == 1 else 'AI (Sharpner)'} won Round {played + 1}!"
            msg2 = f'Next Round: Round {played + 2}'
            played += 1

        else:
            played = 3
    if played == 3:
        msg1 = f"{'You (Eraser)' if eraser_won_times > sharpner_won_times else 'AI (Sharpner)'} is the ultimate winner!"
        msg2 = f"{'AI (Sharpner)' if eraser_won_times < sharpner_won_times else 'You (Eraser)'} You {'need more practice!' if eraser_won_times < sharpner_won_times else 'are amazing!'}"

    button2 = Button('Continue!', 300, 40, ((WIDTH / 2) - 150, (HEIGHT / 2) + 80), 5)
    button3 = Button('Play again', 300, 40, (30, (HEIGHT / 2) + 80), 5)
    button4 = Button('Exit', 300, 40, (360, (HEIGHT / 2) + 80), 5)
    while win:
        screen.fill((255, 255, 255))
        if played < 3:
            button2.draw(screen)
            if button2.not_running == False:
                restart()
                win = False
        else:
            button3.draw(screen)
            button4.draw(screen)
            if button3.not_running == False:
                restart()
                eraser_won_times, sharpner_won_times, played = 0, 0, 0
                win = False
            elif button4.not_running == False:
                sys.exit()

        textobj = font2.render(msg1, True, (0, 0, 0))
        text_rect = textobj.get_rect(center=(WIDTH / 2, HEIGHT / 2))

        textobj2 = font1.render(msg2, True, (0, 0, 0))
        text_rect2 = textobj2.get_rect(center=(WIDTH / 2, (HEIGHT / 2) + 40))

        screen.blit(textobj, text_rect)
        screen.blit(textobj2, text_rect2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()


# --------
# MAINLOOP
# --------
start_scene(screen)
while True:
    screen.blit(game_board, (0, 0))

    # AI's turn
    if player == AI and not game_over and not again:
        make_ai_move()
        
        if check_win(player):
            again = True
            if player == 1:
                eraser_won_times += 1
            else:
                sharpner_won_times += 1
        else:
            player = player % 2 + 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and player == HUMAN:
            x, y = pygame.mouse.get_pos()

            if selected == False:
                if not is_board_full():
                    valid, row, col = click_valid(x, y)

                else:
                    prev_row, prev_col, selected, valid, wrong_select = select(x, y, selected)
            else:
                prev_row, prev_col, valid, selected = move(x, y, prev_row, prev_col)

            if check_win(player):
                again = True
                if player == 1:
                    eraser_won_times += 1
                else:
                    sharpner_won_times += 1
            if valid == True and selected == False and not again:
                player = player % 2 + 1

            if valid == False and not again:
                error_start_time = pygame.time.get_ticks()
                show_error_type = 'invalid'

            if wrong_select == True and not again:
                error_start_time = pygame.time.get_ticks()
                show_error_type = 'wrong_select'

            if valid == True and not selected:
                for row in range(BOARD_ROWS):
                    for col in range(BOARD_COLS):
                        if board[row][col] in [1.5, 2.5]:
                            board[row][col] = 0

    score1 = font1.render(f'You (Eraser): {eraser_won_times}', True, (0, 0, 0))
    screen.blit(score1, (30, 10))

    score2 = font1.render(f'AI (Sharpner): {sharpner_won_times}', True, (0, 0, 0))
    screen.blit(score2, (480, 10))
    draw_figures()

    current_time = pygame.time.get_ticks()
    if show_error_type and current_time - error_start_time <= ERROR_DISPLAY_DURATION:
        if show_error_type == 'invalid':
            textobj = font1.render('Invalid Move!', True, (255, 0, 0))
            text_rect = textobj.get_rect(center=(WIDTH / 2, 30))
            screen.blit(textobj, text_rect)
        elif show_error_type == 'wrong_select':
            score3 = font1.render(f"Your turn!", True, (255, 0, 0))
            text_rect = score3.get_rect(center=(WIDTH / 2, 30))
            screen.blit(score3, text_rect)
    elif show_error_type:
        show_error_type = None

    # Display whose turn it is
    if not again:
        turn_text = font1.render(f"{'Your' if player == HUMAN else 'AI'} turn", True, (0, 0, 0))
        turn_rect = turn_text.get_rect(center=(WIDTH / 2, HEIGHT - 30))
        screen.blit(turn_text, turn_rect)

    pygame.display.update()
    if again:
        time.sleep(0.2)
        win_scene(screen, player)
        again = False
