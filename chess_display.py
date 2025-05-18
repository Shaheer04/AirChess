import pygame
import os

IMAGES = {}  

SQUARE_SIZE = 200  
BOARD_SIZE = 8 * SQUARE_SIZE
screen = None
piece_font = None
status_font = None

piece_colors = {"p": "white", "r": "white", "n": "white", "b": "white", "q": "white", "k": "white",
                "P": "black", "R": "black", "N": "black", "B": "black", "Q": "black", "K": "black"}

def load_chess_images():
    """Load all chess piece images"""
    global IMAGES
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try:
            img_path = os.path.join("images", piece + ".png")
            print(f"Loading image: {img_path}")
            image = pygame.image.load(img_path)
            IMAGES[piece] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
        except pygame.error as e:
            print(f"Error loading {piece}.png: {e}")
            IMAGES[piece] = None  # Set to None to indicate failed loading
    
    print(f"Loaded {len(IMAGES)} images: {list(IMAGES.keys())}")

def init_transparent_display():
    global screen, piece_font, status_font
    pygame.init()
    # Create a surface without opening a window
    screen_height = BOARD_SIZE + 250 
    screen_width = BOARD_SIZE
    screen = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    piece_font = pygame.font.Font(None, 120)
    status_font = pygame.font.Font(None, 60)
    
    # Load images during initialization
    load_chess_images()
    
    return screen   

def draw_transparent_board(screen, board, valid_moves=None, in_check=False, king_pos=None):
    colors = [(205, 133, 63, 128), (245, 222, 179, 128)]  # Brown and Beige with alpha (transparency)
    for row in range(8):
        for col in range(8):
            # Draw base square
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Highlight valid moves if provided
            if valid_moves:
                for move in valid_moves:
                    if move.end_row == row and move.end_col == col:
                        # Draw highlight circle for valid move destination
                        highlight_color = (0, 255, 0, 80)  # Semi-transparent green
                        pygame.draw.circle(screen, highlight_color, 
                                          (col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                           row * SQUARE_SIZE + SQUARE_SIZE // 2), 
                                          SQUARE_SIZE // 4)
            
            # Draw pieces using images
            piece = board[row][col]
            if piece:
                # Convert piece notation to image key
                if piece.islower():  # Black pieces
                    piece_type = piece.upper() if piece != 'p' else 'p'  # Keep pawn lowercase
                    img_key = "b" + piece_type
                else:  # White pieces
                    piece_type = piece if piece != 'P' else 'p'  # Keep pawn lowercase
                    img_key = "w" + piece_type
                
                # Get the image from main's IMAGES dictionary
                if img_key in IMAGES:
                    piece_img = IMAGES[img_key]
                    # Position the image correctly on the board
                    piece_rect = piece_img.get_rect(center=(
                        col * SQUARE_SIZE + SQUARE_SIZE // 2,
                        row * SQUARE_SIZE + SQUARE_SIZE // 2
                    ))
                    screen.blit(piece_img, piece_rect)

    # Highlight king if in check
    if in_check and king_pos:
        king_row, king_col = king_pos
        check_color = (255, 0, 0, 100)  # Semi-transparent red
        pygame.draw.rect(screen, check_color, 
                        (king_col * SQUARE_SIZE, king_row * SQUARE_SIZE, 
                         SQUARE_SIZE, SQUARE_SIZE))

def draw_game_status(screen, checkmate=False, stalemate=False, white_to_move=True, ai_enabled=False, ai_thinking=False):
    status_text = ""
    if checkmate:
        status_text = "Checkmate! " + ("Black" if white_to_move else "White") + " wins!"
    elif stalemate:
        status_text = "Stalemate! Game is a draw."
    elif white_to_move:
        status_text = "White to move" + (" (Human)" if ai_enabled else "")
    else:
        status_text = "Black to move" + (" (AI)" if ai_enabled else "")
        
    if status_text:
        text_surface = status_font.render(status_text, True, (255, 255, 255))
        text_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 180))
        screen.blit(text_bg, (10, 10))
        screen.blit(text_surface, (20, 15))
        
    # Show AI thinking indicator
    if ai_thinking:
        thinking_text = "AI is thinking..."
        think_surface = status_font.render(thinking_text, True, (255, 255, 255))
        think_bg = pygame.Surface((think_surface.get_width() + 20, think_surface.get_height() + 10), pygame.SRCALPHA)
        think_bg.fill((50, 50, 200, 180))
        screen.blit(think_bg, (BOARD_SIZE - think_surface.get_width() - 30, 10))
        screen.blit(think_surface, (BOARD_SIZE - think_surface.get_width() - 20, 15))

def draw_transparent_dragging_piece(screen, piece, center):
    if piece:
        # Convert piece to image key
        if piece.islower():  # Black pieces
            piece_type = piece.upper() if piece != 'p' else 'p'
            img_key = "b" + piece_type
        else:  # White pieces
            piece_type = piece if piece != 'P' else 'p'
            img_key = "w" + piece_type
            
        # Get the image from the main module
        if img_key in IMAGES:
            piece_img = IMAGES[img_key]
            # Add glow effect
            glow_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 255, 80), 
                             (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 
                             SQUARE_SIZE // 2.5)
            
            # Position the image at the cursor
            piece_rect = piece_img.get_rect(center=center)
            screen.blit(glow_surface, (piece_rect.x, piece_rect.y))
            screen.blit(piece_img, piece_rect)

def screen_to_board(x, y):
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None, None

def quit_display():
    pygame.quit()

def get_status_font():
    """Return the status font after initialization"""
    global status_font
    return status_font