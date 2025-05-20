# Air Chess

Air Chess is an innovative, gesture-controlled chess game that allows players to move pieces using hand gestures in the air. Using computer vision technology, the game tracks hand movements through a webcam, enabling a unique and interactive chess experience.

## Features

- **Gesture Controls**: Control chess pieces naturally with pinch gestures captured by your webcam
- **Real-time Hand Tracking**: Advanced hand detection and tracking using computer vision
- **Visual Feedback**: See valid moves highlighted on the board when selecting pieces
- **AI Opponent**: Play against a computer opponent that adapts to your moves
- **Game Status Indicators**: Clear visual cues for game states like check, checkmate, and stalemate
- **Transparent Interface**: Overlay chess board on your webcam feed for an immersive experience

## Requirements

- Python 3.7 or higher
- Webcam or camera device
- The following Python libraries:
  - OpenCV (cv2)
  - Pygame
  - Mediapipe (for hand tracking)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/air-chess.git
   cd air-chess
   ```

2. Install required dependencies:
   ```
   pip install opencv-python pygame mediapipe
   ```

## How to Play

1. Run the main script:
   ```
   python main.py
   ```

2. Position yourself in front of the webcam, making sure your hands are visible.

3. To move a chess piece:
   - Make a pinch gesture (touching thumb and index finger) over the piece you want to move
   - Maintain the pinch while moving your hand to the destination square
   - Release the pinch to place the piece

4. Game controls:
   - Press 'A' to toggle the AI opponent (plays as Black)
   - Press 'Q' to quit the game

## Game Rules

Air Chess follows standard chess rules, including:
- Special moves like castling, en passant, and pawn promotion
- Check and checkmate detection
- Stalemate conditions

## Project Structure

- `main.py` - The main game loop and integration of all components
- `gesture_handler.py` - Hand detection and gesture recognition
- `chess_display.py` - Visual rendering of the chess board and pieces
- `game_state.py` - Chess logic and game state management

## Troubleshooting

- **Camera not detected**: Ensure your webcam is properly connected and not in use by another application
- **Hand detection issues**: Make sure there's adequate lighting and your hands are clearly visible
- **Performance problems**: Close other resource-intensive applications for smoother gameplay

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Chess piece designs based on standard chess notation
- Hand tracking capabilities powered by MediaPipe