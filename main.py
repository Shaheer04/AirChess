import cv2
import pygame
from gesture_handler import detect_hands, draw_landmarks, is_pinching, close_hands
from chess_display import init_transparent_display, draw_transparent_board, draw_transparent_dragging_piece, quit_display, draw_game_status, SQUARE_SIZE, status_font
from game_state import (
    get_board, get_selected_piece, handle_pinch_end, handle_pinch_start, 
    handle_pinch_move, get_piece_drag_position, get_valid_moves_for_selected,
    chess_engine, get_king_position,
    toggle_ai, is_ai_enabled, is_ai_thinking, 
    request_ai_move, make_ai_move
)

# OpenCV setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open webcam")
    exit()

# Get camera feed dimensions
success, frame = cap.read()
if success:
    camera_height, camera_width, _ = frame.shape
else:
    camera_width, camera_height = 640, 480

# Pygame setup
BOARD_SIZE = 8 * SQUARE_SIZE
screen = init_transparent_display()
if screen is None:
    print("Error initializing display")
    exit()
    

clock = pygame.time.Clock()

# Game state
pinched = False
pinch_location_pygame = None
initial_pinch_location = None # To track where the pinch started
last_valid_pinch_location = None

running = True
while running:
    # Get and process camera feed
    success, camera_feed = cap.read()
    if not success:
        continue
    camera_feed = cv2.flip(camera_feed, 1)
    height, width, _ = camera_feed.shape
    image_rgb = cv2.cvtColor(camera_feed, cv2.COLOR_BGR2RGB)
    
    # Detect hands and pinch gestures
    results = detect_hands(image_rgb)
    pinch_detected, current_pinch_location_cv = False, None
    
    if results.multi_hand_landmarks:
        draw_landmarks(camera_feed, results)
        if results.multi_hand_landmarks:
            pinch_detected, current_pinch_location_cv = is_pinching(results.multi_hand_landmarks[0], width, height)
        
        if current_pinch_location_cv:
            pinch_location_pygame = (current_pinch_location_cv[0], current_pinch_location_cv[1])
    
    # Reset pinch location when no pinch is detected
    if not pinch_detected:
        pinch_location_pygame = None

    # Prepare the display
    screen.fill((0, 0, 0, 0))
    
    # Get valid moves for the selected piece
    valid_moves = get_valid_moves_for_selected()
    king_pos = get_king_position() if chess_engine.in_check else None
    
    # Draw board with valid moves highlighted
    draw_transparent_board(
        screen, 
        get_board(), 
        valid_moves, 
        chess_engine.in_check, 
        king_pos
    )
    
    # Draw game status
    draw_game_status(
        screen, 
        chess_engine.checkmate, 
        chess_engine.stalemate, 
        chess_engine.white_to_move,
        is_ai_enabled(),
        is_ai_thinking()
    )

    # Handle AI turns
    if is_ai_enabled() and not chess_engine.white_to_move and not is_ai_thinking():
        request_ai_move()
        
    if is_ai_thinking():
        # Use OpenCV text instead of Pygame for the thinking indicator
        ai_thinking_text = "AI is thinking..."
        cv2.putText(
            camera_feed, 
            ai_thinking_text, 
            (width - 250, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.8, 
            (0, 200, 255), 
            2
        )
        
    # Process AI moves if available
    make_ai_move()

    # Handle pinch events for chess piece movement
    if pinch_location_pygame:
        # Scale the coordinates from camera space to board space
        scale_x = BOARD_SIZE / camera_width
        scale_y = BOARD_SIZE / camera_height
        
        # Apply scaling and offset
        board_x = pinch_location_pygame[0] * scale_x
        board_y = pinch_location_pygame[1] * scale_y

        adjusted_pinch_location = (board_x, board_y)
    else:
        adjusted_pinch_location = None
    
    if pinch_detected and not pinched and adjusted_pinch_location:
        # Start dragging a piece
        initial_pinch_location = adjusted_pinch_location
        last_valid_pinch_location = adjusted_pinch_location
        handle_pinch_start(adjusted_pinch_location)
        pinched = True
    elif pinched and pinch_detected and adjusted_pinch_location:
        # Continue dragging a piece and draw it
        handle_pinch_move(adjusted_pinch_location)
        last_valid_pinch_location = adjusted_pinch_location
        if get_selected_piece():
            # Get the visual drag position from the function
            drag_position = get_piece_drag_position(adjusted_pinch_location)
            if drag_position:
                # Draw the piece being dragged
                draw_transparent_dragging_piece(screen, get_selected_piece(), drag_position)
    elif not pinch_detected and pinched:
        # Drop a piece when pinch is released
        handle_pinch_end(last_valid_pinch_location)
        pinched = False
        initial_pinch_location = None
        last_valid_pinch_location = None

    # Combine camera feed with chess display
    pygame_image = pygame.surfarray.array3d(screen).transpose(1, 0, 2)
    pygame_image_bgr = cv2.cvtColor(pygame_image, cv2.COLOR_RGB2BGR)
    pygame_image_bgr = cv2.resize(pygame_image_bgr, (camera_width, camera_height))
    
    # Adjust alpha blending for better visibility
    alpha = 0.4
    overlayed_image = cv2.addWeighted(camera_feed, 1 - alpha, pygame_image_bgr, alpha, 0)

    # Display game status as text on the camera feed
    status_text = ""
    if chess_engine.checkmate:
        status_text = "Checkmate!"
    elif chess_engine.stalemate:
        status_text = "Stalemate!"
    elif chess_engine.in_check:
        status_text = "Check!"
        
    if status_text:
        cv2.putText(overlayed_image, status_text, (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Add instructions text to the display
    instructions = "Press 'A' to toggle AI opponent | Press 'Q' to quit"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(overlayed_image, instructions, (10, camera_height - 15), 
               font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    if is_ai_enabled():
        ai_status = "AI: ON (playing as Black)" 
        cv2.putText(overlayed_image, ai_status, (10, camera_height - 40), 
                   font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('Virtual Chess', overlayed_image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('a'):
        ai_on = toggle_ai()
        print(f"AI opponent {'enabled' if ai_on else 'disabled'}")
    clock.tick(30)

# Clean up
cap.release()
cv2.destroyAllWindows()
close_hands()
quit_display()