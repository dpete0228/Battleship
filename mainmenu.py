# main_menu.py
import arcade
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

class MainMenuView(arcade.View):
    def __init__(self, on_start_game):
        super().__init__()
        self.on_start_game = on_start_game  # Callback to launch selected game mode

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create buttons for selecting game modes
        hotseat_button = arcade.gui.UIFlatButton(text="Hotseat Game", width=200)
        network_button = arcade.gui.UIFlatButton(text="Network Game", width=200)

        # Arrange buttons vertically with spacing using a grid layout
        grid = arcade.gui.UIGridLayout(
            column_count=1, row_count=2, vertical_spacing=20
        )
        grid.add(hotseat_button, col=0, row=0)
        grid.add(network_button, col=0, row=1)

        # Center the grid on the screen using an anchor layout
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=grid, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

        # Bind button clicks to call the start_game callback with appropriate mode
        hotseat_button.on_click = lambda e: self.on_start_game("hotseat")
        network_button.on_click = lambda e: self.on_start_game("network")

    def on_show_view(self):
        # Set background color and enable GUI manager when view is shown
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.manager.enable()

    def on_hide_view(self):
        # Disable GUI manager when view is hidden to pause UI processing
        self.manager.disable()

    def on_draw(self):
        # Clear screen and draw the UI elements managed by the manager
        self.clear()
        self.manager.draw()