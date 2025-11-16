# main.py
import arcade
from mainmenu import MainMenuView
from hotseat import HotseatGame
from internet import InternetGame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


def start_game(mode: str):
    def _launch(dt):
        # Close the current window (menu) safely before starting a new game window
        arcade.close_window()

        # Instantiate the correct game class based on selected mode
        if mode == "hotseat":
            game_window = HotseatGame()
        else:
            game_window = InternetGame()

        # Set the newly created game window as the active window
        arcade.set_window(game_window)

        # Start the Arcade event loop for the new game window
        arcade.run()

    # Schedule _launch to run on the next frame to ensure safe window transition
    arcade.schedule(_launch, 0)


def main():
    # Create the main arcade window for the menu with specified width, height, and title
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Battleship - Menu")

    # Initialize and display the main menu view, passing the start_game callback
    menu_view = MainMenuView(on_start_game=start_game)
    window.show_view(menu_view)

    # Start the Arcade event loop for the menu window
    arcade.run()


if __name__ == "__main__":
    main()