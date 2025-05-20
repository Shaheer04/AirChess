from chess_engine import GameState, Move
import threading
import queue
from chess_ai import findBestMove
import time

# Initialize the chess engine
chess_engine = GameState()

selected_piece = None
selected_piece_pos = None  # (row, col)
dragging = False
drag_offset = (0, 0)
SQUARE_SIZE = 200  # Size of each square on the board

# Add these globals after existing ones
ai_enabled = False
ai_thinking = False
ai_move_queue = queue.Queue()

def get_board():
    # Convert chess engine board format to your display format
    display_board = []
    for row in chess_engine.board:
        display_row = []
        for piece in row:
            if piece == "--":
                display_row.append("")
            else:
                # Convert chess engine notation to your notation
                # First char is color (w/b), second is piece type
                color_prefix = "" if piece[0] == "b" else piece[0].upper()
                piece_char = piece[1].lower() if piece[0] == "b" else piece[1].upper()
                display_row.append(piece_char)
        display_board.append(display_row)
    return display_board

def get_selected_piece():
    return selected_piece

def set_selected_piece(piece):
    global selected_piece
    selected_piece = piece

def get_selected_piece_pos():
    return selected_piece_pos

def set_selected_piece_pos(pos):
    global selected_piece_pos
    selected_piece_pos = pos

def is_dragging():
    return dragging

def set_dragging(is_drag):
    global dragging
    dragging = is_drag

def get_drag_offset():
    return drag_offset

def set_drag_offset(offset):
    global drag_offset
    drag_offset = offset

def get_piece_drag_position(pinch_location):
    if pinch_location and is_dragging() and get_selected_piece():
        offset = get_drag_offset()
        return (pinch_location[0] - offset[0], pinch_location[1] - offset[1])
    return None

def handle_pinch_start(pinch_location):
    global selected_piece, selected_piece_pos, dragging, drag_offset
    
    print(f"Raw pinch location: {pinch_location}")
    
    row = int(pinch_location[1] // SQUARE_SIZE)
    col = int(pinch_location[0] // SQUARE_SIZE)
    print(f"Calculated board position: row={row}, col={col}")
    
    if 0 <= row < 8 and 0 <= col < 8:
        engine_piece = chess_engine.board[row][col]
        if engine_piece != "--":
            # Convert to display format for dragging
            color = engine_piece[0]
            piece_type = engine_piece[1]
            display_piece = piece_type.lower() if color == "b" else piece_type.upper()
            
            set_selected_piece(display_piece)
            set_selected_piece_pos((row, col))
            set_dragging(True)
            
            # Calculate drag offset from center of square
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            drag_offset = (pinch_location[0] - center_x, pinch_location[1] - center_y)
            set_drag_offset(drag_offset)
            
            print(f"Selected piece: '{display_piece}' at position: ({row}, {col})")
            print(f"Drag offset: {drag_offset}")
        else:
            print(f"No piece at position ({row}, {col})")
    else:
        print(f"Position out of bounds: ({row}, {col})")

def handle_pinch_move(pinch_location):
    """Updates the drag position during piece movement"""
    global drag_offset
    if dragging and pinch_location:
        # Just update the drag position during movement
        # No need to modify the board state here
        return True
    return False

def get_valid_moves_for_selected():
    """Returns all valid moves for the currently selected piece"""
    if selected_piece and selected_piece_pos:
        valid_moves = chess_engine.getValidMoves()
        row, col = selected_piece_pos
        # Filter moves that start from the selected position
        return [move for move in valid_moves 
                if move.start_row == row and move.start_col == col]
    return []

def get_king_position():
    """Returns position of the king that might be in check"""
    if chess_engine.in_check:
        if chess_engine.white_to_move:
            return chess_engine.white_king_location
        else:
            return chess_engine.black_king_location
    return None

def handle_pinch_end(pinch_location):
    global selected_piece, selected_piece_pos, dragging
    
    if dragging and selected_piece and selected_piece_pos:
        start_row, start_col = selected_piece_pos
        
        if pinch_location:
            end_row = int(pinch_location[1] // SQUARE_SIZE)
            end_col = int(pinch_location[0] // SQUARE_SIZE)
            
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                # Create move and check if valid
                move = Move((start_row, start_col), (end_row, end_col), chess_engine.board)
                valid_moves = chess_engine.getValidMoves()
                
                if move in valid_moves:
                    # Make the move in the chess engine
                    chess_engine.makeMove(move)
                    print(f"Valid move: {move.getChessNotation()}")
                else:
                    print(f"Invalid move attempted: {start_row},{start_col} to {end_row},{end_col}")
        
        # Reset dragging state
        set_selected_piece(None)
        set_selected_piece_pos(None)
        set_dragging(False)
        set_drag_offset((0, 0))

def toggle_ai():
    global ai_enabled
    ai_enabled = not ai_enabled
    return ai_enabled

def is_ai_enabled():
    return ai_enabled

def is_ai_thinking():
    return ai_thinking

def get_ai_move():
    if not ai_move_queue.empty():
        return ai_move_queue.get()
    return None

def request_ai_move():
    global ai_thinking
    print(f"AI enabled: {ai_enabled}, Current player: {'White' if chess_engine.white_to_move else 'Black'}")
    if not ai_thinking and is_ai_enabled() and chess_engine.white_to_move == False:
        print("Starting AI move calculation...")
        ai_thinking = True
        valid_moves = chess_engine.getValidMoves()
        ai_thread = threading.Thread(target=findBestMove, args=(chess_engine, valid_moves, ai_move_queue))
        ai_thread.daemon = True
        ai_thread.start()
        return True
    return False

def make_ai_move():
    global ai_thinking
    time.sleep(5)  
    if ai_thinking:
        ai_move = get_ai_move()
        if ai_move:
            chess_engine.makeMove(ai_move)
            ai_thinking = False
            return True
    return False