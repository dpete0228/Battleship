import arcade
# Import from the new constants file
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIZE, createShip, on_draw, letters

class SetupView(arcade.View):
    """Handles drag-and-drop ship placement for a single player during setup phase."""
    def __init__(self, player_number, game_window, player_board):
        super().__init__()
        self.window = game_window
        self.player_number = player_number
        self.player_board = player_board
        arcade.set_background_color(arcade.color.WHITE)

        print(f"Starting Setup for Player {self.player_number}")

        # Calculate offsets to center the 10x10 grid on screen
        self.grid_x_offset = (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2
        self.grid_y_offset = (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2
        
        # --- Create Ships at initial off-grid positions ---
        # Positions are placeholders; ships are draggable
        self.carrier = createShip(5, 20, 20)
        self.battleship = createShip(4, 20, 100)
        self.submarine = createShip(3, 20, 180)
        self.cruiser = createShip(3, 20, 260)
        self.destroyer = createShip(2, 20, 340)

        # Store all ships as list for easy processing
        self.player_ships = [self.carrier, self.battleship, self.submarine, self.cruiser, self.destroyer]
        
        # Combine all ship parts into a single sprite list for rendering/manipulation
        self.all_sprites = arcade.SpriteList()
        for ship in self.player_ships:
            self.all_sprites.extend(ship)
            
        # Variables to track which ship is selected and orientation state
        self.selected_ship = None
        self.horizontal = True  # Current orientation: True=horizontal, False=vertical

        # Drag offsets to maintain smooth dragging relative to mouse click point
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def on_draw(self):
        """Render the grid, ships, and on-screen instructions."""
        self.clear()
        # Draw grid and player's board using shared utility on_draw function
        on_draw(self, self.player_board)

        # Draw instructions with color indicating active player
        color = arcade.color.BLUE if self.player_number == 1 else arcade.color.RED
        arcade.draw_text(
            f"Player {self.player_number} Setup: Place your ships. "
            f"Press [Space] to rotate. Press [N] to finish.", 
            SCREEN_WIDTH / 2, 10, color, 16, anchor_x="center"
        )

    def on_mouse_press(self, x, y, button, modifiers):
        """Select the ship part under the mouse to enable dragging."""
        current_ships = self.player_ships

        for ship in current_ships:
            for part in ship:
                if part.collides_with_point((x, y)):
                    self.selected_ship = ship
                    # Determine orientation from first part's angle (0 or 180 horizontal)
                    self.horizontal = ship[0].angle in (0, 180)
                    # Store offset between mouse position and part center for smooth dragging
                    self.drag_offset_x = part.center_x - x
                    self.drag_offset_y = part.center_y - y
                    return
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Move the selected ship with the mouse drag delta."""
        if not self.selected_ship:
            return
        
        # Update each part's position by mouse delta (dx, dy)
        for part in self.selected_ship:
            part.center_x += dx
            part.center_y += dy


    def on_mouse_release(self, x, y, button, modifiers):
        """Snap the dropped ship to the nearest valid grid position and adjust orientation."""
        if not self.selected_ship:
            return

        anchor = self.selected_ship[0]
        ship_length = len(self.selected_ship)

        # Calculate nearest grid cell for the anchor part
        col = round((anchor.center_x - self.grid_x_offset) / SQUARE_SIZE - 0.5)
        row = round((anchor.center_y - self.grid_y_offset) / SQUARE_SIZE - 0.5)

        # Clamp column and row to valid grid range, accounting for ship length and orientation
        if self.horizontal:
            max_col = 10 - ship_length
            col = max(0, min(max_col, col))
            row = max(0, min(9, row))
        else:  # Vertical orientation
            max_row = 10 - ship_length
            col = max(0, min(9, col))
            row = max(0, min(max_row, row))

        # Calculate exact center coordinates of the grid cell
        start_x = self.grid_x_offset + col * SQUARE_SIZE + SQUARE_SIZE / 2
        start_y = self.grid_y_offset + row * SQUARE_SIZE + SQUARE_SIZE / 2

        # Position each ship part evenly based on orientation and length
        for i, part in enumerate(self.selected_ship):
            if self.horizontal:
                part.center_x = start_x + i * SQUARE_SIZE
                part.center_y = start_y
                # Set angle: front 0°, back 180°, others 0°
                part.angle = 0 if i == 0 else (180 if i == ship_length - 1 else 0)
            else:
                part.center_x = start_x
                part.center_y = start_y + i * SQUARE_SIZE
                # Set angle: front 270°, back 90°, others 90°
                part.angle = 270 if i == 0 else (90 if i == ship_length - 1 else 90)

        # Clear selected ship after snapping
        self.selected_ship = None

    def on_key_press(self, key, modifiers):
        """Handle rotation and finalization input during setup."""
        if key == arcade.key.SPACE and self.selected_ship:
            # Toggle orientation flag
            self.horizontal = not self.horizontal
            anchor = self.selected_ship[0]
            anchor_x = anchor.center_x
            anchor_y = anchor.center_y
            ship_length = len(self.selected_ship)
            
            # Recalculate current grid position of anchor part
            col = round((anchor_x - self.grid_x_offset) / SQUARE_SIZE - 0.5)
            row = round((anchor_y - self.grid_y_offset) / SQUARE_SIZE - 0.5)

            # Clamp to grid bounds with respect to new orientation
            if self.horizontal:
                max_col = 10 - ship_length
                col = max(0, min(max_col, col))
                row = max(0, min(9, row))
            else:  # Vertical orientation
                max_row = 10 - ship_length
                col = max(0, min(9, col))
                row = max(0, min(max_row, row))
            
            # Calculate new snapped positions based on rotated orientation
            start_x = self.grid_x_offset + col * SQUARE_SIZE + SQUARE_SIZE / 2
            start_y = self.grid_y_offset + row * SQUARE_SIZE + SQUARE_SIZE / 2

            # Apply new position and correct angles to ship parts
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
            # Check if ship placement is valid: all within grid and no overlaps
            value = self.all_ships_placed_correctly()
            if value == 2:
                # Get ship placement data and updated board marking ships
                ship_data, board = self.get_ship_placement_data()
                
                # Inform game window that setup finished for this player
                self.window.on_setup_finished(self.player_number, ship_data, board)
            elif value == 1:
                print("Error: You can't have any overlapping ships")
            else:
                print("Error: All ships must be placed on the grid!")
    
    def all_ships_placed_correctly(self):
        """Verify all ship parts are fully inside the grid and no ships overlap.

        Returns:
            0 if any ship part is outside grid bounds,
            1 if any ships overlap,
            2 if all ship placements are valid.
        """
        grid_left = self.grid_x_offset
        grid_right = self.grid_x_offset + 10 * SQUARE_SIZE
        grid_bottom = self.grid_y_offset
        grid_top = self.grid_y_offset + 10 * SQUARE_SIZE

        occupied_cells = set()  # Track which grid cells are occupied

        for ship in self.player_ships:
            for part in ship:
                # Check if part is inside grid boundaries
                if not (grid_left <= part.center_x <= grid_right and 
                        grid_bottom <= part.center_y <= grid_top):
                    return 0

                # Convert part's center position to grid coordinates (row, col)
                col = int((part.center_x - self.grid_x_offset) // SQUARE_SIZE)
                row = int((part.center_y - self.grid_y_offset) // SQUARE_SIZE)

                # Check for overlapping parts by adding to set
                if (row, col) in occupied_cells:
                    return 1  # Overlap detected
                occupied_cells.add((row, col))

        return 2  # All valid with no overlaps

    def get_ship_placement_data(self):
        """
        Collect placement data for all ships and update player's board to mark ship positions.

        Returns:
            data (list): Nested list with ship parts as [[(x, y, angle), hit_flag], ...].
            board (dict): Updated player board with ship parts marked as 1.
        """
        data = []
        board = self.player_board

        for ship in self.player_ships:
            ship_parts_data = []
            for part in ship:
                # Store part position and default hit_flag=0 (unhit)
                ship_parts_data.append([(part.center_x, part.center_y, part.angle), 0])
                
                # Convert center_x/y coordinates to board key like 'A1'
                col = int((part.center_x - self.grid_x_offset) // SQUARE_SIZE)
                row = int((part.center_y - self.grid_y_offset) // SQUARE_SIZE)
                
                # Verify within grid bounds before updating board state
                if 0 <= col < 10 and 0 <= row < 10:
                    key = letters[row] + str(col + 1)
                    if key in board:
                        board[key] = 1  # Mark this cell as containing ship
                
            data.append(ship_parts_data)
        
        return data, board