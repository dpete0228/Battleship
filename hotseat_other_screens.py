import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class GameOverView(arcade.View):
    """
    View shown when the game has ended, displaying the winner and options to exit or restart.
    """
    def __init__(self, main_game_window, winner_player_number):
        # Reference to the main game window to allow restarting the game
        super().__init__()
        self.winner = winner_player_number
        self.message = f"VICTORY! PLAYER {winner_player_number} HAS SUNK ALL OPPONENT SHIPS!"
        self.game = main_game_window

    def on_draw(self):
        """Render the game over screen with victory message and controls info."""
        self.clear()
        # Draw victory message, green text if message contains "VICTORY"
        arcade.draw_text(
            self.message,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 50,
            arcade.color.GREEN if "VICTORY" in self.message else arcade.color.RED,
            font_size=30,
            anchor_x="center",
        )
        
        # Draw instructions for exiting or restarting game
        arcade.draw_text(
            "Press ESC to exit or R to play again.",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 50,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        """Handle key input for quitting or restarting the game."""
        if key == arcade.key.ESCAPE:
            # Exit the entire game application cleanly
            arcade.exit()
        elif key == arcade.key.R:
            # Reset game state and return to initial connection/setup screen
            self.game.reset_game_state()
            

class WaitingView(arcade.View):
    """View displayed during hotseat transitions, prompting the next player to get ready."""
    def __init__(self, game_window, next_player_number):
        super().__init__()
        self.window = game_window
        self.next_player_number = next_player_number

    def on_show_view(self):
        """Set background color when view is shown."""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Draw the waiting screen with turn message and prompt."""
        self.clear()
        message = f"Turn Over. Player {self.next_player_number}'s turn is next."
        prompt = f"Player {self.next_player_number} press [Space] when ready."

        # Display the message about whose turn is next
        arcade.draw_text(
            message,
            self.window.width / 2,
            self.window.height / 2 + 50,
            arcade.color.WHITE,
            36,
            anchor_x="center"
        )
        
        # Display prompt to press [Space] to continue
        arcade.draw_text(
            prompt,
            self.window.width / 2,
            self.window.height / 2 - 50,
            arcade.color.YELLOW,
            24,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        """Detect spacebar press to continue to the next player's battle view."""
        if key == arcade.key.SPACE:
            self.window.show_player_battle(self.next_player_number)