import arcade
from setup import SetupView
from battle import BattleView
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, player1_board, player2_board, SQUARE_SIZE

class HotseatGame(arcade.Window):
    """Main Hotseat class controlling the flow between setup and battle views."""
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Battleship Hotseat")
        
        # Player data placeholders
        self.player1_setup_data = None
        self.player2_setup_data = None
        self.player1_board = player1_board
        self.player2_board = player2_board

        # Track current player for setup and battle
        self.current_player = 1

        # Start the first setup view
        self.show_player_setup(self.current_player)
    
    def show_player_setup(self, player_number):
        """Show the SetupView for the given player."""
        board = self.player1_board if player_number == 1 else self.player2_board
        setup_view = SetupView(player_number, self, board)
        self.show_view(setup_view)

    def show_player_battle(self, player_number):
        """Show the BattleView for the given player."""
        setup_data = self.player1_setup_data if player_number == 1 else self.player2_setup_data
        your_board = self.player1_board if player_number == 1 else self.player2_board
        opponents_board = self.player2_board if player_number == 1 else self.player1_board
        battle_view = BattleView(player_number, self, setup_data, your_board, opponents_board)
        self.show_view(battle_view)

    def on_setup_finished(self, player_number, ship_data, board):
        """Called by SetupView when a player finishes placing ships."""
        if player_number == 1:
            self.player1_setup_data = ship_data
            self.player1_board = board
            self.current_player = 2
            self.show_player_setup(self.current_player)
        else:
            self.player2_setup_data = ship_data
            self.player2_board = board
            self.current_player = 1  # Reset to Player 1 for battle
            self.start_game()

    def check_if_hit(self, player_number, key):
        if player_number == 1:
            board = self.player2_board
            ship_data = self.player2_setup_data
        else:
            board = self.player1_board
            ship_data = self.player1_setup_data

        if board[key] == 1:
            board[key] = 2  # mark hit on board
            # Now find which ship contains this hit part
            for ship in ship_data:
                # Each part_data in ship_parts is ((x,y,angle), hit)
                for part in ship:
                    (x, y, angle), hit = part
                    # Convert coordinates to grid key to match 'key'
                    col = int((x - (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                    row = int((y - (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                    part_key = chr(ord('A') + row) + str(col + 1)
                    if part_key == key:
                        part[1] = 1  # mark hit True in ship_data
                        # Check if all parts of this ship are hit
                        if all(p[1] == 1 for p in ship):
                            # Mark all parts as destroyed on the board
                            for p in ship:
                                (px, py, _) , _ = p
                                c = int((px - (SCREEN_WIDTH - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                                r = int((py - (SCREEN_HEIGHT - SQUARE_SIZE * 10) / 2) // SQUARE_SIZE)
                                destroyed_key = chr(ord('A') + r) + str(c + 1)
                                if destroyed_key in board:
                                    board[destroyed_key] = 4  # mark destroyed
                        break

            check = self.check_if_game_end(player_number)
            if check:
                return 2
            else:
                return 1
        else:
            board[key] = 3  # miss
            return 0

    
    def check_if_game_end(self, player_number):
        """Simple check to see if the game has ended"""
        # Check which player's turn it is and look at the opponent's board
        if player_number == 1:
            board = self.player2_board
        else:
            board = self.player1_board
        for key, value in board.items():
            if value == 1:  # A ship piece still exists
                return False
        # If it gets to this that means that all of the opponent's ships have been destroyed
        return True
        
    def on_attack_finished(self, player_number, opponents_board):
        """Called by BattleView when a player finishes their turn or battle."""
        if player_number == 1:
            self.player2_board = opponents_board
            self.current_player = 2
            self.show_player_battle(self.current_player)
        else:
            self.player1_board = opponents_board
            self.current_player = 1
            self.show_player_battle(self.current_player)
    


    def start_game(self):
        """Switch to battle view after both players finish setup."""
        print("Starting the battle!")
        self.current_player = 1  # Always start battle with Player 1
        self.show_player_battle(self.current_player)
