import arcade
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIZE, createShip, on_draw, blank_board

class BattleView(arcade.View):
    """Hotseat Battle view with two screens per turn: status and attack."""

    def __init__(self, player_number, game_window, player_ship_data, player_board, opponent_board):
        super().__init__()
        self.window = game_window
        self.player_number = player_number
        self.player_board = player_board
        self.opponent_board = opponent_board

        # Rebuild ships from setup data
        self.player_ships = arcade.SpriteList()
        self.player_ships = self.rebuild_ships(player_ship_data)
        self.all_sprites = arcade.SpriteList()


        # Grid offsets
        self.grid_x_offset = (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2
        self.grid_y_offset = (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2

        # Modes: 'status' shows player's ships, 'attack' shows blank grid to attack
        self.mode = "start"

        arcade.set_background_color(arcade.color.WHITE)
        print(f"Battle started for Player {self.player_number}")

    def rebuild_ships(self, ship_data):
        """Convert saved ship_data back into arcade.SpriteLists."""
        ships = arcade.SpriteList()
        for ship_parts in ship_data:
            length = len(ship_parts)
            ship_sprites = createShip(length, 0, 0)
            for part_sprite, part_data in zip(ship_sprites, ship_parts):
                (x, y, angle), hit = part_data
                part_sprite.center_x = x
                part_sprite.center_y = y
                part_sprite.angle = angle
                part_sprite.hit = hit
            ships.extend(ship_sprites)
        return ships

    def on_draw(self):
        """Draw the current screen (status or attack)."""
        self.clear()
        # Legend
        start_y = SCREEN_HEIGHT - 40
        line_spacing = 18
        arcade.draw_text("Legend:", 20, start_y, arcade.color.BLACK, 16)
        # Red = hit
        arcade.draw_text("Red = Hit", 20, start_y - line_spacing, arcade.color.RED, 14)

        # Green = miss
        arcade.draw_text("Green = Miss", 20, start_y - line_spacing*2, arcade.color.GREEN, 14)

        # Purple = ship destroyed
        arcade.draw_text("Purple = Ship Destroyed", 20, start_y - line_spacing*3, arcade.color.PURPLE, 14)

        if self.mode == "start":
            on_draw(self, blank_board)
            arcade.draw_text(
                f"Player {self.player_number}: Press [Enter] when ready",
                SCREEN_WIDTH/2, SCREEN_HEIGHT-40, arcade.color.BLUE, 30, anchor_x="center" 
            )
        
        elif self.mode == "status":
            # Show player's ships
            on_draw(self, self.player_board)
            self.player_ships.draw()
            arcade.draw_text(
                f"Player {self.player_number} - Your Ships",
                SCREEN_WIDTH / 2, 10, arcade.color.BLUE, 16, anchor_x="center"
            )
            arcade.draw_text(
                "Press [Enter] to switch to Attack Grid",
                SCREEN_WIDTH / 2, 30, arcade.color.BLACK, 14, anchor_x="center"
            )

        elif self.mode == "attack":
            # draw opponent board
            on_draw(self, self.opponent_board)  # Draw grid lines
            arcade.draw_text(
                f"Player {self.player_number} - Attack Opponent: Click any square to target it",
                SCREEN_WIDTH / 2, 10, arcade.color.RED, 16, anchor_x="center"
            )
        elif self.mode == "hit":
            on_draw(self,self.opponent_board)
            arcade.draw_text(
                f"Player {self.player_number} - Press [Enter] to change players",
                SCREEN_WIDTH / 2, 10, arcade.color.RED, 16, anchor_x="center"
            )
        elif self.mode == "end":
            on_draw(self, self.opponent_board)
            arcade.draw_text(
                f"Player {self.player_number} has won the game!!!!",
                SCREEN_WIDTH/2, SCREEN_HEIGHT-40, arcade.color.BLUE, 30, anchor_x="center" 
            )

    def on_key_press(self, key, modifiers):
        """Switch between status and attack screens."""
        if key == arcade.key.ENTER:
            if self.mode == "status":
                self.mode = "attack"
            elif self.mode == "hit":
                self.window.on_attack_finished(self.player_number, self.opponent_board)
            elif self.mode == "start":
                self.mode = "status"


    def on_mouse_press(self, x, y, button, modifiers):
        if self.mode != "attack":
            return  # Only clickable in attack mode

        col = int((x - self.grid_x_offset) // SQUARE_SIZE)
        row = int((y - self.grid_y_offset) // SQUARE_SIZE)
        key = chr(ord('A') + row) + str(col + 1)

        if key not in self.opponent_board:
            return  # Outside grid
        if (self.opponent_board[key] == 2 or self.opponent_board[key] == 3):
            print(f"Already attacked {key}")
            return
        check = self.window.check_if_hit(self.player_number, key)   
        if check == 2:
            self.mode = "end"
        else:
            self.mode = "hit"

