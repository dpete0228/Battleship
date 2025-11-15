import arcade
# Import from the new constants file
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIZE, createShip, on_draw, letters

class SetupView(arcade.View):
    """ Handles the drag-and-drop ship placement for one player. """
    def __init__(self, player_number, game_window, player_board):
        super().__init__()
        self.window = game_window
        self.player_number = player_number
        self.player_board = player_board
        arcade.set_background_color(arcade.color.WHITE)

        print(f"Starting Setup for Player {self.player_number}")

        # Set grid offsets
        self.grid_x_offset = (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2
        self.grid_y_offset = (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2
        
        # --- Player Ships (Initially off-grid) ---
        # Ship coordinates don't matter much here, as they'll be dragged.
        # We can reuse the coordinates from the previous setup
        self.carrier = createShip(5, 20, 20)
        self.battleship = createShip(4, 20, 100)
        self.submarine = createShip(3, 20, 180)
        self.cruiser = createShip(3, 20, 260)
        self.destroyer = createShip(2, 20, 340)

        self.player_ships = [self.carrier, self.battleship, self.submarine, self.cruiser, self.destroyer]
        
        # --- Ship Placement Logic Variables ---
        self.all_sprites = arcade.SpriteList()
        for ship in self.player_ships:
            self.all_sprites.extend(ship)
            
        self.selected_ship = None
        self.horizontal = True 
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def on_draw(self):
        """ Draw the game elements. """
        self.clear()
        # on_draw is now passed the window/view object (self)
        on_draw(self, self.player_board) # Utility function to draw grid and sprites

        # Draw prompt for the current player
        color = arcade.color.BLUE if self.player_number == 1 else arcade.color.RED
        arcade.draw_text(f"Player {self.player_number} Setup: Place your ships. Press [Space] to rotate. Press [N] to finish.", 
                         SCREEN_WIDTH / 2, 10, color, 16, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        # --- Ship Selection/Drag Logic (Copied from previous response) ---
        current_ships = self.player_ships

        for ship in current_ships:
            for part in ship:
                if part.collides_with_point((x, y)):
                    self.selected_ship = ship
                    self.horizontal = ship[0].angle in (0, 180)
                    # Calculate offset relative to the clicked part
                    self.drag_offset_x = part.center_x - x
                    self.drag_offset_y = part.center_y - y
                    return
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.selected_ship:
            return
        
        # A simpler drag logic that *moves* the ship by the mouse delta:
        for part in self.selected_ship:
            part.center_x += dx
            part.center_y += dy


    def on_mouse_release(self, x, y, button, modifiers):
        if not self.selected_ship:
            return

        # --- Snap to Grid Logic (Copied from previous response) ---
        anchor = self.selected_ship[0]
        ship_length = len(self.selected_ship)

        # Calculate grid cell for the anchor (part 0)
        col = round((anchor.center_x - self.grid_x_offset) / SQUARE_SIZE - 0.5)
        row = round((anchor.center_y - self.grid_y_offset) / SQUARE_SIZE - 0.5)

        # Check bounds and adjust
        if self.horizontal:
            max_col = 10 - ship_length
            col = max(0, min(max_col, col))
            row = max(0, min(9, row))
        else: # Vertical
            max_row = 10 - ship_length
            col = max(0, min(9, col))
            row = max(0, min(max_row, row))

        # Calculate snapped coordinates for the anchor (center of the cell)
        start_x = self.grid_x_offset + col * SQUARE_SIZE + SQUARE_SIZE / 2
        start_y = self.grid_y_offset + row * SQUARE_SIZE + SQUARE_SIZE / 2

        # Apply snapped position and correct angles
        for i, part in enumerate(self.selected_ship):
            if self.horizontal:
                part.center_x = start_x + i * SQUARE_SIZE
                part.center_y = start_y
                part.angle = 0 if i == 0 else (180 if i == ship_length - 1 else 0)
            else:
                part.center_x = start_x
                part.center_y = start_y + i * SQUARE_SIZE
                part.angle = 270 if i == 0 else (90 if i == ship_length - 1 else 90)

        self.selected_ship = None

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE and self.selected_ship:
            # --- Rotation Logic (Copied from previous response) ---
            self.horizontal = not self.horizontal
            anchor = self.selected_ship[0]
            anchor_x = anchor.center_x
            anchor_y = anchor.center_y
            ship_length = len(self.selected_ship)
            
            # Recalculate grid cell
            col = round((anchor_x - self.grid_x_offset) / SQUARE_SIZE - 0.5)
            row = round((anchor_y - self.grid_y_offset) / SQUARE_SIZE - 0.5)

            # Re-check bounds after rotation
            if self.horizontal:
                max_col = 10 - ship_length
                col = max(0, min(max_col, col))
                row = max(0, min(9, row))
            else:
                max_row = 10 - ship_length
                col = max(0, min(9, col))
                row = max(0, min(max_row, row))
            
            # Recalculate snapped position
            start_x = self.grid_x_offset + col * SQUARE_SIZE + SQUARE_SIZE / 2
            start_y = self.grid_y_offset + row * SQUARE_SIZE + SQUARE_SIZE / 2

            # Apply new position and angles
            for i, part in enumerate(self.selected_ship):
                if self.horizontal:
                    part.center_x = start_x + i * SQUARE_SIZE
                    part.center_y = start_y
                    part.angle = 0 if i == 0 else (180 if i == ship_length - 1 else 0)
                else:
                    part.center_x = start_x
                    part.center_y = start_y + i * SQUARE_SIZE
                    part.angle = 270 if i == 0 else (90 if i == ship_length - 1 else 90)
                
        if key == arcade.key.N:
            # Check if all ships are on the grid (Simple check: center is within grid bounds)
            value = self.all_ships_placed_correctly()
            if value == 2:
                # Store the placement data somewhere accessible by the game
                ship_data, board = self.get_ship_placement_data()
                
                if self.player_number == 1:
                    # Finish Setup
                    self.window.on_setup_finished(self.player_number, ship_data, board)
                    return
                else: # Player 2
                    # Finish Setup
                    self.window.on_setup_finished(self.player_number, ship_data, board)
                    return
            elif value == 1:
                print("Error: You can't have any overlapping ships")
            else:
                print("Error: All ships must be placed on the grid!")
    
    def all_ships_placed_correctly(self):
        """Checks if all ship parts are within the grid and no ships overlap."""
        grid_left = self.grid_x_offset
        grid_right = self.grid_x_offset + 10 * SQUARE_SIZE
        grid_bottom = self.grid_y_offset
        grid_top = self.grid_y_offset + 10 * SQUARE_SIZE

        # Keep track of occupied cells
        occupied_cells = set()

        for ship in self.player_ships:
            for part in ship:
                # 1. Check if the part is inside the grid
                if not (grid_left <= part.center_x <= grid_right and 
                        grid_bottom <= part.center_y <= grid_top):
                    return 0

                # 2. Check for overlap
                # Convert part's center to a grid coordinate
                col = int((part.center_x - self.grid_x_offset) // SQUARE_SIZE)
                row = int((part.center_y - self.grid_y_offset) // SQUARE_SIZE)

                if (row, col) in occupied_cells:
                    return 1  # Overlap detected
                occupied_cells.add((row, col))

        return 2 # No errors


    def get_ship_placement_data(self):
        """
        Returns ship placement data AND updates the player's board (state=1 for ship parts).
        Each part's data includes (center_x, center_y, angle).
        """
        data = []
        
        board = self.player_board

        for ship in self.player_ships:
            ship_parts_data = []
            for part in ship:
                ship_parts_data.append([(part.center_x, part.center_y, part.angle), 0])
                
                # Convert center_x, center_y to grid key
                col = int((part.center_x - self.grid_x_offset) // SQUARE_SIZE)
                row = int((part.center_y - self.grid_y_offset) // SQUARE_SIZE)
                
                # Make sure we are inside grid
                if 0 <= col < 10 and 0 <= row < 10:
                    key = letters[row] + str(col + 1)
                    if key in board:
                        board[key] = 1  # Mark ship on the board
            
            data.append(ship_parts_data)
        
        return data, board
