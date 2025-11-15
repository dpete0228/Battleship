import arcade
# Import constants and utilities from the new constants file
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE 
from hotseat import HotseatGame # Import the main window class

def main():
    # Use the hotseat game window
    window = HotseatGame() 
    arcade.run()

if __name__ == "__main__":
    main()