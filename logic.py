from typing import Dict

def decompose_coord(coordinate: str) -> list:
    """
    Decompose a chess coordinate (e.g., 'e4') into a list [column, row].
    """
    if len(coordinate) != 2 or not coordinate[0].isalpha() or not coordinate[1].isdigit():
        raise ValueError(f"Invalid chess coordinate: {coordinate}")
    return [coordinate[0], int(coordinate[1])]

def is_square_empty(chess_coord: str, positions: Dict[str, Dict[str, list]]) -> bool:
    """
    Check if a square on the chessboard is empty.
    """
    if len(chess_coord) != 2 or chess_coord[0] not in "abcdefgh" or not chess_coord[1].isdigit():
        return False
    row = int(chess_coord[1])
    if row < 1 or row > 8:
        return False

    # Check all positions to see if the square is occupied
    for color in positions:
        for piece in positions[color]:
            if chess_coord in positions[color][piece]:
                return False
    return True

def is_enemy_piece(chess_coord: str, piece_color: str, positions: Dict[str, Dict[str, list]]) -> bool:
    """
    Check if a square is occupied by an enemy piece.
    """
    for color in positions:
        for piece in positions[color]:
            if chess_coord in positions[color][piece] and color != piece_color:
                return True
    return False

def get_moves_in_direction(col: str, row: int, dx: int, dy: int, piece_color: str, positions: Dict[str, Dict[str, list]]) -> list:
    """
    Helper function to get all possible moves in a particular direction (dx, dy).
    """
    possible_moves = []
    cur_col, cur_row = col, row
    while True:
        cur_col = chr(ord(cur_col) + dx)
        cur_row += dy
        new_coord = f"{cur_col}{cur_row}"

        # Check if is out of bounds
        if cur_col not in "abcdefgh" or not (1 <= cur_row <= 8):
            break

        # If the square is empty, add it as a possible move
        if is_square_empty(new_coord, positions):
            possible_moves.append(new_coord)
        elif is_enemy_piece(new_coord, piece_color, positions):
            possible_moves.append(new_coord)
            break  # Capture the enemy piece and stop in this direction
        else:
            break  # Blocked by a friendly piece

    return possible_moves

def movement_schema(chess_coord: str, piece_type: str, piece_color: str, positions: Dict[str, Dict[str, list]]) -> list:
    """
    Generate the possible moves for a chess piece.
    """
    col, row = decompose_coord(chess_coord)
    possible_moves = []

    match piece_type:
        case 'pawn':
            direction = 1 if piece_color == "white" else -1
            start_row = 2 if piece_color == "white" else 7

            # Forward move (1 step)
            forward = f"{col}{row + direction}"
            if is_square_empty(forward, positions):
                possible_moves.append(forward)

            # Forward move (2 steps) from starting row
            if row == start_row:
                double_forward = f"{col}{row + 2 * direction}"
                if is_square_empty(double_forward, positions):
                    possible_moves.append(double_forward)

            # Diagonal captures
            for dcol in [-1, 1]:
                new_col = chr(ord(col) + dcol)
                capture = f"{new_col}{row + direction}"
                if new_col in "abcdefgh" and is_enemy_piece(capture, piece_color, positions):
                    possible_moves.append(capture)

        case 'rook':
            # Rook moves: up, down, left, right
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dx, dy in directions:
                cur_col, cur_row = col, row
                while True:
                    cur_col = chr(ord(cur_col) + dx)
                    cur_row += dy
                    new_coord = f"{cur_col}{cur_row}"

                    if cur_col not in "abcdefgh" or not (1 <= cur_row <= 8):
                        break

                    if not is_square_empty(new_coord, positions):
                        if is_enemy_piece(new_coord, piece_color, positions):
                            possible_moves.append(new_coord)
                        break

                    possible_moves.append(new_coord)

        case 'bishop':
            # Bishop moves: diagonals
            directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
            for dx, dy in directions:
                cur_col, cur_row = col, row
                while True:
                    cur_col = chr(ord(cur_col) + dx)
                    cur_row += dy
                    new_coord = f"{cur_col}{cur_row}"

                    if cur_col not in "abcdefgh" or not (1 <= cur_row <= 8):
                        break

                    if not is_square_empty(new_coord, positions):
                        if is_enemy_piece(new_coord, piece_color, positions):
                            possible_moves.append(new_coord)
                        break

                    possible_moves.append(new_coord)

        case 'queen':
            # Queen combines rook and bishop moves
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
            for dx, dy in directions:
                cur_col, cur_row = col, row
                while True:
                    cur_col = chr(ord(cur_col) + dx)
                    cur_row += dy
                    new_coord = f"{cur_col}{cur_row}"

                    if cur_col not in "abcdefgh" or not (1 <= cur_row <= 8):
                        break

                    if not is_square_empty(new_coord, positions):
                        if is_enemy_piece(new_coord, piece_color, positions):
                            possible_moves.append(new_coord)
                        break

                    possible_moves.append(new_coord)

        case 'king':
            # King moves: 1 square in any direction
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
            for dx, dy in directions:
                new_col = chr(ord(col) + dx)
                new_row = row + dy
                new_coord = f"{new_col}{new_row}"

                # Check if the new position is within bounds and if it's empty or occupied by an enemy piece
                if new_col in "abcdefgh" and 1 <= new_row <= 8:
                    if is_square_empty(new_coord, positions) or is_enemy_piece(new_coord, piece_color, positions):
                        possible_moves.append(new_coord)

        case 'knight':
            # Knight moves: L-shaped moves (2 squares in one direction and 1 square perpendicular)
            knight_moves = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]
            for dx, dy in knight_moves:
                new_col = chr(ord(col) + dx)
                new_row = row + dy
                new_coord = f"{new_col}{new_row}"

                # Check if the new position is within bounds and if it's empty or occupied by an enemy piece
                if new_col in "abcdefgh" and 1 <= new_row <= 8:
                    if is_square_empty(new_coord, positions) or is_enemy_piece(new_coord, piece_color, positions):
                        possible_moves.append(new_coord)

    return possible_moves

