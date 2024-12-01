import pygame
import sys
import os
import time
import logic
import logging
import threading
import ai
from enum import Enum
from typing import Dict, Tuple
from screens import main_menu, game_over, promotion_choice

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FPS = 10
DEBUG = True

class Colors(Enum):
    LIGHT = (224, 205, 169)
    DARK = (186, 135, 89)
    HIGHLIGHT = (0, 0, 0)

INITIAL_POSITIONS = {
    "white": {
        "rook": ["a1", "h1"],
        "knight": ["b1", "g1"],
        "bishop": ["c1", "f1"],
        "queen": ["d1"],
        "king": ["e1"],
        "pawn": [f"{chr(col)}2" for col in range(ord("a"), ord("h") + 1)],
    },
    "black": {
        "rook": ["a8", "h8"],
        "knight": ["b8", "g8"],
        "bishop": ["c8", "f8"],
        "queen": ["d8"],
        "king": ["e8"],
        "pawn": [f"{chr(col)}7" for col in range(ord("a"), ord("h") + 1)],
    },
}

player = 'white'
winner = None

icon_surface = pygame.image.load("assets/3d-pawn.png")

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()
pygame.display.set_icon(icon_surface) 
movement_sound = pygame.mixer.Sound("assets/movement.wav")

# Global timer variables
timer_running = False
turn_lock = threading.Lock()  # To prevent simultaneous timer modification

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def load_pieces() -> Dict[str, pygame.Surface]:
    pieces = {}
    base_path = os.path.join(os.path.dirname(__file__), "assets")
    for color in ["white", "black"]:
        for piece in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
            path = os.path.join(base_path, f"{color}-{piece}.png")
            image = pygame.image.load(path)
            scaled_image = pygame.transform.smoothscale(image, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
            pieces[f"{color}-{piece}"] = scaled_image
    return pieces

def chess_to_indices(coord: str) -> Tuple[int, int]:
    col, row = coord
    return 8 - int(row), ord(col) - ord("a")

def get_chess_coords(row: int, col: int) -> str:
    letters = "abcdefgh"
    return f"{letters[col]}{ROWS - row}"

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = Colors.LIGHT.value if (row + col) % 2 == 0 else Colors.DARK.value
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(pieces: Dict[str, pygame.Surface], positions: Dict[str, str]):
    for piece_with_coords, coord in positions.items():
        piece = "-".join(piece_with_coords.split("-")[:2])  # Extract "white-rook" from "white-rook-a1"
        row, col = chess_to_indices(coord)
        x = col * SQUARE_SIZE + SQUARE_SIZE // 2 - pieces[piece].get_width() // 2
        y = row * SQUARE_SIZE + SQUARE_SIZE // 2 - pieces[piece].get_height() // 2
        screen.blit(pieces[piece], (x, y))

def draw_text_with_border(
    text: str,
    font: pygame.font.Font,
    text_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    x: int,
    y: int,
    opacity: int = 255,
):
    text_surface = font.render(text, True, text_color)
    border_surface = font.render(text, True, border_color)

    temp_surface = pygame.Surface(
        (text_surface.get_width() + 2, text_surface.get_height() + 2), pygame.SRCALPHA
    )
    temp_surface.set_alpha(opacity)

    offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in offsets:
        temp_surface.blit(border_surface, (1 + dx, 1 + dy))

    temp_surface.blit(text_surface, (1, 1))
    screen.blit(temp_surface, (x, y))

def highlight_square(row: int, col: int):
    pygame.draw.rect(
        screen,
        Colors.HIGHLIGHT.value,
        (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
        3,
    )

def highlight_move(row: int, col: int):
    overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
    overlay.set_alpha(100)
    overlay.fill((105, 105, 105))
    screen.blit(overlay, (col * SQUARE_SIZE, row * SQUARE_SIZE))



def logic_output(chess_coord, piece_type, piece_color, current_positions):
    possible_moves = logic.movement_schema(chess_coord, piece_type, piece_color, current_positions)
    print(f"Possible moves for {piece_color} {piece_type} at {chess_coord}: {possible_moves}")

    for move in possible_moves:
        row, col = chess_to_indices(move)
        highlight_move(row, col)

def timer_thread(timer_length):
    global white_time_left, black_time_left, timer_running
    white_time_left, black_time_left = timer_length, timer_length
    while timer_running:
        time.sleep(1)
        with turn_lock:
            if player == "white" and white_time_left > 0:
                white_time_left -= 1
            elif player == "black" and black_time_left > 0:
                black_time_left -= 1
        logger.debug(f"White time left: {white_time_left}, Black time left: {black_time_left}")

def start_timer(timer_length):
    global timer_running
    timer_running = True
    threading.Thread(target=timer_thread, args=(timer_length,), daemon=True).start()

def stop_timer():
    global timer_running
    timer_running = False

def promotion_handler(new_chess_coord, piece_color, current_positions):
    logger.debug(f"Pawn reached the last row at {new_chess_coord}. Promoting...")
    promoted_piece = promotion_choice(WIDTH, HEIGHT, player)
    current_positions[piece_color]['pawn'].remove(new_chess_coord)
    current_positions[piece_color].setdefault(promoted_piece, []).append(new_chess_coord)
    print(f"Pawn promoted to {promoted_piece} at {new_chess_coord}.")

def check_game_over_by_time(white_time_left, black_time_left, player):
    global timer_running
    logger.debug(f"Checking timer ({timer_running}) lenght: {white_time_left} && {black_time_left}")
    if white_time_left == 0:
        winner = "Black"
        print(f"GameOver. {winner} wins by time.")
        game_over(winner, WIDTH, HEIGHT)
        timer_running = False
        return True
    elif black_time_left == 0:
        winner = "White"
        print(f"!GameOver. {winner} wins by time.")
        game_over(winner, WIDTH, HEIGHT)
        timer_running = False
        return True
    return False

def checkmate_detector(player_color, current_positions):
    king_coord = next((coord for coord in current_positions[player_color]['king']), None)
    if not king_coord:
        return True
    return False

def main():
    global player, winner

    # Main menu screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    timer_length, singleplayer = main_menu(screen)
    timer_length *= 60


    pieces = load_pieces()
    positions = {
        f"{color}-{piece}-{coord}": coord
        for color, pieces_dict in INITIAL_POSITIONS.items()
        for piece, coords in pieces_dict.items()
        for coord in coords
    }

     # Initialize timers
    white_time_left = timer_length
    black_time_left = timer_length

    running = True
    selected_square = None
    valid_piece_selected = False
    current_positions = INITIAL_POSITIONS
    possible_moves = []
    chess_coord = None
    piece_color = None
    piece_type = None
    move_made = False
    timer_on = False

    # Start timer when the game begins
    if timer_length > 0:
        timer_on = True
        print(f"Timer length: {timer_length}")
        start_timer(timer_length)

    while running:
        if move_made:  # Check for checkmate (soon)
            if checkmate_detector(player, current_positions) or (timer_on and check_game_over_by_time(white_time_left, black_time_left, player)):
                if winner is not None:
                    winner = "Black" if player == "white" else "White"
                print(f"GameOver. {winner} wins.")
                game_over(winner, WIDTH, HEIGHT)
                running = False  # End the game loop
                break  # Exit the event loop

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
                selected_square = (row, col)
                new_chess_coord = get_chess_coords(row, col)

                if valid_piece_selected and (chess_coord != new_chess_coord):
                    valid_piece_selected = False
                    if new_chess_coord in possible_moves:
                        # Play movement sound
                        movement_sound.play()

                        print(f"Moving {piece_color} {piece_type} from {chess_coord} to {new_chess_coord}")
                        current_positions[piece_color][piece_type].remove(chess_coord)
                        current_positions[piece_color][piece_type].append(new_chess_coord)


                        # Handle promotion
                        if piece_type == 'pawn' and (new_chess_coord.endswith('8') or new_chess_coord.endswith('1')):
                            promotion_handler(new_chess_coord, piece_color, current_positions)

                        # Remove captured pieces
                        for enemy_color in current_positions:
                            if enemy_color != piece_color:
                                for enemy_piece, enemy_positions in current_positions[enemy_color].items():
                                    if new_chess_coord in enemy_positions:
                                        enemy_positions.remove(new_chess_coord)

                        positions = {
                            f"{color}-{piece}-{coord}": coord
                            for color, pieces_dict in current_positions.items()
                            for piece, coords in pieces_dict.items()
                            for coord in coords
                        }
                        logging.debug(current_positions)

                        # Switch turn
                        if singleplayer or None:
                            player = "white" if player == "black" else "black"
                            print(f"Turn changed to: {player}")
                            move_made = True
                        else:
                            ai.ai_initialization(positions, player)
                            
                    else:
                        print(f"Invalid move to {new_chess_coord}")

                # Select the new piece 
                chess_coord = get_chess_coords(row, col)
                piece = next((p for p, c in positions.items() if c == chess_coord), None)
                piece_type = piece.split("-")[1] if piece else "empty"
                piece_color = piece.split("-")[0] if piece else "none"

                print(f"Selected square: {chess_coord}, contains: {piece_color} {piece_type}")
                pygame.display.set_caption(f"Chess Game | {piece_type}-{chess_coord}")

                if piece and piece_color == player:
                    possible_moves = logic.movement_schema(chess_coord, piece_type, piece_color, current_positions)
                    valid_piece_selected = True
                    print(f"Possible moves for {piece_color} {piece_type} at {chess_coord}: {possible_moves}")
                else:
                    print("No valid piece selected")

        draw_board()
        draw_pieces(pieces, positions)

        if selected_square and piece_type != "empty" and piece_color == player:
            highlight_square(*selected_square)

            for move in possible_moves:
                row, col = chess_to_indices(move)
                highlight_move(row, col)

        font = pygame.font.Font(None, 50)
        opacity = 180

        # Draw the timer
        draw_text_with_border(
            f"  ~{white_time_left}s" if timer_on and player == "white" else f"  ~{black_time_left}s" if timer_on else f"{player.upper()}",
            font,
            (255, 255, 255) if player == "white" else (0, 0, 0),
            (0, 0, 0) if player == "white" else (255, 255, 255),
            WIDTH - 150,
            20,
            opacity 
        )
        logger.debug(f"Rendering: {player} ~{white_time_left if player == 'white' else black_time_left}s")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
