import arcade
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIZE, createShip, on_draw, blank_board

class BattleView(arcade.View):
    """Network Battle view for a single player, showing own ships or opponent's grid."""

    def __init__(self, player_number, game_window, player_ship_data, player_board, opponent_board):
        super().__init__()
        self.window = game_window
        self.player_number = player_number
        self.player_board = player_board
        self.opponent_board = opponent_board

        # Determine if this player is the current active player (can make moves)
        self.is_my_turn = (self.window.current_player == self.player_number)

        # Recreate player's ships from saved setup data into sprite objects
        self.player_ships = self.rebuild_ships(player_ship_data)

        # Calculate offsets to center the 10x10 grid in window
        self.grid_x_offset = (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2
        self.grid_y_offset = (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2
        self.all_sprites = arcade.SpriteList()

        # Set mode based on whether it's this player's turn
        # start = initial prompt, attack = player's turn to attack, status = waiting
        if self.is_my_turn:
            self.mode = "start" 
        else:
            self.mode = "status"
            # If it is not player's turn and not already on WaitingView, switch to waiting screen
            if not self.window.current_view.__class__.__name__ == 'WaitingView':
                self.window.show_waiting_screen()

        arcade.set_background_color(arcade.color.WHITE)
        print(f"Battle view initialized for Player {self.player_number}. My turn: {self.is_my_turn}")

    def rebuild_ships(self, ship_data):
        """Recreate ship sprites from stored ship part data after loading a game state."""
        ships = arcade.SpriteList()
        for ship_parts in ship_data:
            length = len(ship_parts)  # Number of parts in the ship
            ship_sprites = createShip(length, 0, 0)  # Create sprites with placeholder positions
            for part_sprite, part_data in zip(ship_sprites, ship_parts):
                (x, y, angle), hit = part_data  # Extract saved position, rotation, and hit status
                part_sprite.center_x = x
                part_sprite.center_y = y
                part_sprite.angle = angle
                part_sprite.hit = hit  # Restore hit state for visual feedback
            ships.extend(ship_sprites)
        return ships

    def on_draw(self):
        """Render current game view depending on mode and game state."""
        self.clear()
        
        # Draw legend indicating what the colors mean on the board
        start_y = SCREEN_HEIGHT - 40
        line_spacing = 18
        arcade.draw_text("Legend:", 20, start_y, arcade.color.BLACK, 16)
        arcade.draw_text("Red = Hit", 20, start_y - line_spacing, arcade.color.RED, 14)
        arcade.draw_text("Green = Miss", 20, start_y - line_spacing*2, arcade.color.GREEN, 14)
        arcade.draw_text("Purple = Ship Destroyed", 20, start_y - line_spacing*3, arcade.color.PURPLE, 14)

        if self.mode == "start":
            # Show player's own ships with a prompt to press Enter to attack
            on_draw(self, self.player_board)
            self.player_ships.draw()
            arcade.draw_text(
                f"Player {self.player_number}: Press [Enter] to view attack grid",
                SCREEN_WIDTH/2, SCREEN_HEIGHT-40, arcade.color.BLUE, 30, anchor_x="center" 
            )
            
        elif self.mode == "status":
            # Show own ships when waiting for opponent's turn
            on_draw(self, self.player_board)
            self.player_ships.draw()
            arcade.draw_text(
                f"Player {self.player_number} - Your Ships (Opponent's Turn)",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT-40, arcade.color.BLUE, 30, anchor_x="center"
            )

        elif self.mode == "attack" or self.mode == "hit":
            # Show opponent's grid for attacking or after shot fired
            on_draw(self, self.opponent_board)
            if self.mode == "attack":
                arcade.draw_text(
                    f"Player {self.player_number} - Attack Opponent: Click any square to target it",
                    SCREEN_WIDTH / 2, 10, arcade.color.RED, 16, anchor_x="center"
                )
            elif self.mode == "hit":
                arcade.draw_text(
                    f"Player {self.player_number}: Shot Fired! Waiting for Opponent's Move...",
                    SCREEN_WIDTH / 2, 10, arcade.color.ORANGE, 16, anchor_x="center"
                )

        elif self.mode == "end":
            # Display winning message once the game ends
            on_draw(self, self.opponent_board)
            arcade.draw_text(
                f"Player {self.player_number} has won the game!!!!",
                SCREEN_WIDTH/2, SCREEN_HEIGHT-40, arcade.color.BLUE, 30, anchor_x="center" 
            )

    def on_key_press(self, key, modifiers):
        """Handle key presses to switch from start prompt to attack mode if it's player's turn."""
        if key == arcade.key.ENTER and self.is_my_turn:
            if self.mode == "start":
                self.mode = "attack"
            # No action for other modes on Enter key

    def on_mouse_press(self, x, y, button, modifiers):
        # Ignore clicks if not in attack mode or player's turn
        if self.mode != "attack" or not self.is_my_turn:
            return 

        # Calculate grid coordinates based on mouse position and grid offset
        col = int((x - self.grid_x_offset) // SQUARE_SIZE)
        row = int((y - self.grid_y_offset) // SQUARE_SIZE)
        key = chr(ord('A') + row) + str(col + 1)  # Convert to Battleship-style coordinate (e.g. A1)

        # Return if click is outside opponent's board or invalid coordinate
        if key not in self.opponent_board:
            return 

        # Ignore if the square has already been attacked (values 2=hit,3=miss,4=sunk)
        if (self.opponent_board.get(key) in [2, 3, 4]):
            print(f"Already attacked {key}")
            return
        
        # 1. Send attack request to main window/game logic
        self.window.request_attack(self.player_number, key)
        
        # 2. If game over state is detected after attack request, switch to end screen
        if self.window.current_view.__class__.__name__ == "GameOverView":
            self.window.show_end_screen(self.window.current_player) 
        else:
            # 3. Set mode to 'hit' to show shot fired feedback
            self.mode = "hit"
            
            # 4. Switch to waiting screen while opponent takes their turn
            self.window.show_waiting_screen()