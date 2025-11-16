import arcade, arcade.gui
import socket
from arcade import Rect

# ------------- Utility for showing local IP -------------

def get_local_ip():
    """
    Retrieves the local IP address of the machine.
    Attempts to connect to an external server (Google DNS) to get the IP.
    Falls back to hostname resolution if connection fails.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to external server
        ip = s.getsockname()[0]    # Get socket's own IP address
        s.close()
        return ip
    except:
        # Fall back to hostname resolution
        return socket.gethostbyname(socket.gethostname())


# ------------- Main Menu (Host / Join Buttons) -------------

class ConnectView(arcade.View):
    """Main menu view with options to host or join a game."""

    def __init__(self):
        super().__init__()

        # UIManager to handle GUI widgets
        self.manager = arcade.gui.UIManager()

        # Create Host and Join buttons
        host_button = arcade.gui.UIFlatButton(text="Host Game", width=150)
        join_button = arcade.gui.UIFlatButton(text="Join Game", width=150)

        # Layout buttons vertically with spacing using a grid layout
        self.grid = arcade.gui.UIGridLayout(
            column_count=1, row_count=2, horizontal_spacing=20, vertical_spacing=20
        )
        self.grid.add(host_button, column=0, row=0)
        self.grid.add(join_button, column=0, row=1)

        # Anchor the grid at center of the screen
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.grid,
        )
        
        # Bind click events using decorator syntax
        @host_button.event("on_click")
        def on_click_host_button(event):
            # Switch to HostWaitingView when hosting game
            self.window.show_view(HostWaitingView())

        @join_button.event("on_click")
        def on_click_join_button(event):
            # Switch to JoinGameView when joining a game
            self.window.show_view(JoinGameView())

    def on_hide_view(self):
        """Disable UIManager when view is hidden to suspend GUI processing."""
        self.manager.disable()

    def on_show_view(self):
        """Set background color and enable UIManager when view is shown."""
        arcade.set_background_color(arcade.color.WHITE)
        self.manager.enable()

    def on_draw(self):
        """Draw the menu screen and UI widgets."""
        self.clear()
        self.manager.draw()


# ----------- Host screen (shows your IP) -------------

class HostWaitingView(arcade.View):
    """Screen shown to the host player displaying their local IP to share."""

    def __init__(self):
        super().__init__()
        # Retrieve local IP address for display
        self.host_ip = get_local_ip()
        # Notify game window to begin hosting connection with this IP
        self.window.host_connect(self.host_ip)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        """Draw hosting info and instructions."""
        self.clear()
        arcade.draw_text("Hosting Game…", 400, 450, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text(f"Give this IP to your opponent:", 400, 350, arcade.color.BLACK, 20, anchor_x="center")
        arcade.draw_text(self.host_ip, 400, 300, arcade.color.DARK_GRAY, 40, anchor_x="center")


# ----------- Join screen (type an IP address) -------------

class JoinGameView(arcade.View):
    """Screen for joining a hosted game by entering host's IP address."""

    def __init__(self):
        super().__init__()
        # Create UIManager for managing input box and button
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create an input text box for entering IP address
        self.input_box = arcade.gui.UIInputText(
            x=300,
            y=300,
            width=200,
            height=40,
            text="",
            border_color=arcade.color.BLACK,
            text_color=arcade.color.BLACK,
            font_size=20
        )
        # Create a connect button below the input box
        self.join_button = arcade.gui.UIFlatButton(
            text="Connect",
            x=350,
            y=230,
            width=120,
            height=40
        )

        # Add widgets to the UIManager so they are processed and drawn
        self.manager.add(self.input_box)
        self.manager.add(self.join_button)

        # Bind the connect button click to the on_connect handler
        self.join_button.on_click = self.on_connect
    

    def on_connect(self, event):
        """Callback when the connect button is pressed to join the game.

        Retrieves the IP address from input and calls the join_connect method
        on the main window, initiating connection to the host.
        """
        ip = self.input_box.text.strip()
        print("Connecting to:", ip)
        self.window.join_connect(ip)
        self.clear()  # Clear screen after connect


    def on_draw(self):
        """Render the join screen UI and instructions."""
        self.clear()
        self.manager.draw()
        arcade.draw_text(
            "Enter Host IP:",
            self.window.width // 2,
            380,
            arcade.color.BLACK,
            30,
            anchor_x="center"
        )