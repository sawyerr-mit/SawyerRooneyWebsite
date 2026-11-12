import pygame
import math
import sys
import os

# Initialize board parameters, if you want to play on a different board size, change these
ROWS, COLS = 6, 7
CELL = 145
WIDTH = COLS * CELL
HEIGHT = (ROWS + 1) * CELL

# Initialize the colors that pygame will use.
BLUE = (30, 100, 200)
BLACK = (10, 10, 10)
RED = (220, 50, 50)
DARK_RED = (184, 29, 29)
YELLOW = (240, 200, 30)
DARK_YELLOW = (209, 163, 23)
WHITE = (240, 240, 240)
GRAY = (60, 60, 60)

EMPTY, P1, P2 = 0, 1, 2


# Create the empty board
def make_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]


# Function for when a player makes a move at a column
def drop(board, col, player):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return row
    return -1


# undo move, not accessible to the player, it is used as a helper
# function during the implementation of the minimax algorithm
def undo(board, row, col):
    board[row][col] = EMPTY


# Checks if given move is valid on board
def valid(board, col):
    return board[0][col] == EMPTY


# Generates a list of valid moves for the AI to check
def valid_moves(board):
    cols = list(range(COLS))
    return [c for c in cols if valid(board, c)]


# Checks if someone has won
def winner(board, row, col, player):
    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        count = 1
        for sign in (1, -1):
            r, c = row + dr * sign, col + dc * sign
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                count += 1
                r += dr * sign
                c += dc * sign
        if count >= 4:
            return True
    return False


# Evaluation window, which acts as a kernal which the evaluation function moves
# across the board to get a good evaluation. More pieces in a row corresponds
# to higher values, and more pieces in a row by the opponent is scored poorly.
def evaluate_window(a, b, c, d, player):
    score = 0
    opponent = P1 if player == P2 else P2

    pieces = [a, b, c, d]

    if pieces.count(player) == 4:
        return math.inf
    elif pieces.count(player) == 3 and pieces.count(EMPTY) == 1:
        score += 150
    elif pieces.count(player) == 2 and pieces.count(EMPTY) == 2:
        score += 15

    if pieces.count(opponent) == 3 and pieces.count(EMPTY) == 1:
        score -= 120

    return score


# Evaluation function. This function checks from the center column and slides the 4-cell evaluation
# window across every possible winning direction.
def evaluate(board, player):
    score = 0
    opponent = P1 if player == P2 else P2
    center = COLS // 2

    # Score control of center
    for r in range(ROWS):
        if board[r][center] == player:
            score += 10

    # Score horizontal 4 cell windows
    for r in range(ROWS):
        for c in range(COLS - 3):
            score += evaluate_window(
                board[r][c], board[r][c + 1],
                board[r][c + 2], board[r][c + 3],
                player
            )

    # Score vertical 4 cell windows
    for c in range(COLS):
        for r in range(ROWS - 3):
            score += evaluate_window(
                board[r][c], board[r + 1][c],
                board[r + 2][c], board[r + 3][c],
                player
            )

    # Score diagonal 4 cell windows with positive slope
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            score += evaluate_window(
                board[r][c], board[r + 1][c + 1],
                board[r + 2][c + 2], board[r + 3][c + 3],
                player
            )

    # Score diagonal 4 cell windows with negative slope
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            score += evaluate_window(
                board[r][c], board[r + 1][c - 1],
                board[r + 2][c - 2], board[r + 3][c - 3],
                player
            )

    return score


# This method prioritizes moves in this order: immediate winning moves, moves that block an
# immediate opponent win, the center column, and then all remaining columns. Connect 4 theory
# generally weights the center as better positionally. Searching the most promising moves first
# makes alpha-beta pruning more likely to cut off branches; this is known as move ordering.
def order_moves(board, cols, player):
    opponent = P1 if player == P2 else P2

    # Four priority move types: moves that win immediately, moves blocking
    # opponent's immediate win, the center column, and everything else.
    winning, blocking, center, others = [], [], [], []

    for col in cols:
        # Check if the played move was an immediate win
        row = drop(board, col, player)
        if row != -1 and winner(board, row, col, player):
            undo(board, row, col)
            winning.append(col)
            continue
        undo(board, row, col)

        # Check if the played move is an immediate block
        row = drop(board, col, opponent)
        if row != -1 and winner(board, row, col, opponent):
            undo(board, row, col)
            blocking.append(col)
            continue
        undo(board, row, col)

        # Check if it is a center move, else it is a standard move
        if col == COLS // 2:
            center.append(col)
        else:
            others.append(col)

    # Return the list of moves arranged in this prioritized order
    return winning + blocking + center + others


# The minimax algorithm; this is the heart of this code.
def minimax(board, depth, alpha, beta, maximizing, player):
    opponent = P1 if player == P2 else P2

    # If there are no valid moves remaining the game is a draw
    valid_cols = valid_moves(board)
    if not valid_cols:
        return 0, None

    # Check if the side to move has an immediate win. If so return infinity
    # for the AI or negative infinity for the opponent
    for col in valid_cols:
        row = drop(board, col, player if maximizing else opponent)
        if row != -1:
            if winner(board, row, col, player if maximizing else opponent):
                undo(board, row, col)
                return (math.inf, col) if maximizing else (-math.inf, col)
            undo(board, row, col)

    # Once the search depth is reached, score the board using the evaluation function
    # Depth largely determines the skill of the AI. An infinite depth AI would play perfectly.
    # However, connect 4 does not have infinite depth (in fact, the game has actually been solved).
    if depth == 0:
        return evaluate(board, player), None

    # Search the columns closest to the center first for better alpha-beta pruning
    valid_cols = sorted(valid_cols, key=lambda c: abs(c - COLS // 2))
    best_col = valid_cols[0]

    # Maximizing is the AI's turn, so it optimizes for the highest score
    if maximizing:
        value = -math.inf

        for col in valid_cols:
            row = drop(board, col, player)
            if row == -1:
                continue

            # Play the move, search the opponent's replies, then undo the move to continue search
            score, _ = minimax(board, depth - 1, alpha, beta, False, player)
            undo(board, row, col)

            # Keep track of the best score and the column that produced it
            if score > value:
                value = score
                best_col = col

            # Prune this branch if the minimizing player would never allow it - alpha pruning
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return value, best_col

    # Minimizing is the human's turn, so it looks for the lowest score
    else:
        value = math.inf

        for col in valid_cols:
            row = drop(board, col, opponent)
            if row == -1:
                continue

            # Play the move, search the AI's replies, then undo the move to keep searching
            score, _ = minimax(board, depth - 1, alpha, beta, True, player)
            undo(board, row, col)

            # Keep track of the lowest score and the column that produced it
            if score < value:
                value = score
                best_col = col

            # Prune this branch if the maximizing player would never allow it - beta pruning
            beta = min(beta, value)
            if alpha >= beta:
                break

        return value, best_col


# Draws the whole game screen
def draw(screen, board, font, hover_col, current_player):
    screen.fill(BLACK)

    # Draw the piece hovering above the column the mouse is over
    color = RED if current_player == P1 else YELLOW
    cx = hover_col * CELL + CELL // 2
    pygame.draw.circle(screen, DARK_RED if color is RED else DARK_YELLOW, (cx, CELL // 2), CELL // 2 - 8)
    pygame.draw.circle(screen, color, (cx, CELL // 2), 0.8 * CELL // 2 - 8)

    # Draw the blue board, then a circle for every cell on it (the holes on the connect 4 board)
    pygame.draw.rect(screen, BLUE, (0, CELL, WIDTH, ROWS * CELL))
    for r in range(ROWS):
        for c in range(COLS):
            # Empty cells are black, filled cells get a piece relative to the player color
            ring_color = BLACK
            if board[r][c] == P1:
                ring_color = DARK_RED
            elif board[r][c] == P2:
                ring_color = DARK_YELLOW
            cx = c * CELL + CELL // 2
            cy = (r + 1) * CELL + CELL // 2
            pygame.draw.circle(screen, ring_color, (cx, cy), CELL // 2 - 8)
            # Draw the lighter inner circle on top of the ring for placed pieces
            if ring_color is not BLACK:
                pygame.draw.circle(screen, RED if ring_color is DARK_RED else YELLOW, (cx, cy), 0.8 * CELL // 2 - 8)

    pygame.display.flip()


# Shows the end of game message in the center of the screen with a prompt to play again
def show_message(screen, font, text):
    surf = font.render(text, True, WHITE)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(surf, rect)
    # Smaller text below the message telling the player how to restart
    small = pygame.font.SysFont(None, 32)
    sub = small.render("Click to play again", True, GRAY)
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
    pygame.display.flip()


def main():
    # Run relative to this file. The sound files are found from any working directory if you wish to change them.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # The human is player 1 and the AI takes the other player
    HUMAN = P1

    # Start pygame and load the sounds
    pygame.init()
    pygame.mixer.init()
    piece_played = pygame.mixer.Sound("place.wav")
    you_lose = pygame.mixer.Sound("lose.wav")
    start = pygame.mixer.Sound("new_game.mp3")
    victory = pygame.mixer.Sound("victory.mp3")

    # Create the game window and important values for pygame such as clock and font
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four")
    font = pygame.font.SysFont(None, 64)
    clock = pygame.time.Clock()

    AI = P2 if HUMAN == P1 else P1

    # Plays the start sound and returns a new board, with player 1 going first
    def new_game():
        start.play()
        return make_board(), P1, False

    board, current, game_over = new_game()
    hover_col = COLS // 2

    # AI chooses move, plays it, and check if the game has ended
    def do_ai_move(board, current):
        draw(screen, board, font, hover_col, current)
        _, col = minimax(board, 14, -math.inf, math.inf, True, AI)
        row = drop(board, col, AI)
        piece_played.play()

        # Check if the AI's move won the game
        if winner(board, row, col, AI):
            you_lose.play()
            draw(screen, board, font, hover_col, current)
            show_message(screen, font, "AI wins! You Lose :(")
            return True

        # Check if it is a draw
        if not valid_moves(board):
            draw(screen, board, font, hover_col, current)
            show_message(screen, font, "Draw!")
            return True

        return False

    # AI makes the first move if it is the AI's turn
    if current == AI:
        game_over = do_ai_move(board, current)
        current = HUMAN

    # Main game loop
    while True:
        for event in pygame.event.get():
            # Close the window and exit the program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # After the game ends, a click starts a new game
            if game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    board, current, game_over = new_game()
                    hover_col = COLS // 2

                    if current == AI:
                        game_over = do_ai_move(board, current)
                        current = HUMAN
                continue

            # Move the hovering piece to the column the mouse is over
            if event.type == pygame.MOUSEMOTION:
                hover_col = min(event.pos[0] // CELL, COLS - 1)

            # A click plays a piece in the hovered column if the column isn't full
            if event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // CELL
                if not valid(board, col):
                    continue

                row = drop(board, col, HUMAN)
                piece_played.play()

                # Check if the human's move won the game
                if winner(board, row, col, HUMAN):
                    victory.play()
                    draw(screen, board, font, hover_col, current)
                    show_message(screen, font, "You win!")
                    game_over = True
                    continue

                # Check if the game is a draw
                if not valid_moves(board):
                    draw(screen, board, font, hover_col, current)
                    show_message(screen, font, "Draw!")
                    game_over = True
                    continue

                # Otherwise it is now the AI's turn
                current = AI
                game_over = do_ai_move(board, current)
                current = HUMAN

        # Redraw the board every frame while the game is still going, capped at 60 fps (pygame requires re-drawing like this)
        if not game_over:
            draw(screen, board, font, hover_col, current)

        clock.tick(60)


if __name__ == "__main__":
    main()
