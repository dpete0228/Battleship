import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import sys

class GameOverView(arcade.View):
    """
    View shown when the game has ended, either in victory or defeat.
    """
    def __init__(self, main_game_window, winner_player_number):
        # Initialize the parent class (arcade.View)
        super().__init__()
        
        # Store reference to the main game window so we can control transitions
        self.game = main_game_window
        
        # Which player won the game
        self.winner = winner_player_number
        
        # The text message that will be displayed on screen
        self.message = ""
        
        # Determine which player this machine is: host = Player 1, client = Player 2
        my_player_number = 1 if self.game.game_role == 'host' else 2
        
        # Set the appropriate victory/defeat message
        if my_player_number == self.winner:
            self.message = "VICTORY! YOU SUNK ALL OPPONENT SHIPS!"
        else:
            self.message = "DEFEAT! ALL YOUR SHIPS WERE SUNK!"
        
        # Stop any scheduled network-update callbacks from continuing after game end
        arcade.unschedule(self.game._process_command)

    def on_draw(self):
        """Render the game-over message and instructions."""
        self.clear()
        
        # Draw the win/lose message in green for victory or red for defeat
        arcade.draw_text(
            self.message,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 50,
            arcade.color.GREEN if "VICTORY" in self.message else arcade.color.RED,
            font_size=50,
            anchor_x="center",
        )
        
        # Draw instructions for restarting or exiting
        arcade.draw_text(
            "Press ESC to exit or R to return to connection screen.",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 50,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        """Process key input for exiting or restarting."""
        if key == arcade.key.ESCAPE:
            # Exit the entire program instantly
            sys.exit(0)
        elif key == arcade.key.R:
            # Reset game state and return to connection menu
            self.game.reset_game_state()
            self.game.show_connection_screen()


class WaitingView(arcade.View):
    """View used while waiting for the opponent to submit a networked move."""
    def __init__(self, game_window):
        # Initialize parent arcade.View class
        super().__init__()
        
        # Store reference to the main game window for screen size access
        self.window = game_window
        
        # Set a neutral background color while waiting
        arcade.set_background_color(arcade.color.LIGHT_GRAY)
        
    def on_draw(self):
        """Render the waiting message."""
        self.clear()
        arcade.draw_text(
            "Waiting for Opponent's Move...",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.BLACK,
            font_size=50,
            anchor_x="center",
        )

    # User input is intentionally disabled while waiting
    def on_key_press(self, key, modifiers):
        pass
        
    def on_mouse_press(self, x, y, button, modifiers):
        pass
